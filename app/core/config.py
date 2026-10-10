from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    APP_ENV: str = "development"
    APP_PORT: int = 8000
    APP_HOST: str = "127.0.0.1"
    API_V1_STR: str = "/api/v1"

    # База данных
    DB_URL: str = "postgresql://postgres:mysecretpassword@localhost:5432/postgres"

    # Курсы валют
    EXCHANGE_RATE_API_URL: str = "https://open.er-api.com/v6/latest/USD"
    DEFAULT_CURRENCY: str = "RUB"

    # Безопасность и JWT
    SECRET_KEY: str = "super-secret-family-jwt-key-2026-change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200

    # Фронтенд URL для писем и QR-кодов
    FRONTEND_URL: str = "http://localhost:5173"

    # Почта (SMTP) для восстановления пароля
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@familyfinance.local"
    SMTP_USE_TLS: bool = True

    # Разрешенные источники для фронтенда
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]


settings = Settings()