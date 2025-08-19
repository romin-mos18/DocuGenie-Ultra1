"""
Structured Data Extraction Service
Handles extraction and processing of structured data from CSV, JSON, XML files
"""
import json
import csv
import xml.etree.ElementTree as ET
import logging
from typing import Dict, List, Any, Optional
import io

logger = logging.getLogger(__name__)

class StructuredDataService:
    """Service for extracting structured data from various file formats"""
    
    def __init__(self):
        """Initialize the structured data service"""
        self.supported_formats = ['csv', 'json', 'xml', 'xlsx', 'xls']
    
    def extract_structured_data(self, file_path: str, file_type: str, content: bytes = None) -> Dict:
        """
        Extract structured data from a file
        
        Args:
            file_path: Path to the file
            file_type: Type of file (csv, json, xml, xlsx, etc.)
            content: Raw file content if available
            
        Returns:
            Dict containing extracted structured data
        """
        try:
            if file_type.lower() == 'csv':
                return self._extract_csv_data(file_path, content)
            elif file_type.lower() == 'json':
                return self._extract_json_data(file_path, content)
            elif file_type.lower() == 'xml':
                return self._extract_xml_data(file_path, content)
            elif file_type.lower() in ['xlsx', 'xls']:
                return self._extract_excel_data(file_path, content)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported file type: {file_type}",
                    "structured_data": {},
                    "data_type": "unsupported"
                }
                
        except Exception as e:
            logger.error(f"❌ Structured data extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "structured_data": {},
                "data_type": "error"
            }
    
    def _extract_csv_data(self, file_path: str, content: bytes = None) -> Dict:
        """Extract data from CSV file"""
        try:
            data_rows = []
            headers = []
            
            if content:
                # Read from content bytes
                text_content = content.decode('utf-8')
                csv_reader = csv.reader(io.StringIO(text_content))
            else:
                # Read from file
                with open(file_path, 'r', encoding='utf-8') as file:
                    csv_reader = csv.reader(file)
            
            for i, row in enumerate(csv_reader):
                if i == 0:
                    headers = row
                else:
                    if len(row) == len(headers):
                        row_dict = {headers[j]: row[j] for j in range(len(headers))}
                        data_rows.append(row_dict)
            
            # Analyze data to determine if it's financial, medical, or other
            data_type = self._analyze_csv_data_type(headers, data_rows)
            
            # Extract key metrics
            metrics = self._extract_csv_metrics(headers, data_rows, data_type)
            
            return {
                "success": True,
                "structured_data": {
                    "headers": headers,
                    "rows": data_rows[:100],  # Limit to first 100 rows
                    "total_rows": len(data_rows),
                    "metrics": metrics
                },
                "data_type": data_type,
                "row_count": len(data_rows),
                "column_count": len(headers)
            }
            
        except Exception as e:
            logger.error(f"❌ CSV extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "structured_data": {},
                "data_type": "csv_error"
            }
    
    def _extract_json_data(self, file_path: str, content: bytes = None) -> Dict:
        """Extract data from JSON file"""
        try:
            if content:
                # Read from content bytes
                json_data = json.loads(content.decode('utf-8'))
            else:
                # Read from file
                with open(file_path, 'r', encoding='utf-8') as file:
                    json_data = json.load(file)
            
            # Analyze JSON structure
            data_type = self._analyze_json_data_type(json_data)
            
            # Extract key information based on data type
            key_info = self._extract_json_key_info(json_data, data_type)
            
            return {
                "success": True,
                "structured_data": {
                    "data": json_data,
                    "key_info": key_info,
                    "structure": self._analyze_json_structure(json_data)
                },
                "data_type": data_type,
                "size": len(str(json_data))
            }
            
        except Exception as e:
            logger.error(f"❌ JSON extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "structured_data": {},
                "data_type": "json_error"
            }
    
    def _extract_xml_data(self, file_path: str, content: bytes = None) -> Dict:
        """Extract data from XML file"""
        try:
            if content:
                # Parse from content bytes
                root = ET.fromstring(content.decode('utf-8'))
            else:
                # Parse from file
                tree = ET.parse(file_path)
                root = tree.getroot()
            
            # Convert XML to dictionary
            xml_dict = self._xml_to_dict(root)
            
            # Analyze XML data type
            data_type = self._analyze_xml_data_type(root, xml_dict)
            
            # Extract key information
            key_info = self._extract_xml_key_info(root, xml_dict, data_type)
            
            return {
                "success": True,
                "structured_data": {
                    "data": xml_dict,
                    "key_info": key_info,
                    "root_tag": root.tag,
                    "structure": self._analyze_xml_structure(root)
                },
                "data_type": data_type,
                "element_count": len(list(root.iter()))
            }
            
        except Exception as e:
            logger.error(f"❌ XML extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "structured_data": {},
                "data_type": "xml_error"
            }
    
    def _extract_excel_data(self, file_path: str, content: bytes = None) -> Dict:
        """Extract data from Excel file (requires openpyxl or xlrd)"""
        try:
            # Try to import excel libraries
            try:
                import openpyxl
                excel_available = True
            except ImportError:
                try:
                    import xlrd
                    excel_available = True
                except ImportError:
                    excel_available = False
            
            if not excel_available:
                return {
                    "success": False,
                    "error": "Excel libraries not available (openpyxl or xlrd required)",
                    "structured_data": {},
                    "data_type": "excel_unavailable"
                }
            
            # For now, return basic info - full implementation would require excel libraries
            return {
                "success": True,
                "structured_data": {
                    "note": "Excel file detected - specialized extraction would require additional libraries",
                    "filename": file_path
                },
                "data_type": "excel_file",
                "requires_libraries": ["openpyxl", "xlrd"]
            }
            
        except Exception as e:
            logger.error(f"❌ Excel extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "structured_data": {},
                "data_type": "excel_error"
            }
    
    def _analyze_csv_data_type(self, headers: List[str], rows: List[Dict]) -> str:
        """Analyze CSV headers and data to determine document type"""
        header_text = ' '.join(headers).lower()
        
        # Financial indicators
        financial_keywords = ['revenue', 'expenses', 'profit', 'income', 'balance', 'amount', 'cost', 'price']
        if any(keyword in header_text for keyword in financial_keywords):
            return 'financial_report'
        
        # Medical/lab indicators
        medical_keywords = ['patient', 'test', 'result', 'lab', 'hemoglobin', 'glucose', 'cholesterol']
        if any(keyword in header_text for keyword in medical_keywords):
            return 'lab_result'
        
        # Bank statement indicators
        bank_keywords = ['transaction', 'deposit', 'withdrawal', 'account', 'bank']
        if any(keyword in header_text for keyword in bank_keywords):
            return 'bank_statement'
        
        return 'data_table'
    
    def _extract_csv_metrics(self, headers: List[str], rows: List[Dict], data_type: str) -> Dict:
        """Extract key metrics from CSV data"""
        metrics = {}
        
        if data_type == 'financial_report':
            # Extract financial metrics
            for header in headers:
                if 'profit' in header.lower() or 'revenue' in header.lower():
                    try:
                        values = [float(row.get(header, 0)) for row in rows if row.get(header)]
                        if values:
                            metrics[f"{header}_total"] = sum(values)
                            metrics[f"{header}_avg"] = sum(values) / len(values)
                    except:
                        pass
        
        return metrics
    
    def _analyze_json_data_type(self, json_data: Any) -> str:
        """Analyze JSON data to determine document type"""
        json_str = str(json_data).lower()
        
        # Appointment indicators
        if 'appointment' in json_str or 'appointment_id' in json_str:
            return 'appointment'
        
        # Patient record indicators
        if 'patient' in json_str or 'medical_record' in json_str:
            return 'patient_record'
        
        # Insurance claim indicators
        if 'insurance' in json_str or 'claim' in json_str:
            return 'insurance_claim'
        
        # Prescription indicators
        if 'prescription' in json_str or 'medication' in json_str:
            return 'prescription'
        
        return 'json_data'
    
    def _extract_json_key_info(self, json_data: Any, data_type: str) -> Dict:
        """Extract key information from JSON based on data type"""
        key_info = {}
        
        if isinstance(json_data, dict):
            if data_type == 'appointment':
                key_info['appointment_id'] = json_data.get('appointment_id')
                key_info['patient_name'] = json_data.get('patient_name')
                key_info['appointment_date'] = json_data.get('appointment_date')
                key_info['provider'] = json_data.get('provider')
            
            elif data_type == 'patient_record':
                key_info['patient_name'] = json_data.get('patient_name')
                key_info['patient_id'] = json_data.get('patient_id')
                key_info['medical_record_number'] = json_data.get('mrn')
            
            # Add more type-specific extractions as needed
        
        return key_info
    
    def _analyze_xml_data_type(self, root: ET.Element, xml_dict: Dict) -> str:
        """Analyze XML structure to determine document type"""
        root_tag = root.tag.lower()
        
        if 'certificate' in root_tag:
            return 'certificate'
        elif 'contract' in root_tag:
            return 'contract'
        elif 'invoice' in root_tag:
            return 'billing'
        elif 'policy' in root_tag:
            return 'legal_document'
        
        return 'xml_document'
    
    def _extract_xml_key_info(self, root: ET.Element, xml_dict: Dict, data_type: str) -> Dict:
        """Extract key information from XML based on data type"""
        key_info = {}
        
        if data_type == 'certificate':
            # Extract certificate-specific information
            for child in root.iter():
                if 'name' in child.tag.lower():
                    key_info['recipient_name'] = child.text
                elif 'number' in child.tag.lower():
                    key_info['certificate_number'] = child.text
                elif 'date' in child.tag.lower():
                    key_info['issue_date'] = child.text
        
        return key_info
    
    def _xml_to_dict(self, element: ET.Element) -> Dict:
        """Convert XML element to dictionary"""
        result = {}
        
        # Add attributes
        if element.attrib:
            result['@attributes'] = element.attrib
        
        # Add text content
        if element.text and element.text.strip():
            if len(element) == 0:
                return element.text.strip()
            result['text'] = element.text.strip()
        
        # Add child elements
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result
    
    def _analyze_json_structure(self, json_data: Any) -> Dict:
        """Analyze JSON structure"""
        if isinstance(json_data, dict):
            return {
                "type": "object",
                "keys": list(json_data.keys()),
                "key_count": len(json_data.keys())
            }
        elif isinstance(json_data, list):
            return {
                "type": "array",
                "length": len(json_data),
                "item_type": type(json_data[0]).__name__ if json_data else "empty"
            }
        else:
            return {
                "type": type(json_data).__name__,
                "value": str(json_data)[:100]
            }
    
    def _analyze_xml_structure(self, root: ET.Element) -> Dict:
        """Analyze XML structure"""
        return {
            "root_tag": root.tag,
            "child_count": len(list(root)),
            "total_elements": len(list(root.iter())),
            "child_tags": [child.tag for child in root]
        }
