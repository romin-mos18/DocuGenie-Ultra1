"""
Documents API endpoints for file upload and management
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database.session import get_db

router = APIRouter(prefix="/documents", tags=["Documents"])


class DocumentResponse(BaseModel):
    id: int
    title: str
    filename: str
    file_size: int
    file_type: str
    status: str
    document_type: Optional[str] = None


class DocumentUploadResponse(BaseModel):
    message: str
    document_id: Optional[int] = None
    filename: str


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Upload a document"""
    # Validate file type
    allowed_types = ["pdf", "docx", "doc", "txt", "png", "jpg", "jpeg"]
    file_extension = ""
    if file.filename and "." in file.filename:
        file_extension = file.filename.split(".")[-1].lower()
    
    if file_extension not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_extension} not allowed. Allowed types: {', '.join(allowed_types)}"
        )
    
    # For now, return a mock response
    # TODO: Implement actual file upload and storage
    return {
        "message": "Document upload endpoint created",
        "document_id": 1,
        "filename": file.filename
    }


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all documents"""
    # For now, return mock data
    # TODO: Implement actual document listing
    return [
        {
            "id": 1,
            "title": "Sample Medical Report",
            "filename": "sample_report.pdf",
            "file_size": 1024000,
            "file_type": "pdf",
            "status": "processed",
            "document_type": "medical_report"
        }
    ]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific document"""
    # For now, return mock data
    # TODO: Implement actual document retrieval
    return {
        "id": document_id,
        "title": f"Document {document_id}",
        "filename": f"document_{document_id}.pdf",
        "file_size": 1024000,
        "file_type": "pdf",
        "status": "processed",
        "document_type": "medical_report"
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Delete a document"""
    # For now, return a mock response
    # TODO: Implement actual document deletion
    return {
        "message": f"Document {document_id} deletion endpoint created"
    }
