# Implementation Plan: Theme Toggle Feature

## Overview

This implementation plan breaks down the theme toggle feature into discrete, incremental tasks. Each task builds on previous work, starting with core infrastructure (context and provider), then adding UI components, integrating with existing components, and finally adding tests. The approach ensures that functionality can be validated at each step.

## Tasks

- [ ] 1. Create theme context and provider infrastructure
  - [x] 1.1 Create ThemeContext with type definitions
    - Create `frontend/src/contexts/ThemeContext.tsx`
    - Define `Theme` type as `'light' | 'dark'`
    - Define `ThemeContextType` interface with `theme` and `toggleTheme`
    - Create and export `ThemeContext` using `React.createContext`
    - _Requirements: 1.1, 1.3_

  - [x] 1.2 Implement ThemeProvider component
    - Implement state management with `useState<Theme>`
    - Implement `getInitialTheme` function to load from localStorage with fallback to 'light'
    - Implement `toggleTheme` function to switch between themes
    - Add `useEffect` to update `document.documentElement.classList` when theme changes
    - Add `useEffect` to save theme to localStorage when theme changes
    - Wrap children with `ThemeContext.Provider`
    - _Requirements: 1.1, 1.2, 1.4, 1.5, 3.1, 3.2_

  - [x] 1.3 Create useTheme custom hook
    - Create `frontend/src/hooks/useTheme.ts`
    - Implement hook that consumes `ThemeContext`
    - Throw descriptive error if used outside `ThemeProvider`
    - Export hook for use in components
    - _Requirements: 1.1_

  - [ ]* 1.4 Write property test for theme state propagation
    - **Property 1: Theme State Propagation**
    - **Validates: Requirements 1.2**
    - Test that theme changes propagate to all context consumers
    - Use fast-check to generate random theme changes
    - Verify multiple consumers receive updated values

  - [ ]* 1.5 Write property test for theme value validation
    - **Property 2: Theme Value Validation**
    - **Validates: Requirements 1.3**
    - Test that only 'light' and 'dark' are valid theme values
    - Use fast-check to generate random strings
    - Verify invalid values are rejected or default to 'light'

  - [x] 1.6 Write unit tests for ThemeProvider initialization
    - Test loading saved theme from localStorage
    - Test default to 'light' when no saved preference exists
    - Test handling of corrupted localStorage data
    - _Requirements: 1.4, 1.5_

- [ ] 2. Create ThemeToggle UI component
  - [x] 2.1 Implement ThemeToggle button component
    - Create `frontend/src/components/ThemeToggle.tsx`
    - Import `Sun` and `Moon` icons from lucide-react
    - Use `useTheme` hook to access theme state and toggle function
    - Render button with conditional icon (Sun for dark mode, Moon for light mode)
    - Add click handler that calls `toggleTheme`
    - Add Tailwind classes for styling with dark mode variants
    - Add smooth rotation animation on theme change
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 2.2 Add accessibility features to ThemeToggle
    - Add `aria-label` describing current action (e.g., "Switch to dark mode")
    - Make button keyboard accessible (focusable, responds to Enter/Space)
    - Add focus visible styles
    - Add ARIA live region for screen reader announcements
    - _Requirements: 8.3, 8.4, 8.5_

  - [ ]* 2.3 Write property test for theme toggle inversion
    - **Property 3: Theme Toggle Inversion**
    - **Validates: Requirements 2.2**
    - Test that clicking toggle switches to opposite theme
    - Use fast-check to generate random starting themes
    - Verify light → dark and dark → light transitions

  - [x] 2.4 Write unit tests for ThemeToggle component
    - Test button is rendered and visible
    - Test correct icon is displayed for each theme
    - Test button has proper ARIA labels
    - Test keyboard accessibility (focus, Enter, Space)
    - _Requirements: 2.1, 2.3, 8.3, 8.4_

- [x] 3. Integrate ThemeProvider and ThemeToggle into App
  - [x] 3.1 Wrap App with ThemeProvider
    - Update `frontend/src/main.tsx` to wrap `<App />` with `<ThemeProvider>`
    - Set `storageKey` prop to `'leetcode-analyzer-theme'`
    - Verify app still renders correctly
    - _Requirements: 1.1, 1.2_

  - [x] 3.2 Add ThemeToggle to application header
    - Import `ThemeToggle` component in `App.tsx`
    - Add `ThemeToggle` button to header section (near "View History" and "Shortcuts" buttons)
    - Position with Tailwind classes for consistent layout
    - Test that toggle appears and is clickable
    - _Requirements: 2.1, 2.5_

