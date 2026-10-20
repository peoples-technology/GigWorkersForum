from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "CITU Kerala Gig Workers Union Platform"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "dev_secret_key_citu_solidarity_change_in_production_32b"
    
    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/citu_gigworkers"
    DB_POOL_SIZE: int = 15
    DB_MAX_OVERFLOW: int = 5

    # Storage
    UPLOAD_DIR: str = "/tmp/citu_uploads"
    
    # Flags & Mocks
    MOCK_SMS: bool = True
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
