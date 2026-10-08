import logging
from datetime import datetime, timedelta
from typing import Protocol

from project.gateway.usecases.premieres import MOSCOW_TZ, premieres_code
from project.utils.models import MovieItem

logger = logging.getLogger(__name__)

FIRST_YEAR = 1995
QUOTA_RESERVE = 30  # сколько запросов из дневной квоты не трогать: оставить приложению
RETRY_DAYS = (1, 3, 15)  # в какие числа загружать текущий месяц

class PremieresSource(Protocol):

    def daily_quota_left(self) -> int: ...

    def fetch_premieres(self, year: int, month: int) -> list[MovieItem] | None: ...

class CollectionStore(Protocol):
    def try_acquire_import_lock(self): ...

    def release_import_lock(self, lock) -> None: ...

    def existing_collections(self, kind: str) -> dict[str, datetime]: ...

    def save_collection(self, code: str, kind: str, title: str, items: list[MovieItem]) -> int: ...


class ImportPremieresUseCase:
    def __init__(self, source: PremieresSource, store: CollectionStore):
        self._source = source
        self._store = store

    def execute(self) -> dict:
        lock = self._store.try_acquire_import_lock()
        if lock is None:
            logger.info("Импорт уже выполняется в другом процессе")
            return {"imported": 0, "skipped": 0, "stopped_at": "locked"}

        try:
            return self._run_import()
        finally:
            self._store.release_import_lock(lock)

    def _run_import(self) -> dict:
        done = self._store.existing_collections("premieres")
        imported = 0
        skipped = 0

        today = datetime.now(MOSCOW_TZ).date()
        month_start = today.replace(day=1)
        current_code = premieres_code(today.year, today.month)

        previous = month_start - timedelta(days=1)
        previous_code = premieres_code(previous.year, previous.month)
        previous_updated = done.get(previous_code)
        if previous_updated and previous_updated.astimezone(MOSCOW_TZ).date() < month_start:
            del done[previous_code]

        budget = self._source.daily_quota_left() - QUOTA_RESERVE
        logger.info("Доступно запросов: %s", budget)

        for year in range(today.year, FIRST_YEAR - 1, -1):
            for month in range(12, 0, -1):
                if year == today.year and month > today.month:
                    continue

                code = premieres_code(year, month)

                if code in done:
                    skipped += 1
                    continue

                if code == current_code and today.day not in RETRY_DAYS:
                    continue

                if budget <= 0:
                    logger.info("Квота исчерпана, остановка на %s", code)
                    return {"imported": imported, "skipped": skipped, "stopped_at": code}

                items = self._source.fetch_premieres(year, month)
                budget -= 1

                if items is None:
                    logger.warning("Не удалось получить %s, остановка", code)
                    return {"imported": imported, "skipped": skipped, "stopped_at": code}

                self._store.save_collection(
                    code=code,
                    kind="premieres",
                    title=f"Премьеры {month:02d}.{year}",
                    items=items,
                )
                done[code] = datetime.now(MOSCOW_TZ)
                imported += 1
                logger.info("%s — %s записей, осталось %s", code, len(items), budget)

        if current_code not in done and today.day == RETRY_DAYS[-1]:
            logger.error("Премьеры за %s не загружены после трёх попыток", current_code)

        return {"imported": imported, "skipped": skipped, "stopped_at": None}
