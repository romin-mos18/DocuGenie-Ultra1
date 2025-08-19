#!/usr/bin/env python3
"""
Debug backend processing to see why AI analysis isn't being stored
"""

import requests
import time
import json

def debug_backend_processing():
    print("🔍 Debug Backend Processing")
    print("=" * 50)
    
    backend_url = "http://localhost:8007"
    
    # Simple test TXT file (we know this works)
    txt_content = """HOSPITAL DISCHARGE SUMMARY
--------------------------------------------------

Hospital: Regional Healthcare Center
Patient: John Doe
MRN: 346152
Admission Date: 07/13/2025
Discharge Date: 08/12/2025

DIAGNOSIS:
Primary diagnosis of hypertension with secondary symptoms of fatigue.

TREATMENT:
Patient received medication therapy and lifestyle counseling.
"""
    
    try:
        print("1. 📝 Creating test TXT file...")
        with open("debug_test.txt", "w") as f:
            f.write(txt_content)
        print("   ✅ Test TXT created")
        
        print("\n2. 📤 Uploading document...")
        with open("debug_test.txt", "rb") as f:
            files = {'file': ('debug_test.txt', f, 'text/plain')}
            upload_response = requests.post(f"{backend_url}/api/v1/upload", files=files, timeout=60)
        
        print(f"   📊 Upload Response Status: {upload_response.status_code}")
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            document_id = upload_data.get("document_id")
            print(f"   ✅ Upload successful! Document ID: {document_id}")
            
            # Print the full upload response
            print("\n   📋 Full Upload Response:")
            print(json.dumps(upload_data, indent=4))
            
            # Wait for processing
            print("\n3. ⏳ Waiting for AI processing...")
            time.sleep(2)
            
            # Check detail immediately
            print("\n4. 🔍 Checking detail response...")
            detail_response = requests.get(f"{backend_url}/api/v1/documents/{document_id}", timeout=30)
            
            print(f"   📊 Detail Response Status: {detail_response.status_code}")
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                
                print("\n   📋 Full Detail Response:")
                print(json.dumps(detail_data, indent=4)[:1000] + "..." if len(json.dumps(detail_data, indent=4)) > 1000 else json.dumps(detail_data, indent=4))
                
                # Check if AI analysis is present
                ai_analysis = detail_data.get("ai_analysis", {})
                if ai_analysis:
                    print(f"\n   ✅ AI Analysis present with {len(ai_analysis)} keys: {list(ai_analysis.keys())}")
                else:
                    print(f"\n   ❌ AI Analysis missing or empty")
                    
                # Check the document object directly
                document = detail_data.get("document", {})
                if document:
                    doc_ai_analysis = document.get("ai_analysis", {})
                    if doc_ai_analysis:
                        print(f"   ✅ Document.ai_analysis present with {len(doc_ai_analysis)} keys: {list(doc_ai_analysis.keys())}")
                    else:
                        print(f"   ❌ Document.ai_analysis missing or empty")
            
            # Cleanup
            print("\n5. 🗑️ Cleaning up...")
            try:
                delete_response = requests.delete(f"{backend_url}/documents/{document_id}")
                print(f"   Delete status: {delete_response.status_code}")
            except:
                pass
            
            import os
            if os.path.exists("debug_test.txt"):
                os.remove("debug_test.txt")
                print("   ✅ Local test file removed")
        
        else:
            print(f"   ❌ Upload failed: {upload_response.text[:200]}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🎉 Debug Complete!")

if __name__ == "__main__":
    debug_backend_processing()
