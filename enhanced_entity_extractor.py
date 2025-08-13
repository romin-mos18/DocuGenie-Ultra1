#!/usr/bin/env python3
"""
Enhanced Entity Extractor for DocuGenie Ultra
Learns from processed documents to improve entity extraction accuracy
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EnhancedEntityExtractor:
    """Enhanced entity extractor with learning capabilities"""
    
    def __init__(self):
        """Initialize enhanced entity extractor"""
        self.learned_patterns = {
            "names": defaultdict(list),
            "organizations": defaultdict(list),
            "locations": defaultdict(list),
            "dates": defaultdict(list),
            "medical_terms": defaultdict(list),
            "numbers": defaultdict(list),
            "identifiers": defaultdict(list)
        }
        
        self.document_type_patterns = defaultdict(dict)
        self.extraction_rules = self._initialize_extraction_rules()
        
        # Load learned patterns if available
        self._load_learned_patterns()
    
    def _initialize_extraction_rules(self) -> Dict:
        """Initialize extraction rules for different entity types"""
        return {
            "names": {
                "patterns": [
                    r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # First Last
                    r'\b[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+\b',  # First Middle Last
                    r'\b[A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+\b',  # First M. Last
                ],
                "context_keywords": ["patient", "doctor", "physician", "nurse", "attending", "resident"],
                "confidence_boost": 0.2
            },
            
            "organizations": {
                "patterns": [
                    r'\b[A-Z][a-z]+(?: [A-Z][a-z]+)* (?:Hospital|Clinic|Medical Center|Laboratory|Lab|Institute)\b',
                    r'\b[A-Z][a-z]+(?: [A-Z][a-z]+)* (?:University|College|School)\b',
                    r'\b[A-Z][a-z]+(?: [A-Z][a-z]+)* (?:Corporation|Corp|Company|Inc|LLC)\b',
                ],
                "context_keywords": ["hospital", "clinic", "lab", "medical", "healthcare", "facility"],
                "confidence_boost": 0.15
            },
            
            "locations": {
                "patterns": [
                    r'\b[A-Z][a-z]+, [A-Z]{2}\b',  # City, State
                    r'\b[A-Z][a-z]+ [A-Z][a-z]+, [A-Z]{2}\b',  # City Name, State
                    r'\b\d{5}(?:-\d{4})?\b',  # ZIP codes
                ],
                "context_keywords": ["address", "location", "city", "state", "zip", "postal"],
                "confidence_boost": 0.1
            },
            
            "dates": {
                "patterns": [
                    r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY
                    r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
                    r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',  # Month DD, YYYY
                ],
                "context_keywords": ["date", "report", "issued", "created", "updated", "effective"],
                "confidence_boost": 0.1
            },
            
            "medical_terms": {
                "patterns": [
                    r'\b(?:diagnosis|diagnoses|diagnostic)\b',
                    r'\b(?:treatment|therapy|therapeutic)\b',
                    r'\b(?:symptoms|symptom|clinical)\b',
                    r'\b(?:medication|medications|drug|drugs)\b',
                    r'\b(?:prescription|prescribed|dosage)\b',
                    r'\b(?:laboratory|lab|test|tests|results)\b',
                ],
                "context_keywords": ["medical", "clinical", "healthcare", "patient", "treatment"],
                "confidence_boost": 0.05
            },
            
            "identifiers": {
                "patterns": [
                    r'\bMRN:?\s*(\d+)\b',  # Medical Record Number
                    r'\bID:?\s*(\d+)\b',  # Generic ID
                    r'\bCase:?\s*(\d+)\b',  # Case number
                    r'\bAccount:?\s*(\d+)\b',  # Account number
                    r'\bReference:?\s*(\d+)\b',  # Reference number
                ],
                "context_keywords": ["mrn", "id", "case", "account", "reference", "number"],
                "confidence_boost": 0.2
            }
        }
    
    def extract_entities_enhanced(self, text: str, document_type: str = "unknown") -> Dict[str, Any]:
        """Extract entities using enhanced patterns and learning"""
        try:
            entities = {
                "names": [],
                "organizations": [],
                "locations": [],
                "dates": [],
                "medical_terms": [],
                "numbers": [],
                "identifiers": [],
                "custom_entities": []
            }
            
            # Extract using base patterns
            for entity_type, rules in self.extraction_rules.items():
                if entity_type in entities:
                    extracted = self._extract_with_patterns(text, rules, entity_type)
                    entities[entity_type] = extracted
            
            # Extract numbers (general)
            entities["numbers"] = self._extract_numbers(text)
            
            # Apply document-type specific extraction
            if document_type != "unknown":
                entities = self._apply_document_type_extraction(entities, text, document_type)
            
            # Apply learned patterns
            entities = self._apply_learned_patterns(entities, text, document_type)
            
            # Extract custom entities based on context
            entities["custom_entities"] = self._extract_custom_entities(text, document_type)
            
            # Calculate confidence scores
            entities_with_confidence = self._add_confidence_scores(entities, text, document_type)
            
            return {
                "success": True,
                "entities": entities_with_confidence,
                "entity_count": sum(len(v) for v in entities.values() if isinstance(v, list)),
                "extraction_method": "enhanced",
                "document_type": document_type,
                "confidence": self._calculate_overall_confidence(entities_with_confidence),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Enhanced entity extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "entities": {},
                "entity_count": 0
            }
    
    def _extract_with_patterns(self, text: str, rules: Dict, entity_type: str) -> List[Dict]:
        """Extract entities using regex patterns and context"""
        extracted = []
        
        for pattern in rules["patterns"]:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entity_text = match.group()
                
                # Check context for confidence boost
                context_score = self._check_context(text, match.start(), match.end(), rules["context_keywords"])
                confidence = 0.7 + (context_score * rules["confidence_boost"])
                
                extracted.append({
                    "text": entity_text,
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": min(confidence, 1.0),
                    "pattern": pattern,
                    "context_boost": context_score > 0
                })
        
        # Remove duplicates and sort by confidence
        unique_entities = self._deduplicate_entities(extracted)
        return sorted(unique_entities, key=lambda x: x["confidence"], reverse=True)
    
    def _check_context(self, text: str, start: int, end: int, keywords: List[str]) -> float:
        """Check context around entity for confidence boost"""
        context_window = 100  # Characters before and after
        
        context_start = max(0, start - context_window)
        context_end = min(len(text), end + context_window)
        
        context_text = text[context_start:context_end].lower()
        
        # Count keyword matches in context
        keyword_matches = sum(1 for keyword in keywords if keyword.lower() in context_text)
        
        # Return normalized score (0-1)
        return min(keyword_matches / len(keywords), 1.0) if keywords else 0.0
    
    def _extract_numbers(self, text: str) -> List[Dict]:
        """Extract numbers with context"""
        numbers = []
        
        # Find all numbers
        number_patterns = [
            (r'\b\d+(?:\.\d+)?\b', 'decimal'),
            (r'\b\d{1,2}:\d{2}\b', 'time'),
            (r'\b\d{1,2}:\d{2}:\d{2}\b', 'time_full'),
            (r'\$\d+(?:,\d{3})*(?:\.\d{2})?\b', 'currency'),
            (r'\b\d+(?:,\d{3})*\b', 'integer')
        ]
        
        for pattern, number_type in number_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                numbers.append({
                    "text": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "type": number_type,
                    "confidence": 0.8,
                    "context": self._get_number_context(text, match.start(), match.end())
                })
        
        return numbers
    
    def _get_number_context(self, text: str, start: int, end: int) -> str:
        """Get context around a number"""
        context_window = 50
        context_start = max(0, start - context_window)
        context_end = min(len(text), end + context_window)
        return text[context_start:context_end].strip()
    
    def _apply_document_type_extraction(self, entities: Dict, text: str, document_type: str) -> Dict:
        """Apply document-type specific extraction rules"""
        if document_type == "lab_result":
            entities = self._extract_lab_specific_entities(entities, text)
        elif document_type == "medical_report":
            entities = self._extract_medical_report_entities(entities, text)
        elif document_type == "prescription":
            entities = self._extract_prescription_entities(entities, text)
        elif document_type == "billing":
            entities = self._extract_billing_entities(entities, text)
        
        return entities
    
    def _extract_lab_specific_entities(self, entities: Dict, text: str) -> Dict:
        """Extract lab-specific entities"""
        # Lab values with ranges
        lab_patterns = [
            (r'(\w+)\s+([\d.]+)\s*[-–]\s*([\d.]+)', 'lab_range'),
            (r'(\w+)\s+([\d.]+)\s*[<>]\s*([\d.]+)', 'lab_threshold'),
            (r'(\w+)\s+([\d.]+)', 'lab_value')
        ]
        
        for pattern, entity_type in lab_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities["custom_entities"].append({
                    "text": match.group(),
                    "type": entity_type,
                    "confidence": 0.9,
                    "components": match.groups()
                })
        
        return entities
    
    def _extract_medical_report_entities(self, entities: Dict, text: str) -> Dict:
        """Extract medical report specific entities"""
        # Vital signs
        vital_patterns = [
            (r'Blood Pressure:\s*(\d+)/(\d+)', 'vital_sign'),
            (r'Heart Rate:\s*(\d+)', 'vital_sign'),
            (r'Temperature:\s*([\d.]+)', 'vital_sign'),
            (r'Weight:\s*([\d.]+)', 'vital_sign')
        ]
        
        for pattern, entity_type in vital_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities["custom_entities"].append({
                    "text": match.group(),
                    "type": entity_type,
                    "confidence": 0.9,
                    "components": match.groups()
                })
        
        return entities
    
    def _extract_prescription_entities(self, entities: Dict, text: str) -> Dict:
        """Extract prescription specific entities"""
        # Medication details
        med_patterns = [
            (r'(\w+)\s+(\d+)\s*(mg|mcg|g)', 'medication'),
            (r'(\w+)\s+(\d+)\s*(tablet|capsule|injection)', 'medication_form'),
            (r'Take\s+(\d+)\s*(?:tablet|pill|capsule)', 'dosage_instruction')
        ]
        
        for pattern, entity_type in med_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities["custom_entities"].append({
                    "text": match.group(),
                    "type": entity_type,
                    "confidence": 0.9,
                    "components": match.groups()
                })
        
        return entities
    
    def _extract_billing_entities(self, entities: Dict, text: str) -> Dict:
        """Extract billing specific entities"""
        # Financial information
        financial_patterns = [
            (r'\$([\d,]+(?:\.\d{2})?)', 'amount'),
            (r'Balance:\s*\$([\d,]+(?:\.\d{2})?)', 'balance'),
            (r'Due Date:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', 'due_date')
        ]
        
        for pattern, entity_type in financial_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities["custom_entities"].append({
                    "text": match.group(),
                    "type": entity_type,
                    "confidence": 0.9,
                    "components": match.groups()
                })
        
        return entities
    
    def _apply_learned_patterns(self, entities: Dict, text: str, document_type: str) -> Dict:
        """Apply patterns learned from previous documents"""
        # This would be enhanced with actual learning from processed documents
        # For now, we'll use some common patterns
        
        # Learn from document type
        if document_type in self.document_type_patterns:
            for entity_type, patterns in self.document_type_patterns[document_type].items():
                if entity_type in entities:
                    # Apply learned patterns
                    learned_entities = self._extract_with_learned_patterns(text, patterns)
                    entities[entity_type].extend(learned_entities)
        
        return entities
    
    def _extract_with_learned_patterns(self, text: str, patterns: List[str]) -> List[Dict]:
        """Extract entities using learned patterns"""
        entities = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append({
                    "text": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.8,
                    "pattern": pattern,
                    "learned": True
                })
        
        return entities
    
    def _extract_custom_entities(self, text: str, document_type: str) -> List[Dict]:
        """Extract custom entities based on document context"""
        custom_entities = []
        
        # Extract key-value pairs
        key_value_patterns = [
            (r'(\w+):\s*([^\n]+)', 'key_value'),
            (r'(\w+)\s*=\s*([^\n]+)', 'key_value'),
            (r'(\w+)\s*:\s*([^\n]+)', 'key_value')
        ]
        
        for pattern, entity_type in key_value_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                key, value = match.groups()
                if len(key.strip()) > 2 and len(value.strip()) > 1:
                    custom_entities.append({
                        "text": match.group(),
                        "type": entity_type,
                        "key": key.strip(),
                        "value": value.strip(),
                        "confidence": 0.7,
                        "start": match.start(),
                        "end": match.end()
                    })
        
        return custom_entities
    
    def _deduplicate_entities(self, entities: List[Dict]) -> List[Dict]:
        """Remove duplicate entities, keeping highest confidence"""
        seen = {}
        
        for entity in entities:
            text_key = entity["text"].lower().strip()
            
            if text_key not in seen or entity["confidence"] > seen[text_key]["confidence"]:
                seen[text_key] = entity
        
        return list(seen.values())
    
    def _add_confidence_scores(self, entities: Dict, text: str, document_type: str) -> Dict:
        """Add confidence scores to all entities"""
        entities_with_confidence = {}
        
        for entity_type, entity_list in entities.items():
            if isinstance(entity_list, list):
                entities_with_confidence[entity_type] = []
                
                for entity in entity_list:
                    if isinstance(entity, dict):
                        # Ensure confidence is present
                        if "confidence" not in entity:
                            entity["confidence"] = 0.7
                        
                        # Boost confidence for certain types
                        if entity_type == "names" and self._is_likely_name(entity["text"]):
                            entity["confidence"] = min(entity["confidence"] + 0.1, 1.0)
                        
                        if entity_type == "dates" and self._is_valid_date(entity["text"]):
                            entity["confidence"] = min(entity["confidence"] + 0.1, 1.0)
                        
                        entities_with_confidence[entity_type].append(entity)
                    else:
                        # Convert simple strings to dict format
                        entities_with_confidence[entity_type].append({
                            "text": str(entity),
                            "confidence": 0.7,
                            "type": entity_type
                        })
            else:
                entities_with_confidence[entity_type] = entity_list
        
        return entities_with_confidence
    
    def _is_likely_name(self, text: str) -> bool:
        """Check if text is likely a person's name"""
        # Simple heuristics for names
        words = text.split()
        if len(words) < 2 or len(words) > 4:
            return False
        
        # Check if words start with capital letters
        return all(word[0].isupper() for word in words if word)
    
    def _is_valid_date(self, text: str) -> bool:
        """Check if text is a valid date"""
        try:
            # Try to parse common date formats
            date_patterns = [
                r'\d{1,2}/\d{1,2}/\d{2,4}',
                r'\d{4}-\d{2}-\d{2}',
                r'\w+ \d{1,2},? \d{4}'
            ]
            
            for pattern in date_patterns:
                if re.match(pattern, text):
                    return True
            
            return False
        except:
            return False
    
    def _calculate_overall_confidence(self, entities: Dict) -> float:
        """Calculate overall confidence score for entity extraction"""
        if not entities:
            return 0.0
        
        total_confidence = 0.0
        total_entities = 0
        
        for entity_type, entity_list in entities.items():
            if isinstance(entity_list, list):
                for entity in entity_list:
                    if isinstance(entity, dict) and "confidence" in entity:
                        total_confidence += entity["confidence"]
                        total_entities += 1
        
        return total_confidence / total_entities if total_entities > 0 else 0.0
    
    def learn_from_documents(self, processed_documents: List[Dict]):
        """Learn patterns from processed documents"""
        print("🧠 Learning patterns from processed documents...")
        
        for doc in processed_documents:
            if not doc.get("extraction_results", {}).get("success"):
                continue
            
            doc_type = doc.get("classification_results", {}).get("document_type", "unknown")
            entities = doc.get("entity_extraction", {}).get("entities", {})
            text = doc.get("extraction_results", {}).get("extracted_text", "")
            
            # Learn entity patterns
            for entity_type, entity_list in entities.items():
                if isinstance(entity_list, list):
                    for entity in entity_list:
                        if isinstance(entity, dict) and "text" in entity:
                            self.learned_patterns[entity_type][doc_type].append(entity["text"])
            
            # Learn document type patterns
            if doc_type not in self.document_type_patterns:
                self.document_type_patterns[doc_type] = {}
            
            # Extract common patterns for this document type
            self._extract_document_patterns(text, doc_type)
        
        # Save learned patterns
        self._save_learned_patterns()
        print(f"✅ Learned patterns from {len(processed_documents)} documents")
    
    def _extract_document_patterns(self, text: str, document_type: str):
        """Extract common patterns from document text"""
        # Extract common phrases and patterns
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 100:
                # Look for structured patterns
                if ':' in line and len(line.split(':')) == 2:
                    key, value = line.split(':', 1)
                    if key.strip() and value.strip():
                        pattern = f"{key.strip()}:\\s*([^\\n]+)"
                        if pattern not in self.document_type_patterns[document_type].get("key_value", []):
                            if "key_value" not in self.document_type_patterns[document_type]:
                                self.document_type_patterns[document_type]["key_value"] = []
                            self.document_type_patterns[document_type]["key_value"].append(pattern)
    
    def _load_learned_patterns(self):
        """Load learned patterns from file"""
        try:
            if os.path.exists("learned_patterns.json"):
                with open("learned_patterns.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.learned_patterns = data.get("learned_patterns", self.learned_patterns)
                    self.document_type_patterns = data.get("document_type_patterns", self.document_type_patterns)
                print("✅ Loaded learned patterns from file")
        except Exception as e:
            print(f"⚠️ Could not load learned patterns: {e}")
    
    def _save_learned_patterns(self):
        """Save learned patterns to file"""
        try:
            data = {
                "learned_patterns": self.learned_patterns,
                "document_type_patterns": self.document_type_patterns,
                "last_updated": datetime.now().isoformat()
            }
            
            with open("learned_patterns.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print("✅ Saved learned patterns to file")
        except Exception as e:
            print(f"⚠️ Could not save learned patterns: {e}")
    
    def get_extraction_stats(self) -> Dict:
        """Get statistics about entity extraction"""
        stats = {
            "learned_patterns": {},
            "document_type_patterns": {},
            "total_learned_entities": 0
        }
        
        for entity_type, doc_types in self.learned_patterns.items():
            stats["learned_patterns"][entity_type] = {
                "total_patterns": sum(len(patterns) for patterns in doc_types.values()),
                "by_document_type": {doc_type: len(patterns) for doc_type, patterns in doc_types.items()}
            }
            stats["total_learned_entities"] += stats["learned_patterns"][entity_type]["total_patterns"]
        
        stats["document_type_patterns"] = {
            doc_type: {pattern_type: len(patterns) for pattern_type, patterns in patterns_dict.items()}
            for doc_type, patterns_dict in self.document_type_patterns.items()
        }
        
        return stats

def main():
    """Test the enhanced entity extractor"""
    extractor = EnhancedEntityExtractor()
    
    # Test with sample text
    sample_text = """
    LABORATORY REPORT
    LabCorp
    Report Date: 08/12/2025
    Patient: Michael Brown
    DOB: 1995-12-15
    MRN: 665680
    
    Test Results:
    Glucose: 94 mg/dL (Normal: 70-100)
    Cholesterol: 210 mg/dL (Normal: <200)
    Hemoglobin: 13.5 g/dL (Normal: 12-16)
    """
    
    result = extractor.extract_entities_enhanced(sample_text, "lab_result")
    print("Enhanced Entity Extraction Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
