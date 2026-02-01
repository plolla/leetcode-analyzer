from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta
from pydantic import BaseModel
import re
import logging
from services.leetcode_parser import leetcode_parser, ProblemDetails
from services.ai.ai_service_factory import ai_service
from services.ai.ai_service import ComplexityAnalysis, HintResponse, OptimizationResponse, DebugResponse, AnalysisType, QuickComplexityAnalysis, ComplexityExplanation
from services.history_service import history_service, HistoryCreateRequest, HistoryResponse, HistoryEntry
from services.validation_service import validation_service, ValidationResult
from services.cache_service import cache_service
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LeetCode Analysis API")

# Configure CORS - must be added before routes
import os

# Get allowed origins from environment or use defaults
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://leetcode-analyzer-nu.vercel.app",  # Production frontend
]

# Add additional frontend URLs from environment if configured
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    expose_headers=["*"],
    max_age=3600,
)

# Simple in-memory cache for problem details
# In production, use Redis or similar
problem_cache: Dict[str, Tuple[ProblemDetails, datetime]] = {}
CACHE_DURATION = timedelta(hours=24)


class QuickComplexityRequest(BaseModel):
    problem_url: Optional[str] = None
    code: str
    language: str


class ExplainComplexityRequest(BaseModel):
    code: str
    language: str
    time_complexity: str
    space_complexity: str
    problem_url: Optional[str] = None


# Request Models
class AnalysisRequest(BaseModel):
    problem_url: Optional[str] = None  # Now optional
    code: str
    language: str
    analysis_type: str  # 'complexity', 'hints', 'optimization', 'debugging'


def get_cached_problem(slug: str) -> Optional[ProblemDetails]:
    """Get problem from cache if it exists and is not expired."""
    return cache_service.get_problem(slug)


def cache_problem(slug: str, problem: ProblemDetails):
    """Cache a problem with current timestamp."""
    cache_service.set_problem(slug, problem)


@app.get("/")
async def root():
    return {"message": "LeetCode Analysis API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/cache/stats")
async def get_cache_stats():
    """
    Get cache statistics.
    
    Returns:
        Cache statistics including hit rates and sizes
    """
    return cache_service.get_stats()


@app.delete("/api/cache/clear")
async def clear_cache(cache_type: Optional[str] = Query(None, description="Type of cache to clear: 'problem', 'analysis', or 'all'")):
    """
    Clear cache entries.
    
    Args:
        cache_type: Optional cache type to clear ('problem', 'analysis', or 'all')
        
    Returns:
        Success message
    """
    if cache_type == "problem":
        cache_service.clear_problem_cache()
        return {"message": "Problem cache cleared successfully"}
    elif cache_type == "analysis":
        cache_service.clear_analysis_cache()
        return {"message": "Analysis cache cleared successfully"}
    elif cache_type == "all" or cache_type is None:
        cache_service.clear_all()
        return {"message": "All caches cleared successfully"}
    else:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid cache type",
                "message": f"Cache type '{cache_type}' is not supported",
                "suggestion": "Use 'problem', 'analysis', or 'all'",
                "examples": ["problem", "analysis", "all"]
            }
        )


