# Design Document: Theme Toggle Feature

## Overview

The theme toggle feature will implement a light/dark mode system for the LeetCode Analyzer application using React Context API for state management, CSS custom properties (CSS variables) for theming, and localStorage for persistence. The design leverages Tailwind CSS's dark mode utilities and integrates with the existing Monaco editor component.

The implementation follows a provider pattern where a `ThemeProvider` component wraps the application and makes theme state available to all child components. Theme changes trigger CSS class updates on the root HTML element, which cascades theme-specific styles throughout the application.

## Architecture

### Component Hierarchy

```
App (wrapped by ThemeProvider)
├── ThemeProvider (Context Provider)
│   ├── Theme State Management
│   ├── localStorage Integration
│   └── Theme Context
└── Application Components
    ├── Header (contains ThemeToggle)
    ├── ThemeToggle Button
    └── All other components (consume theme via Tailwind dark: classes)
```

### Data Flow

1. **Initialization**: ThemeProvider reads from localStorage or defaults to 'light'
2. **User Action**: User clicks ThemeToggle button
3. **State Update**: ThemeProvider updates internal state
4. **DOM Update**: ThemeProvider adds/removes 'dark' class on document.documentElement
5. **Persistence**: ThemeProvider saves new preference to localStorage
6. **Re-render**: React re-renders components with new theme classes

### Technology Stack

- **State Management**: React Context API + useState hook
- **Styling**: Tailwind CSS with dark mode variant
- **Persistence**: Browser localStorage API
- **Icons**: lucide-react (Sun/Moon icons)
- **Editor Theming**: Monaco Editor theme API

## Components and Interfaces

### 1. ThemeContext

**Purpose**: Provides theme state and toggle function to all components

**Interface**:
```typescript
type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = React.createContext<ThemeContextType | undefined>(undefined);
```

### 2. ThemeProvider Component

**Purpose**: Manages theme state, persistence, and DOM updates

**Props**:
```typescript
interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: Theme;
  storageKey?: string;
}
```

**Implementation Details**:
- Uses `useState` to manage current theme
- Uses `useEffect` to:
  - Load initial theme from localStorage on mount
  - Update document.documentElement class when theme changes
  - Save theme to localStorage when theme changes
- Provides theme context value to children

**Key Functions**:
```typescript
// Load theme from localStorage or use default
const getInitialTheme = (): Theme => {
  const stored = localStorage.getItem(storageKey);
  if (stored === 'light' || stored === 'dark') {
    return stored;
  }
  return defaultTheme;
};

// Toggle between light and dark
const toggleTheme = () => {
  setTheme(prev => prev === 'light' ? 'dark' : 'light');
};
```

### 3. useTheme Hook

**Purpose**: Custom hook for consuming theme context

**Interface**:
```typescript
function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
```

### 4. ThemeToggle Component

**Purpose**: UI button for switching themes

**Props**:
```typescript
interface ThemeToggleProps {
  className?: string;
}
```

**Implementation Details**:
- Consumes theme context via `useTheme` hook
- Displays Sun icon in dark mode, Moon icon in light mode
- Calls `toggleTheme` on click
- Includes ARIA labels for accessibility
- Styled with Tailwind classes that respond to theme

**Visual Design**:
- Circular button with icon
- Smooth rotation animation on theme change
- Hover and focus states
- Positioned in header area (top-right recommended)

### 5. Monaco Editor Integration

**Purpose**: Apply theme to code editor

**Implementation**:
```typescript
// In component using Monaco Editor
const { theme } = useTheme();

<Editor
  theme={theme === 'dark' ? 'vs-dark' : 'vs-light'}
  // ... other props
/>
```

## Data Models

### Theme Type

```typescript
type Theme = 'light' | 'dark';
```

**Validation**: Only 'light' or 'dark' are valid values

### LocalStorage Schema

**Key**: `'leetcode-analyzer-theme'` (configurable via ThemeProvider prop)

