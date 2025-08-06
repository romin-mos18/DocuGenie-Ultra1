"""
AI Processing Service - Combines OCR and Document Classification
"""
import os
import logging
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from .ocr_service import OCRService
from .classification_service import DocumentClassificationService
from core.config import settings

logger = logging.getLogger(__name__)

class AIProcessingService:
    """AI processing service for document analysis"""
    
    def __init__(self):
        """Initialize AI processing service"""
        self.ocr_service = OCRService()
        self.classification_service = DocumentClassificationService()
        logger.info("✅ AI Processing Service initialized")
    
    async def process_document(self, file_path: str, file_type: str) -> Dict:
        """
        Process document with OCR and classification
        
        Args:
            file_path: Path to document file
            file_type: Type of document (image, pdf, etc.)
            
        Returns:
            Dict containing processing results
        """
        try:
            logger.info(f"🔄 Processing document: {file_path}")
            
            # Extract text using OCR
            ocr_result = await self._extract_text(file_path, file_type)
            
            if not ocr_result["success"]:
                return {
                    "success": False,
                    "error": ocr_result["error"],
                    "processing_time": 0,
                    "timestamp": datetime.now().isoformat()
                }
            
            extracted_text = ocr_result["text"]
            
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
                "processing_time": ocr_result.get("processing_time", 0),
                "timestamp": datetime.now().isoformat(),
                
                # OCR Results
                "ocr": {
                    "text": extracted_text,
                    "confidence": ocr_result.get("confidence", 0.0),
                    "word_count": ocr_result.get("word_count", 0),
                    "lines": ocr_result.get("lines", 0)
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
            
            logger.info(f"✅ Document processing completed: {file_path}")
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
    
    async def _extract_text(self, file_path: str, file_type: str) -> Dict:
        """Extract text from document based on file type"""
        try:
            start_time = datetime.now()
            
            if file_type.lower() in ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'gif']:
                # Process image files
                if not self.ocr_service.validate_image(file_path):
                    return {
                        "success": False,
                        "error": "Invalid image file",
                        "text": "",
                        "confidence": 0.0
                    }
                
                # Preprocess image for better OCR
                preprocessed_path = self.ocr_service.preprocess_image(file_path)
                
                # Extract text
                result = self.ocr_service.extract_text_from_image(preprocessed_path)
                
                # Clean up preprocessed file if different from original
                if preprocessed_path != file_path and os.path.exists(preprocessed_path):
                    os.remove(preprocessed_path)
                
            elif file_type.lower() == 'pdf':
                # Process PDF files
                result = self.ocr_service.extract_text_from_pdf(file_path)
                
            else:
                return {
                    "success": False,
                    "error": f"Unsupported file type: {file_type}",
                    "text": "",
                    "confidence": 0.0
                }
            
            # Add processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            result["processing_time"] = processing_time
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Text extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0
            }
    
    def get_processing_stats(self) -> Dict:
        """Get AI processing service statistics"""
        return {
            "ocr_service": "PaddleOCR",
            "classification_service": "ML + Keyword-based",
            "supported_image_formats": ["jpg", "jpeg", "png", "bmp", "tiff", "gif"],
            "supported_document_types": self.classification_service.document_types,
            "entity_extraction": True,
            "summary_generation": True,
            "preprocessing": True
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
            
            # Process documents concurrently
            tasks = []
            for file_path in file_paths:
                if os.path.exists(file_path):
                    file_type = file_path.split('.')[-1].lower()
                    task = self.process_document(file_path, file_type)
                    tasks.append(task)
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions
            valid_results = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"❌ Batch processing error: {result}")
                else:
                    valid_results.append(result)
            
            logger.info(f"✅ Batch processing completed: {len(valid_results)}/{len(file_paths)} successful")
            return valid_results
            
        except Exception as e:
            logger.error(f"❌ Batch processing failed: {e}")
            return []
    
    def validate_document(self, file_path: str) -> Dict:
        """
        Validate document before processing
        
        Args:
            file_path: Path to document file
            
        Returns:
            Dict containing validation results
        """
        try:
            if not os.path.exists(file_path):
                return {
                    "valid": False,
                    "error": "File does not exist",
                    "file_size": 0,
                    "file_type": ""
                }
            
            # Get file info
            file_size = os.path.getsize(file_path)
            file_type = file_path.split('.')[-1].lower()
            
            # Check file size (max 50MB)
            if file_size > 50 * 1024 * 1024:  # 50MB
                return {
                    "valid": False,
                    "error": "File too large (max 50MB)",
                    "file_size": file_size,
                    "file_type": file_type
                }
            
            # Check supported file types
            supported_types = ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'gif', 'pdf']
            if file_type not in supported_types:
                return {
                    "valid": False,
                    "error": f"Unsupported file type: {file_type}",
                    "file_size": file_size,
                    "file_type": file_type
                }
            
            return {
                "valid": True,
                "file_size": file_size,
                "file_type": file_type,
                "supported": True
            }
            
        except Exception as e:
            logger.error(f"❌ Document validation failed: {e}")
            return {
                "valid": False,
                "error": str(e),
                "file_size": 0,
                "file_type": ""
            }
