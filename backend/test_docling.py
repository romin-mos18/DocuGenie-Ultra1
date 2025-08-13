#!/usr/bin/env python3
"""
Test script to verify DocLing service is working
"""
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.docling_service import DoclingService
from services.classification_service import DocumentClassificationService
from services.multilang_service import MultiLanguageService

def test_docling_service():
    """Test the DocLing service with a sample document"""
    print("🧪 Testing DocLing Service...")
    
    # Initialize services
    docling_service = DoclingService()
    classification_service = DocumentClassificationService()
    multilang_service = MultiLanguageService()
    
    print(f"✅ DocLing available: {docling_service.docling_available}")
    print(f"✅ LangChain available: {docling_service.langchain_available}")
    
    # Check if we have any documents to test with
    uploads_dir = Path("./uploads")
    if uploads_dir.exists():
        pdf_files = list(uploads_dir.glob("*.pdf"))
        if pdf_files:
            test_file = str(pdf_files[0])
            print(f"📄 Testing with file: {test_file}")
            
            # Test DocLing processing
            result = docling_service.process_document(test_file, "pdf")
            print(f"📊 Processing result: {result}")
            
            if result.get("success"):
                text = result.get("text", "")
                print(f"📝 Extracted text length: {len(text)}")
                print(f"📝 Text preview: {text[:200]}...")
                
                # Test classification
                classification = classification_service.classify_document(text)
                print(f"🏷️ Classification: {classification}")
                
                # Test entity extraction
                entities = classification_service.extract_entities(text)
                print(f"🔍 Entities extracted: {len(entities) if isinstance(entities, dict) else 0}")
                
                # Test language detection
                language = multilang_service.detect_language(text)
                print(f"🌐 Language: {language}")
            else:
                print(f"❌ Processing failed: {result.get('error')}")
        else:
            print("⚠️ No PDF files found in uploads directory")
    else:
        print("⚠️ Uploads directory not found")
    
    print("✅ DocLing service test completed")

if __name__ == "__main__":
    test_docling_service()
