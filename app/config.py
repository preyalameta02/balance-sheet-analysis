from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./test.db"
    
    # JWT
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OpenAI
    openai_api_key: str = ""
    
    # File Upload
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings()

# Override database URL for Railway deployment
if os.getenv("DATABASE_URL"):
    settings.database_url = os.getenv("DATABASE_URL")
    # Convert Railway's postgres:// to postgresql:// for SQLAlchemy
    if settings.database_url.startswith("postgres://"):
        settings.database_url = settings.database_url.replace("postgres://", "postgresql://", 1)

# Override allowed origins for production
if os.getenv("FRONTEND_URL"):
    settings.allowed_origins.append(os.getenv("FRONTEND_URL")) 