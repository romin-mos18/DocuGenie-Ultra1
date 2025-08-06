"""
Document Classification Service
"""
import os
import logging
import re
from typing import Dict, List, Optional, Tuple

# Try to import ML libraries, but make them optional
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report
    import joblib
    import numpy as np
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ ML libraries not available. Using keyword-based classification only.")

from core.config import settings

logger = logging.getLogger(__name__)

class DocumentClassificationService:
    """Document classification service for categorizing documents"""
    
    def __init__(self):
        """Initialize classification service"""
        self.model = None
        self.vectorizer = None
        self.classifier = None
        self.document_types = [
            "medical_report",
            "lab_result", 
            "prescription",
            "clinical_trial",
            "consent_form",
            "insurance",
            "billing",
            "administrative",
            "other"
        ]
        
        # Keywords for document classification
        self.keywords = {
            "medical_report": [
                "patient", "diagnosis", "treatment", "symptoms", "medical", "report",
                "physician", "doctor", "clinic", "hospital", "examination", "findings"
            ],
            "lab_result": [
                "laboratory", "test", "result", "blood", "urine", "analysis", "lab",
                "biochemistry", "hematology", "microbiology", "pathology", "values"
            ],
            "prescription": [
                "prescription", "medication", "drug", "dosage", "pharmacy", "rx",
                "tablet", "capsule", "injection", "refill", "prescribed"
            ],
            "clinical_trial": [
                "clinical", "trial", "study", "protocol", "investigation", "research",
                "participant", "informed consent", "phase", "randomized", "placebo"
            ],
            "consent_form": [
                "consent", "permission", "authorization", "agreement", "signature",
                "informed", "voluntary", "understand", "risks", "benefits"
            ],
            "insurance": [
                "insurance", "policy", "coverage", "claim", "benefits", "premium",
                "deductible", "copay", "provider", "network", "authorization"
            ],
            "billing": [
                "bill", "invoice", "payment", "charge", "cost", "fee", "amount",
                "balance", "statement", "account", "financial"
            ],
            "administrative": [
                "administrative", "form", "application", "registration", "appointment",
                "schedule", "record", "documentation", "policy", "procedure"
            ]
        }
        
        # Only try to load ML model if libraries are available
        if ML_AVAILABLE:
            self._load_or_create_model()
        else:
            logger.info("ℹ️ Using keyword-based classification (ML libraries not available)")
    
    def _load_or_create_model(self):
        """Load existing model or create new one"""
        if not ML_AVAILABLE:
            return
            
        model_path = "models/document_classifier.pkl"
        
        try:
            if os.path.exists(model_path):
                # Load existing model
                self.classifier = joblib.load(model_path)
                logger.info("✅ Loaded existing classification model")
            else:
                # Create new model with sample data
                self._create_model_with_sample_data()
                logger.info("✅ Created new classification model")
        except Exception as e:
            logger.error(f"❌ Failed to load/create model: {e}")
            self._create_simple_classifier()
    
    def _create_model_with_sample_data(self):
        """Create model with sample training data"""
        if not ML_AVAILABLE:
            return
            
        try:
            # Sample training data
            documents = []
            labels = []
            
            # Add sample documents for each type
            for doc_type, keywords in self.keywords.items():
                for keyword in keywords:
                    # Create sample documents with keywords
                    sample_text = f"This is a {doc_type} document containing {keyword} information."
                    documents.append(sample_text)
                    labels.append(doc_type)
            
            # Create and train model
            self.classifier = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=1000, stop_words='english')),
                ('clf', MultinomialNB())
            ])
            
            self.classifier.fit(documents, labels)
            
            # Save model
            os.makedirs("models", exist_ok=True)
            joblib.dump(self.classifier, "models/document_classifier.pkl")
            
        except Exception as e:
            logger.error(f"❌ Failed to create model: {e}")
            self._create_simple_classifier()
    
    def _create_simple_classifier(self):
        """Create a simple keyword-based classifier"""
        self.classifier = None
        logger.info("✅ Using simple keyword-based classification")
    
    def classify_document(self, text: str) -> Dict:
        """
        Classify document based on text content
        
        Args:
            text: Document text content
            
        Returns:
            Dict containing classification results
        """
        try:
            if not text or not text.strip():
                return {
                    "success": False,
                    "error": "No text content provided",
                    "document_type": "other",
                    "confidence": 0.0
                }
            
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            if self.classifier and ML_AVAILABLE:
                # Use ML model for classification
                prediction = self.classifier.predict([cleaned_text])[0]
                confidence = self._calculate_confidence(cleaned_text, prediction)
            else:
                # Use keyword-based classification
                prediction, confidence = self._keyword_based_classification(cleaned_text)
            
            return {
                "success": True,
                "document_type": prediction,
                "confidence": confidence,
                "text_length": len(text),
                "cleaned_text": cleaned_text[:200] + "..." if len(cleaned_text) > 200 else cleaned_text
            }
            
        except Exception as e:
            logger.error(f"❌ Document classification failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "document_type": "other",
                "confidence": 0.0
            }
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for classification"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _keyword_based_classification(self, text: str) -> Tuple[str, float]:
        """Classify document using keyword matching"""
        scores = {}
        
        for doc_type, keywords in self.keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text:
                    score += 1
            
            # Normalize score by number of keywords
            scores[doc_type] = score / len(keywords) if keywords else 0
        
        # Find best match
        if scores:
            best_type = max(scores, key=scores.get)
            confidence = scores[best_type]
            
            # If confidence is too low, classify as "other"
            if confidence < 0.1:
                return "other", 0.5
            else:
                return best_type, confidence
        else:
            return "other", 0.5
    
    def _calculate_confidence(self, text: str, prediction: str) -> float:
        """Calculate confidence score for ML prediction"""
        try:
            if not ML_AVAILABLE or not self.classifier:
                return 0.5
                
            # Get prediction probabilities
            proba = self.classifier.predict_proba([text])[0]
            max_prob = max(proba)
            
            # Normalize confidence
            confidence = min(max_prob * 2, 1.0)  # Scale to 0-1
            
            return confidence
        except Exception:
            return 0.5
    
    def extract_entities(self, text: str) -> Dict:
        """
        Extract named entities from document text
        
        Args:
            text: Document text content
            
        Returns:
            Dict containing extracted entities
        """
        try:
            entities = {
                "dates": [],
                "names": [],
                "organizations": [],
                "locations": [],
                "medical_terms": [],
                "numbers": []
            }
            
            # Extract dates (simple pattern)
            date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
            entities["dates"] = re.findall(date_pattern, text)
            
            # Extract numbers
            number_pattern = r'\b\d+(?:\.\d+)?\b'
            entities["numbers"] = re.findall(number_pattern, text)
            
            # Extract potential names (capitalized words)
            name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
            entities["names"] = re.findall(name_pattern, text)
            
            # Extract medical terms (common medical words)
            medical_terms = [
                "diagnosis", "treatment", "symptoms", "patient", "physician",
                "medication", "prescription", "laboratory", "test", "result"
            ]
            
            text_lower = text.lower()
            for term in medical_terms:
                if term in text_lower:
                    entities["medical_terms"].append(term)
            
            return {
                "success": True,
                "entities": entities,
                "entity_count": sum(len(v) for v in entities.values())
            }
            
        except Exception as e:
            logger.error(f"❌ Entity extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "entities": {},
                "entity_count": 0
            }
    
    def get_document_summary(self, text: str) -> Dict:
        """
        Generate document summary
        
        Args:
            text: Document text content
            
        Returns:
            Dict containing document summary
        """
        try:
            # Simple summary generation
            sentences = text.split('.')
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # Take first few sentences as summary
            summary_sentences = sentences[:3]
            summary = '. '.join(summary_sentences) + '.'
            
            return {
                "success": True,
                "summary": summary,
                "word_count": len(text.split()),
                "sentence_count": len(sentences),
                "summary_length": len(summary)
            }
            
        except Exception as e:
            logger.error(f"❌ Summary generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "summary": "",
                "word_count": 0,
                "sentence_count": 0
            }
