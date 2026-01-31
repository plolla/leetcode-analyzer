"""
Cache service for storing and retrieving cached data.
Implements in-memory caching with TTL (Time To Live) support.
"""

from typing import Optional, Any, Dict, Tuple
from datetime import datetime, timedelta
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class CacheEntry:
    """Represents a cached entry with expiration."""
    
    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(seconds=ttl_seconds)
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return datetime.now() > self.expires_at
    
    def get_value(self) -> Any:
        """Get the cached value."""
        return self.value


class CacheService:
    """
    In-memory cache service with TTL support.
    
    Features:
    - TTL-based expiration
    - Automatic cleanup of expired entries
    - Cache key generation from request parameters
    - Separate caches for different data types
    """
    
    def __init__(self):
        # Separate caches for different types of data
        self.problem_cache: Dict[str, CacheEntry] = {}
        self.analysis_cache: Dict[str, CacheEntry] = {}
        
        # Default TTL values (in seconds)
        self.PROBLEM_TTL = 24 * 60 * 60  # 24 hours
        self.ANALYSIS_TTL = 60 * 60  # 1 hour
        
        # Cache statistics
        self.stats = {
            'problem_hits': 0,
            'problem_misses': 0,
            'analysis_hits': 0,
            'analysis_misses': 0
        }
    
    def _generate_cache_key(self, **kwargs) -> str:
        """
        Generate a cache key from parameters.
        
        Args:
            **kwargs: Parameters to include in the cache key
            
        Returns:
            A hash string to use as cache key
        """
        # Sort keys for consistent hashing
        sorted_params = sorted(kwargs.items())
        key_string = json.dumps(sorted_params, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def _cleanup_expired(self, cache: Dict[str, CacheEntry]) -> None:
        """Remove expired entries from a cache."""
        expired_keys = [
            key for key, entry in cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del cache[key]
            logger.debug(f"Removed expired cache entry: {key[:8]}...")
    
    # Problem caching methods
    
    def get_problem(self, slug: str) -> Optional[Any]:
        """
        Get a cached problem by slug.
        
        Args:
            slug: The problem slug
            
        Returns:
            Cached problem details if found and not expired, None otherwise
        """
        self._cleanup_expired(self.problem_cache)
        
        if slug in self.problem_cache:
            entry = self.problem_cache[slug]
            if not entry.is_expired():
                self.stats['problem_hits'] += 1
                logger.info(f"Problem cache HIT for slug: {slug}")
                return entry.get_value()
            else:
                del self.problem_cache[slug]
        
        self.stats['problem_misses'] += 1
        logger.info(f"Problem cache MISS for slug: {slug}")
        return None
    
    def set_problem(self, slug: str, problem: Any, ttl: Optional[int] = None) -> None:
        """
        Cache a problem.
        
        Args:
            slug: The problem slug
            problem: The problem details to cache
            ttl: Optional custom TTL in seconds (defaults to PROBLEM_TTL)
        """
        ttl = ttl or self.PROBLEM_TTL
        self.problem_cache[slug] = CacheEntry(problem, ttl)
        logger.info(f"Cached problem: {slug} (TTL: {ttl}s)")
    
    # Analysis result caching methods
    
    def get_analysis(
        self,
        problem_slug: str,
        code: str,
        language: str,
        analysis_type: str
    ) -> Optional[Any]:
        """
        Get a cached analysis result.
        
        Args:
            problem_slug: The problem slug
            code: The solution code
            language: Programming language
            analysis_type: Type of analysis
            
        Returns:
            Cached analysis result if found and not expired, None otherwise
        """
        self._cleanup_expired(self.analysis_cache)
        
        cache_key = self._generate_cache_key(
            problem_slug=problem_slug,
            code=code,
            language=language,
            analysis_type=analysis_type
        )
        
        if cache_key in self.analysis_cache:
            entry = self.analysis_cache[cache_key]
            if not entry.is_expired():
                self.stats['analysis_hits'] += 1
                logger.info(f"Analysis cache HIT for {analysis_type} on {problem_slug}")
                return entry.get_value()
            else:
                del self.analysis_cache[cache_key]
        
        self.stats['analysis_misses'] += 1
        logger.info(f"Analysis cache MISS for {analysis_type} on {problem_slug}")
        return None
    
    def set_analysis(
        self,
        problem_slug: str,
        code: str,
        language: str,
        analysis_type: str,
        result: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        Cache an analysis result.
        
        Args:
            problem_slug: The problem slug
            code: The solution code
            language: Programming language
            analysis_type: Type of analysis
            result: The analysis result to cache
            ttl: Optional custom TTL in seconds (defaults to ANALYSIS_TTL)
        """
        ttl = ttl or self.ANALYSIS_TTL
        cache_key = self._generate_cache_key(
            problem_slug=problem_slug,
            code=code,
            language=language,
            analysis_type=analysis_type
        )
        
        self.analysis_cache[cache_key] = CacheEntry(result, ttl)
        logger.info(f"Cached analysis: {analysis_type} on {problem_slug} (TTL: {ttl}s)")
    
    # Cache management methods
    
    def clear_problem_cache(self) -> None:
        """Clear all cached problems."""
        count = len(self.problem_cache)
        self.problem_cache.clear()
        logger.info(f"Cleared {count} problem cache entries")
    
    def clear_analysis_cache(self) -> None:
        """Clear all cached analysis results."""
        count = len(self.analysis_cache)
        self.analysis_cache.clear()
        logger.info(f"Cleared {count} analysis cache entries")
    
    def clear_all(self) -> None:
        """Clear all caches."""
        self.clear_problem_cache()
        self.clear_analysis_cache()
        logger.info("Cleared all caches")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_problem_requests = self.stats['problem_hits'] + self.stats['problem_misses']
        total_analysis_requests = self.stats['analysis_hits'] + self.stats['analysis_misses']
        
        problem_hit_rate = (
            self.stats['problem_hits'] / total_problem_requests * 100
            if total_problem_requests > 0 else 0
        )
        analysis_hit_rate = (
            self.stats['analysis_hits'] / total_analysis_requests * 100
            if total_analysis_requests > 0 else 0
        )
        
        return {
            'problem_cache': {
                'size': len(self.problem_cache),
                'hits': self.stats['problem_hits'],
                'misses': self.stats['problem_misses'],
                'hit_rate': f"{problem_hit_rate:.1f}%"
            },
            'analysis_cache': {
                'size': len(self.analysis_cache),
                'hits': self.stats['analysis_hits'],
                'misses': self.stats['analysis_misses'],
                'hit_rate': f"{analysis_hit_rate:.1f}%"
            }
        }


# Singleton instance
cache_service = CacheService()
