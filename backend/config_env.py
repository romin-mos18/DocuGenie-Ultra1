#!/usr/bin/env python3
"""
Environment Configuration for DocuGenie Ultra Backend
This file sets environment variables programmatically to avoid .env file issues
"""

import os

def setup_environment():
    """Setup environment variables for the backend"""
    
    # Application Settings
    os.environ.setdefault("APP_NAME", "DocuGenie Ultra Backend")
    os.environ.setdefault("APP_VERSION", "1.0.0")
    os.environ.setdefault("DEBUG", "true")
    os.environ.setdefault("HOST", "0.0.0.0")
    os.environ.setdefault("PORT", "8007")
    
    # Database Configuration
    os.environ.setdefault("DB_HOST", "localhost")
    os.environ.setdefault("DB_PORT", "5432")
    os.environ.setdefault("DB_NAME", "docugenie_db")
    os.environ.setdefault("DB_USER", "docugenie")
    os.environ.setdefault("DB_PASSWORD", "docugenie123")
    os.environ.setdefault("DATABASE_URL", "postgresql://docugenie:docugenie123@localhost:5432/docugenie_db")
    os.environ.setdefault("DB_POOL_SIZE", "10")
    os.environ.setdefault("DB_MAX_OVERFLOW", "20")
    
    # Redis Configuration
    os.environ.setdefault("REDIS_HOST", "localhost")
    os.environ.setdefault("REDIS_PORT", "6379")
    os.environ.setdefault("REDIS_PASSWORD", "docugenie123")
    
    # OpenSearch Configuration
    os.environ.setdefault("OPENSEARCH_HOST", "localhost")
    os.environ.setdefault("OPENSEARCH_PORT", "9200")
    
    # JWT Configuration
    os.environ.setdefault("SECRET_KEY", "your_super_secret_key_here_change_in_production")
    os.environ.setdefault("JWT_ALGORITHM", "HS256")
    os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    
    # AI/ML Service Endpoints
    os.environ.setdefault("OCR_SERVICE_URL", "http://localhost:8002/ocr")
    os.environ.setdefault("NER_SERVICE_URL", "http://localhost:8003/ner")
    
    # File Storage
    os.environ.setdefault("UPLOAD_DIR", "uploads")
    os.environ.setdefault("LOG_FILE", "logs/app.log")
    
    # Model Configuration
    os.environ.setdefault("MODEL_CACHE_DIR", "models/cache")
    os.environ.setdefault("USE_LOCAL_MODELS", "true")
    os.environ.setdefault("SKIP_MODEL_LOADING_ON_ERROR", "true")
    
    # LLM API Keys (Optional - system will work without these)
    # Add your actual API keys here:
    os.environ.setdefault("OPENAI_API_KEY", "your_openai_api_key_here")
    os.environ.setdefault("ANTHROPIC_API_KEY", "your_anthropic_api_key_here")
    
    print("✅ Environment variables configured")
    print("ℹ️ OpenAI and Anthropic API keys are optional")
    print("ℹ️ System will use fallback providers if keys are not provided")

if __name__ == "__main__":
    setup_environment()
    print("🔧 Environment setup complete!")
