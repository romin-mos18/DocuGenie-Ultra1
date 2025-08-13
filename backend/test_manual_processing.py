#!/usr/bin/env python3
"""
Manual test script to process existing documents and verify DocLing integration
"""
import os
import sys
from pathlib import Path
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.docling_service import DoclingService
from services.classification_service import DocumentClassificationService
from services.multilang_service import MultiLanguageService

def test_manual_document_processing():
    """Manually process existing documents to test DocLing integration"""
    print("🧪 Manual Document Processing Test...")
    
    # Initialize services
    docling_service = DoclingService()
    classification_service = DocumentClassificationService()
    multilang_service = MultiLanguageService()
    
    print(f"✅ DocLing available: {docling_service.docling_available}")
    
    # Check for existing documents
    uploads_dir = Path("./uploads")
    if not uploads_dir.exists():
        print("❌ Uploads directory not found")
        return
    
    pdf_files = list(uploads_dir.glob("*.pdf"))
    if not pdf_files:
        print("❌ No PDF files found in uploads directory")
        return
    
    print(f"📄 Found {len(pdf_files)} PDF files")
    
    # Process each document manually
    for pdf_file in pdf_files:
        print(f"\n🔄 Processing: {pdf_file.name}")
        
        try:
            # Process with DocLing
            docling_result = docling_service.process_document(str(pdf_file), "pdf")
            print(f"📊 DocLing result: {docling_result.get('success', False)}")
            
            if docling_result.get("success"):
                text = docling_result.get("text", "")
                print(f"📝 Text extracted: {len(text)} characters")
                
                # Classify document
                classification_result = classification_service.classify_document(text)
                print(f"🏷️ Classification: {classification_result.get('document_type', 'unknown')}")
                print(f"🎯 Confidence: {classification_result.get('confidence', 0.0):.2f}")
                
                # Extract entities
                entities_result = classification_service.extract_entities(text)
                print(f"🔍 Entities: {len(entities_result) if isinstance(entities_result, dict) else 0}")
                
                # Detect language
                language_result = multilang_service.detect_language(text)
                print(f"🌐 Language: {language_result.get('primary_language', 'unknown')}")
                
                # Save results to a test file
                test_results = {
                    "filename": pdf_file.name,
                    "docling_result": docling_result,
                    "classification": classification_result,
                    "entities": entities_result,
                    "language": language_result,
                    "status": "processed"
                }
                
                test_file = f"test_results_{pdf_file.stem}.json"
                with open(test_file, 'w') as f:
                    json.dump(test_results, f, indent=2, default=str)
                
                print(f"💾 Results saved to: {test_file}")
                
            else:
                print(f"❌ DocLing failed: {docling_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error processing {pdf_file.name}: {e}")
    
    print("\n✅ Manual processing test completed")

if __name__ == "__main__":
    test_manual_document_processing()
