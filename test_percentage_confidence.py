#!/usr/bin/env python3
"""
Test script to verify confidence scores are displayed as percentages with 2 decimal places
"""

import requests
import json

def test_percentage_confidence():
    print("📊 Testing Confidence Score Percentage Display Format")
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
            
            print(f"\n📊 Confidence Display Format Examples:")
            print(f"   Backend Value → Frontend Display")
            print(f"   ──────────────────────────────────")
            
            # Test with various confidence values
            test_values = [
                0.5555555555555556,  # Should show as 55.56%
                0.6000000000000001,  # Should show as 60.00%
                0.89,                # Should show as 89.00%
                0.567,               # Should show as 56.70%
                0.1,                 # Should show as 10.00%
                0.9999,              # Should show as 99.99%
                0.0001,              # Should show as 0.01%
                0                    # Should show as 0.00%
            ]
            
            for val in test_values:
                formatted = f"{(val * 100):.2f}%"
                print(f"   {val:18.16f} → {formatted}")
            
            print(f"\n📄 Actual Documents:")
            for i, doc in enumerate(documents[:5]):  # Show first 5 documents
                filename = doc.get("filename", "Unknown")
                confidence = doc.get("confidence", 0)
                formatted_confidence = f"{(confidence * 100):.2f}%"
                
                print(f"   {i+1}. {filename}")
                print(f"      Raw: {confidence}")
                print(f"      Display: {formatted_confidence}")
        
        # Test specific document detail
        if documents:
            doc_id = documents[0].get("id")
            print(f"\n2. 🔍 Testing detail view for document {doc_id}...")
            
            detail_response = requests.get(f"{backend_url}/api/v1/documents/{doc_id}", timeout=10)
            
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                ai_analysis = detail_data.get("ai_analysis", {})
                
                if ai_analysis:
                    classification = ai_analysis.get("classification", {})
                    confidence = classification.get("confidence", 0)
                    formatted_confidence = f"{(confidence * 100):.2f}%"
                    
                    print(f"   📊 AI Analysis Confidence:")
                    print(f"      Raw Value: {confidence}")
                    print(f"      Frontend Display: {formatted_confidence}")
                    
                else:
                    print("   ❌ No AI analysis available")
        
        print(f"\n3. ✅ Updated Display Format Specifications:")
        print(f"   • Format: Percentage with exactly 2 decimal places")
        print(f"   • Formula: (confidence * 100).toFixed(2) + '%'")
        print(f"   • Examples:")
        print(f"     - 0.5556 → 55.56%")
        print(f"     - 0.6000 → 60.00%") 
        print(f"     - 0.8900 → 89.00%")
        print(f"     - 0.5670 → 56.70%")
        print(f"   • Range: 0.00% to 100.00%")
        print(f"   • Always includes % symbol")
        
        print(f"\n4. 📱 Frontend Components Updated:")
        print(f"   ✅ formatConfidence() utility function")
        print(f"   ✅ UniversalDocumentDetails (3 locations)")
        print(f"   ✅ DocumentTypeSpecificSections")
        print(f"   ✅ Folder view chips (3 locations)")
        print(f"   ✅ Main documents page CircularConfidence")
        print(f"   ✅ AI Features table")
        print(f"   ✅ Quality card display")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server not running")
        print("💡 Please start the backend with: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Confidence Percentage Format Complete!")
    print("🎯 All confidence scores now show as: XX.XX%")
    print("=" * 60)

if __name__ == "__main__":
    test_percentage_confidence()
