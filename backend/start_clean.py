#!/usr/bin/env python3
"""
Clean Startup Script for DocuGenie Ultra Backend
This script handles all configuration issues and starts the backend properly
"""

import os
import sys
import shutil
from pathlib import Path

def cleanup_corrupted_files():
    """Clean up corrupted model files and other issues"""
    print("🧹 Cleaning up corrupted files...")
    
    # Remove corrupted pickle file
    model_path = Path("models/document_classifier.pkl")
    if model_path.exists():
        try:
            model_path.unlink()
            print("✅ Removed corrupted model file")
        except Exception as e:
            print(f"⚠️ Could not remove corrupted file: {e}")
    
    # Clean up any other corrupted files
    cache_dir = Path("models/cache")
    if cache_dir.exists():
        try:
            shutil.rmtree(cache_dir)
            print("✅ Cleaned model cache directory")
        except Exception as e:
            print(f"⚠️ Could not clean cache: {e}")

def setup_environment():
    """Setup environment variables"""
    print("🔧 Setting up environment...")
    
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
    
    # File Storage
    os.environ.setdefault("UPLOAD_DIR", "uploads")
    os.environ.setdefault("LOG_FILE", "logs/app.log")
    
    # Model Configuration
    os.environ.setdefault("USE_LOCAL_MODELS", "true")
    os.environ.setdefault("SKIP_MODEL_LOADING_ON_ERROR", "true")
    
    # LLM API Keys (Optional)
    # os.environ.setdefault("OPENAI_API_KEY", "your_key_here")
    # os.environ.setdefault("ANTHROPIC_API_KEY", "your_key_here")
    
    print("✅ Environment configured")

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    try:
        import fastapi
        print("✅ FastAPI available")
    except ImportError:
        print("❌ FastAPI not available")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn available")
    except ImportError:
        print("❌ Uvicorn not available")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ Python-dotenv available")
    except ImportError:
        print("❌ Python-dotenv not available")
        return False
    
    print("✅ All required dependencies available")
    return True

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting DocuGenie Ultra Backend...")
    
    try:
        import uvicorn
        from main import app
        
        print("✅ Application loaded successfully")
        print("🌐 Server will be available at: http://localhost:8007")
        print("📚 API documentation at: http://localhost:8007/api/docs")
        print("🔄 Press Ctrl+C to stop the server")
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8007,
            reload=True,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        print("🔧 Please check the error and try again")
        return False

def main():
    """Main startup function"""
    print("=" * 50)
    print("🚀 DocuGenie Ultra Backend - Clean Startup")
    print("=" * 50)
    
    # Clean up corrupted files
    cleanup_corrupted_files()
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependencies check failed. Please install required packages.")
        return False
    
    # Start server
    return start_server()

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
