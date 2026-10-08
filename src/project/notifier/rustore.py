import logging
import random

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log

from project.utils.config import settings

logger = logging.getLogger(__name__)

RUSTORE_BASE_URL = "https://vkpns.rustore.ru/v1"


class RuStorePushService:
    @staticmethod
    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError)),
        stop=stop_after_attempt(6),
        wait=lambda retry_state: wait_exponential(multiplier=1, min=2, max=30)(retry_state) + random.uniform(0, 0.5),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def send(device_push_token: str, title: str, body: str) -> tuple[int, str]:
        payload = {
            "message": {
                "token": device_push_token,
                "data": {
                    "title": title,
                    "body": body
                }
            }
        }

        with httpx.Client(http2=True, timeout=10.0) as client:
            response = client.post(
                f"{RUSTORE_BASE_URL}/projects/{settings.rustore_project_id}/messages:send",
                headers={
                    "Authorization": f"Bearer {settings.rustore_service_token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )

        if response.status_code != 200:
            logger.error(
                "RuStore push failed",
                extra={
                    "status_code": response.status_code,
                    "response": response.text,
                    "token_prefix": device_push_token[:10] + "..."
                }
            )

        response.raise_for_status()
        return response.status_code, response.text
