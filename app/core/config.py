from typing import List, Optional
from pydantic import validator
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
    
    # CORS
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
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Admin credentials (change in production)
    DEFAULT_ADMIN_USERNAME: str = "01234567"
    DEFAULT_ADMIN_PASSWORD: str = "23154216"
    
    # File upload
    UPLOAD_FOLDER: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Timezone
    TIMEZONE: str = "Asia/Tashkent"  # Uzbekistan timezone
    
    class Config:
        env_file = ".env"

settings = Settings() 