@app.get("/api/problem/{slug}", response_model=ProblemDetails)
async def get_problem_details(slug: str):
    """
    Get problem details by slug.
    
    Args:
        slug: The LeetCode problem slug (e.g., 'two-sum')
        
    Returns:
        Problem details including title, difficulty, description, etc.
        
    Raises:
        HTTPException: If problem not found or invalid slug
    """
    # Validate slug format
    if not slug or not re.match(r'^[\w-]+$', slug):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid problem slug",
                "message": f"Problem slug '{slug}' contains invalid characters",
                "suggestion": "Problem slug should only contain letters, numbers, and hyphens",
                "examples": ["two-sum", "reverse-linked-list", "binary-tree-inorder-traversal"]
            }
        )
    
    # Check cache first
    cached = get_cached_problem(slug)
    if cached:
        return cached
    
    # Fetch from LeetCode
    try:
        problem = leetcode_parser.fetch_problem_details(slug)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to fetch problem",
                "message": f"Could not retrieve problem details from LeetCode",
                "suggestion": "Please check your internet connection and try again. If the problem persists, the LeetCode API may be temporarily unavailable.",
                "technical_details": str(e)
            }
        )
    
    if not problem:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Problem not found",
                "message": f"Problem '{slug}' not found on LeetCode",
                "suggestion": "Please verify the problem URL is correct and the problem exists on LeetCode",
                "examples": [
                    "https://leetcode.com/problems/two-sum/",
                    "https://leetcode.com/problems/add-two-numbers/"
                ]
            }
        )
    
    # Cache the result
    cache_problem(slug, problem)
    
    return problem


@app.post("/api/validate-url")
async def validate_url(url: str):
    """
    Validate a LeetCode problem URL with detailed error messages.
    
    Args:
        url: The URL to validate
        
    Returns:
        Validation result with slug if valid, or detailed errors
    """
    # Use validation service for comprehensive error handling
    validation_result = validation_service.validate_problem_url(url)
    
    if validation_result.is_valid:
        slug = leetcode_parser.extract_problem_slug(url)
        return {
            "valid": True,
            "slug": slug,
            "message": "Valid LeetCode problem URL"
        }
    else:
        # Return detailed error information
        error = validation_result.errors[0] if validation_result.errors else None
        return {
            "valid": False,
            "slug": None,
            "message": error.message if error else "Invalid LeetCode problem URL",
            "suggestion": error.suggestion if error else None,
            "examples": error.examples if error else None
        }


@app.options("/api/analyze")
async def analyze_options():
    """Handle CORS preflight for analyze endpoint."""
    return {"message": "OK"}


@app.post("/api/analyze-complexity-quick")
async def analyze_complexity_quick(request: QuickComplexityRequest):
    """
    Quick complexity analysis - returns only Big O notation for fast response.
    Optimized for speed with minimal AI prompt and response.
    
    Args:
        request: Quick analysis request with optional problem URL, code, and language
        
    Returns:
        QuickComplexityAnalysis with just time/space complexity
        
    Raises:
        HTTPException: If analysis fails or invalid request
    """
    # Validate API key is configured
    if not config.validate_config():
        raise HTTPException(
            status_code=503,
            detail={
                "error": "AI service not configured",
                "message": "The AI service is not properly configured",
                "suggestion": "Please contact the administrator to configure API keys"
            }
        )
    
    # Validate inputs
    code_validation = validation_service.validate_code(request.code, request.language)
    language_validation = validation_service.validate_language(request.language)
    
    if not code_validation.is_valid or not language_validation.is_valid:
        errors = code_validation.errors + language_validation.errors
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Input validation failed",
                "message": "Code or language validation failed",
                "validation_errors": [
                    {
                        "field": error.field,
                        "message": error.message,
                        "suggestion": error.suggestion
                    }
                    for error in errors
                ]
            }
        )
    
    # Handle problem details
    problem_description = None
    slug = None
    
    if request.problem_url:
        slug = leetcode_parser.extract_problem_slug(request.problem_url)
        if slug:
            try:
                problem = await get_problem_details(slug)
                problem_description = f"{problem.title}: {problem.description}"
            except Exception as e:
                logger.warning(f"Failed to fetch problem details: {e}")
                slug = "unknown-problem"
        else:
            slug = "unknown-problem"
    else:
        slug = "inferred-problem"
    
    # Check cache for quick analysis
    cache_key_params = {
        "problem_slug": slug,
        "code": request.code,
        "language": request.language,
        "analysis_type": "complexity-quick"
    }
    cached_result = cache_service.get_analysis(**cache_key_params)
    
    if cached_result is not None:
        logger.info(f"Returning cached quick complexity analysis for {slug}")
        return cached_result
    
    # Perform quick analysis
    try:
        result = await ai_service.analyze_complexity_quick(
            problem_description=problem_description,
            code=request.code,
            language=request.language
        )
        
        # Cache the result (1 hour TTL)
        cache_service.set_analysis(
            **cache_key_params,
            result=result.dict() if hasattr(result, 'dict') else result,
            ttl=3600  # 1 hour
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Quick complexity analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Analysis failed",
                "message": "Failed to analyze complexity",
                "suggestion": "Please try again. If the problem persists, contact support.",
                "technical_details": str(e)
            }
        )


