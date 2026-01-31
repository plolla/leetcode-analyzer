"""
End-to-end integration tests for the LeetCode Analysis Website.
Tests complete user journeys from input to results, history integration, and error scenarios.

Task 18.1: Integrate all components and test end-to-end workflows
- Test complete user journeys from input to results
- Verify history integration works correctly
- Test error scenarios and recovery
"""
import asyncio
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from services.history_service import history_service
from services.cache_service import cache_service


client = TestClient(app)


class TestEndToEndWorkflows:
    """Test complete user workflows from start to finish."""
    
    def setup_method(self):
        """Clear caches and history before each test."""
        cache_service.clear_all()
        # Note: History cleanup would require database access
    
    def test_complete_complexity_analysis_workflow(self):
        """
        Test complete workflow: URL validation -> Problem fetch -> Code input -> Complexity analysis -> History save
        """
        print("\n" + "=" * 70)
        print("TEST: Complete Complexity Analysis Workflow")
        print("=" * 70)
        
        # Step 1: Validate problem URL
        print("\n📝 Step 1: Validate problem URL")
        problem_url = "https://leetcode.com/problems/two-sum/"
        
        response = client.post(
            "/api/validate-url",
            params={"url": problem_url}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["slug"] == "two-sum"
        print(f"   ✓ URL validated: {data['slug']}")
        
        # Step 2: Fetch problem details
        print("\n🔍 Step 2: Fetch problem details")
        response = client.get(f"/api/problem/{data['slug']}")
        assert response.status_code == 200
        problem = response.json()
        assert problem["title"] is not None
        assert problem["difficulty"] in ["Easy", "Medium", "Hard"]
        print(f"   ✓ Problem fetched: {problem['title']} ({problem['difficulty']})")
        
        # Step 3: Validate complete solution code
        print("\n✍️  Step 3: Validate solution code")
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
        language = "python"
        
        response = client.post(
            "/api/validate",
            params={
                "code": code,
                "language": language
            }
        )
        assert response.status_code == 200
        validation = response.json()
        assert validation["validation_results"]["code"]["valid"] is True
        assert validation["validation_results"]["language"]["valid"] is True
        print("   ✓ Code validated successfully")
        
        # Step 4: Request complexity analysis
        print("\n🔬 Step 4: Request complexity analysis")
        response = client.post(
            "/api/analyze",
            json={
                "problem_url": problem_url,
                "code": code,
                "language": language,
                "analysis_type": "complexity"
            }
        )
        assert response.status_code == 200
        result = response.json()
        assert "time_complexity" in result
        assert "space_complexity" in result
        assert "explanation" in result
        print(f"   ✓ Analysis complete: {result['time_complexity']} time, {result['space_complexity']} space")
        
        # Step 5: Verify history was saved
        print("\n📚 Step 5: Verify history was saved")
        response = client.get("/api/history")
        assert response.status_code == 200
        history = response.json()
        assert history["total_count"] > 0
        assert len(history["entries"]) > 0
        
        # Find our entry
        our_entry = None
        for entry in history["entries"]:
            if entry["problem_slug"] == "two-sum" and entry["analysis_type"] == "complexity":
                our_entry = entry
                break
        
        assert our_entry is not None
        assert our_entry["code"] == code
        assert our_entry["language"] == language
        print(f"   ✓ History entry saved: {our_entry['id']}")
        
        print("\n" + "=" * 70)
        print("✓ COMPLETE WORKFLOW TEST PASSED")
        print("=" * 70)
    
    def test_hints_workflow_with_incomplete_solution(self):
        """
        Test workflow: Incomplete solution -> Completeness check -> Hints generation
        """
        print("\n" + "=" * 70)
        print("TEST: Hints Workflow with Incomplete Solution")
        print("=" * 70)
        
        problem_url = "https://leetcode.com/problems/two-sum/"
        incomplete_code = """
def twoSum(nums, target):
    # TODO: implement solution
    pass
"""
        
        # Step 1: Check completeness
        print("\n🔍 Step 1: Check solution completeness")
        response = client.post(
            "/api/check-completeness",
            params={
                "code": incomplete_code,
                "language": "python"
            }
        )
        assert response.status_code == 200
        completeness = response.json()
        assert completeness["is_complete"] is False
        print(f"   ✓ Detected as incomplete (confidence: {completeness['confidence']})")
        
        # Step 2: Request hints (should work regardless of completeness)
        print("\n💡 Step 2: Request hints for incomplete solution")
        response = client.post(
            "/api/analyze",
            json={
                "problem_url": problem_url,
                "code": incomplete_code,
                "language": "python",
                "analysis_type": "hints"
            }
        )
        assert response.status_code == 200
        result = response.json()
        assert "hints" in result
        assert len(result["hints"]) > 0
        print(f"   ✓ Hints generated: {len(result['hints'])} hints provided")
        
        print("\n" + "=" * 70)
        print("✓ HINTS WORKFLOW TEST PASSED")
        print("=" * 70)
    
    def test_completeness_blocking_workflow(self):
        """
        Test that incomplete solutions are blocked from complexity/optimization/debugging analysis.
        """
        print("\n" + "=" * 70)
        print("TEST: Completeness Blocking Workflow")
        print("=" * 70)
        
        problem_url = "https://leetcode.com/problems/two-sum/"
        incomplete_code = "def twoSum(): pass"
        
        # Test each analysis type that requires complete solution
        analysis_types = ["complexity", "optimization", "debugging"]
        
        for analysis_type in analysis_types:
            print(f"\n🔒 Testing {analysis_type} with incomplete solution")
            response = client.post(
                "/api/analyze",
                json={
                    "problem_url": problem_url,
                    "code": incomplete_code,
                    "language": "python",
                    "analysis_type": analysis_type
                }
            )
            assert response.status_code == 200
            result = response.json()
            
            # Should return guidance message, not analysis
            assert "incomplete_solution" in result
            assert result["incomplete_solution"] is True
            assert "message" in result
            assert "suggestion" in result
            print(f"   ✓ {analysis_type.capitalize()} blocked with guidance message")
        
        print("\n" + "=" * 70)
        print("✓ COMPLETENESS BLOCKING TEST PASSED")
        print("=" * 70)
    
    def test_history_retrieval_and_filtering(self):
        """
        Test history retrieval, filtering by problem, and entry management.
        """
        print("\n" + "=" * 70)
        print("TEST: History Retrieval and Filtering")
        print("=" * 70)
        
        # Create multiple analysis entries
        print("\n📝 Step 1: Create multiple analysis entries")
        
        test_cases = [
            ("https://leetcode.com/problems/two-sum/", "def twoSum(): return []", "complexity"),
            ("https://leetcode.com/problems/two-sum/", "def twoSum(): return []", "hints"),
            ("https://leetcode.com/problems/add-two-numbers/", "def addTwoNumbers(): return None", "complexity"),
        ]
        
        for problem_url, code, analysis_type in test_cases:
            response = client.post(
                "/api/analyze",
                json={
                    "problem_url": problem_url,
                    "code": code,
                    "language": "python",
                    "analysis_type": analysis_type
                }
            )
            # May succeed or fail depending on completeness, but should not error
            assert response.status_code in [200, 400, 500]
        
        print("   ✓ Analysis entries created")
        
        # Step 2: Retrieve all history
        print("\n📚 Step 2: Retrieve all history")
        response = client.get("/api/history")
        assert response.status_code == 200
        history = response.json()
        assert "entries" in history
        assert "total_count" in history
        print(f"   ✓ Retrieved {history['total_count']} total entries")
        
        # Step 3: Filter by specific problem
        print("\n🔍 Step 3: Filter history by problem")
        response = client.get("/api/history/two-sum")
        assert response.status_code == 200
        problem_history = response.json()
        assert isinstance(problem_history, list)
        
        # All entries should be for two-sum
        for entry in problem_history:
            assert entry["problem_slug"] == "two-sum"
        print(f"   ✓ Retrieved {len(problem_history)} entries for 'two-sum'")
        
        # Step 4: Delete a history entry
        if len(problem_history) > 0:
            print("\n🗑️  Step 4: Delete a history entry")
            entry_id = problem_history[0]["id"]
            response = client.delete(f"/api/history/{entry_id}")
            assert response.status_code == 200
            result = response.json()
            assert result["entry_id"] == entry_id
            print(f"   ✓ Deleted entry: {entry_id}")
        
        print("\n" + "=" * 70)
        print("✓ HISTORY MANAGEMENT TEST PASSED")
        print("=" * 70)
    
    def test_caching_workflow(self):
        """
        Test that caching works correctly for problem details and analysis results.
        """
        print("\n" + "=" * 70)
        print("TEST: Caching Workflow")
        print("=" * 70)
        
        # Clear cache first
        cache_service.clear_all()
        
        # Step 1: First request (cache miss)
        print("\n🔍 Step 1: First problem fetch (cache miss)")
        response1 = client.get("/api/problem/two-sum")
        assert response1.status_code == 200
        problem1 = response1.json()
        print("   ✓ Problem fetched from LeetCode")
        
        # Step 2: Second request (cache hit)
        print("\n⚡ Step 2: Second problem fetch (cache hit)")
        response2 = client.get("/api/problem/two-sum")
        assert response2.status_code == 200
        problem2 = response2.json()
        assert problem1 == problem2
        print("   ✓ Problem fetched from cache")
        
        # Step 3: Check cache stats
        print("\n📊 Step 3: Check cache statistics")
        response = client.get("/api/cache/stats")
        assert response.status_code == 200
        stats = response.json()
        assert "problem_cache" in stats
        print(f"   ✓ Cache stats: {stats['problem_cache']['size']} problems cached")
        
        # Step 4: Clear cache
        print("\n🗑️  Step 4: Clear cache")
        response = client.delete("/api/cache/clear?cache_type=all")
        assert response.status_code == 200
        print("   ✓ Cache cleared")
        
        # Step 5: Verify cache is empty
        response = client.get("/api/cache/stats")
        stats = response.json()
        assert stats["problem_cache"]["size"] == 0
        print("   ✓ Cache confirmed empty")
        
        print("\n" + "=" * 70)
        print("✓ CACHING WORKFLOW TEST PASSED")
        print("=" * 70)


class TestErrorScenariosAndRecovery:
    """Test error handling and recovery mechanisms."""
    
    def test_invalid_url_error_handling(self):
        """Test error handling for invalid problem URLs."""
        print("\n" + "=" * 70)
        print("TEST: Invalid URL Error Handling")
        print("=" * 70)
        
        invalid_urls = [
            "",
            "not-a-url",
            "https://google.com",
            "https://leetcode.com/invalid",
            "https://leetcode.com/problems/",
        ]
        
        for url in invalid_urls:
            print(f"\n❌ Testing invalid URL: '{url}'")
            response = client.post(
                "/api/validate-url",
                params={"url": url}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is False
            assert "message" in data
            assert "suggestion" in data or data["suggestion"] is None
            print(f"   ✓ Error handled: {data['message']}")
        
        print("\n" + "=" * 70)
        print("✓ INVALID URL ERROR HANDLING TEST PASSED")
        print("=" * 70)
    
    def test_invalid_code_error_handling(self):
        """Test error handling for invalid code inputs."""
        print("\n" + "=" * 70)
        print("TEST: Invalid Code Error Handling")
        print("=" * 70)
        
        test_cases = [
            ("", "python", "Empty code"),
            ("x", "python", "Code too short"),
            ("def test(", "python", "Mismatched parentheses"),
        ]
        
        for code, language, description in test_cases:
            print(f"\n❌ Testing: {description}")
            response = client.post(
                "/api/validate",
                params={
                    "code": code,
                    "language": language
                }
            )
            assert response.status_code == 200
            data = response.json()
            
            if code == "":
                assert data["validation_results"]["code"]["valid"] is False
            
            print(f"   ✓ Validation result: {data['validation_results']['code']['valid']}")
        
        print("\n" + "=" * 70)
        print("✓ INVALID CODE ERROR HANDLING TEST PASSED")
        print("=" * 70)
    
    def test_unsupported_language_error_handling(self):
        """Test error handling for unsupported programming languages."""
        print("\n" + "=" * 70)
        print("TEST: Unsupported Language Error Handling")
        print("=" * 70)
        
        unsupported_languages = ["brainfuck", "cobol", "fortran", ""]
        
        for language in unsupported_languages:
            print(f"\n❌ Testing unsupported language: '{language}'")
            response = client.post(
                "/api/validate",
                params={
                    "language": language
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["validation_results"]["language"]["valid"] is False
            
            errors = data["validation_results"]["language"]["errors"]
            assert len(errors) > 0
            assert "examples" in errors[0]
            print(f"   ✓ Error handled with suggestions: {errors[0]['examples'][:3]}")
        
        print("\n" + "=" * 70)
        print("✓ UNSUPPORTED LANGUAGE ERROR HANDLING TEST PASSED")
        print("=" * 70)
    
    def test_invalid_analysis_type_error_handling(self):
        """Test error handling for invalid analysis types."""
        print("\n" + "=" * 70)
        print("TEST: Invalid Analysis Type Error Handling")
        print("=" * 70)
        
        invalid_types = ["invalid", "test", "", "complexity-analysis"]
        
        for analysis_type in invalid_types:
            print(f"\n❌ Testing invalid analysis type: '{analysis_type}'")
            response = client.post(
                "/api/validate",
                params={
                    "analysis_type": analysis_type
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["validation_results"]["analysis_type"]["valid"] is False
            
            errors = data["validation_results"]["analysis_type"]["errors"]
            assert len(errors) > 0
            assert "examples" in errors[0]
            print(f"   ✓ Error handled with valid options: {errors[0]['examples']}")
        
        print("\n" + "=" * 70)
        print("✓ INVALID ANALYSIS TYPE ERROR HANDLING TEST PASSED")
        print("=" * 70)
    
    def test_nonexistent_problem_error_handling(self):
        """Test error handling for non-existent LeetCode problems."""
        print("\n" + "=" * 70)
        print("TEST: Non-existent Problem Error Handling")
        print("=" * 70)
        
        print("\n❌ Testing non-existent problem")
        response = client.get("/api/problem/this-problem-does-not-exist-12345")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        
        detail = data["detail"]
        assert "error" in detail
        assert "message" in detail
        assert "suggestion" in detail
        print(f"   ✓ Error handled: {detail['message']}")
        print(f"   ✓ Suggestion provided: {detail['suggestion']}")
        
        print("\n" + "=" * 70)
        print("✓ NON-EXISTENT PROBLEM ERROR HANDLING TEST PASSED")
        print("=" * 70)
    
    def test_comprehensive_validation_error_handling(self):
        """Test comprehensive validation with multiple errors."""
        print("\n" + "=" * 70)
        print("TEST: Comprehensive Validation Error Handling")
        print("=" * 70)
        
        print("\n❌ Testing request with multiple validation errors")
        response = client.post(
            "/api/analyze",
            json={
                "problem_url": "invalid-url",
                "code": "",
                "language": "invalid-language",
                "analysis_type": "invalid-type"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        
        detail = data["detail"]
        assert "validation_errors" in detail
        assert len(detail["validation_errors"]) > 0
        
        print(f"   ✓ Multiple validation errors detected: {len(detail['validation_errors'])} errors")
        
        # Check that each error has required fields
        for error in detail["validation_errors"]:
            assert "field" in error
            assert "message" in error
            assert "suggestion" in error
            print(f"   ✓ Error for {error['field']}: {error['message']}")
        
        print("\n" + "=" * 70)
        print("✓ COMPREHENSIVE VALIDATION ERROR HANDLING TEST PASSED")
        print("=" * 70)


def run_all_tests():
    """Run all end-to-end integration tests."""
    print("\n" + "=" * 80)
    print(" " * 20 + "END-TO-END INTEGRATION TESTS")
    print("=" * 80)
    
    # Workflow tests
    workflow_tests = TestEndToEndWorkflows()
    workflow_tests.setup_method()
    
    try:
        workflow_tests.test_complete_complexity_analysis_workflow()
        workflow_tests.test_hints_workflow_with_incomplete_solution()
        workflow_tests.test_completeness_blocking_workflow()
        workflow_tests.test_history_retrieval_and_filtering()
        workflow_tests.test_caching_workflow()
    except Exception as e:
        print(f"\n❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Error handling tests
    error_tests = TestErrorScenariosAndRecovery()
    
    try:
        error_tests.test_invalid_url_error_handling()
        error_tests.test_invalid_code_error_handling()
        error_tests.test_unsupported_language_error_handling()
        error_tests.test_invalid_analysis_type_error_handling()
        error_tests.test_nonexistent_problem_error_handling()
        error_tests.test_comprehensive_validation_error_handling()
    except Exception as e:
        print(f"\n❌ Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 80)
    print(" " * 25 + "✓ ALL TESTS PASSED")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
