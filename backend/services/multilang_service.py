#!/usr/bin/env python3
"""
Multi-Language Support Service for DocuGenie Ultra
Provides international healthcare document processing with language detection and translation
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
from pathlib import Path
from enum import Enum

# Language processing imports
try:
    import langdetect
    from langdetect import detect, detect_langs
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    print("⚠️ langdetect not available. Please install: pip install langdetect")

# Simplified translation without googletrans to avoid compatibility issues
GOOGLETRANS_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("⚠️ spaCy not available. Please install: pip install spacy")

# Configuration - using environment variables directly

logger = logging.getLogger(__name__)

class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    HINDI = "hi"
    DUTCH = "nl"
    SWEDISH = "sv"
    NORWEGIAN = "no"
    DANISH = "da"
    FINNISH = "fi"
    POLISH = "pl"
    TURKISH = "tr"
    GREEK = "el"

class MultiLanguageService:
    """Service for multi-language healthcare document processing"""
    
    def __init__(self):
        """Initialize multi-language service"""
        self.supported_languages = {lang.value: lang.name for lang in Language}
        self.healthcare_terms = self._load_healthcare_terms()
        self.language_models = {}
        
        # Initialize language processing capabilities
        self.langdetect_available = LANGDETECT_AVAILABLE
        self.translation_available = GOOGLETRANS_AVAILABLE
        self.nlp_available = SPACY_AVAILABLE
        
        # Translation service disabled to avoid compatibility issues
        self.translator = None
        
        # Initialize NLP models for key languages
        self._initialize_nlp_models()
        
        logger.info("✅ Multi-Language Service initialized successfully")
    
    def _load_healthcare_terms(self) -> Dict[str, Dict[str, str]]:
        """Load healthcare terminology in multiple languages"""
        return {
            "en": {
                "medical_record": "Medical Record",
                "lab_result": "Laboratory Result",
                "prescription": "Prescription",
                "diagnosis": "Diagnosis",
                "treatment": "Treatment",
                "medication": "Medication",
                "symptoms": "Symptoms",
                "allergies": "Allergies",
                "blood_pressure": "Blood Pressure",
                "heart_rate": "Heart Rate"
            },
            "es": {
                "medical_record": "Expediente Médico",
                "lab_result": "Resultado de Laboratorio",
                "prescription": "Receta Médica",
                "diagnosis": "Diagnóstico",
                "treatment": "Tratamiento",
                "medication": "Medicamento",
                "symptoms": "Síntomas",
                "allergies": "Alergias",
                "blood_pressure": "Presión Arterial",
                "heart_rate": "Frecuencia Cardíaca"
            },
            "fr": {
                "medical_record": "Dossier Médical",
                "lab_result": "Résultat de Laboratoire",
                "prescription": "Ordonnance",
                "diagnosis": "Diagnostic",
                "treatment": "Traitement",
                "medication": "Médicament",
                "symptoms": "Symptômes",
                "allergies": "Allergies",
                "blood_pressure": "Tension Artérielle",
                "heart_rate": "Fréquence Cardiaque"
            },
            "de": {
                "medical_record": "Krankenakte",
                "lab_result": "Laborergebnis",
                "prescription": "Rezept",
                "diagnosis": "Diagnose",
                "treatment": "Behandlung",
                "medication": "Medikament",
                "symptoms": "Symptome",
                "allergies": "Allergien",
                "blood_pressure": "Blutdruck",
                "heart_rate": "Herzfrequenz"
            }
        }
    
    def _initialize_nlp_models(self):
        """Initialize NLP models for key languages"""
        if not self.nlp_available:
            return
        
        try:
            # Load English model by default
            try:
                self.language_models["en"] = spacy.load("en_core_web_sm")
                logger.info("✅ Loaded English NLP model")
            except OSError:
                logger.warning("⚠️ English NLP model not found. Install with: python -m spacy download en_core_web_sm")
            
            # Add other languages as needed
            # In production, you would load models for all supported languages
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize NLP models: {e}")
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect the language of text content"""
        try:
            if not self.langdetect_available:
                return {
                    "success": False,
                    "error": "Language detection not available"
                }
            
            if not text or len(text.strip()) < 10:
                return {
                    "success": False,
                    "error": "Text too short for reliable language detection"
                }
            
            # Detect primary language
            primary_lang = detect(text)
            
            # Get confidence scores for all detected languages
            detected_langs = detect_langs(text)
            
            # Format results
            language_scores = []
            for lang in detected_langs:
                language_scores.append({
                    "language": lang.lang,
                    "language_name": self.supported_languages.get(lang.lang, "Unknown"),
                    "confidence": lang.prob
                })
            
            # Sort by confidence
            language_scores.sort(key=lambda x: x["confidence"], reverse=True)
            
            return {
                "success": True,
                "primary_language": primary_lang,
                "primary_language_name": self.supported_languages.get(primary_lang, "Unknown"),
                "detected_languages": language_scores,
                "confidence": language_scores[0]["confidence"] if language_scores else 0.0
            }
            
        except Exception as e:
            logger.error(f"❌ Language detection failed: {e}")
            return {
                "success": False,
                "error": f"Language detection failed: {str(e)}"
            }
    
    def translate_text(
        self, 
        text: str, 
        target_language: str, 
        source_language: str = None
    ) -> Dict[str, Any]:
        """Translate text to target language"""
        try:
            if not self.translation_available:
                return {
                    "success": False,
                    "error": "Translation service not available"
                }
            
            if not text or len(text.strip()) == 0:
                return {
                    "success": False,
                    "error": "No text to translate"
                }
            
            # Validate target language
            if target_language not in self.supported_languages:
                return {
                    "success": False,
                    "error": f"Unsupported target language: {target_language}"
                }
            
            # Perform translation
            if source_language:
                translation = self.translator.translate(
                    text, 
                    dest=target_language, 
                    src=source_language
                )
            else:
                translation = self.translator.translate(text, dest=target_language)
            
            return {
                "success": True,
                "original_text": text,
                "translated_text": translation.text,
                "source_language": translation.src,
                "target_language": translation.dest,
                "confidence": 0.9,  # Google Translate confidence
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Translation failed: {e}")
            return {
                "success": False,
                "error": f"Translation failed: {str(e)}"
            }
    
    def translate_healthcare_terms(
        self, 
        terms: List[str], 
        target_language: str
    ) -> Dict[str, Any]:
        """Translate healthcare terminology to target language"""
        try:
            if target_language not in self.healthcare_terms:
                return {
                    "success": False,
                    "error": f"Healthcare terms not available for language: {target_language}"
                }
            
            translations = {}
            available_terms = self.healthcare_terms[target_language]
            
            for term in terms:
                if term in available_terms:
                    translations[term] = available_terms[term]
                else:
                    # Try to translate using translation service
                    if self.translation_available:
                        try:
                            translation = self.translator.translate(term, dest=target_language)
                            translations[term] = translation.text
                        except:
                            translations[term] = f"[{term}]"  # Mark as untranslated
                    else:
                        translations[term] = f"[{term}]"
            
            return {
                "success": True,
                "target_language": target_language,
                "translations": translations,
                "total_terms": len(terms),
                "translated_terms": len([v for v in translations.values() if not v.startswith("[")])
            }
            
        except Exception as e:
            logger.error(f"❌ Healthcare terms translation failed: {e}")
            return {
                "success": False,
                "error": f"Terms translation failed: {str(e)}"
            }
    
    def process_multilingual_document(
        self, 
        content: str, 
        target_language: str = "en"
    ) -> Dict[str, Any]:
        """Process document in multiple languages"""
        try:
            # Detect source language
            lang_detection = self.detect_language(content)
            
            if not lang_detection["success"]:
                return {
                    "success": False,
                    "error": "Failed to detect document language"
                }
            
            source_language = lang_detection["primary_language"]
            
            # Check if translation is needed
            if source_language == target_language:
                return {
                    "success": True,
                    "translation_needed": False,
                    "source_language": source_language,
                    "target_language": target_language,
                    "original_content": content,
                    "translated_content": content,
                    "language_confidence": lang_detection["confidence"]
                }
            
            # Translate content
            translation = self.translate_text(content, target_language, source_language)
            
            if not translation["success"]:
                return {
                    "success": False,
                    "error": f"Translation failed: {translation['error']}"
                }
            
            return {
                "success": True,
                "translation_needed": True,
                "source_language": source_language,
                "target_language": target_language,
                "original_content": content,
                "translated_content": translation["translated_text"],
                "language_confidence": lang_detection["confidence"],
                "translation_confidence": translation["confidence"]
            }
            
        except Exception as e:
            logger.error(f"❌ Multilingual document processing failed: {e}")
            return {
                "success": False,
                "error": f"Multilingual processing failed: {str(e)}"
            }
    
    def extract_healthcare_entities(
        self, 
        text: str, 
        language: str = "en"
    ) -> Dict[str, Any]:
        """Extract healthcare entities from text using NLP"""
        try:
            if not self.nlp_available:
                return {
                    "success": False,
                    "error": "NLP not available for entity extraction"
                }
            
            if language not in self.language_models:
                return {
                    "success": False,
                    "error": f"NLP model not available for language: {language}"
                }
            
            # Process text with spaCy
            doc = self.language_models[language](text)
            
            # Extract entities
            entities = []
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "description": spacy.explain(ent.label_)
                })
            
            # Extract medical terms
            medical_terms = []
            for token in doc:
                if token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 3:
                    medical_terms.append({
                        "term": token.text,
                        "pos": token.pos_,
                        "lemma": token.lemma_
                    })
            
            return {
                "success": True,
                "language": language,
                "entities": entities,
                "medical_terms": medical_terms,
                "total_entities": len(entities),
                "total_medical_terms": len(medical_terms)
            }
            
        except Exception as e:
            logger.error(f"❌ Entity extraction failed: {e}")
            return {
                "success": False,
                "error": f"Entity extraction failed: {str(e)}"
            }
    
    def batch_translate_documents(
        self, 
        documents: List[Dict[str, Any]], 
        target_language: str
    ) -> Dict[str, Any]:
        """Batch translate multiple documents"""
        try:
            results = []
            successful = 0
            failed = 0
            
            for doc in documents:
                try:
                    content = doc.get('content', '')
                    if content:
                        result = self.process_multilingual_document(content, target_language)
                        if result["success"]:
                            successful += 1
                        else:
                            failed += 1
                        
                        results.append({
                            "document_id": doc.get('id'),
                            "filename": doc.get('filename'),
                            "translation_result": result
                        })
                    else:
                        failed += 1
                        results.append({
                            "document_id": doc.get('id'),
                            "filename": doc.get('filename'),
                            "translation_result": {
                                "success": False,
                                "error": "No content to translate"
                            }
                        })
                        
                except Exception as e:
                    failed += 1
                    results.append({
                        "document_id": doc.get('id'),
                        "filename": doc.get('filename'),
                        "translation_result": {
                            "success": False,
                            "error": str(e)
                        }
                    })
            
            return {
                "success": True,
                "target_language": target_language,
                "total_documents": len(documents),
                "successful_translations": successful,
                "failed_translations": failed,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Batch translation failed: {e}")
            return {
                "success": False,
                "error": f"Batch translation failed: {str(e)}"
            }
    
    def get_language_support_info(self) -> Dict[str, Any]:
        """Get information about language support capabilities"""
        return {
            "supported_languages": self.supported_languages,
            "total_languages": len(self.supported_languages),
            "healthcare_terms_available": list(self.healthcare_terms.keys()),
            "nlp_models_loaded": list(self.language_models.keys()),
            "capabilities": {
                "language_detection": self.langdetect_available,
                "translation": self.translation_available,
                "nlp_processing": self.nlp_available,
                "healthcare_terminology": True,
                "batch_processing": True
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        return {
            "service_name": "MultiLanguageService",
            "langdetect_available": self.langdetect_available,
            "translation_available": self.translation_available,
            "nlp_available": self.nlp_available,
            "supported_languages": len(self.supported_languages),
            "healthcare_terms_languages": len(self.healthcare_terms),
            "loaded_nlp_models": len(self.language_models),
            "capabilities": {
                "multilingual_document_processing": True,
                "healthcare_entity_extraction": self.nlp_available,
                "batch_translation": True,
                "language_detection": self.langdetect_available
            },
            "timestamp": datetime.now().isoformat()
        }
