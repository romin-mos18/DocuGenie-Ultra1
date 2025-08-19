#!/usr/bin/env python3
"""
Test script to upload a document and verify detail view data
"""

import os
import sys
import json
import requests
import time
from pathlib import Path

# Test with a sample document from Testing Documents
def test_upload_and_detail_view():
    print("🚀 Testing Document Upload and Detail View Data Flow")
    print("=" * 60)
    
    # Find a test document
    testing_docs_path = Path("../Testing Documents/Testing Documents")
    
    # Try different paths
    alternative_paths = [
        Path("Testing Documents/Testing Documents"),
        Path("Testing Documents"),
        Path("../Testing Documents"),
    ]
    
    found_path = None
    for path in [testing_docs_path] + alternative_paths:
        if path.exists():
            found_path = path
            break
    
    if not found_path:
        print("❌ Could not find Testing Documents folder!")
        return
    
    # Find a few test files of different types
    test_files = []
    
    # CSV file
    csv_files = list(found_path.glob("csv/financial_report_*.csv"))
    if csv_files:
        test_files.append(("CSV Financial Report", csv_files[0]))
    
    # JSON file
    json_files = list(found_path.glob("json/appointment_*.json"))
    if json_files:
        test_files.append(("JSON Appointment", json_files[0]))
    
    # XML file
    xml_files = list(found_path.glob("xml/certificate_*.xml"))
    if xml_files:
        test_files.append(("XML Certificate", xml_files[0]))
    
    # TXT file
    txt_files = list(found_path.glob("txt/hospital_report_*.txt"))
    if txt_files:
        test_files.append(("TXT Hospital Report", txt_files[0]))
    
    if not test_files:
        print("❌ No test files found!")
        return
    
    backend_url = "http://localhost:8007"
    
    print(f"📁 Found {len(test_files)} test files to upload")
    print(f"🔗 Backend URL: {backend_url}")
    print()
    
    for file_type, file_path in test_files:
        print(f"\n📄 Testing {file_type}: {file_path.name}")
        print("-" * 40)
        
        try:
            # Test upload
            print("1. 📤 Uploading document...")
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'application/octet-stream')}
                upload_response = requests.post(f"{backend_url}/api/v1/upload", files=files, timeout=60)
            
            if upload_response.status_code == 200:
                upload_data = upload_response.json()
                document_id = upload_data.get("document_id")
                print(f"   ✅ Upload successful! Document ID: {document_id}")
                print(f"   📋 Document Type: {upload_data.get('document_type', 'unknown')}")
                print(f"   🎯 Confidence: {upload_data.get('confidence', 0):.1%}")
                
                # Test detail view data retrieval
                print("\n2. 🔍 Fetching detail view data...")
                detail_response = requests.get(f"{backend_url}/api/v1/documents/{document_id}", timeout=30)
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    print("   ✅ Detail data retrieved successfully!")
                    
                    # Analyze the AI analysis data
                    ai_analysis = detail_data.get("ai_analysis", {})
                    document_info = detail_data.get("document", {})
                    
                    print("\n📊 AI Analysis Data Available:")
                    print(f"   • Classification: {ai_analysis.get('classification', {}).get('document_type', 'N/A')}")
                    print(f"   • Confidence: {ai_analysis.get('classification', {}).get('confidence', 0):.1%}")
                    print(f"   • Word Count: {ai_analysis.get('word_count', 0):,}")
                    print(f"   • Entity Count: {ai_analysis.get('entity_count', 0)}")
                    print(f"   • Language: {ai_analysis.get('language', {}).get('primary_language', 'N/A')}")
                    print(f"   • Has Structured Data: {ai_analysis.get('has_structured_data', False)}")
                    
                    # Show entity types found
                    entities = ai_analysis.get('extracted_entities_list', {})
                    if entities:
                        print("   • Entity Types Found:")
                        for entity_type, entity_list in entities.items():
                            if entity_list:
                                print(f"     - {entity_type.replace('_', ' ').title()}: {len(entity_list)} items")
                    
                    # Show structured data info if available
                    structured_data = ai_analysis.get('structured_data', {})
                    if structured_data and structured_data.get('success'):
                        print("   • Structured Data:")
                        data_type = structured_data.get('data_type', 'unknown')
                        print(f"     - Type: {data_type}")
                        
                        struct_data_content = structured_data.get('structured_data', {})
                        if 'headers' in struct_data_content:
                            print(f"     - Columns: {len(struct_data_content['headers'])}")
                            print(f"     - Rows: {struct_data_content.get('total_rows', 0)}")
                        elif 'key_info' in struct_data_content:
                            key_info = struct_data_content['key_info']
                            print(f"     - Key Information: {len(key_info)} fields")
                    
                    # Show test results if available (for medical documents)
                    test_results = ai_analysis.get('test_results', [])
                    if test_results:
                        print(f"   • Test Results: {len(test_results)} entries")
                    
                    print(f"\n✅ {file_type} processing and detail view: SUCCESS")
                    
                    # Clean up - delete the test document
                    print("3. 🗑️ Cleaning up...")
                    delete_response = requests.delete(f"{backend_url}/documents/{document_id}")
                    if delete_response.status_code == 200:
                        print("   ✅ Test document deleted")
                    
                else:
                    print(f"   ❌ Failed to fetch detail data: {detail_response.status_code}")
                    print(f"   Response: {detail_response.text[:200]}")
            
            else:
                print(f"   ❌ Upload failed: {upload_response.status_code}")
                print(f"   Response: {upload_response.text[:200]}")
        
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection Error: Backend server not running")
            print("   💡 Please start the backend with: python main.py")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Upload and Detail View Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_upload_and_detail_view()
