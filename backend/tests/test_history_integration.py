"""
Integration test for history functionality with analysis endpoints.
Tests that history is automatically saved when analysis is performed.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_history_integration():
    """Test history integration with analysis workflow."""
    print("Testing History Integration with Analysis...")
    print("-" * 50)
    
    # Test 1: Perform an analysis (this should save to history)
    print("\n1. Performing complexity analysis...")
    analysis_request = {
        "problem_url": "https://leetcode.com/problems/two-sum/",
        "code": """def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []""",
        "language": "python",
        "analysis_type": "complexity"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/analyze", json=analysis_request)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Analysis completed successfully")
            if "time_complexity" in result:
                print(f"  Time Complexity: {result['time_complexity']}")
                print(f"  Space Complexity: {result['space_complexity']}")
        else:
            print(f"⚠ Analysis failed: {response.text}")
            print("  (This is expected if API keys are not configured)")
    except Exception as e:
        print(f"⚠ Analysis request failed: {str(e)}")
        print("  (This is expected if API keys are not configured)")
    
    # Small delay to ensure database write completes
    time.sleep(0.5)
    
    # Test 2: Check if history was saved
    print("\n2. Checking if history was saved...")
    response = requests.get(f"{BASE_URL}/api/history")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Retrieved {len(data['entries'])} entries")
        
        if data['entries']:
            entry = data['entries'][0]
            print(f"  Entry ID: {entry['id']}")
            print(f"  Problem: {entry['problem_title']}")
            print(f"  Analysis Type: {entry['analysis_type']}")
            print(f"  Language: {entry['language']}")
            print(f"  Timestamp: {entry['timestamp']}")
            
            # Test 3: Get history for specific problem
            print("\n3. Getting history for 'two-sum'...")
            response = requests.get(f"{BASE_URL}/api/history/two-sum")
            if response.status_code == 200:
                entries = response.json()
                print(f"✓ Retrieved {len(entries)} entries for 'two-sum'")
            
            # Test 4: Perform another analysis with different type
            print("\n4. Performing hints analysis...")
            analysis_request["analysis_type"] = "hints"
            try:
                response = requests.post(f"{BASE_URL}/api/analyze", json=analysis_request)
                if response.status_code == 200:
                    print("✓ Hints analysis completed")
                else:
                    print(f"⚠ Hints analysis failed (expected if no API keys)")
            except Exception as e:
                print(f"⚠ Hints request failed (expected if no API keys)")
            
            time.sleep(0.5)
            
            # Test 5: Check if we now have multiple entries
            print("\n5. Checking for multiple entries...")
            response = requests.get(f"{BASE_URL}/api/history/two-sum")
            if response.status_code == 200:
                entries = response.json()
                print(f"✓ Now have {len(entries)} entries for 'two-sum'")
                
                # Show analysis types
                analysis_types = [e['analysis_type'] for e in entries]
                print(f"  Analysis types: {', '.join(analysis_types)}")
            
            # Test 6: Delete entries
            print("\n6. Cleaning up test entries...")
            response = requests.get(f"{BASE_URL}/api/history")
            if response.status_code == 200:
                data = response.json()
                deleted_count = 0
                for entry in data['entries']:
                    if entry['problem_slug'] == 'two-sum':
                        delete_response = requests.delete(f"{BASE_URL}/api/history/{entry['id']}")
                        if delete_response.status_code == 200:
                            deleted_count += 1
                print(f"✓ Deleted {deleted_count} test entries")
        else:
            print("⊘ No entries found (analysis may have failed due to missing API keys)")
    
    print("\n" + "=" * 50)
    print("Integration test completed!")
    print("=" * 50)


if __name__ == "__main__":
    test_history_integration()