@app.post("/api/explain-complexity")
async def explain_complexity(request: ExplainComplexityRequest):
    """
    Generate detailed explanation for complexity analysis.
    Uses already-computed Big O notation to provide focused explanation.
    
    Args:
        request: Request with code, language, complexities, and optional problem URL
        
    Returns:
        ComplexityExplanation with detailed explanation and suggestions
        
    Raises:
        HTTPException: If explanation generation fails
    """
    # Validate API key is configured
    if not config.validate_config():
        raise HTTPException(
            status_code=503,
            detail={
                "error": "AI service not configured",
                "message": "The AI service is not properly configured",
                "suggestion": "Please contact the administrator to configure API keys"
            }
        )
    
    # Handle problem details
    problem_description = None
    slug = None
    
    if request.problem_url:
        slug = leetcode_parser.extract_problem_slug(request.problem_url)
        if slug:
            try:
                problem = await get_problem_details(slug)
                problem_description = f"{problem.title}: {problem.description}"
            except Exception as e:
                logger.warning(f"Failed to fetch problem details: {e}")
                slug = "unknown-problem"
        else:
            slug = "unknown-problem"
    else:
        slug = "inferred-problem"
    
    # Check cache for explanation (24 hour TTL for explanations)
    cache_key_params = {
        "problem_slug": slug,
        "code": request.code,
        "language": request.language,
        "analysis_type": f"complexity-explanation-{request.time_complexity}-{request.space_complexity}"
    }
    cached_result = cache_service.get_analysis(**cache_key_params)
    
    if cached_result is not None:
        logger.info(f"Returning cached complexity explanation for {slug}")
        return cached_result
    
    # Generate explanation
    try:
        result = await ai_service.explain_complexity(
            problem_description=problem_description,
            code=request.code,
            language=request.language,
            time_complexity=request.time_complexity,
            space_complexity=request.space_complexity
        )
        
        # Cache the explanation (24 hours TTL - longer since explanations are more stable)
        cache_service.set_analysis(
            **cache_key_params,
            result=result.dict() if hasattr(result, 'dict') else result,
            ttl=86400  # 24 hours
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Complexity explanation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Explanation generation failed",
                "message": "Failed to generate detailed explanation",
                "suggestion": "Please try again. If the problem persists, contact support.",
                "technical_details": str(e)
            }
        )


@app.options("/api/analyze")
async def analyze_options():
    """Handle CORS preflight for analyze endpoint."""
    return {"message": "OK"}


@app.post("/api/check-completeness")
async def check_completeness(code: str, language: str):
    """
    Check if the provided code is a complete solution.
    
    Args:
        code: The solution code to check
        language: Programming language of the code
        
    Returns:
        CompletenessCheck with is_complete flag, missing elements, and confidence
        
    Raises:
        HTTPException: If check fails
    """
    # Validate inputs
    code_validation = validation_service.validate_code(code, language)
    language_validation = validation_service.validate_language(language)
    
    if not code_validation.is_valid or not language_validation.is_valid:
        errors = code_validation.errors + language_validation.errors
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid input",
                "message": "Code or language validation failed",
                "validation_errors": [
                    {
                        "field": error.field,
                        "message": error.message,
                        "suggestion": error.suggestion
                    }
                    for error in errors
                ]
            }
        )
    
    # Validate API key is configured
    if not config.validate_config():
        raise HTTPException(
            status_code=503,
            detail={
                "error": "AI service not configured",
                "message": "The AI service is not properly configured",
                "suggestion": "Please contact the administrator to configure API keys"
            }
        )
    
    try:
        result = await ai_service.check_solution_completeness(
            code=code,
            language=language
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Completeness check failed",
                "message": "Failed to check solution completeness",
                "suggestion": "Please try again. If the problem persists, try a different analysis type.",
                "technical_details": str(e)
            }
        )


