"""
AI Processing Service - Combines Docling and Document Classification
"""
import os
import logging
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from .docling_service import DoclingService
from .classification_service import DocumentClassificationService
from core.config import settings

logger = logging.getLogger(__name__)

class AIProcessingService:
    """AI processing service for document analysis using Docling"""
    
    def __init__(self):
        """Initialize AI processing service"""
        self.docling_service = DoclingService()
        self.classification_service = DocumentClassificationService()
        logger.info("✅ AI Processing Service initialized with Docling")
    
    async def process_document(self, file_path: str, file_type: str) -> Dict:
        """
        Process document with Docling and classification
        
        Args:
            file_path: Path to document file
            file_type: Type of document (pdf, docx, xlsx, etc.)
            
        Returns:
            Dict containing processing results
        """
        try:
            logger.info(f"🔄 Processing document with Docling: {file_path}")
            
            # Extract text using Docling
            docling_result = await self._extract_text_with_docling(file_path, file_type)
            
            if not docling_result["success"]:
                return {
                    "success": False,
                    "error": docling_result["error"],
                    "processing_time": 0,
                    "timestamp": datetime.now().isoformat()
                }
            
            extracted_text = docling_result["text"]
            
            # Classify document
            classification_result = self.classification_service.classify_document(extracted_text)
            
            # Extract entities
            entities_result = self.classification_service.extract_entities(extracted_text)
            
            # Generate summary
            summary_result = self.classification_service.get_document_summary(extracted_text)
            
            # Combine results
            processing_result = {
                "success": True,
                "file_path": file_path,
                "file_type": file_type,
                "processing_time": docling_result.get("processing_time", 0),
                "timestamp": datetime.now().isoformat(),
                
                # Docling Results
                "docling": {
                    "text": extracted_text,
                    "confidence": docling_result.get("confidence", 0.0),
                    "word_count": docling_result.get("word_count", 0),
                    "metadata": docling_result.get("metadata", {}),
                    "processing_method": docling_result.get("processing_method", "docling")
                },
                
                # Classification Results
                "classification": {
                    "document_type": classification_result.get("document_type", "other"),
                    "confidence": classification_result.get("confidence", 0.0),
                    "text_length": classification_result.get("text_length", 0)
                },
                
                # Entity Extraction
                "entities": entities_result.get("entities", {}),
                "entity_count": entities_result.get("entity_count", 0),
                
                # Summary
                "summary": summary_result.get("summary", ""),
                "summary_stats": {
                    "word_count": summary_result.get("word_count", 0),
                    "sentence_count": summary_result.get("sentence_count", 0)
                }
            }
            
            logger.info(f"✅ Document processing completed with Docling: {file_path}")
            return processing_result
            
        except Exception as e:
            logger.error(f"❌ Document processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path,
                "processing_time": 0,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _extract_text_with_docling(self, file_path: str, file_type: str) -> Dict:
        """Extract text from document using Docling"""
        try:
            start_time = datetime.now()
            
            # Validate document first
            validation_result = self.docling_service.validate_document(file_path)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "text": "",
                    "confidence": 0.0,
                    "word_count": 0
                }
            
            # Process document with Docling
            docling_result = self.docling_service.process_document(file_path, file_type)
            
            if not docling_result["success"]:
                return docling_result
            
            # Add processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Enhance result with processing time
            docling_result["processing_time"] = processing_time
            
            return docling_result
            
        except Exception as e:
            logger.error(f"Error extracting text with Docling: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0,
                "word_count": 0
            }
    
    def get_processing_stats(self) -> Dict:
        """Get processing statistics"""
        return {
            "service_name": "AIProcessingService",
            "docling_status": self.docling_service.get_service_status(),
            "classification_status": "active",
            "total_processed": 0,  # TODO: Implement counter
            "last_processed": None,
            "processing_method": "docling"
        }
    
    async def batch_process_documents(self, file_paths: List[str]) -> List[Dict]:
        """
        Process multiple documents in batch
        
        Args:
            file_paths: List of file paths to process
            
        Returns:
            List of processing results
        """
        try:
            logger.info(f"🔄 Starting batch processing of {len(file_paths)} documents")
            
            results = []
            for file_path in file_paths:
                try:
                    # Determine file type from extension
                    file_type = os.path.splitext(file_path)[1][1:].lower()
                    
                    # Process document
                    result = await self.process_document(file_path, file_type)
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    results.append({
                        "success": False,
                        "file_path": file_path,
                        "error": str(e),
                        "processing_time": 0,
                        "timestamp": datetime.now().isoformat()
                    })
            
            logger.info(f"✅ Batch processing completed: {len(results)} documents processed")
            return results
            
        except Exception as e:
            logger.error(f"❌ Batch processing failed: {e}")
            return []
    
    def validate_document(self, file_path: str) -> Dict:
        """Validate document file"""
        return self.docling_service.validate_document(file_path)
