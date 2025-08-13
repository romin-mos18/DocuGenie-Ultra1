#!/usr/bin/env python3
"""
Test script to debug delete functionality
"""
import os
import sys

def test_file_paths():
    """Test file path resolution"""
    print("🔍 Testing file paths...")
    
    # Current working directory
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")
    
    # Uploads directory
    upload_dir = "./uploads"
    abs_upload_dir = os.path.abspath(upload_dir)
    print(f"Uploads directory (relative): {upload_dir}")
    print(f"Uploads directory (absolute): {abs_upload_dir}")
    
    # Check if uploads directory exists
    if os.path.exists(upload_dir):
        print("✅ Uploads directory exists")
        
        # List files in uploads directory
        files = os.listdir(upload_dir)
        print(f"Files in uploads directory: {len(files)}")
        
        # Show first few files
        for i, file in enumerate(files[:5]):
            file_path = os.path.join(upload_dir, file)
            if os.path.isfile(file_path):
                print(f"  {i+1}. {file} (exists: {os.path.exists(file_path)})")
    else:
        print("❌ Uploads directory does not exist")
    
    # Test specific file
    test_file = "DocuGenie_Ultra_V3.0.0_-_Final_QA_Validation_Report.pdf"
    test_file_path = os.path.join(upload_dir, test_file)
    abs_test_file_path = os.path.abspath(test_file_path)
    
    print(f"\n🔍 Testing specific file: {test_file}")
    print(f"Relative path: {test_file_path}")
    print(f"Absolute path: {abs_test_file_path}")
    print(f"File exists: {os.path.exists(test_file_path)}")
    
    if os.path.exists(test_file_path):
        file_stat = os.stat(test_file_path)
        print(f"File size: {file_stat.st_size} bytes")
        print(f"Last modified: {file_stat.st_mtime}")

if __name__ == "__main__":
    test_file_paths()
