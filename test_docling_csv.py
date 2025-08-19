#!/usr/bin/env python3
"""
Test DocLing processing of CSV files directly
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.docling_service import DoclingService
from services.structured_data_service import StructuredDataService

def test_docling_csv():
    print("🔍 Testing DocLing CSV Processing")
    print("=" * 50)
    
    # Create test CSV
    csv_content = """Month,Revenue,Expenses,Profit,Profit_Margin
01/2024,70298,66847,3451,4.9%
02/2024,118433,37038,81395,68.7%
03/2024,82659,54821,27838,33.7%"""
    
    test_file = "test_docling.csv"
    
    try:
        print("1. 📝 Creating test CSV...")
        with open(test_file, "w") as f:
            f.write(csv_content)
        print("   ✅ Test CSV created")
        
        print("\n2. 🔍 Testing DocLing Service...")
        docling_service = DoclingService()
        result = docling_service.process_document(test_file, "csv")
        
        print(f"   📊 DocLing Result:")
        print(f"      - Success: {result.get('success', False)}")
        if result.get('success'):
            text = result.get('text', '')
            print(f"      - Text Length: {len(text)} characters")
            print(f"      - Text Preview: '{text[:100]}{'...' if len(text) > 100 else ''}'")
        else:
            print(f"      - Error: {result.get('error', 'Unknown error')}")
        
        print("\n3. 📊 Testing Structured Data Service...")
        structured_service = StructuredDataService()
        with open(test_file, "rb") as f:
            content = f.read()
        struct_result = structured_service.extract_structured_data(test_file, "csv", content)
        
        print(f"   📊 Structured Data Result:")
        print(f"      - Success: {struct_result.get('success', False)}")
        if struct_result.get('success'):
            data_type = struct_result.get('data_type', 'unknown')
            structured_data = struct_result.get('structured_data', {})
            print(f"      - Data Type: {data_type}")
            if 'headers' in structured_data:
                print(f"      - Headers: {structured_data['headers']}")
                print(f"      - Rows: {structured_data.get('total_rows', 0)}")
        else:
            print(f"      - Error: {struct_result.get('error', 'Unknown error')}")
        
        print("\n4. 🤖 Testing Combined Processing...")
        # Simulate the backend processing logic
        if result.get('success'):
            extracted_text = result.get('text', '')
            
            # Enhance with structured data summary
            if struct_result.get('success'):
                structured_summary = f"\n\nStructured Data Summary:\n"
                structured_summary += f"Data Type: {struct_result.get('data_type', 'unknown')}\n"
                
                structured_data = struct_result.get('structured_data', {})
                if 'headers' in structured_data:
                    structured_summary += f"Columns: {', '.join(structured_data['headers'][:5])}\n"
                    structured_summary += f"Total Rows: {structured_data.get('total_rows', 0)}\n"
                
                extracted_text += structured_summary
            
            print(f"   📄 Enhanced Text ({len(extracted_text)} chars):")
            print(f"      '{extracted_text[:200]}{'...' if len(extracted_text) > 200 else ''}'")
            
            # Test classification
            print("\n5. 🏷️ Testing Classification...")
            from services.classification_service import DocumentClassificationService
            classification_service = DocumentClassificationService()
            classification_result = classification_service.classify_document(extracted_text)
            
            print(f"   📊 Classification Result:")
            print(f"      - Type: {classification_result.get('document_type', 'unknown')}")
            print(f"      - Confidence: {classification_result.get('confidence', 0):.2f}")
            print(f"      - Success: {classification_result.get('success', False)}")
            
            if classification_result.get('success'):
                print("   ✅ Full AI processing pipeline works for CSV!")
            else:
                print("   ❌ Classification failed")
        
        else:
            print("   ❌ DocLing failed, cannot proceed with AI processing")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\n🗑️ Cleaned up {test_file}")
    
    print("\n" + "=" * 50)
    print("🎉 DocLing CSV Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_docling_csv()
