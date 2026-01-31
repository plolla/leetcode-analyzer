"""
Tests for the cache service.
"""

import pytest
import time
from services.cache_service import CacheService


def test_cache_service_problem_caching():
    """Test that problem caching works correctly."""
    cache = CacheService()
    cache.clear_all()
    
    # Test problem caching
    problem_data = {
        "slug": "two-sum",
        "title": "Two Sum",
        "difficulty": "Easy"
    }
    
    # Cache the problem
    cache.set_problem("two-sum", problem_data)
    
    # Retrieve from cache
    cached = cache.get_problem("two-sum")
    assert cached is not None
    assert cached["slug"] == "two-sum"
    assert cached["title"] == "Two Sum"
    
    # Check stats
    stats = cache.get_stats()
    assert stats["problem_cache"]["hits"] == 1
    assert stats["problem_cache"]["misses"] == 0


def test_cache_service_analysis_caching():
    """Test that analysis result caching works correctly."""
    cache = CacheService()
    cache.clear_all()
    
    # Test analysis caching
    analysis_result = {
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
        "explanation": "Linear scan"
    }
    
    # Cache the analysis
    cache.set_analysis(
        problem_slug="two-sum",
        code="def solution(): pass",
        language="python",
        analysis_type="complexity",
        result=analysis_result
    )
    
    # Retrieve from cache
    cached = cache.get_analysis(
        problem_slug="two-sum",
        code="def solution(): pass",
        language="python",
        analysis_type="complexity"
    )
    
    assert cached is not None
    assert cached["time_complexity"] == "O(n)"
    
    # Check stats
    stats = cache.get_stats()
    assert stats["analysis_cache"]["hits"] == 1
    assert stats["analysis_cache"]["misses"] == 0


def test_cache_service_expiration():
    """Test that cache entries expire correctly."""
    cache = CacheService()
    cache.clear_all()
    
    # Cache with very short TTL (1 second)
    cache.set_problem("test-problem", {"data": "test"}, ttl=1)
    
    # Should be available immediately
    cached = cache.get_problem("test-problem")
    assert cached is not None
    
    # Wait for expiration
    time.sleep(1.1)
    
    # Should be expired now
    cached = cache.get_problem("test-problem")
    assert cached is None


def test_cache_service_different_code_different_cache():
    """Test that different code produces different cache entries."""
    cache = CacheService()
    cache.clear_all()
    
    result1 = {"result": "first"}
    result2 = {"result": "second"}
    
    # Cache two different analyses with different code
    cache.set_analysis(
        problem_slug="two-sum",
        code="def solution1(): pass",
        language="python",
        analysis_type="complexity",
        result=result1
    )
    
    cache.set_analysis(
        problem_slug="two-sum",
        code="def solution2(): pass",
        language="python",
        analysis_type="complexity",
        result=result2
    )
    
    # Retrieve both
    cached1 = cache.get_analysis(
        problem_slug="two-sum",
        code="def solution1(): pass",
        language="python",
        analysis_type="complexity"
    )
    
    cached2 = cache.get_analysis(
        problem_slug="two-sum",
        code="def solution2(): pass",
        language="python",
        analysis_type="complexity"
    )
    
    assert cached1["result"] == "first"
    assert cached2["result"] == "second"


def test_cache_service_clear():
    """Test that cache clearing works correctly."""
    cache = CacheService()
    cache.clear_all()
    
    # Add some entries
    cache.set_problem("problem1", {"data": "test1"})
    cache.set_problem("problem2", {"data": "test2"})
    cache.set_analysis("problem1", "code", "python", "complexity", {"result": "test"})
    
    # Verify they exist
    assert cache.get_problem("problem1") is not None
    assert cache.get_problem("problem2") is not None
    assert cache.get_analysis("problem1", "code", "python", "complexity") is not None
    
    # Clear problem cache
    cache.clear_problem_cache()
    assert cache.get_problem("problem1") is None
    assert cache.get_problem("problem2") is None
    assert cache.get_analysis("problem1", "code", "python", "complexity") is not None
    
    # Clear all
    cache.clear_all()
    assert cache.get_analysis("problem1", "code", "python", "complexity") is None


def test_cache_service_stats():
    """Test that cache statistics are tracked correctly."""
    cache = CacheService()
    cache.clear_all()
    
    # Add some entries and access them
    cache.set_problem("problem1", {"data": "test"})
    
    # Hit
    cache.get_problem("problem1")
    
    # Miss
    cache.get_problem("nonexistent")
    
    stats = cache.get_stats()
    assert stats["problem_cache"]["hits"] == 1
    assert stats["problem_cache"]["misses"] == 1
    assert "%" in stats["problem_cache"]["hit_rate"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
