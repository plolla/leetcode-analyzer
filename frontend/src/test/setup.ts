import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';

// Cleanup after each test
afterEach(() => {
  cleanup();
  // Clear localStorage after each test
  localStorage.clear();
  // Remove dark class from document element
  document.documentElement.classList.remove('dark');
});