**Value**: `'light' | 'dark'`

**Example**:
```json
{
  "leetcode-analyzer-theme": "dark"
}
```

### Theme Context State

```typescript
interface ThemeContextType {
  theme: Theme;           // Current active theme
  toggleTheme: () => void; // Function to switch themes
}
```

## Styling Implementation

### Tailwind Configuration

The application uses Tailwind CSS v4 with the `dark:` variant for dark mode styles. Tailwind automatically detects the `dark` class on the root element.

**Dark Mode Strategy**: Class-based (not media query based)

### Color Scheme

#### Light Mode Colors
- Background: `bg-gradient-to-br from-slate-50 to-slate-100`
- Cards: `bg-white`
- Text Primary: `text-slate-800`
- Text Secondary: `text-slate-600`
- Borders: `border-slate-300`
- Buttons: Existing gradient colors (blue, purple, red, green)

#### Dark Mode Colors
- Background: `dark:bg-gradient-to-br dark:from-slate-900 dark:to-slate-800`
- Cards: `dark:bg-slate-800`
- Text Primary: `dark:text-slate-100`
- Text Secondary: `dark:text-slate-300`
- Borders: `dark:border-slate-600`
- Buttons: Darker variants of existing colors with adjusted opacity

### CSS Transitions

All color transitions use CSS transitions for smooth changes:

```css
* {
  transition-property: background-color, border-color, color, fill, stroke;
  transition-duration: 200ms;
  transition-timing-function: ease-in-out;
}
```

This will be added to the global styles in `index.css`.

### Component-Specific Styling

Each component will receive dark mode variants using Tailwind's `dark:` prefix:

**Example**:
```tsx
<div className="bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100">
  {/* content */}
</div>
```

## Integration Points

### 1. App.tsx Modifications

- Wrap the entire app with `ThemeProvider`
- Add `ThemeToggle` button to header section
- Update Monaco Editor to use theme-aware theme prop

### 2. Component Updates

All existing components need dark mode class variants added:
- Main container backgrounds
- Card components
- Input fields and selects
- Buttons (adjust hover states)
- Loading indicators
- Modal overlays
- History panel
- Results display

### 3. Monaco Editor

Update the Editor component in App.tsx:
```typescript
const { theme } = useTheme();

<Editor
  theme={theme === 'dark' ? 'vs-dark' : 'vs-light'}
  // ... existing props
/>
```

### 4. Global Styles

