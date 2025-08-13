from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum
from datetime import datetime

class AuditAction(enum.Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    DOWNLOAD = "download"
    SHARE = "share"
    LOGIN = "login"
    LOGOUT = "logout"

class AuditLog(BaseModel):
    __tablename__ = "audit_logs"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String)
    
    # Request details
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Additional metadata
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    # Commented out to avoid initialization issues - will be fixed in Phase 3
    # document = relationship("Document", back_populates="audit_logs", foreign_keys=[resource_id])