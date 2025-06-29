#!/usr/bin/env python3
"""
Test script to verify API connection to the backend
"""

import requests
import json
import time

API_BASE_URL = 'http://localhost:8050'

def test_health():
    """Test if the backend is responding"""
    try:
        response = requests.get(f'{API_BASE_URL}/health', timeout=5)
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Services: {data.get('services', {})}")
            return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
    return False

def test_upload():
    """Test document upload with a simple text file"""
    try:
        # Create test content
        test_content = """
        Test Document for AI Processing
        
        This is a test document to verify that our AI integration is working correctly.
        The document contains multiple paragraphs with different types of content.
        
        Key points:
        - AI processing should work
        - Summary should be generated
        - Insights should be extracted
        
        Conclusion: This test will verify the complete pipeline from upload to AI processing.
        """
        
        # Prepare the file
        files = {
            'file': ('test.txt', test_content, 'text/plain')
        }
        data = {
            'template': 'general'
        }
        
        print("🔄 Testing document upload...")
        response = requests.post(f'{API_BASE_URL}/summarize', files=files, data=data, timeout=60)
        
        print(f"Upload response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print(f"   Doc ID: {result.get('doc_id')}")
            print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
            print(f"   Summary preview: {result.get('summary', '')[:100]}...")
            return True
        else:
            print(f"❌ Upload failed: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Upload test failed: {e}")
    return False

def main():
    print("🚀 Testing AI Document Summarizer API Connection")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Backend is not running or not accessible")
        print("   Please start the backend with:")
        print("   cd backend && .\\venv\\Scripts\\activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8050")
        return
    
    # Wait a bit
    time.sleep(2)
    
    # Test 2: Document upload
    print("\n" + "=" * 50)
    if test_upload():
        print("\n🎉 All tests passed! Your AI integration is working!")
    else:
        print("\n❌ Upload test failed. Check backend logs for details.")

if __name__ == "__main__":
    main() 