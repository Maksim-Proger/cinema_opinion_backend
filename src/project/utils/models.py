from pydantic import BaseModel


# устройство, на которое нужно отправить пуш
class DevicePushTarget(BaseModel):
    userKey: str  # ключ пользователя в Firebase (узел list_users/{userKey})
    deviceId: str  # id устройства
    pushToken: str  # токен, по которому RuStore доставляет пуш на устройство
    platform: str  # платформа устройства (android или ios)

# один фильм в подборке; в таком виде он идёт из collector в хранилище
class MovieItem(BaseModel):
    position: int  # место в подборке (1 — первое)
    kp_id: int | None  # id фильма на Кинопоиске
    title_ru: str | None  # название по-русски
    title_en: str | None  # название по-английски или оригинальное
    year: int | None  # год выпуска
    type: str | None  # фильм или сериал (FILM, TV_SERIES и т. п.)
    rating_kp: float | None = None  # рейтинг Кинопоиска (у премьер не заполняется)
    rating_imdb: float | None = None  # рейтинг IMDb (у премьер не заполняется)
    length_min: int | None = None  # длительность в минутах
    premiere_ru: str | None = None  # дата премьеры в России, ГГГГ-ММ-ДД
    genres: list[str]  # жанры
    countries: list[str]  # страны
    poster_url: str | None  # ссылка на большой постер
    poster_preview: str | None  # ссылка на маленький постер
    raw: dict  # исходный объект фильма из ответа Кинопоиска целиком


