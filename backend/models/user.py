from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    RESEARCHER = "researcher"
    VIEWER = "viewer"

class UserStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Healthcare specific
    license_number = Column(String(100))
    department = Column(String(100))
    phone = Column(String(20))
    
    # Computed property
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"