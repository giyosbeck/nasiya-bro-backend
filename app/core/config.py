import secrets
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Nasiya Bro API"
    VERSION: str = "1.2.0"
    API_V1_STR: str = "/api/v1"
    API_V2_STR: str = "/api/v2"

    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "sqlite:///./nasiya_bro.db"

    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30

    BACKEND_CORS_ORIGINS_RAW: str = ""

    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS_RAW.split(",") if o.strip()]

    DEFAULT_ADMIN_USERNAME: str = ""
    DEFAULT_ADMIN_PASSWORD: str = ""

    UPLOAD_FOLDER: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024

    TIMEZONE: str = "Asia/Tashkent"

    SENTRY_DSN: str = ""

    TRIAL_DAYS: int = 90

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_required()

    def _validate_required(self) -> None:
        is_prod = self.ENVIRONMENT.lower() in {"production", "staging"}

        if not self.SECRET_KEY:
            if is_prod:
                raise RuntimeError(
                    "SECRET_KEY is required in production. "
                    "Generate with: python -c \"import secrets; print(secrets.token_urlsafe(48))\""
                )
            self.SECRET_KEY = secrets.token_urlsafe(48)

        if is_prod and not self.BACKEND_CORS_ORIGINS:
            raise RuntimeError(
                "BACKEND_CORS_ORIGINS must be configured in production."
            )

        if is_prod and (not self.DEFAULT_ADMIN_USERNAME or not self.DEFAULT_ADMIN_PASSWORD):
            raise RuntimeError(
                "DEFAULT_ADMIN_USERNAME and DEFAULT_ADMIN_PASSWORD must be set in production."
            )


settings = Settings()
