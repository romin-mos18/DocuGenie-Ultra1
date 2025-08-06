"""
Application configuration management
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "DocuGenie Ultra"
    APP_ENV: str = Field(default="development", env="APP_ENV")
    DEBUG: bool = Field(default=True, env="DEBUG")
    API_VERSION: str = "v1"
    
    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://docugenie:docugenie123@localhost:5432/docugenie_db",
        env="DATABASE_URL"
    )
    DB_POOL_SIZE: int = Field(default=20, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=0, env="DB_MAX_OVERFLOW")
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://:docugenie123@localhost:6379/0",
        env="REDIS_URL"
    )
    REDIS_CACHE_TTL: int = Field(default=3600, env="REDIS_CACHE_TTL")
    
    # Security
    SECRET_KEY: str = Field(
        default="your-super-secret-key-change-this-in-production",
        env="SECRET_KEY"
    )
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="ALLOWED_ORIGINS"
    )
    
    # Storage
    UPLOAD_DIR: str = Field(default="./uploads", env="UPLOAD_DIR")
    MAX_UPLOAD_SIZE: int = Field(default=104857600, env="MAX_UPLOAD_SIZE")  # 100MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=["pdf", "png", "jpg", "jpeg", "docx", "txt"],
        env="ALLOWED_EXTENSIONS"
    )
    
    # S3/MinIO
    S3_ENDPOINT_URL: str = Field(default="http://localhost:9000", env="S3_ENDPOINT_URL")
    S3_ACCESS_KEY: str = Field(default="minioadmin", env="S3_ACCESS_KEY")
    S3_SECRET_KEY: str = Field(default="minioadmin123", env="S3_SECRET_KEY")
    S3_BUCKET_NAME: str = Field(default="docugenie-documents", env="S3_BUCKET_NAME")
    S3_REGION: str = Field(default="us-east-1", env="S3_REGION")
    
    # OpenSearch
    OPENSEARCH_URL: str = Field(default="http://localhost:9200", env="OPENSEARCH_URL")
    OPENSEARCH_INDEX: str = Field(default="docugenie-documents", env="OPENSEARCH_INDEX")
    
    # Qdrant
    QDRANT_URL: str = Field(default="http://localhost:6333", env="QDRANT_URL")
    QDRANT_COLLECTION: str = Field(default="document-embeddings", env="QDRANT_COLLECTION")
    
    # AI/ML
    OCR_ENGINE: str = Field(default="paddleocr", env="OCR_ENGINE")
    OCR_CONFIDENCE_THRESHOLD: float = Field(default=0.8, env="OCR_CONFIDENCE_THRESHOLD")
    CLASSIFICATION_CONFIDENCE_THRESHOLD: float = Field(
        default=0.7, 
        env="CLASSIFICATION_CONFIDENCE_THRESHOLD"
    )
    MAX_WORKERS: int = Field(default=4, env="MAX_WORKERS")
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    LOG_FILE: str = Field(default="logs/docugenie.log", env="LOG_FILE")
    
    # Feature Flags
    ENABLE_OCR: bool = Field(default=True, env="ENABLE_OCR")
    ENABLE_CLASSIFICATION: bool = Field(default=True, env="ENABLE_CLASSIFICATION")
    ENABLE_ENTITY_EXTRACTION: bool = Field(default=True, env="ENABLE_ENTITY_EXTRACTION")
    ENABLE_AUDIT_LOGGING: bool = Field(default=True, env="ENABLE_AUDIT_LOGGING")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    def get_db_url(self) -> str:
        """Get database URL with async driver"""
        if self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        return self.DATABASE_URL


# Create global settings instance
settings = Settings()


# Create necessary directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
