import json
from typing import List, Optional
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
    CompletenessCheck,
    ProblemInference
)
from .prompts import AIPrompts
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
            max_tokens=1000,
            temperature=temperature,
            system=system,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        return response.content[0].text
    
    async def analyze_time_complexity(
        self, 
        problem_description: Optional[str], 
        code: str, 
        language: str
    ) -> ComplexityAnalysis:
        """Analyze time and space complexity using Claude."""
        
        system, user_message = AIPrompts.complexity_analysis(
            code=code,
            language=language,
            problem_description=problem_description
        )
        
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
                improvements=None,
                inferred_problem="Unable to parse analysis" if not problem_description else None
            )
    
    async def generate_hints(
        self, 
        problem_description: Optional[str], 
        code: str, 
        language: str
    ) -> HintResponse:
        """Generate progressive hints using Claude."""
        
        system, user_message = AIPrompts.hints_generation(
            code=code,
            language=language,
            problem_description=problem_description
        )
        
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
        problem_description: Optional[str], 
        code: str, 
        language: str
    ) -> OptimizationResponse:
        """Suggest optimizations using Claude."""
        
        system, user_message = AIPrompts.optimization_suggestions(
            code=code,
            language=language,
            problem_description=problem_description
        )
        
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
        problem_description: Optional[str], 
        code: str, 
        language: str
    ) -> DebugResponse:
        """Debug solution using Claude."""
        
        system, user_message = AIPrompts.debugging(
            code=code,
            language=language,
            problem_description=problem_description
        )
        
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
        
        system, user_message = AIPrompts.completeness_check(
            code=code,
            language=language
        )
        
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
    
    async def infer_problem_from_code(
        self, 
        code: str, 
        language: str
    ) -> ProblemInference:
        """Infer the LeetCode problem from code structure and method names."""
        
        system, user_message = AIPrompts.problem_inference(
            code=code,
            language=language
        )
        
        response = self._call_claude(system, user_message, temperature=0.5)
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response)
            return ProblemInference(**data)
        except (json.JSONDecodeError, KeyError):
            # Fallback if JSON parsing fails
            return ProblemInference(
                inferred_problem=response,
                confidence=0.5,
                suggested_title=None,
                reasoning="Unable to parse structured response"
            )


# Singleton instance
claude_service = ClaudeService()
