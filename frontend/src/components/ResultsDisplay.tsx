import type { 
  ComplexityAnalysisResult, 
  HintResult, 
  OptimizationResult, 
  DebugResult, 
  IncompleteSolutionResult
} from '../types/analysis';

interface ResultsDisplayProps {
  result: ComplexityAnalysisResult | HintResult | OptimizationResult | DebugResult | IncompleteSolutionResult | null;
  analysisType: string;
  loading: boolean;
  error: string | null;
  loadingProgress?: number;
  estimatedTime?: number;
  loadingMessage?: string;
}

export default function ResultsDisplay({ 
  result, 
  analysisType, 
  loading, 
  error,
  loadingProgress = 0,
  estimatedTime = 10,
  loadingMessage = 'Analyzing your solution...'
}: ResultsDisplayProps) {
  if (loading) {
    const remainingTime = Math.max(0, Math.ceil(estimatedTime * (1 - loadingProgress / 100)));
    
    return (
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-100 p-12" role="status" aria-live="polite" aria-label="Analysis in progress">
        <div className="flex flex-col items-center justify-center space-y-6">
          {/* Animated spinner */}
          <div className="relative" aria-hidden="true">
            <div className="animate-spin rounded-full h-20 w-20 border-4 border-blue-200"></div>
            <div className="animate-spin rounded-full h-20 w-20 border-t-4 border-blue-600 absolute top-0"></div>
            {/* Progress percentage in center */}
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-sm font-bold text-blue-600">{Math.round(loadingProgress)}%</span>
            </div>
          </div>
          
          {/* Loading message */}
          <span className="text-gray-700 font-medium text-lg">{loadingMessage}</span>
          
          {/* Progress bar */}
          <div className="w-full max-w-md">
            <div className="h-3 bg-gray-200 rounded-full overflow-hidden" role="progressbar" aria-valuenow={Math.round(loadingProgress)} aria-valuemin={0} aria-valuemax={100} aria-label="Analysis progress">
              <div 
                className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 transition-all duration-300 ease-out rounded-full"
                style={{ width: `${loadingProgress}%` }}
              ></div>
            </div>
          </div>
          
          {/* Estimated time */}
          {remainingTime > 0 && (
            <span className="text-gray-500 text-sm">
              Estimated time remaining: {remainingTime}s
            </span>
          )}
          
          {/* Tips while waiting */}
          <div className="mt-4 p-4 bg-blue-50 rounded-xl border border-blue-200 max-w-md">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <p className="text-sm text-blue-800">
                {loadingProgress < 30 && "Our AI is reading your code and understanding the problem context..."}
                {loadingProgress >= 30 && loadingProgress < 60 && "Analyzing patterns and identifying key insights..."}
                {loadingProgress >= 60 && "Almost done! Formatting the results for you..."}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    // Parse error message for structured display
    const errorLines = error.split('\n');
    const mainError = errorLines[0];
    const details = errorLines.slice(1);
    
    return (
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-red-200 p-8">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
            <svg className="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-bold text-red-900 mb-2">Analysis Failed</h3>
            <p className="text-red-700 leading-relaxed font-semibold mb-3">{mainError}</p>
            
            {details.length > 0 && (
              <div className="mt-4 p-4 bg-red-50 rounded-xl border border-red-200">
                <div className="space-y-2">
                  {details.map((detail, idx) => {
                    const trimmed = detail.trim();
                    if (!trimmed) return null;
                    
                    // Check if this is a section header
                    if (trimmed.endsWith(':')) {
                      return (
                        <p key={idx} className="text-sm font-bold text-red-800 mt-3 first:mt-0">
                          {trimmed}
                        </p>
                      );
                    }
                    
                    // Check if this is a bullet point
                    if (trimmed.startsWith('•')) {
                      return (
                        <div key={idx} className="flex items-start gap-2 ml-2">
                          <span className="text-red-600 font-bold">•</span>
                          <p className="text-sm text-red-700 flex-1">{trimmed.substring(1).trim()}</p>
                        </div>
                      );
                    }
                    
                    // Regular detail line
                    return (
                      <p key={idx} className="text-sm text-red-700 ml-2">
                        {trimmed}
                      </p>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (!result) {
    return null;
  }

  // Check if this is an incomplete solution response
  if ('incomplete_solution' in result && result.incomplete_solution) {
    const incompleteResult = result as IncompleteSolutionResult;
    return (
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-amber-200 p-8">
        <div className="flex items-start gap-4 mb-6">
          <div className="flex-shrink-0 w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center">
            <svg className="w-6 h-6 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-bold text-amber-900 mb-2">Incomplete Solution Detected</h3>
            <p className="text-amber-800 leading-relaxed mb-4">{incompleteResult.message}</p>
          </div>
        </div>

        {/* Missing Elements */}
        {incompleteResult.missing_elements && incompleteResult.missing_elements.length > 0 && (
          <div className="mb-6 p-5 bg-amber-50 rounded-xl border border-amber-200">
            <h4 className="text-lg font-bold text-amber-900 mb-3 flex items-center gap-2">
              <svg className="w-5 h-5 text-amber-700" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0015.414 6L12 2.586A2 2 0 0010.586 2H6zm5 6a1 1 0 10-2 0v3.586l-1.293-1.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V8z" clipRule="evenodd" />
              </svg>
              Missing Elements
            </h4>
            <ul className="space-y-2">
              {incompleteResult.missing_elements.map((element, index) => (
                <li key={index} className="flex items-start gap-2">
                  <div className="flex-shrink-0 w-5 h-5 bg-amber-500 rounded-md flex items-center justify-center mt-0.5">
                    <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <span className="text-amber-900 leading-relaxed">{element}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Suggestion */}
        <div className="p-5 bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-10 h-10 bg-blue-500 rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z" />
              </svg>
            </div>
            <div className="flex-1">
              <h4 className="text-lg font-bold text-blue-900 mb-2">Suggestion</h4>
              <p className="text-blue-800 leading-relaxed">{incompleteResult.suggestion}</p>
            </div>
          </div>
        </div>

        {/* Confidence indicator */}
        <div className="mt-4 text-sm text-gray-600 text-center">
          Confidence: {Math.round(incompleteResult.confidence * 100)}%
        </div>
      </div>
    );
  }

  // Render complexity analysis results
  if (analysisType === 'complexity') {
    return (
      <article className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-100 p-8" aria-labelledby="complexity-heading">
        <header className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center" aria-hidden="true">
            <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0015.414 6L12 2.586A2 2 0 0010.586 2H6zm5 6a1 1 0 10-2 0v3.586l-1.293-1.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V8z" clipRule="evenodd" />
            </svg>
          </div>
          <h2 id="complexity-heading" className="text-3xl font-bold text-gray-900">
            Complexity Analysis
          </h2>
        </header>

        {/* Complexity Summary */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8" role="region" aria-label="Complexity summary">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 border-2 border-blue-200 rounded-2xl p-6 transform transition-transform hover:scale-105">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-blue-500 rounded-xl flex items-center justify-center" aria-hidden="true">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="text-lg font-bold text-blue-900">Time Complexity</h3>
            </div>
            <p className="text-4xl font-black text-blue-700" aria-label={`Time complexity is ${(result as ComplexityAnalysisResult).time_complexity}`}>{(result as ComplexityAnalysisResult).time_complexity}</p>
          </div>

          <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 border-2 border-emerald-200 rounded-2xl p-6 transform transition-transform hover:scale-105">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center" aria-hidden="true">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M3 12v3c0 1.657 3.134 3 7 3s7-1.343 7-3v-3c0 1.657-3.134 3-7 3s-7-1.343-7-3z" />
                  <path d="M3 7v3c0 1.657 3.134 3 7 3s7-1.343 7-3V7c0 1.657-3.134 3-7 3S3 8.657 3 7z" />
                  <path d="M17 5c0 1.657-3.134 3-7 3S3 6.657 3 5s3.134-3 7-3 7 1.343 7 3z" />
                </svg>
              </div>
              <h3 className="text-lg font-bold text-emerald-900">Space Complexity</h3>
            </div>
            <p className="text-4xl font-black text-emerald-700" aria-label={`Space complexity is ${(result as ComplexityAnalysisResult).space_complexity}`}>{(result as ComplexityAnalysisResult).space_complexity}</p>
          </div>
        </div>

        {/* Explanation */}
        <div className="mb-8 p-6 bg-gray-50 rounded-2xl border border-gray-200">
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <svg className="w-6 h-6 text-gray-700" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            Explanation
          </h3>
          <p className="text-gray-700 leading-relaxed text-base">{(result as ComplexityAnalysisResult).explanation}</p>
        </div>

        {/* Key Operations */}
        {(result as ComplexityAnalysisResult).key_operations && (result as ComplexityAnalysisResult).key_operations.length > 0 && (
          <div className="mb-8 p-6 bg-indigo-50 rounded-2xl border border-indigo-200">
            <h3 className="text-xl font-bold text-indigo-900 mb-4 flex items-center gap-2">
              <svg className="w-6 h-6 text-indigo-700" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
              </svg>
              Key Operations
            </h3>
            <ul className="space-y-3">
              {(result as ComplexityAnalysisResult).key_operations.map((operation, index) => (
                <li key={index} className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-indigo-500 rounded-lg flex items-center justify-center mt-0.5">
                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <span className="text-gray-800 leading-relaxed flex-1">{operation}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Improvements */}
        {(result as ComplexityAnalysisResult).improvements && (result as ComplexityAnalysisResult).improvements!.length > 0 && (
          <div className="p-6 bg-gradient-to-br from-amber-50 to-orange-50 border-2 border-amber-300 rounded-2xl">
            <h3 className="text-xl font-bold text-amber-900 mb-4 flex items-center gap-2">
              <svg className="w-6 h-6 text-amber-700" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
              </svg>
              Potential Improvements
            </h3>
            <ul className="space-y-3">
              {(result as ComplexityAnalysisResult).improvements!.map((improvement, index) => (
                <li key={index} className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-amber-500 rounded-lg flex items-center justify-center mt-0.5">
                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <span className="text-amber-900 leading-relaxed flex-1 font-medium">{improvement}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </article>
    );
  }

  // Render hint results
  if (analysisType === 'hints') {
    const hintResult = result as HintResult;
    return (
      <article className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-100 p-8" aria-labelledby="hints-heading">
        <header className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center" aria-hidden="true">
            <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z" />
            </svg>
          </div>
          <h2 id="hints-heading" className="text-3xl font-bold text-gray-900">
            Strategic Hints
          </h2>
        </header>

        {/* Progressive Hints Badge */}
        {hintResult.progressive && (
          <div className="mb-6 inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-100 to-pink-100 border border-purple-300 rounded-xl">
            <svg className="w-5 h-5 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clipRule="evenodd" />
            </svg>
            <span className="text-sm font-semibold text-purple-900">Progressive Hints - Start with the first one!</span>
          </div>
        )}

        {/* Hints List */}
        <div className="mb-8 space-y-4">
          {hintResult.hints.map((hint, index) => (
            <div 
              key={index} 
              className="p-6 bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200 rounded-2xl transform transition-all hover:scale-[1.02] hover:shadow-lg"
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center shadow-md">
                  <span className="text-white font-bold text-lg">{index + 1}</span>
                </div>
                <div className="flex-1">
                  <p className="text-gray-800 leading-relaxed text-base">{hint}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Next Steps */}
        {hintResult.next_steps && hintResult.next_steps.length > 0 && (
          <div className="p-6 bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-2xl">
            <h3 className="text-xl font-bold text-blue-900 mb-4 flex items-center gap-2">
              <svg className="w-6 h-6 text-blue-700" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M12.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
              Next Steps
            </h3>
            <ul className="space-y-3">
              {hintResult.next_steps.map((step, index) => (
                <li key={index} className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-blue-500 rounded-lg flex items-center justify-center mt-0.5">
                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <span className="text-blue-900 leading-relaxed flex-1 font-medium">{step}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </article>
    );
  }

  // Render optimization results
  if (analysisType === 'optimization') {
    const optimizationResult = result as OptimizationResult;
    return (
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-100 p-8">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-teal-600 rounded-xl flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-gray-900">
            Solution Optimization
          </h2>
        </div>

        {/* Complexity Comparison */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-gradient-to-br from-orange-50 to-red-100 border-2 border-orange-300 rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-orange-500 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="text-lg font-bold text-orange-900">Current Complexity</h3>
            </div>
            <p className="text-3xl font-black text-orange-700">{optimizationResult.current_complexity}</p>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-emerald-100 border-2 border-green-300 rounded-2xl p-6 transform transition-transform hover:scale-105">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-green-500 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="text-lg font-bold text-green-900">Optimized Complexity</h3>
            </div>
            <p className="text-3xl font-black text-green-700">{optimizationResult.optimized_complexity}</p>
          </div>
        </div>

        {/* Optimization Suggestions */}
        <div className="mb-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <svg className="w-7 h-7 text-gray-700" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
              <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
            </svg>
            Optimization Suggestions
          </h3>
          <div className="space-y-6">
            {optimizationResult.suggestions.map((suggestion, index) => (
              <div 
                key={index} 
                className="p-6 bg-gradient-to-br from-teal-50 to-cyan-50 border-2 border-teal-200 rounded-2xl transform transition-all hover:shadow-lg"
              >
                <div className="flex items-start gap-4 mb-4">
                  <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-teal-500 to-cyan-600 rounded-xl flex items-center justify-center shadow-md">
                    <span className="text-white font-bold text-lg">{index + 1}</span>
                  </div>
                  <div className="flex-1">
                    <h4 className="text-xl font-bold text-teal-900 mb-2">{suggestion.area}</h4>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div className="p-4 bg-white/70 rounded-xl border border-teal-200">
                    <div className="flex items-center gap-2 mb-2">
                      <svg className="w-5 h-5 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm font-bold text-orange-900 uppercase tracking-wide">Current</span>
                    </div>
                    <p className="text-gray-800 leading-relaxed">{suggestion.current_approach}</p>
                  </div>
                  
                  <div className="p-4 bg-white/70 rounded-xl border border-green-300">
                    <div className="flex items-center gap-2 mb-2">
                      <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm font-bold text-green-900 uppercase tracking-wide">Suggested</span>
                    </div>
                    <p className="text-gray-800 leading-relaxed">{suggestion.suggested_approach}</p>
                  </div>
                </div>
                
                <div className="p-4 bg-gradient-to-r from-amber-100 to-yellow-100 border-2 border-amber-300 rounded-xl">
                  <div className="flex items-start gap-3">
                    <svg className="w-6 h-6 text-amber-700 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
                    </svg>
                    <div>
                      <span className="text-sm font-bold text-amber-900 uppercase tracking-wide block mb-1">Impact</span>
                      <p className="text-amber-900 font-semibold leading-relaxed">{suggestion.impact}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Code Examples */}
        {optimizationResult.code_examples && optimizationResult.code_examples.length > 0 && (
          <div className="p-6 bg-gradient-to-br from-slate-50 to-gray-100 border-2 border-slate-300 rounded-2xl">
            <h3 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
              <svg className="w-6 h-6 text-slate-700" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
              Code Examples
            </h3>
            <div className="space-y-4">
              {optimizationResult.code_examples.map((example, index) => (
                <div key={index} className="p-4 bg-slate-800 rounded-xl overflow-x-auto">
                  <pre className="text-sm text-slate-100 font-mono leading-relaxed whitespace-pre-wrap">{example}</pre>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  // Render debugging results
  if (analysisType === 'debugging') {
    const debugResult = result as DebugResult;
    const hasIssues = debugResult.issues && debugResult.issues.length > 0;
    
    return (
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-100 p-8">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-rose-600 rounded-xl flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-gray-900">
            Solution Debugging
          </h2>
        </div>

        {/* Status Badge */}
        {!hasIssues ? (
          <div className="mb-8 p-6 bg-gradient-to-br from-green-50 to-emerald-100 border-2 border-green-300 rounded-2xl">
            <div className="flex items-center gap-4">
              <div className="flex-shrink-0 w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center">
                <svg className="w-7 h-7 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-bold text-green-900 mb-1">No Issues Found!</h3>
                <p className="text-green-800">Your solution appears to be correct. Consider testing with edge cases below.</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="mb-8 p-6 bg-gradient-to-br from-red-50 to-rose-100 border-2 border-red-300 rounded-2xl">
            <div className="flex items-center gap-4">
              <div className="flex-shrink-0 w-12 h-12 bg-red-500 rounded-xl flex items-center justify-center">
                <svg className="w-7 h-7 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-bold text-red-900 mb-1">
                  {debugResult.issues.length} {debugResult.issues.length === 1 ? 'Issue' : 'Issues'} Identified
                </h3>
                <p className="text-red-800">Review the issues below and apply the suggested fixes.</p>
              </div>
            </div>
          </div>
        )}

        {/* Issues List */}
        {hasIssues && (
          <div className="mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <svg className="w-7 h-7 text-gray-700" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              Identified Issues
            </h3>
            <div className="space-y-4">
              {debugResult.issues.map((issue, index) => {
                const severityColors = {
                  high: 'from-red-50 to-rose-100 border-red-300',
                  medium: 'from-orange-50 to-amber-100 border-orange-300',
                  low: 'from-yellow-50 to-yellow-100 border-yellow-300',
                  unknown: 'from-gray-50 to-gray-100 border-gray-300'
                };
                const severityBadgeColors = {
                  high: 'bg-red-500 text-white',
                  medium: 'bg-orange-500 text-white',
                  low: 'bg-yellow-500 text-gray-900',
                  unknown: 'bg-gray-500 text-white'
                };
                const severityColor = severityColors[issue.severity as keyof typeof severityColors] || severityColors.unknown;
                const badgeColor = severityBadgeColors[issue.severity as keyof typeof severityBadgeColors] || severityBadgeColors.unknown;
                
                return (
                  <div 
                    key={index} 
                    className={`p-6 bg-gradient-to-br ${severityColor} border-2 rounded-2xl`}
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-red-500 to-rose-600 rounded-xl flex items-center justify-center shadow-md">
                        <span className="text-white font-bold text-lg">{index + 1}</span>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-3">
                          {issue.line !== null && (
                            <span className="px-3 py-1 bg-gray-800 text-white text-sm font-mono rounded-lg">
                              Line {issue.line}
                            </span>
                          )}
                          <span className={`px-3 py-1 ${badgeColor} text-xs font-bold uppercase tracking-wide rounded-lg`}>
                            {issue.severity}
                          </span>
                        </div>
                        <p className="text-gray-800 leading-relaxed text-base">{issue.description}</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Fixes */}
        {debugResult.fixes && debugResult.fixes.length > 0 && (
          <div className="mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <svg className="w-7 h-7 text-gray-700" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
              </svg>
              Suggested Fixes
            </h3>
            <div className="space-y-6">
              {debugResult.fixes.map((fix, index) => (
                <div 
                  key={index} 
                  className="p-6 bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-2xl"
                >
                  <div className="flex items-start gap-4 mb-4">
                    <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-md">
                      <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h4 className="text-lg font-bold text-blue-900 mb-2">{fix.issue}</h4>
                      <p className="text-gray-800 leading-relaxed mb-4">{fix.suggestion}</p>
                      
                      {fix.code_example && (
                        <div className="mt-4">
                          <div className="flex items-center gap-2 mb-2">
                            <svg className="w-5 h-5 text-blue-700" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
                            </svg>
                            <span className="text-sm font-bold text-blue-900 uppercase tracking-wide">Code Example</span>
                          </div>
                          <div className="p-4 bg-slate-800 rounded-xl overflow-x-auto">
                            <pre className="text-sm text-slate-100 font-mono leading-relaxed whitespace-pre-wrap">{fix.code_example}</pre>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Test Cases */}
        {debugResult.test_cases && debugResult.test_cases.length > 0 && (
          <div className="p-6 bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200 rounded-2xl">
            <h3 className="text-xl font-bold text-purple-900 mb-4 flex items-center gap-2">
              <svg className="w-6 h-6 text-purple-700" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm9.707 5.707a1 1 0 00-1.414-1.414L9 12.586l-1.293-1.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              Recommended Test Cases
            </h3>
            <ul className="space-y-3">
              {debugResult.test_cases.map((testCase, index) => (
                <li key={index} className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-purple-500 rounded-lg flex items-center justify-center mt-0.5">
                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <span className="text-purple-900 leading-relaxed flex-1 font-medium">{testCase}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  }

  return null;
}
