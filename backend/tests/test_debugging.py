"""
Test script for debugging analysis feature.
"""
import asyncio
from services.ai.ai_service_factory import ai_service

async def test_debugging():
    """Test the debugging analysis functionality."""
    
    # Sample problem description
    problem_description = """
    Two Sum: Given an array of integers nums and an integer target, 
    return indices of the two numbers such that they add up to target.
    """
    
    # Sample code with a bug (off-by-one error)
    buggy_code = """
def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i, len(nums)):  # Bug: should be i+1
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""
    
    print("Testing debugging analysis...")
    print(f"Problem: {problem_description.strip()}")
    print(f"\nCode:\n{buggy_code}")
    print("\n" + "="*60)
    print("Running AI debugging analysis...")
    print("="*60 + "\n")
    
    try:
        result = await ai_service.debug_solution(
            problem_description=problem_description,
            code=buggy_code,
            language="python"
        )
        
        print("✓ Debugging analysis completed successfully!\n")
        print(f"Issues found: {len(result.issues)}")
        
        for i, issue in enumerate(result.issues, 1):
            print(f"\nIssue {i}:")
            print(f"  Line: {issue.line if issue.line else 'N/A'}")
            print(f"  Severity: {issue.severity}")
            print(f"  Description: {issue.description}")
        
        print(f"\nFixes suggested: {len(result.fixes)}")
        for i, fix in enumerate(result.fixes, 1):
            print(f"\nFix {i}:")
            print(f"  Issue: {fix.issue}")
            print(f"  Suggestion: {fix.suggestion}")
            if fix.code_example:
                print(f"  Code Example: {fix.code_example}")
        
        print(f"\nTest cases: {len(result.test_cases)}")
        for i, test_case in enumerate(result.test_cases, 1):
            print(f"  {i}. {test_case}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during debugging analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_debugging())
    exit(0 if success else 1)
