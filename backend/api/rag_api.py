#!/usr/bin/env python3
"""
RAG API Router
Provides endpoints for document processing, semantic search, and AI-powered Q&A
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime
import logging

# Import RAG service
from services.rag_service import RAGService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG - AI Document Intelligence"])

# Initialize RAG service
rag_service = RAGService()

# Pydantic models for request/response
class SearchRequest(BaseModel):
    query: str
    limit: int = 5

class QuestionRequest(BaseModel):
    question: str
    context_limit: int = 3

class DocumentProcessRequest(BaseModel):
    file_path: str
    file_type: str

@router.get("/status")
async def get_rag_status():
    """Get RAG service status and capabilities"""
    try:
        status = rag_service.get_rag_status()
        return {
            "success": True,
            "rag_status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Failed to get RAG status: {e}")
        raise HTTPException(status_code=500, detail=f"Status fetch failed: {str(e)}")

@router.post("/process")
async def process_document_for_rag(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Process document and prepare it for RAG pipeline"""
    try:
        logger.info(f"🔄 RAG document processing: {file.filename}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Get file extension
        file_extension = file.filename.split('.')[-1].lower()
        file_type = file_extension
        
        # Check if file type is supported
        supported_types = ['pdf', 'docx', 'doc', 'xlsx', 'xls', 'jpg', 'jpeg', 'png', 'bmp', 'tiff', 'txt']
        if file_type not in supported_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_type}. Supported: {', '.join(supported_types)}"
            )
        
        # Create uploads directory if it doesn't exist
        import os
        upload_dir = "./uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"📁 File saved for RAG processing: {file_path}")
        
        # Process document for RAG
        result = rag_service.process_document_for_rag(file_path, file_type)
        
        if not result["success"]:
            raise HTTPException(
                status_code=500, 
                detail=f"RAG processing failed: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "message": "Document processed and prepared for RAG pipeline",
            "filename": file.filename,
            "file_type": file_type,
            "file_size": len(content),
            "rag_result": result,
            "ai_models_used": ["DocLayNet", "TableFormer", "sentence-transformers"],
            "capabilities_unlocked": [
                "Semantic search",
                "AI-powered Q&A", 
                "Document intelligence",
                "Vector embeddings"
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ RAG document processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"RAG processing failed: {str(e)}")

@router.post("/search")
async def search_documents(request: SearchRequest):
    """Search documents using semantic similarity"""
    try:
        logger.info(f"🔍 RAG semantic search: {request.query}")
        
        result = rag_service.search_documents(request.query, request.limit)
        
        if not result["success"]:
            raise HTTPException(
                status_code=500, 
                detail=f"Search failed: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "search_results": result,
            "search_metadata": {
                "query": request.query,
                "limit": request.limit,
                "total_results": result["total_results"],
                "search_timestamp": result["search_timestamp"]
            }
        }
        
    except Exception as e:
        logger.error(f"❌ RAG search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/ask")
async def ask_question(request: QuestionRequest):
    """Ask questions and get AI-powered answers using RAG pipeline"""
    try:
        logger.info(f"❓ RAG Q&A: {request.question}")
        
        result = rag_service.answer_question(request.question, request.context_limit)
        
        if not result["success"]:
            raise HTTPException(
                status_code=500, 
                detail=f"Q&A failed: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "qa_result": result,
            "ai_capabilities": {
                "context_retrieval": True,
                "semantic_understanding": True,
                "answer_generation": True,
                "source_tracking": True
            }
        }
        
    except Exception as e:
        logger.error(f"❌ RAG Q&A failed: {e}")
        raise HTTPException(status_code=500, detail=f"Q&A failed: {str(e)}")

@router.get("/documents")
async def get_processed_documents():
    """Get list of documents processed for RAG"""
    try:
        documents = []
        
        for doc_id, doc_info in rag_service.processed_documents.items():
            doc_summary = rag_service.get_document_summary(doc_id)
            if doc_summary["success"]:
                documents.append(doc_summary)
        
        return {
            "success": True,
            "documents": documents,
            "total_documents": len(documents),
            "total_chunks": sum(doc.get("chunk_count", 0) for doc in documents),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get processed documents: {e}")
        raise HTTPException(status_code=500, detail=f"Document fetch failed: {str(e)}")

@router.get("/documents/{document_id}")
async def get_document_details(document_id: str):
    """Get detailed information about a processed document"""
    try:
        doc_summary = rag_service.get_document_summary(document_id)
        
        if not doc_summary["success"]:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "success": True,
            "document": doc_summary,
            "rag_capabilities": {
                "searchable": True,
                "question_answerable": True,
                "vector_embedded": True
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get document details: {e}")
        raise HTTPException(status_code=500, detail=f"Document details fetch failed: {str(e)}")

@router.get("/capabilities")
async def get_rag_capabilities():
    """Get comprehensive RAG capabilities and AI models"""
    try:
        status = rag_service.get_rag_status()
        
        capabilities = {
            "document_processing": {
                "pdf": "Docling (DocLayNet + TableFormer)",
                "docx": "python-docx",
                "xlsx": "pandas",
                "images": "Tesseract OCR",
                "txt": "Direct reading"
            },
            "ai_models": {
                "layout_analysis": "DocLayNet",
                "table_recognition": "TableFormer", 
                "embeddings": "sentence-transformers/all-MiniLM-L6-v2",
                "text_splitting": "RecursiveCharacterTextSplitter"
            },
            "rag_pipeline": {
                "document_ingestion": True,
                "text_chunking": True,
                "vector_embeddings": True,
                "semantic_search": True,
                "context_retrieval": True,
                "question_answering": True
            },
            "healthcare_optimization": {
                "medical_document_processing": True,
                "lab_result_extraction": True,
                "clinical_document_analysis": True,
                "regulatory_compliance": True
            }
        }
        
        return {
            "success": True,
            "rag_capabilities": capabilities,
            "service_status": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get RAG capabilities: {e}")
        raise HTTPException(status_code=500, detail=f"Capabilities fetch failed: {str(e)}")

@router.post("/demo")
async def run_rag_demo():
    """Run a demonstration of RAG capabilities"""
    try:
        logger.info("🎯 Running RAG demo")
        
        # Check if we have any processed documents
        if not rag_service.processed_documents:
            return {
                "success": False,
                "message": "No documents processed yet. Please process a document first.",
                "next_steps": [
                    "Upload a document using /rag/process",
                    "Wait for processing to complete",
                    "Try searching or asking questions"
                ]
            }
        
        # Get demo statistics
        status = rag_service.get_rag_status()
        
        demo_results = {
            "documents_processed": status["documents_processed"],
            "total_chunks": status["total_chunks"],
            "vector_store_ready": status["vector_store_ready"],
            "sample_documents": list(rag_service.processed_documents.keys())[:3],
            "demo_queries": [
                "What is the main topic of the documents?",
                "How can I implement the described solution?",
                "What are the key requirements mentioned?"
            ]
        }
        
        return {
            "success": True,
            "message": "RAG demo ready! Try the sample queries or ask your own questions.",
            "demo_data": demo_results,
            "try_endpoints": [
                "POST /rag/search - Search documents",
                "POST /rag/ask - Ask questions",
                "GET /rag/documents - View processed documents"
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ RAG demo failed: {e}")
        raise HTTPException(status_code=500, detail=f"Demo failed: {str(e)}")
