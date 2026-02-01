// API Configuration
// Centralized API URL management for all API calls

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://leetcode-analyzer-xto0.onrender.com';

// API endpoints
export const API_ENDPOINTS = {
  analyze: `${API_BASE_URL}/api/analyze`,
  analyzeComplexityQuick: `${API_BASE_URL}/api/analyze-complexity-quick`,
  explainComplexity: `${API_BASE_URL}/api/explain-complexity`,
  history: `${API_BASE_URL}/api/history`,
  historyById: (id: string) => `${API_BASE_URL}/api/history/${id}`,
} as const;
