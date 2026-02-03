import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider } from '../contexts/ThemeContext';
import { ThemeToggle } from './ThemeToggle';

describe('ThemeToggle Component', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Remove dark class from document element
    document.documentElement.classList.remove('dark');
  });

  describe('Button rendering and visibility', () => {
    it('should render the toggle button', () => {
      // Act: Render ThemeToggle within ThemeProvider
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );

      // Assert: Button should be in the document
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });

    it('should be visible and accessible', () => {
      // Act: Render ThemeToggle
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );

      // Assert: Button should be visible
      const button = screen.getByRole('button');
      expect(button).toBeVisible();
    });
  });

  describe('Icon display based on theme', () => {
    it('should display Moon icon in light mode', () => {
      // Arrange: Set theme to light
      localStorage.setItem('theme', 'light');

      // Act: Render ThemeToggle
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );

      // Assert: Button should have aria-label for switching to dark mode
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Switch to dark mode');
    });

    it('should display Sun icon in dark mode', () => {
      // Arrange: Set theme to dark
      localStorage.setItem('theme', 'dark');

      // Act: Render ThemeToggle
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );

      // Assert: Button should have aria-label for switching to light mode
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Switch to light mode');
    });
  });

  describe('ARIA labels and accessibility', () => {
    it('should have proper aria-label in light mode', () => {
      // Arrange: Set theme to light
      localStorage.setItem('theme', 'light');

      // Act: Render ThemeToggle
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );

      // Assert: Button should have descriptive aria-label
      const button = screen.getByRole('button', { name: 'Switch to dark mode' });
      expect(button).toBeInTheDocument();
    });

    it('should have proper aria-label in dark mode', () => {
      // Arrange: Set theme to dark
      localStorage.setItem('theme', 'dark');

      // Act: Render ThemeToggle
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );

      // Assert: Button should have descriptive aria-label
      const button = screen.getByRole('button', { name: 'Switch to light mode' });
      expect(button).toBeInTheDocument();
    });

    it('should update aria-label when theme changes', async () => {
      // Arrange: Start with light theme
      localStorage.setItem('theme', 'light');
      const user = userEvent.setup();

      // Act: Render ThemeToggle
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );

      // Assert: Initial aria-label
      let button = screen.getByRole('button', { name: 'Switch to dark mode' });
      expect(button).toBeInTheDocument();

      // Act: Click to toggle theme
      await user.click(button);

      // Assert: aria-label should update
      button = screen.getByRole('button', { name: 'Switch to light mode' });
      expect(button).toBeInTheDocument();
    });

    it('should have ARIA live region for screen reader announcements', () => {
      // Arrange: Start with light theme
      localStorage.setItem('theme', 'light');

      // Act: Render ThemeToggle
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );

      // Assert: ARIA live region should exist with correct attributes
      const liveRegions = screen.getAllByRole('status');
      expect(liveRegions.length).toBeGreaterThan(0);
      const liveRegion = liveRegions[0];
      expect(liveRegion).toBeInTheDocument();
      expect(liveRegion).toHaveAttribute('aria-live', 'polite');
      expect(liveRegion).toHaveAttribute('aria-atomic', 'true');
      expect(liveRegion).toHaveTextContent('Light mode enabled');
    });

    it('should announce theme changes to screen readers', async () => {
      // Arrange: Start with light theme
      localStorage.setItem('theme', 'light');
      const user = userEvent.setup();

      // Act: Render ThemeToggle
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );

      // Assert: Initial announcement
      let liveRegions = screen.getAllByRole('status');
      expect(liveRegions[0]).toHaveTextContent('Light mode enabled');

      // Act: Click to toggle theme
      const button = screen.getByRole('button');
      await user.click(button);

      // Assert: Announcement should update
      liveRegions = screen.getAllByRole('status');
      expect(liveRegions[0]).toHaveTextContent('Dark mode enabled');
    });
  });

  describe('Keyboard accessibility', () => {
    it('should be focusable', () => {
      // Act: Render ThemeToggle
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );

      // Assert: Button should be focusable
      const button = screen.getByRole('button');
      button.focus();
      expect(button).toHaveFocus();
    });

    it('should toggle theme when Enter key is pressed', async () => {
      // Arrange: Start with light theme
      localStorage.setItem('theme', 'light');
      const user = userEvent.setup();

      // Act: Render ThemeToggle
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );

      // Assert: Initial state
      expect(document.documentElement.classList.contains('dark')).toBe(false);

      // Act: Focus button and press Enter
      const button = screen.getByRole('button');
      button.focus();
      await user.keyboard('{Enter}');

      // Assert: Theme should toggle to dark
      expect(document.documentElement.classList.contains('dark')).toBe(true);
    });

    it('should toggle theme when Space key is pressed', async () => {
      // Arrange: Start with light theme
      localStorage.setItem('theme', 'light');
      const user = userEvent.setup();

      // Act: Render ThemeToggle
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );

      // Assert: Initial state
      expect(document.documentElement.classList.contains('dark')).toBe(false);

      // Act: Focus button and press Space
      const button = screen.getByRole('button');
      button.focus();
      await user.keyboard(' ');

      // Assert: Theme should toggle to dark
      expect(document.documentElement.classList.contains('dark')).toBe(true);
    });
  });

  describe('Click handler functionality', () => {
    it('should toggle theme from light to dark when clicked', async () => {
      // Arrange: Start with light theme
      localStorage.setItem('theme', 'light');
      const user = userEvent.setup();

      // Act: Render ThemeToggle
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );

      // Assert: Initial state
      expect(document.documentElement.classList.contains('dark')).toBe(false);

      // Act: Click button
      const button = screen.getByRole('button');
      await user.click(button);

      // Assert: Theme should toggle to dark
      expect(document.documentElement.classList.contains('dark')).toBe(true);
    });

    it('should toggle theme from dark to light when clicked', async () => {
      // Arrange: Start with dark theme
      localStorage.setItem('theme', 'dark');
      const user = userEvent.setup();

      // Act: Render ThemeToggle
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );

      // Assert: Initial state
      expect(document.documentElement.classList.contains('dark')).toBe(true);

      // Act: Click button
      const button = screen.getByRole('button');
      await user.click(button);

      // Assert: Theme should toggle to light
      expect(document.documentElement.classList.contains('dark')).toBe(false);
    });

    it('should toggle theme multiple times', async () => {
      // Arrange: Start with light theme
      localStorage.setItem('theme', 'light');
      const user = userEvent.setup();

      // Act: Render ThemeToggle
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );

      const button = screen.getByRole('button');

      // Assert: Initial state (light)
      expect(document.documentElement.classList.contains('dark')).toBe(false);

      // Act: Click to toggle to dark
      await user.click(button);
      expect(document.documentElement.classList.contains('dark')).toBe(true);

      // Act: Click to toggle back to light
      await user.click(button);
      expect(document.documentElement.classList.contains('dark')).toBe(false);

      // Act: Click to toggle to dark again
      await user.click(button);
      expect(document.documentElement.classList.contains('dark')).toBe(true);
    });
  });

  describe('Custom className prop', () => {
    it('should apply custom className when provided', () => {
      // Act: Render ThemeToggle with custom className
      render(
        <ThemeProvider>
          <ThemeToggle className="custom-class ml-4" />
        </ThemeProvider>
      );

      // Assert: Button should have custom class
      const button = screen.getByRole('button');
      expect(button).toHaveClass('custom-class');
      expect(button).toHaveClass('ml-4');
    });

    it('should work without custom className', () => {
      // Act: Render ThemeToggle without custom className
      render(
        <ThemeProvider>
          <ThemeToggle />
        </ThemeProvider>
      );

      // Assert: Button should still render correctly
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });
  });
});
