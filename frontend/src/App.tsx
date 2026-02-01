import { useState, useRef } from 'react'
import { Code2, Link, Code, Activity, Sparkles, Bug, Zap, History, Keyboard } from 'lucide-react'
import { Resizable } from 're-resizable'
import Editor from '@monaco-editor/react'
import ResultsDisplay from './components/ResultsDisplay'
import HistoryPanel from './components/HistoryPanel'
import KeyboardShortcutsHelp from './components/KeyboardShortcutsHelp'
import { useKeyboardShortcuts, type KeyboardShortcut } from './hooks/useKeyboardShortcuts'
import type { AnalysisType } from './components/AnalysisSelector'
import type { HistoryEntryData } from './types/history'
import type { AnalysisResult } from './types/analysis'
import { frontendCache } from './utils/cache'
import { API_ENDPOINTS } from './config/api'
import './App.css'

const LANGUAGES = [
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'java', label: 'Java' },
  { value: 'cpp', label: 'C++' },
  { value: 'c', label: 'C' },
  { value: 'csharp', label: 'C#' },
  { value: 'go', label: 'Go' },
  { value: 'rust', label: 'Rust' },
];

function App() {
  const [problemUrl, setProblemUrl] = useState('');
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
  const problemInputRef = useRef<HTMLInputElement>(null);
  const codeEditorRef = useRef<HTMLDivElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  // Validate LeetCode URL - now optional, so only check if provided
  const isUrlValid = !problemUrl || /leetcode\.com\/problems\/[\w-]+/.test(problemUrl);

  const handleAnalysisSelect = (type: AnalysisType) => {
    setSelectedAnalysis(type);
    setAnalysisResult(null);
    setError(null);
  };

  // Quick complexity analysis - two-stage approach for faster response
  const handleComplexityAnalysisQuick = async () => {
    setLoadingMessage('Analyzing complexity...');
    setLoadingProgress(10);
    
    try {
      console.log('Sending quick complexity request:', {
        problem_url: problemUrl || null,
        code: code.substring(0, 50) + '...',
        language: language,
      });

      const response = await fetch(API_ENDPOINTS.analyzeComplexityQuick, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          problem_url: problemUrl || null,
          code: code,
          language: language,
        }),
      });

      console.log('Quick complexity response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        console.error('Quick complexity error response:', errorData);
        
        // Handle structured error responses
        if (typeof errorData.detail === 'object') {
          const detail = errorData.detail;
          let errorMessage = detail.message || detail.error || 'Analysis failed';
          
          // Add validation errors if present
          if (detail.validation_errors && detail.validation_errors.length > 0) {
            errorMessage += '\n\nValidation errors:';
            detail.validation_errors.forEach((err: { field: string; message: string; suggestion?: string }) => {
              errorMessage += `\n• ${err.field}: ${err.message}`;
              if (err.suggestion) {
                errorMessage += `\n  Suggestion: ${err.suggestion}`;
              }
            });
          }
          
          // Add suggestion if present
          if (detail.suggestion && !detail.validation_errors) {
            errorMessage += `\n\nSuggestion: ${detail.suggestion}`;
          }
          
          throw new Error(errorMessage);
        } else {
          throw new Error(errorData.detail || 'Analysis failed');
        }
      }

      const quickResult = await response.json();
      console.log('Quick complexity result:', quickResult);
      
      setLoadingProgress(100);
      setLoadingMessage('Complete!');
      
      // Set result with quick analysis and placeholder for explanation
      setAnalysisResult({
        time_complexity: quickResult.time_complexity,
        space_complexity: quickResult.space_complexity,
        explanation: '', // Will be loaded on demand
        key_operations: [],
        improvements: [],
        inferred_problem: quickResult.inferred_problem,
        inferred_problem_title: quickResult.inferred_problem_title,
      });
      
      setLoading(false);
    } catch (err) {
      console.error('Quick complexity analysis error:', err);
      const errorMessage = err instanceof Error ? err.message : 
                          typeof err === 'string' ? err : 
                          'Analysis failed. Please check the console for details.';
      setError(errorMessage);
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!canAnalyze || !selectedAnalysis) return;

    setLoading(true);
    setError(null);
    setAnalysisResult(null);
    setLoadingProgress(0);
    
    // For complexity analysis, use quick two-stage approach
    if (selectedAnalysis === 'complexity') {
      await handleComplexityAnalysisQuick();
      return;
    }
    
    // Set estimated time based on analysis type (in seconds)
    const estimatedTimes: Record<string, number> = {
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
          problem_url: problemUrl || null,
          code: code.substring(0, 50) + '...',
          language: language,
          analysis_type: selectedAnalysis,
        });

        const response = await fetch(API_ENDPOINTS.analyze, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            problem_url: problemUrl || null, // Send null if empty
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
        console.log('Analysis type:', selectedAnalysis);
        
        // Additional logging for hints
        if (selectedAnalysis === 'hints') {
          console.log('Hints result structure:', {
            hasHints: 'hints' in result,
            hintsValue: (result as any).hints,
            hintsType: typeof (result as any).hints,
            isArray: Array.isArray((result as any).hints),
            fullResult: JSON.stringify(result, null, 2)
          });
        }
        
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
    setProblemUrl(`https://leetcode.com/problems/${entry.problem_slug}/`);
    setCode(entry.code);
    setLanguage(entry.language);
    setSelectedAnalysis(entry.analysis_type as AnalysisType);
    setAnalysisResult(entry.result);
    setError(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleRerunAnalysis = async (entry: HistoryEntryData) => {
    setProblemUrl(`https://leetcode.com/problems/${entry.problem_slug}/`);
    setCode(entry.code);
    setLanguage(entry.language);
    setSelectedAnalysis(entry.analysis_type as AnalysisType);
    setAnalysisResult(null);
    setError(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
    setTimeout(() => {
      handleAnalyze();
    }, 100);
  };

  // Determine if analysis options should be enabled - only code is required now
  const canAnalyze = code.trim().length > 0 && isUrlValid;

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
        problemInputRef.current?.focus();
      }
    },
    {
      key: '2',
      alt: true,
      description: 'Focus code editor',
      category: 'Navigation',
      action: () => {
        codeEditorRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Keyboard Shortcuts Help Overlay */}
      <KeyboardShortcutsHelp
        shortcuts={shortcuts}
        isOpen={showShortcutsHelp}
        onClose={() => setShowShortcutsHelp(false)}
      />

      <div className="container mx-auto px-4 py-8 max-w-[1800px]">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-3">
            <Code2 className="w-10 h-10 text-orange-500" />
            <h1 className="text-4xl font-bold text-slate-800">LeetCode Analyzer</h1>
          </div>
          <p className="text-slate-600 text-lg">
            AI-powered insights for your coding solutions
          </p>
          
          {/* Action Buttons */}
          <div className="mt-6 flex items-center justify-center gap-3">
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 flex items-center gap-2"
              aria-label="Toggle history panel"
            >
              <History className="w-5 h-5" />
              {showHistory ? 'Hide History' : 'View History'}
            </button>
            
            <button
              onClick={() => setShowShortcutsHelp(true)}
              className="px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 flex items-center gap-2"
              aria-label="Show keyboard shortcuts"
              title="Keyboard shortcuts (Press ?)"
            >
              <Keyboard className="w-5 h-5" />
              Shortcuts
            </button>
          </div>
        </div>

        {/* History Panel */}
        {showHistory && (
          <aside className="mb-8" aria-label="Analysis history">
            <HistoryPanel
              onEntrySelect={handleHistoryEntrySelect}
              onRerunAnalysis={handleRerunAnalysis}
            />
          </aside>
        )}

        {/* Main Content - Split Pane Layout */}
        <div className="flex gap-6 flex-col lg:flex-row">
          {/* Left Panel - Input */}
          <Resizable
            defaultSize={{
              width: '60%',
              height: 'auto',
            }}
            minWidth="400px"
            maxWidth="90%"
            enable={{
              top: false,
              right: true,
              bottom: false,
              left: false,
              topRight: false,
              bottomRight: false,
              bottomLeft: false,
              topLeft: false,
            }}
            handleStyles={{
              right: {
                width: '8px',
                right: '-4px',
                cursor: 'col-resize',
              },
            }}
            handleClasses={{
              right: 'hover:bg-orange-400 transition-colors',
            }}
            className="flex-shrink-0"
          >
            <div className="bg-white rounded-xl shadow-lg p-6 h-fit">
              <h2 className="text-2xl font-semibold text-slate-800 mb-4">Input</h2>

              {/* LeetCode Link Input */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  <Link className="inline w-4 h-4 mr-1" />
                  LeetCode Problem Link <span className="text-sm text-slate-500">(Optional)</span>
                </label>
                <input
                  ref={problemInputRef}
                  type="text"
                  value={problemUrl}
                  onChange={(e) => setProblemUrl(e.target.value)}
                  placeholder="https://leetcode.com/problems/... (or leave empty)"
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition"
                />
                <p className="mt-1 text-xs text-slate-500">
                  Leave empty to let AI infer the problem from your code
                </p>
              </div>

              {/* Language Selector */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  <Code className="inline w-4 h-4 mr-1" />
                  Programming Language
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition bg-white cursor-pointer"
                >
                  {LANGUAGES.map((lang) => (
                    <option key={lang.value} value={lang.value}>
                      {lang.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Code Input */}
              <div className="mb-6" ref={codeEditorRef}>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Your Code <span className="text-red-500">*</span>
                </label>
                <div className="border border-slate-300 rounded-lg overflow-hidden" style={{ height: '400px' }}>
                  <Editor
                    height="100%"
                    language={language}
                    value={code}
                    onChange={(value) => setCode(value || '')}
                    theme="vs-light"
                    options={{
                      minimap: { enabled: false },
                      fontSize: 14,
                      lineNumbers: 'on',
                      scrollBeyondLastLine: false,
                      automaticLayout: true,
                      tabSize: 2,
                      wordWrap: 'on',
                    }}
                  />
                </div>
              </div>

              {/* Analysis Options */}
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-slate-700 mb-2">Analysis Options</h3>
                
                <button
                  onClick={() => {
                    handleAnalysisSelect('complexity');
                    if (canAnalyze) handleAnalyze();
                  }}
                  disabled={!canAnalyze || loading}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition shadow-md ${
                    selectedAnalysis === 'complexity'
                      ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white'
                      : 'bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  <Activity className="w-5 h-5" />
                  <span className="font-medium">Analyze Time Complexity</span>
                </button>

                <button
                  onClick={() => {
                    handleAnalysisSelect('hints');
                    if (canAnalyze) handleAnalyze();
                  }}
                  disabled={!canAnalyze || loading}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition shadow-md ${
                    selectedAnalysis === 'hints'
                      ? 'bg-gradient-to-r from-purple-600 to-purple-700 text-white'
                      : 'bg-gradient-to-r from-purple-500 to-purple-600 text-white hover:from-purple-600 hover:to-purple-700'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  <Sparkles className="w-5 h-5" />
                  <span className="font-medium">Get Hints</span>
                </button>

                <button
                  onClick={() => {
                    handleAnalysisSelect('debugging');
                    if (canAnalyze) handleAnalyze();
                  }}
                  disabled={!canAnalyze || loading}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition shadow-md ${
                    selectedAnalysis === 'debugging'
                      ? 'bg-gradient-to-r from-red-600 to-red-700 text-white'
                      : 'bg-gradient-to-r from-red-500 to-red-600 text-white hover:from-red-600 hover:to-red-700'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  <Bug className="w-5 h-5" />
                  <span className="font-medium">Debug</span>
                </button>

                <button
                  onClick={() => {
                    handleAnalysisSelect('optimization');
                    if (canAnalyze) handleAnalyze();
                  }}
                  disabled={!canAnalyze || loading}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition shadow-md ${
                    selectedAnalysis === 'optimization'
                      ? 'bg-gradient-to-r from-green-600 to-green-700 text-white'
                      : 'bg-gradient-to-r from-green-500 to-green-600 text-white hover:from-green-600 hover:to-green-700'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  <Zap className="w-5 h-5" />
                  <span className="font-medium">Optimize</span>
                </button>
              </div>

              {loading && (
                <div className="mt-4 text-center text-slate-600">
                  <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-orange-500"></div>
                  <p className="mt-2 text-sm">{loadingMessage || 'Analyzing your code...'}</p>
                </div>
              )}
            </div>
          </Resizable>

          {/* Right Panel - Results */}
          <div className="flex-1 min-w-0" ref={resultsRef}>
            <ResultsDisplay
              result={analysisResult}
              analysisType={selectedAnalysis || ''}
              loading={loading}
              error={error}
              loadingProgress={loadingProgress}
              estimatedTime={estimatedTime}
              loadingMessage={loadingMessage}
              currentCode={code}
              currentLanguage={language}
              currentProblemUrl={problemUrl}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
