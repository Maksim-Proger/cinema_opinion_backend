import asyncio
import logging
from app.usecases.import_premieres import _run_import

logger = logging.getLogger(__name__)

SYNC_INTERVAL_SECONDS = 24 * 60 * 60


async def premieres_sync_worker():
    while True:
        try:
            result = await asyncio.to_thread(_run_import)
            logger.info("Синхронизация премьер: %s", result)
        except Exception:
            logger.exception("Ошибка синхронизации премьер")
        await asyncio.sleep(SYNC_INTERVAL_SECONDS)
