from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "RailConnect Railway Booking System"
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "super-secret-jwt-key-railconnect-2026-challenge-secure"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    RESET_TOKEN_EXPIRE_MINUTES: int = 15
    DATABASE_URL: str = "sqlite:///./railconnect.db"
    FIRST_SUPERUSER_EMAIL: str = "admin@railconnect.com"
    FIRST_SUPERUSER_PASSWORD: str = "AdminSecret123!"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
