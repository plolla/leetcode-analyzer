/**
 * Type definitions for analysis results and related data structures
 */

export interface ComplexityAnalysisResult {
  time_complexity: string;
  space_complexity: string;
  explanation: string;
  key_operations: string[];
  improvements?: string[];
  inferred_problem?: string;  // Present when no problem URL was provided
  inferred_problem_title?: string;  // Suggested problem title if identified
}

export interface HintResult {
  hints: string[];
  progressive: boolean;
  next_steps: string[];
}

export interface OptimizationSuggestion {
  area: string;
  current_approach: string;
  suggested_approach: string;
  impact: string;
}

export interface OptimizationResult {
  current_complexity: string;
  optimized_complexity: string;
  suggestions: OptimizationSuggestion[];
  code_examples?: string[];
}

export interface Issue {
  line: number | null;
  description: string;
  severity: string;
}

export interface Fix {
  issue: string;
  suggestion: string;
  code_example?: string;
}

export interface DebugResult {
  issues: Issue[];
  fixes: Fix[];
  test_cases: string[];
}

export interface IncompleteSolutionResult {
  incomplete_solution: true;
  message: string;
  missing_elements: string[];
  confidence: number;
  suggestion: string;
  analysis_type: string;
}

export type AnalysisResult = 
  | ComplexityAnalysisResult 
  | HintResult 
  | OptimizationResult 
  | DebugResult 
  | IncompleteSolutionResult;

export interface ProblemExample {
  input: string;
  output: string;
  explanation?: string;
}

export interface ProblemDetails {
  slug: string;
  title: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  description: string;
  constraints: string[];
  examples: ProblemExample[];
}
