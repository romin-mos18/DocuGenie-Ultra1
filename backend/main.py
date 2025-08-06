"""
DocuGenie Ultra - Main Application Entry Point
"""
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import configuration
from .core.config import settings

# Import API routes
from .api.auth import router as auth_router
from .api.users import router as users_router
from .api.documents import router as documents_router

# Import database
from .database.session import create_tables

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="AI-powered healthcare document management system API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to DocuGenie Ultra API"}


@app.get("/health", tags=["Monitoring"])
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/api/v1/", tags=["API Info"])
async def api_info():
    return {
        "message": "DocuGenie Ultra API v1",
        "version": "1.0.0",
        "docs": "/api/docs",
        "endpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users",
            "documents": "/api/v1/documents"
        }
    }


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")


if __name__ == "__main__":
    # Development server
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level="info"
    )
