#!/usr/bin/env python3
"""
Test script to verify frontend displays extracted data properly
"""

import requests
import json

def test_frontend_display():
    print("🖥️ Testing Frontend Display of Extracted Data")
    print("=" * 50)
    
    backend_url = "http://localhost:8007"
    
    try:
        # Get documents list
        print("1. 📋 Fetching documents...")
        list_response = requests.get(f"{backend_url}/api/v1/documents", timeout=10)
        
        if list_response.status_code == 200:
            list_data = list_response.json()
            documents = list_data.get("documents", [])
            
            # Find the hospital report (should have rich AI analysis)
            hospital_doc = None
            for doc in documents:
                if "hospital_report" in doc.get("filename", "").lower():
                    hospital_doc = doc
                    break
            
            if hospital_doc:
                doc_id = hospital_doc.get("id")
                print(f"2. 🏥 Testing hospital report display (Document ID: {doc_id})")
                
                # Get detail data
                detail_response = requests.get(f"{backend_url}/api/v1/documents/{doc_id}", timeout=10)
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    
                    print("✅ Detail API Response Structure:")
                    print(f"   📄 Document: {detail_data.get('filename', 'N/A')}")
                    print(f"   📋 Status: {detail_data.get('status', 'N/A')}")
                    print(f"   📊 File Type: {detail_data.get('file_type', 'N/A')}")
                    
                    # Check AI analysis structure for frontend
                    ai_analysis = detail_data.get("ai_analysis", {})
                    if ai_analysis:
                        print("\n🤖 AI Analysis Available for Frontend:")
                        
                        # Classification data
                        classification = ai_analysis.get("classification", {})
                        if classification:
                            print(f"   🏷️  Classification:")
                            print(f"      - document_type: '{classification.get('document_type', 'N/A')}'")
                            print(f"      - confidence: {classification.get('confidence', 0):.2f}")
                            print(f"      - success: {classification.get('success', False)}")
                        
                        # Entities data
                        entities = ai_analysis.get("entities", {})
                        extracted_entities = ai_analysis.get("extracted_entities_list", {})
                        
                        if entities:
                            print(f"   🔍 Entities Structure:")
                            print(f"      - success: {entities.get('success', False)}")
                            print(f"      - entity_count: {entities.get('entity_count', 0)}")
                            
                            entity_data = entities.get('entities', {})
                            if entity_data:
                                print(f"      - Available entity types:")
                                for entity_type, entity_list in entity_data.items():
                                    if entity_list:
                                        print(f"        * {entity_type}: {len(entity_list)} items {entity_list[:2]}")
                        
                        # Language data
                        language = ai_analysis.get("language", {})
                        if language:
                            print(f"   🌍 Language:")
                            print(f"      - primary_language: '{language.get('primary_language', 'N/A')}'")
                            print(f"      - confidence: {language.get('confidence', 0):.2f}")
                        
                        # Metadata
                        print(f"   📊 Metadata:")
                        print(f"      - word_count: {ai_analysis.get('word_count', 0)}")
                        print(f"      - entity_count: {ai_analysis.get('entity_count', 0)}")
                        print(f"      - processing_method: '{ai_analysis.get('processing_method', 'N/A')}'")
                        
                        # Text preview
                        text_preview = ai_analysis.get("text_preview", "")
                        if text_preview:
                            print(f"   📄 Text Preview: '{text_preview[:100]}{'...' if len(text_preview) > 100 else ''}'")
                        
                        print("\n✅ Frontend should be able to display:")
                        print("   • Document type badge from classification.document_type")
                        print("   • Confidence percentage from classification.confidence")
                        print("   • Language from language.primary_language")
                        print("   • Word count from word_count")
                        print("   • Entity count from entity_count")
                        print("   • Individual entities from extracted_entities_list")
                        print("   • Full text preview from text_preview")
                        
                        # Test what frontend will see
                        print("\n🎨 Frontend Data Mapping Test:")
                        print("   Navigation: /documents → Click hospital_report_001.txt → Detail View")
                        print(f"   Expected Type: {classification.get('document_type', 'unknown').replace('_', ' ').title()}")
                        print(f"   Expected Confidence: {classification.get('confidence', 0) * 100:.1f}%")
                        print(f"   Expected Language: {language.get('primary_language', 'EN').upper()}")
                        print(f"   Expected Entity Count: {ai_analysis.get('entity_count', 0)}")
                        
                        # Check for medical-specific data
                        if classification.get('document_type') == 'medical_report':
                            names = extracted_entities.get('names', [])
                            dates = extracted_entities.get('dates', [])
                            medical_terms = extracted_entities.get('medical_terms', [])
                            
                            print(f"\n🏥 Medical Document Specific:")
                            print(f"   • Patient Names: {names[:2] if names else 'None found'}")
                            print(f"   • Medical Dates: {dates[:2] if dates else 'None found'}")
                            print(f"   • Medical Terms: {medical_terms[:3] if medical_terms else 'None found'}")
                    
                    else:
                        print("   ❌ No AI analysis found in response")
                else:
                    print(f"   ❌ Detail request failed: {detail_response.status_code}")
            else:
                print("   ⚠️  Hospital report not found in documents list")
        else:
            print(f"   ❌ Documents list request failed: {list_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server not running")
        print("💡 Please start the backend with: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 50)
    print("🎉 Frontend Display Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_frontend_display()
