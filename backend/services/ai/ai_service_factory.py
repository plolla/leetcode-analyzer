"""
AI Service Factory with automatic fallback support.

This module provides a factory for creating AI service instances with
automatic fallback to secondary providers when the primary fails.
"""

import logging
import asyncio
from typing import Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from services.ai.ai_service import AIService
from services.ai.claude_service import claude_service
from services.ai.openai_service import openai_service
from config import config, AIProvider

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, max_calls_per_minute: int = 10):
        self.max_calls = max_calls_per_minute
        self.calls = defaultdict(list)
    
    def check_rate_limit(self, client_id: str = "default") -> Tuple[bool, Optional[int]]:
        """
        Check if rate limit is exceeded.
        
        Returns:
            Tuple of (is_allowed, seconds_until_reset)
        """
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        
        # Clean up old calls
        self.calls[client_id] = [
            call_time for call_time in self.calls[client_id]
            if call_time > one_minute_ago
        ]
        
        # Check if limit exceeded
        if len(self.calls[client_id]) >= self.max_calls:
            oldest_call = min(self.calls[client_id])
            seconds_until_reset = int((oldest_call + timedelta(minutes=1) - now).total_seconds())
            return False, max(1, seconds_until_reset)
        
        # Record this call
        self.calls[client_id].append(now)
        return True, None
    
    def reset(self, client_id: str = "default"):
        """Reset rate limit for a client."""
        if client_id in self.calls:
            del self.calls[client_id]


# Global rate limiter
rate_limiter = RateLimiter(max_calls_per_minute=config.RATE_LIMIT_PER_MINUTE)


