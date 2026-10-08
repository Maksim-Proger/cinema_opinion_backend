from zoneinfo import ZoneInfo

MOSCOW_TZ = ZoneInfo("Europe/Moscow")


def premieres_code(year: int, month: int) -> str:
    return f"premieres_{year}_{month:02d}"