- [x] 4. Add dark mode styles to existing components
  - [x] 4.1 Update main container and background styles
    - Update root container in `App.tsx` to include dark mode gradient
    - Change `bg-gradient-to-br from-slate-50 to-slate-100` to include `dark:from-slate-900 dark:to-slate-800`
    - _Requirements: 4.1, 5.1_

  - [x] 4.2 Update card and panel components
    - Add dark mode classes to all `bg-white` elements: `dark:bg-slate-800`
    - Update text colors: `text-slate-800` → `dark:text-slate-100`, `text-slate-600` → `dark:text-slate-300`
    - Update borders: `border-slate-300` → `dark:border-slate-600`
    - Apply to: input panel, results panel, history panel, keyboard shortcuts modal
    - _Requirements: 4.1, 4.2, 5.1, 5.2, 7.1, 7.2_

  - [x] 4.3 Update form inputs and selects
    - Add dark mode classes to input fields and select dropdowns
    - Update focus ring colors for dark mode
    - Update placeholder text colors
    - _Requirements: 7.2_

  - [x] 4.4 Update button styles
    - Add dark mode hover states to all buttons
    - Adjust gradient colors for better contrast in dark mode
    - Update disabled button styles for dark mode
    - _Requirements: 7.2_

  - [x] 4.5 Update loading indicators and progress bars
    - Add dark mode colors to loading spinner
    - Update progress bar colors for dark mode
    - Update loading message text colors
    - _Requirements: 7.5_

  - [x] 4.6 Update modal and overlay components
    - Add dark mode styles to KeyboardShortcutsHelp modal
    - Update modal backdrop colors for dark mode
    - Update modal content background and text colors
    - _Requirements: 7.6_

  - [ ]* 4.7 Write property test for DOM class reflection
    - **Property 5: DOM Class Reflects Theme**
    - **Validates: Requirements 4.1, 5.1**
    - Test that document root has 'dark' class if and only if theme is 'dark'
    - Use fast-check to generate random theme states
    - Verify DOM class presence matches theme value

- [x] 5. Integrate Monaco Editor with theme system
  - [x] 5.1 Update Monaco Editor theme prop
    - In `App.tsx`, use `useTheme` hook to get current theme
    - Update `<Editor>` component to use `theme={theme === 'dark' ? 'vs-dark' : 'vs-light'}`
    - Test that editor theme changes when app theme changes
    - _Requirements: 4.5, 5.5, 7.3_

  - [ ]* 5.2 Write property test for Monaco editor theme synchronization
    - **Property 6: Monaco Editor Theme Synchronization**
    - **Validates: Requirements 4.5, 5.5**
    - Test that Monaco editor theme matches app theme
    - Use fast-check to generate random theme states
    - Verify editor receives correct theme prop

  - [ ]* 5.3 Write unit test for Monaco editor integration
    - Test editor receives 'vs-dark' when theme is 'dark'
    - Test editor receives 'vs-light' when theme is 'light'
    - _Requirements: 4.5, 5.5_

- [x] 6. Add global transition styles
  - [x] 6.1 Update global CSS with transition styles
    - Add transition properties to `frontend/src/index.css`
    - Add transitions for `background-color`, `border-color`, `color`, `fill`, `stroke`
    - Set duration to 200ms with ease-in-out timing
    - _Requirements: 6.1, 6.2_

  - [ ]* 6.2 Write unit test for scroll position preservation
    - Test that scroll position is maintained during theme change
    - Set scroll position, change theme, verify position unchanged
    - _Requirements: 6.4_

- [x] 7. Add error handling and edge cases
  - [x] 7.1 Add localStorage error handling
    - Wrap localStorage operations in try-catch blocks in ThemeProvider
    - Log errors to console when localStorage fails
    - Ensure app continues to function without persistence
    - _Requirements: 3.1, 3.2_

  - [x] 7.2 Add context error handling
    - Ensure `useTheme` throws descriptive error when used outside provider
    - Add error message guiding developer to wrap app with ThemeProvider
    - _Requirements: 1.1_

  - [ ]* 7.3 Write unit tests for error handling
    - Test behavior when localStorage is unavailable
    - Test useTheme throws error outside provider
    - Test handling of invalid localStorage values
    - _Requirements: 3.1, 3.2_

- [ ] 8. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ]* 9. Write property test for localStorage persistence round-trip
  - **Property 4: LocalStorage Persistence Round-Trip**
  - **Validates: Requirements 3.1**
  - Test that saving theme to localStorage and loading it produces same value
  - Use fast-check to generate random theme values
  - Verify round-trip consistency

- [ ]* 10. Write integration tests
  - Test complete theme toggle flow from button click to DOM update
  - Test theme persistence across simulated page refreshes
  - Test screen reader announcements on theme change
  - _Requirements: 2.2, 3.1, 3.2, 8.5_

- [ ] 11. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The implementation uses React Context API for state management and Tailwind CSS for styling
- All color transitions are handled via CSS for smooth theme changes
