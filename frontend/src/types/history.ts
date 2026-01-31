// History entry types
export interface HistoryEntryData {
  id: string;
  problem_slug: string;
  problem_title: string;
  code: string;
  language: string;
  analysis_type: string;
  result: AnalysisResult;
  timestamp: string;
  user_id?: string;
}

// Analysis result types
export type AnalysisResult = 
  | ComplexityAnalysisResult 
  | HintResult 
  | OptimizationResult 
  | DebugResult;

export interface ComplexityAnalysisResult {
  time_complexity: string;
  space_complexity: string;
  explanation: string;
  key_operations: string[];
  improvements?: string[];
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
