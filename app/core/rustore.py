import httpx
import time
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

RUSTORE_BASE_URL = "https://vkpns.rustore.ru/v1"
# URL для получения токена (согласно доке RuStore)
AUTH_URL = "https://auth.vkpns.rustore.ru/v1/internal/auth"

# Переменные для хранения токена в памяти процесса
_cached_access_token = None
_token_expires_at = 0


def get_access_token() -> str:
    global _cached_access_token, _token_expires_at

    current_time = time.time()

    # Если токен есть и он будет валиден еще хотя бы 10 минут — возвращаем его
    if _cached_access_token and current_time < (_token_expires_at - 600):
        return _cached_access_token

    # Если токена нет или он просрочен — идем за новым
    try:
        with httpx.Client() as client:
            response = client.post(
                AUTH_URL,
                json={"service_token": settings.rustore_service_token},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

            # В ответе RuStore токен лежит в body.access_token
            # А время жизни в body.expires_in (обычно это 24 часа в секундах)
            body = data.get("body", {})
            _cached_access_token = body.get("access_token")
            expires_in = body.get("expires_in", 86400)

            _token_expires_at = current_time + expires_in

            logger.info("RuStore Access Token refreshed successfully")
            return _cached_access_token

    except Exception as e:
        logger.error(f"Failed to refresh RuStore Access Token: {e}")
        # Если не удалось получить новый, а старый еще есть — попробуем вернуть старый как последний шанс
        if _cached_access_token:
            return _cached_access_token
        raise


def rustore_send_url() -> str:
    return f"{RUSTORE_BASE_URL}/projects/{settings.rustore_project_id}/messages:send"


def rustore_headers() -> dict:
    # Теперь мы вызываем функцию, которая сама решит: выдать старый токен или обновить его
    token = get_access_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


# from app.core.config import settings
#
# RUSTORE_BASE_URL = "https://vkpns.rustore.ru/v1"
#
# def rustore_send_url() -> str:
#     return f"{RUSTORE_BASE_URL}/projects/{settings.rustore_project_id}/messages:send"
#
# def rustore_headers() -> dict:
#     return {
#         "Authorization": f"Bearer {settings.rustore_service_token}",
#         "Content-Type": "application/json"
#     }