@app.post("/api/validate")
async def validate_inputs(
    problem_url: Optional[str] = None,
    code: Optional[str] = None,
    language: Optional[str] = None,
    analysis_type: Optional[str] = None
):
    """
    Validate inputs before analysis.
    
    Args:
        problem_url: Optional LeetCode problem URL to validate
        code: Optional code to validate
        language: Optional language to validate
        analysis_type: Optional analysis type to validate
        
    Returns:
        Validation results with detailed errors and suggestions
    """
    results = {}
    
    if problem_url is not None:
        url_result = validation_service.validate_problem_url(problem_url)
        results["problem_url"] = {
            "valid": url_result.is_valid,
            "errors": [
                {
                    "message": error.message,
                    "suggestion": error.suggestion,
                    "examples": error.examples
                }
                for error in url_result.errors
            ]
        }
    
    if code is not None and language is not None:
        code_result = validation_service.validate_code(code, language)
        results["code"] = {
            "valid": code_result.is_valid,
            "errors": [
                {
                    "message": error.message,
                    "suggestion": error.suggestion
                }
                for error in code_result.errors
            ],
            "warnings": code_result.warnings
        }
    
    if language is not None:
        lang_result = validation_service.validate_language(language)
        results["language"] = {
            "valid": lang_result.is_valid,
            "errors": [
                {
                    "message": error.message,
                    "suggestion": error.suggestion,
                    "examples": error.examples
                }
                for error in lang_result.errors
            ]
        }
    
    if analysis_type is not None:
        analysis_result = validation_service.validate_analysis_type(analysis_type)
        results["analysis_type"] = {
            "valid": analysis_result.is_valid,
            "errors": [
                {
                    "message": error.message,
                    "suggestion": error.suggestion,
                    "examples": error.examples
                }
                for error in analysis_result.errors
            ]
        }
    
    return {
        "validation_results": results,
        "all_valid": all(
            result.get("valid", True) for result in results.values()
        )
    }



@app.get("/api/history", response_model=HistoryResponse)
async def get_history(
    user_id: Optional[str] = Query(None, description="Optional user ID to filter by"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of entries to return"),
    offset: int = Query(0, ge=0, description="Number of entries to skip")
):
    """
    Get analysis history entries.
    
    Args:
        user_id: Optional user ID to filter by
        limit: Maximum number of entries to return (1-500)
        offset: Number of entries to skip for pagination
        
    Returns:
        HistoryResponse with entries and metadata
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        return history_service.get_history(user_id=user_id, limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve history: {str(e)}"
        )


@app.get("/api/history/{problem_slug}", response_model=List[HistoryEntry])
async def get_history_by_problem(
    problem_slug: str,
    user_id: Optional[str] = Query(None, description="Optional user ID to filter by")
):
    """
    Get history entries for a specific problem.
    
    Args:
        problem_slug: Problem slug to filter by (e.g., 'two-sum')
        user_id: Optional user ID to filter by
        
    Returns:
        List of HistoryEntry objects for the problem
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        entries = history_service.get_history_by_problem(problem_slug=problem_slug, user_id=user_id)
        return entries
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve problem history: {str(e)}"
        )


@app.delete("/api/history/{entry_id}")
async def delete_history_entry(
    entry_id: str,
    user_id: Optional[str] = Query(None, description="Optional user ID for ownership validation")
):
    """
    Delete a specific history entry.
    
    Args:
        entry_id: ID of the entry to delete
        user_id: Optional user ID for ownership validation
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If entry not found or deletion fails
    """
    try:
        deleted = history_service.delete_entry(entry_id=entry_id, user_id=user_id)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"History entry '{entry_id}' not found or access denied"
            )
        
        return {"message": "History entry deleted successfully", "entry_id": entry_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete history entry: {str(e)}"
        )


