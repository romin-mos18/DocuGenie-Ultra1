"""
AuditLog model for tracking system activities and compliance
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class AuditAction(str, enum.Enum):
    """Audit action types"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    PROCESS = "process"
    CLASSIFY = "classify"
    EXTRACT = "extract"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    ROLE_CHANGE = "role_change"
    STATUS_CHANGE = "status_change"


class AuditResource(str, enum.Enum):
    """Audit resource types"""
    USER = "user"
    DOCUMENT = "document"
    SYSTEM = "system"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    PROCESSING = "processing"


class AuditLog(BaseModel):
    """AuditLog model for tracking system activities and compliance"""
    __tablename__ = "audit_logs"

    # Action details
    action = Column(Enum(AuditAction), nullable=False)
    resource_type = Column(Enum(AuditResource), nullable=False)
    resource_id = Column(String(100), nullable=True)  # ID of the affected resource
    
    # User information
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_email = Column(String(255), nullable=True)  # Cached for historical records
    user_ip = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    
    # Action details
    description = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)  # Additional action details
    success = Column(String(10), default="true", nullable=False)  # true/false
    
    # Security and compliance
    session_id = Column(String(100), nullable=True)
    request_id = Column(String(100), nullable=True)  # For request tracing
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    document = relationship("Document", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id})>"

    @property
    def is_successful(self):
        """Check if the action was successful"""
        return self.success == "true"
