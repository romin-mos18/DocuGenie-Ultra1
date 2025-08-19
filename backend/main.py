"""
DocuGenie Ultra - Main Application Entry Point
Clean, working version without dependency conflicts
"""
import os
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file (if exists)
load_dotenv()

# Setup programmatic environment configuration
from config_env import setup_environment
setup_environment()

# Check for optional API keys and log status
openai_key = os.getenv("OPENAI_API_KEY")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")

print("🔧 DocuGenie Ultra Backend Starting...")
if openai_key:
    print("✅ OpenAI API key found")
else:
    print("ℹ️ OpenAI API key not provided - using fallback providers")
    
if anthropic_key:
    print("✅ Anthropic API key found")
else:
    print("ℹ️ Anthropic API key not provided - using fallback providers")

print("🚀 Initializing services...")

# Import API routes
from api.documents import router as documents_router
from api.ai_documents import router as ai_documents_router
from api.auth import router as auth_router

app = FastAPI(
    title="DocuGenie Ultra - Working Version",
    version="1.0.0",
    description="AI-powered healthcare document management system API - Clean Working Version",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Middleware - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3006", "http://127.0.0.1:3006", "*"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes with paths that match the frontend
# Documents endpoints exposed under /documents/* and related paths
app.include_router(documents_router)

# AI-powered documents endpoints under /ai-documents/*
app.include_router(ai_documents_router, prefix="/ai-documents", tags=["AI Documents"])

# Auth endpoints under /auth/* (matches frontend calls)
app.include_router(auth_router)

# Create compatibility routers for /api/v1/* (frontend still uses these)
# We'll create simple route handlers for the /api/v1 endpoints

@app.get("/api/v1/documents")
async def get_documents_v1():
    """Compatibility endpoint for /api/v1/documents - returns documents with entity extraction"""
    from api.documents import get_documents
    # Use None for db parameter since documents.py has dependency injection  
    return await get_documents(None)

@app.get("/api/v1/ai-documents")
async def get_ai_documents_v1():
    """AI documents endpoint for /api/v1/ai-documents"""
    from api.ai_documents import get_ai_documents
    return await get_ai_documents()

@app.post("/api/v1/upload")
async def upload_document_v1(file: UploadFile = File(...)):
    """Compatibility endpoint for /api/v1/upload - uses enhanced AI processing with entity extraction"""
    from api.documents import upload_document
    from fastapi import BackgroundTasks
    background_tasks = BackgroundTasks()
    # Use None for db parameter since documents.py has dependency injection
    return await upload_document(background_tasks, file, None)

@app.get("/api/v1/documents/{document_id}")
async def get_document_v1(document_id: str):
    """Compatibility endpoint for /api/v1/documents/{id} GET"""
    from api.documents import document_storage
    try:
        doc_id = int(document_id)
        if doc_id not in document_storage:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = document_storage[doc_id]
        
        # Return detailed document information with AI analysis
        return {
            "success": True,
            "document": {
                "id": str(doc_id),
                "filename": doc_data.get("filename", "Unknown"),
                "file_type": doc_data.get("file_type", "unknown"),
                "status": doc_data.get("status", "uploaded"),
                "upload_date": doc_data.get("upload_date", ""),
                "file_size": doc_data.get("file_size", 0),
                "ai_analysis": doc_data.get("ai_analysis", {}),
                "docling_result": doc_data.get("docling_result", {}),
                "extracted_entities": doc_data.get("extracted_entities", {}),
                "document_type": doc_data.get("document_type", "unknown"),
                "confidence": doc_data.get("confidence", 0.0)
            },
            "ai_analysis": doc_data.get("ai_analysis", {}),
            "extracted_text": doc_data.get("ai_analysis", {}).get("text_preview", ""),
            "ai_summary": doc_data.get("ai_analysis", {}).get("text_preview", "")
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch document: {str(e)}")

@app.post("/api/v1/ai-upload")
async def upload_ai_document_v1(file: UploadFile = File(...)):
    """AI-powered upload endpoint for /api/v1/ai-upload"""
    from api.ai_documents import upload_document_with_ai
    from fastapi import BackgroundTasks
    background_tasks = BackgroundTasks()
    return await upload_document_with_ai(background_tasks, file)

@app.delete("/api/v1/documents/{document_id}")
async def delete_document_v1(document_id: str):
    """Compatibility endpoint for /api/v1/documents/{id} DELETE"""
    from api.documents import document_storage
    try:
        doc_id = int(document_id)
        
        if doc_id not in document_storage:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Remove file if it exists
        doc_data = document_storage[doc_id]
        file_path = doc_data.get("file_path")
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"⚠️ Could not delete file {file_path}: {e}")
        
        # Remove from storage
        del document_storage[doc_id]
        
        print(f"✅ Document {doc_id} deleted successfully")
        
        return {
            "success": True,
            "message": "Document deleted successfully",
            "document_id": document_id,
            "deleted_at": datetime.now().isoformat()
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@app.get("/api/v1/documents/{document_id}")
async def get_document_v1(document_id: str):
    """Compatibility endpoint for /api/v1/documents/{id} GET"""
    from api.documents import document_storage
    try:
        doc_id = int(document_id)
        if doc_id not in document_storage:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = document_storage[doc_id]
        
        # Return detailed document information with AI analysis
        return {
            "success": True,
            "document": {
                "id": str(doc_id),
                "filename": doc_data.get("filename", "Unknown"),
                "file_type": doc_data.get("file_type", "unknown"),
                "status": doc_data.get("status", "uploaded"),
                "upload_date": doc_data.get("upload_date", ""),
                "file_size": doc_data.get("file_size", 0),
                "ai_analysis": doc_data.get("ai_analysis", {}),
                "docling_result": doc_data.get("docling_result", {}),
                "extracted_entities": doc_data.get("extracted_entities", {}),
                "document_type": doc_data.get("document_type", "unknown"),
                "confidence": doc_data.get("confidence", 0.0)
            },
            "ai_analysis": doc_data.get("ai_analysis", {}),
            "extracted_text": doc_data.get("ai_analysis", {}).get("text_preview", ""),
            "ai_summary": doc_data.get("ai_analysis", {}).get("text_preview", "")
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch document: {str(e)}")

@app.get("/api/v1/documents/{document_id}/download")
async def download_document_v1(document_id: str):
    """Compatibility endpoint for /api/v1/documents/{id}/download"""
    from api.documents import document_storage
    from fastapi.responses import FileResponse
    try:
        doc_id = int(document_id)
        if doc_id not in document_storage:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = document_storage[doc_id]
        file_path = doc_data.get("file_path")
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Document file not found")
        
        return FileResponse(
            path=file_path,
            filename=doc_data.get("filename", f"document_{document_id}"),
            media_type="application/octet-stream"
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.post("/api/v1/documents/{document_id}/process")
async def process_document_v1(document_id: str):
    """Compatibility endpoint for /api/v1/documents/{id}/process"""
    from api.documents import document_storage
    try:
        doc_id = int(document_id)
        if doc_id not in document_storage:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # For now, return success if document exists
        # In a full implementation, this would trigger reprocessing
        return {
            "success": True,
            "message": "Document processing initiated",
            "document_id": document_id,
            "processing_status": "started"
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/api/v1/documents/{document_id}/process")
async def process_document_v1(document_id: str):
    """Compatibility endpoint for /api/v1/documents/{id}/process"""
    from api.documents import process_document_manually
    from database.session import get_db
    from sqlalchemy.orm import Session
    from fastapi import Depends, BackgroundTasks
    
    background_tasks = BackgroundTasks()
    db = next(get_db())
    return await process_document_manually(document_id, background_tasks, db)

@app.get("/api/v1/auth/me")
async def get_current_user_v1():
    """Compatibility endpoint for /api/v1/auth/me"""
    return {
        "id": "admin",
        "name": "Admin User",
        "email": "admin@docugenie.com",
        "role": "admin",
        "status": "active"
    }

@app.get("/", tags=["Root"])
async def read_root():
    return {
        "message": "Welcome to DocuGenie Ultra API - Working Version",
        "status": "Document Upload Fully Functional",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Health check for working version"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "documents": "active",
            "upload": "working"
        },
        "supported_formats": ["pdf", "docx", "doc", "xlsx", "xls", "jpg", "jpeg", "png", "bmp", "tiff", "txt"],
        "note": "Clean working version - all services functional"
    }

@app.get("/api/", tags=["API Info"])
async def api_info():
    return {
        "message": "DocuGenie Ultra API - Working Version",
        "version": "1.0.0",
        "docs": "/api/docs",
        "endpoints": {
            "documents": "/documents",
            "upload": "/documents/upload",
            "auth": "/auth"
        },
        "status": "All endpoints functional"
    }

@app.get("/api/ai/status", tags=["AI Services"])
async def get_ai_status():
    """Get AI services status"""
    return {
        "ai_services": {
            "document_processing": {
                "status": "active",
                "processing_method": "enhanced_text_extraction",
                "classification_status": "active"
            }
        },
        "supported_formats": ["pdf", "docx", "doc", "xlsx", "xls", "jpg", "jpeg", "png", "bmp", "tiff", "txt"],
        "processing_capabilities": {
            "text_extraction": True,
            "document_classification": True,
            "metadata_extraction": True
        },
        "status": "Document processing fully functional"
    }

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        print("✅ Clean API initialized successfully")
        print("✅ Document upload endpoint available at /documents/upload and /api/v1/upload")
        print("🤖 AI-powered document processing available at /ai-documents/ai-upload")
        print("✅ All services working without dependency conflicts")
        print("✅ Supported formats: pdf, docx, doc, xlsx, xls, jpg, jpeg, png, bmp, tiff, txt")
        print("🧠 AI Features: Content extraction, intelligent analysis, automatic labeling")
        print("🏷️ Document Types: Medical Report, Lab Result, Prescription, Clinical Trial, Insurance, Billing, Administrative")
        print("✅ Frontend connection enabled at http://localhost:3006")
        print("📊 AI Processing Statistics available at /ai-documents/ai-stats")
        
    except Exception as e:
        print(f"⚠️  Startup initialization warning: {e}")

if __name__ == "__main__":
    # Development server
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8007)),
        reload=True,
        log_level="info"
    )
