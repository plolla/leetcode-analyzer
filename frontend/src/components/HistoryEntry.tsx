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
        bg: 'bg-blue-100',
        text: 'text-blue-800',
        icon: (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
          </svg>
        )
      },
      hints: {
        bg: 'bg-purple-100',
        text: 'text-purple-800',
        icon: (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z" />
          </svg>
        )
      },
      optimization: {
        bg: 'bg-green-100',
        text: 'text-green-800',
        icon: (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
          </svg>
        )
      },
      debugging: {
        bg: 'bg-red-100',
        text: 'text-red-800',
        icon: (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        )
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
    <div className="bg-white border-2 border-gray-200 rounded-xl hover:border-purple-300 hover:shadow-lg transition-all">
      {/* Main Entry Content */}
      <div className="p-5">
        <div className="flex items-start gap-4">
          {/* Analysis Type Badge */}
          <div className={`flex-shrink-0 w-12 h-12 ${typeStyle.bg} rounded-xl flex items-center justify-center`}>
            <div className={typeStyle.text}>
              {typeStyle.icon}
            </div>
          </div>

          {/* Entry Details */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-3 mb-2">
              <div className="flex-1 min-w-0">
                <h4 className="text-lg font-bold text-gray-900 truncate">
                  {entry.problem_title}
                </h4>
                <div className="flex items-center gap-3 mt-1 flex-wrap">
                  <span className={`inline-flex items-center gap-1.5 px-3 py-1 ${typeStyle.bg} ${typeStyle.text} text-xs font-semibold rounded-lg`}>
                    {typeStyle.icon}
                    {entry.analysis_type}
                  </span>
                  <span className="text-sm text-gray-600 font-medium">
                    {entry.language}
                  </span>
                  <span className="text-sm text-gray-500">
                    {formatTimestamp(entry.timestamp)}
                  </span>
                </div>
              </div>
            </div>

            {/* Result Summary */}
            <p className="text-sm text-gray-700 font-medium mt-3">
              {getResultSummary()}
            </p>

            {/* Code Preview */}
            {showDetails && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-gray-700 uppercase tracking-wide">Code</span>
                  <span className="text-xs text-gray-500">{entry.code.length} characters</span>
                </div>
                <pre className="text-xs text-gray-800 font-mono overflow-x-auto whitespace-pre-wrap max-h-40 overflow-y-auto">
                  {entry.code}
                </pre>
              </div>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 mt-4 pt-4 border-t border-gray-200">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium rounded-lg transition-colors text-sm flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
              <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
            </svg>
            {showDetails ? 'Hide Details' : 'View Details'}
          </button>

          <button
            onClick={onSelect}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors text-sm flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm3 1h6v4H7V5zm6 6H7v2h6v-2z" clipRule="evenodd" />
            </svg>
            Load
          </button>

          <button
            onClick={onRerun}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-colors text-sm flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
            </svg>
            Re-run
          </button>

          <button
            onClick={handleDelete}
            className={`ml-auto px-4 py-2 font-medium rounded-lg transition-colors text-sm flex items-center gap-2 ${
              showDeleteConfirm
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-gray-100 hover:bg-red-100 text-gray-700 hover:text-red-700'
            }`}
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {showDeleteConfirm ? 'Confirm Delete' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  );
}
