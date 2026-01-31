"""
Tests for comprehensive error handling implementation.
Tests validation service, rate limiting, and error responses.
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.validation_service import validation_service, ValidationErrorType
from services.ai.ai_service_factory import rate_limiter


class TestValidationService:
    """Test input validation with comprehensive error messages."""
    
    def test_valid_leetcode_url(self):
        """Test validation of valid LeetCode URLs."""
        valid_urls = [
            "https://leetcode.com/problems/two-sum/",
            "https://leetcode.com/problems/reverse-linked-list/description/",
            "https://www.leetcode.com/problems/binary-tree-inorder-traversal/",
        ]
        
        for url in valid_urls:
            result = validation_service.validate_problem_url(url)
            assert result.is_valid, f"URL should be valid: {url}"
            assert len(result.errors) == 0
    
    def test_invalid_leetcode_url(self):
        """Test validation of invalid LeetCode URLs."""
        result = validation_service.validate_problem_url("invalid-url")
        
        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].error_type == ValidationErrorType.INVALID_URL
        assert result.errors[0].suggestion is not None
        assert result.errors[0].examples is not None
    
    def test_empty_url(self):
        """Test validation of empty URL."""
        result = validation_service.validate_problem_url("")
        
        assert not result.is_valid
        assert len(result.errors) == 1
        assert "required" in result.errors[0].message.lower()
    
    def test_url_without_protocol(self):
        """Test URL without http/https protocol."""
        result = validation_service.validate_problem_url("leetcode.com/problems/two-sum/")
        
        assert not result.is_valid
        assert len(result.errors) == 1
        assert "http" in result.errors[0].message.lower()
    
    def test_valid_code(self):
        """Test validation of valid code."""
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
    
    def test_empty_code(self):
        """Test validation of empty code."""
        result = validation_service.validate_code("", "python")
        
        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].error_type == ValidationErrorType.EMPTY_CODE
    
    def test_code_too_short(self):
        """Test validation of code that's too short."""
        result = validation_service.validate_code("x = 1", "python")
        
        assert not result.is_valid
        assert any(err.error_type == ValidationErrorType.CODE_TOO_SHORT for err in result.errors)
    
    def test_code_with_mismatched_parentheses(self):
        """Test validation of code with syntax errors."""
        code = "def solution(nums):\n    return sum(nums"
        result = validation_service.validate_code(code, "python")
        
        assert not result.is_valid
        assert any(err.error_type == ValidationErrorType.SYNTAX_ERROR for err in result.errors)
    
    def test_valid_language(self):
        """Test validation of supported languages."""
        languages = ["python", "javascript", "java", "cpp", "typescript"]
        
        for lang in languages:
            result = validation_service.validate_language(lang)
            assert result.is_valid, f"Language should be valid: {lang}"
    
    def test_invalid_language(self):
        """Test validation of unsupported language."""
        result = validation_service.validate_language("cobol")
        
        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].error_type == ValidationErrorType.INVALID_LANGUAGE
        assert result.errors[0].examples is not None
    
    def test_valid_analysis_type(self):
        """Test validation of valid analysis types."""
        types = ["complexity", "hints", "optimization", "debugging"]
        
        for analysis_type in types:
            result = validation_service.validate_analysis_type(analysis_type)
            assert result.is_valid, f"Analysis type should be valid: {analysis_type}"
    
    def test_invalid_analysis_type(self):
        """Test validation of invalid analysis type."""
        result = validation_service.validate_analysis_type("invalid")
        
        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].error_type == ValidationErrorType.INVALID_ANALYSIS_TYPE
    
    def test_complete_analysis_request_validation(self):
        """Test validation of complete analysis request."""
        result = validation_service.validate_analysis_request(
            problem_url="https://leetcode.com/problems/two-sum/",
            code="def solution(): return 42",
            language="python",
            analysis_type="complexity"
        )
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_analysis_request_with_multiple_errors(self):
        """Test validation with multiple errors."""
        result = validation_service.validate_analysis_request(
            problem_url="invalid",
            code="",
            language="invalid",
            analysis_type="invalid"
        )
        
        assert not result.is_valid
        assert len(result.errors) >= 3  # At least URL, code, and language errors


class TestRateLimiter:
    """Test rate limiting functionality."""
    
    def test_rate_limit_allows_initial_requests(self):
        """Test that initial requests are allowed."""
        limiter = rate_limiter
        limiter.reset("test_client")
        
        allowed, wait = limiter.check_rate_limit("test_client")
        assert allowed is True
        assert wait is None
    
    def test_rate_limit_enforced_after_max_calls(self):
        """Test that rate limit is enforced after max calls."""
        from services.ai.ai_service_factory import RateLimiter
        
        # Create a limiter with low limit for testing
        limiter = RateLimiter(max_calls_per_minute=2)
        
        # First two calls should succeed
        allowed1, _ = limiter.check_rate_limit("test_client_2")
        allowed2, _ = limiter.check_rate_limit("test_client_2")
        
        assert allowed1 is True
        assert allowed2 is True
        
        # Third call should be rate limited
        allowed3, wait = limiter.check_rate_limit("test_client_2")
        
        assert allowed3 is False
        assert wait is not None
        assert wait > 0


class TestErrorMessages:
    """Test error message formatting and suggestions."""
    
    def test_url_error_has_examples(self):
        """Test that URL validation errors include examples."""
        result = validation_service.validate_problem_url("bad-url")
        
        assert not result.is_valid
        assert len(result.errors) > 0
        error = result.errors[0]
        assert error.examples is not None
        assert len(error.examples) > 0
        assert all("leetcode.com" in ex for ex in error.examples)
    
    def test_language_error_has_suggestions(self):
        """Test that language errors include supported languages."""
        result = validation_service.validate_language("unsupported")
        
        assert not result.is_valid
        error = result.errors[0]
        assert error.suggestion is not None
        assert error.examples is not None
        assert "python" in error.examples
    
    def test_error_messages_are_actionable(self):
        """Test that error messages provide actionable guidance."""
        result = validation_service.validate_code("", "python")
        
        assert not result.is_valid
        error = result.errors[0]
        assert error.message is not None
        assert error.suggestion is not None
        assert len(error.suggestion) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