class AsyncOpenAIWrapper:
    """Wrapper to make synchronous OpenAI service async-compatible."""
    
    def __init__(self, sync_service):
        self.sync_service = sync_service
        self.executor = None
    
    def _get_executor(self):
        """Get or create thread pool executor."""
        if self.executor is None:
            from concurrent.futures import ThreadPoolExecutor
            self.executor = ThreadPoolExecutor(max_workers=5)
        return self.executor
    
    async def analyze_time_complexity(self, problem_description: str, code: str, language: str):
        """Async wrapper for analyze_time_complexity."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._get_executor(),
            lambda: self.sync_service.analyze_time_complexity(problem_description, code, language)
        )
    
    async def analyze_complexity_quick(self, problem_description: str, code: str, language: str):
        """Async wrapper for analyze_complexity_quick."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._get_executor(),
            lambda: self.sync_service.analyze_complexity_quick(problem_description, code, language)
        )
    
    async def explain_complexity(self, problem_description: str, code: str, language: str, time_complexity: str, space_complexity: str):
        """Async wrapper for explain_complexity."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._get_executor(),
            lambda: self.sync_service.explain_complexity(problem_description, code, language, time_complexity, space_complexity)
        )
    
    async def generate_hints(self, problem_description: str, code: str, language: str):
        """Async wrapper for generate_hints."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._get_executor(),
            lambda: self.sync_service.generate_hints(problem_description, code, language)
        )
    
    async def optimize_solution(self, problem_description: str, code: str, language: str):
        """Async wrapper for optimize_solution."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._get_executor(),
            lambda: self.sync_service.optimize_solution(problem_description, code, language)
        )
    
    async def debug_solution(self, problem_description: str, code: str, language: str):
        """Async wrapper for debug_solution."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._get_executor(),
            lambda: self.sync_service.debug_solution(problem_description, code, language)
        )
    
    async def check_solution_completeness(self, code: str, language: str):
        """Async wrapper for check_solution_completeness."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._get_executor(),
            lambda: self.sync_service.check_solution_completeness(code, language)
        )


class AIServiceWithFallback:
    """
    AI Service wrapper that provides automatic fallback functionality.
    
    Attempts to use the primary service first, and falls back to the
    secondary service if the primary fails.
    """
    
    def __init__(self, primary: AIService, fallback: Optional[AIService] = None):
        self.primary = primary
        self.fallback = fallback
        self.rate_limiter = rate_limiter
    
    def _get_error_details(self, error: Exception) -> dict:
        """
        Extract detailed error information from exception.
        
        Returns:
            Dictionary with error details for user-friendly messages
        """
        error_str = str(error).lower()
        
        # Check for specific error types
        if "rate limit" in error_str or "429" in error_str:
            return {
                "type": "rate_limit",
                "message": "AI service rate limit exceeded",
                "suggestion": "Please wait a moment and try again. The service has temporary usage limits.",
                "retry_after": 60
            }
        elif "timeout" in error_str or "timed out" in error_str:
            return {
                "type": "timeout",
                "message": "Request timed out",
                "suggestion": "The AI service took too long to respond. Please try again.",
                "retry_after": 5
            }
        elif "connection" in error_str or "network" in error_str:
            return {
                "type": "network",
                "message": "Network connection error",
                "suggestion": "Unable to connect to the AI service. Please check your internet connection and try again.",
                "retry_after": 10
            }
        elif "authentication" in error_str or "api key" in error_str or "401" in error_str:
            return {
                "type": "authentication",
                "message": "AI service authentication failed",
                "suggestion": "The API key is invalid or expired. Please contact the administrator.",
                "retry_after": None
            }
        elif "quota" in error_str or "insufficient" in error_str:
            return {
                "type": "quota",
                "message": "AI service quota exceeded",
                "suggestion": "The service has reached its usage quota. Please try again later or contact the administrator.",
                "retry_after": None
            }
        else:
            return {
                "type": "unknown",
                "message": f"AI service error: {str(error)}",
                "suggestion": "An unexpected error occurred. Please try again or contact support if the problem persists.",
                "retry_after": 10
            }
    
    async def _execute_with_fallback(self, method_name: str, *args, **kwargs):
        """
        Execute a method with automatic fallback support.
        
        Args:
            method_name: Name of the method to call
            *args, **kwargs: Arguments to pass to the method
            
        Returns:
            Result from the method call
            
        Raises:
            Exception: If both primary and fallback services fail
        """
        # Check rate limit
        is_allowed, seconds_until_reset = self.rate_limiter.check_rate_limit()
        if not is_allowed:
            raise Exception(
                f"Rate limit exceeded. Please wait {seconds_until_reset} seconds before trying again."
            )
        
        primary_error = None
        fallback_error = None
        
        # Try primary service
        try:
            logger.info(f"Calling primary AI service: {method_name}")
            method = getattr(self.primary, method_name)
            return await method(*args, **kwargs)
        except Exception as e:
            primary_error = e
            error_details = self._get_error_details(e)
            logger.warning(
                f"Primary AI service failed for {method_name}: {error_details['message']}"
            )
        
        # Try fallback service if available
        if self.fallback:
            try:
                logger.info(f"Falling back to secondary AI service: {method_name}")
                method = getattr(self.fallback, method_name)
                result = await method(*args, **kwargs)
                logger.info(f"Fallback service succeeded for {method_name}")
                return result
            except Exception as e:
                fallback_error = e
                fallback_details = self._get_error_details(e)
                logger.error(
                    f"Fallback AI service also failed for {method_name}: {fallback_details['message']}"
                )
        
        # Both services failed - raise detailed error
        primary_details = self._get_error_details(primary_error)
        
        if fallback_error:
            fallback_details = self._get_error_details(fallback_error)
            error_message = (
                f"Both AI services failed. "
                f"Primary: {primary_details['message']}. "
                f"Fallback: {fallback_details['message']}. "
                f"Suggestion: {primary_details['suggestion']}"
            )
        else:
            error_message = (
                f"AI service failed: {primary_details['message']}. "
                f"Suggestion: {primary_details['suggestion']}"
            )
        
        raise Exception(error_message)
    
    async def analyze_time_complexity(self, problem_description: str, code: str, language: str):
        """Analyze time complexity with fallback support."""
        return await self._execute_with_fallback(
            "analyze_time_complexity",
            problem_description, code, language
        )
    
    async def analyze_complexity_quick(self, problem_description: str, code: str, language: str):
        """Quick complexity analysis with fallback support."""
        return await self._execute_with_fallback(
            "analyze_complexity_quick",
            problem_description, code, language
        )
    
    async def explain_complexity(self, problem_description: str, code: str, language: str, time_complexity: str, space_complexity: str):
        """Explain complexity with fallback support."""
        return await self._execute_with_fallback(
            "explain_complexity",
            problem_description, code, language, time_complexity, space_complexity
        )
    
    async def generate_hints(self, problem_description: str, code: str, language: str):
        """Generate hints with fallback support."""
        return await self._execute_with_fallback(
            "generate_hints",
            problem_description, code, language
        )
    
    async def optimize_solution(self, problem_description: str, code: str, language: str):
        """Optimize solution with fallback support."""
        return await self._execute_with_fallback(
            "optimize_solution",
            problem_description, code, language
        )
    
    async def debug_solution(self, problem_description: str, code: str, language: str):
        """Debug solution with fallback support."""
        return await self._execute_with_fallback(
            "debug_solution",
            problem_description, code, language
        )
    
    async def check_solution_completeness(self, code: str, language: str):
        """Check solution completeness with fallback support."""
        return await self._execute_with_fallback(
            "check_solution_completeness",
            code, language
        )


def get_ai_service() -> AIServiceWithFallback:
    """
    Factory function to create AI service with fallback support.
    
    Returns:
        AIServiceWithFallback configured with primary and fallback services
    """
    primary_provider = config.get_ai_provider()
    fallback_provider = config.get_fallback_provider()
    
    # Get primary service
    if primary_provider == AIProvider.CLAUDE:
        primary = claude_service
    elif primary_provider == AIProvider.OPENAI:
        primary = AsyncOpenAIWrapper(openai_service)
    else:
        raise ValueError(f"Unsupported primary AI provider: {primary_provider}")
    
    # Get fallback service (if different from primary)
    fallback = None
    if fallback_provider != primary_provider:
        if fallback_provider == AIProvider.CLAUDE:
            fallback = claude_service
        elif fallback_provider == AIProvider.OPENAI:
            fallback = AsyncOpenAIWrapper(openai_service)
    
    return AIServiceWithFallback(primary, fallback)


# Singleton instance
ai_service = get_ai_service()
