from pydantic import BaseModel


class DevicePushTarget(BaseModel):
    userKey: str
    deviceId: str
    pushToken: str
    platform: str

class MovieItem(BaseModel):
    position: int
    kp_id: int | None
    title_ru: str | None
    title_en: str | None
    year: int | None
    type: str | None
    rating_kp: float | None = None
    rating_imdb: float | None = None
    length_min: int | None = None
    premiere_ru: str | None = None
    genres: list[str]
    countries: list[str]
    poster_url: str | None
    poster_preview: str | None
    raw: dict


