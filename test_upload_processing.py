#!/usr/bin/env python3
"""
Test script to upload a document and verify backend processing
"""

import requests
import time
import json

def test_upload_processing():
    print("📤 Testing Document Upload and Backend Processing")
    print("=" * 60)
    
    backend_url = "http://localhost:8007"
    
    # Create a simple test CSV file
    csv_content = """Month,Revenue,Expenses,Profit,Profit_Margin
01/2024,70298,66847,3451,4.9%
02/2024,118433,37038,81395,68.7%
03/2024,82659,54821,27838,33.7%"""
    
    try:
        print("1. 📝 Creating test CSV file...")
        with open("test_financial_upload.csv", "w") as f:
            f.write(csv_content)
        print("   ✅ Test CSV created")
        
        print("\n2. 📤 Uploading document...")
        with open("test_financial_upload.csv", "rb") as f:
            files = {'file': ('test_financial_upload.csv', f, 'text/csv')}
            upload_response = requests.post(f"{backend_url}/api/v1/upload", files=files, timeout=60)
        
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            document_id = upload_data.get("document_id")
            print(f"   ✅ Upload successful! Document ID: {document_id}")
            print(f"   📋 Initial Status: {upload_data.get('processing_status', 'unknown')}")
            
            # Wait a moment for processing
            print("\n3. ⏳ Waiting for AI processing...")
            time.sleep(3)
            
            # Check the processing result
            print("\n4. 🔍 Checking AI processing results...")
            detail_response = requests.get(f"{backend_url}/api/v1/documents/{document_id}", timeout=30)
            
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                print("   ✅ Detail data retrieved successfully!")
                
                # Check processing status
                status = detail_data.get("status", "unknown")
                print(f"   📊 Processing Status: {status}")
                
                # Check AI analysis
                ai_analysis = detail_data.get("ai_analysis", {})
                if ai_analysis:
                    print("\n   🤖 AI Analysis Results:")
                    
                    # Classification
                    classification = ai_analysis.get("classification", {})
                    if classification:
                        print(f"      🏷️  Classification:")
                        print(f"         - Type: {classification.get('document_type', 'N/A')}")
                        print(f"         - Confidence: {classification.get('confidence', 0):.2f}")
                        print(f"         - Success: {classification.get('success', False)}")
                    
                    # Entities
                    entities = ai_analysis.get("entities", {})
                    if entities:
                        print(f"      🔍 Entities:")
                        print(f"         - Entity Count: {entities.get('entity_count', 0)}")
                        print(f"         - Success: {entities.get('success', False)}")
                        
                        entity_data = entities.get('entities', {})
                        if entity_data:
                            for entity_type, entity_list in entity_data.items():
                                if entity_list:
                                    print(f"         - {entity_type}: {len(entity_list)} items")
                    
                    # Language
                    language = ai_analysis.get("language", {})
                    if language:
                        print(f"      🌍 Language: {language.get('primary_language', 'N/A')}")
                    
                    # Structured data
                    structured_data = ai_analysis.get("structured_data", {})
                    if structured_data and structured_data.get("success"):
                        print(f"      📊 Structured Data:")
                        print(f"         - Type: {structured_data.get('data_type', 'N/A')}")
                        struct_content = structured_data.get("structured_data", {})
                        if "headers" in struct_content:
                            print(f"         - Headers: {struct_content['headers']}")
                            print(f"         - Rows: {struct_content.get('total_rows', 0)}")
                    
                    print(f"      📄 Word Count: {ai_analysis.get('word_count', 0)}")
                    
                    if ai_analysis:
                        print("\n   ✅ CSV processing successful! AI analysis available.")
                    else:
                        print("\n   ❌ CSV processing failed - no AI analysis.")
                else:
                    print("\n   ❌ No AI analysis found in response")
                    print(f"   📄 Raw response keys: {list(detail_data.keys())}")
            else:
                print(f"   ❌ Detail request failed: {detail_response.status_code}")
                print(f"   Response: {detail_response.text[:200]}")
            
            # Cleanup
            print("\n5. 🗑️ Cleaning up...")
            delete_response = requests.delete(f"{backend_url}/documents/{document_id}")
            if delete_response.status_code == 200:
                print("   ✅ Test document deleted")
            
            # Remove local test file
            import os
            if os.path.exists("test_financial_upload.csv"):
                os.remove("test_financial_upload.csv")
                print("   ✅ Local test file removed")
        
        else:
            print(f"   ❌ Upload failed: {upload_response.status_code}")
            print(f"   Response: {upload_response.text[:200]}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server not running")
        print("💡 Please start the backend with: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Upload Processing Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_upload_processing()
