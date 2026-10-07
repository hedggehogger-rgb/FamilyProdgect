from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    APP_ENV: str = "development"
    APP_PORT: int = 8000
    APP_HOST: str = "127.0.0.1"
    STORAGE_FILE_PATH: str = "database.json"
    DB_URL: str = (
        "postgresql://postgres:mysecretpassword@localhost:5432/postgres"
    )
    EXCHANGE_RATE_API_URL: str = "https://open.er-api.com/v6/latest/USD"
    DEFAULT_CURRENCY: str = "RUB"

    # JWT Настройки
    SECRET_KEY: str = (
        "super-secret-family-jwt-key-2026-change-me-in-production"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200


settings = Settings()