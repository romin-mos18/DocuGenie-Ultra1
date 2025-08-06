"""
Documents API endpoints for file upload and management
"""
import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database.session import get_db
from ..models.document import Document, DocumentType, DocumentStatus
from ..api.auth import get_current_user

router = APIRouter(prefix="/documents", tags=["Documents"])

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


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
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Upload a document"""
    try:
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
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Create document record
        document_title = title or file.filename
        document = Document(
            title=document_title,
            filename=safe_filename,
            original_filename=file.filename,
            file_size=len(content),
            file_type=file_extension,
            mime_type=file.content_type or "application/octet-stream",
            storage_path=file_path,
            storage_bucket="local",
            storage_key=safe_filename,
            status=DocumentStatus.UPLOADED,
            owner_id=current_user.id
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return {
            "message": "Document uploaded successfully",
            "document_id": document.id,
            "filename": file.filename
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all documents"""
    try:
        # Get documents owned by current user or all if admin
        query = db.query(Document)
        if current_user.role.value != "admin":
            query = query.filter(Document.owner_id == current_user.id)
        
        documents = query.offset(skip).limit(limit).all()
        
        return [
            {
                "id": doc.id,
                "title": doc.title,
                "filename": doc.filename,
                "file_size": doc.file_size,
                "file_type": doc.file_type,
                "status": doc.status.value,
                "document_type": doc.document_type.value if doc.document_type else None
            }
            for doc in documents
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific document"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Check if user has access to this document
        if document.owner_id != current_user.id and current_user.role.value != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        return {
            "id": document.id,
            "title": document.title,
            "filename": document.filename,
            "file_size": document.file_size,
            "file_type": document.file_type,
            "status": document.status.value,
            "document_type": document.document_type.value if document.document_type else None
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document: {str(e)}"
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a document"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Check if user has access to this document
        if document.owner_id != current_user.id and current_user.role.value != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        # Delete file from storage
        file_path = os.path.join(UPLOAD_DIR, document.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete from database
        db.delete(document)
        db.commit()
        
        return {
            "message": f"Document {document_id} deleted successfully"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )
