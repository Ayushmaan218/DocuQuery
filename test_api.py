"""
Test script for DocuQuery RAG System
Tests document upload and query functionality
"""

import requests
import json
import os

BASE_URL = "http://localhost:5000/api"

def test_health_check():
    """Test health check endpoint"""
    print("\n" + "="*50)
    print("Testing Health Check...")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_upload_document(file_path):
    """Test document upload"""
    print("\n" + "="*50)
    print(f"Testing Document Upload: {file_path}")
    print("="*50)
    
    if not os.path.exists(file_path):
        print(f"Error: File not found - {file_path}")
        return None
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return response.json().get('document_id')
    return None

def test_query(query_text, top_k=3):
    """Test query endpoint"""
    print("\n" + "="*50)
    print(f"Testing Query: {query_text}")
    print("="*50)
    
    payload = {
        "query": query_text,
        "top_k": top_k
    }
    
    response = requests.post(
        f"{BASE_URL}/query",
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    
    print(f"\nQuery: {result.get('query')}")
    print(f"\nAnswer: {result.get('answer')}")
    print(f"\nConfidence: {result.get('confidence')}")
    print(f"\nChunks Retrieved: {result.get('chunks_retrieved')}")
    
    if result.get('sources'):
        print("\nSources:")
        for i, source in enumerate(result['sources'], 1):
            print(f"\n  Source {i}:")
            print(f"    Filename: {source.get('filename')}")
            print(f"    Chunk Index: {source.get('chunk_index')}")
            print(f"    Similarity Score: {source.get('similarity_score'):.4f}")
            print(f"    Preview: {source.get('text_preview')[:100]}...")
    
    return response.status_code == 200

def test_list_documents():
    """Test list documents endpoint"""
    print("\n" + "="*50)
    print("Testing List Documents...")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/documents")
    print(f"Status Code: {response.status_code}")
    result = response.json()
    
    print(f"Total Documents: {result.get('count')}")
    
    if result.get('documents'):
        print("\nDocuments:")
        for doc in result['documents']:
            print(f"\n  - ID: {doc.get('document_id')}")
            print(f"    Filename: {doc.get('filename')}")
            print(f"    Chunks: {doc.get('chunk_count')}")
            print(f"    Status: {doc.get('status')}")
    
    return response.status_code == 200

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("DOCUQUERY RAG SYSTEM - TEST SUITE")
    print("="*70)
    
    try:
        # Test 1: Health Check
        health_ok = test_health_check()
        
        # Test 2: Upload Document
        sample_file = "sample_document.txt"
        document_id = test_upload_document(sample_file)
        
        # Test 3: List Documents
        list_ok = test_list_documents()
        
        # Test 4: Query Documents
        queries = [
            "What is artificial intelligence?",
            "What are the types of machine learning?",
            "What are the applications of AI?",
            "What are the ethical considerations of AI?"
        ]
        
        for query in queries:
            test_query(query)
        
        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Health Check: {'✓ PASSED' if health_ok else '✗ FAILED'}")
        print(f"Document Upload: {'✓ PASSED' if document_id else '✗ FAILED'}")
        print(f"List Documents: {'✓ PASSED' if list_ok else '✗ FAILED'}")
        print(f"Query Tests: ✓ COMPLETED")
        print("="*70)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server.")
        print("Make sure the Flask server is running on http://localhost:5000")
        print("Run: python app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    run_all_tests()
