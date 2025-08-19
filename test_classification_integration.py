#!/usr/bin/env python3
"""
Test script to verify document classification integration
"""
import requests
import json
import time
import os
from pathlib import Path

def test_classification_integration():
    """Test the complete document classification flow"""
    base_url = "http://localhost:8007"
    
    print("🧪 Testing DocuGenie Ultra Document Classification Integration")
    print("=" * 60)
    
    # Wait for server to be ready
    print("📡 Checking server health...")
    for i in range(10):
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server is ready!")
                break
        except requests.exceptions.ConnectionError:
            print(f"⏳ Server not ready yet, waiting... ({i+1}/10)")
            time.sleep(2)
    else:
        print("❌ Server failed to start after 20 seconds")
        return
    
    # Test 1: Create sample medical documents
    print("\n📝 Creating test documents...")
    
    test_documents = [
        {
            "filename": "medical_report_test.txt",
            "content": """MEDICAL REPORT
            
Patient: John Smith
Date: 2025-01-17
Physician: Dr. Jane Wilson

Chief Complaint: Patient reports chest pain and shortness of breath.

History of Present Illness:
The patient is a 45-year-old male who presents with acute onset chest pain that started approximately 2 hours ago. The pain is described as sharp and radiating to the left arm.

Physical Examination:
Vital signs: BP 140/90, HR 95, Temp 98.6°F
Cardiovascular: Regular rate and rhythm, no murmurs
Respiratory: Clear to auscultation bilaterally

Assessment and Plan:
1. Chest pain - likely cardiac origin
2. Order ECG and cardiac enzymes
3. Consider cardiology consultation
4. Monitor in observation unit

Dr. Jane Wilson, MD
Internal Medicine""",
            "expected_type": "medical_report"
        },
        {
            "filename": "lab_results_test.txt", 
            "content": """LABORATORY REPORT
            
LabCorp
Patient: John Smith
DOB: 1978-05-15
MRN: 123456

Test Results:
Glucose: 95 mg/dL (Normal: 70-100)
Hemoglobin: 14.2 g/dL (Normal: 12-16)
Total Cholesterol: 180 mg/dL (Normal: <200)
HDL Cholesterol: 45 mg/dL (Normal: >40)
LDL Cholesterol: 110 mg/dL (Normal: <130)
Triglycerides: 125 mg/dL (Normal: <150)

All values within normal limits.

Reviewed by: Dr. Sarah Johnson, MD
Laboratory Medicine""",
            "expected_type": "lab_result"
        }
    ]
    
    # Create uploads directory
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    
    results = []
    
    for doc in test_documents:
        print(f"\n🔬 Testing: {doc['filename']}")
        
        # Save test document
        file_path = uploads_dir / doc["filename"]
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(doc["content"])
        
        # Upload document
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (doc["filename"], f, 'text/plain')}
                response = requests.post(f"{base_url}/documents/upload", files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload successful!")
                print(f"   Document ID: {result.get('document_id')}")
                print(f"   Classified as: {result.get('document_type', 'unknown')}")
                print(f"   Confidence: {result.get('confidence', 0.0):.2%}")
                print(f"   Expected: {doc['expected_type']}")
                
                # Check if classification is correct
                if result.get('document_type') == doc['expected_type']:
                    print(f"✅ Classification CORRECT!")
                else:
                    print(f"❌ Classification INCORRECT!")
                
                results.append({
                    "filename": doc["filename"],
                    "expected": doc["expected_type"],
                    "actual": result.get('document_type', 'unknown'),
                    "confidence": result.get('confidence', 0.0),
                    "correct": result.get('document_type') == doc['expected_type']
                })
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error uploading document: {e}")
    
    # Test 2: Check document list
    print(f"\n📋 Fetching document list...")
    try:
        response = requests.get(f"{base_url}/documents/", timeout=10)
        if response.status_code == 200:
            docs = response.json()
            print(f"✅ Found {len(docs.get('documents', []))} documents")
            
            for doc in docs.get('documents', []):
                print(f"   📄 {doc.get('filename')}: {doc.get('documentType', 'Unknown')}")
        else:
            print(f"❌ Failed to fetch documents: {response.status_code}")
    except Exception as e:
        print(f"❌ Error fetching documents: {e}")
    
    # Summary
    print(f"\n📊 CLASSIFICATION TEST SUMMARY")
    print("=" * 40)
    correct_count = sum(1 for r in results if r['correct'])
    total_count = len(results)
    accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
    
    print(f"Total Tests: {total_count}")
    print(f"Correct Classifications: {correct_count}")
    print(f"Accuracy: {accuracy:.1f}%")
    
    if accuracy >= 80:
        print("🎉 EXCELLENT! Classification system is working accurately!")
    elif accuracy >= 60:
        print("👍 GOOD! Classification system is working reasonably well.")
    else:
        print("⚠️ Classification accuracy needs improvement.")
    
    # Cleanup
    print(f"\n🧹 Cleaning up test files...")
    for doc in test_documents:
        file_path = uploads_dir / doc["filename"]
        if file_path.exists():
            file_path.unlink()
            print(f"   Removed: {doc['filename']}")

if __name__ == "__main__":
    test_classification_integration()
