"""
Centralized prompt templates for AI services.
This module contains all prompt templates used by both Claude and OpenAI services.
"""

from typing import Optional, Tuple


class AIPrompts:
    """Centralized prompt templates for AI analysis services."""
    
    @staticmethod
    def complexity_analysis(
        code: str,
        language: str,
        problem_description: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Generate prompts for time/space complexity analysis.
        
        Args:
            code: The solution code to analyze
            language: Programming language of the code
            problem_description: Optional problem description
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system = "You are an expert algorithm analyst. Provide accurate Big O complexity analysis."
        
        if problem_description:
            user = f"""Analyze the time and space complexity of the following {language} code for this LeetCode problem:

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
        else:
            user = f"""Analyze the time and space complexity of the following {language} code. First, infer what problem this code is solving based on the method names, data structures, and logic patterns, then provide the complexity analysis.

Code:
```{language}
{code}
```

Provide analysis in JSON format:
{{
    "time_complexity": "O(...)",
    "space_complexity": "O(...)",
    "explanation": "Detailed explanation of the complexity analysis",
    "key_operations": ["operation1", "operation2"],
    "improvements": ["suggestion1", "suggestion2"] (optional),
    "inferred_problem": "Description of what problem this code appears to solve",
    "inferred_problem_title": "Problem Name" (if you can identify the specific LeetCode problem)
}}

Be specific about the complexity and explain your reasoning."""
        
        return system, user
    
    @staticmethod
    def hints_generation(
        code: str,
        language: str,
        problem_description: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Generate prompts for progressive hints.
        
        Args:
            code: The current solution attempt
            language: Programming language of the code
            problem_description: Optional problem description
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system = "You are a helpful coding mentor. Provide hints that guide learning without spoiling solutions."
        
        if problem_description:
            user = f"""Generate progressive hints for solving this LeetCode problem. The user has written some code but needs guidance.

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
        else:
            user = f"""The user has written some code but needs guidance. First infer what problem they're trying to solve from the code, then provide progressive hints.

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

Start by mentioning what problem you think they're solving, then provide hints. Make hints increasingly specific but never give away the full solution."""
        
        return system, user
    
    @staticmethod
    def optimization_suggestions(
        code: str,
        language: str,
        problem_description: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Generate prompts for optimization suggestions.
        
        Args:
            code: The solution code to optimize
            language: Programming language of the code
            problem_description: Optional problem description
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system = "You are an expert at code optimization. Provide actionable suggestions."
        
        if problem_description:
            user = f"""Analyze this {language} solution and suggest optimizations:

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
        else:
            user = f"""Analyze this {language} solution and suggest optimizations. First infer what problem this code is solving, then provide optimization suggestions.

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

Start by mentioning what problem you think this solves, then focus on practical improvements with significant impact."""
        
        return system, user
    
    @staticmethod
    def debugging(
        code: str,
        language: str,
        problem_description: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Generate prompts for debugging analysis.
        
        Args:
            code: The solution code to debug
            language: Programming language of the code
            problem_description: Optional problem description
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system = "You are an expert debugger. Identify issues and provide clear fixes."
        
        if problem_description:
            user = f"""Debug this {language} code for potential issues:

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
        else:
            user = f"""Debug this {language} code for potential issues. First infer what problem this code is trying to solve, then identify bugs.

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
Start by mentioning what problem you think this solves, then be specific about line numbers and provide concrete fixes."""
        
        return system, user
    
    @staticmethod
    def completeness_check(code: str, language: str) -> Tuple[str, str]:
        """
        Generate prompts for solution completeness check.
        
        Args:
            code: The solution code to check
            language: Programming language of the code
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system = "You are a code reviewer. Determine if code is complete."
        
        user = f"""Analyze if this {language} code is a complete solution:

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
        
        return system, user
    
    @staticmethod
    def problem_inference(code: str, language: str) -> Tuple[str, str]:
        """
        Generate prompts for inferring the problem from code.
        
        Args:
            code: The solution code to analyze
            language: Programming language of the code
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system = "You are an expert at identifying coding problems from solution code. Analyze patterns and provide your best inference."
        
        user = f"""Analyze this {language} code and infer which LeetCode problem it's trying to solve:

Code:
```{language}
{code}
```

Based on the method names, data structures, algorithm patterns, and logic, identify the most likely LeetCode problem.

Return JSON format:
{{
    "inferred_problem": "Detailed description of the problem this code is solving",
    "confidence": 0.85,
    "suggested_title": "Two Sum" (optional - if you can identify the specific problem),
    "reasoning": "Explanation of why you think this is the problem (mention method names, patterns, etc.)"
}}

Look for clues like:
- Method names (e.g., twoSum, reverseList, maxProfit)
- Data structures used (arrays, linked lists, trees, graphs)
- Algorithm patterns (two pointers, sliding window, DFS, BFS, dynamic programming)
- Problem characteristics (searching, sorting, optimization)"""
        
        return system, user
