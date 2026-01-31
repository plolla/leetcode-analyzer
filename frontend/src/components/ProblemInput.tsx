import { useState } from 'react';

interface ProblemInputProps {
  onUrlChange: (url: string, isValid: boolean) => void;
}

interface ValidationState {
  isValid: boolean;
  error: string;
  success: string;
  suggestion?: string;
  examples?: string[];
}

export default function ProblemInput({ onUrlChange }: ProblemInputProps) {
  const [url, setUrl] = useState('');
  const [validation, setValidation] = useState<ValidationState>({
    isValid: false,
    error: '',
    success: ''
  });

  // LeetCode URL patterns
  const LEETCODE_PATTERNS = [
    /^https?:\/\/(www\.)?leetcode\.com\/problems\/[\w-]+\/?$/,
    /^https?:\/\/(www\.)?leetcode\.com\/problems\/[\w-]+\/description\/?$/,
    /^https?:\/\/(www\.)?leetcode\.com\/problems\/[\w-]+\/solutions?\/?$/,
  ];

  const validateUrl = (inputUrl: string): ValidationState => {
    if (!inputUrl.trim()) {
      return {
        isValid: false,
        error: '',
        success: ''
      };
    }

    const isValid = LEETCODE_PATTERNS.some(pattern => pattern.test(inputUrl));

    if (isValid) {
      return {
        isValid: true,
        error: '',
        success: 'Valid LeetCode problem URL'
      };
    }

    // Provide specific error messages based on common mistakes
    let errorMessage = 'Invalid LeetCode URL format';
    let suggestion = '';
    const examples = [
      'https://leetcode.com/problems/two-sum/',
      'https://leetcode.com/problems/reverse-linked-list/description/'
    ];

    if (!inputUrl.toLowerCase().includes('leetcode')) {
      errorMessage = 'URL must be from leetcode.com';
      suggestion = 'Please use a valid LeetCode problem URL';
    } else if (!inputUrl.startsWith('http')) {
      errorMessage = 'URL must start with http:// or https://';
      suggestion = 'Add the protocol to your URL';
    } else if (!inputUrl.includes('/problems/')) {
      errorMessage = 'URL must contain /problems/ path';
      suggestion = 'Make sure you\'re using a problem URL, not a profile or other page';
    } else {
      errorMessage = 'Invalid LeetCode problem URL format';
      suggestion = 'Expected format: https://leetcode.com/problems/problem-name/';
    }

    return {
      isValid: false,
      error: errorMessage,
      success: '',
      suggestion,
      examples
    };
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newUrl = e.target.value;
    setUrl(newUrl);
    
    const validationResult = validateUrl(newUrl);
    setValidation(validationResult);
    onUrlChange(newUrl, validationResult.isValid);
  };

  return (
    <div className="w-full">
      <label htmlFor="leetcode-url" className="block text-base font-semibold text-gray-800 mb-3">
        LeetCode Problem URL
      </label>
      <div className="relative">
        <input
          id="leetcode-url"
          type="url"
          value={url}
          onChange={handleChange}
          placeholder="https://leetcode.com/problems/two-sum/"
          aria-describedby={validation.error ? "url-error" : validation.success ? "url-success" : "url-help"}
          aria-invalid={url && !validation.isValid ? "true" : "false"}
          className={`w-full px-5 py-3.5 border-2 rounded-xl focus:outline-none focus:ring-4 transition-all duration-200 text-base ${
            url && validation.isValid
              ? 'border-green-400 focus:ring-green-100 bg-green-50/50'
              : url && validation.error
              ? 'border-red-400 focus:ring-red-100 bg-red-50/50'
              : 'border-gray-200 focus:ring-blue-100 bg-white hover:border-gray-300'
          }`}
        />
        {url && validation.isValid && (
          <div className="absolute right-4 top-1/2 -translate-y-1/2" aria-hidden="true">
            <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        )}
      </div>
      
      {/* Validation feedback */}
      {validation.error && (
        <div id="url-error" className="mt-3 p-4 bg-red-50 border border-red-200 rounded-xl" role="alert" aria-live="polite">
          <div className="flex items-start gap-3 mb-2">
            <div className="flex-shrink-0 w-6 h-6 bg-red-500 rounded-lg flex items-center justify-center" aria-hidden="true">
              <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="flex-1">
              <p className="text-sm font-semibold text-red-700">{validation.error}</p>
              {validation.suggestion && (
                <p className="text-sm text-red-600 mt-1">{validation.suggestion}</p>
              )}
              {validation.examples && validation.examples.length > 0 && (
                <div className="mt-2">
                  <p className="text-xs font-semibold text-red-700 mb-1">Valid examples:</p>
                  <ul className="text-xs text-red-600 space-y-1" role="list">
                    {validation.examples.map((example, idx) => (
                      <li key={idx} className="font-mono bg-red-100 px-2 py-1 rounded">
                        {example}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      
      {validation.success && (
        <div id="url-success" className="mt-3 flex items-start gap-3 p-4 bg-green-50 border border-green-200 rounded-xl" role="status" aria-live="polite">
          <div className="flex-shrink-0 w-6 h-6 bg-green-500 rounded-lg flex items-center justify-center" aria-hidden="true">
            <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          </div>
          <span className="text-sm text-green-700 font-medium leading-relaxed">{validation.success}</span>
        </div>
      )}

      {/* Help text */}
      {!url && (
        <p id="url-help" className="mt-3 text-sm text-gray-500">
          Enter a LeetCode problem URL (e.g., https://leetcode.com/problems/two-sum/)
        </p>
      )}
    </div>
  );
}
