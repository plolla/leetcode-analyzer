"""
Checkpoint 12: End-to-End Test for Core Analysis Features

This test verifies:
1. All four analysis types work end-to-end
2. Completeness detection and routing works correctly
3. Error handling works as expected
"""
import asyncio
from services.ai.ai_service_factory import ai_service
from services.leetcode_parser import leetcode_parser


async def test_time_complexity_analysis():
    """Test 1: Time Complexity Analysis"""
    print("\n" + "=" * 70)
    print("TEST 1: Time Complexity Analysis")
    print("=" * 70)
    
    problem_desc = """
    Two Sum: Given an array of integers nums and an integer target, 
    return indices of the two numbers such that they add up to target.
    """
    
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
    
    print("\n📝 Testing time complexity analysis with complete solution...")
    print(f"Code:\n{complete_code}")
    
    try:
        result = await ai_service.analyze_time_complexity(
            problem_description=problem_desc,
            code=complete_code,
            language="python"
        )
        
        print("\n✓ Time Complexity Analysis Successful!")
        print(f"   Time Complexity: {result.time_complexity}")
        print(f"   Space Complexity: {result.space_complexity}")
        print(f"   Explanation: {result.explanation[:100]}...")
        print(f"   Key Operations: {len(result.key_operations)} identified")
        
        # Verify result structure
        assert result.time_complexity, "Time complexity should not be empty"
        assert result.space_complexity, "Space complexity should not be empty"
        assert result.explanation, "Explanation should not be empty"
        assert isinstance(result.key_operations, list), "Key operations should be a list"
        
        return True
    except Exception as e:
        print(f"\n✗ Time Complexity Analysis Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_hints_generation():
    """Test 2: Hints Generation"""
    print("\n" + "=" * 70)
    print("TEST 2: Hints Generation")
    print("=" * 70)
    
    problem_desc = """
    Two Sum: Given an array of integers nums and an integer target, 
    return indices of the two numbers such that they add up to target.
    """
    
    incomplete_code = """
def two_sum(nums, target):
    # I'm stuck, need help
    for i in range(len(nums)):
        pass
"""
    
    print("\n📝 Testing hint generation with incomplete solution...")
    print(f"Code:\n{incomplete_code}")
    
    try:
        result = await ai_service.generate_hints(
            problem_description=problem_desc,
            code=incomplete_code,
            language="python"
        )
        
        print("\n✓ Hint Generation Successful!")
        print(f"   Progressive: {result.progressive}")
        print(f"   Number of Hints: {len(result.hints)}")
        print(f"   Number of Next Steps: {len(result.next_steps)}")
        
        if result.hints:
            print(f"   First Hint: {result.hints[0][:80]}...")
        
        # Verify result structure
        assert isinstance(result.hints, list), "Hints should be a list"
        assert len(result.hints) > 0, "Should provide at least one hint"
        assert isinstance(result.next_steps, list), "Next steps should be a list"
        assert isinstance(result.progressive, bool), "Progressive should be a boolean"
        
        return True
    except Exception as e:
        print(f"\n✗ Hint Generation Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_optimization_analysis():
    """Test 3: Optimization Analysis"""
    print("\n" + "=" * 70)
    print("TEST 3: Optimization Analysis")
    print("=" * 70)
    
    problem_desc = """
    Two Sum: Given an array of integers nums and an integer target, 
    return indices of the two numbers such that they add up to target.
    """
    
    # Suboptimal solution (nested loops)
    suboptimal_code = """
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""
    
    print("\n📝 Testing optimization analysis with suboptimal solution...")
    print(f"Code:\n{suboptimal_code}")
    
    try:
        result = await ai_service.optimize_solution(
            problem_description=problem_desc,
            code=suboptimal_code,
            language="python"
        )
        
        print("\n✓ Optimization Analysis Successful!")
        print(f"   Current Complexity: {result.current_complexity}")
        print(f"   Optimized Complexity: {result.optimized_complexity}")
        print(f"   Number of Suggestions: {len(result.suggestions)}")
        
        if result.suggestions:
            print(f"   First Suggestion Area: {result.suggestions[0].area}")
            print(f"   Impact: {result.suggestions[0].impact}")
        
        # Verify result structure
        assert result.current_complexity, "Current complexity should not be empty"
        assert result.optimized_complexity, "Optimized complexity should not be empty"
        assert isinstance(result.suggestions, list), "Suggestions should be a list"
        assert len(result.suggestions) > 0, "Should provide at least one suggestion"
        
        return True
    except Exception as e:
        print(f"\n✗ Optimization Analysis Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_debugging_analysis():
    """Test 4: Debugging Analysis"""
    print("\n" + "=" * 70)
    print("TEST 4: Debugging Analysis")
    print("=" * 70)
    
    problem_desc = """
    Two Sum: Given an array of integers nums and an integer target, 
    return indices of the two numbers such that they add up to target.
    """
    
    # Code with a bug (off-by-one error)
    buggy_code = """
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i, len(nums)):  # Bug: should be i+1
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""
    
    print("\n📝 Testing debugging analysis with buggy solution...")
    print(f"Code:\n{buggy_code}")
    
    try:
        result = await ai_service.debug_solution(
            problem_description=problem_desc,
            code=buggy_code,
            language="python"
        )
        
        print("\n✓ Debugging Analysis Successful!")
        print(f"   Issues Found: {len(result.issues)}")
        print(f"   Fixes Suggested: {len(result.fixes)}")
        print(f"   Test Cases: {len(result.test_cases)}")
        
        if result.issues:
            print(f"   First Issue: {result.issues[0].description[:80]}...")
        
        # Verify result structure
        assert isinstance(result.issues, list), "Issues should be a list"
        assert isinstance(result.fixes, list), "Fixes should be a list"
        assert isinstance(result.test_cases, list), "Test cases should be a list"
        
        return True
    except Exception as e:
        print(f"\n✗ Debugging Analysis Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_completeness_detection():
    """Test 5: Completeness Detection and Routing"""
    print("\n" + "=" * 70)
    print("TEST 5: Completeness Detection and Routing")
    print("=" * 70)
    
    incomplete_code = """
def two_sum(nums, target):
    # TODO: implement this
    pass
"""
    
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
    
    print("\n📝 Testing completeness detection...")
    
    try:
        # Test 1: Incomplete solution
        print("\n   1. Testing incomplete solution:")
        result_incomplete = await ai_service.check_solution_completeness(
            incomplete_code, "python"
        )
        print(f"      Is Complete: {result_incomplete.is_complete}")
        print(f"      Missing Elements: {len(result_incomplete.missing_elements)}")
        print(f"      Confidence: {result_incomplete.confidence}")
        
        assert not result_incomplete.is_complete, "Should detect incomplete solution"
        
        # Test 2: Complete solution
        print("\n   2. Testing complete solution:")
        result_complete = await ai_service.check_solution_completeness(
            complete_code, "python"
        )
        print(f"      Is Complete: {result_complete.is_complete}")
        print(f"      Confidence: {result_complete.confidence}")
        
        assert result_complete.is_complete, "Should detect complete solution"
        
        # Test 3: Verify hints work with incomplete solutions
        print("\n   3. Verifying hints work with incomplete solutions:")
        problem_desc = "Two Sum problem"
        hints = await ai_service.generate_hints(
            problem_desc, incomplete_code, "python"
        )
        print(f"      ✓ Hints generated: {len(hints.hints)} hints")
        
        print("\n✓ Completeness Detection and Routing Successful!")
        return True
        
    except Exception as e:
        print(f"\n✗ Completeness Detection Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_error_handling():
    """Test 6: Error Handling"""
    print("\n" + "=" * 70)
    print("TEST 6: Error Handling")
    print("=" * 70)
    
    print("\n📝 Testing error handling scenarios...")
    
    try:
        # Test 1: Empty code
        print("\n   1. Testing with empty code:")
        try:
            result = await ai_service.check_solution_completeness("", "python")
            print(f"      Result: {result.is_complete}")
            print("      ✓ Handled empty code gracefully")
        except Exception as e:
            print(f"      ✓ Caught error: {str(e)[:50]}...")
        
        # Test 2: Invalid language
        print("\n   2. Testing with unsupported language:")
        code = "function test() { return 42; }"
        try:
            result = await ai_service.analyze_time_complexity(
                "Test problem", code, "unsupported_lang"
            )
            print("      ✓ Handled unsupported language")
        except Exception as e:
            print(f"      ✓ Caught error: {str(e)[:50]}...")
        
        # Test 3: LeetCode URL parsing
        print("\n   3. Testing LeetCode URL parsing:")
        valid_url = "https://leetcode.com/problems/two-sum/"
        invalid_url = "https://example.com/not-leetcode"
        
        valid_slug = leetcode_parser.extract_problem_slug(valid_url)
        invalid_slug = leetcode_parser.extract_problem_slug(invalid_url)
        
        print(f"      Valid URL slug: {valid_slug}")
        print(f"      Invalid URL slug: {invalid_slug}")
        
        assert valid_slug == "two-sum", "Should extract correct slug"
        assert invalid_slug is None, "Should return None for invalid URL"
        print("      ✓ URL parsing works correctly")
        
        print("\n✓ Error Handling Tests Successful!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error Handling Tests Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_leetcode_parser():
    """Test 7: LeetCode Problem Parsing"""
    print("\n" + "=" * 70)
    print("TEST 7: LeetCode Problem Parsing")
    print("=" * 70)
    
    print("\n📝 Testing LeetCode problem parsing...")
    
    try:
        # Test URL extraction
        test_urls = [
            ("https://leetcode.com/problems/two-sum/", "two-sum"),
            ("https://leetcode.com/problems/add-two-numbers/description/", "add-two-numbers"),
            ("https://leetcode.com/problems/longest-substring-without-repeating-characters", "longest-substring-without-repeating-characters"),
            ("https://example.com/invalid", None),
        ]
        
        print("\n   Testing URL slug extraction:")
        for url, expected_slug in test_urls:
            slug = leetcode_parser.extract_problem_slug(url)
            status = "✓" if slug == expected_slug else "✗"
            print(f"      {status} {url[:50]}... -> {slug}")
            assert slug == expected_slug, f"Expected {expected_slug}, got {slug}"
        
        print("\n✓ LeetCode Parser Tests Successful!")
        return True
        
    except Exception as e:
        print(f"\n✗ LeetCode Parser Tests Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all checkpoint tests."""
    print("\n" + "=" * 70)
    print("CHECKPOINT 12: CORE ANALYSIS FEATURES VERIFICATION")
    print("=" * 70)
    print("\nThis test suite verifies:")
    print("  1. Time Complexity Analysis")
    print("  2. Hints Generation")
    print("  3. Optimization Analysis")
    print("  4. Debugging Analysis")
    print("  5. Completeness Detection and Routing")
    print("  6. Error Handling")
    print("  7. LeetCode Problem Parsing")
    
    results = []
    
    # Run all tests
    results.append(("Time Complexity Analysis", await test_time_complexity_analysis()))
    results.append(("Hints Generation", await test_hints_generation()))
    results.append(("Optimization Analysis", await test_optimization_analysis()))
    results.append(("Debugging Analysis", await test_debugging_analysis()))
    results.append(("Completeness Detection", await test_completeness_detection()))
    results.append(("Error Handling", await test_error_handling()))
    results.append(("LeetCode Parser", await test_leetcode_parser()))
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Total: {passed + failed} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 70)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Core analysis features are working correctly.")
        print("\nCheckpoint 12 Status: ✓ COMPLETE")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the errors above.")
        print("\nCheckpoint 12 Status: ✗ INCOMPLETE")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
