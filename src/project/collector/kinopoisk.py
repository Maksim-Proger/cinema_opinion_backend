import logging
import time

import httpx

from project.utils.config import settings
from project.utils.models import MovieItem

logger = logging.getLogger(__name__)

KINOPOISK_BASE_URL = "https://kinopoiskapiunofficial.tech/api"  # адрес API Кинопоиска

# названия месяцев в формате API Кинопоиска; индекс = номер месяца минус 1
MONTHS = [
    "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
    "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER",
]

QUOTA_EXHAUSTED_STATUS = 402  # код ответа Кинопоиска «квота на сегодня кончилась»
REQUEST_DELAY_SECONDS = 1.0  # пауза между запросами, чтобы API не ответил 429
RATE_LIMIT_PAUSE_SECONDS = 15  # пауза после ответа 429; растёт с каждой попыткой: 15, 30, 45 с
MAX_RETRIES = 3  # сколько раз пробовать запросить один месяц, прежде чем сдаться

# превращает значение в число; не получилось — None
def to_int(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

# переводит один фильм из ответа Кинопоиска в MovieItem
def map_premiere(raw: dict, position: int) -> MovieItem:
    return MovieItem(
        position=position,
        kp_id=raw.get("kinopoiskId"),
        title_ru=raw.get("nameRu"),
        title_en=raw.get("nameEn") or raw.get("nameOriginal"),
        year=to_int(raw.get("year")),
        type=raw.get("type"),
        length_min=to_int(raw.get("duration")),
        premiere_ru=raw.get("premiereRu") or None,
        genres=[g["genre"] for g in raw.get("genres") or [] if g.get("genre")],
        countries=[c["country"] for c in raw.get("countries") or [] if c.get("country")],
        poster_url=raw.get("posterUrl"),
        poster_preview=raw.get("posterUrlPreview"),
        raw=raw,
    )

# все запросы к API Кинопоиска идут через этот класс
class KinopoiskClient:
    # создаёт HTTP-клиент с адресом, ключом и таймаутом
    def __init__(self):
        self._client = httpx.Client(
            base_url=KINOPOISK_BASE_URL,
            headers={
                "X-API-KEY": settings.kinopoisk_api_key,
                "accept": "application/json",
            },
            timeout=30.0,
        )

    # закрывает HTTP-клиент при остановке сервиса
    def close(self):
        self._client.close()

    # сколько запросов осталось на сегодня
    def daily_quota_left(self) -> int:
        response = self._client.get(f"/v1/api_keys/{settings.kinopoisk_api_key}")
        response.raise_for_status()
        daily = response.json()["dailyQuota"]
        return daily["value"] - daily["used"]

    # премьеры за месяц; при 429 повторяет с паузой; None — квота кончилась или попытки исчерпаны
    def fetch_premieres(self, year: int, month: int) -> list[MovieItem] | None:
        month_name = MONTHS[month - 1]

        for attempt in range(MAX_RETRIES):
            response = self._client.get(
                "/v2.2/films/premieres",
                params={"year": year, "month": month_name},
            )

            if response.status_code == 429:
                pause = RATE_LIMIT_PAUSE_SECONDS * (attempt + 1)
                logger.warning("429 на %s %s, пауза %s с", month_name, year, pause)
                time.sleep(pause)
                continue

            if response.status_code == QUOTA_EXHAUSTED_STATUS:
                logger.info("Суточная квота исчерпана на %s %s", month_name, year)
                return None

            response.raise_for_status()
            time.sleep(REQUEST_DELAY_SECONDS)
            items = response.json().get("items") or []
            return [map_premiere(raw, index + 1) for index, raw in enumerate(items)]

        return None
