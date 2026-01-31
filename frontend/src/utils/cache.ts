/**
 * Frontend cache utility using localStorage
 * Provides caching for problem details and analysis results
 */

import type { ProblemDetails, AnalysisResult } from '../types/analysis';

interface CacheEntry<T> {
  value: T;
  timestamp: number;
  expiresAt: number;
}

class FrontendCache {
  private readonly PROBLEM_PREFIX = 'leetcode_problem_';
  private readonly ANALYSIS_PREFIX = 'leetcode_analysis_';
  
  // TTL in milliseconds
  private readonly PROBLEM_TTL = 24 * 60 * 60 * 1000; // 24 hours
  private readonly ANALYSIS_TTL = 60 * 60 * 1000; // 1 hour
  
  /**
   * Generate a cache key from parameters
   */
  private generateKey(prefix: string, ...params: string[]): string {
    return prefix + params.join('_');
  }
  
  /**
   * Set a cache entry
   */
  private setEntry<T>(key: string, value: T, ttl: number): void {
    try {
      const entry: CacheEntry<T> = {
        value,
        timestamp: Date.now(),
        expiresAt: Date.now() + ttl
      };
      localStorage.setItem(key, JSON.stringify(entry));
    } catch (error) {
      console.warn('Failed to cache entry:', error);
      // If localStorage is full, clear old entries
      this.clearExpired();
    }
  }
  
  /**
   * Get a cache entry
   */
  private getEntry<T>(key: string): T | null {
    try {
      const item = localStorage.getItem(key);
      if (!item) return null;
      
      const entry: CacheEntry<T> = JSON.parse(item);
      
      // Check if expired
      if (Date.now() > entry.expiresAt) {
        localStorage.removeItem(key);
        return null;
      }
      
      return entry.value;
    } catch (error) {
      console.warn('Failed to retrieve cache entry:', error);
      return null;
    }
  }
  
  /**
   * Cache a problem
   */
  setProblem(slug: string, problem: ProblemDetails): void {
    const key = this.generateKey(this.PROBLEM_PREFIX, slug);
    this.setEntry(key, problem, this.PROBLEM_TTL);
  }
  
  /**
   * Get a cached problem
   */
  getProblem(slug: string): ProblemDetails | null {
    const key = this.generateKey(this.PROBLEM_PREFIX, slug);
    return this.getEntry<ProblemDetails>(key);
  }
  
  /**
   * Cache an analysis result
   */
  setAnalysis(
    problemSlug: string,
    code: string,
    language: string,
    analysisType: string,
    result: AnalysisResult
  ): void {
    // Create a hash of the code to keep key size manageable
    const codeHash = this.hashCode(code);
    const key = this.generateKey(
      this.ANALYSIS_PREFIX,
      problemSlug,
      codeHash,
      language,
      analysisType
    );
    this.setEntry(key, result, this.ANALYSIS_TTL);
  }
  
  /**
   * Get a cached analysis result
   */
  getAnalysis(
    problemSlug: string,
    code: string,
    language: string,
    analysisType: string
  ): AnalysisResult | null {
    const codeHash = this.hashCode(code);
    const key = this.generateKey(
      this.ANALYSIS_PREFIX,
      problemSlug,
      codeHash,
      language,
      analysisType
    );
    return this.getEntry<AnalysisResult>(key);
  }
  
  /**
   * Simple hash function for strings
   */
  private hashCode(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash).toString(36);
  }
  
  /**
   * Clear expired entries
   */
  clearExpired(): void {
    const now = Date.now();
    const keysToRemove: string[] = [];
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (!key) continue;
      
      // Only check our cache entries
      if (key.startsWith(this.PROBLEM_PREFIX) || key.startsWith(this.ANALYSIS_PREFIX)) {
        try {
          const item = localStorage.getItem(key);
          if (item) {
            const entry = JSON.parse(item) as CacheEntry<ProblemDetails | AnalysisResult>;
            if (now > entry.expiresAt) {
              keysToRemove.push(key);
            }
          }
        } catch {
          // If we can't parse it, remove it
          keysToRemove.push(key);
        }
      }
    }
    
    keysToRemove.forEach(key => localStorage.removeItem(key));
    console.log(`Cleared ${keysToRemove.length} expired cache entries`);
  }
  
  /**
   * Clear all problem cache
   */
  clearProblemCache(): void {
    const keysToRemove: string[] = [];
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(this.PROBLEM_PREFIX)) {
        keysToRemove.push(key);
      }
    }
    
    keysToRemove.forEach(key => localStorage.removeItem(key));
    console.log(`Cleared ${keysToRemove.length} problem cache entries`);
  }
  
  /**
   * Clear all analysis cache
   */
  clearAnalysisCache(): void {
    const keysToRemove: string[] = [];
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(this.ANALYSIS_PREFIX)) {
        keysToRemove.push(key);
      }
    }
    
    keysToRemove.forEach(key => localStorage.removeItem(key));
    console.log(`Cleared ${keysToRemove.length} analysis cache entries`);
  }
  
  /**
   * Clear all cache
   */
  clearAll(): void {
    this.clearProblemCache();
    this.clearAnalysisCache();
  }
  
  /**
   * Get cache statistics
   */
  getStats(): {
    problemCount: number;
    analysisCount: number;
    totalSize: number;
  } {
    let problemCount = 0;
    let analysisCount = 0;
    let totalSize = 0;
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (!key) continue;
      
      if (key.startsWith(this.PROBLEM_PREFIX)) {
        problemCount++;
        const item = localStorage.getItem(key);
        if (item) totalSize += item.length;
      } else if (key.startsWith(this.ANALYSIS_PREFIX)) {
        analysisCount++;
        const item = localStorage.getItem(key);
        if (item) totalSize += item.length;
      }
    }
    
    return {
      problemCount,
      analysisCount,
      totalSize
    };
  }
}

// Singleton instance
export const frontendCache = new FrontendCache();

// Clear expired entries on load
frontendCache.clearExpired();
