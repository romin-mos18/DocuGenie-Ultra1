#!/usr/bin/env python3
"""
Batch Document Processor for DocuGenie Ultra
Processes all 500 documents to train DocLing AI and improve extraction
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import concurrent.futures
from collections import defaultdict, Counter

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.docling_service import DoclingService
from backend.services.classification_service import DocumentClassificationService
from backend.services.ai_processing_service import AIProcessingService
from backend.services.multilang_service import MultiLanguageService

class BatchDocumentProcessor:
    """Batch processor for all 500 documents with AI learning capabilities"""
    
    def __init__(self):
        """Initialize batch processor"""
        print("🚀 Initializing Batch Document Processor...")
        
        self.docling_service = DoclingService()
        self.classification_service = DocumentClassificationService()
        self.ai_service = AIProcessingService()
        self.multilang_service = MultiLanguageService()
        
        # Base paths
        self.testing_docs_path = "../Testing Documents/Testing Documents"
        self.output_path = "batch_processing_results"
        
        # Processing statistics
        self.stats = {
            "total_documents": 0,
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "processing_times": [],
            "document_types": Counter(),
            "languages": Counter(),
            "entities_found": defaultdict(int),
            "extraction_methods": Counter()
        }
        
        # AI Learning Data
        self.ai_learning_data = {
            "document_patterns": defaultdict(list),
            "entity_patterns": defaultdict(list),
            "classification_improvements": [],
            "extraction_insights": []
        }
        
        # Create output directory
        os.makedirs(self.output_path, exist_ok=True)
        
        print("✅ Batch Document Processor initialized successfully")
    
    def discover_documents(self) -> List[Dict[str, str]]:
        """Discover all documents in the testing folder"""
        print("🔍 Discovering documents...")
        
        documents = []
        supported_extensions = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.txt', '.json', '.xml', '.csv']
        
        for root, dirs, files in os.walk(self.testing_docs_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext in supported_extensions:
                    documents.append({
                        "file_path": file_path,
                        "file_name": file,
                        "file_type": file_ext[1:],  # Remove the dot
                        "relative_path": os.path.relpath(file_path, self.testing_docs_path)
                    })
        
        self.stats["total_documents"] = len(documents)
        print(f"✅ Discovered {len(documents)} documents")
        
        return documents
    
    def process_single_document(self, doc_info: Dict[str, str]) -> Dict[str, Any]:
        """Process a single document with comprehensive analysis"""
        start_time = time.time()
        
        try:
            print(f"📄 Processing: {doc_info['file_name']}")
            
            # Process with DocLing
            docling_result = self.docling_service.process_document(
                doc_info["file_path"], 
                doc_info["file_type"]
            )
            
            if not docling_result["success"]:
                return self._create_failed_result(doc_info, docling_result["error"], start_time)
            
            # Extract text content
            extracted_text = docling_result["text"]
            
            # Classify document
            classification_result = self.classification_service.classify_document(extracted_text)
            
            # Extract entities
            entities_result = self.classification_service.extract_entities(extracted_text)
            
            # Detect language
            lang_result = self.multilang_service.detect_language(extracted_text)
            
            # Create comprehensive result
            result = self._create_document_result(
                doc_info, docling_result, classification_result, 
                entities_result, lang_result, start_time
            )
            
            # Update statistics
            self._update_stats(result, True)
            
            # Learn from this document
            self._learn_from_document(result)
            
            return result
            
        except Exception as e:
            error_result = self._create_failed_result(doc_info, str(e), start_time)
            self._update_stats(error_result, False)
            return error_result
    
    def _create_document_result(self, doc_info, docling_result, classification_result, 
                               entities_result, lang_result, start_time):
        """Create comprehensive document processing result"""
        processing_time = time.time() - start_time
        
        return {
            "document_info": {
                "file_path": doc_info["file_path"],
                "file_name": doc_info["file_name"],
                "file_type": doc_info["file_type"],
                "relative_path": doc_info["relative_path"],
                "processing_timestamp": datetime.now().isoformat(),
                "processing_time": processing_time,
                "processing_status": "completed"
            },
            
            "extraction_results": {
                "success": docling_result["success"],
                "confidence": docling_result.get("confidence", 0.0),
                "word_count": docling_result.get("word_count", 0),
                "processing_method": docling_result.get("processing_method", "unknown"),
                "extracted_text": docling_result.get("text", "")[:2000] + "..." if len(docling_result.get("text", "")) > 2000 else docling_result.get("text", ""),
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
            
            "ai_insights": {
                "key_phrases": self._extract_key_phrases(docling_result.get("text", "")),
                "document_summary": self._generate_document_summary(docling_result.get("text", "")),
                "confidence_score": self._calculate_overall_confidence(
                    docling_result, classification_result, entities_result, lang_result
                )
            }
        }
    
    def _create_failed_result(self, doc_info, error, start_time):
        """Create result for failed document processing"""
        processing_time = time.time() - start_time
        
        return {
            "document_info": {
                "file_path": doc_info["file_path"],
                "file_name": doc_info["file_name"],
                "file_type": doc_info["file_type"],
                "relative_path": doc_info["relative_path"],
                "processing_timestamp": datetime.now().isoformat(),
                "processing_time": processing_time,
                "processing_status": "failed"
            },
            "error": error,
            "extraction_results": {"success": False},
            "classification_results": {"success": False},
            "entity_extraction": {"success": False},
            "language_analysis": {"success": False},
            "ai_insights": {"success": False}
        }
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from document text"""
        if not text:
            return []
        
        # Simple key phrase extraction (can be enhanced with NLP)
        lines = text.split('\n')
        key_phrases = []
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 10 and len(line) < 100:
                # Look for lines that might contain key information
                if any(keyword in line.lower() for keyword in [
                    'patient', 'doctor', 'hospital', 'lab', 'test', 'result', 
                    'date', 'name', 'diagnosis', 'treatment', 'medication'
                ]):
                    key_phrases.append(line)
        
        return key_phrases[:10]  # Limit to top 10
    
    def _generate_document_summary(self, text: str) -> str:
        """Generate a brief summary of the document"""
        if not text:
            return "No content available"
        
        # Simple summary generation
        sentences = text.split('.')
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
        
        if len(sentences) <= 2:
            return text[:200] + "..." if len(text) > 200 else text
        
        # Take first and last meaningful sentences
        summary_sentences = sentences[:2]
        if len(sentences) > 3:
            summary_sentences.append(sentences[-1])
        
        summary = '. '.join(summary_sentences) + '.'
        return summary[:300] + "..." if len(summary) > 300 else summary
    
    def _calculate_overall_confidence(self, docling_result, classification_result, 
                                    entities_result, lang_result) -> float:
        """Calculate overall confidence score for the document"""
        scores = []
        
        if docling_result.get("success"):
            scores.append(docling_result.get("confidence", 0.0))
        
        if classification_result.get("success"):
            scores.append(classification_result.get("confidence", 0.0))
        
        if entities_result.get("success"):
            # Normalize entity count to 0-1 scale
            entity_score = min(entities_result.get("entity_count", 0) / 50.0, 1.0)
            scores.append(entity_score)
        
        if lang_result.get("success"):
            scores.append(lang_result.get("confidence", 0.0))
        
        if not scores:
            return 0.0
        
        return sum(scores) / len(scores)
    
    def _update_stats(self, result: Dict, success: bool):
        """Update processing statistics"""
        self.stats["processed"] += 1
        
        if success:
            self.stats["successful"] += 1
        else:
            self.stats["failed"] += 1
        
        # Update document type stats
        if success:
            doc_type = result.get("classification_results", {}).get("document_type", "unknown")
            self.stats["document_types"][doc_type] += 1
            
            # Update language stats
            lang = result.get("language_analysis", {}).get("primary_language", "unknown")
            self.stats["languages"][lang] += 1
            
            # Update entity stats
            entities = result.get("entity_extraction", {}).get("entities", {})
            for entity_type, entity_list in entities.items():
                self.stats["entities_found"][entity_type] += len(entity_list)
            
            # Update extraction method stats
            method = result.get("extraction_results", {}).get("processing_method", "unknown")
            self.stats["extraction_methods"][method] += 1
        
        # Update processing time
        processing_time = result.get("document_info", {}).get("processing_time", 0)
        if processing_time > 0:
            self.stats["processing_times"].append(processing_time)
    
    def _learn_from_document(self, result: Dict):
        """Learn patterns from successfully processed document"""
        if not result.get("extraction_results", {}).get("success"):
            return
        
        # Learn document patterns
        doc_type = result.get("classification_results", {}).get("document_type", "unknown")
        text_length = result.get("classification_results", {}).get("text_length", 0)
        
        self.ai_learning_data["document_patterns"][doc_type].append({
            "text_length": text_length,
            "word_count": result.get("extraction_results", {}).get("word_count", 0),
            "confidence": result.get("extraction_results", {}).get("confidence", 0.0)
        })
        
        # Learn entity patterns
        entities = result.get("entity_extraction", {}).get("entities", {})
        for entity_type, entity_list in entities.items():
            if entity_list:
                self.ai_learning_data["entity_patterns"][entity_type].extend(entity_list[:5])
        
        # Learn extraction insights
        extraction_method = result.get("extraction_results", {}).get("processing_method", "unknown")
        confidence = result.get("extraction_results", {}).get("confidence", 0.0)
        
        self.ai_learning_data["extraction_insights"].append({
            "method": extraction_method,
            "confidence": confidence,
            "document_type": doc_type,
            "success": True
        })
    
    def process_documents_batch(self, documents: List[Dict], batch_size: int = 10):
        """Process documents in batches with progress tracking"""
        print(f"\n🚀 Starting batch processing of {len(documents)} documents...")
        print(f"📊 Batch size: {batch_size}")
        print("=" * 60)
        
        all_results = []
        start_time = time.time()
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(documents) + batch_size - 1) // batch_size
            
            print(f"\n📦 Processing Batch {batch_num}/{total_batches} ({len(batch)} documents)")
            print("-" * 50)
            
            # Process batch with threading for better performance
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(batch_size, 5)) as executor:
                batch_results = list(executor.map(self.process_single_document, batch))
            
            all_results.extend(batch_results)
            
            # Progress update
            processed = len(all_results)
            success_rate = (self.stats["successful"] / processed * 100) if processed > 0 else 0
            avg_time = sum(self.stats["processing_times"]) / len(self.stats["processing_times"]) if self.stats["processing_times"] else 0
            
            print(f"✅ Batch {batch_num} completed")
            print(f"   Progress: {processed}/{len(documents)} ({processed/len(documents)*100:.1f}%)")
            print(f"   Success Rate: {success_rate:.1f}%")
            print(f"   Average Time: {avg_time:.2f}s per document")
        
        total_time = time.time() - start_time
        print(f"\n🎉 Batch processing completed in {total_time:.2f} seconds!")
        
        return all_results
    
    def generate_analytics_report(self, results: List[Dict]):
        """Generate comprehensive analytics report"""
        print("\n📊 Generating Analytics Report...")
        
        # Calculate additional statistics
        total_processing_time = sum(self.stats["processing_times"])
        avg_processing_time = total_processing_time / len(self.stats["processing_times"]) if self.stats["processing_times"] else 0
        
        analytics = {
            "processing_summary": {
                "total_documents": self.stats["total_documents"],
                "successfully_processed": self.stats["successful"],
                "failed_processing": self.stats["failed"],
                "success_rate": (self.stats["successful"] / self.stats["total_documents"] * 100) if self.stats["total_documents"] > 0 else 0,
                "total_processing_time": total_processing_time,
                "average_processing_time": avg_processing_time
            },
            
            "document_type_distribution": dict(self.stats["document_types"]),
            "language_distribution": dict(self.stats["languages"]),
            "entity_extraction_summary": dict(self.stats["entities_found"]),
            "extraction_methods": dict(self.stats["extraction_methods"]),
            
            "ai_learning_insights": {
                "document_patterns": dict(self.ai_learning_data["document_patterns"]),
                "entity_patterns": dict(self.ai_learning_data["entity_patterns"]),
                "extraction_insights": self.ai_learning_data["extraction_insights"]
            },
            
            "performance_metrics": {
                "documents_per_minute": (self.stats["successful"] / (total_processing_time / 60)) if total_processing_time > 0 else 0,
                "peak_processing_rate": max(self.stats["processing_times"]) if self.stats["processing_times"] else 0,
                "efficiency_score": self.stats["successful"] / (total_processing_time + 1)  # Avoid division by zero
            }
        }
        
        return analytics
    
    def save_results(self, results: List[Dict], analytics: Dict):
        """Save all results and analytics to files"""
        print("\n💾 Saving results...")
        
        # Save individual results
        results_file = os.path.join(self.output_path, "all_document_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save analytics
        analytics_file = os.path.join(self.output_path, "processing_analytics.json")
        with open(analytics_file, 'w', encoding='utf-8') as f:
            json.dump(analytics, f, indent=2, ensure_ascii=False)
        
        # Save AI learning data
        learning_file = os.path.join(self.output_path, "ai_learning_data.json")
        with open(learning_file, 'w', encoding='utf-8') as f:
            json.dump(self.ai_learning_data, f, indent=2, ensure_ascii=False)
        
        # Save summary report
        summary_file = os.path.join(self.output_path, "processing_summary.txt")
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(self._generate_summary_text(analytics))
        
        print(f"✅ Results saved to: {self.output_path}/")
        print(f"   📄 Document Results: {results_file}")
        print(f"   📊 Analytics: {analytics_file}")
        print(f"   🧠 AI Learning Data: {learning_file}")
        print(f"   📋 Summary Report: {summary_file}")
    
    def _generate_summary_text(self, analytics: Dict) -> str:
        """Generate human-readable summary report"""
        summary = []
        summary.append("=" * 60)
        summary.append("DOCUGENIE ULTRA - BATCH PROCESSING SUMMARY REPORT")
        summary.append("=" * 60)
        summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")
        
        # Processing Summary
        ps = analytics["processing_summary"]
        summary.append("📊 PROCESSING SUMMARY")
        summary.append("-" * 30)
        summary.append(f"Total Documents: {ps['total_documents']:,}")
        summary.append(f"Successfully Processed: {ps['successfully_processed']:,}")
        summary.append(f"Failed: {ps['failed_processing']:,}")
        summary.append(f"Success Rate: {ps['success_rate']:.1f}%")
        summary.append(f"Total Processing Time: {ps['total_processing_time']:.2f} seconds")
        summary.append(f"Average Time per Document: {ps['average_processing_time']:.2f} seconds")
        summary.append("")
        
        # Document Types
        summary.append("🏷️ DOCUMENT TYPE DISTRIBUTION")
        summary.append("-" * 30)
        for doc_type, count in analytics["document_type_distribution"].items():
            percentage = (count / ps['successfully_processed'] * 100) if ps['successfully_processed'] > 0 else 0
            summary.append(f"{doc_type.replace('_', ' ').title()}: {count:,} ({percentage:.1f}%)")
        summary.append("")
        
        # Languages
        summary.append("🌐 LANGUAGE DISTRIBUTION")
        summary.append("-" * 30)
        for lang, count in analytics["language_distribution"].items():
            percentage = (count / ps['successfully_processed'] * 100) if ps['successfully_processed'] > 0 else 0
            summary.append(f"{lang.upper()}: {count:,} ({percentage:.1f}%)")
        summary.append("")
        
        # Performance
        pm = analytics["performance_metrics"]
        summary.append("⚡ PERFORMANCE METRICS")
        summary.append("-" * 30)
        summary.append(f"Documents per Minute: {pm['documents_per_minute']:.1f}")
        summary.append(f"Peak Processing Rate: {pm['peak_processing_rate']:.2f}s")
        summary.append(f"Efficiency Score: {pm['efficiency_score']:.3f}")
        summary.append("")
        
        summary.append("=" * 60)
        summary.append("END OF REPORT")
        summary.append("=" * 60)
        
        return "\n".join(summary)
    
    def run_batch_processing(self, batch_size: int = 10):
        """Run the complete batch processing pipeline"""
        print("🚀 Starting Batch Document Processing Pipeline")
        print("=" * 60)
        
        try:
            # Discover documents
            documents = self.discover_documents()
            
            if not documents:
                print("❌ No documents found to process")
                return
            
            # Process documents in batches
            results = self.process_documents_batch(documents, batch_size)
            
            # Generate analytics
            analytics = self.generate_analytics_report(results)
            
            # Save results
            self.save_results(results, analytics)
            
            # Display final summary
            self._display_final_summary(analytics)
            
            print("\n🎉 Batch Document Processing Completed Successfully!")
            return results, analytics
            
        except Exception as e:
            print(f"\n❌ Batch processing failed: {e}")
            import traceback
            traceback.print_exc()
            return None, None
    
    def _display_final_summary(self, analytics: Dict):
        """Display final processing summary"""
        print("\n🎯 FINAL PROCESSING SUMMARY")
        print("=" * 60)
        
        ps = analytics["processing_summary"]
        print(f"📊 Total Documents: {ps['total_documents']:,}")
        print(f"✅ Successfully Processed: {ps['successfully_processed']:,}")
        print(f"❌ Failed: {ps['failed_processing']:,}")
        print(f"🎯 Success Rate: {ps['success_rate']:.1f}%")
        print(f"⏱️ Total Time: {ps['total_processing_time']:.2f} seconds")
        print(f"⚡ Average Time: {ps['average_processing_time']:.2f}s per document")
        print(f"🚀 Processing Rate: {analytics['performance_metrics']['documents_per_minute']:.1f} docs/min")
        
        print(f"\n🏷️ Top Document Types:")
        doc_types = sorted(analytics["document_type_distribution"].items(), key=lambda x: x[1], reverse=True)[:5]
        for doc_type, count in doc_types:
            print(f"   {doc_type.replace('_', ' ').title()}: {count:,}")
        
        print(f"\n🌐 Languages Detected:")
        languages = sorted(analytics["language_distribution"].items(), key=lambda x: x[1], reverse=True)[:5]
        for lang, count in languages:
            print(f"   {lang.upper()}: {count:,}")

def main():
    """Main function to run batch processing"""
    processor = BatchDocumentProcessor()
    processor.run_batch_processing(batch_size=20)  # Process 20 documents at a time

if __name__ == "__main__":
    main()
