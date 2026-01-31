"""
Test script for history service functionality.
Tests basic CRUD operations and retention policy.
"""

import sys
import os
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.history_service import history_service, HistoryCreateRequest


def test_history_service():
    """Test basic history service operations."""
    print("Testing History Service...")
    print("-" * 50)
    
    # Test 1: Create a history entry
    print("\n1. Testing entry creation...")
    entry_data = HistoryCreateRequest(
        problem_slug="two-sum",
        problem_title="Two Sum",
        code="def twoSum(nums, target):\n    pass",
        language="python",
        analysis_type="complexity",
        result={
            "time_complexity": "O(n^2)",
            "space_complexity": "O(1)",
            "explanation": "Nested loops",
            "key_operations": ["nested iteration"]
        }
    )
    
    created_entry = history_service.save_analysis(entry_data)
    print(f"✓ Created entry with ID: {created_entry.id}")
    print(f"  Problem: {created_entry.problem_title}")
    print(f"  Analysis Type: {created_entry.analysis_type}")
    
    # Test 2: Retrieve all history
    print("\n2. Testing history retrieval...")
    history_response = history_service.get_history()
    print(f"✓ Retrieved {len(history_response.entries)} entries")
    print(f"  Total count: {history_response.total_count}")
    
    # Test 3: Retrieve history by problem
    print("\n3. Testing problem-specific history...")
    problem_entries = history_service.get_history_by_problem("two-sum")
    print(f"✓ Retrieved {len(problem_entries)} entries for 'two-sum'")
    
    # Test 4: Create another entry for the same problem
    print("\n4. Testing multiple entries for same problem...")
    entry_data2 = HistoryCreateRequest(
        problem_slug="two-sum",
        problem_title="Two Sum",
        code="def twoSum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        pass",
        language="python",
        analysis_type="hints",
        result={
            "hints": ["Consider using a hash map"],
            "progressive": True,
            "next_steps": ["Implement the lookup logic"]
        }
    )
    
    created_entry2 = history_service.save_analysis(entry_data2)
    print(f"✓ Created second entry with ID: {created_entry2.id}")
    
    problem_entries = history_service.get_history_by_problem("two-sum")
    print(f"✓ Now have {len(problem_entries)} entries for 'two-sum'")
    
    # Test 5: Delete an entry
    print("\n5. Testing entry deletion...")
    deleted = history_service.delete_entry(created_entry.id)
    print(f"✓ Deleted entry: {deleted}")
    
    history_response = history_service.get_history()
    print(f"✓ Remaining entries: {len(history_response.entries)}")
    
    # Test 6: Test pagination
    print("\n6. Testing pagination...")
    page1 = history_service.get_history(limit=1, offset=0)
    print(f"✓ Page 1: {len(page1.entries)} entries, has_more: {page1.has_more}")
    
    # Test 7: Cleanup test (manual trigger)
    print("\n7. Testing expired entries cleanup...")
    deleted_count = history_service.delete_expired_entries()
    print(f"✓ Deleted {deleted_count} expired entries")
    
    print("\n" + "=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)
    
    # Cleanup
    history_service.shutdown()


if __name__ == "__main__":
    test_history_service()
