import { useContext } from 'react';
import { ThemeContext, type ThemeContextType } from '../contexts/ThemeContext';

/**
 * Custom hook for consuming theme context
 * 
 * @returns ThemeContextType containing current theme and toggleTheme function
 * @throws Error if used outside of ThemeProvider
 * 
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { theme, toggleTheme } = useTheme();
 *   
 *   return (
 *     <div className={theme === 'dark' ? 'dark-mode' : 'light-mode'}>
 *       <button onClick={toggleTheme}>Toggle Theme</button>
 *     </div>
 *   );
 * }
 * ```
 * 
 * @remarks
 * This hook must be used within a component that is wrapped by ThemeProvider.
 * If used outside of ThemeProvider, it will throw a descriptive error to guide
 * developers to properly set up the theme context.
 */
export function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext);
  
  if (context === undefined) {
    throw new Error(
      'useTheme must be used within a ThemeProvider. ' +
      'Please wrap your component tree with <ThemeProvider> to use theme functionality.'
    );
  }
  
  return context;
}
