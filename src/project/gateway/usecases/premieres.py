from zoneinfo import ZoneInfo

MOSCOW_TZ = ZoneInfo("Europe/Moscow")  # часовой пояс Москвы: «сегодня» и начало месяца считаем по нему


# имя подборки по году и месяцу: (2026, 9) даёт "premieres_2026_09"
def premieres_code(year: int, month: int) -> str:
    return f"premieres_{year}_{month:02d}"