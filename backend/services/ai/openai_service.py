import json
from typing import List, Optional
from openai import OpenAI
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
        import logging
        logger = logging.getLogger(__name__)
        
        client = self._get_client()
        # GPT-5 models only support temperature=1
        if "gpt-5" in self.model:
            temperature = 1.0
        # Use max_completion_tokens for newer models (GPT-5+), max_tokens for older models
        token_param = "max_completion_tokens" if "gpt-5" in self.model or "gpt-4" in self.model else "max_tokens"
        
        logger.info(f"Calling OpenAI with model={self.model}, {token_param}=2000, temperature={temperature}")
        
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            **{token_param: 2000}
        )
        
        content = response.choices[0].message.content
        logger.info(f"OpenAI response length: {len(content) if content else 0} characters")
        logger.debug(f"OpenAI response preview: {content[:200] if content else 'None'}")
        
        return content
    
    def analyze_time_complexity(
        self, 
        problem_description: Optional[str], 
        code: str, 
        language: str
    ) -> ComplexityAnalysis:
        """Analyze time and space complexity using OpenAI."""
        
        import logging
        logger = logging.getLogger(__name__)
        
        system, prompt = AIPrompts.complexity_analysis(
            code=code,
            language=language,
            problem_description=problem_description
        )

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
        
        response = self._call_openai(messages, temperature=0.3)
        
        logger.info(f"Raw OpenAI response for complexity analysis: {response[:500]}")
        
        # Parse JSON response
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            logger.info(f"Extracted JSON: {response[:500]}")
            
            data = json.loads(response)
            logger.info(f"Parsed data keys: {data.keys()}")
            return ComplexityAnalysis(**data)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            logger.error(f"Response was: {response}")
            # Fallback if JSON parsing fails
            return ComplexityAnalysis(
                time_complexity="O(n)",
                space_complexity="O(1)",
                explanation=response,
                key_operations=["See explanation"],
                improvements=None,
                inferred_problem="Unable to parse analysis" if not problem_description else None
            )
    
    def analyze_complexity_quick(
        self, 
        problem_description: Optional[str], 
        code: str, 
        language: str
    ) -> QuickComplexityAnalysis:
        """Quick complexity analysis - returns only Big O notation."""
        
        import logging
        logger = logging.getLogger(__name__)
        
        system, prompt = AIPrompts.complexity_analysis_quick(
            code=code,
            language=language,
            problem_description=problem_description
        )

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
        
        # Use lower temperature and smaller max_tokens for faster response
        client = self._get_client()
        if "gpt-5" in self.model:
            temperature = 1.0
        else:
            temperature = 0.1
        
        token_param = "max_completion_tokens" if "gpt-5" in self.model or "gpt-4" in self.model else "max_tokens"
        
        logger.info(f"Quick complexity analysis with model={self.model}, {token_param}=200")
        
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            **{token_param: 200}  # Much smaller for quick response
        )
        
        response_text = response.choices[0].message.content
        logger.info(f"Quick analysis response: {response_text}")
        
        # Parse JSON response
        try:
            if not response_text or response_text.strip() == '':
                logger.error("Empty response from OpenAI")
                raise Exception("AI returned an empty response. Please try again.")
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response_text)
            return QuickComplexityAnalysis(**data)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse quick analysis response: {e}")
            logger.error(f"Response was: {response_text}")
            # Don't return fallback - raise error instead
            raise Exception(f"Failed to parse AI response for complexity analysis: {str(e)}")
    
    def explain_complexity(
        self, 
        problem_description: Optional[str], 
        code: str, 
        language: str,
        time_complexity: str,
        space_complexity: str
    ) -> ComplexityExplanation:
        """Generate detailed explanation for complexity analysis."""
        
        import logging
        logger = logging.getLogger(__name__)
        
        system, prompt = AIPrompts.complexity_explanation(
            code=code,
            language=language,
            time_complexity=time_complexity,
            space_complexity=space_complexity,
            problem_description=problem_description
        )

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
        
        response = self._call_openai(messages, temperature=0.3)
        
        logger.info(f"Complexity explanation response: {response[:500]}")
        
        # Parse JSON response
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response)
            return ComplexityExplanation(**data)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse explanation response: {e}")
            # Don't return fallback - raise error instead
            raise Exception(f"Failed to parse AI response for complexity explanation: {str(e)}")
    
    def generate_hints(
        self, 
        problem_description: Optional[str], 
        code: str, 
        language: str
    ) -> HintResponse:
        """Generate progressive hints using OpenAI."""
        
        import logging
        logger = logging.getLogger(__name__)
        
        system, prompt = AIPrompts.hints_generation(
            code=code,
            language=language,
            problem_description=problem_description
        )

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
        
        response = self._call_openai(messages, temperature=0.7)
        
        logger.info(f"Raw OpenAI response for hints: {response[:500]}")
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            logger.info(f"Extracted JSON for hints: {response[:500]}")
            
            data = json.loads(response)
            logger.info(f"Parsed hints data keys: {data.keys()}")
            logger.info(f"Number of hints: {len(data.get('hints', []))}")
            return HintResponse(**data)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse hints response: {e}")
            logger.error(f"Response was: {response}")
            return HintResponse(
                hints=[response],
                progressive=True,
                next_steps=["Review the hints and try implementing them"]
            )
    
    def optimize_solution(
        self, 
        problem_description: Optional[str], 
        code: str, 
        language: str
    ) -> OptimizationResponse:
        """Suggest optimizations using OpenAI."""
        
        system, prompt = AIPrompts.optimization_suggestions(
            code=code,
            language=language,
            problem_description=problem_description
        )

        messages = [
            {"role": "system", "content": system},
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
        problem_description: Optional[str], 
        code: str, 
        language: str
    ) -> DebugResponse:
        """Debug solution using OpenAI."""
        
        system, prompt = AIPrompts.debugging(
            code=code,
            language=language,
            problem_description=problem_description
        )

        messages = [
            {"role": "system", "content": system},
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
        
        system, prompt = AIPrompts.completeness_check(
            code=code,
            language=language
        )

        messages = [
            {"role": "system", "content": system},
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
    
    def infer_problem_from_code(
        self, 
        code: str, 
        language: str
    ) -> ProblemInference:
        """Infer the LeetCode problem from code structure and method names."""
        
        system, prompt = AIPrompts.problem_inference(
            code=code,
            language=language
        )

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
        
        response = self._call_openai(messages, temperature=0.5)
        
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
openai_service = OpenAIService()
