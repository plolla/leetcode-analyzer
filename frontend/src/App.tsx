import { useState, useRef } from 'react'
import ProblemInput from './components/ProblemInput'
import CodeEditor from './components/CodeEditor'
import AnalysisSelector from './components/AnalysisSelector'
import ResultsDisplay from './components/ResultsDisplay'
import HistoryPanel from './components/HistoryPanel'
import KeyboardShortcutsHelp from './components/KeyboardShortcutsHelp'
import { useKeyboardShortcuts, type KeyboardShortcut } from './hooks/useKeyboardShortcuts'
import type { AnalysisType } from './components/AnalysisSelector'
import type { HistoryEntryData } from './types/history'
import type { AnalysisResult } from './types/analysis'
import { frontendCache } from './utils/cache'
import './App.css'

function App() {
  const [problemUrl, setProblemUrl] = useState('');
  const [isUrlValid, setIsUrlValid] = useState(false);
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [selectedAnalysis, setSelectedAnalysis] = useState<AnalysisType | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [estimatedTime, setEstimatedTime] = useState(0);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [showShortcutsHelp, setShowShortcutsHelp] = useState(false);

  // Refs for focus management
  const problemInputRef = useRef<HTMLDivElement>(null);
  const codeEditorRef = useRef<HTMLDivElement>(null);
  const analysisSelectorRef = useRef<HTMLDivElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  const handleUrlChange = (url: string, isValid: boolean) => {
    setProblemUrl(url);
    setIsUrlValid(isValid);
  };

  const handleCodeChange = (newCode: string, newLanguage: string) => {
    setCode(newCode);
    setLanguage(newLanguage);
  };

  const handleAnalysisSelect = (type: AnalysisType) => {
    setSelectedAnalysis(type);
    // Clear previous results when changing analysis type
    setAnalysisResult(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!canAnalyze || !selectedAnalysis) return;

    setLoading(true);
    setError(null);
    setAnalysisResult(null);
    setLoadingProgress(0);
    
    // Set estimated time based on analysis type (in seconds)
    const estimatedTimes: Record<string, number> = {
      'complexity': 8,
      'hints': 10,
      'optimization': 12,
      'debugging': 10
    };
    const estimatedSeconds = estimatedTimes[selectedAnalysis] || 10;
    setEstimatedTime(estimatedSeconds);
    
    // Set initial loading message
    setLoadingMessage('Preparing your request...');
    
    // Start progress simulation
    const startTime = Date.now();
    const progressInterval = setInterval(() => {
      const elapsed = (Date.now() - startTime) / 1000;
      const progress = Math.min((elapsed / estimatedSeconds) * 90, 90); // Cap at 90% until complete
      setLoadingProgress(progress);
      
      // Update loading message based on progress
      if (progress < 20) {
        setLoadingMessage('Preparing your request...');
      } else if (progress < 40) {
        setLoadingMessage('Analyzing your code...');
      } else if (progress < 60) {
        setLoadingMessage('Processing with AI...');
      } else if (progress < 80) {
        setLoadingMessage('Generating insights...');
      } else {
        setLoadingMessage('Finalizing results...');
      }
    }, 200);
    
    // Extract problem slug for caching
    const slugMatch = problemUrl.match(/\/problems\/([\w-]+)/);
    const problemSlug = slugMatch ? slugMatch[1] : '';
    
    // Check frontend cache first
    if (problemSlug) {
      const cachedResult = frontendCache.getAnalysis(
        problemSlug,
        code,
        language,
        selectedAnalysis
      );
      
      if (cachedResult) {
        console.log('Using cached result from frontend');
        clearInterval(progressInterval);
        setLoadingProgress(100);
        setLoadingMessage('Loaded from cache!');
        
        // Small delay to show cache hit
        await new Promise(resolve => setTimeout(resolve, 300));
        
        setAnalysisResult(cachedResult);
        setLoading(false);
        return;
      }
    }

    // Retry configuration
    const maxRetries = 2;
    let retryCount = 0;
    let lastError: Error | null = null;

    while (retryCount <= maxRetries) {
      try {
        console.log(`Sending analysis request (attempt ${retryCount + 1}/${maxRetries + 1}):`, {
          problem_url: problemUrl,
          code: code.substring(0, 50) + '...',
          language: language,
          analysis_type: selectedAnalysis,
        });

        const response = await fetch('http://localhost:8000/api/analyze', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            problem_url: problemUrl,
            code: code,
            language: language,
            analysis_type: selectedAnalysis,
          }),
        });

        console.log('Response status:', response.status);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
          console.error('Error response:', errorData);
          
          // Handle structured error responses
          if (typeof errorData.detail === 'object') {
            const detail = errorData.detail;
            let errorMessage = detail.message || detail.error || 'Analysis failed';
            
            // Add validation errors if present
            if (detail.validation_errors && detail.validation_errors.length > 0) {
              errorMessage += '\n\nValidation errors:';
              detail.validation_errors.forEach((err: { field: string; message: string; suggestion?: string; examples?: string[] }) => {
                errorMessage += `\n• ${err.field}: ${err.message}`;
                if (err.suggestion) {
                  errorMessage += `\n  Suggestion: ${err.suggestion}`;
                }
                if (err.examples && err.examples.length > 0) {
                  errorMessage += `\n  Examples: ${err.examples.join(', ')}`;
                }
              });
            }
            
            // Add suggestion if present
            if (detail.suggestion && !detail.validation_errors) {
              errorMessage += `\n\nSuggestion: ${detail.suggestion}`;
            }
            
            // Add examples if present
            if (detail.examples && detail.examples.length > 0) {
              errorMessage += `\n\nExamples:\n${detail.examples.map((ex: string) => `• ${ex}`).join('\n')}`;
            }
            
            // Check if we should retry
            if (detail.retry_after && retryCount < maxRetries) {
              console.log(`Retrying after ${detail.retry_after} seconds...`);
              await new Promise(resolve => setTimeout(resolve, detail.retry_after * 1000));
              retryCount++;
              continue;
            }
            
            throw new Error(errorMessage);
          } else {
            // Check for network errors that should be retried
            if (response.status >= 500 && retryCount < maxRetries) {
              console.log(`Server error (${response.status}), retrying...`);
              await new Promise(resolve => setTimeout(resolve, 2000));
              retryCount++;
              continue;
            }
            
            throw new Error(errorData.detail || 'Analysis failed');
          }
        }

        const result = await response.json() as AnalysisResult;
        console.log('Analysis result:', result);
        
        // Cache the result in frontend
        if (problemSlug) {
          frontendCache.setAnalysis(
            problemSlug,
            code,
            language,
            selectedAnalysis,
            result
          );
        }
        
        // Clear progress interval and set to 100%
        clearInterval(progressInterval);
        setLoadingProgress(100);
        setLoadingMessage('Complete!');
        
        // Small delay to show completion
        await new Promise(resolve => setTimeout(resolve, 300));
        
        setAnalysisResult(result);
        setLoading(false);
        return; // Success - exit the retry loop
        
      } catch (err) {
        lastError = err instanceof Error ? err : new Error('An error occurred during analysis');
        console.error(`Analysis error (attempt ${retryCount + 1}):`, err);
        
        // Check if this is a network error that should be retried
        if (err instanceof TypeError && err.message.includes('fetch') && retryCount < maxRetries) {
          console.log('Network error, retrying...');
          await new Promise(resolve => setTimeout(resolve, 2000));
          retryCount++;
          continue;
        }
        
        // If we've exhausted retries or it's not a retryable error, break
        break;
      }
    }

    // If we get here, all retries failed
    clearInterval(progressInterval);
    if (lastError) {
      let errorMessage = lastError.message;
      if (retryCount > 0) {
        errorMessage += `\n\nFailed after ${retryCount + 1} attempts. Please check your connection and try again.`;
      }
      setError(errorMessage);
    }
    
    setLoading(false);
  };

  const handleHistoryEntrySelect = (entry: HistoryEntryData) => {
    // Load the entry data into the form
    setProblemUrl(`https://leetcode.com/problems/${entry.problem_slug}/`);
    setIsUrlValid(true);
    setCode(entry.code);
    setLanguage(entry.language);
    setSelectedAnalysis(entry.analysis_type as AnalysisType);
    setAnalysisResult(entry.result);
    setError(null);
    
    // Scroll to top to show the loaded data
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleRerunAnalysis = async (entry: HistoryEntryData) => {
    // Load the entry data
    setProblemUrl(`https://leetcode.com/problems/${entry.problem_slug}/`);
    setIsUrlValid(true);
    setCode(entry.code);
    setLanguage(entry.language);
    setSelectedAnalysis(entry.analysis_type as AnalysisType);
    
    // Clear previous results and trigger new analysis
    setAnalysisResult(null);
    setError(null);
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Wait a bit for state to update, then run analysis
    setTimeout(() => {
      handleAnalyze();
    }, 100);
  };

  // Determine if analysis options should be enabled
  const canAnalyze = isUrlValid && code.trim().length > 0;

  // Keyboard shortcuts configuration
  const shortcuts: KeyboardShortcut[] = [
    {
      key: 'Enter',
      ctrl: true,
      description: 'Run analysis',
      category: 'Actions',
      action: () => {
        if (canAnalyze && selectedAnalysis && !loading) {
          handleAnalyze();
        }
      }
    },
    {
      key: '?',
      description: 'Show keyboard shortcuts',
      category: 'Help',
      action: () => setShowShortcutsHelp(!showShortcutsHelp)
    },
    {
      key: 'Escape',
      description: 'Close dialogs',
      category: 'Navigation',
      action: () => {
        if (showShortcutsHelp) {
          setShowShortcutsHelp(false);
        } else if (showHistory) {
          setShowHistory(false);
        }
      }
    },
    {
      key: 'h',
      ctrl: true,
      description: 'Toggle history panel',
      category: 'Navigation',
      action: () => setShowHistory(!showHistory)
    },
    {
      key: '1',
      alt: true,
      description: 'Focus problem input',
      category: 'Navigation',
      action: () => {
        problemInputRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        const input = problemInputRef.current?.querySelector('input');
        input?.focus();
      }
    },
    {
      key: '2',
      alt: true,
      description: 'Focus code editor',
      category: 'Navigation',
      action: () => {
        codeEditorRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        // Monaco editor will handle focus internally
      }
    },
    {
      key: '3',
      alt: true,
      description: 'Focus analysis selector',
      category: 'Navigation',
      action: () => {
        analysisSelectorRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    },
    {
      key: 'c',
      ctrl: true,
      shift: true,
      description: 'Select complexity analysis',
      category: 'Analysis Types',
      action: () => {
        if (canAnalyze) {
          handleAnalysisSelect('complexity');
        }
      }
    },
    {
      key: 'h',
      ctrl: true,
      shift: true,
      description: 'Select hints analysis',
      category: 'Analysis Types',
      action: () => {
        if (canAnalyze) {
          handleAnalysisSelect('hints');
        }
      }
    },
    {
      key: 'o',
      ctrl: true,
      shift: true,
      description: 'Select optimization analysis',
      category: 'Analysis Types',
      action: () => {
        if (canAnalyze) {
          handleAnalysisSelect('optimization');
        }
      }
    },
    {
      key: 'd',
      ctrl: true,
      shift: true,
      description: 'Select debugging analysis',
      category: 'Analysis Types',
      action: () => {
        if (canAnalyze) {
          handleAnalysisSelect('debugging');
        }
      }
    },
    {
      key: 'r',
      ctrl: true,
      description: 'Scroll to results',
      category: 'Navigation',
      action: () => {
        if (analysisResult || error) {
          resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    }
  ];

  // Enable keyboard shortcuts
  useKeyboardShortcuts({ shortcuts, enabled: !showShortcutsHelp });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Keyboard Shortcuts Help Overlay */}
      <KeyboardShortcutsHelp
        shortcuts={shortcuts}
        isOpen={showShortcutsHelp}
        onClose={() => setShowShortcutsHelp(false)}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <header className="text-center mb-16">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl mb-6 shadow-lg" aria-hidden="true">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
          </div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-indigo-900 bg-clip-text text-transparent mb-4">
            LeetCode Analysis
          </h1>
          <p className="text-xl text-gray-600 font-medium">
            AI-powered insights for your coding solutions
          </p>
          
          {/* History Toggle Button */}
          <div className="mt-6 flex items-center justify-center gap-3">
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 flex items-center gap-2"
              aria-label="Toggle history panel"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
              </svg>
              {showHistory ? 'Hide History' : 'View History'}
            </button>
            
            <button
              onClick={() => setShowShortcutsHelp(true)}
              className="px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 flex items-center gap-2"
              aria-label="Show keyboard shortcuts"
              title="Keyboard shortcuts (Press ?)"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V4a2 2 0 00-2-2H6zm1 2a1 1 0 000 2h6a1 1 0 100-2H7zm6 7a1 1 0 011 1v3a1 1 0 11-2 0v-3a1 1 0 011-1zm-3 3a1 1 0 100 2h.01a1 1 0 100-2H10zm-4 1a1 1 0 011-1h.01a1 1 0 110 2H7a1 1 0 01-1-1zm1-4a1 1 0 100 2h.01a1 1 0 100-2H7zm2 1a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1zm4-4a1 1 0 100 2h.01a1 1 0 100-2H13zM9 9a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1zM7 8a1 1 0 000 2h.01a1 1 0 000-2H7z" clipRule="evenodd" />
              </svg>
              Shortcuts
            </button>
          </div>
        </header>

        {/* History Panel */}
        {showHistory && (
          <aside className="mb-8" aria-label="Analysis history">
            <HistoryPanel
              onEntrySelect={handleHistoryEntrySelect}
              onRerunAnalysis={handleRerunAnalysis}
            />
          </aside>
        )}

        {/* Main Content */}
        <main className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-100 p-8 mb-8">
          <div className="space-y-10">
            {/* Problem Input Section */}
            <section ref={problemInputRef} aria-labelledby="problem-input-heading">
              <div className="flex items-center gap-3 mb-5">
                <div className="flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-600 rounded-lg font-bold text-sm" aria-hidden="true">
                  1
                </div>
                <h2 id="problem-input-heading" className="text-2xl font-bold text-gray-900">
                  Enter Problem URL
                </h2>
              </div>
              <ProblemInput onUrlChange={handleUrlChange} />
            </section>

            {/* Code Editor Section */}
            <section className="pt-8 border-t border-gray-200" ref={codeEditorRef} aria-labelledby="code-editor-heading">
              <div className="flex items-center gap-3 mb-5">
                <div className="flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-600 rounded-lg font-bold text-sm" aria-hidden="true">
                  2
                </div>
                <h2 id="code-editor-heading" className="text-2xl font-bold text-gray-900">
                  Paste Your Solution
                </h2>
              </div>
              <CodeEditor onCodeChange={handleCodeChange} />
            </section>

            {/* Analysis Selector Section */}
            <section className="pt-8 border-t border-gray-200" ref={analysisSelectorRef} aria-labelledby="analysis-selector-heading">
              <div className="flex items-center gap-3 mb-5">
                <div className="flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-600 rounded-lg font-bold text-sm" aria-hidden="true">
                  3
                </div>
                <h2 id="analysis-selector-heading" className="text-2xl font-bold text-gray-900">
                  Choose Analysis Type
                </h2>
              </div>
              <AnalysisSelector 
                onAnalysisSelect={handleAnalysisSelect}
                disabled={!canAnalyze}
              />
            </section>

            {/* Analyze Button */}
            {canAnalyze && selectedAnalysis && (
              <section className="pt-8 border-t border-gray-200">
                <button
                  onClick={handleAnalyze}
                  disabled={loading}
                  aria-label={loading ? 'Analysis in progress' : 'Run analysis (Ctrl+Enter)'}
                  className="w-full py-5 px-6 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 disabled:transform-none text-lg focus:outline-none focus:ring-4 focus:ring-blue-100"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-3">
                      <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Analyzing...
                    </span>
                  ) : (
                    'Analyze Solution'
                  )}
                </button>
              </section>
            )}
          </div>
        </main>

        {/* Results Section */}
        {(analysisResult || loading || error) && (
          <div ref={resultsRef}>
            <ResultsDisplay
              result={analysisResult}
              analysisType={selectedAnalysis || ''}
              loading={loading}
              error={error}
              loadingProgress={loadingProgress}
              estimatedTime={estimatedTime}
              loadingMessage={loadingMessage}
            />
          </div>
        )}

        {/* Debug Info (remove in production) */}
        {import.meta.env.DEV && (
          <div className="mt-6 p-5 bg-gray-900 text-gray-300 rounded-xl text-sm font-mono shadow-lg">
            <p className="text-gray-400 font-bold mb-2">Debug Info:</p>
            <div className="space-y-1">
              <p><span className="text-blue-400">URL:</span> {problemUrl || '(empty)'}</p>
              <p><span className="text-blue-400">Valid:</span> {isUrlValid ? '✓ Yes' : '✗ No'}</p>
              <p><span className="text-blue-400">Code:</span> {code.length} characters</p>
              <p><span className="text-blue-400">Language:</span> {language}</p>
              <p><span className="text-blue-400">Can Analyze:</span> {canAnalyze ? '✓ Yes' : '✗ No'}</p>
              <p><span className="text-blue-400">Selected:</span> {selectedAnalysis || 'None'}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
