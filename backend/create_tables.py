#!/usr/bin/env python3
"""
Script to create database tables
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from models.base import Base
from models.user import User
from models.document import Document
from models.audit_log import AuditLog
from core.config import settings

def create_tables():
    """Create all database tables"""
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables created successfully!")
        print(f"Database URL: {settings.DATABASE_URL}")
        
        # List created tables
        inspector = engine.dialect.inspector(engine)
        tables = inspector.get_table_names()
        print(f"Created tables: {', '.join(tables)}")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_tables()
