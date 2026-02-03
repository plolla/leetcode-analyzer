import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from './ThemeContext';
import { useTheme } from '../hooks/useTheme';

// Test component that displays the current theme
const TestComponent = () => {
  const { theme } = useTheme();
  return <div data-testid="theme-display">{theme}</div>;
};

describe('ThemeProvider Initialization', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Remove dark class from document element
    document.documentElement.classList.remove('dark');
  });

  describe('Loading saved theme from localStorage', () => {
    it('should load "light" theme from localStorage', () => {
      // Arrange: Set localStorage to 'light'
      localStorage.setItem('theme', 'light');

      // Act: Render ThemeProvider
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Assert: Theme should be 'light'
      expect(screen.getByTestId('theme-display')).toHaveTextContent('light');
    });

    it('should load "dark" theme from localStorage', () => {
      // Arrange: Set localStorage to 'dark'
      localStorage.setItem('theme', 'dark');

      // Act: Render ThemeProvider
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Assert: Theme should be 'dark'
      expect(screen.getByTestId('theme-display')).toHaveTextContent('dark');
    });

    it('should load theme from custom storage key', () => {
      // Arrange: Set custom storage key
      const customKey = 'my-custom-theme-key';
      localStorage.setItem(customKey, 'dark');

      // Act: Render ThemeProvider with custom storage key
      render(
        <ThemeProvider storageKey={customKey}>
          <TestComponent />
        </ThemeProvider>
      );

      // Assert: Theme should be 'dark'
      expect(screen.getByTestId('theme-display')).toHaveTextContent('dark');
    });
  });

  describe('Default to light when no saved preference exists', () => {
    it('should default to "light" when localStorage is empty', () => {
      // Arrange: localStorage is empty (cleared in beforeEach)

      // Act: Render ThemeProvider
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Assert: Theme should default to 'light'
      expect(screen.getByTestId('theme-display')).toHaveTextContent('light');
    });

    it('should use custom defaultTheme when localStorage is empty', () => {
      // Arrange: localStorage is empty, set defaultTheme to 'dark'

      // Act: Render ThemeProvider with custom default
      render(
        <ThemeProvider defaultTheme="dark">
          <TestComponent />
        </ThemeProvider>
      );

      // Assert: Theme should be 'dark'
      expect(screen.getByTestId('theme-display')).toHaveTextContent('dark');
    });
  });

  describe('Handling corrupted localStorage data', () => {
    it('should default to "light" when localStorage contains invalid value', () => {
      // Arrange: Set localStorage to invalid value
      localStorage.setItem('theme', 'invalid-theme');

      // Act: Render ThemeProvider
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Assert: Theme should default to 'light'
      expect(screen.getByTestId('theme-display')).toHaveTextContent('light');
    });

    it('should default to "light" when localStorage contains empty string', () => {
      // Arrange: Set localStorage to empty string
      localStorage.setItem('theme', '');

      // Act: Render ThemeProvider
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Assert: Theme should default to 'light'
      expect(screen.getByTestId('theme-display')).toHaveTextContent('light');
    });

    it('should default to "light" when localStorage contains null', () => {
      // Arrange: Set localStorage to 'null' string
      localStorage.setItem('theme', 'null');

      // Act: Render ThemeProvider
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Assert: Theme should default to 'light'
      expect(screen.getByTestId('theme-display')).toHaveTextContent('light');
    });

    it('should default to "light" when localStorage contains undefined', () => {
      // Arrange: Set localStorage to 'undefined' string
      localStorage.setItem('theme', 'undefined');

      // Act: Render ThemeProvider
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Assert: Theme should default to 'light'
      expect(screen.getByTestId('theme-display')).toHaveTextContent('light');
    });

    it('should default to "light" when localStorage contains JSON object', () => {
      // Arrange: Set localStorage to JSON object
      localStorage.setItem('theme', JSON.stringify({ theme: 'dark' }));

      // Act: Render ThemeProvider
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Assert: Theme should default to 'light'
      expect(screen.getByTestId('theme-display')).toHaveTextContent('light');
    });

    it('should use custom defaultTheme when localStorage contains invalid value', () => {
      // Arrange: Set localStorage to invalid value, set defaultTheme to 'dark'
      localStorage.setItem('theme', 'corrupted-data');

      // Act: Render ThemeProvider with custom default
      render(
        <ThemeProvider defaultTheme="dark">
          <TestComponent />
        </ThemeProvider>
      );

      // Assert: Theme should be 'dark' (custom default)
      expect(screen.getByTestId('theme-display')).toHaveTextContent('dark');
    });

    it('should handle localStorage.getItem throwing an error', () => {
      // Arrange: Mock localStorage.getItem to throw an error
      const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const originalGetItem = Storage.prototype.getItem;
      Storage.prototype.getItem = vi.fn(() => {
        throw new Error('localStorage is not available');
      });

      // Act: Render ThemeProvider
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Assert: Theme should default to 'light' and warning should be logged
      expect(screen.getByTestId('theme-display')).toHaveTextContent('light');
      expect(consoleWarnSpy).toHaveBeenCalledWith(
        'Failed to load theme preference from localStorage:',
        expect.any(Error)
      );

      // Cleanup
      Storage.prototype.getItem = originalGetItem;
      consoleWarnSpy.mockRestore();
    });
  });

  describe('DOM class updates on initialization', () => {
    it('should add "dark" class to document.documentElement when theme is "dark"', () => {
      // Arrange: Set localStorage to 'dark'
      localStorage.setItem('theme', 'dark');

      // Act: Render ThemeProvider
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Assert: document.documentElement should have 'dark' class
      expect(document.documentElement.classList.contains('dark')).toBe(true);
    });

    it('should not add "dark" class to document.documentElement when theme is "light"', () => {
      // Arrange: Set localStorage to 'light'
      localStorage.setItem('theme', 'light');

      // Act: Render ThemeProvider
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Assert: document.documentElement should not have 'dark' class
      expect(document.documentElement.classList.contains('dark')).toBe(false);
    });

    it('should not add "dark" class when defaulting to "light"', () => {
      // Arrange: localStorage is empty

      // Act: Render ThemeProvider
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Assert: document.documentElement should not have 'dark' class
      expect(document.documentElement.classList.contains('dark')).toBe(false);
    });
  });

  describe('ARIA live region for screen reader announcements', () => {
    it('should render ARIA live region with "Light mode enabled" when theme is light', () => {
      // Arrange: Set localStorage to 'light'
      localStorage.setItem('theme', 'light');

      // Act: Render ThemeProvider
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Assert: ARIA live region should announce light mode
      const liveRegion = screen.getByRole('status');
      expect(liveRegion).toBeInTheDocument();
      expect(liveRegion).toHaveTextContent('Light mode enabled');
      expect(liveRegion).toHaveAttribute('aria-live', 'polite');
      expect(liveRegion).toHaveAttribute('aria-atomic', 'true');
    });

    it('should render ARIA live region with "Dark mode enabled" when theme is dark', () => {
      // Arrange: Set localStorage to 'dark'
      localStorage.setItem('theme', 'dark');

      // Act: Render ThemeProvider
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Assert: ARIA live region should announce dark mode
      const liveRegion = screen.getByRole('status');
      expect(liveRegion).toBeInTheDocument();
      expect(liveRegion).toHaveTextContent('Dark mode enabled');
      expect(liveRegion).toHaveAttribute('aria-live', 'polite');
      expect(liveRegion).toHaveAttribute('aria-atomic', 'true');
    });
  });

  describe('useTheme hook error handling', () => {
    it('should throw descriptive error when useTheme is used outside ThemeProvider', () => {
      // Arrange: Component that uses useTheme without ThemeProvider
      const ComponentWithoutProvider = () => {
        useTheme(); // This should throw
        return <div>Should not render</div>;
      };

      // Act & Assert: Rendering should throw an error
      expect(() => {
        render(<ComponentWithoutProvider />);
      }).toThrow('useTheme must be used within a ThemeProvider');
    });

    it('should include guidance message in error when used outside provider', () => {
      // Arrange: Component that uses useTheme without ThemeProvider
      const ComponentWithoutProvider = () => {
        useTheme(); // This should throw
        return <div>Should not render</div>;
      };

      // Act & Assert: Error should include guidance
      expect(() => {
        render(<ComponentWithoutProvider />);
      }).toThrow('Please wrap your component tree with <ThemeProvider>');
    });

    it('should not throw error when useTheme is used inside ThemeProvider', () => {
      // Arrange: Component that uses useTheme inside ThemeProvider
      const ComponentWithProvider = () => {
        const { theme } = useTheme();
        return <div data-testid="theme">{theme}</div>;
      };

      // Act & Assert: Should render without throwing
      expect(() => {
        render(
          <ThemeProvider>
            <ComponentWithProvider />
          </ThemeProvider>
        );
      }).not.toThrow();

      // Verify it rendered correctly
      expect(screen.getByTestId('theme')).toBeInTheDocument();
    });
  });

  describe('localStorage error handling', () => {
    it('should handle localStorage.setItem throwing an error', () => {
      // Arrange: Mock localStorage.setItem to throw an error
      const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const originalSetItem = Storage.prototype.setItem;
      Storage.prototype.setItem = vi.fn(() => {
        throw new Error('localStorage quota exceeded');
      });

      // Act: Render ThemeProvider (which will try to save to localStorage)
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Assert: App should still function and warning should be logged
      expect(screen.getByTestId('theme-display')).toHaveTextContent('light');
      expect(consoleWarnSpy).toHaveBeenCalledWith(
        'Failed to save theme preference to localStorage:',
        expect.any(Error)
      );

      // Cleanup
      Storage.prototype.setItem = originalSetItem;
      consoleWarnSpy.mockRestore();
    });

    it('should continue functioning when localStorage is completely unavailable', () => {
      // Arrange: Mock both getItem and setItem to throw errors
      const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      const originalGetItem = Storage.prototype.getItem;
      const originalSetItem = Storage.prototype.setItem;
      
      Storage.prototype.getItem = vi.fn(() => {
        throw new Error('localStorage not available');
      });
      Storage.prototype.setItem = vi.fn(() => {
        throw new Error('localStorage not available');
      });

      // Act: Render ThemeProvider
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Assert: App should still function with in-memory state
      expect(screen.getByTestId('theme-display')).toHaveTextContent('light');
      expect(consoleWarnSpy).toHaveBeenCalled();

      // Cleanup
      Storage.prototype.getItem = originalGetItem;
      Storage.prototype.setItem = originalSetItem;
      consoleWarnSpy.mockRestore();
    });
  });
});
