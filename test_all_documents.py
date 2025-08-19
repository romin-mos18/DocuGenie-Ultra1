#!/usr/bin/env python3
"""
Comprehensive Document Processing Test Script
Tests all documents from Testing Documents folder through the complete AI pipeline
"""

import os
import sys
import json
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Import all AI services
from services.docling_service import DoclingService
from services.classification_service import DocumentClassificationService
from services.multilang_service import MultiLanguageService
from services.structured_data_service import StructuredDataService

# Configure logging for detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('document_processing_test.log')
    ]
)

logger = logging.getLogger(__name__)

class DocumentTestProcessor:
    """Comprehensive document testing processor"""
    
    def __init__(self):
        """Initialize all AI services"""
        print("🚀 Initializing AI Services...")
        print("=" * 80)
        
        try:
            self.docling_service = DoclingService()
            print("✅ DocLing Service initialized")
        except Exception as e:
            print(f"❌ DocLing Service failed: {e}")
            self.docling_service = None
        
        try:
            self.classification_service = DocumentClassificationService()
            print("✅ Classification Service initialized")
        except Exception as e:
            print(f"❌ Classification Service failed: {e}")
            self.classification_service = None
        
        try:
            self.multilang_service = MultiLanguageService()
            print("✅ Multi-Language Service initialized")
        except Exception as e:
            print(f"❌ Multi-Language Service failed: {e}")
            self.multilang_service = None
        
        try:
            self.structured_data_service = StructuredDataService()
            print("✅ Structured Data Service initialized")
        except Exception as e:
            print(f"❌ Structured Data Service failed: {e}")
            self.structured_data_service = None
        
        self.results = []
        self.stats = {
            "total_documents": 0,
            "successful_processing": 0,
            "failed_processing": 0,
            "document_types": {},
            "file_types": {},
            "processing_times": [],
            "total_entities": 0,
            "languages_detected": {},
        }
        
        print("=" * 80)
        print("🎯 All AI Services Ready!")
        print()
    
    def get_file_type(self, file_path: str) -> str:
        """Get file extension/type"""
        return Path(file_path).suffix[1:].lower()
    
    def process_single_document(self, file_path: str, relative_path: str) -> Dict:
        """Process a single document through the complete AI pipeline"""
        start_time = time.time()
        file_type = self.get_file_type(file_path)
        file_size = os.path.getsize(file_path)
        
        print(f"\n📄 Processing: {relative_path}")
        print(f"   File Type: {file_type.upper()}")
        print(f"   File Size: {file_size:,} bytes")
        print("-" * 60)
        
        result = {
            "file_path": relative_path,
            "file_type": file_type,
            "file_size": file_size,
            "processing_start": datetime.now().isoformat(),
            "success": False,
            "error": None,
            "docling_result": {},
            "classification_result": {},
            "entities_result": {},
            "language_result": {},
            "structured_data_result": {},
            "processing_time": 0,
        }
        
        try:
            # Step 1: DocLing Text Extraction
            print("🔍 Step 1: DocLing Text Extraction...")
            if self.docling_service:
                try:
                    docling_result = self.docling_service.process_document(file_path, file_type)
                    result["docling_result"] = docling_result
                    
                    if docling_result.get("success"):
                        extracted_text = docling_result.get("text", "")
                        print(f"   ✅ Text extracted: {len(extracted_text)} characters")
                        if extracted_text:
                            print(f"   📝 Preview: {extracted_text[:150]}...")
                        else:
                            print("   ⚠️ No text content extracted")
                    else:
                        print(f"   ❌ DocLing failed: {docling_result.get('error', 'Unknown error')}")
                        extracted_text = ""
                except Exception as e:
                    print(f"   ❌ DocLing exception: {e}")
                    extracted_text = ""
                    result["docling_result"] = {"success": False, "error": str(e)}
            else:
                print("   ⏭️ DocLing service not available")
                extracted_text = ""
            
            # Step 2: Structured Data Extraction (for structured files)
            print("\n📊 Step 2: Structured Data Extraction...")
            if self.structured_data_service and file_type in ['csv', 'json', 'xml', 'xlsx', 'xls']:
                try:
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                    
                    structured_result = self.structured_data_service.extract_structured_data(
                        file_path, file_type, file_content
                    )
                    result["structured_data_result"] = structured_result
                    
                    if structured_result.get("success"):
                        data_type = structured_result.get("data_type", "unknown")
                        print(f"   ✅ Structured data extracted: {data_type}")
                        
                        structured_data = structured_result.get("structured_data", {})
                        if "headers" in structured_data:
                            headers = structured_data["headers"]
                            row_count = structured_data.get("total_rows", 0)
                            print(f"   📋 CSV/Excel: {len(headers)} columns, {row_count} rows")
                            print(f"   📊 Columns: {', '.join(headers[:5])}")
                            if len(headers) > 5:
                                print(f"             ... and {len(headers) - 5} more")
                        
                        elif "key_info" in structured_data:
                            key_info = structured_data["key_info"]
                            print(f"   🔑 Key Information: {len(key_info)} fields")
                            for key, value in list(key_info.items())[:5]:
                                if value:
                                    print(f"      • {key}: {value}")
                        
                        # Enhance extracted text with structured data summary
                        if structured_result.get("success"):
                            structured_summary = f"\n\nStructured Data Summary:\n"
                            structured_summary += f"Data Type: {data_type}\n"
                            
                            if "headers" in structured_data:
                                structured_summary += f"Columns: {', '.join(headers[:3])}\n"
                                structured_summary += f"Total Rows: {row_count}\n"
                            elif "key_info" in structured_data:
                                for key, value in list(key_info.items())[:3]:
                                    if value:
                                        structured_summary += f"{key.replace('_', ' ').title()}: {value}\n"
                            
                            extracted_text += structured_summary
                    else:
                        print(f"   ❌ Structured extraction failed: {structured_result.get('error', 'Unknown error')}")
                except Exception as e:
                    print(f"   ❌ Structured extraction exception: {e}")
                    result["structured_data_result"] = {"success": False, "error": str(e)}
            else:
                print(f"   ⏭️ No structured data extraction for {file_type.upper()} files")
            
            # Step 3: Document Classification
            print("\n🏷️ Step 3: Document Classification...")
            if self.classification_service and extracted_text:
                try:
                    classification_result = self.classification_service.classify_document(extracted_text)
                    result["classification_result"] = classification_result
                    
                    if classification_result.get("success"):
                        doc_type = classification_result.get("document_type", "unknown")
                        confidence = classification_result.get("confidence", 0)
                        print(f"   ✅ Classified as: {doc_type}")
                        print(f"   🎯 Confidence: {confidence:.1%}")
                        
                        # Update stats
                        if doc_type in self.stats["document_types"]:
                            self.stats["document_types"][doc_type] += 1
                        else:
                            self.stats["document_types"][doc_type] = 1
                    else:
                        print(f"   ❌ Classification failed: {classification_result.get('error', 'Unknown error')}")
                except Exception as e:
                    print(f"   ❌ Classification exception: {e}")
                    result["classification_result"] = {"success": False, "error": str(e)}
            else:
                print("   ⏭️ Classification skipped (no text or service unavailable)")
            
            # Step 4: Entity Extraction
            print("\n🔍 Step 4: Entity Extraction...")
            if self.classification_service and extracted_text:
                try:
                    entities_result = self.classification_service.extract_entities(extracted_text)
                    result["entities_result"] = entities_result
                    
                    if entities_result.get("success"):
                        entity_count = entities_result.get("entity_count", 0)
                        entities = entities_result.get("entities", {})
                        print(f"   ✅ Entities extracted: {entity_count} total")
                        
                        for entity_type, entity_list in entities.items():
                            if entity_list:
                                print(f"      • {entity_type.replace('_', ' ').title()}: {len(entity_list)} items")
                                # Show first few entities
                                sample_entities = entity_list[:3]
                                if sample_entities:
                                    print(f"        Examples: {', '.join(str(e) for e in sample_entities)}")
                        
                        self.stats["total_entities"] += entity_count
                    else:
                        print(f"   ❌ Entity extraction failed: {entities_result.get('error', 'Unknown error')}")
                except Exception as e:
                    print(f"   ❌ Entity extraction exception: {e}")
                    result["entities_result"] = {"success": False, "error": str(e)}
            else:
                print("   ⏭️ Entity extraction skipped (no text or service unavailable)")
            
            # Step 5: Language Detection
            print("\n🌍 Step 5: Language Detection...")
            if self.multilang_service and extracted_text:
                try:
                    language_result = self.multilang_service.detect_language(extracted_text)
                    result["language_result"] = language_result
                    
                    if language_result:
                        primary_language = language_result.get("primary_language", "unknown")
                        lang_confidence = language_result.get("confidence", 0)
                        print(f"   ✅ Language detected: {primary_language}")
                        print(f"   🎯 Confidence: {lang_confidence:.1%}")
                        
                        # Update language stats
                        if primary_language in self.stats["languages_detected"]:
                            self.stats["languages_detected"][primary_language] += 1
                        else:
                            self.stats["languages_detected"][primary_language] = 1
                    else:
                        print("   ❌ Language detection failed")
                except Exception as e:
                    print(f"   ❌ Language detection exception: {e}")
                    result["language_result"] = {"error": str(e)}
            else:
                print("   ⏭️ Language detection skipped (no text or service unavailable)")
            
            # Calculate processing time
            processing_time = time.time() - start_time
            result["processing_time"] = processing_time
            result["success"] = True
            
            print(f"\n✅ Processing completed in {processing_time:.2f} seconds")
            self.stats["successful_processing"] += 1
            self.stats["processing_times"].append(processing_time)
            
        except Exception as e:
            processing_time = time.time() - start_time
            result["processing_time"] = processing_time
            result["error"] = str(e)
            result["success"] = False
            
            print(f"\n❌ Processing failed after {processing_time:.2f} seconds")
            print(f"   Error: {e}")
            self.stats["failed_processing"] += 1
            logger.error(f"Failed to process {relative_path}: {e}")
        
        # Update file type stats
        if file_type in self.stats["file_types"]:
            self.stats["file_types"][file_type] += 1
        else:
            self.stats["file_types"][file_type] = 1
        
        return result
    
    def process_testing_documents(self, testing_docs_path: str):
        """Process all documents in the Testing Documents folder"""
        print("🎯 Starting Comprehensive Document Processing Test")
        print("=" * 80)
        
        if not os.path.exists(testing_docs_path):
            print(f"❌ Testing Documents folder not found: {testing_docs_path}")
            return
        
        # Find all files in the testing documents folder
        all_files = []
        for root, dirs, files in os.walk(testing_docs_path):
            for file in files:
                if not file.startswith('.'):  # Skip hidden files
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, testing_docs_path)
                    all_files.append((file_path, relative_path))
        
        print(f"📁 Found {len(all_files)} documents to process")
        print(f"📍 Processing from: {testing_docs_path}")
        print()
        
        self.stats["total_documents"] = len(all_files)
        
        # Process each document
        for i, (file_path, relative_path) in enumerate(all_files, 1):
            print(f"\n{'=' * 20} Document {i}/{len(all_files)} {'=' * 20}")
            
            try:
                result = self.process_single_document(file_path, relative_path)
                self.results.append(result)
                
                # Show progress
                if i % 10 == 0:
                    success_rate = (self.stats["successful_processing"] / i) * 100
                    print(f"\n🚀 Progress: {i}/{len(all_files)} ({i/len(all_files)*100:.1f}%)")
                    print(f"   Success rate: {success_rate:.1f}%")
            
            except KeyboardInterrupt:
                print(f"\n⏹️ Processing interrupted by user at document {i}")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error processing {relative_path}: {e}")
                self.stats["failed_processing"] += 1
                continue
        
        # Generate final summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate comprehensive processing summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE PROCESSING SUMMARY")
        print("=" * 80)
        
        # Overall Statistics
        print("🎯 OVERALL STATISTICS:")
        print(f"   Total Documents Processed: {self.stats['total_documents']}")
        print(f"   Successful Processing: {self.stats['successful_processing']}")
        print(f"   Failed Processing: {self.stats['failed_processing']}")
        
        if self.stats['total_documents'] > 0:
            success_rate = (self.stats['successful_processing'] / self.stats['total_documents']) * 100
            print(f"   Success Rate: {success_rate:.1f}%")
        
        # Processing Times
        if self.stats['processing_times']:
            avg_time = sum(self.stats['processing_times']) / len(self.stats['processing_times'])
            max_time = max(self.stats['processing_times'])
            min_time = min(self.stats['processing_times'])
            total_time = sum(self.stats['processing_times'])
            
            print(f"\n⏱️ PROCESSING TIMES:")
            print(f"   Total Processing Time: {total_time:.2f} seconds")
            print(f"   Average Time per Document: {avg_time:.2f} seconds")
            print(f"   Fastest Processing: {min_time:.2f} seconds")
            print(f"   Slowest Processing: {max_time:.2f} seconds")
        
        # Document Types Distribution
        print(f"\n📋 DOCUMENT TYPES DETECTED:")
        for doc_type, count in sorted(self.stats['document_types'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / self.stats['successful_processing']) * 100 if self.stats['successful_processing'] > 0 else 0
            print(f"   {doc_type.replace('_', ' ').title()}: {count} documents ({percentage:.1f}%)")
        
        # File Types Distribution
        print(f"\n📁 FILE TYPES PROCESSED:")
        for file_type, count in sorted(self.stats['file_types'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / self.stats['total_documents']) * 100 if self.stats['total_documents'] > 0 else 0
            print(f"   {file_type.upper()}: {count} files ({percentage:.1f}%)")
        
        # Languages Detected
        if self.stats['languages_detected']:
            print(f"\n🌍 LANGUAGES DETECTED:")
            for language, count in sorted(self.stats['languages_detected'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len([r for r in self.results if r.get('language_result', {}).get('primary_language')])) * 100
                print(f"   {language}: {count} documents ({percentage:.1f}%)")
        
        # Entity Extraction Summary
        print(f"\n🔍 ENTITY EXTRACTION:")
        print(f"   Total Entities Extracted: {self.stats['total_entities']:,}")
        if self.stats['successful_processing'] > 0:
            avg_entities = self.stats['total_entities'] / self.stats['successful_processing']
            print(f"   Average Entities per Document: {avg_entities:.1f}")
        
        # Top Performing Document Types
        print(f"\n🏆 TOP PERFORMING COMBINATIONS:")
        successful_docs = [r for r in self.results if r['success']]
        if successful_docs:
            # Group by file type and document type
            combinations = {}
            for doc in successful_docs:
                file_type = doc.get('file_type', 'unknown')
                doc_type = doc.get('classification_result', {}).get('document_type', 'unknown')
                key = f"{file_type.upper()} → {doc_type.replace('_', ' ').title()}"
                combinations[key] = combinations.get(key, 0) + 1
            
            for combo, count in sorted(combinations.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"   {combo}: {count} documents")
        
        # Save detailed results to JSON
        output_file = f"document_processing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'summary': self.stats,
                    'detailed_results': self.results,
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Detailed results saved to: {output_file}")
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")
        
        print("\n" + "=" * 80)
        print("🎉 TESTING COMPLETE!")
        print("=" * 80)

def main():
    """Main function to run the comprehensive test"""
    # Determine the path to Testing Documents
    current_dir = Path(__file__).parent
    testing_docs_path = current_dir.parent / "Testing Documents" / "Testing Documents"
    
    # Alternative paths to try
    alternative_paths = [
        current_dir / "Testing Documents" / "Testing Documents",
        current_dir / "Testing Documents",
        current_dir.parent / "Testing Documents",
        Path("Testing Documents/Testing Documents"),
        Path("Testing Documents"),
    ]
    
    # Find the correct path
    found_path = None
    for path in [testing_docs_path] + alternative_paths:
        if path.exists():
            found_path = str(path)
            break
    
    if not found_path:
        print("❌ Could not find Testing Documents folder!")
        print("📁 Searched in:")
        for path in [testing_docs_path] + alternative_paths:
            print(f"   - {path}")
        print("\n💡 Please ensure the Testing Documents folder exists and contains documents to test.")
        return
    
    print(f"📁 Found Testing Documents at: {found_path}")
    
    # Create processor and run tests
    processor = DocumentTestProcessor()
    processor.process_testing_documents(found_path)

if __name__ == "__main__":
    main()
