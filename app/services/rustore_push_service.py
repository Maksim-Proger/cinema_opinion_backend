import httpx
import logging
import random
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
from app.core.rustore import rustore_send_url, rustore_headers

logger = logging.getLogger(__name__)

class RuStorePushService:
    @staticmethod
    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError)),
        stop=stop_after_attempt(6),
        wait=lambda retry_state: wait_exponential(multiplier=1, min=2, max=30)(retry_state) + random.uniform(0, 0.5),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def send(device_push_token: str, title: str, body: str):
        payload = {
            "message": {
                "token": device_push_token,
                # "data": {
                #     "title": title,
                #     "body": body
                # }
                "notification": {
                    "title": title,
                    "body": body
                },
                # "android": {
                #     "notification": {
                #         "icon": "ic_notification",
                #         "color": "#1D2523",
                #         "channel_id": "default_push_channel"
                #     }
                # }
            }
        }

        with httpx.Client(http2=True, timeout=10.0) as client:
            response = client.post(
                rustore_send_url(),
                headers=rustore_headers(),
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

