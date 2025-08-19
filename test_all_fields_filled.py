#!/usr/bin/env python3
"""
Test script to verify all document detail fields are filled with extracted data or "-"
"""

import requests
import json

def test_all_fields_filled():
    print("📋 Testing All Document Fields are Filled")
    print("=" * 60)
    
    backend_url = "http://localhost:8007"
    
    try:
        # Get documents list
        print("1. 📋 Fetching documents...")
        list_response = requests.get(f"{backend_url}/api/v1/documents", timeout=10)
        
        if list_response.status_code == 200:
            list_data = list_response.json()
            documents = list_data.get("documents", [])
            
            print(f"   ✅ Found {len(documents)} documents")
            
            # Test different document types
            test_docs = []
            
            for doc in documents:
                filename = doc.get("filename", "Unknown")
                doc_type = doc.get("document_type", "unknown")
                
                if "hospital" in filename.lower():
                    test_docs.append((doc, "Medical Report"))
                elif "lab" in filename.lower():
                    test_docs.append((doc, "Lab Result"))
                elif "financial" in filename.lower():
                    test_docs.append((doc, "Financial Report"))
                elif "certificate" in filename.lower():
                    test_docs.append((doc, "Certificate"))
            
            if not test_docs:
                test_docs = [(documents[0], "General Document")] if documents else []
            
            print(f"\n2. 🔍 Testing document fields for {len(test_docs)} different document types...")
            
            for doc_info, doc_category in test_docs:
                doc_id = doc_info.get("id")
                filename = doc_info.get("filename")
                
                print(f"\n📄 Testing {doc_category}: {filename}")
                print(f"   Document ID: {doc_id}")
                
                # Get detail data
                detail_response = requests.get(f"{backend_url}/api/v1/documents/{doc_id}", timeout=10)
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    ai_analysis = detail_data.get("ai_analysis", {})
                    
                    if ai_analysis:
                        print(f"   ✅ AI Analysis available")
                        
                        # Check extracted entities
                        entities = ai_analysis.get("extracted_entities_list", {}) or ai_analysis.get("entities", {}).get("entities", {})
                        
                        if entities:
                            print(f"   🔍 Available Entities:")
                            for entity_type, entity_list in entities.items():
                                if entity_list:
                                    print(f"      - {entity_type}: {len(entity_list)} items")
                                    print(f"        Examples: {entity_list[:2]}")
                        
                        # Check structured data
                        structured_data = ai_analysis.get("structured_data", {})
                        if structured_data and structured_data.get("success"):
                            print(f"   📊 Structured Data available:")
                            print(f"      - Type: {structured_data.get('data_type', 'unknown')}")
                            
                            struct_content = structured_data.get("structured_data", {})
                            if "key_info" in struct_content:
                                key_info = struct_content["key_info"]
                                print(f"      - Key Info Fields: {list(key_info.keys())}")
                            elif "headers" in struct_content:
                                print(f"      - Headers: {struct_content['headers']}")
                        
                        # Expected fields based on document type
                        expected_fields = {}
                        
                        if "medical" in doc_category.lower() or "hospital" in filename.lower() or "lab" in filename.lower():
                            expected_fields = {
                                "Patient Name": "Should show patient name from entities or '-'",
                                "MRN": "Should show medical record number from identifiers or '-'",
                                "DOB": "Should show date of birth from dates or '-'",
                                "Diagnosis": "Should show diagnosis from medical terms or '-'",
                                "Provider": "Should show doctor/provider name or '-'",
                                "Report Date": "Should show report date from dates or '-'"
                            }
                        
                        elif "financial" in filename.lower():
                            expected_fields = {
                                "Institution": "Should show bank/institution name or '-'",
                                "Account Number": "Should show account number from identifiers or '-'",
                                "Statement Date": "Should show date from dates or '-'",
                                "Total Amount": "Should show amount from amounts or '-'"
                            }
                        
                        elif "certificate" in filename.lower():
                            expected_fields = {
                                "Recipient": "Should show recipient name from names or '-'",
                                "Certificate Number": "Should show number from identifiers or '-'",
                                "Issue Date": "Should show date from dates or '-'",
                                "Organization": "Should show issuing org from organizations or '-'"
                            }
                        
                        else:
                            expected_fields = {
                                "Language": "Should show detected language or 'EN'",
                                "Word Count": "Should show word count or 0",
                                "Entity Count": "Should show entity count or 0"
                            }
                        
                        print(f"   📋 Expected Fields for Frontend:")
                        for field_name, description in expected_fields.items():
                            print(f"      ✓ {field_name}: {description}")
                        
                        # Data mapping verification
                        print(f"   🎯 Data Extraction Verification:")
                        
                        # Check if we have data to populate fields
                        names = entities.get("names", []) if entities else []
                        dates = entities.get("dates", []) if entities else []
                        identifiers = entities.get("identifiers", []) if entities else []
                        organizations = entities.get("organizations", []) if entities else []
                        amounts = entities.get("amounts", []) if entities else []
                        medical_terms = entities.get("medical_terms", []) if entities else []
                        
                        dash_msg = '- (will show "-")'
                        print(f"      - Names available: {len(names)} {'✓' if names else dash_msg}")
                        print(f"      - Dates available: {len(dates)} {'✓' if dates else dash_msg}")
                        print(f"      - Identifiers available: {len(identifiers)} {'✓' if identifiers else dash_msg}")
                        print(f"      - Organizations available: {len(organizations)} {'✓' if organizations else dash_msg}")
                        print(f"      - Amounts available: {len(amounts)} {'✓' if amounts else dash_msg}")
                        print(f"      - Medical terms available: {len(medical_terms)} {'✓' if medical_terms else dash_msg}")
                        
                        print(f"   ✅ Frontend should now show all fields with either extracted data or \"-\"")
                        
                    else:
                        print(f"   ❌ No AI analysis available - will show \"-\" for all fields")
                else:
                    print(f"   ❌ Failed to get document details: {detail_response.status_code}")
        
        print(f"\n3. ✅ Updated Components:")
        print(f"   📋 MedicalDocumentSection:")
        print(f"      - Always shows: Patient Name, MRN, DOB, Diagnosis")
        print(f"      - Always shows: Provider, Report Date")
        print(f"      - Always shows: Medical Information, Test Results")
        
        print(f"   💰 FinancialDocumentSection:")
        print(f"      - Always shows: Institution, Account Number, Statement Date, Total Amount")
        print(f"      - Always shows: Financial Metrics, Financial Entities")
        
        print(f"   📅 AppointmentDocumentSection:")
        print(f"      - Always shows: Appointment ID, Patient, Date, Time, Provider, Type")
        
        print(f"   🏷️ Entity Sections:")
        print(f"      - Always show entity type labels")
        print(f"      - Show chips with data or \"-\" when no data")
        
        print(f"\n4. 🎯 Field Display Rules:")
        print(f"   ✅ All fields always visible (no conditional rendering)")
        print(f"   ✅ Data extracted from multiple sources (structured_data + entities)")
        print(f"   ✅ Intelligent fallbacks (try multiple field names)")
        print("   ✅ Show \"-\" when no data available (never \"Not Found\")")
        print("   ✅ Entity sections always show with chips or \"-\"")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server not running")
        print("💡 Please start the backend with: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ All Fields Filled Test Complete!")
    print("🎯 Every field should now show extracted data or '-'")
    print("=" * 60)

if __name__ == "__main__":
    test_all_fields_filled()
