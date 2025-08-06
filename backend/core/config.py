"""
Application configuration management
"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "DocuGenie Ultra Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000 # Default, can be overridden by env
    
    # Database Configuration
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "docugenie_db"
    DB_USER: str = "user"
    DB_PASSWORD: str = "password"
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/docugenie_db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # OpenSearch Configuration
    OPENSEARCH_HOST: str = "localhost"
    OPENSEARCH_PORT: int = 9200

    # JWT Configuration
    SECRET_KEY: str = "your_super_secret_key_here_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # AI/ML Service Endpoints
    OCR_SERVICE_URL: str = "http://localhost:8002/ocr"
    NER_SERVICE_URL: str = "http://localhost:8003/ner"

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()


# Create necessary directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
