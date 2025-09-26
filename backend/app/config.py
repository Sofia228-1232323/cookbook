from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    database_url: str = "sqlite:///./cookbook.db"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    access_token_expire_minutes: int = 30
    upload_dir: str = "uploads"
    max_file_size: int = 5242880  # 5MB
    
    class Config:
        env_file = ".env"


settings = Settings()

