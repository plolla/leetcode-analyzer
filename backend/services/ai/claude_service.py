import json
from typing import List
from anthropic import Anthropic
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


class ClaudeService(AIService):
    """Claude-based AI service implementation."""
    
    def __init__(self):
        self._client = None
        self.model = config.CLAUDE_MODEL
    
    def _get_client(self):
        """Get or create Claude client."""
        if self._client is None:
            if not config.CLAUDE_API_KEY:
                raise ValueError("CLAUDE_API_KEY not configured")
            self._client = Anthropic(api_key=config.CLAUDE_API_KEY)
        return self._client
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _call_claude(self, system: str, user_message: str, temperature: float = 0.7) -> str:
        """
        Call Claude API with retry logic.
        
        Args:
            system: System prompt
            user_message: User message
            temperature: Sampling temperature
            
        Returns:
            Response content as string
        """
        client = self._get_client()
        response = client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=temperature,
            system=system,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        return response.content[0].text
    
    async def analyze_time_complexity(
        self, 
        problem_description: str, 
        code: str, 
        language: str
    ) -> ComplexityAnalysis:
        """Analyze time and space complexity using Claude."""
        
        system = "You are an expert algorithm analyst. Provide accurate Big O complexity analysis."
        
        user_message = f"""Analyze the time and space complexity of the following {language} code for this LeetCode problem:

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

        response = self._call_claude(system, user_message, temperature=0.3)
        
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
    
    async def generate_hints(
        self, 
        problem_description: str, 
        code: str, 
        language: str
    ) -> HintResponse:
        """Generate progressive hints using Claude."""
        
        system = "You are a helpful coding mentor. Provide hints that guide learning without spoiling solutions."
        
        user_message = f"""Generate progressive hints for solving this LeetCode problem. The user has written some code but needs guidance.

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

        response = self._call_claude(system, user_message, temperature=0.7)
        
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
    
    async def optimize_solution(
        self, 
        problem_description: str, 
        code: str, 
        language: str
    ) -> OptimizationResponse:
        """Suggest optimizations using Claude."""
        
        system = "You are an expert at code optimization. Provide actionable suggestions."
        
        user_message = f"""Analyze this {language} solution and suggest optimizations:

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

        response = self._call_claude(system, user_message, temperature=0.5)
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response)
            # Convert suggestion dicts to OptimizationSuggestion objects
            if "suggestions" in data:
                data["suggestions"] = [OptimizationSuggestion(**s) for s in data["suggestions"]]
            
            # Handle code_examples that might be dicts instead of strings
            if "code_examples" in data and data["code_examples"]:
                examples = []
                for example in data["code_examples"]:
                    if isinstance(example, dict):
                        # Extract the code from dict format
                        if "code" in example:
                            examples.append(example["code"])
                        elif "title" in example and "code" in example:
                            examples.append(f"{example['title']}\n{example['code']}")
                        else:
                            # Convert dict to string representation
                            examples.append(str(example))
                    else:
                        examples.append(str(example))
                data["code_examples"] = examples
            
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
    
    async def debug_solution(
        self, 
        problem_description: str, 
        code: str, 
        language: str
    ) -> DebugResponse:
        """Debug solution using Claude."""
        
        system = "You are an expert debugger. Identify issues and provide clear fixes."
        
        user_message = f"""Debug this {language} code for potential issues:

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

        response = self._call_claude(system, user_message, temperature=0.3)
        
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
    
    async def check_solution_completeness(
        self, 
        code: str, 
        language: str
    ) -> CompletenessCheck:
        """Check if solution is complete using Claude."""
        
        system = "You are a code reviewer. Determine if code is complete."
        
        user_message = f"""Analyze if this {language} code is a complete solution:

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

        response = self._call_claude(system, user_message, temperature=0.3)
        
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
claude_service = ClaudeService()
