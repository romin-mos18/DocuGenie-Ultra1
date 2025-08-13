#!/usr/bin/env python3
"""
Document Processing Test Script for DocuGenie Ultra
Tests DocLing integration with real document processing
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.docling_service import DoclingService
from backend.services.classification_service import DocumentClassificationService
from backend.services.ai_processing_service import AIProcessingService
from backend.services.multilang_service import MultiLanguageService

class DocumentProcessorTester:
    """Test document processing capabilities with DocLing integration"""
    
    def __init__(self):
        """Initialize the tester with all services"""
        print("🚀 Initializing Document Processing Tester...")
        
        self.docling_service = DoclingService()
        self.classification_service = DocumentClassificationService()
        self.ai_service = AIProcessingService()
        self.multilang_service = MultiLanguageService()
        
        # Test document path
        self.test_doc_path = "../Testing Documents/Testing Documents/pdf/lab_report_001.pdf"
        
        print("✅ All services initialized successfully")
    
    def test_single_document(self):
        """Test processing of a single document"""
        print(f"\n📄 Testing Document: {self.test_doc_path}")
        print("=" * 60)
        
        if not os.path.exists(self.test_doc_path):
            print(f"❌ Document not found: {self.test_doc_path}")
            return
        
        # Test 1: Basic DocLing Processing
        print("\n🔍 Test 1: Basic DocLing Processing")
        print("-" * 40)
        docling_result = self.docling_service.process_document(
            self.test_doc_path, 
            "pdf"
        )
        
        if docling_result["success"]:
            print(f"✅ DocLing Processing: SUCCESS")
            print(f"   Confidence: {docling_result['confidence']:.2f}")
            print(f"   Word Count: {docling_result['word_count']}")
            print(f"   Method: {docling_result['processing_method']}")
            print(f"   Text Preview: {docling_result['text'][:200]}...")
        else:
            print(f"❌ DocLing Processing: FAILED")
            print(f"   Error: {docling_result['error']}")
            return
        
        # Test 2: Document Classification
        print("\n🏷️ Test 2: Document Classification")
        print("-" * 40)
        classification_result = self.classification_service.classify_document(
            docling_result["text"]
        )
        
        if classification_result["success"]:
            print(f"✅ Classification: SUCCESS")
            print(f"   Document Type: {classification_result['document_type']}")
            print(f"   Confidence: {classification_result['confidence']:.2f}")
            print(f"   Text Length: {classification_result['text_length']}")
        else:
            print(f"❌ Classification: FAILED")
            print(f"   Error: {classification_result['error']}")
        
        # Test 3: Entity Extraction
        print("\n🔍 Test 3: Entity Extraction")
        print("-" * 40)
        entities_result = self.classification_service.extract_entities(
            docling_result["text"]
        )
        
        if entities_result["success"]:
            print(f"✅ Entity Extraction: SUCCESS")
            print(f"   Total Entities: {entities_result['entity_count']}")
            print(f"   Dates: {len(entities_result['entities']['dates'])}")
            print(f"   Names: {len(entities_result['entities']['names'])}")
            print(f"   Medical Terms: {len(entities_result['entities']['medical_terms'])}")
        else:
            print(f"❌ Entity Extraction: FAILED")
            print(f"   Error: {entities_result['error']}")
        
        # Test 4: Language Detection
        print("\n🌐 Test 4: Language Detection")
        print("-" * 40)
        lang_result = self.multilang_service.detect_language(
            docling_result["text"]
        )
        
        if lang_result["success"]:
            print(f"✅ Language Detection: SUCCESS")
            print(f"   Primary Language: {lang_result['primary_language_name']} ({lang_result['primary_language']})")
            print(f"   Confidence: {lang_result['confidence']:.2f}")
        else:
            print(f"❌ Language Detection: FAILED")
            print(f"   Error: {lang_result['error']}")
        
        # Test 5: AI Processing Service (Combined)
        print("\n🤖 Test 5: AI Processing Service (Combined)")
        print("-" * 40)
        
        # Create comprehensive result
        comprehensive_result = self._create_comprehensive_result(
            docling_result,
            classification_result,
            entities_result,
            lang_result
        )
        
        return comprehensive_result
    
    def _create_comprehensive_result(self, docling_result, classification_result, entities_result, lang_result):
        """Create comprehensive processing result"""
        return {
            "document_info": {
                "file_path": self.test_doc_path,
                "file_name": os.path.basename(self.test_doc_path),
                "file_type": "pdf",
                "processing_timestamp": datetime.now().isoformat(),
                "processing_status": "completed"
            },
            
            "extraction_results": {
                "success": docling_result["success"],
                "confidence": docling_result.get("confidence", 0.0),
                "word_count": docling_result.get("word_count", 0),
                "processing_method": docling_result.get("processing_method", "unknown"),
                "extracted_text": docling_result.get("text", "")[:1000] + "..." if len(docling_result.get("text", "")) > 1000 else docling_result.get("text", ""),
                "metadata": docling_result.get("metadata", {})
            },
            
            "classification_results": {
                "document_type": classification_result.get("document_type", "unknown"),
                "classification_confidence": classification_result.get("confidence", 0.0),
                "text_length": classification_result.get("text_length", 0)
            },
            
            "entity_extraction": {
                "total_entities": entities_result.get("entity_count", 0),
                "entities": entities_result.get("entities", {}),
                "extraction_success": entities_result.get("success", False)
            },
            
            "language_analysis": {
                "primary_language": lang_result.get("primary_language", "unknown"),
                "language_name": lang_result.get("primary_language_name", "Unknown"),
                "detection_confidence": lang_result.get("confidence", 0.0),
                "detection_success": lang_result.get("success", False)
            },
            
            "processing_summary": {
                "overall_success": all([
                    docling_result["success"],
                    classification_result.get("success", False),
                    entities_result.get("success", False),
                    lang_result.get("success", False)
                ]),
                "total_processing_time": "N/A",  # Would be calculated in real scenario
                "services_used": [
                    "DocLing Service",
                    "Document Classification Service", 
                    "Entity Extraction Service",
                    "Multi-Language Service"
                ]
            }
        }
    
    def display_json_output(self, result):
        """Display the raw JSON output"""
        print("\n📊 RAW JSON OUTPUT")
        print("=" * 60)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    def display_detail_view_format(self, result):
        """Display the formatted detail view for UI display"""
        print("\n🎨 DETAIL VIEW FORMAT (UI Display)")
        print("=" * 60)
        
        doc_info = result["document_info"]
        extraction = result["extraction_results"]
        classification = result["classification_results"]
        entities = result["entity_extraction"]
        language = result["language_analysis"]
        
        # Document Header
        print(f"📄 DOCUMENT DETAILS")
        print(f"   File Name: {doc_info['file_name']}")
        print(f"   File Type: {doc_info['file_type'].upper()}")
        print(f"   Processing Date: {doc_info['processing_timestamp'][:19]}")
        print(f"   Status: {'✅ Processed' if result['processing_summary']['overall_success'] else '❌ Failed'}")
        
        # Document Type & Classification
        print(f"\n🏷️ DOCUMENT CLASSIFICATION")
        print(f"   Type: {classification['document_type'].replace('_', ' ').title()}")
        print(f"   Confidence: {classification['classification_confidence']:.1%}")
        print(f"   Content Length: {classification['text_length']:,} characters")
        
        # Language Information
        print(f"\n🌐 LANGUAGE ANALYSIS")
        print(f"   Primary Language: {language['language_name']}")
        print(f"   Language Code: {language['primary_language']}")
        print(f"   Detection Confidence: {language['detection_confidence']:.1%}")
        
        # Entity Summary
        print(f"\n🔍 EXTRACTED ENTITIES")
        print(f"   Total Entities Found: {entities['total_entities']}")
        
        if entities['entities'].get('dates'):
            print(f"   📅 Dates: {', '.join(entities['entities']['dates'][:5])}")
        
        if entities['entities'].get('names'):
            print(f"   👤 Names: {', '.join(entities['entities']['names'][:5])}")
        
        if entities['entities'].get('medical_terms'):
            print(f"   🏥 Medical Terms: {', '.join(entities['entities']['medical_terms'][:5])}")
        
        if entities['entities'].get('numbers'):
            print(f"   🔢 Numbers: {', '.join(entities['entities']['numbers'][:5])}")
        
        # Processing Information
        print(f"\n⚙️ PROCESSING INFORMATION")
        print(f"   Extraction Method: {extraction['processing_method']}")
        print(f"   Extraction Confidence: {extraction['confidence']:.1%}")
        print(f"   Word Count: {extraction['word_count']:,}")
        print(f"   Services Used: {', '.join(result['processing_summary']['services_used'])}")
        
        # Content Preview
        print(f"\n📝 CONTENT PREVIEW")
        preview_text = extraction['extracted_text'][:300]
        print(f"   {preview_text}...")
        
        # Metadata
        if extraction['metadata']:
            print(f"\n📋 METADATA")
            for key, value in extraction['metadata'].items():
                print(f"   {key.replace('_', ' ').title()}: {value}")
    
    def run_comprehensive_test(self):
        """Run the comprehensive document processing test"""
        print("🚀 Starting Comprehensive Document Processing Test")
        print("=" * 60)
        
        try:
            # Test single document
            result = self.test_single_document()
            
            if result:
                # Display results
                self.display_json_output(result)
                self.display_detail_view_format(result)
                
                # Save results to file
                output_file = "document_processing_test_results.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                print(f"\n💾 Results saved to: {output_file}")
                print("\n✅ Document Processing Test Completed Successfully!")
                
                return result
            else:
                print("\n❌ Document Processing Test Failed!")
                return None
                
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return None

def main():
    """Main function to run the test"""
    tester = DocumentProcessorTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
