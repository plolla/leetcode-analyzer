#!/usr/bin/env python3
"""Test script to check GPT-5 responses"""

import json
from services.ai.openai_service import openai_service

def test_hints():
    code = """
def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""
    
    print("Testing hints generation with GPT-5...")
    print("=" * 60)
    
    result = openai_service.generate_hints(
        problem_description=None,
        code=code,
        language="python"
    )
    
    print("\nResult object:")
    print(json.dumps(result.dict(), indent=2))
    
    print("\nHints array:")
    for i, hint in enumerate(result.hints):
        print(f"  Hint {i+1}: {hint[:100]}..." if len(hint) > 100 else f"  Hint {i+1}: {hint}")
    
    print(f"\nNumber of hints: {len(result.hints)}")
    print(f"Progressive: {result.progressive}")
    print(f"Next steps: {result.next_steps}")

if __name__ == "__main__":
    test_hints()