@app.post("/api/analyze")
async def analyze_code(request: AnalysisRequest):
    """
    Analyze code based on the specified analysis type.
    Supports: complexity, hints, optimization, debugging.
    
    Implements completeness checking workflow:
    - Hints: Always allowed (helps complete incomplete solutions)
    - Complexity/Optimization/Debugging: Requires complete solution
    
    Problem URL is now optional - if not provided, AI will infer the problem from code.
    
    Args:
        request: Analysis request with optional problem URL, code, language, and analysis type
        
    Returns:
        Analysis result based on the requested type, or guidance message if incomplete
        
    Raises:
        HTTPException: If analysis fails or invalid request
    """
    # Validate API key is configured
    if not config.validate_config():
        raise HTTPException(
            status_code=503,
            detail={
                "error": "AI service not configured",
                "message": "The AI service is not properly configured. Please contact the administrator.",
                "suggestion": "Ensure CLAUDE_API_KEY or OPENAI_API_KEY is set in environment variables.",
                "technical_details": "Missing API key configuration"
            }
        )
    
    # Comprehensive input validation (problem_url is now optional)
    validation_result = validation_service.validate_analysis_request(
        problem_url=request.problem_url,
        code=request.code,
        language=request.language,
        analysis_type=request.analysis_type
    )
    
    if not validation_result.is_valid:
        # Return detailed validation errors
        error_details = {
            "error": "Input validation failed",
            "message": "Please correct the following issues:",
            "validation_errors": [
                {
                    "field": error.field,
                    "message": error.message,
                    "suggestion": error.suggestion,
                    "examples": error.examples
                }
                for error in validation_result.errors
            ],
            "warnings": validation_result.warnings
        }
        raise HTTPException(status_code=400, detail=error_details)
    
    # Handle problem details - either from URL or let AI infer during analysis
    problem_description = None
    slug = None
    inferred_problem_info = None
    
    if request.problem_url:
        # Extract problem slug from URL
        slug = leetcode_parser.extract_problem_slug(request.problem_url)
        if not slug:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid problem URL",
                    "message": "Could not extract problem identifier from URL",
                    "suggestion": "Please use a valid LeetCode problem URL",
                    "examples": [
                        "https://leetcode.com/problems/two-sum/",
                        "https://leetcode.com/problems/reverse-linked-list/"
                    ]
                }
            )
        
        # Get problem details
        try:
            problem = await get_problem_details(slug)
            problem_description = f"{problem.title}: {problem.description}"
        except HTTPException as e:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to fetch problem details",
                    "message": "Could not retrieve problem information from LeetCode",
                    "suggestion": "Please verify the problem URL and try again. If the issue persists, LeetCode may be temporarily unavailable.",
                    "technical_details": str(e)
                }
            )
    else:
        # No URL provided - pass None to AI service, it will infer during analysis
        # This saves an API call by doing inference and analysis in one go
        problem_description = None
        slug = "inferred-problem"
        logger.info("No problem URL provided - AI will infer problem during analysis")
    
    # Check cache for existing analysis result (only if we have a real slug)
    cached_result = None
    if slug and slug not in ["inferred-problem", "unknown-problem"]:
        cached_result = cache_service.get_analysis(
            problem_slug=slug,
            code=request.code,
            language=request.language,
            analysis_type=request.analysis_type
        )
    
    if cached_result is not None:
        logger.info(f"Returning cached {request.analysis_type} analysis for {slug}")
        return cached_result
    
    # Check solution completeness for analysis types that require it
    # Hints are always allowed, but other analysis types need complete solutions
    requires_complete_solution = request.analysis_type in ["complexity", "optimization", "debugging"]
    
    if requires_complete_solution:
        try:
            completeness = await ai_service.check_solution_completeness(
                code=request.code,
                language=request.language
            )
            
            # If solution is incomplete, return guidance message
            if not completeness.is_complete:
                return {
                    "incomplete_solution": True,
                    "message": f"Your solution appears to be incomplete. {request.analysis_type.capitalize()} analysis requires a complete solution.",
                    "missing_elements": completeness.missing_elements,
                    "confidence": completeness.confidence,
                    "suggestion": "Would you like hints to help complete your solution? Switch to the 'Hints' option for guidance.",
                    "analysis_type": request.analysis_type
                }
        except Exception as e:
            # If completeness check fails, log but continue with analysis
            # This ensures the system is resilient to completeness check failures
            logger.warning(f"Completeness check failed: {str(e)}, proceeding with analysis")
    
    # Perform analysis based on type
    result = None
    try:
        if request.analysis_type == "complexity":
            result = await ai_service.analyze_time_complexity(
                problem_description=problem_description,
                code=request.code,
                language=request.language
            )
        elif request.analysis_type == "hints":
            result = await ai_service.generate_hints(
                problem_description=problem_description,
                code=request.code,
                language=request.language
            )
        elif request.analysis_type == "optimization":
            result = await ai_service.optimize_solution(
                problem_description=problem_description,
                code=request.code,
                language=request.language
            )
        elif request.analysis_type == "debugging":
            result = await ai_service.debug_solution(
                problem_description=problem_description,
                code=request.code,
                language=request.language
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid analysis type",
                    "message": f"Analysis type '{request.analysis_type}' is not supported",
                    "suggestion": "Please select one of: complexity, hints, optimization, debugging",
                    "examples": ["complexity", "hints", "optimization", "debugging"]
                }
            )
        
        # Save to history after successful analysis
        try:
            history_entry = HistoryCreateRequest(
                problem_slug=slug,
                problem_title=problem.title,
                code=request.code,
                language=request.language,
                analysis_type=request.analysis_type,
                result=result.dict() if hasattr(result, 'dict') else result
            )
            history_service.save_analysis(history_entry)
        except Exception as e:
            # Log error but don't fail the request if history save fails
            logger.error(f"Failed to save history: {str(e)}")
        
        # Cache the result for future requests
        try:
            cache_service.set_analysis(
                problem_slug=slug,
                code=request.code,
                language=request.language,
                analysis_type=request.analysis_type,
                result=result.dict() if hasattr(result, 'dict') else result
            )
        except Exception as e:
            # Log error but don't fail the request if caching fails
            logger.error(f"Failed to cache analysis result: {str(e)}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        # Handle AI service errors with detailed messages
        error_str = str(e).lower()
        
        if "rate limit" in error_str:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests to the AI service",
                    "suggestion": "Please wait a moment before trying again. The service has temporary usage limits to ensure fair access.",
                    "retry_after": 60
                }
            )
        elif "timeout" in error_str:
            raise HTTPException(
                status_code=504,
                detail={
                    "error": "Request timeout",
                    "message": "The AI service took too long to respond",
                    "suggestion": "Please try again. If the problem persists, try with a shorter code snippet.",
                    "retry_after": 5
                }
            )
        elif "network" in error_str or "connection" in error_str:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Network error",
                    "message": "Unable to connect to the AI service",
                    "suggestion": "Please check your internet connection and try again. The service may be temporarily unavailable.",
                    "retry_after": 10
                }
            )
        elif "authentication" in error_str or "api key" in error_str:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "AI service authentication failed",
                    "message": "The AI service credentials are invalid or expired",
                    "suggestion": "Please contact the administrator to update the API configuration.",
                    "technical_details": "API key authentication failed"
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Analysis failed",
                    "message": "An error occurred during analysis",
                    "suggestion": "Please try again. If the problem persists, try a different analysis type or contact support.",
                    "technical_details": str(e)
                }
            )
