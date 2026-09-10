from app.core.config import settings

KINOPOISK_BASE_URL = "https://kinopoiskapiunofficial.tech/api"

MONTHS = [
    "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
    "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER",
]

def premiers_url() -> str:
    return f"{KINOPOISK_BASE_URL}/v2.2/films/premiers"

def api_key_info_url() -> str:
    return f"{KINOPOISK_BASE_URL}/v1/api_keys/{settings.kinopoisk_api_key}"

def kinopoisk_headers() -> dict:
    return {
        "X-API-KEY": settings.kinopoisk_api_key,
        "accept": "application/json",
    }

def premiers_code(year: int, month_index: int) -> str:
    return f"premieres_{year}_{month_index + 1:02d}"

