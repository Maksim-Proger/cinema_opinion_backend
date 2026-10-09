from pydantic_settings import BaseSettings


# настройки сервиса из файла .env; если чего-то не хватает, сервис не запустится
class Settings(BaseSettings):
    firebase_db_url: str  # адрес базы Firebase Realtime Database
    firebase_cred_path: str  # путь к файлу ключа сервисного аккаунта Firebase
    rustore_project_id: str  # id проекта в RuStore (нужен для отправки пушей)
    rustore_service_token: str  # токен сервиса RuStore для отправки пушей
    api_secret_key: str  # ключ, который приложение присылает в заголовке X-API-Key
    database_url: str  # адрес подключения к PG
    kinopoisk_api_key: str  # ключ API Кинопоиска
    avatars_storage_path: str = "/var/lib/cinema-opinion/avatars"  # папка на сервере, где лежат файлы аватарок
    avatar_max_upload_bytes: int = 5 * 1024 * 1024  # максимальный размер загружаемой аватарки: 5 МБ

    class Config:
        env_file = ".env"  # откуда читать значения: файл .env в папке запуска сервиса


settings = Settings()  # готовый объект настроек; остальные модули импортируют его
