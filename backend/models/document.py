"""
Document Models
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

Base = declarative_base()

class DocumentStatus(Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"
    COMPLETED = "completed"

class DocumentType(Enum):
    MEDICAL_REPORT = "medical_report"
    LAB_RESULT = "lab_result"
    PRESCRIPTION = "prescription"
    CLINICAL_TRIAL = "clinical_trial"
    CONSENT_FORM = "consent_form"
    INSURANCE = "insurance"
    BILLING = "billing"
    ADMINISTRATIVE = "administrative"
    OTHER = "other"
    UNKNOWN = "unknown"

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    
    # Classification fields
    document_type = Column(String(50), default="unknown")
    classification_confidence = Column(Float, default=0.0)
    
    # Status and timestamps
    status = Column(String(50), default="uploaded")
    upload_date = Column(DateTime, default=datetime.utcnow)
    processed_date = Column(DateTime, nullable=True)
    
    # AI analysis results
    extracted_text = Column(Text, nullable=True)
    ai_analysis = Column(Text, nullable=True)  # JSON string
    entities_extracted = Column(Text, nullable=True)  # JSON string
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert document to dictionary for API responses"""
        return {
            "id": str(self.id),
            "filename": self.filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "document_type": self.document_type,
            "documentType": self.document_type.replace('_', ' ').title() if self.document_type != "unknown" else "Unknown",
            "classification_confidence": self.classification_confidence,
            "status": self.status,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "processed_date": self.processed_date.isoformat() if self.processed_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "confidence": self.classification_confidence,
            "classification": {
                "document_type": self.document_type,
                "confidence": self.classification_confidence,
                "success": self.status == "processed"
            }
        }