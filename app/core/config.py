from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    firebase_db_url: str
    firebase_cred_path: str
    rustore_project_id: str
    rustore_service_token: str

    class Config:
        env_file = ".env"
settings = Settings()
