# Implementation Plan: LeetCode Autocomplete Search

## Overview

This implementation plan breaks down the autocomplete search feature into discrete, incremental tasks. The approach follows a bottom-up strategy: building core utilities first, then services, then UI components, and finally integration. Each task builds on previous work and includes testing to validate functionality early.

## Tasks

- [ ] 1. Set up backend search service infrastructure
  - Create `backend/services/search_service.py` with SearchService class
  - Define ProblemSuggestion, SearchRequest, and SearchResponse models
  - Implement basic GraphQL query structure for LeetCode API
  - Add search service configuration to backend config
  - _Requirements: 4.1, 4.2_

- [ ]* 1.1 Write property test for GraphQL query structure
  - **Property 7: GraphQL Query Structure**
  - **Validates: Requirements 4.2**
  - Generate random search queries and verify GraphQL query includes required fields

- [ ] 2. Implement backend search cache
  - [ ] 2.1 Create SearchCache class with LRU eviction
    - Implement get, set, and clear methods
    - Add timestamp tracking for cache entries
    - Implement TTL-based expiration (1 hour)
    - _Requirements: 8.1, 8.2, 8.3_

  - [ ]* 2.2 Write property tests for cache behavior
    - **Property 15: Cache-First Strategy**
    - **Validates: Requirements 8.1, 8.2**
    - **Property 16: Cache Expiration**
    - **Validates: Requirements 8.3, 8.4**
    - **Property 17: Cache Size Limit**
    - **Validates: Requirements 8.5**

- [ ] 3. Implement LeetCode GraphQL API integration
  - [ ] 3.1 Add GraphQL query method to SearchService
    - Implement `_query_leetcode_api` method
    - Add request timeout and error handling
    - Implement response parsing logic
    - _Requirements: 4.1, 4.3_

  - [ ]* 3.2 Write property test for API response parsing
    - **Property 8: API Response Parsing**
    - **Validates: Requirements 4.3**
    - Generate mock API responses and verify correct parsing

  - [ ] 3.3 Implement error handling for API failures
    - Handle timeout errors (504)
    - Handle rate limit errors (429) with exponential backoff
    - Handle network errors (502)
    - Handle unexpected errors (500)
    - _Requirements: 4.4, 4.5, 7.1, 7.2, 7.4_

  - [ ]* 3.4 Write property test for exponential backoff
    - **Property 13: Exponential Backoff**
    - **Validates: Requirements 7.2**
    - Simulate rate limit errors and verify retry delays increase exponentially

- [ ] 4. Create backend API endpoint
  - [ ] 4.1 Add `/api/search-problems` POST endpoint to main.py
    - Implement request validation
    - Integrate SearchService
    - Add response formatting
    - Add error handling middleware
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ]* 4.2 Write unit tests for API endpoint
    - Test valid search requests
    - Test invalid requests (empty query, too short)
    - Test error responses
    - Test rate limiting behavior

- [ ] 5. Checkpoint - Backend search service complete
  - Ensure all backend tests pass
  - Test search endpoint manually with Postman or curl
  - Verify cache is working correctly
  - Ask the user if questions arise

- [ ] 6. Create frontend debounce hook
  - [ ] 6.1 Implement useDebounce custom hook
    - Create `frontend/src/hooks/useDebounce.ts`
    - Implement timer-based debouncing with cleanup
    - Add TypeScript types
    - _Requirements: 3.1, 3.2, 3.3_

  - [ ]* 6.2 Write property test for debounce behavior
    - **Property 5: Debounce Behavior**
    - **Validates: Requirements 3.1, 3.2, 3.3**
    - Generate random input sequences and verify timing

- [ ] 7. Create frontend search cache utility
  - [ ] 7.1 Implement SearchCache class
    - Create `frontend/src/utils/searchCache.ts`
    - Implement Map-based cache with TTL
    - Add LRU eviction when max size reached
    - Add TypeScript interfaces
    - _Requirements: 8.1, 8.2, 8.5_

  - [ ]* 7.2 Write property tests for frontend cache
    - **Property 15: Cache-First Strategy** (frontend)
    - **Property 17: Cache Size Limit** (frontend)
    - Verify cache behavior matches backend cache properties

- [ ] 8. Implement SuggestionItem component
  - [ ] 8.1 Create SuggestionItem component
    - Create `frontend/src/components/SuggestionItem.tsx`
    - Implement rendering of problem number, title, difficulty
    - Add hover and highlight states
    - Add difficulty color coding (Easy=green, Medium=yellow, Hard=red)
    - Add ARIA attributes for accessibility
    - _Requirements: 2.2, 9.3, 10.1, 10.5_

  - [ ]* 8.2 Write property test for suggestion display
    - **Property 3: Suggestion Display Completeness**
    - **Validates: Requirements 2.2**
    - Generate random suggestions and verify all fields are rendered

