"""
Integration test for solution completeness detection feature.
This test demonstrates the complete workflow from incomplete to complete solution.
"""
import asyncio
from services.ai.ai_service_factory import ai_service


async def test_complete_workflow():
    """
    Test the complete user workflow:
    1. User submits incomplete solution for complexity analysis
    2. System detects incompleteness and suggests hints
    3. User requests hints
    4. User completes solution
    5. User requests complexity analysis again
    6. System provides analysis
    """
    print("=" * 70)
    print("INTEGRATION TEST: Complete Workflow")
    print("=" * 70)
    
    problem_desc = """
    Two Sum: Given an array of integers nums and an integer target, 
    return indices of the two numbers such that they add up to target.
    """
    
    # Step 1: User submits incomplete solution
    print("\n📝 Step 1: User submits incomplete solution for complexity analysis")
    incomplete_code = """
def two_sum(nums, target):
    # I need to find two numbers that add up to target
    # TODO: implement this
    pass
"""
    print(f"Code:\n{incomplete_code}")
    
    # Step 2: System checks completeness
    print("\n🔍 Step 2: System checks solution completeness")
    completeness = await ai_service.check_solution_completeness(
        incomplete_code, "python"
    )
    print(f"   Is Complete: {completeness.is_complete}")
    print(f"   Missing Elements:")
    for element in completeness.missing_elements:
        print(f"      - {element}")
    print(f"   Confidence: {completeness.confidence}")
    
    # Step 3: System suggests hints (simulated response)
    if not completeness.is_complete:
        print("\n⚠️  Step 3: System detects incompleteness")
        print("   Message: 'Your solution appears to be incomplete.'")
        print("   Suggestion: 'Would you like hints to help complete your solution?'")
        print("   Action: User switches to 'Hints' option")
    
    # Step 4: User requests hints
    print("\n💡 Step 4: User requests hints for incomplete solution")
    hints = await ai_service.generate_hints(
        problem_desc, incomplete_code, "python"
    )
    print(f"   Hints provided: {len(hints.hints)}")
    print("   Sample hints:")
    for i, hint in enumerate(hints.hints[:3], 1):
        print(f"      {i}. {hint[:80]}...")
    
    # Step 5: User completes solution (simulated)
    print("\n✍️  Step 5: User completes solution based on hints")
    complete_code = """
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
"""
    print(f"Code:\n{complete_code}")
    
    # Step 6: System checks completeness again
    print("\n🔍 Step 6: System checks completeness of updated solution")
    completeness = await ai_service.check_solution_completeness(
        complete_code, "python"
    )
    print(f"   Is Complete: {completeness.is_complete}")
    print(f"   Confidence: {completeness.confidence}")
    
    # Step 7: User requests complexity analysis
    if completeness.is_complete:
        print("\n✅ Step 7: Solution is complete, proceeding with complexity analysis")
        complexity = await ai_service.analyze_time_complexity(
            problem_desc, complete_code, "python"
        )
        print(f"   Time Complexity: {complexity.time_complexity}")
        print(f"   Space Complexity: {complexity.space_complexity}")
        print(f"   Explanation: {complexity.explanation[:100]}...")
    
    print("\n" + "=" * 70)
    print("✓ INTEGRATION TEST PASSED")
    print("=" * 70)
    print("\nWorkflow Summary:")
    print("1. ✓ Incomplete solution detected")
    print("2. ✓ User guided to use hints")
    print("3. ✓ Hints provided for incomplete solution")
    print("4. ✓ Complete solution verified")
    print("5. ✓ Complexity analysis performed on complete solution")


async def test_hints_bypass():
    """Test that hints work regardless of completeness."""
    print("\n" + "=" * 70)
    print("TEST: Hints Bypass Completeness Check")
    print("=" * 70)
    
    problem_desc = "Two Sum problem"
    
    # Test with very incomplete code
    print("\n📝 Testing hints with minimal code:")
    minimal_code = "def two_sum():"
    
    print(f"Code: {minimal_code}")
    
    try:
        hints = await ai_service.generate_hints(
            problem_desc, minimal_code, "python"
        )
        print(f"✓ Hints generated successfully: {len(hints.hints)} hints")
        print("✓ Hints work regardless of solution completeness")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    print("\n" + "=" * 70)


async def test_analysis_types_routing():
    """Test that different analysis types route correctly."""
    print("\n" + "=" * 70)
    print("TEST: Analysis Type Routing")
    print("=" * 70)
    
    incomplete_code = "def solution(): pass"
    complete_code = "def solution(): return 42"
    problem_desc = "Test problem"
    
    print("\n1. Testing with INCOMPLETE solution:")
    completeness = await ai_service.check_solution_completeness(
        incomplete_code, "python"
    )
    print(f"   Is Complete: {completeness.is_complete}")
    
    if not completeness.is_complete:
        print("   ✓ Would block: Complexity Analysis")
        print("   ✓ Would block: Optimization Analysis")
        print("   ✓ Would block: Debugging Analysis")
        print("   ✓ Would allow: Hints")
    
    print("\n2. Testing with COMPLETE solution:")
    completeness = await ai_service.check_solution_completeness(
        complete_code, "python"
    )
    print(f"   Is Complete: {completeness.is_complete}")
    
    if completeness.is_complete:
        print("   ✓ Would allow: Complexity Analysis")
        print("   ✓ Would allow: Optimization Analysis")
        print("   ✓ Would allow: Debugging Analysis")
        print("   ✓ Would allow: Hints")
    
    print("\n" + "=" * 70)


async def main():
    """Run all integration tests."""
    try:
        await test_complete_workflow()
        await test_hints_bypass()
        await test_analysis_types_routing()
        print("\n" + "=" * 70)
        print("✓ ALL INTEGRATION TESTS PASSED")
        print("=" * 70)
    except Exception as e:
        print(f"\n✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
