"""
Compliance Service for HIPAA, GDPR, and Healthcare Compliance
Provides real compliance checking and audit capabilities
"""
import os
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import hashlib
import json
from enum import Enum

# NLP imports for PHI detection
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("⚠️ spaCy not available. Please install: pip install spacy")

# Healthcare-specific imports
try:
    import scispacy
    from scispacy.linking import EntityLinker
    SCISPACY_AVAILABLE = True
except ImportError:
    SCISPACY_AVAILABLE = False
    print("⚠️ scispaCy not available. Please install: pip install scispacy")

from core.config import settings

logger = logging.getLogger(__name__)

class ComplianceLevel(Enum):
    """Compliance level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceType(Enum):
    """Compliance type enumeration"""
    HIPAA = "hipaa"
    GDPR = "gdpr"
    PHI = "phi"
    PII = "pii"
    MEDICAL = "medical"
    REGULATORY = "regulatory"

class ComplianceService:
    """Compliance service for healthcare document processing"""
    
    def __init__(self):
        """Initialize compliance service"""
        self.nlp = None
        self.entity_linker = None
        self.compliance_rules = self._initialize_compliance_rules()
        self.phi_patterns = self._initialize_phi_patterns()
        self.audit_log = []
        
        # Initialize NLP models
        if SPACY_AVAILABLE:
            try:
                # Load medical model if available
                try:
                    self.nlp = spacy.load("en_core_sci_md")
                    logger.info("✅ Loaded medical spaCy model")
                except OSError:
                    # Fallback to standard model
                    self.nlp = spacy.load("en_core_web_sm")
                    logger.info("✅ Loaded standard spaCy model")
                
                # Initialize scispaCy if available
                if SCISPACY_AVAILABLE:
                    try:
                        self.entity_linker = EntityLinker(
                            resolve_abbreviations=True,
                            name="umls"
                        )
                        self.nlp.add_pipe("scispacy_linker", last=True)
                        logger.info("✅ Initialized scispaCy entity linker")
                    except Exception as e:
                        logger.warning(f"Could not initialize scispaCy: {e}")
                        self.entity_linker = None
                else:
                    self.entity_linker = None
                
            except Exception as e:
                logger.error(f"❌ Failed to load spaCy model: {e}")
                self.nlp = None
        
        logger.info("✅ Compliance Service initialized successfully")
    
    def _initialize_compliance_rules(self) -> Dict:
        """Initialize compliance rules and regulations"""
        return {
            "hipaa": {
                "name": "Health Insurance Portability and Accountability Act",
                "description": "US healthcare privacy and security regulations",
                "requirements": [
                    "PHI protection",
                    "Access controls",
                    "Audit trails",
                    "Data encryption",
                    "Breach notification"
                ],
                "penalties": {
                    "tier1": "Up to $50,000 per violation",
                    "tier2": "Up to $100,000 per violation",
                    "tier3": "Up to $250,000 per violation",
                    "tier4": "Up to $1.5 million per violation"
                }
            },
            "gdpr": {
                "name": "General Data Protection Regulation",
                "description": "EU data protection and privacy regulation",
                "requirements": [
                    "Data minimization",
                    "Purpose limitation",
                    "Consent management",
                    "Right to be forgotten",
                    "Data portability"
                ],
                "penalties": {
                    "tier1": "Up to €10 million or 2% of global revenue",
                    "tier2": "Up to €20 million or 4% of global revenue"
                }
            },
            "phi": {
                "name": "Protected Health Information",
                "description": "Individually identifiable health information",
                "identifiers": [
                    "names",
                    "addresses",
                    "dates",
                    "phone_numbers",
                    "ssn",
                    "medical_record_numbers",
                    "health_plan_beneficiary_numbers",
                    "account_numbers",
                    "certificate_license_numbers",
                    "vehicle_identifiers",
                    "device_identifiers",
                    "urls",
                    "ip_addresses",
                    "biometric_identifiers",
                    "full_face_photos",
                    "any_other_unique_identifying_characteristics"
                ]
            }
        }
    
    def _initialize_phi_patterns(self) -> Dict[str, List[str]]:
        """Initialize PHI detection patterns"""
        return {
            "names": [
                r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b",  # First Last
                r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b",  # First Middle Last
            ],
            "dates": [
                r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",  # MM/DD/YYYY
                r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",  # YYYY/MM/DD
                r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b",  # Month DD, YYYY
            ],
            "phone_numbers": [
                r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # 123-456-7890
                r"\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b",  # (123) 456-7890
                r"\b\+\d{1,3}\s*\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # +1 123-456-7890
            ],
            "ssn": [
                r"\b\d{3}[-]?\d{2}[-]?\d{4}\b",  # 123-45-6789
            ],
            "medical_record_numbers": [
                r"\bMRN[:\s]*\d+\b",
                r"\bMedical\s+Record\s+#?\s*\d+\b",
                r"\bMR\s+#?\s*\d+\b",
            ],
            "email_addresses": [
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            ],
            "addresses": [
                r"\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Way|Place|Pl)\b",
            ]
        }
    
    def check_document_compliance(self, document_data: Dict) -> Dict:
        """
        Check document for compliance with various regulations
        
        Args:
            document_data: Document data to check
            
        Returns:
            Dict containing compliance check results
        """
        try:
            content = document_data.get("extracted_text", "")
            if not content:
                return {
                    "success": False,
                    "error": "No content to analyze"
                }
            
            results = {
                "document_id": document_data.get("id"),
                "filename": document_data.get("filename"),
                "compliance_checks": {},
                "overall_risk_level": ComplianceLevel.LOW.value,
                "recommendations": [],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Check for PHI
            phi_results = self._check_phi_compliance(content)
            results["compliance_checks"]["phi"] = phi_results
            
            # Check for HIPAA compliance
            hipaa_results = self._check_hipaa_compliance(content, phi_results)
            results["compliance_checks"]["hipaa"] = hipaa_results
            
            # Check for GDPR compliance
            gdpr_results = self._check_gdpr_compliance(content, phi_results)
            results["compliance_checks"]["gdpr"] = gdpr_results
            
            # Determine overall risk level
            risk_level = self._calculate_overall_risk(results["compliance_checks"])
            results["overall_risk_level"] = risk_level.value
            
            # Generate recommendations
            results["recommendations"] = self._generate_compliance_recommendations(results["compliance_checks"])
            
            # Log compliance check
            self._log_compliance_check(results)
            
            return {
                "success": True,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error checking document compliance: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _check_phi_compliance(self, content: str) -> Dict:
        """Check for Protected Health Information"""
        try:
            phi_found = {}
            total_phi_count = 0
            
            # Check each PHI category
            for category, patterns in self.phi_patterns.items():
                category_matches = []
                
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Mask the actual value for security
                        masked_value = self._mask_phi_value(match.group(), category)
                        category_matches.append({
                            "pattern": pattern,
                            "masked_value": masked_value,
                            "position": match.span(),
                            "confidence": 0.9
                        })
                
                phi_found[category] = {
                    "count": len(category_matches),
                    "matches": category_matches,
                    "risk_level": self._assess_phi_risk(category, len(category_matches))
                }
                
                total_phi_count += len(category_matches)
            
            # Use NLP for additional PHI detection if available
            nlp_phi = {}
            if self.nlp:
                nlp_phi = self._detect_phi_with_nlp(content)
                total_phi_count += sum(len(matches) for matches in nlp_phi.values())
            
            return {
                "phi_detected": phi_found,
                "nlp_phi_detected": nlp_phi,
                "total_phi_count": total_phi_count,
                "risk_level": self._assess_overall_phi_risk(total_phi_count),
                "compliance_status": "compliant" if total_phi_count == 0 else "requires_review"
            }
            
        except Exception as e:
            logger.error(f"Error checking PHI compliance: {e}")
            return {
                "error": str(e),
                "phi_detected": {},
                "total_phi_count": 0,
                "risk_level": ComplianceLevel.CRITICAL.value,
                "compliance_status": "error"
            }
    
    def _detect_phi_with_nlp(self, content: str) -> Dict:
        """Use NLP to detect additional PHI entities"""
        try:
            doc = self.nlp(content)
            phi_entities = {}
            
            # Define medical entity types
            medical_entity_types = ["PERSON", "ORG", "DATE", "TIME", "CARDINAL", "GPE"]
            
            for ent in doc.ents:
                if ent.label_ in medical_entity_types:
                    entity_type = ent.label_.lower()
                    if entity_type not in phi_entities:
                        phi_entities[entity_type] = []
                    
                    # Mask the entity value
                    masked_value = self._mask_phi_value(ent.text, entity_type)
                    phi_entities[entity_type].append({
                        "text": masked_value,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "confidence": 0.8
                    })
            
            return phi_entities
            
        except Exception as e:
            logger.error(f"Error in NLP PHI detection: {e}")
            return {}
    
    def _check_hipaa_compliance(self, content: str, phi_results: Dict) -> Dict:
        """Check HIPAA compliance"""
        try:
            phi_count = phi_results.get("total_phi_count", 0)
            
            # HIPAA compliance checks
            compliance_checks = {
                "phi_protection": {
                    "status": "compliant" if phi_count == 0 else "non_compliant",
                    "description": "PHI must be protected and minimized",
                    "risk_level": "low" if phi_count == 0 else "high"
                },
                "data_minimization": {
                    "status": "compliant" if phi_count <= 5 else "requires_review",
                    "description": "Only necessary PHI should be included",
                    "risk_level": "low" if phi_count <= 5 else "medium"
                },
                "access_controls": {
                    "status": "requires_implementation",
                    "description": "Access controls must be implemented",
                    "risk_level": "medium"
                },
                "audit_trails": {
                    "status": "requires_implementation",
                    "description": "Audit trails must be maintained",
                    "risk_level": "medium"
                }
            }
            
            # Calculate HIPAA risk level
            risk_level = self._calculate_hipaa_risk(compliance_checks)
            
            return {
                "compliance_checks": compliance_checks,
                "overall_status": "compliant" if risk_level == ComplianceLevel.LOW else "requires_review",
                "risk_level": risk_level.value,
                "recommendations": self._generate_hipaa_recommendations(compliance_checks)
            }
            
        except Exception as e:
            logger.error(f"Error checking HIPAA compliance: {e}")
            return {
                "error": str(e),
                "overall_status": "error",
                "risk_level": ComplianceLevel.CRITICAL.value
            }
    
    def _check_gdpr_compliance(self, content: str, phi_results: Dict) -> Dict:
        """Check GDPR compliance"""
        try:
            phi_count = phi_results.get("total_phi_count", 0)
            
            # GDPR compliance checks
            compliance_checks = {
                "data_minimization": {
                    "status": "compliant" if phi_count <= 3 else "requires_review",
                    "description": "Personal data should be minimized",
                    "risk_level": "low" if phi_count <= 3 else "medium"
                },
                "purpose_limitation": {
                    "status": "requires_review",
                    "description": "Purpose of data processing must be clear",
                    "risk_level": "medium"
                },
                "consent_management": {
                    "status": "requires_implementation",
                    "description": "Consent must be properly managed",
                    "risk_level": "high"
                },
                "data_subject_rights": {
                    "status": "requires_implementation",
                    "description": "Data subject rights must be supported",
                    "risk_level": "high"
                }
            }
            
            # Calculate GDPR risk level
            risk_level = self._calculate_gdpr_risk(compliance_checks)
            
            return {
                "compliance_checks": compliance_checks,
                "overall_status": "compliant" if risk_level == ComplianceLevel.LOW else "requires_review",
                "risk_level": risk_level.value,
                "recommendations": self._generate_gdpr_recommendations(compliance_checks)
            }
            
        except Exception as e:
            logger.error(f"Error checking GDPR compliance: {e}")
            return {
                "error": str(e),
                "overall_status": "error",
                "risk_level": ComplianceLevel.CRITICAL.value
            }
    
    def _mask_phi_value(self, value: str, category: str) -> str:
        """Mask PHI values for security"""
        try:
            if category == "ssn":
                return "XXX-XX-" + value[-4:] if len(value) >= 4 else "XXX-XX-XXXX"
            elif category == "phone_numbers":
                return "XXX-XXX-" + value[-4:] if len(value) >= 4 else "XXX-XXX-XXXX"
            elif category == "email_addresses":
                parts = value.split("@")
                if len(parts) == 2:
                    username = parts[0]
                    domain = parts[1]
                    masked_username = username[0] + "*" * (len(username) - 2) + username[-1] if len(username) > 2 else username
                    return f"{masked_username}@{domain}"
                return value
            elif category == "dates":
                return "MM/DD/YYYY"
            else:
                # Generic masking for other categories
                if len(value) <= 2:
                    return value
                return value[0] + "*" * (len(value) - 2) + value[-1]
                
        except Exception as e:
            logger.warning(f"Error masking PHI value: {e}")
            return "***MASKED***"
    
    def _assess_phi_risk(self, category: str, count: int) -> str:
        """Assess risk level for PHI category"""
        if count == 0:
            return "low"
        elif count <= 3:
            return "medium"
        elif count <= 10:
            return "high"
        else:
            return "critical"
    
    def _assess_overall_phi_risk(self, total_count: int) -> ComplianceLevel:
        """Assess overall PHI risk level"""
        if total_count == 0:
            return ComplianceLevel.LOW
        elif total_count <= 5:
            return ComplianceLevel.MEDIUM
        elif total_count <= 15:
            return ComplianceLevel.HIGH
        else:
            return ComplianceLevel.CRITICAL
    
    def _calculate_hipaa_risk(self, compliance_checks: Dict) -> ComplianceLevel:
        """Calculate HIPAA compliance risk level"""
        high_risk_count = sum(1 for check in compliance_checks.values() 
                             if check.get("risk_level") == "high")
        medium_risk_count = sum(1 for check in compliance_checks.values() 
                               if check.get("risk_level") == "medium")
        
        if high_risk_count > 0:
            return ComplianceLevel.HIGH
        elif medium_risk_count > 0:
            return ComplianceLevel.MEDIUM
        else:
            return ComplianceLevel.LOW
    
    def _calculate_gdpr_risk(self, compliance_checks: Dict) -> ComplianceLevel:
        """Calculate GDPR compliance risk level"""
        high_risk_count = sum(1 for check in compliance_checks.values() 
                             if check.get("risk_level") == "high")
        medium_risk_count = sum(1 for check in compliance_checks.values() 
                               if check.get("risk_level") == "medium")
        
        if high_risk_count > 0:
            return ComplianceLevel.HIGH
        elif medium_risk_count > 0:
            return ComplianceLevel.MEDIUM
        else:
            return ComplianceLevel.LOW
    
    def _calculate_overall_risk(self, compliance_checks: Dict) -> ComplianceLevel:
        """Calculate overall compliance risk level"""
        risk_levels = []
        
        for check_type, check_data in compliance_checks.items():
            if "risk_level" in check_data:
                risk_levels.append(check_data["risk_level"])
        
        if not risk_levels:
            return ComplianceLevel.LOW
        
        # Determine highest risk level
        if any(level == ComplianceLevel.CRITICAL.value for level in risk_levels):
            return ComplianceLevel.CRITICAL
        elif any(level == ComplianceLevel.HIGH.value for level in risk_levels):
            return ComplianceLevel.HIGH
        elif any(level == ComplianceLevel.MEDIUM.value for level in risk_levels):
            return ComplianceLevel.MEDIUM
        else:
            return ComplianceLevel.LOW
    
    def _generate_compliance_recommendations(self, compliance_checks: Dict) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        for check_type, check_data in compliance_checks.items():
            if check_type == "phi" and check_data.get("total_phi_count", 0) > 0:
                recommendations.append("Review and minimize PHI content in documents")
                recommendations.append("Implement PHI detection and redaction tools")
            
            if check_type == "hipaa":
                hipaa_data = check_data
                if hipaa_data.get("overall_status") != "compliant":
                    recommendations.append("Implement HIPAA-compliant data handling procedures")
                    recommendations.append("Establish access controls and audit trails")
                    recommendations.append("Train staff on HIPAA compliance requirements")
            
            if check_type == "gdpr":
                gdpr_data = check_data
                if gdpr_data.get("overall_status") != "compliant":
                    recommendations.append("Implement GDPR-compliant data processing")
                    recommendations.append("Establish consent management systems")
                    recommendations.append("Support data subject rights")
        
        if not recommendations:
            recommendations.append("Document appears compliant with current regulations")
        
        return recommendations
    
    def _generate_hipaa_recommendations(self, compliance_checks: Dict) -> List[str]:
        """Generate HIPAA-specific recommendations"""
        recommendations = []
        
        for check_name, check_data in compliance_checks.items():
            if check_data.get("status") != "compliant":
                if check_name == "phi_protection":
                    recommendations.append("Implement PHI detection and redaction")
                elif check_name == "access_controls":
                    recommendations.append("Implement role-based access controls")
                elif check_name == "audit_trails":
                    recommendations.append("Establish comprehensive audit logging")
        
        return recommendations
    
    def _generate_gdpr_recommendations(self, compliance_checks: Dict) -> List[str]:
        """Generate GDPR-specific recommendations"""
        recommendations = []
        
        for check_name, check_data in compliance_checks.items():
            if check_data.get("status") != "compliant":
                if check_name == "consent_management":
                    recommendations.append("Implement consent management system")
                elif check_name == "data_subject_rights":
                    recommendations.append("Support data subject rights (access, deletion, portability)")
                elif check_name == "purpose_limitation":
                    recommendations.append("Clearly define and document data processing purposes")
        
        return recommendations
    
    def _log_compliance_check(self, results: Dict):
        """Log compliance check for audit purposes"""
        try:
            audit_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "document_id": results.get("document_id"),
                "filename": results.get("filename"),
                "risk_level": results.get("overall_risk_level"),
                "compliance_checks": results.get("compliance_checks", {}),
                "recommendations_count": len(results.get("recommendations", []))
            }
            
            self.audit_log.append(audit_entry)
            
            # Keep only last 1000 entries
            if len(self.audit_log) > 1000:
                self.audit_log = self.audit_log[-1000:]
                
        except Exception as e:
            logger.warning(f"Could not log compliance check: {e}")
    
    def get_compliance_analytics(self) -> Dict:
        """Get compliance analytics and statistics"""
        try:
            if not self.audit_log:
                return {
                    "success": True,
                    "analytics": {
                        "total_checks": 0,
                        "risk_distribution": {},
                        "compliance_trends": [],
                        "top_recommendations": []
                    }
                }
            
            # Calculate statistics
            total_checks = len(self.audit_log)
            risk_distribution = {}
            
            for entry in self.audit_log:
                risk_level = entry.get("risk_level", "unknown")
                risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
            
            # Get recent trends (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_checks = [
                entry for entry in self.audit_log
                if datetime.fromisoformat(entry["timestamp"]) > thirty_days_ago
            ]
            
            # Top recommendations
            all_recommendations = []
            for entry in self.audit_log:
                if "recommendations_count" in entry:
                    all_recommendations.append(entry["recommendations_count"])
            
            avg_recommendations = sum(all_recommendations) / len(all_recommendations) if all_recommendations else 0
            
            return {
                "success": True,
                "analytics": {
                    "total_checks": total_checks,
                    "risk_distribution": risk_distribution,
                    "recent_checks_30_days": len(recent_checks),
                    "average_recommendations": round(avg_recommendations, 2),
                    "compliance_rate": self._calculate_compliance_rate(risk_distribution)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance analytics: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_compliance_rate(self, risk_distribution: Dict) -> float:
        """Calculate overall compliance rate"""
        try:
            total = sum(risk_distribution.values())
            if total == 0:
                return 0.0
            
            compliant_count = risk_distribution.get("low", 0)
            return round((compliant_count / total) * 100, 2)
            
        except Exception as e:
            logger.warning(f"Error calculating compliance rate: {e}")
            return 0.0
    
    def get_service_status(self) -> Dict:
        """Get compliance service status"""
        return {
            "service_name": "ComplianceService",
            "status": "active",
            "nlp_available": SPACY_AVAILABLE,
            "scispacy_available": SCISPACY_AVAILABLE,
            "compliance_types": [comp_type.value for comp_type in ComplianceType],
            "capabilities": {
                "phi_detection": True,
                "hipaa_compliance": True,
                "gdpr_compliance": True,
                "risk_assessment": True,
                "audit_logging": True,
                "recommendations": True
            },
            "total_audit_entries": len(self.audit_log)
        }
