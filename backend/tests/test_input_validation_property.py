"""
Property-Based Test for Input Validation Workflow

**Property 3: Input Validation Workflow**
*For any* combination of problem URL and solution code inputs, the system should 
validate both inputs together before allowing analysis to proceed

**Validates: Requirements 1.4, 9.1**

This test uses Hypothesis for property-based testing to verify that the validation
service correctly handles all combinations of valid and invalid inputs.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hypothesis import given, strategies as st, settings, example
from services.validation_service import validation_service


# Custom strategies for generating test data
@st.composite
def valid_leetcode_urls(draw):
    """Strategy for generating valid LeetCode URLs."""
    problem_slugs = [
        "two-sum", "add-two-numbers", "longest-substring-without-repeating-characters",
        "median-of-two-sorted-arrays", "longest-palindromic-substring",
        "zigzag-conversion", "reverse-integer", "string-to-integer-atoi",
        "palindrome-number", "regular-expression-matching", "container-with-most-water"
    ]
    
    protocol = draw(st.sampled_from(["https://", "http://"]))
    subdomain = draw(st.sampled_from(["", "www."]))
    slug = draw(st.sampled_from(problem_slugs))
    suffix = draw(st.sampled_from(["", "/", "/description/", "/solutions/", "/editorial/"]))
    
    return f"{protocol}{subdomain}leetcode.com/problems/{slug}{suffix}"


@st.composite
def invalid_leetcode_urls(draw):
    """Strategy for generating invalid LeetCode URLs."""
    invalid_patterns = st.sampled_from([
        "",  # Empty
        "not-a-url",  # Not a URL
        "https://google.com",  # Wrong domain
        "https://leetcode.com",  # Missing /problems/
        "https://leetcode.com/problems/",  # Missing slug
        "leetcode.com/problems/two-sum",  # Missing protocol
        "ftp://leetcode.com/problems/two-sum/",  # Wrong protocol
        "https://leetcode.org/problems/two-sum/",  # Wrong TLD
    ])
    
    return draw(invalid_patterns)


@st.composite
def valid_code_samples(draw):
    """Strategy for generating valid code samples."""
    python_templates = [
        "def solution(nums):\n    return sum(nums)",
        "def twoSum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        if target - num in seen:\n            return [seen[target - num], i]\n        seen[num] = i\n    return []",
        "class Solution:\n    def solve(self, arr):\n        return sorted(arr)",
        "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
    ]
    
    return draw(st.sampled_from(python_templates))


@st.composite
def invalid_code_samples(draw):
    """Strategy for generating invalid code samples."""
    invalid_patterns = st.sampled_from([
        "",  # Empty
        "x",  # Too short
        "def test(",  # Mismatched parentheses
        "   ",  # Only whitespace
        "def",  # Incomplete
    ])
    
    return draw(invalid_patterns)


valid_languages = st.sampled_from(["python", "javascript", "typescript", "java", "cpp", "c", "go", "rust"])
invalid_languages = st.sampled_from(["", "brainfuck", "cobol", "fortran", "assembly"])

valid_analysis_types = st.sampled_from(["complexity", "hints", "optimization", "debugging"])
invalid_analysis_types = st.sampled_from(["", "invalid", "test", "analyze", "complexity-analysis"])


class TestInputValidationProperty:
    """Property-based tests for input validation using Hypothesis."""
    
    @given(valid_leetcode_urls())
    @settings(max_examples=50)
    @example("https://leetcode.com/problems/two-sum/")
    @example("https://www.leetcode.com/problems/add-two-numbers/description/")
    def test_property_valid_urls_always_validate(self, url):
        """
        Property: All valid LeetCode URLs should pass validation.
        """
        result = validation_service.validate_problem_url(url)
        assert result.is_valid, f"Valid URL failed validation: {url}\nErrors: {[e.message for e in result.errors]}"
    
    @given(invalid_leetcode_urls())
    @settings(max_examples=50)
    @example("")
    @example("not-a-url")
    def test_property_invalid_urls_always_fail(self, url):
        """
        Property: All invalid LeetCode URLs should fail validation with helpful errors.
        """
        result = validation_service.validate_problem_url(url)
        assert not result.is_valid, f"Invalid URL passed validation: {url}"
        assert len(result.errors) > 0, f"Invalid URL had no error messages: {url}"
        
        # Check that errors have required fields
        for error in result.errors:
            assert error.message, f"Error missing message for URL: {url}"
            assert error.suggestion, f"Error missing suggestion for URL: {url}"
    
    @given(valid_code_samples(), valid_languages)
    @settings(max_examples=50)
    @example("def solution(): return 42", "python")
    def test_property_valid_code_validates(self, code, language):
        """
        Property: All valid code samples should pass validation.
        """
        result = validation_service.validate_code(code, language)
        assert result.is_valid, f"Valid code failed validation\nCode: {code[:50]}...\nLanguage: {language}\nErrors: {[e.message for e in result.errors]}"
    
    @given(invalid_code_samples(), valid_languages)
    @settings(max_examples=50)
    @example("", "python")
    @example("x", "python")
    def test_property_invalid_code_fails(self, code, language):
        """
        Property: All invalid code samples should fail validation with helpful errors.
        """
        result = validation_service.validate_code(code, language)
        assert not result.is_valid, f"Invalid code passed validation: {code[:50]}"
        assert len(result.errors) > 0, f"Invalid code had no error messages: {code[:50]}"
        
        # Check that errors have required fields
        for error in result.errors:
            assert error.message, f"Error missing message for code: {code[:30]}"
            assert error.suggestion, f"Error missing suggestion for code: {code[:30]}"
    
    @given(invalid_languages)
    @settings(max_examples=30)
    @example("")
    @example("brainfuck")
    def test_property_invalid_languages_fail(self, language):
        """
        Property: All invalid languages should fail validation with helpful errors.
        """
        result = validation_service.validate_language(language)
        assert not result.is_valid, f"Invalid language passed validation: {language}"
        assert len(result.errors) > 0, f"Invalid language had no error messages: {language}"
        
        # Check that errors include examples of valid languages
        for error in result.errors:
            assert error.examples, f"Error missing examples for language: {language}"
    
    @given(invalid_analysis_types)
    @settings(max_examples=30)
    @example("")
    @example("invalid")
    def test_property_invalid_analysis_types_fail(self, analysis_type):
        """
        Property: All invalid analysis types should fail validation with helpful errors.
        """
        result = validation_service.validate_analysis_type(analysis_type)
        assert not result.is_valid, f"Invalid analysis type passed validation: {analysis_type}"
        assert len(result.errors) > 0, f"Invalid analysis type had no error messages: {analysis_type}"
        
        # Check that errors include examples of valid types
        for error in result.errors:
            assert error.examples, f"Error missing examples for analysis type: {analysis_type}"
    
    @given(
        st.one_of(valid_leetcode_urls(), invalid_leetcode_urls()),
        st.one_of(valid_code_samples(), invalid_code_samples()),
        st.one_of(valid_languages, invalid_languages),
        st.one_of(valid_analysis_types, invalid_analysis_types)
    )
    @settings(max_examples=100)
    def test_property_comprehensive_validation_consistency(self, url, code, language, analysis_type):
        """
        Property: Comprehensive validation should be consistent with individual validations.
        If any individual validation fails, comprehensive validation should fail.
        """
        # Individual validations
        url_result = validation_service.validate_problem_url(url)
        code_result = validation_service.validate_code(code, language)
        lang_result = validation_service.validate_language(language)
        analysis_result = validation_service.validate_analysis_type(analysis_type)
        
        # Comprehensive validation
        comprehensive_result = validation_service.validate_analysis_request(
            url, code, language, analysis_type
        )
        
        # Check consistency
        individual_valid = (
            url_result.is_valid and 
            code_result.is_valid and 
            lang_result.is_valid and 
            analysis_result.is_valid
        )
        
        assert individual_valid == comprehensive_result.is_valid, \
            f"Inconsistency detected:\n" \
            f"URL valid: {url_result.is_valid}\n" \
            f"Code valid: {code_result.is_valid}\n" \
            f"Language valid: {lang_result.is_valid}\n" \
            f"Analysis valid: {analysis_result.is_valid}\n" \
            f"Comprehensive valid: {comprehensive_result.is_valid}"
    
    @given(valid_leetcode_urls())
    @settings(max_examples=20)
    def test_property_validation_idempotent(self, url):
        """
        Property: Validation should be idempotent - validating the same input multiple times
        should always produce the same result.
        """
        # Validate 5 times
        results = [validation_service.validate_problem_url(url).is_valid for _ in range(5)]
        
        # All results should be the same
        assert len(set(results)) == 1, f"Non-idempotent validation for URL: {url}\nResults: {results}"
    
    @given(
        st.one_of(invalid_leetcode_urls(), invalid_code_samples(), invalid_languages, invalid_analysis_types)
    )
    @settings(max_examples=50)
    def test_property_all_errors_have_suggestions(self, invalid_input):
        """
        Property: All validation errors should include actionable suggestions.
        """
        # Try validating as different types
        results = [
            validation_service.validate_problem_url(invalid_input),
            validation_service.validate_code(invalid_input, "python"),
            validation_service.validate_language(invalid_input),
            validation_service.validate_analysis_type(invalid_input),
        ]
        
        # Check all errors from all validations
        for result in results:
            for error in result.errors:
                assert error.message, f"Error missing message for input: {invalid_input[:50]}"
                assert error.suggestion, f"Error missing suggestion for input: {invalid_input[:50]}"


def run_all_property_tests():
    """Run all property-based tests."""
    print("\n" + "=" * 80)
    print(" " * 20 + "PROPERTY-BASED VALIDATION TESTS")
    print(" " * 15 + "Property 3: Input Validation Workflow")
    print(" " * 20 + "Validates: Requirements 1.4, 9.1")
    print("=" * 80)
    
    test_suite = TestInputValidationProperty()
    
    try:
        print("\n🔍 Testing Property: Valid URLs always validate...")
        test_suite.test_property_valid_urls_always_validate()
        print("✓ Property holds: Valid URLs always validate")
        
        print("\n🔍 Testing Property: Invalid URLs always fail...")
        test_suite.test_property_invalid_urls_always_fail()
        print("✓ Property holds: Invalid URLs always fail with errors")
        
        print("\n🔍 Testing Property: Valid code validates...")
        test_suite.test_property_valid_code_validates()
        print("✓ Property holds: Valid code always validates")
        
        print("\n🔍 Testing Property: Invalid code fails...")
        test_suite.test_property_invalid_code_fails()
        print("✓ Property holds: Invalid code always fails with errors")
        
        print("\n🔍 Testing Property: Invalid languages fail...")
        test_suite.test_property_invalid_languages_fail()
        print("✓ Property holds: Invalid languages always fail with examples")
        
        print("\n🔍 Testing Property: Invalid analysis types fail...")
        test_suite.test_property_invalid_analysis_types_fail()
        print("✓ Property holds: Invalid analysis types always fail with examples")
        
        print("\n🔍 Testing Property: Comprehensive validation consistency...")
        test_suite.test_property_comprehensive_validation_consistency()
        print("✓ Property holds: Comprehensive validation is consistent")
        
        print("\n🔍 Testing Property: Validation is idempotent...")
        test_suite.test_property_validation_idempotent()
        print("✓ Property holds: Validation is idempotent")
        
        print("\n🔍 Testing Property: All errors have suggestions...")
        test_suite.test_property_all_errors_have_suggestions()
        print("✓ Property holds: All errors have actionable suggestions")
        
        print("\n" + "=" * 80)
        print(" " * 25 + "✓ ALL PROPERTY TESTS PASSED")
        print("=" * 80)
        print("\nProperty Summary:")
        print("✓ Valid URLs always validate (50 examples)")
        print("✓ Invalid URLs always fail with errors (50 examples)")
        print("✓ Valid code always validates (50 examples)")
        print("✓ Invalid code always fails with errors (50 examples)")
        print("✓ Invalid languages fail with examples (30 examples)")
        print("✓ Invalid analysis types fail with examples (30 examples)")
        print("✓ Comprehensive validation is consistent (100 examples)")
        print("✓ Validation is idempotent (20 examples)")
        print("✓ All errors have suggestions (50 examples)")
        print(f"\nTotal test cases generated: 380+")
        return True
        
    except AssertionError as e:
        print(f"\n❌ Property test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_property_tests()
    exit(0 if success else 1)
