from app.core.config import settings

RUSTORE_BASE_URL = "https://vkpns.rustore.ru/v1"

def rustore_send_url() -> str:
    return f"{RUSTORE_BASE_URL}/projects/{settings.rustore_project_id}/messages:send"

def rustore_headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.rustore_service_token}",
        "Content-Type": "application/json"
    }
