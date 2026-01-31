"""
Test script for history API endpoints.
Tests the FastAPI endpoints for history management.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"


def test_history_endpoints():
    """Test history API endpoints."""
    print("Testing History API Endpoints...")
    print("-" * 50)
    
    # Test 1: Check if server is running
    print("\n1. Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ Server is running")
        else:
            print("✗ Server health check failed")
            return
    except requests.exceptions.ConnectionError:
        print("✗ Server is not running. Please start the server with: uvicorn main:app --reload")
        return
    
    # Test 2: Get all history (should be empty or have previous entries)
    print("\n2. Testing GET /api/history...")
    response = requests.get(f"{BASE_URL}/api/history")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Retrieved {len(data['entries'])} entries")
        print(f"  Total count: {data['total_count']}")
        print(f"  Has more: {data['has_more']}")
    else:
        print(f"✗ Failed: {response.text}")
    
    # Test 3: Get history for a specific problem
    print("\n3. Testing GET /api/history/{problem_slug}...")
    response = requests.get(f"{BASE_URL}/api/history/two-sum")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        entries = response.json()
        print(f"✓ Retrieved {len(entries)} entries for 'two-sum'")
        if entries:
            print(f"  First entry ID: {entries[0]['id']}")
            print(f"  Analysis type: {entries[0]['analysis_type']}")
    else:
        print(f"✗ Failed: {response.text}")
    
    # Test 4: Test pagination
    print("\n4. Testing pagination with limit and offset...")
    response = requests.get(f"{BASE_URL}/api/history?limit=2&offset=0")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Retrieved {len(data['entries'])} entries (limit=2)")
        print(f"  Has more: {data['has_more']}")
    else:
        print(f"✗ Failed: {response.text}")
    
    # Test 5: Delete an entry (if any exist)
    print("\n5. Testing DELETE /api/history/{entry_id}...")
    response = requests.get(f"{BASE_URL}/api/history")
    if response.status_code == 200:
        data = response.json()
        if data['entries']:
            entry_id = data['entries'][0]['id']
            delete_response = requests.delete(f"{BASE_URL}/api/history/{entry_id}")
            print(f"Status: {delete_response.status_code}")
            if delete_response.status_code == 200:
                print(f"✓ Deleted entry: {entry_id}")
            else:
                print(f"✗ Failed: {delete_response.text}")
        else:
            print("⊘ No entries to delete")
    
    # Test 6: Try to delete non-existent entry
    print("\n6. Testing DELETE with non-existent entry...")
    response = requests.delete(f"{BASE_URL}/api/history/non-existent-id")
    print(f"Status: {response.status_code}")
    if response.status_code == 404:
        print("✓ Correctly returned 404 for non-existent entry")
    else:
        print(f"✗ Expected 404, got {response.status_code}")
    
    print("\n" + "=" * 50)
    print("Endpoint tests completed!")
    print("=" * 50)


if __name__ == "__main__":
    test_history_endpoints()
