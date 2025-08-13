#!/usr/bin/env python3
"""
Test script to populate document storage with processed documents
"""
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def populate_test_documents():
    """Populate document storage with test documents"""
    try:
        from api.documents import document_storage, document_counter
        
        print("🧪 Populating document storage with test documents...")
        
        # Create a test document with complete data structure
        test_doc_id = 1
        document_storage[test_doc_id] = {
            "id": test_doc_id,
            "filename": "test_lab_report.pdf",
            "file_type": "pdf",
            "file_path": "./uploads/test_lab_report.pdf",
            "file_size": 1024000,
            "status": "processed",
            "upload_date": datetime.now().isoformat(),
            "ai_analysis": {
                "classification": {
                    "document_type": "lab_result",
                    "confidence": 0.85
                },
                "entities": {
                    "dates": ["08/12/2025", "1995-12-15"],
                    "names": ["Michael Brown", "Dr. Sarah Johnson"],
                    "organizations": ["LabCorp", "City Hospital"],
                    "medical_terms": ["patient", "laboratory", "test", "result", "glucose", "cholesterol"],
                    "numbers": ["94", "210", "13.5", "665680"]
                },
                "language": {
                    "primary_language": "en",
                    "confidence": 0.95
                },
                "processing_timestamp": datetime.now().isoformat(),
                "text_preview": "LABORATORY REPORT LabCorp Report Date: 08/12/2025 Patient: Michael Brown DOB: 1995-12-15 MRN: 665680 Test Results: Glucose mg/dL 70-100 94 Cholesterol mg/dL <200 210 Hemoglobin g/dL 12-16 13.5...",
                "word_count": 150,
                "key_information": {
                    "dates_found": ["08/12/2025", "1995-12-15"],
                    "potential_names": ["Michael Brown", "Dr. Sarah Johnson"],
                    "numbers": ["94", "210", "13.5", "665680"],
                    "emails": ["michael.brown@email.com"],
                    "phone_numbers": ["(555) 123-4567"],
                    "total_words": 150,
                    "text_preview": "LABORATORY REPORT LabCorp Report Date: 08/12/2025 Patient: Michael Brown..."
                }
            },
            "docling_result": {
                "success": True,
                "text": "LABORATORY REPORT LabCorp Report Date: 08/12/2025 Patient: Michael Brown DOB: 1995-12-15 MRN: 665680 Test Results: Glucose mg/dL 70-100 94 Cholesterol mg/dL <200 210 Hemoglobin g/dL 12-16 13.5 White Blood Cell Count 4.5-11.0 7.6 Platelet Count 150-450 216",
                "processing_time": 2.3
            },
            "extracted_entities": {
                "dates": ["08/12/2025", "1995-12-15"],
                "names": ["Michael Brown", "Dr. Sarah Johnson"],
                "organizations": ["LabCorp", "City Hospital"],
                "medical_terms": ["patient", "laboratory", "test", "result", "glucose", "cholesterol"],
                "numbers": ["94", "210", "13.5", "665680"],
                "success": True,
                "entity_count": 25
            },
            "document_type": "lab_result",
            "confidence": 0.85
        }
        
        print(f"✅ Test document added with ID: {test_doc_id}")
        print(f"📚 Total documents in storage: {len(document_storage)}")
        print(f"📄 Document data structure:")
        print(f"   - Filename: {document_storage[test_doc_id]['filename']}")
        print(f"   - Type: {document_storage[test_doc_id]['document_type']}")
        print(f"   - Status: {document_storage[test_doc_id]['status']}")
        print(f"   - AI Analysis: {'✅ Present' if document_storage[test_doc_id]['ai_analysis'] else '❌ Missing'}")
        print(f"   - DocLing Result: {'✅ Present' if document_storage[test_doc_id]['docling_result'] else '❌ Missing'}")
        print(f"   - Extracted Entities: {'✅ Present' if document_storage[test_doc_id]['extracted_entities'] else '❌ Missing'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error populating test documents: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = populate_test_documents()
    if success:
        print("\n✅ Document storage populated successfully!")
        print("🎯 Now you can test the frontend with real data!")
    else:
        print("\n❌ Failed to populate document storage!")
