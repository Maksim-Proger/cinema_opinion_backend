from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    firebase_db_url: str
    firebase_cred_path: str
    rustore_project_id: str
    rustore_service_token: str
    api_secret_key: str
    database_url: str
    avatars_storage_path: str = "/var/lib/cinema-opinion/avatars"
    avatar_max_upload_bytes: int = 5 * 1024 * 1024

    class Config:
        env_file = ".env"

settings = Settings()
