"""
DocuGenie Ultra - Main Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers (we'll create these next)
# from api.v1 import documents, auth, health

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle
    """
    # Startup
    print("🚀 Starting DocuGenie Ultra API...")
    # Initialize database connections
    # Initialize AI models
    yield
    # Shutdown
    print("🛑 Shutting down DocuGenie Ultra API...")

# Create FastAPI application
app = FastAPI(
    title="DocuGenie Ultra API",
    description="AI-powered healthcare document management system",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "DocuGenie Ultra API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs"
    }

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "docugenie-api",
        "version": "1.0.0"
    }

# Include routers (uncomment when created)
# app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
# app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])

if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8001)),
        reload=True,
        log_level="info"
    )
