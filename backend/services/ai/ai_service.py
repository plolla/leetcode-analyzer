from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum


class AnalysisType(str, Enum):
    COMPLEXITY = "complexity"
    HINTS = "hints"
    OPTIMIZATION = "optimization"
    DEBUGGING = "debugging"


# Response Models
class ComplexityAnalysis(BaseModel):
    time_complexity: str
    space_complexity: str
    explanation: str
    key_operations: List[str]
    improvements: Optional[List[str]] = None
    inferred_problem: Optional[str] = None  # Present when no problem URL was provided
    inferred_problem_title: Optional[str] = None  # Suggested problem title if identified


class QuickComplexityAnalysis(BaseModel):
    """Quick complexity analysis with just Big O notation."""
    time_complexity: str
    space_complexity: str
    inferred_problem: Optional[str] = None  # Present when no problem URL was provided
    inferred_problem_title: Optional[str] = None  # Suggested problem title if identified


class ComplexityExplanation(BaseModel):
    """Detailed explanation for complexity analysis."""
    explanation: str
    key_operations: List[str]
    improvements: Optional[List[str]] = None


class HintResponse(BaseModel):
    hints: List[str]
    progressive: bool
    next_steps: List[str]


class OptimizationSuggestion(BaseModel):
    area: str
    current_approach: str
    suggested_approach: str
    impact: str


class OptimizationResponse(BaseModel):
    current_complexity: str
    optimized_complexity: str
    suggestions: List[OptimizationSuggestion]
    code_examples: Optional[List[str]] = None


class Issue(BaseModel):
    line: Optional[int]
    description: str
    severity: str


class Fix(BaseModel):
    issue: str
    suggestion: str
    code_example: Optional[str] = None


class DebugResponse(BaseModel):
    issues: List[Issue]
    fixes: List[Fix]
    test_cases: List[str]


class CompletenessCheck(BaseModel):
    is_complete: bool
    missing_elements: List[str]
    confidence: float


class ProblemInference(BaseModel):
    inferred_problem: str
    confidence: float
    suggested_title: Optional[str] = None
    reasoning: str


# Abstract AI Service Interface
class AIService(ABC):
    """Abstract base class for AI service providers."""
    
    @abstractmethod
    async def analyze_time_complexity(
        self, 
        problem_description: Optional[str], 
        code: str, 
        language: str
    ) -> ComplexityAnalysis:
        """
        Analyze the time and space complexity of the given code.
        
        Args:
            problem_description: The LeetCode problem description (optional - will infer if None)
            code: The solution code to analyze
            language: Programming language of the code
            
        Returns:
            ComplexityAnalysis with time/space complexity and explanations
        """
        pass
    
    @abstractmethod
    async def analyze_complexity_quick(
        self, 
        problem_description: Optional[str], 
        code: str, 
        language: str
    ) -> QuickComplexityAnalysis:
        """
        Quick complexity analysis - returns only Big O notation.
        Optimized for speed with minimal prompt and response.
        
        Args:
            problem_description: The LeetCode problem description (optional - will infer if None)
            code: The solution code to analyze
            language: Programming language of the code
            
        Returns:
            QuickComplexityAnalysis with just time/space complexity
        """
        pass
    
    @abstractmethod
    async def explain_complexity(
        self, 
        problem_description: Optional[str], 
        code: str, 
        language: str,
        time_complexity: str,
        space_complexity: str
    ) -> ComplexityExplanation:
        """
        Generate detailed explanation for complexity analysis.
        Uses the already-computed Big O notation to provide context.
        
        Args:
            problem_description: The LeetCode problem description (optional)
            code: The solution code
            language: Programming language of the code
            time_complexity: Already computed time complexity (e.g., "O(n)")
            space_complexity: Already computed space complexity (e.g., "O(1)")
            
        Returns:
            ComplexityExplanation with detailed explanation and suggestions
        """
        pass
    
    @abstractmethod
    async def generate_hints(
        self, 
        problem_description: Optional[str], 
        code: str, 
        language: str
    ) -> HintResponse:
        """
        Generate progressive hints for solving the problem.
        
        Args:
            problem_description: The LeetCode problem description (optional - will infer if None)
            code: The current solution attempt (may be incomplete)
            language: Programming language of the code
            
        Returns:
            HintResponse with progressive hints and next steps
        """
        pass
    
    @abstractmethod
    async def optimize_solution(
        self, 
        problem_description: Optional[str], 
        code: str, 
        language: str
    ) -> OptimizationResponse:
        """
        Suggest optimizations for the given solution.
        
        Args:
            problem_description: The LeetCode problem description (optional - will infer if None)
            code: The solution code to optimize
            language: Programming language of the code
            
        Returns:
            OptimizationResponse with suggestions and complexity improvements
        """
        pass
    
    @abstractmethod
    async def debug_solution(
        self, 
        problem_description: Optional[str], 
        code: str, 
        language: str
    ) -> DebugResponse:
        """
        Debug the solution and identify issues.
        
        Args:
            problem_description: The LeetCode problem description (optional - will infer if None)
            code: The solution code to debug
            language: Programming language of the code
            
        Returns:
            DebugResponse with identified issues and fixes
        """
        pass
    
    @abstractmethod
    async def check_solution_completeness(
        self, 
        code: str, 
        language: str
    ) -> CompletenessCheck:
        """
        Check if the solution is complete.
        
        Args:
            code: The solution code to check
            language: Programming language of the code
            
        Returns:
            CompletenessCheck indicating if solution is complete
        """
        pass
    
    @abstractmethod
    async def infer_problem_from_code(
        self, 
        code: str, 
        language: str
    ) -> ProblemInference:
        """
        Infer the LeetCode problem from the code structure and method names.
        
        Args:
            code: The solution code to analyze
            language: Programming language of the code
            
        Returns:
            ProblemInference with inferred problem details
        """
        pass
