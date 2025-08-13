from sqlalchemy import Column, String, Text, JSON, Float, Enum, ForeignKey, DateTime, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum
from datetime import datetime

class DocumentStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ANALYZING = "analyzing"
    APPROVED = "approved"
    REJECTED = "rejected"

class DocumentType(enum.Enum):
    CLINICAL_TRIAL = "clinical_trial"
    LAB_REPORT = "lab_report"
    MEDICAL_RECORD = "medical_record"
    CONSENT_FORM = "consent_form"
    PRESCRIPTION = "prescription"
    REGULATORY = "regulatory"
    MEDICAL_IMAGE = "medical_image"
    RADIOLOGY_REPORT = "radiology_report"
    PATHOLOGY_REPORT = "pathology_report"
    DISCHARGE_SUMMARY = "discharge_summary"
    OPERATION_NOTE = "operation_note"
    OTHER = "other"

class ProcessingMethod(enum.Enum):
    DOCLING = "docling"
    PYMUPDF = "pymupdf"
    PYTHON_DOCX = "python_docx"
    PANDAS = "pandas"
    TESSERACT = "tesseract"
    TEXT_READER = "text_reader"
    BASIC = "basic"

class Document(BaseModel):
    __tablename__ = "documents"
    
    # Basic file information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    file_path = Column(String(500), nullable=False)
    file_size = Column(Float)
    mime_type = Column(String(100))
    file_extension = Column(String(20))
    
    # Status and workflow
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING)
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    
    # Classification
    document_type = Column(Enum(DocumentType))
    classification_confidence = Column(Float)
    classification_result = Column(JSON)
    
    # Healthcare specific fields
    patient_id = Column(String(100))
    provider_id = Column(String(100))
    facility_id = Column(String(100))
    encounter_date = Column(DateTime)
    
    # AI processing results - Enhanced for Docling
    processing_method = Column(Enum(ProcessingMethod))
    processing_confidence = Column(Float)
    processing_time = Column(Float)
    
    # Text extraction results
    extracted_text = Column(Text)
    text_length = Column(Integer)
    word_count = Column(Integer)
    line_count = Column(Integer)
    
    # AI analysis results
    ai_models_used = Column(JSON)  # List of AI models used
    layout_analysis = Column(JSON)  # Docling layout analysis results
    table_recognition = Column(JSON)  # Table structure recognition
    entities_extracted = Column(JSON)  # Named entities found
    summary = Column(Text)  # AI-generated summary
    
    # Metadata and processing details
    processing_metadata = Column(JSON)  # Detailed processing metadata
    error_logs = Column(JSON)  # Any errors during processing
    retry_count = Column(Integer, default=0)
    
    # Legacy fields for backward compatibility
    ocr_text = Column(Text)  # Legacy OCR text field
    ocr_confidence = Column(Float)  # Legacy OCR confidence
    ocr_engine = Column(String(50))  # Legacy OCR engine
    
    # User and ownership
    uploaded_by = Column(String, ForeignKey("users.id"))
    processed_by = Column(String)  # System or user who processed
    reviewed_by = Column(String, ForeignKey("users.id"))
    reviewed_at = Column(DateTime)
    
    # Relationships - Commented out for now to avoid initialization issues
    # audit_logs = relationship("AuditLog", back_populates="document")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.processing_started_at:
            self.processing_started_at = datetime.utcnow()
    
    def update_processing_status(self, status: DocumentStatus, **kwargs):
        """Update processing status and related fields"""
        self.status = status
        
        if status == DocumentStatus.PROCESSING:
            self.processing_started_at = datetime.utcnow()
        elif status in [DocumentStatus.COMPLETED, DocumentStatus.FAILED]:
            self.processing_completed_at = datetime.utcnow()
        
        # Update other fields if provided
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_processing_results(self, results: dict):
        """Set processing results from Docling service"""
        if results.get("success"):
            self.processing_method = ProcessingMethod(results.get("processing_method", "basic"))
            self.processing_confidence = results.get("confidence", 0.0)
            self.extracted_text = results.get("text", "")
            self.word_count = results.get("word_count", 0)
            self.processing_metadata = results.get("metadata", {})
            
            # Extract AI models used
            if "ai_models" in results.get("metadata", {}):
                self.ai_models_used = results["metadata"]["ai_models"]
            
            # Set text statistics
            if self.extracted_text:
                self.text_length = len(self.extracted_text)
                self.line_count = len(self.extracted_text.split('\n'))
            
            self.status = DocumentStatus.COMPLETED
        else:
            self.status = DocumentStatus.FAILED
            self.error_logs = {"error": results.get("error", "Unknown error")}
    
    def get_processing_summary(self) -> dict:
        """Get a summary of processing results"""
        return {
            "id": self.id,
            "filename": self.filename,
            "status": self.status.value,
            "processing_method": self.processing_method.value if self.processing_method else None,
            "confidence": self.processing_confidence,
            "word_count": self.word_count,
            "processing_time": self.processing_time,
            "ai_models": self.ai_models_used,
            "document_type": self.document_type.value if self.document_type else None,
            "extracted_text_preview": self.extracted_text[:200] + "..." if self.extracted_text and len(self.extracted_text) > 200 else self.extracted_text
        }
    
    def is_processed(self) -> bool:
        """Check if document has been processed"""
        return self.status in [DocumentStatus.COMPLETED, DocumentStatus.APPROVED]
    
    def has_errors(self) -> bool:
        """Check if document has processing errors"""
        return self.status == DocumentStatus.FAILED or bool(self.error_logs)
    
    def get_processing_duration(self) -> float:
        """Get processing duration in seconds"""
        if self.processing_started_at and self.processing_completed_at:
            return (self.processing_completed_at - self.processing_started_at).total_seconds()
        return None