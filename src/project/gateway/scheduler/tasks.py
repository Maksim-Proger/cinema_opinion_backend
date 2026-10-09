import asyncio
import logging
from datetime import datetime, time, timedelta
from typing import Callable

from project.gateway.usecases.premieres import MOSCOW_TZ

logger = logging.getLogger(__name__)

SYNC_TIME = time(0, 5)  # во сколько запускать ежедневную загрузку (по Москве)
RETRY_AFTER_ERROR_SECONDS = 60 * 60  # через сколько секунд повторить после ошибки: 1 час


# сколько секунд осталось до ближайших 00:05 по Москве
def seconds_until_next_sync() -> float:
    now = datetime.now(MOSCOW_TZ)
    next_run = datetime.combine(now.date() + timedelta(days=1), SYNC_TIME, tzinfo=MOSCOW_TZ)
    return (next_run - now).total_seconds()


# в цикле запускает загрузку премьер: сразу при старте и каждый день в 00:05; после ошибки повтор через час
async def premieres_sync_worker(import_premieres: Callable[[], dict]):
    while True:
        try:
            result = await asyncio.to_thread(import_premieres)
            logger.info("Синхронизация премьер: %s", result)
            delay = seconds_until_next_sync()
        except Exception:
            logger.exception("Ошибка синхронизации премьер")
            delay = RETRY_AFTER_ERROR_SECONDS
        await asyncio.sleep(delay)
