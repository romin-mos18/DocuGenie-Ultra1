"""
OCR Service for document text extraction
"""
import os
import logging
from typing import Dict, List, Optional, Tuple
from PIL import Image
import cv2
import numpy as np
from paddleocr import PaddleOCR
from ..core.config import settings

logger = logging.getLogger(__name__)

class OCRService:
    """OCR service for document text extraction"""
    
    def __init__(self):
        """Initialize OCR service"""
        try:
            # Initialize PaddleOCR
            self.ocr = PaddleOCR(
                use_angle_cls=True,
                lang='en',
                use_gpu=False,  # Set to True if GPU available
                show_log=False
            )
            logger.info("✅ OCR service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize OCR service: {e}")
            self.ocr = None
    
    def extract_text_from_image(self, image_path: str) -> Dict:
        """
        Extract text from image file
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict containing extracted text and metadata
        """
        try:
            if not self.ocr:
                return {
                    "success": False,
                    "error": "OCR service not initialized",
                    "text": "",
                    "confidence": 0.0,
                    "word_count": 0
                }
            
            # Read image
            if not os.path.exists(image_path):
                return {
                    "success": False,
                    "error": f"Image file not found: {image_path}",
                    "text": "",
                    "confidence": 0.0,
                    "word_count": 0
                }
            
            # Perform OCR
            result = self.ocr.ocr(image_path, cls=True)
            
            if not result or not result[0]:
                return {
                    "success": True,
                    "text": "",
                    "confidence": 0.0,
                    "word_count": 0,
                    "message": "No text detected in image"
                }
            
            # Extract text and confidence scores
            extracted_text = []
            confidence_scores = []
            
            for line in result[0]:
                if line and len(line) >= 2:
                    text = line[1][0]  # Text content
                    confidence = line[1][1]  # Confidence score
                    
                    if text.strip():
                        extracted_text.append(text.strip())
                        confidence_scores.append(confidence)
            
            # Combine all text
            full_text = " ".join(extracted_text)
            word_count = len(full_text.split())
            
            # Calculate average confidence
            avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            
            return {
                "success": True,
                "text": full_text,
                "confidence": float(avg_confidence),
                "word_count": word_count,
                "lines": len(extracted_text),
                "raw_result": result
            }
            
        except Exception as e:
            logger.error(f"❌ OCR extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0,
                "word_count": 0
            }
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dict containing extracted text and metadata
        """
        try:
            # For now, return a placeholder
            # TODO: Implement PDF text extraction
            return {
                "success": True,
                "text": f"PDF text extraction from {pdf_path}",
                "confidence": 0.8,
                "word_count": 100,
                "message": "PDF extraction placeholder"
            }
            
        except Exception as e:
            logger.error(f"❌ PDF extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0,
                "word_count": 0
            }
    
    def preprocess_image(self, image_path: str) -> str:
        """
        Preprocess image for better OCR results
        
        Args:
            image_path: Path to original image
            
        Returns:
            Path to preprocessed image
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return image_path
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply noise reduction
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # Save preprocessed image
            preprocessed_path = image_path.replace('.', '_preprocessed.')
            cv2.imwrite(preprocessed_path, enhanced)
            
            return preprocessed_path
            
        except Exception as e:
            logger.error(f"❌ Image preprocessing failed: {e}")
            return image_path
    
    def validate_image(self, image_path: str) -> bool:
        """
        Validate if image is suitable for OCR
        
        Args:
            image_path: Path to image file
            
        Returns:
            True if image is valid for OCR
        """
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                return False
            
            # Check file size (max 10MB)
            file_size = os.path.getsize(image_path)
            if file_size > 10 * 1024 * 1024:  # 10MB
                return False
            
            # Check if it's a valid image
            try:
                with Image.open(image_path) as img:
                    # Check image dimensions
                    width, height = img.size
                    if width < 100 or height < 100:
                        return False
                    if width > 4000 or height > 4000:
                        return False
                    
                    # Check if image has content
                    if img.mode == 'RGBA':
                        # Convert to RGB for better OCR
                        img = img.convert('RGB')
                    
                    return True
                    
            except Exception:
                return False
                
        except Exception as e:
            logger.error(f"❌ Image validation failed: {e}")
            return False
