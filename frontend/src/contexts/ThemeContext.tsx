import React, { useState, useEffect } from 'react';

/**
 * Theme type representing the two supported theme modes
 */
export type Theme = 'light' | 'dark';

/**
 * ThemeContext type definition
 * Provides theme state and toggle function to consuming components
 */
export interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

/**
 * ThemeContext - React context for theme state management
 * Provides theme state and toggle function throughout the application
 * 
 * @remarks
 * This context should be consumed via the useTheme hook rather than directly.
 * Components must be wrapped in a ThemeProvider to access this context.
 */
export const ThemeContext = React.createContext<ThemeContextType | undefined>(undefined);

/**
 * ThemeProvider props
 */
export interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: Theme;
  storageKey?: string;
}

/**
 * ThemeProvider component
 * Manages theme state, persistence, and DOM updates
 * 
 * @param children - Child components to wrap with theme context
 * @param defaultTheme - Default theme to use if no saved preference exists (defaults to 'light')
 * @param storageKey - localStorage key for persisting theme preference (defaults to 'theme')
 * 
 * @remarks
 * - Loads initial theme from localStorage on mount
 * - Updates document.documentElement classList when theme changes
 * - Saves theme to localStorage when theme changes
 * - Provides theme context to all child components
 */
export const ThemeProvider: React.FC<ThemeProviderProps> = ({
  children,
  defaultTheme = 'light',
  storageKey = 'theme',
}) => {
  /**
   * Get initial theme from localStorage or use default
   * @returns The initial theme value
   */
  const getInitialTheme = (): Theme => {
    try {
      const stored = localStorage.getItem(storageKey);
      if (stored === 'light' || stored === 'dark') {
        return stored;
      }
    } catch (error) {
      console.warn('Failed to load theme preference from localStorage:', error);
    }
    return defaultTheme;
  };

  // Initialize theme state
  const [theme, setTheme] = useState<Theme>(getInitialTheme);

  /**
   * Toggle between light and dark themes
   */
  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  // Update document.documentElement classList when theme changes
  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [theme]);

  // Save theme to localStorage when theme changes
  useEffect(() => {
    try {
      localStorage.setItem(storageKey, theme);
    } catch (error) {
      console.warn('Failed to save theme preference to localStorage:', error);
    }
  }, [theme, storageKey]);

  const value: ThemeContextType = {
    theme,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
      {/* ARIA live region for screen reader announcements */}
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      >
        {theme === 'dark' ? 'Dark mode enabled' : 'Light mode enabled'}
      </div>
    </ThemeContext.Provider>
  );
};
