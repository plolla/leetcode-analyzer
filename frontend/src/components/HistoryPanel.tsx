import { useState, useEffect } from 'react';
import HistoryEntry from './HistoryEntry';
import type { HistoryEntryData } from '../types/history';
import { API_ENDPOINTS } from '../config/api';

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
      const response = await fetch(`${API_ENDPOINTS.history}?limit=100`);
      
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
      const response = await fetch(API_ENDPOINTS.historyById(entryId), {
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
        <div>
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
    );
  }

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-100 p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Analysis History</h2>
        <button
          onClick={fetchHistory}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
        >
          Refresh
        </button>
      </div>

      {/* Search and Filters */}
      <div className="mb-6 space-y-4">
        {/* Search Bar */}
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search by problem name..."
          className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-4 focus:ring-blue-100 focus:border-blue-400 transition-all"
        />

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
                <div className="px-4 py-2 bg-gradient-to-r from-purple-50 to-indigo-50 border-l-4 border-purple-500 rounded-lg">
                  <h3 className="text-lg font-bold text-purple-900">
                    {groupEntries[0].problem_title}
                  </h3>
                  <span className="text-sm font-semibold text-purple-700 bg-purple-200 px-3 py-1 rounded-full">
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
