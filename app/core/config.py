import os
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Nasiya Bro API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://nasiya_user@localhost/nasiya_bro"
    
    # Security
    SECRET_KEY: str = "nasiya-bro-secret-key-2025-change-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 8  # 8 days
    
    # CORS - Handle manually to avoid pydantic parsing issues
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://localhost:5173", 
        "http://localhost:8080", 
        "http://192.168.100.29:19000", 
        "http://192.168.100.29:19006",
        "http://192.168.100.29:8081",
        "http://172.20.10.14:19000",
        "http://172.20.10.14:19006",
        "http://172.20.10.14:8081"
    ]
    
    # Admin credentials (change in production)
    DEFAULT_ADMIN_USERNAME: str = "01234567"
    DEFAULT_ADMIN_PASSWORD: str = "23154216"
    
    # File upload
    UPLOAD_FOLDER: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Timezone
    TIMEZONE: str = "Asia/Tashkent"  # Uzbekistan timezone
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override CORS origins from environment if provided
        cors_env = os.getenv("BACKEND_CORS_ORIGINS")
        if cors_env:
            self.BACKEND_CORS_ORIGINS = [origin.strip() for origin in cors_env.split(",")]
    
    class Config:
        env_file = ".env"

settings = Settings()