Add transition styles to `index.css`:
```css
@layer base {
  * {
    transition-property: background-color, border-color, color, fill, stroke;
    transition-duration: 200ms;
    transition-timing-function: ease-in-out;
  }
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Theme State Propagation

*For any* theme change (from light to dark or dark to light), all components consuming the theme context should receive and reflect the updated theme value.

**Validates: Requirements 1.2**

### Property 2: Theme Value Validation

*For any* attempted theme value assignment, the Theme_System should only accept 'light' or 'dark' as valid values and reject any other values.

**Validates: Requirements 1.3**

### Property 3: Theme Toggle Inversion

*For any* current theme state, clicking the toggle button should switch to the opposite theme (light → dark, dark → light).

**Validates: Requirements 2.2**

### Property 4: LocalStorage Persistence Round-Trip

*For any* theme change, saving the theme to localStorage and then loading it should produce the same theme value.

**Validates: Requirements 3.1**

### Property 5: DOM Class Reflects Theme

*For any* theme state, the document root element should have the 'dark' class if and only if the theme is 'dark'.

**Validates: Requirements 4.1, 5.1**

### Property 6: Monaco Editor Theme Synchronization

*For any* theme state, the Monaco editor should use 'vs-dark' theme when the app theme is 'dark' and 'vs-light' theme when the app theme is 'light'.

**Validates: Requirements 4.5, 5.5**

## Error Handling

### Invalid Theme Values

**Scenario**: User or code attempts to set an invalid theme value

**Handling**:
- TypeScript type system prevents invalid values at compile time
- Runtime validation in ThemeProvider ensures only 'light' or 'dark' are accepted
- Invalid values default to 'light' with console warning

### LocalStorage Errors

**Scenario**: localStorage is unavailable or throws errors (private browsing, quota exceeded)

**Handling**:
- Wrap localStorage operations in try-catch blocks
- Fall back to in-memory state if localStorage fails
- Log errors to console for debugging
- Application continues to function without persistence

**Example**:
```typescript
try {
  localStorage.setItem(storageKey, theme);
} catch (error) {
  console.warn('Failed to save theme preference:', error);
  // Continue with in-memory state
}
```

### Context Not Available

**Scenario**: Component tries to use `useTheme` outside of ThemeProvider

**Handling**:
- `useTheme` hook throws descriptive error
- Error message guides developer to wrap app with ThemeProvider
- Prevents silent failures and undefined behavior

### Missing Icons

**Scenario**: lucide-react icons fail to load

**Handling**:
- Provide text fallback ("Light" / "Dark")
- Button remains functional even without icons
- Graceful degradation of UI

## Testing Strategy

The theme toggle feature will be tested using a dual approach combining unit tests for specific scenarios and property-based tests for universal behaviors.

### Unit Tests

Unit tests will focus on specific examples, edge cases, and integration points:

1. **Initialization Tests**
   - Test loading saved theme from localStorage on mount
   - Test default to light mode when no saved preference exists
   - Test handling of corrupted localStorage data

2. **UI Component Tests**
   - Test ThemeToggle button is rendered and visible
   - Test correct icon is displayed for each theme
   - Test button has proper ARIA labels
   - Test keyboard accessibility (focus, Enter, Space)

3. **Integration Tests**
   - Test Monaco editor receives correct theme prop
   - Test scroll position is maintained during theme change
   - Test screen reader announcements on theme change

4. **Error Handling Tests**
   - Test behavior when localStorage is unavailable
   - Test useTheme throws error outside provider
   - Test handling of invalid localStorage values

### Property-Based Tests

Property tests will verify universal properties across all inputs using a property-based testing library (fast-check for TypeScript):

1. **Property 1: Theme State Propagation**
   - Generate random theme changes
   - Verify all context consumers receive updated value
   - **Tag**: Feature: theme-toggle, Property 1: Theme State Propagation

2. **Property 2: Theme Value Validation**
   - Generate random strings as theme values
   - Verify only 'light' and 'dark' are accepted
   - **Tag**: Feature: theme-toggle, Property 2: Theme Value Validation

3. **Property 3: Theme Toggle Inversion**
   - Generate random starting theme
   - Verify toggle switches to opposite theme
   - **Tag**: Feature: theme-toggle, Property 3: Theme Toggle Inversion

4. **Property 4: LocalStorage Persistence Round-Trip**
   - Generate random theme values
   - Verify save then load produces same value
   - **Tag**: Feature: theme-toggle, Property 4: LocalStorage Persistence Round-Trip

5. **Property 5: DOM Class Reflects Theme**
   - Generate random theme states
   - Verify 'dark' class presence matches theme === 'dark'
   - **Tag**: Feature: theme-toggle, Property 5: DOM Class Reflects Theme

6. **Property 6: Monaco Editor Theme Synchronization**
   - Generate random theme states
   - Verify editor theme matches app theme
   - **Tag**: Feature: theme-toggle, Property 6: Monaco Editor Theme Synchronization

### Test Configuration

- **Property test iterations**: Minimum 100 iterations per test
- **Testing library**: Vitest for unit tests, fast-check for property tests
- **Coverage target**: 90% code coverage for theme-related components
- **CI Integration**: All tests run on every commit

### Testing Tools

- **Vitest**: Test runner and assertion library
- **@testing-library/react**: React component testing utilities
- **@testing-library/user-event**: User interaction simulation
- **fast-check**: Property-based testing library
- **@testing-library/jest-dom**: Custom matchers for DOM assertions
