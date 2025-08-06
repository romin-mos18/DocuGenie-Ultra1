#!/usr/bin/env python3
"""
Test script for AI services
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ai_services():
    """Test AI services functionality"""
    try:
        print("🔄 Testing AI Services...")
        
        # Test OCR Service
        print("1. Testing OCR Service...")
        from services.ocr_service import OCRService
        ocr_service = OCRService()
        print("✅ OCR Service initialized")
        
        # Test Classification Service
        print("2. Testing Classification Service...")
        from services.classification_service import DocumentClassificationService
        classification_service = DocumentClassificationService()
        print("✅ Classification Service initialized")
        
        # Test AI Processing Service
        print("3. Testing AI Processing Service...")
        from services.ai_processing_service import AIProcessingService
        ai_service = AIProcessingService()
        print("✅ AI Processing Service initialized")
        
        # Test document classification
        print("4. Testing document classification...")
        sample_text = "This is a medical report for patient John Doe with diagnosis of hypertension."
        classification_result = classification_service.classify_document(sample_text)
        print(f"✅ Classification result: {classification_result['document_type']} (confidence: {classification_result['confidence']:.2f})")
        
        # Test entity extraction
        print("5. Testing entity extraction...")
        entities_result = classification_service.extract_entities(sample_text)
        print(f"✅ Entities extracted: {entities_result['entity_count']} entities")
        
        # Test summary generation
        print("6. Testing summary generation...")
        summary_result = classification_service.get_document_summary(sample_text)
        print(f"✅ Summary generated: {summary_result['summary']}")
        
        # Test AI processing stats
        print("7. Testing AI processing stats...")
        stats = ai_service.get_processing_stats()
        print(f"✅ AI stats: {stats['ocr_service']}, {stats['classification_service']}")
        
        print("\n🎉 All AI services tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ AI services test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_ai_services()
    sys.exit(0 if success else 1)
