import json
from typing import List
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from .ai_service import (
    AIService,
    ComplexityAnalysis,
    HintResponse,
    OptimizationResponse,
    OptimizationSuggestion,
    DebugResponse,
    Issue,
    Fix,
    CompletenessCheck
)
from config import config


class OpenAIService(AIService):
    """OpenAI-based AI service implementation."""
    
    def __init__(self):
        self._client = None
        self.model = config.OPENAI_MODEL
    
    def _get_client(self):
        """Get or create OpenAI client."""
        if self._client is None:
            if not config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not configured")
            self._client = OpenAI(api_key=config.OPENAI_API_KEY)
        return self._client
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _call_openai(self, messages: List[dict], temperature: float = 0.7) -> str:
        """
        Call OpenAI API with retry logic.
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            
        Returns:
            Response content as string
        """
        client = self._get_client()
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=1500
        )
        return response.choices[0].message.content
    
    def analyze_time_complexity(
        self, 
        problem_description: str, 
        code: str, 
        language: str
    ) -> ComplexityAnalysis:
        """Analyze time and space complexity using OpenAI."""
        
        prompt = f"""Analyze the time and space complexity of the following {language} code for this LeetCode problem:

Problem: {problem_description[:500]}

Code:
```{language}
{code}
```

Provide a detailed analysis in JSON format with the following structure:
{{
    "time_complexity": "O(...)",
    "space_complexity": "O(...)",
    "explanation": "Detailed explanation of the complexity analysis",
    "key_operations": ["operation1", "operation2"],
    "improvements": ["suggestion1", "suggestion2"] (optional)
}}

Be specific about the complexity and explain your reasoning."""

        messages = [
            {"role": "system", "content": "You are an expert algorithm analyst. Provide accurate Big O complexity analysis."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._call_openai(messages, temperature=0.3)
        
        # Parse JSON response
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response)
            return ComplexityAnalysis(**data)
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback if JSON parsing fails
            return ComplexityAnalysis(
                time_complexity="O(n)",
                space_complexity="O(1)",
                explanation=response,
                key_operations=["See explanation"],
                improvements=None
            )
    
    def generate_hints(
        self, 
        problem_description: str, 
        code: str, 
        language: str
    ) -> HintResponse:
        """Generate progressive hints using OpenAI."""
        
        prompt = f"""Generate progressive hints for solving this LeetCode problem. The user has written some code but needs guidance.

Problem: {problem_description[:500]}

Current Code:
```{language}
{code}
```

Provide 3-5 progressive hints that guide toward a solution WITHOUT revealing the complete implementation. Return JSON format:
{{
    "hints": ["hint1", "hint2", "hint3"],
    "progressive": true,
    "next_steps": ["step1", "step2"]
}}

Make hints increasingly specific but never give away the full solution."""

        messages = [
            {"role": "system", "content": "You are a helpful coding mentor. Provide hints that guide learning without spoiling solutions."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._call_openai(messages, temperature=0.7)
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response)
            return HintResponse(**data)
        except (json.JSONDecodeError, KeyError):
            return HintResponse(
                hints=[response],
                progressive=True,
                next_steps=["Review the hints and try implementing them"]
            )
    
    def optimize_solution(
        self, 
        problem_description: str, 
        code: str, 
        language: str
    ) -> OptimizationResponse:
        """Suggest optimizations using OpenAI."""
        
        prompt = f"""Analyze this {language} solution and suggest optimizations:

Problem: {problem_description[:500]}

Code:
```{language}
{code}
```

Provide optimization suggestions in JSON format:
{{
    "current_complexity": "O(...)",
    "optimized_complexity": "O(...)",
    "suggestions": [
        {{
            "area": "Data structure",
            "current_approach": "Using array",
            "suggested_approach": "Use hash map",
            "impact": "Reduces time from O(n²) to O(n)"
        }}
    ],
    "code_examples": ["example1", "example2"] (optional)
}}

Focus on practical improvements with significant impact."""

        messages = [
            {"role": "system", "content": "You are an expert at code optimization. Provide actionable suggestions."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._call_openai(messages, temperature=0.5)
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response)
            # Convert suggestion dicts to OptimizationSuggestion objects
            if "suggestions" in data:
                data["suggestions"] = [OptimizationSuggestion(**s) for s in data["suggestions"]]
            return OptimizationResponse(**data)
        except (json.JSONDecodeError, KeyError):
            return OptimizationResponse(
                current_complexity="Unknown",
                optimized_complexity="Unknown",
                suggestions=[OptimizationSuggestion(
                    area="General",
                    current_approach="Current implementation",
                    suggested_approach=response,
                    impact="See suggestion"
                )],
                code_examples=None
            )
    
    def debug_solution(
        self, 
        problem_description: str, 
        code: str, 
        language: str
    ) -> DebugResponse:
        """Debug solution using OpenAI."""
        
        prompt = f"""Debug this {language} code for potential issues:

Problem: {problem_description[:500]}

Code:
```{language}
{code}
```

Identify bugs and provide fixes in JSON format:
{{
    "issues": [
        {{"line": 5, "description": "Off-by-one error", "severity": "high"}},
        {{"line": null, "description": "Missing edge case", "severity": "medium"}}
    ],
    "fixes": [
        {{"issue": "Off-by-one error", "suggestion": "Change < to <=", "code_example": "for i in range(len(arr)):"}}
    ],
    "test_cases": ["Test with empty array", "Test with single element", "Test with duplicate values"]
}}

IMPORTANT: test_cases must be an array of strings, not objects.
Be specific about line numbers and provide concrete fixes."""

        messages = [
            {"role": "system", "content": "You are an expert debugger. Identify issues and provide clear fixes."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._call_openai(messages, temperature=0.3)
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response)
            # Convert dicts to proper objects
            if "issues" in data:
                data["issues"] = [Issue(**i) for i in data["issues"]]
            if "fixes" in data:
                data["fixes"] = [Fix(**f) for f in data["fixes"]]
            # Ensure test_cases are strings
            if "test_cases" in data:
                test_cases = []
                for tc in data["test_cases"]:
                    if isinstance(tc, dict):
                        # If it's a dict, convert to string representation
                        test_cases.append(str(tc.get("input", tc)))
                    else:
                        test_cases.append(str(tc))
                data["test_cases"] = test_cases
            return DebugResponse(**data)
        except (json.JSONDecodeError, KeyError):
            return DebugResponse(
                issues=[Issue(line=None, description=response, severity="unknown")],
                fixes=[Fix(issue="See description", suggestion="Review the analysis", code_example=None)],
                test_cases=["Test with provided examples"]
            )
    
    def check_solution_completeness(
        self, 
        code: str, 
        language: str
    ) -> CompletenessCheck:
        """Check if solution is complete using OpenAI."""
        
        prompt = f"""Analyze if this {language} code is a complete solution:

Code:
```{language}
{code}
```

Return JSON format:
{{
    "is_complete": true/false,
    "missing_elements": ["element1", "element2"],
    "confidence": 0.95
}}

A complete solution should have proper function definition, logic implementation, and return statement."""

        messages = [
            {"role": "system", "content": "You are a code reviewer. Determine if code is complete."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._call_openai(messages, temperature=0.3)
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response)
            return CompletenessCheck(**data)
        except (json.JSONDecodeError, KeyError):
            # Default to complete if we can't parse
            return CompletenessCheck(
                is_complete=True,
                missing_elements=[],
                confidence=0.5
            )


# Singleton instance
openai_service = OpenAIService()
