import httpx
import time
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

RUSTORE_BASE_URL = "https://vkpns.rustore.ru/v1"
AUTH_URL = "https://auth.vkpns.rustore.ru/v1/internal/auth"

# Кэш для токена в памяти процесса
_cached_access_token = None
_token_expires_at = 0


def get_access_token() -> str:
    global _cached_access_token, _token_expires_at

    current_time = time.time()

    # 1. Если в кэше есть живой access_token, возвращаем его
    if _cached_access_token and current_time < (_token_expires_at - 600):
        return _cached_access_token

    # 2. Пробуем обменять service_token на новый access_token
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.post(
                AUTH_URL,
                json={"service_token": settings.rustore_service_token},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

            data = response.json()
            body = data.get("body", {})

            _cached_access_token = body.get("access_token")
            # Если время жизни не пришло, ставим 24 часа (86400 сек)
            expires_in = body.get("expires_in", 86400)
            _token_expires_at = current_time + expires_in

            logger.info("RuStore Access Token refreshed successfully")
            return _cached_access_token

    except Exception as e:
        # 3. Если RuStore выдал 502 или лежит — откатываемся к старому методу
        logger.warning(
            f"RuStore Auth failed ({type(e).__name__}: {e}). "
            "Falling back to static service_token."
        )
        # Возвращаем service_token напрямую. В этом случае RuStore
        # может принять его как замену access_token (как это было раньше).
        return settings.rustore_service_token


def rustore_send_url() -> str:
    return f"{RUSTORE_BASE_URL}/projects/{settings.rustore_project_id}/messages:send"


def rustore_headers() -> dict:
    # Вызываем получение токена (умное или с откатом)
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
