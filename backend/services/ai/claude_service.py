import json
from typing import List, Optional
from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential
from .ai_service import (
    AIService,
    ComplexityAnalysis,
    QuickComplexityAnalysis,
    ComplexityExplanation,
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
            
            # Validate required fields
            if 'time_complexity' not in data:
                data['time_complexity'] = "Unknown (Try again)"
            if 'space_complexity' not in data:
                data['space_complexity'] = "Unknown (Try again)"
            if 'explanation' not in data:
                data['explanation'] = response
            if 'key_operations' not in data or not isinstance(data['key_operations'], list):
                data['key_operations'] = ["See explanation"]
            
            return ComplexityAnalysis(**data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error parsing complexity response: {e}")
            print(f"Raw response: {response[:500]}")
            
            # Fallback if JSON parsing fails
            return ComplexityAnalysis(
                time_complexity="O(n)",
                space_complexity="O(1)",
                explanation=response if len(response) < 1000 else "Unable to analyze complexity. Please try again.",
                key_operations=["See explanation"],
                improvements=None,
                inferred_problem="Unable to parse analysis" if not problem_description else None
            )
    
    async def analyze_complexity_quick(
        self, 
        problem_description: Optional[str], 
        code: str, 
        language: str
    ) -> QuickComplexityAnalysis:
        """Quick complexity analysis - returns only Big O notation."""
        
        system, user_message = AIPrompts.complexity_analysis_quick(
            code=code,
            language=language,
            problem_description=problem_description
        )
        
        # Use lower temperature and max_tokens for faster response
        client = self._get_client()
        response = client.messages.create(
            model=self.model,
            max_tokens=200,  # Much smaller for quick response
            temperature=0.1,  # Lower temperature for consistency
            system=system,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        response_text = response.content[0].text
        
        # Parse JSON response
        try:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response_text)
            return QuickComplexityAnalysis(**data)
        except (json.JSONDecodeError, KeyError) as e:
            # Don't return fallback - raise error instead
            raise Exception(f"Failed to parse AI response for complexity analysis: {str(e)}")
    
    async def explain_complexity(
        self, 
        problem_description: Optional[str], 
        code: str, 
        language: str,
        time_complexity: str,
        space_complexity: str
    ) -> ComplexityExplanation:
        """Generate detailed explanation for complexity analysis."""
        
        system, user_message = AIPrompts.complexity_explanation(
            code=code,
            language=language,
            time_complexity=time_complexity,
            space_complexity=space_complexity,
            problem_description=problem_description
        )
        
        response = self._call_claude(system, user_message, temperature=0.3)
        
        # Parse JSON response
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response)
            return ComplexityExplanation(**data)
        except (json.JSONDecodeError, KeyError) as e:
            # Don't return fallback - raise error instead
            raise Exception(f"Failed to parse AI response for complexity explanation: {str(e)}")
    
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
            
            # Validate that required fields exist and are correct types
            if not isinstance(data.get('hints'), list):
                raise ValueError("hints field must be a list")
            if not data.get('hints'):
                raise ValueError("hints list cannot be empty")
            if 'progressive' not in data:
                data['progressive'] = True
            if 'next_steps' not in data:
                data['next_steps'] = []
            elif not isinstance(data['next_steps'], list):
                data['next_steps'] = []
            
            return HintResponse(**data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Log the error for debugging
            print(f"Error parsing hints response: {e}")
            print(f"Raw response: {response[:500]}")
            
            # Return a fallback response with the raw text as a single hint
            return HintResponse(
                hints=[response if len(response) < 500 else "Unable to generate hints. Please try again with a different code sample."],
                progressive=True,
                next_steps=["Review the hint and try implementing a solution"]
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
            
            # Validate required fields
            if 'current_complexity' not in data:
                data['current_complexity'] = "Unknown"
            if 'optimized_complexity' not in data:
                data['optimized_complexity'] = "Unknown"
            if 'suggestions' not in data or not isinstance(data['suggestions'], list):
                raise ValueError("suggestions field must be a list")
            if not data['suggestions']:
                raise ValueError("suggestions list cannot be empty")
            
            # Convert suggestion dicts to OptimizationSuggestion objects
            validated_suggestions = []
            for s in data["suggestions"]:
                if isinstance(s, dict):
                    # Ensure all required fields exist
                    validated_suggestions.append(OptimizationSuggestion(
                        area=s.get('area', 'General'),
                        current_approach=s.get('current_approach', 'Current implementation'),
                        suggested_approach=s.get('suggested_approach', 'See details'),
                        impact=s.get('impact', 'Unknown impact')
                    ))
            data["suggestions"] = validated_suggestions
            
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
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error parsing optimization response: {e}")
            print(f"Raw response: {response[:500]}")
            
            return OptimizationResponse(
                current_complexity="Unknown",
                optimized_complexity="Unknown",
                suggestions=[OptimizationSuggestion(
                    area="General",
                    current_approach="Current implementation",
                    suggested_approach=response if len(response) < 500 else "Unable to generate optimization suggestions. Please try again.",
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
            
            # Validate and convert issues
            if "issues" not in data or not isinstance(data["issues"], list):
                data["issues"] = []
            validated_issues = []
            for i in data["issues"]:
                if isinstance(i, dict):
                    validated_issues.append(Issue(
                        line=i.get('line'),
                        description=i.get('description', 'Unknown issue'),
                        severity=i.get('severity', 'unknown')
                    ))
            data["issues"] = validated_issues
            
            # Validate and convert fixes
            if "fixes" not in data or not isinstance(data["fixes"], list):
                data["fixes"] = []
            validated_fixes = []
            for f in data["fixes"]:
                if isinstance(f, dict):
                    validated_fixes.append(Fix(
                        issue=f.get('issue', 'Unknown issue'),
                        suggestion=f.get('suggestion', 'See details'),
                        code_example=f.get('code_example')
                    ))
            data["fixes"] = validated_fixes
            
            # Ensure test_cases are strings
            if "test_cases" not in data or not isinstance(data["test_cases"], list):
                data["test_cases"] = ["Test with edge cases"]
            else:
                test_cases = []
                for tc in data["test_cases"]:
                    if isinstance(tc, dict):
                        # If it's a dict, convert to string representation
                        test_cases.append(str(tc.get("input", tc)))
                    else:
                        test_cases.append(str(tc))
                data["test_cases"] = test_cases
            
            return DebugResponse(**data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error parsing debug response: {e}")
            print(f"Raw response: {response[:500]}")
            
            return DebugResponse(
                issues=[Issue(line=None, description=response if len(response) < 500 else "Unable to analyze code. Please try again.", severity="unknown")],
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
