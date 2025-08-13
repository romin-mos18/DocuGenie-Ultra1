#!/usr/bin/env python3
"""
Test script to verify API endpoints are working
"""
import requests
import time
import json

BASE_URL = "http://localhost:8007"

def test_endpoints():
    """Test all API endpoints"""
    print("🧪 Testing DocuGenie Ultra API Endpoints")
    print("=" * 50)
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    
    try:
        # Test root endpoint
        print("\n1️⃣ Testing root endpoint...")
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
        
        # Test documents endpoint
        print("\n2️⃣ Testing documents endpoint...")
        response = requests.get(f"{BASE_URL}/documents")
        if response.status_code == 200:
            print("✅ Documents endpoint working")
            data = response.json()
            print(f"   Found {len(data.get('documents', []))} documents")
        else:
            print(f"❌ Documents endpoint failed: {response.status_code}")
            return False
        
        # Test AI processing endpoint
        print("\n3️⃣ Testing AI processing endpoint...")
        response = requests.post(f"{BASE_URL}/documents/test123/process-ai")
        if response.status_code == 200:
            print("✅ AI processing endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ AI processing endpoint failed: {response.status_code}")
            return False
        
        # Test AI analysis endpoint
        print("\n4️⃣ Testing AI analysis endpoint...")
        response = requests.get(f"{BASE_URL}/documents/test123/ai-analysis")
        if response.status_code == 200:
            print("✅ AI analysis endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ AI analysis endpoint failed: {response.status_code}")
            return False
        
        # Test delete endpoint
        print("\n5️⃣ Testing delete endpoint...")
        response = requests.delete(f"{BASE_URL}/documents/test123")
        if response.status_code == 200:
            print("✅ Delete endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Delete endpoint failed: {response.status_code}")
            return False
        
        # Test download endpoint
        print("\n6️⃣ Testing download endpoint...")
        response = requests.get(f"{BASE_URL}/documents/test123/download")
        if response.status_code == 200:
            print("✅ Download endpoint working")
            print(f"   Content-Type: {response.headers.get('content-type')}")
        else:
            print(f"❌ Download endpoint failed: {response.status_code}")
            return False
        
        print("\n🎉 All API endpoints are working correctly!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on port 8007.")
        return False
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")
        return False

if __name__ == "__main__":
    success = test_endpoints()
    if success:
        print("\n🚀 API is ready for frontend integration!")
    else:
        print("\n⚠️ Some API endpoints need attention.")
