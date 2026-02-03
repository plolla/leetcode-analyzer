import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../hooks/useTheme';

/**
 * ThemeToggle component props
 */
export interface ThemeToggleProps {
  className?: string;
}

/**
 * ThemeToggle button component
 * 
 * Provides a button for switching between light and dark themes.
 * Displays a Sun icon in dark mode and a Moon icon in light mode.
 * Includes smooth rotation animation on theme change.
 * 
 * @param className - Optional additional CSS classes to apply to the button
 * 
 * @example
 * ```tsx
 * <ThemeToggle />
 * <ThemeToggle className="ml-4" />
 * ```
 * 
 * @remarks
 * - Must be used within a ThemeProvider
 * - Includes ARIA labels for accessibility
 * - Keyboard accessible (focusable, responds to Enter/Space)
 * - Smooth rotation animation on theme change
 */
export const ThemeToggle: React.FC<ThemeToggleProps> = ({ className = '' }) => {
  const { theme, toggleTheme } = useTheme();

  return (
    <>
      <button
        onClick={toggleTheme}
        aria-label={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
        className={`
          p-2 rounded-lg
          bg-white dark:bg-slate-800
          border border-slate-300 dark:border-slate-600
          text-slate-800 dark:text-slate-100
          hover:bg-slate-100 dark:hover:bg-slate-700
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
          focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2
          dark:focus:ring-offset-slate-900
          dark:focus-visible:ring-offset-slate-900
          transition-all duration-200
          ${className}
        `.trim()}
      >
        <div className="w-5 h-5 transition-transform duration-300 ease-in-out hover:rotate-12">
          {theme === 'dark' ? (
            <Sun className="w-5 h-5" aria-hidden="true" />
          ) : (
            <Moon className="w-5 h-5" aria-hidden="true" />
          )}
        </div>
      </button>
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      >
        {theme === 'dark' ? 'Dark mode enabled' : 'Light mode enabled'}
      </div>
    </>
  );
};
