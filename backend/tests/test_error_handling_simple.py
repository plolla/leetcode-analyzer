"""
Simple tests for comprehensive error handling implementation.
Tests validation service and rate limiting without pytest.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.validation_service import validation_service, ValidationErrorType
from services.ai.ai_service_factory import RateLimiter


def test_valid_leetcode_url():
    """Test validation of valid LeetCode URLs."""
    print("Testing valid LeetCode URLs...")
    valid_urls = [
        "https://leetcode.com/problems/two-sum/",
        "https://leetcode.com/problems/reverse-linked-list/description/",
    ]
    
    for url in valid_urls:
        result = validation_service.validate_problem_url(url)
        assert result.is_valid, f"URL should be valid: {url}"
        assert len(result.errors) == 0
    print("✓ Valid URL test passed")


def test_invalid_leetcode_url():
    """Test validation of invalid LeetCode URLs."""
    print("Testing invalid LeetCode URLs...")
    result = validation_service.validate_problem_url("invalid-url")
    
    assert not result.is_valid
    assert len(result.errors) == 1
    assert result.errors[0].error_type == ValidationErrorType.INVALID_URL
    assert result.errors[0].suggestion is not None
    assert result.errors[0].examples is not None
    print(f"✓ Invalid URL test passed - Error: {result.errors[0].message}")


def test_valid_code():
    """Test validation of valid code."""
    print("Testing valid code...")
    code = """
def twoSum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
"""
    result = validation_service.validate_code(code, "python")
    
    assert result.is_valid
    assert len(result.errors) == 0
    print("✓ Valid code test passed")


def test_empty_code():
    """Test validation of empty code."""
    print("Testing empty code...")
    result = validation_service.validate_code("", "python")
    
    assert not result.is_valid
    assert len(result.errors) == 1
    assert result.errors[0].error_type == ValidationErrorType.EMPTY_CODE
    print(f"✓ Empty code test passed - Error: {result.errors[0].message}")


def test_code_with_syntax_error():
    """Test validation of code with syntax errors."""
    print("Testing code with syntax errors...")
    code = "def solution(nums):\n    return sum(nums"
    result = validation_service.validate_code(code, "python")
    
    assert not result.is_valid
    assert any(err.error_type == ValidationErrorType.SYNTAX_ERROR for err in result.errors)
    print(f"✓ Syntax error test passed - Found {len(result.errors)} error(s)")


def test_valid_language():
    """Test validation of supported languages."""
    print("Testing valid languages...")
    languages = ["python", "javascript", "java", "cpp", "typescript"]
    
    for lang in languages:
        result = validation_service.validate_language(lang)
        assert result.is_valid, f"Language should be valid: {lang}"
    print(f"✓ Valid language test passed - Tested {len(languages)} languages")


def test_invalid_language():
    """Test validation of unsupported language."""
    print("Testing invalid language...")
    result = validation_service.validate_language("cobol")
    
    assert not result.is_valid
    assert len(result.errors) == 1
    assert result.errors[0].error_type == ValidationErrorType.INVALID_LANGUAGE
    assert result.errors[0].examples is not None
    print(f"✓ Invalid language test passed - Suggested: {result.errors[0].examples[:3]}")


def test_rate_limiter():
    """Test rate limiting functionality."""
    print("Testing rate limiter...")
    limiter = RateLimiter(max_calls_per_minute=2)
    
    # First two calls should succeed
    allowed1, _ = limiter.check_rate_limit("test_client")
    allowed2, _ = limiter.check_rate_limit("test_client")
    
    assert allowed1 is True
    assert allowed2 is True
    
    # Third call should be rate limited
    allowed3, wait = limiter.check_rate_limit("test_client")
    
    assert allowed3 is False
    assert wait is not None
    assert wait > 0
    print(f"✓ Rate limiter test passed - Blocked after 2 calls, wait time: {wait}s")


def test_complete_validation():
    """Test validation of complete analysis request."""
    print("Testing complete analysis request validation...")
    result = validation_service.validate_analysis_request(
        problem_url="https://leetcode.com/problems/two-sum/",
        code="def solution(): return 42",
        language="python",
        analysis_type="complexity"
    )
    
    assert result.is_valid
    assert len(result.errors) == 0
    print("✓ Complete validation test passed")


def test_multiple_errors():
    """Test validation with multiple errors."""
    print("Testing multiple validation errors...")
    result = validation_service.validate_analysis_request(
        problem_url="invalid",
        code="",
        language="invalid",
        analysis_type="invalid"
    )
    
    assert not result.is_valid
    assert len(result.errors) >= 3
    print(f"✓ Multiple errors test passed - Found {len(result.errors)} errors")
    for error in result.errors:
        print(f"  - {error.field}: {error.message}")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("Running Error Handling Tests")
    print("="*60 + "\n")
    
    tests = [
        test_valid_leetcode_url,
        test_invalid_leetcode_url,
        test_valid_code,
        test_empty_code,
        test_code_with_syntax_error,
        test_valid_language,
        test_invalid_language,
        test_rate_limiter,
        test_complete_validation,
        test_multiple_errors,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
        print()
    
    print("="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
