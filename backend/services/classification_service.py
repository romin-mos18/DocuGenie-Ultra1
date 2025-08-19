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
            "financial_report",
            "bank_statement",
            "appointment",
            "patient_record",
            "insurance_claim",
            "prescription",
            "clinical_trial",
            "consent_form",
            "insurance",
            "billing",
            "administrative",
            "certificate",
            "technical_document",
            "technical_report",
            "qa_document",
            "guide",
            "tutorial",
            "manual",
            "presentation",
            "legal_document",
            "contract",
            "other"
        ]
        
        # Enhanced keywords for all document types in Testing Documents
        self.keywords = {
            "medical_report": [
                "patient", "diagnosis", "treatment", "symptoms", "medical", "report",
                "physician", "doctor", "clinic", "hospital", "examination", "findings",
                "consultation", "assessment", "clinical", "history", "condition", "therapeutic",
                "prognosis", "evaluation", "consultation report", "medical history", "progress note",
                "discharge summary", "attending physician", "mrn", "congestive heart failure"
            ],
            "lab_result": [
                "laboratory", "lab results", "blood test", "urine test", "lab work", "lab",
                "biochemistry", "hematology", "microbiology", "pathology", "lab values",
                "specimen", "glucose", "hemoglobin", "cholesterol", "culture", "biopsy",
                "lab report", "blood work", "normal range", "abnormal", "reference range",
                "platelet", "white blood cell", "red blood cell", "serum", "plasma",
                "test results", "reference values", "clinical chemistry"
            ],
            "financial_report": [
                "revenue", "expenses", "profit", "profit margin", "financial", "income",
                "financial report", "quarterly", "monthly", "balance sheet", "p&l",
                "profit and loss", "earnings", "expenditure", "budget", "cost analysis",
                "financial data", "accounting", "fiscal", "financial statement"
            ],
            "bank_statement": [
                "bank statement", "account balance", "transaction", "deposit", "withdrawal",
                "checking account", "savings account", "bank", "banking", "account number",
                "routing number", "balance", "debit", "credit", "transfer", "wire",
                "account summary", "statement period", "available balance"
            ],
            "appointment": [
                "appointment", "appointment date", "appointment time", "patient name",
                "provider", "doctor appointment", "medical appointment", "schedule",
                "appointment type", "duration", "appointment id", "appointment_id",
                "visit", "consultation", "new patient", "follow up", "routine check"
            ],
            "patient_record": [
                "patient record", "patient information", "patient data", "medical record",
                "patient_name", "patient demographics", "medical history", "health record",
                "patient id", "patient chart", "clinical record", "health information",
                "patient file", "medical file", "patient documentation"
            ],
            "insurance_claim": [
                "insurance claim", "claim number", "claim id", "insurance", "coverage",
                "policy number", "deductible", "copay", "claim amount", "benefits",
                "reimbursement", "claim status", "authorization", "pre-authorization",
                "insurance_claim", "claim form", "medical claim", "health insurance"
            ],
            "prescription": [
                "prescription", "medication", "drug", "dosage", "pharmacy", "rx",
                "tablet", "capsule", "injection", "refill", "prescribed", "medication list",
                "prescriber", "drug name", "strength", "quantity", "directions",
                "prescription number", "prescription_id", "medication order"
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
                "balance", "statement", "account", "financial", "billing", "invoice_id",
                "invoice number", "due date", "total amount", "payment terms"
            ],
            "administrative": [
                "administrative", "form", "application", "registration", "appointment",
                "schedule", "record", "documentation", "policy", "procedure"
            ],
            "certificate": [
                "certificate", "certification", "certified", "credential", "diploma",
                "award", "achievement", "completion", "qualification", "license",
                "accreditation", "badge", "honors", "degree", "title", "training completion",
                "course completion", "certificate number", "cert", "issue date"
            ],
            "technical_document": [
                "api", "sdk", "programming", "code", "software", "development",
                "integration", "implementation", "architecture", "system", "framework",
                "library", "database", "server", "client", "backend", "frontend",
                "algorithm", "technical", "engineering", "specification", "protocol"
            ],
            "technical_report": [
                "technical report", "analysis report", "performance report", "test report",
                "evaluation", "assessment", "review", "audit", "inspection", "quality",
                "validation", "verification", "benchmark", "metrics", "statistics",
                "findings", "conclusions", "recommendations", "methodology"
            ],
            "qa_document": [
                "quality assurance", "qa", "qc", "quality control", "testing", "validation",
                "verification", "compliance", "standards", "checklist", "test plan",
                "test case", "bug", "defect", "issue", "requirement", "specification"
            ],
            "guide": [
                "guide", "tutorial", "walkthrough", "step by step", "how to", "instructions",
                "manual", "handbook", "documentation", "setup", "installation", "configuration",
                "getting started", "quick start", "user guide", "admin guide"
            ],
            "tutorial": [
                "tutorial", "lesson", "course", "training", "workshop", "example",
                "demo", "demonstration", "practice", "exercise", "learning", "education",
                "teach", "learn", "study", "module", "chapter", "section"
            ],
            "manual": [
                "manual", "handbook", "reference", "documentation", "user manual",
                "admin manual", "operation manual", "maintenance", "troubleshooting",
                "faq", "frequently asked questions", "help", "support"
            ],
            "presentation": [
                "presentation", "slide", "slideshow", "powerpoint", "deck", "slides",
                "keynote", "pitch", "demo", "overview", "summary", "briefing",
                "meeting", "conference", "seminar", "webinar"
            ],
            "legal_document": [
                "legal", "law", "regulation", "statute", "code", "rule", "policy",
                "terms", "conditions", "privacy", "disclaimer", "notice", "agreement",
                "contract", "license", "copyright", "trademark", "patent"
            ],
            "contract": [
                "contract", "agreement", "terms", "conditions", "service agreement",
                "license agreement", "user agreement", "privacy policy", "terms of service",
                "terms of use", "end user license", "software license", "subscription",
                "contract_id", "contract number", "party", "parties", "obligations"
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
                # Try to load existing model
                try:
                    if ML_AVAILABLE:
                        self.classifier = joblib.load(model_path)
                        logger.info("✅ Loaded existing classification model")
                except Exception as load_error:
                    logger.warning(f"⚠️ Failed to load existing model: {load_error}")
                    logger.info("🔄 Creating new model to replace corrupted one...")
                    # Remove corrupted file
                    try:
                        os.remove(model_path)
                        logger.info("🗑️ Removed corrupted model file")
                    except Exception as remove_error:
                        logger.warning(f"⚠️ Could not remove corrupted file: {remove_error}")
                    # Create new model
                    self._create_model_with_sample_data()
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
            
            # Create and train model (only if ML libraries are available)
            if ML_AVAILABLE:
                self.classifier = Pipeline([
                    ('tfidf', TfidfVectorizer(max_features=1000, stop_words='english')),
                    ('clf', MultinomialNB())
                ])
                
                self.classifier.fit(documents, labels)
                
                # Save model
                os.makedirs("models", exist_ok=True)
                if ML_AVAILABLE:
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
            
            # Force keyword-based classification for now (ML model trained only on medical data)
            # TODO: Retrain ML model with new document types
            # if self.classifier and ML_AVAILABLE:
            #     # Use ML model for classification
            #     prediction = self.classifier.predict([cleaned_text])[0]
            #     confidence = self._calculate_confidence(cleaned_text, prediction)
            # else:
            #     # Use keyword-based classification
            #     prediction, confidence = self._keyword_based_classification(cleaned_text)
            
            # Use improved keyword-based classification
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
        """Classify document using improved keyword matching with specificity weighting"""
        scores = {}
        debug_info = {}
        
        # Check for strong indicators first (multi-word phrases)
        strong_indicators = {
            "financial_report": ["revenue", "expenses", "profit", "profit margin", "financial report", "p&l"],
            "bank_statement": ["bank statement", "account balance", "transaction", "deposit", "withdrawal"],
            "appointment": ["appointment", "appointment_id", "appointment date", "appointment time", "provider"],
            "patient_record": ["patient record", "patient_name", "patient information", "medical record", "health record"],
            "insurance_claim": ["insurance claim", "claim number", "claim_id", "policy number", "reimbursement"],
            "certificate": ["certificate", "certification", "certified", "diploma", "credential", "training completion"],
            "qa_document": ["quality assurance", "qa", "validation", "verification", "test plan"],
            "technical_document": ["api", "sdk", "integration", "implementation", "programming"],
            "technical_report": ["technical report", "analysis report", "performance report"],
            "guide": ["guide", "tutorial", "walkthrough", "step by step", "how to"],
            "manual": ["manual", "handbook", "user manual", "admin manual"],
            "lab_result": ["lab report", "blood test", "lab results", "laboratory", "specimen"],
            "contract": ["contract", "agreement", "contract_id", "party", "parties", "obligations"],
            "billing": ["invoice", "invoice_id", "bill", "payment", "due date", "total amount"]
        }
        
        # Score strong indicators first
        for doc_type, indicators in strong_indicators.items():
            strong_score = 0
            matched_indicators = []
            for indicator in indicators:
                if indicator.lower() in text.lower():
                    strong_score += 2  # Double weight for strong indicators
                    matched_indicators.append(indicator)
            
            if strong_score > 0:
                scores[doc_type] = strong_score / len(indicators)
                debug_info[doc_type] = f"Strong matches: {matched_indicators}"
        
        # Then check regular keywords for types that didn't get strong matches
        for doc_type, keywords in self.keywords.items():
            if doc_type not in scores:  # Only if no strong indicators found
                score = 0
                matched_keywords = []
                for keyword in keywords:
                    if keyword.lower() in text.lower():
                        score += 1
                        matched_keywords.append(keyword)
                
                # Normalize score by number of keywords
                if keywords:
                    scores[doc_type] = score / len(keywords)
                    debug_info[doc_type] = f"Regular matches: {matched_keywords[:5]}"
        
        # Find best match
        if scores:
            best_type = max(scores.items(), key=lambda x: x[1])[0]
            confidence = scores[best_type]
            
            # Debug info
            print(f"🔍 Classification debug for text '{text[:50]}...':")
            for doc_type, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"   {doc_type}: {score:.3f} - {debug_info.get(doc_type, 'No matches')}")
            print(f"   → Selected: {best_type} (confidence: {confidence:.3f})")
            
            # If confidence is too low, classify as "other"
            if confidence < 0.05:  # Lower threshold for better sensitivity
                return "other", 0.5
            else:
                return best_type, min(confidence * 1.5, 1.0)  # Boost confidence slightly
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
    
    def extract_entities(self, text: str) -> Dict:
        """
        Extract named entities from document text
        
        Args:
            text: Document text content
            
        Returns:
            Dict containing extracted entities
        """
        try:
            if not text or not text.strip():
                return {
                    "success": False,
                    "error": "No text content provided",
                    "entities": {},
                    "entity_count": 0
                }
            
            import re
            
            entities = {
                "dates": [],
                "names": [],
                "organizations": [],
                "locations": [],
                "medical_terms": [],
                "financial_terms": [],
                "numbers": [],
                "amounts": [],
                "identifiers": [],
                "emails": [],
                "phone_numbers": [],
                "addresses": []
            }
            
            # Extract dates
            date_patterns = [
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY
                r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',    # YYYY/MM/DD
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'  # Month DD, YYYY
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities["dates"].extend(matches)
            
            # Extract potential names (capitalized words)
            name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
            entities["names"] = re.findall(name_pattern, text)[:10]  # Limit to 10
            
            # Extract organizations (words ending with common org suffixes)
            org_patterns = [
                r'\b[A-Z][a-z]+(?: [A-Z][a-z]+)* (?:Hospital|Clinic|Medical Center|Laboratory|Lab|Institute)\b',
                r'\b[A-Z][a-z]+(?: [A-Z][a-z]+)* (?:University|College|Corporation|Corp|Company|Inc|LLC)\b'
            ]
            
            for pattern in org_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities["organizations"].extend(matches)
            
            # Extract medical terms
            medical_keywords = [
                "diagnosis", "treatment", "symptoms", "medication", "prescription",
                "laboratory", "test", "result", "blood", "urine", "analysis",
                "patient", "physician", "doctor", "clinic", "hospital", "discharge",
                "congestive heart failure", "hypertension", "diabetes", "cholesterol"
            ]
            
            for keyword in medical_keywords:
                if keyword.lower() in text.lower():
                    entities["medical_terms"].append(keyword)
            
            # Extract financial terms
            financial_keywords = [
                "revenue", "expenses", "profit", "margin", "income", "balance",
                "transaction", "deposit", "withdrawal", "account", "bank",
                "payment", "amount", "cost", "fee", "invoice", "bill", "statement"
            ]
            
            for keyword in financial_keywords:
                if keyword.lower() in text.lower():
                    entities["financial_terms"].append(keyword)
            
            # Extract monetary amounts
            amount_patterns = [
                r'\$\d+(?:,\d{3})*(?:\.\d{2})?',  # $1,234.56
                r'\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|dollars?)\b',  # 1234.56 USD
                r'\b\d+(?:\.\d{2})?\%',  # 12.5%
            ]
            
            for pattern in amount_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities["amounts"].extend(matches)
            
            # Extract emails
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            entities["emails"] = re.findall(email_pattern, text)
            
            # Extract phone numbers
            phone_patterns = [
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890
                r'\(\d{3}\)\s?\d{3}[-.]?\d{4}',    # (123) 456-7890
                r'\+1[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # +1-123-456-7890
            ]
            
            for pattern in phone_patterns:
                matches = re.findall(pattern, text)
                entities["phone_numbers"].extend(matches)
            
            # Extract numbers and IDs
            number_patterns = [
                r'\bMRN:?\s*(\d+)\b',  # Medical Record Number
                r'\bID:?\s*(\d+)\b',   # Generic ID
                r'\b\d{4,}\b'          # Any 4+ digit number
            ]
            
            for pattern in number_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities["identifiers"].extend(matches)
            
            # Count total entities
            total_entities = sum(len(v) for v in entities.values() if isinstance(v, list))
            
            return {
                "success": True,
                "entities": entities,
                "entity_count": total_entities,
                "text_length": len(text)
            }
            
        except Exception as e:
            logger.error(f"❌ Entity extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "entities": {},
                "entity_count": 0
            }
