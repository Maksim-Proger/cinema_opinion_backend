import httpx
import logging
import time
from datetime import date
from psycopg2.extras import Json

from app.core.kinopoisk import (
    MONTHS,
    premieres_url,
    api_key_info_url,
    kinopoisk_headers,
    premieres_code,
)
from app.repositories.collection_repository import CollectionRepository

logger = logging.getLogger(__name__)

FIRST_YEAR = 1995
QUOTA_RESERVE = 30
QUOTA_EXHAUSTED_STATUS = 402
REQUEST_DELAY_SECONDS = 1.0
RATE_LIMIT_PAUSE_SECONDS = 15
MAX_RETRIES = 3
RETRY_DAYS = (1, 3, 15)


def daily_quota_left(client: httpx.Client) -> int:
    response = client.get(api_key_info_url(), headers=kinopoisk_headers())
    response.raise_for_status()
    daily = response.json()["dailyQuota"]
    return daily["value"] - daily["used"]


def to_int(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def map_item(raw: dict, position: int) -> dict:
    return {
        "position": position,
        "kp_id": raw.get("kinopoiskId"),
        "title_ru": raw.get("nameRu"),
        "title_en": raw.get("nameEn") or raw.get("nameOriginal"),
        "year": to_int(raw.get("year")),
        "type": raw.get("type"),
        "rating_kp": None,
        "rating_imdb": None,
        "length_min": to_int(raw.get("duration")),
        "premiere_ru": raw.get("premiereRu") or None,
        "genres": [g["genre"] for g in raw.get("genres") or [] if g.get("genre")],
        "countries": [c["country"] for c in raw.get("countries") or [] if c.get("country")],
        "poster_url": raw.get("posterUrl"),
        "poster_preview": raw.get("posterUrlPreview"),
        "raw": Json(raw),
    }


def fetch_month(client: httpx.Client, year: int, month: str) -> list[dict] | None:
    for attempt in range(MAX_RETRIES):
        response = client.get(
            premieres_url(),
            headers=kinopoisk_headers(),
            params={"year": year, "month": month},
        )

        if response.status_code == 429:
            pause = RATE_LIMIT_PAUSE_SECONDS * (attempt + 1)
            logger.warning("429 на %s %s, пауза %s с", month, year, pause)
            time.sleep(pause)
            continue

        if response.status_code == QUOTA_EXHAUSTED_STATUS:
            logger.info("Суточная квота исчерпана на %s %s", month, year)
            return None

        response.raise_for_status()
        items = response.json().get("items") or []
        return [map_item(raw, index + 1) for index, raw in enumerate(items)]

    return None


def import_premieres() -> dict:
    lock_conn = CollectionRepository.try_acquire_import_lock()
    if lock_conn is None:
        logger.info("Импорт уже выполняется в другом процессе")
        return {"imported": 0, "skipped": 0, "stopped_at": "locked"}

    try:
        return _run_import()
    finally:
        CollectionRepository.release_import_lock(lock_conn)


def _run_import() -> dict:
    done = CollectionRepository.existing_codes("premieres")
    imported = 0
    skipped = 0

    with httpx.Client(timeout=30.0) as client:
        budget = daily_quota_left(client) - QUOTA_RESERVE
        logger.info("Доступно запросов: %s", budget)

        today = date.today()
        current_code = premieres_code(today.year, today.month - 1)

        for year in range(today.year, FIRST_YEAR - 1, -1):
            for month_index in range(11, -1, -1):
                if year == today.year and month_index > today.month - 1:
                    continue

                code = premieres_code(year, month_index)

                if code in done:
                    skipped += 1
                    continue

                if code == current_code and today.day not in RETRY_DAYS:
                    continue

                if budget <= 0:
                    logger.info("Квота исчерпана, остановка на %s", code)
                    return {"imported": imported, "skipped": skipped, "stopped_at": code}

                month = MONTHS[month_index]
                items = fetch_month(client, year, month)
                budget -= 1

                if items is None:
                    logger.warning("Не удалось получить %s, остановка", code)
                    return {"imported": imported, "skipped": skipped, "stopped_at": code}

                CollectionRepository.save_collection(
                    code=code,
                    kind="premieres",
                    title=f"Премьеры {month} {year}",
                    items=items,
                )
                done.add(code)
                imported += 1
                logger.info("%s — %s записей, осталось %s", code, len(items), budget)
                time.sleep(REQUEST_DELAY_SECONDS)

    if current_code not in done and today.day == RETRY_DAYS[-1]:
        logger.error("Премьеры за %s не загружены после трёх попыток", current_code)

    return {"imported": imported, "skipped": skipped, "stopped_at": None}

