"""
OCR Service for document text extraction
"""
import os
import logging
from typing import Dict, List, Optional, Tuple
from PIL import Image
import cv2
import numpy as np

# Try to import PaddleOCR, but make it optional
try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    print("⚠️ PaddleOCR not available. Using basic OCR features.")

from core.config import settings

logger = logging.getLogger(__name__)

class OCRService:
    """OCR service for document text extraction"""
    
    def __init__(self):
        """Initialize OCR service"""
        self.ocr = None
        self.paddleocr_available = PADDLEOCR_AVAILABLE
        
        if self.paddleocr_available:
            try:
                # Initialize PaddleOCR
                self.ocr = PaddleOCR(
                    use_angle_cls=True,
                    lang='en',
                    use_gpu=False,  # Set to True if GPU available
                    show_log=False
                )
                logger.info("✅ PaddleOCR service initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize PaddleOCR service: {e}")
                self.ocr = None
                self.paddleocr_available = False
        else:
            logger.info("ℹ️ Using basic OCR features (PaddleOCR not available)")
    
    def extract_text_from_image(self, image_path: str) -> Dict:
        """
        Extract text from image file
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict containing extracted text and metadata
        """
        try:
            if not os.path.exists(image_path):
                return {
                    "success": False,
                    "error": f"Image file not found: {image_path}",
                    "text": "",
                    "confidence": 0.0,
                    "word_count": 0
                }
            
            # If PaddleOCR is available, use it
            if self.ocr and self.paddleocr_available:
                return self._extract_text_with_paddleocr(image_path)
            else:
                # Fallback to basic image processing
                return self._extract_text_basic(image_path)
                
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0,
                "word_count": 0
            }
    
    def _extract_text_with_paddleocr(self, image_path: str) -> Dict:
        """Extract text using PaddleOCR"""
        try:
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
                "method": "paddleocr"
            }
            
        except Exception as e:
            logger.error(f"PaddleOCR extraction failed: {e}")
            return self._extract_text_basic(image_path)
    
    def _extract_text_basic(self, image_path: str) -> Dict:
        """Basic text extraction using image processing"""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return {
                    "success": False,
                    "error": "Could not read image file",
                    "text": "",
                    "confidence": 0.0,
                    "word_count": 0
                }
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get binary image
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Extract text regions (simplified)
            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 10 and h > 10:  # Filter small noise
                    text_regions.append((x, y, w, h))
            
            # For now, return basic info about detected regions
            return {
                "success": True,
                "text": f"Detected {len(text_regions)} text regions",
                "confidence": 0.5,  # Basic confidence
                "word_count": len(text_regions),
                "lines": len(text_regions),
                "method": "basic_processing",
                "message": "Basic image processing completed. Text extraction requires OCR library."
            }
            
        except Exception as e:
            logger.error(f"Basic extraction failed: {e}")
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
            if not os.path.exists(pdf_path):
                return {
                    "success": False,
                    "error": f"PDF file not found: {pdf_path}",
                    "text": "",
                    "confidence": 0.0,
                    "word_count": 0
                }
            
            # For now, return placeholder
            # TODO: Implement PDF text extraction
            return {
                "success": True,
                "text": "PDF text extraction not yet implemented",
                "confidence": 0.0,
                "word_count": 0,
                "message": "PDF processing requires additional libraries"
            }
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
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
            image_path: Path to input image
            
        Returns:
            Path to preprocessed image
        """
        try:
            if not os.path.exists(image_path):
                return image_path
            
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return image_path
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply adaptive threshold
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Save preprocessed image
            output_path = image_path.replace('.', '_preprocessed.')
            cv2.imwrite(output_path, thresh)
            
            logger.info(f"Image preprocessed and saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return image_path
    
    def validate_image(self, image_path: str) -> bool:
        """
        Validate if image file is suitable for OCR
        
        Args:
            image_path: Path to image file
            
        Returns:
            True if image is valid for OCR
        """
        try:
            if not os.path.exists(image_path):
                return False
            
            # Check file size
            file_size = os.path.getsize(image_path)
            if file_size == 0:
                return False
            
            # Try to open image
            image = cv2.imread(image_path)
            if image is None:
                return False
            
            # Check image dimensions
            height, width = image.shape[:2]
            if width < 10 or height < 10:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating image: {e}")
            return False
    
    def get_service_status(self) -> Dict:
        """Get OCR service status"""
        return {
            "available": self.paddleocr_available,
            "initialized": self.ocr is not None,
            "method": "paddleocr" if self.paddleocr_available else "basic",
            "status": "ready" if (self.ocr or not self.paddleocr_available) else "failed"
        }
