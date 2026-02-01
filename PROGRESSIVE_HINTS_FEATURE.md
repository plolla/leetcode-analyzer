# Progressive Hints Feature

## Overview
Implemented a progressive hint reveal system that mimics real interview scenarios where hints are given one at a time.

## Features

### 1. First Hint Auto-Revealed
- The first hint is always visible by default
- Helps users get started without friction

### 2. Subsequent Hints Blurred
- Hints 2+ are blurred with a semi-transparent overlay
- Prevents accidental spoilers
- Encourages users to try solving with minimal hints

### 3. Next Steps Also Blurred
- The "Next Steps" section is also blurred by default
- Users must reveal it intentionally
- Maintains the progressive learning experience

### 4. Single Reveal Button
- Each blurred section has one centered "Click to Reveal" button
- Clean, simple interface
- Button appears on hover over the blurred area
- Once revealed, hints stay visible (no hide option to keep it simple)

### 5. Visual Design
- **Info Banner**: Purple banner explaining the progressive hint system
- **Hint Labels**: "Hint 1", "Hint 2", etc. in purple text
- **Blur Effect**: CSS blur filter on unrevealed hints
- **Overlay Button**: Large, centered "Click to Reveal" button on blurred content
- **Gradient Overlay**: Semi-transparent white gradient over blurred content

### 6. Interview-Like Experience
- Mimics how interviewers give hints progressively
- Encourages problem-solving with minimal assistance
- Users can track how many hints they needed

## Technical Implementation

### State Management
```typescript
const [revealedHints, setRevealedHints] = useState<Set<number>>(new Set([0]));
const [nextStepsRevealed, setNextStepsRevealed] = useState(false);
```
- Uses React `useState` with a Set to track revealed hint indices
- First hint (index 0) is in the set by default
- Separate boolean state for Next Steps section

### Toggle Function
```typescript
const toggleHint = (index: number) => {
  setRevealedHints(prev => {
    const newSet = new Set(prev);
    if (newSet.has(index)) {
      newSet.delete(index);
    } else {
      newSet.add(index);
    }
    return newSet;
  });
};
```

### Visual Effects
- **Blur**: `blur-md filter` class on unrevealed content
- **Overlay**: Gradient overlay with centered reveal button
- **Select Prevention**: `select-none` prevents text selection on blurred content
- **Smooth Transitions**: `transition-all` for smooth reveal animations
- **Clickable Area**: Entire blurred area is clickable for better UX

## User Experience

### Before Revealing
```
┌─────────────────────────────────────┐
│ 💡 Progressive Hints: Hints are    │
│ revealed one at a time...           │
└─────────────────────────────────────┘

Hint 1
This is the first hint (always visible)

Hint 2
████████████████████████████████
█  Click to Reveal Hint 2      █
████████████████████████████████

Hint 3
████████████████████████████████
█  Click to Reveal Hint 3      █
████████████████████████████████

Next Steps:
████████████████████████████████
█  Click to Reveal Next Steps  █
████████████████████████████████
```

### After Revealing
```
Hint 1
This is the first hint (always visible)

Hint 2
This is the second hint (now visible)

Hint 3
████████████████████████████████
█  Click to Reveal Hint 3      █
████████████████████████████████

Next Steps:
████████████████████████████████
█  Click to Reveal Next Steps  █
████████████████████████████████
```

## Benefits

1. **Pedagogical**: Encourages independent problem-solving
2. **Interview Prep**: Simulates real interview hint-giving
3. **Self-Assessment**: Users can track hint usage
4. **Spoiler Prevention**: Avoids accidental hint reading
5. **Simple UX**: One-way reveal keeps interface clean and simple
6. **Complete Coverage**: Both hints and next steps are protected

## Future Enhancements (Optional)

- Track and display hint count: "You used 2 out of 4 hints"
- Add hint difficulty indicators
- Save hint reveal state in history
- Add keyboard shortcuts for revealing hints (e.g., Ctrl+H)
- Animate the reveal transition with fade-in effect
- Add a "Reveal All" button for users who want all hints at once
- Show a congratulations message if user solves with minimal hints