- [ ] 9. Implement AutocompleteSearch component
  - [ ] 9.1 Create AutocompleteSearch component structure
    - Create `frontend/src/components/AutocompleteSearch.tsx`
    - Set up component state (searchQuery, suggestions, isLoading, etc.)
    - Implement input field with change handler
    - Add TypeScript interfaces
    - _Requirements: 1.1, 1.2, 2.1_

  - [ ] 9.2 Implement search API integration
    - Add fetch call to `/api/search-problems`
    - Integrate useDebounce hook
    - Implement request cancellation with AbortController
    - Add loading state management
    - _Requirements: 3.1, 3.4, 4.1_

  - [ ]* 9.3 Write property test for request cancellation
    - **Property 6: Request Cancellation**
    - **Validates: Requirements 3.4**
    - Simulate rapid typing and verify previous requests are cancelled

  - [ ] 9.4 Implement suggestions dropdown
    - Add dropdown container with conditional rendering
    - Integrate SuggestionItem components
    - Implement click-outside-to-close behavior
    - Add loading spinner display
    - Limit display to 10 suggestions
    - _Requirements: 2.1, 2.3, 2.4, 2.5, 9.1_

  - [ ]* 9.5 Write property test for suggestion count limit
    - **Property 4: Suggestion Count Limit**
    - **Validates: Requirements 2.4**
    - Generate result sets of various sizes and verify max 10 displayed

  - [ ] 9.6 Implement keyboard navigation
    - Add keydown handler for arrow keys, Enter, Escape
    - Implement highlight state management with wrapping
    - Add keyboard selection logic
    - Update ARIA attributes for screen reader announcements
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 10.3, 10.4_

  - [ ]* 9.7 Write property tests for keyboard navigation
    - **Property 11: Keyboard Navigation**
    - **Validates: Requirements 6.1, 6.2, 6.5**
    - **Property 12: Keyboard Selection**
    - **Validates: Requirements 6.3**
    - **Property 18: Focus Management**
    - **Validates: Requirements 10.3, 10.4**

  - [ ] 9.8 Implement problem selection logic
    - Add selection handler that populates URL field
    - Mark input as valid on selection
    - Close dropdown on selection
    - Trigger problem details fetch
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ]* 9.9 Write property tests for selection behavior
    - **Property 9: Problem Selection Behavior**
    - **Validates: Requirements 5.1, 5.2, 5.4**
    - **Property 10: Problem Details Caching**
    - **Validates: Requirements 5.5**

  - [ ] 9.10 Add error handling and edge cases
    - Display "No results found" for empty results
    - Display error messages for API failures
    - Handle rate limiting with user-friendly messages
    - Show loading indicator after 500ms delay
    - _Requirements: 2.3, 7.1, 7.4, 7.5_

  - [ ]* 9.11 Write property test for loading indicator timing
    - **Property 14: Loading Indicator Timing**
    - **Validates: Requirements 7.5**

- [ ] 10. Checkpoint - Autocomplete component complete
  - Ensure all frontend tests pass
  - Test component in isolation with mock data
  - Verify keyboard navigation works correctly
  - Verify accessibility with screen reader
  - Ask the user if questions arise

- [ ] 11. Enhance ProblemInput component
  - [ ] 11.1 Add input mode detection
    - Detect URL pattern (starts with http)
    - Switch between URL mode and search mode
    - Maintain backward compatibility
    - _Requirements: 1.4, 1.5_

  - [ ]* 11.2 Write property test for input mode detection
    - **Property 2: Input Mode Detection**
    - **Validates: Requirements 1.4, 1.5**
    - Generate various inputs and verify correct mode selection

  - [ ] 11.3 Integrate AutocompleteSearch component
    - Replace or enhance existing input with AutocompleteSearch
    - Pass through onUrlChange callback
    - Maintain existing validation flow
    - Add smooth transition between modes
    - _Requirements: 1.1, 1.4, 5.4_

  - [ ]* 11.4 Write integration tests
    - Test URL input still works
    - Test search input works
    - Test switching between modes
    - Test validation flow consistency

- [ ] 12. Add search query threshold validation
  - [ ] 12.1 Implement 2-character minimum threshold
    - Add validation in AutocompleteSearch component
    - Clear suggestions for queries < 2 characters
    - Trigger search for queries >= 2 characters
    - _Requirements: 1.2, 1.3_

  - [ ]* 12.2 Write property test for search threshold
    - **Property 1: Search Trigger Threshold**
    - **Validates: Requirements 1.2, 1.3**
    - Generate strings of various lengths and verify threshold behavior

- [ ] 13. Implement frontend cache integration
  - [ ] 13.1 Integrate SearchCache into AutocompleteSearch
    - Check cache before API calls
    - Store results in cache after successful fetch
    - Handle cache errors gracefully
    - _Requirements: 8.1, 8.2, 8.4_

  - [ ]* 13.2 Write property test for cache integration
    - Verify cache-first strategy in component
    - Verify cache updates after API calls

- [ ] 14. Add accessibility enhancements
  - [ ] 14.1 Implement ARIA attributes
    - Add role="combobox" to input
    - Add role="listbox" to dropdown
    - Add role="option" to suggestions
    - Add aria-expanded, aria-activedescendant
    - Add aria-live region for result announcements
    - _Requirements: 10.1, 10.2, 10.5_

  - [ ]* 14.2 Write accessibility tests
    - Verify all ARIA attributes are present
    - Verify screen reader announcements
    - Test with axe-core or similar tool

- [ ] 15. Add visual polish and animations
  - Add smooth dropdown open/close transitions
  - Add hover effects on suggestions
  - Add selection confirmation animation
  - Style loading spinner
  - Add difficulty color coding
  - _Requirements: 9.2, 9.3, 9.4, 9.5_

- [ ] 16. Final integration and testing
  - [ ] 16.1 Integration testing
    - Test complete flow: search → select → analyze
    - Test with real LeetCode API
    - Test error scenarios end-to-end
    - Test on different browsers
    - _Requirements: All_

  - [ ]* 16.2 End-to-end property tests
    - Run all property tests with increased iterations (500+)
    - Verify all 18 correctness properties pass
    - Check test coverage meets 80%+ goal

- [ ] 17. Final checkpoint - Feature complete
  - Ensure all tests pass (unit and property)
  - Verify feature works in production-like environment
  - Test accessibility compliance
  - Review error handling for all edge cases
  - Ask the user for final approval

## Notes

- Tasks marked with `*` are optional property-based tests that can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation throughout implementation
- Property tests validate universal correctness properties with minimum 100 iterations
- Unit tests validate specific examples and edge cases
- The implementation follows a bottom-up approach: utilities → services → components → integration
