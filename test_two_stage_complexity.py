#!/usr/bin/env python3
"""
Quick test script for two-stage complexity analysis
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.ai.ai_service_factory import ai_service

# Sample code for testing
SAMPLE_CODE = """
def twoSum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
"""

async def test_quick_analysis():
    """Test quick complexity analysis"""
    print("=" * 60)
    print("Testing Quick Complexity Analysis")
    print("=" * 60)
    
    try:
        result = await ai_service.analyze_complexity_quick(
            problem_description=None,
            code=SAMPLE_CODE,
            language="python"
        )
        
        print(f"\n✓ Quick Analysis Result:")
        print(f"  Time Complexity: {result.time_complexity}")
        print(f"  Space Complexity: {result.space_complexity}")
        if result.inferred_problem:
            print(f"  Inferred Problem: {result.inferred_problem}")
        
        return result
    except Exception as e:
        print(f"\n✗ Quick Analysis Failed: {e}")
        return None

async def test_explanation(time_complexity, space_complexity):
    """Test detailed explanation"""
    print("\n" + "=" * 60)
    print("Testing Detailed Explanation")
    print("=" * 60)
    
    try:
        result = await ai_service.explain_complexity(
            problem_description=None,
            code=SAMPLE_CODE,
            language="python",
            time_complexity=time_complexity,
            space_complexity=space_complexity
        )
        
        print(f"\n✓ Explanation Result:")
        print(f"  Explanation: {result.explanation[:200]}...")
        print(f"  Key Operations: {len(result.key_operations)} operations")
        if result.improvements:
            print(f"  Improvements: {len(result.improvements)} suggestions")
        
        return result
    except Exception as e:
        print(f"\n✗ Explanation Failed: {e}")
        return None

async def main():
    """Run all tests"""
    print("\n🚀 Starting Two-Stage Complexity Analysis Tests\n")
    
    # Test 1: Quick analysis
    quick_result = await test_quick_analysis()
    if not quick_result:
        print("\n❌ Quick analysis test failed!")
        return
    
    # Test 2: Detailed explanation
    explanation_result = await test_explanation(
        quick_result.time_complexity,
        quick_result.space_complexity
    )
    if not explanation_result:
        print("\n❌ Explanation test failed!")
        return
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    print("\nTwo-stage complexity analysis is working correctly!")
    print(f"Quick analysis returned: {quick_result.time_complexity} time, {quick_result.space_complexity} space")
    print(f"Explanation provided {len(explanation_result.key_operations)} key operations")

if __name__ == "__main__":
    asyncio.run(main())
