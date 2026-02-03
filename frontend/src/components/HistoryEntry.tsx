import { useState } from 'react';
import type { HistoryEntryData } from '../types/history';

interface HistoryEntryProps {
  entry: HistoryEntryData;
  onSelect: () => void;
  onRerun: () => void;
  onDelete: () => void;
}

export default function HistoryEntry({ entry, onSelect, onRerun, onDelete }: HistoryEntryProps) {
  const [showDetails, setShowDetails] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
  };

  // Get analysis type styling
  const getAnalysisTypeStyle = (type: string) => {
    const styles = {
      complexity: {
        bg: 'bg-blue-100 dark:bg-blue-900/50',
        text: 'text-blue-800 dark:text-blue-300',
      },
      hints: {
        bg: 'bg-purple-100 dark:bg-purple-900/50',
        text: 'text-purple-800 dark:text-purple-300',
      },
      optimization: {
        bg: 'bg-green-100 dark:bg-green-900/50',
        text: 'text-green-800 dark:text-green-300',
      },
      debugging: {
        bg: 'bg-red-100 dark:bg-red-900/50',
        text: 'text-red-800 dark:text-red-300',
      }
    };
    return styles[type as keyof typeof styles] || styles.complexity;
  };

  const typeStyle = getAnalysisTypeStyle(entry.analysis_type);

  // Generate result summary
  const getResultSummary = () => {
    const result = entry.result;
    
    if (entry.analysis_type === 'complexity' && 'time_complexity' in result) {
      return `${result.time_complexity} time, ${result.space_complexity} space`;
    } else if (entry.analysis_type === 'hints' && 'hints' in result) {
      return `${result.hints?.length || 0} hints provided`;
    } else if (entry.analysis_type === 'optimization' && 'current_complexity' in result) {
      return `${result.current_complexity} → ${result.optimized_complexity}`;
    } else if (entry.analysis_type === 'debugging' && 'issues' in result) {
      const issueCount = result.issues?.length || 0;
      return issueCount === 0 ? 'No issues found' : `${issueCount} issue${issueCount > 1 ? 's' : ''} identified`;
    }
    return 'Analysis complete';
  };

  const handleDelete = () => {
    if (showDeleteConfirm) {
      onDelete();
      setShowDeleteConfirm(false);
    } else {
      setShowDeleteConfirm(true);
      setTimeout(() => setShowDeleteConfirm(false), 3000);
    }
  };

  return (
    <div className="bg-white dark:bg-slate-800 border-2 border-gray-200 dark:border-slate-700 rounded-xl hover:border-purple-300 dark:hover:border-purple-700 hover:shadow-lg transition-all">
      {/* Main Entry Content */}
      <div className="p-5">
        <div className="flex items-start gap-4">
          {/* Analysis Type Badge */}
          <div className={`flex-shrink-0 px-4 py-2 ${typeStyle.bg} rounded-xl`}>
            <span className={`${typeStyle.text} font-bold text-sm uppercase`}>
              {entry.analysis_type}
            </span>
          </div>

          {/* Entry Details */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-3 mb-2">
              <div className="flex-1 min-w-0">
                <h4 className="text-lg font-bold text-gray-900 dark:text-slate-100 truncate">
                  {entry.problem_title}
                </h4>
                <div className="flex items-center gap-3 mt-1 flex-wrap">
                  <span className="text-sm text-gray-600 dark:text-slate-400 font-medium">
                    {entry.language}
                  </span>
                  <span className="text-sm text-gray-500 dark:text-slate-500">
                    {formatTimestamp(entry.timestamp)}
                  </span>
                </div>
              </div>
            </div>

            {/* Result Summary */}
            <p className="text-sm text-gray-700 dark:text-slate-300 font-medium mt-3">
              {getResultSummary()}
            </p>

            {/* Code Preview */}
            {showDetails && (
              <div className="mt-4 p-4 bg-gray-50 dark:bg-slate-700 rounded-lg border border-gray-200 dark:border-slate-600">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-gray-700 dark:text-slate-300 uppercase tracking-wide">Code</span>
                  <span className="text-xs text-gray-500 dark:text-slate-400">{entry.code.length} characters</span>
                </div>
                <pre className="text-xs text-gray-800 dark:text-slate-200 font-mono overflow-x-auto whitespace-pre-wrap max-h-40 overflow-y-auto">
                  {entry.code}
                </pre>
              </div>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 mt-4 pt-4 border-t border-gray-200 dark:border-slate-700">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="px-4 py-2 bg-gray-100 dark:bg-slate-700 hover:bg-gray-200 dark:hover:bg-slate-600 text-gray-700 dark:text-slate-300 font-medium rounded-lg transition-colors text-sm"
          >
            {showDetails ? 'Hide Details' : 'View Details'}
          </button>

          <button
            onClick={onSelect}
            className="px-4 py-2 bg-blue-600 dark:bg-blue-700 hover:bg-blue-700 dark:hover:bg-blue-800 text-white font-medium rounded-lg transition-colors text-sm"
          >
            Load
          </button>

          <button
            onClick={onRerun}
            className="px-4 py-2 bg-purple-600 dark:bg-purple-700 hover:bg-purple-700 dark:hover:bg-purple-800 text-white font-medium rounded-lg transition-colors text-sm"
          >
            Re-run
          </button>

          <button
            onClick={handleDelete}
            className={`ml-auto px-4 py-2 font-medium rounded-lg transition-colors text-sm ${
              showDeleteConfirm
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-gray-100 dark:bg-slate-700 hover:bg-red-100 dark:hover:bg-red-900/30 text-gray-700 dark:text-slate-300 hover:text-red-700 dark:hover:text-red-400'
            }`}
          >
            {showDeleteConfirm ? 'Confirm Delete' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  );
}
