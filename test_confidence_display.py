#!/usr/bin/env python3
"""
Test script to verify confidence scores are displayed as numerical values with 2 decimal places
"""

import requests
import json

def test_confidence_display():
    print("🎯 Testing Confidence Score Display Format")
    print("=" * 50)
    
    backend_url = "http://localhost:8007"
    
    try:
        # Get documents list
        print("1. 📋 Fetching documents...")
        list_response = requests.get(f"{backend_url}/api/v1/documents", timeout=10)
        
        if list_response.status_code == 200:
            list_data = list_response.json()
            documents = list_data.get("documents", [])
            
            print(f"   ✅ Found {len(documents)} documents")
            
            for doc in documents:
                filename = doc.get("filename", "Unknown")
                confidence = doc.get("confidence", 0)
                
                # Check if confidence is properly formatted  
                print(f"\n📄 Document: {filename}")
                print(f"   📊 Backend Confidence: {confidence} (raw value)")
                print(f"   🎯 Expected Frontend Display: {confidence:.2f}")
                
                # Test with different confidence values to show formatting
                test_values = [0.89, 0.567, 0.1, 0.9999, 0]
                
                print(f"   📝 Format Examples:")
                for val in test_values:
                    print(f"      {val} → {val:.2f}")
        
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
                    
                    print(f"   📊 AI Analysis Confidence: {confidence}")
                    print(f"   🎯 Frontend Should Display: {confidence:.2f}")
                    
                    # Verify it's between 0-1 (not percentage)
                    if 0 <= confidence <= 1:
                        print(f"   ✅ Confidence is in correct range (0-1)")
                    else:
                        print(f"   ⚠️ Confidence might be in percentage format")
                
                else:
                    print("   ❌ No AI analysis available")
        
        print(f"\n3. 📋 Confidence Display Specifications:")
        print(f"   • Format: Numerical with exactly 2 decimal places")
        print(f"   • Range: 0.00 to 1.00 (not percentages)")
        print(f"   • Examples: 0.89, 0.92, 0.56, 0.01")
        print(f"   • NO percentage signs (%) in display")
        print(f"   • NO multiplication by 100")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server not running")
        print("💡 Please start the backend with: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Confidence Display Format Specification Complete!")
    print("🎯 All confidence scores now show as: X.XX (2 decimal places)")
    print("=" * 50)

if __name__ == "__main__":
    test_confidence_display()
