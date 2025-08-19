#!/usr/bin/env python3
"""
Debug script to check API response structure for detail view
"""

import requests
import json

def check_api_response():
    print("🔍 Debugging API Response Structure")
    print("=" * 50)
    
    backend_url = "http://localhost:8007"
    
    try:
        # Check documents list first
        print("1. 📋 Fetching documents list...")
        list_response = requests.get(f"{backend_url}/api/v1/documents", timeout=10)
        
        if list_response.status_code == 200:
            list_data = list_response.json()
            documents = list_data.get("documents", [])
            print(f"   ✅ Found {len(documents)} documents")
            
            if documents:
                # Check detail for the first few documents
                for i, doc in enumerate(documents[:3]):
                    doc_id = doc.get("id")
                    filename = doc.get("filename", "unknown")
                    print(f"\n2.{i+1} 📄 Checking detail for document {doc_id}: {filename}")
                    
                    detail_response = requests.get(f"{backend_url}/api/v1/documents/{doc_id}", timeout=10)
                    
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        print(f"   ✅ Detail response received")
                        
                        # Check AI analysis structure
                        ai_analysis = detail_data.get("ai_analysis", {})
                        document_info = detail_data.get("document", {})
                        
                        print(f"   📊 AI Analysis Keys: {list(ai_analysis.keys())}")
                        
                        # Check classification
                        classification = ai_analysis.get("classification", {})
                        if classification:
                            print(f"   🏷️  Classification:")
                            print(f"      - Type: {classification.get('document_type', 'N/A')}")
                            print(f"      - Confidence: {classification.get('confidence', 0):.2f}")
                        
                        # Check entities
                        entities = ai_analysis.get("entities", {})
                        extracted_entities = ai_analysis.get("extracted_entities_list", {})
                        
                        if entities:
                            print(f"   🔍 Entities Structure:")
                            print(f"      - Success: {entities.get('success', False)}")
                            print(f"      - Entity Count: {entities.get('entity_count', 0)}")
                            entity_data = entities.get('entities', {})
                            if entity_data:
                                print(f"      - Entity Types: {list(entity_data.keys())}")
                                # Show samples
                                for entity_type, entity_list in entity_data.items():
                                    if entity_list:
                                        sample = entity_list[:2]  # Show first 2
                                        print(f"        * {entity_type}: {sample}")
                        
                        if extracted_entities:
                            print(f"   📝 Extracted Entities List:")
                            for entity_type, entity_list in extracted_entities.items():
                                if entity_list:
                                    print(f"      - {entity_type}: {len(entity_list)} items ({entity_list[:2]})")
                        
                        # Check structured data
                        structured_data = ai_analysis.get("structured_data", {})
                        if structured_data and structured_data.get("success"):
                            print(f"   📊 Structured Data:")
                            print(f"      - Type: {structured_data.get('data_type', 'N/A')}")
                            struct_content = structured_data.get("structured_data", {})
                            if struct_content:
                                if "key_info" in struct_content:
                                    key_info = struct_content["key_info"]
                                    print(f"      - Key Info Fields: {list(key_info.keys())}")
                                    # Show sample values
                                    for key, value in list(key_info.items())[:3]:
                                        if value:
                                            print(f"        * {key}: {value}")
                                if "headers" in struct_content:
                                    headers = struct_content["headers"]
                                    print(f"      - Headers: {headers}")
                                    print(f"      - Rows: {struct_content.get('total_rows', 0)}")
                        
                        # Check test results (for medical documents)
                        test_results = ai_analysis.get("test_results", [])
                        if test_results:
                            print(f"   🩺 Test Results: {len(test_results)} entries")
                            if test_results:
                                first_result = test_results[0]
                                print(f"      - Sample: {first_result}")
                        
                        print(f"   📊 Word Count: {ai_analysis.get('word_count', 0)}")
                        print(f"   🌍 Language: {ai_analysis.get('language', {}).get('primary_language', 'N/A')}")
                        
                    else:
                        print(f"   ❌ Detail request failed: {detail_response.status_code}")
                        print(f"   Response: {detail_response.text[:200]}")
            else:
                print("   ⚠️  No documents found")
        else:
            print(f"   ❌ Documents list request failed: {list_response.status_code}")
            print(f"   Response: {list_response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server not running")
        print("💡 Please start the backend with: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_api_response()
