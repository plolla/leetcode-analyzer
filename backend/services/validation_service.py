"""
Input validation service with comprehensive error handling.
Provides specific error messages and actionable guidance for all input types.
"""

import re
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel
from enum import Enum


class ValidationErrorType(str, Enum):
    """Types of validation errors."""
    INVALID_URL = "invalid_url"
    EMPTY_CODE = "empty_code"
    INVALID_LANGUAGE = "invalid_language"
    SYNTAX_ERROR = "syntax_error"
    CODE_TOO_SHORT = "code_too_short"
    CODE_TOO_LONG = "code_too_long"
    MISSING_FUNCTION = "missing_function"
    INVALID_ANALYSIS_TYPE = "invalid_analysis_type"


class ValidationError(BaseModel):
    """Represents a validation error with actionable guidance."""
    error_type: ValidationErrorType
    field: str
    message: str
    suggestion: str
    examples: Optional[List[str]] = None


class ValidationResult(BaseModel):
    """Result of input validation."""
    is_valid: bool
    errors: List[ValidationError] = []
    warnings: List[str] = []


class ValidationService:
    """Service for validating user inputs with comprehensive error handling."""
    
    # Supported programming languages
    SUPPORTED_LANGUAGES = {
        "python": ["py", "python", "python3"],
        "javascript": ["js", "javascript"],
        "typescript": ["ts", "typescript"],
        "java": ["java"],
        "cpp": ["cpp", "c++", "cxx"],
        "c": ["c"],
        "go": ["go", "golang"],
        "rust": ["rust", "rs"],
        "ruby": ["ruby", "rb"],
        "swift": ["swift"],
        "kotlin": ["kotlin", "kt"]
    }
    
    # LeetCode URL patterns
    LEETCODE_URL_PATTERNS = [
        r'^https?://(?:www\.)?leetcode\.com/problems/([\w-]+)/?$',
        r'^https?://(?:www\.)?leetcode\.com/problems/([\w-]+)/description/?$',
        r'^https?://(?:www\.)?leetcode\.com/problems/([\w-]+)/solutions?/?$',
        r'^https?://(?:www\.)?leetcode\.com/problems/([\w-]+)/editorial/?$',
    ]
    
    # Valid analysis types
    VALID_ANALYSIS_TYPES = ["complexity", "hints", "optimization", "debugging"]
    
    # Code length constraints
    MIN_CODE_LENGTH = 10  # Minimum characters for meaningful code
    MAX_CODE_LENGTH = 10000  # Maximum characters to prevent abuse
    
    def validate_problem_url(self, url: str) -> ValidationResult:
        """
        Validate a LeetCode problem URL.
        
        Args:
            url: The URL to validate
            
        Returns:
            ValidationResult with errors if invalid
        """
        errors = []
        
        # Check if URL is empty
        if not url or not url.strip():
            errors.append(ValidationError(
                error_type=ValidationErrorType.INVALID_URL,
                field="problem_url",
                message="Problem URL is required",
                suggestion="Please enter a valid LeetCode problem URL",
                examples=[
                    "https://leetcode.com/problems/two-sum/",
                    "https://leetcode.com/problems/add-two-numbers/description/"
                ]
            ))
            return ValidationResult(is_valid=False, errors=errors)
        
        # Check URL format
        url = url.strip()
        is_valid_format = any(
            re.match(pattern, url) for pattern in self.LEETCODE_URL_PATTERNS
        )
        
        if not is_valid_format:
            # Provide specific guidance based on common mistakes
            suggestions = []
            if "leetcode" not in url.lower():
                suggestions.append("URL must be from leetcode.com")
            if not url.startswith("http"):
                suggestions.append("URL must start with http:// or https://")
            if "/problems/" not in url:
                suggestions.append("URL must contain /problems/ path")
            
            errors.append(ValidationError(
                error_type=ValidationErrorType.INVALID_URL,
                field="problem_url",
                message="Invalid LeetCode problem URL format",
                suggestion=". ".join(suggestions) if suggestions else "Please use a valid LeetCode problem URL",
                examples=[
                    "https://leetcode.com/problems/two-sum/",
                    "https://leetcode.com/problems/reverse-linked-list/description/",
                    "https://leetcode.com/problems/binary-tree-inorder-traversal/"
                ]
            ))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_code(self, code: str, language: str) -> ValidationResult:
        """
        Validate solution code.
        
        Args:
            code: The code to validate
            language: Programming language
            
        Returns:
            ValidationResult with errors if invalid
        """
        errors = []
        warnings = []
        
        # Check if code is empty
        if not code or not code.strip():
            errors.append(ValidationError(
                error_type=ValidationErrorType.EMPTY_CODE,
                field="code",
                message="Solution code is required",
                suggestion="Please paste your solution code in the editor",
                examples=None
            ))
            return ValidationResult(is_valid=False, errors=errors)
        
        # Check code length
        code_length = len(code.strip())
        if code_length < self.MIN_CODE_LENGTH:
            errors.append(ValidationError(
                error_type=ValidationErrorType.CODE_TOO_SHORT,
                field="code",
                message=f"Code is too short ({code_length} characters)",
                suggestion=f"Please provide at least {self.MIN_CODE_LENGTH} characters of code",
                examples=None
            ))
        
        if code_length > self.MAX_CODE_LENGTH:
            errors.append(ValidationError(
                error_type=ValidationErrorType.CODE_TOO_LONG,
                field="code",
                message=f"Code is too long ({code_length} characters)",
                suggestion=f"Please keep code under {self.MAX_CODE_LENGTH} characters",
                examples=None
            ))
        
        # Basic syntax validation (language-specific)
        syntax_errors = self._check_basic_syntax(code, language)
        errors.extend(syntax_errors)
        
        # Check for function definition (warning only)
        if not self._has_function_definition(code, language):
            warnings.append(
                "Code may be missing a function definition. "
                "Most LeetCode solutions require a function/method."
            )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def validate_language(self, language: str) -> ValidationResult:
        """
        Validate programming language.
        
        Args:
            language: The language identifier
            
        Returns:
            ValidationResult with errors if invalid
        """
        errors = []
        
        if not language or not language.strip():
            errors.append(ValidationError(
                error_type=ValidationErrorType.INVALID_LANGUAGE,
                field="language",
                message="Programming language is required",
                suggestion="Please select a programming language",
                examples=list(self.SUPPORTED_LANGUAGES.keys())
            ))
            return ValidationResult(is_valid=False, errors=errors)
        
        # Normalize language name
        language_lower = language.lower().strip()
        
        # Check if language is supported
        is_supported = False
        for lang, aliases in self.SUPPORTED_LANGUAGES.items():
            if language_lower == lang or language_lower in aliases:
                is_supported = True
                break
        
        if not is_supported:
            errors.append(ValidationError(
                error_type=ValidationErrorType.INVALID_LANGUAGE,
                field="language",
                message=f"Language '{language}' is not supported",
                suggestion="Please select one of the supported languages",
                examples=list(self.SUPPORTED_LANGUAGES.keys())
            ))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_analysis_type(self, analysis_type: str) -> ValidationResult:
        """
        Validate analysis type.
        
        Args:
            analysis_type: The analysis type to validate
            
        Returns:
            ValidationResult with errors if invalid
        """
        errors = []
        
        if not analysis_type or not analysis_type.strip():
            errors.append(ValidationError(
                error_type=ValidationErrorType.INVALID_ANALYSIS_TYPE,
                field="analysis_type",
                message="Analysis type is required",
                suggestion="Please select an analysis type",
                examples=self.VALID_ANALYSIS_TYPES
            ))
            return ValidationResult(is_valid=False, errors=errors)
        
        if analysis_type.lower() not in self.VALID_ANALYSIS_TYPES:
            errors.append(ValidationError(
                error_type=ValidationErrorType.INVALID_ANALYSIS_TYPE,
                field="analysis_type",
                message=f"Analysis type '{analysis_type}' is not valid",
                suggestion="Please select a valid analysis type",
                examples=self.VALID_ANALYSIS_TYPES
            ))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_analysis_request(
        self,
        problem_url: str,
        code: str,
        language: str,
        analysis_type: str
    ) -> ValidationResult:
        """
        Validate complete analysis request.
        
        Args:
            problem_url: LeetCode problem URL
            code: Solution code
            language: Programming language
            analysis_type: Type of analysis
            
        Returns:
            ValidationResult with all validation errors
        """
        all_errors = []
        all_warnings = []
        
        # Validate each field
        url_result = self.validate_problem_url(problem_url)
        all_errors.extend(url_result.errors)
        all_warnings.extend(url_result.warnings)
        
        code_result = self.validate_code(code, language)
        all_errors.extend(code_result.errors)
        all_warnings.extend(code_result.warnings)
        
        language_result = self.validate_language(language)
        all_errors.extend(language_result.errors)
        all_warnings.extend(language_result.warnings)
        
        analysis_result = self.validate_analysis_type(analysis_type)
        all_errors.extend(analysis_result.errors)
        all_warnings.extend(analysis_result.warnings)
        
        return ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings
        )
    
    def _check_basic_syntax(self, code: str, language: str) -> List[ValidationError]:
        """
        Perform basic syntax checks for common errors.
        
        Args:
            code: The code to check
            language: Programming language
            
        Returns:
            List of validation errors
        """
        errors = []
        language_lower = language.lower()
        
        # Python-specific checks
        if language_lower in ["python", "py", "python3"]:
            # Check for common Python syntax issues
            if code.count("(") != code.count(")"):
                errors.append(ValidationError(
                    error_type=ValidationErrorType.SYNTAX_ERROR,
                    field="code",
                    message="Mismatched parentheses in Python code",
                    suggestion="Check that all opening parentheses have matching closing parentheses",
                    examples=None
                ))
            
            if code.count("[") != code.count("]"):
                errors.append(ValidationError(
                    error_type=ValidationErrorType.SYNTAX_ERROR,
                    field="code",
                    message="Mismatched brackets in Python code",
                    suggestion="Check that all opening brackets have matching closing brackets",
                    examples=None
                ))
        
        # Java/C++/JavaScript checks
        elif language_lower in ["java", "cpp", "c++", "javascript", "js", "typescript", "ts"]:
            if code.count("{") != code.count("}"):
                errors.append(ValidationError(
                    error_type=ValidationErrorType.SYNTAX_ERROR,
                    field="code",
                    message="Mismatched braces in code",
                    suggestion="Check that all opening braces have matching closing braces",
                    examples=None
                ))
            
            if code.count("(") != code.count(")"):
                errors.append(ValidationError(
                    error_type=ValidationErrorType.SYNTAX_ERROR,
                    field="code",
                    message="Mismatched parentheses in code",
                    suggestion="Check that all opening parentheses have matching closing parentheses",
                    examples=None
                ))
        
        return errors
    
    def _has_function_definition(self, code: str, language: str) -> bool:
        """
        Check if code contains a function definition.
        
        Args:
            code: The code to check
            language: Programming language
            
        Returns:
            True if function definition found
        """
        language_lower = language.lower()
        
        # Python
        if language_lower in ["python", "py", "python3"]:
            return bool(re.search(r'\bdef\s+\w+\s*\(', code))
        
        # Java
        elif language_lower == "java":
            return bool(re.search(r'\b(public|private|protected)?\s*(static)?\s*\w+\s+\w+\s*\(', code))
        
        # JavaScript/TypeScript
        elif language_lower in ["javascript", "js", "typescript", "ts"]:
            return bool(re.search(r'\b(function\s+\w+|const\s+\w+\s*=\s*\(|let\s+\w+\s*=\s*\(|var\s+\w+\s*=\s*\()', code))
        
        # C++/C
        elif language_lower in ["cpp", "c++", "c"]:
            return bool(re.search(r'\w+\s+\w+\s*\([^)]*\)\s*\{', code))
        
        # Default: assume it's okay
        return True


# Singleton instance
validation_service = ValidationService()
