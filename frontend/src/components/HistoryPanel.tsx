import { useState, useEffect } from 'react';
import HistoryEntry from './HistoryEntry';
import type { HistoryEntryData } from '../types/history';

interface HistoryPanelProps {
  onEntrySelect: (entry: HistoryEntryData) => void;
  onRerunAnalysis: (entry: HistoryEntryData) => void;
}

export default function HistoryPanel({ onEntrySelect, onRerunAnalysis }: HistoryPanelProps) {
  const [entries, setEntries] = useState<HistoryEntryData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [groupByProblem, setGroupByProblem] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/history?limit=100');
      
      if (!response.ok) {
        throw new Error('Failed to fetch history');
      }
      
      const data = await response.json();
      setEntries(data.entries || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (entryId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/history/${entryId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete entry');
      }
      
      // Remove from local state
      setEntries(entries.filter(e => e.id !== entryId));
    } catch (err) {
      console.error('Delete failed:', err);
      alert('Failed to delete entry');
    }
  };

  // Filter entries based on search and filter type
  const filteredEntries = entries.filter(entry => {
    const matchesSearch = searchQuery === '' || 
      entry.problem_title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      entry.problem_slug.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesFilter = filterType === 'all' || entry.analysis_type === filterType;
    
    return matchesSearch && matchesFilter;
  });

  // Group entries by problem if enabled
  const groupedEntries = groupByProblem
    ? filteredEntries.reduce((groups, entry) => {
        const key = entry.problem_slug;
        if (!groups[key]) {
          groups[key] = [];
        }
        groups[key].push(entry);
        return groups;
      }, {} as Record<string, HistoryEntryData[]>)
    : { all: filteredEntries };

  // Sort groups by most recent entry
  const sortedGroups = Object.entries(groupedEntries).sort((a, b) => {
    const aLatest = new Date(a[1][0].timestamp).getTime();
    const bLatest = new Date(b[1][0].timestamp).getTime();
    return bLatest - aLatest;
  });

  if (loading) {
    return (
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-100 p-8">
        <div className="flex items-center justify-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-red-200 p-8">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 w-10 h-10 bg-red-100 rounded-xl flex items-center justify-center">
            <svg className="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-red-900 mb-2">Failed to Load History</h3>
            <p className="text-red-700">{error}</p>
            <button
              onClick={fetchHistory}
              className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-100 p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
              <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-gray-900">Analysis History</h2>
        </div>
        <button
          onClick={fetchHistory}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
          </svg>
          Refresh
        </button>
      </div>

      {/* Search and Filters */}
      <div className="mb-6 space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
            </svg>
          </div>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by problem name..."
            className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-4 focus:ring-blue-100 focus:border-blue-400 transition-all"
          />
        </div>

        {/* Filter Controls */}
        <div className="flex items-center gap-4 flex-wrap">
          {/* Analysis Type Filter */}
          <div className="flex items-center gap-2">
            <label className="text-sm font-semibold text-gray-700">Filter:</label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-400 transition-all"
            >
              <option value="all">All Types</option>
              <option value="complexity">Complexity</option>
              <option value="hints">Hints</option>
              <option value="optimization">Optimization</option>
              <option value="debugging">Debugging</option>
            </select>
          </div>

          {/* Group Toggle */}
          <button
            onClick={() => setGroupByProblem(!groupByProblem)}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              groupByProblem
                ? 'bg-purple-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {groupByProblem ? 'Grouped by Problem' : 'Show All'}
          </button>

          {/* Entry Count */}
          <div className="ml-auto text-sm text-gray-600 font-medium">
            {filteredEntries.length} {filteredEntries.length === 1 ? 'entry' : 'entries'}
          </div>
        </div>
      </div>

      {/* Entries List */}
      {filteredEntries.length === 0 ? (
        <div className="text-center py-16">
          <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-10 h-10 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm3 1h6v4H7V5zm6 6H7v2h6v-2z" clipRule="evenodd" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">No History Found</h3>
          <p className="text-gray-600">
            {searchQuery || filterType !== 'all'
              ? 'Try adjusting your search or filters'
              : 'Start analyzing solutions to build your history'}
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {sortedGroups.map(([problemSlug, groupEntries]) => (
            <div key={problemSlug} className="space-y-3">
              {groupByProblem && (
                <div className="flex items-center gap-3 px-4 py-2 bg-gradient-to-r from-purple-50 to-indigo-50 border-l-4 border-purple-500 rounded-lg">
                  <svg className="w-5 h-5 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                  </svg>
                  <h3 className="text-lg font-bold text-purple-900">
                    {groupEntries[0].problem_title}
                  </h3>
                  <span className="ml-auto text-sm font-semibold text-purple-700 bg-purple-200 px-3 py-1 rounded-full">
                    {groupEntries.length} {groupEntries.length === 1 ? 'analysis' : 'analyses'}
                  </span>
                </div>
              )}
              
              {groupEntries.map((entry) => (
                <HistoryEntry
                  key={entry.id}
                  entry={entry}
                  onSelect={() => onEntrySelect(entry)}
                  onRerun={() => onRerunAnalysis(entry)}
                  onDelete={() => handleDelete(entry.id)}
                />
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
