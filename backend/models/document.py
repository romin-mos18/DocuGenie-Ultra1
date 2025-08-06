"""
Document model for document management and processing
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum, Float, JSON
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class DocumentType(str, enum.Enum):
    """Document types for classification"""
    MEDICAL_REPORT = "medical_report"
    LAB_RESULT = "lab_result"
    PRESCRIPTION = "prescription"
    CLINICAL_TRIAL = "clinical_trial"
    CONSENT_FORM = "consent_form"
    INSURANCE = "insurance"
    BILLING = "billing"
    ADMINISTRATIVE = "administrative"
    OTHER = "other"


class DocumentStatus(str, enum.Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    ARCHIVED = "archived"


class Document(BaseModel):
    """Document model for document management and processing"""
    __tablename__ = "documents"

    # Basic information
    title = Column(String(500), nullable=False)
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    
    # File information
    file_size = Column(Integer, nullable=False)  # in bytes
    file_type = Column(String(50), nullable=False)  # pdf, docx, etc.
    mime_type = Column(String(100), nullable=False)
    
    # Storage information
    storage_path = Column(String(1000), nullable=False)
    storage_bucket = Column(String(100), nullable=False)
    storage_key = Column(String(500), nullable=False)
    
    # Classification and processing
    document_type = Column(Enum(DocumentType), nullable=True)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED, nullable=False)
    
    # OCR and AI processing results
    ocr_text = Column(Text, nullable=True)
    ocr_confidence = Column(Float, nullable=True)
    classification_confidence = Column(Float, nullable=True)
    extracted_entities = Column(JSON, nullable=True)  # Named entities extracted
    document_metadata = Column(JSON, nullable=True)  # Additional metadata
    
    # Security and compliance
    is_encrypted = Column(String(10), default="false", nullable=False)
    encryption_key_id = Column(String(100), nullable=True)
    retention_date = Column(String(50), nullable=True)
    
    # Relationships
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="documents")
    audit_logs = relationship("AuditLog", back_populates="document")

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', type='{self.document_type}')>"

    def is_processed(self):
        """Check if document is fully processed"""
        return self.status == DocumentStatus.PROCESSED
