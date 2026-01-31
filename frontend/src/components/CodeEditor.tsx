import { useState } from 'react';
import Editor from '@monaco-editor/react';

interface CodeEditorProps {
  onCodeChange: (code: string, language: string) => void;
}

const SUPPORTED_LANGUAGES = [
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'java', label: 'Java' },
];

export default function CodeEditor({ onCodeChange }: CodeEditorProps) {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');

  const handleEditorChange = (value: string | undefined) => {
    const newCode = value || '';
    setCode(newCode);
    onCodeChange(newCode, language);
  };

  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newLanguage = e.target.value;
    setLanguage(newLanguage);
    onCodeChange(code, newLanguage);
  };

  return (
    <div className="w-full">
      {/* Language Selector */}
      <div className="flex items-center justify-between mb-3">
        <label htmlFor="language-select" className="block text-base font-semibold text-gray-800">
          Programming Language
        </label>
        <select
          id="language-select"
          value={language}
          onChange={handleLanguageChange}
          aria-label="Select programming language"
          className="px-4 py-2 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-4 focus:ring-blue-100 focus:border-blue-400 text-sm font-medium bg-white hover:border-gray-300 transition-all cursor-pointer"
        >
          {SUPPORTED_LANGUAGES.map((lang) => (
            <option key={lang.value} value={lang.value}>
              {lang.label}
            </option>
          ))}
        </select>
      </div>

      {/* Monaco Editor */}
      <div 
        className="border-2 border-gray-200 rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow"
        role="region"
        aria-label="Code editor"
      >
        <Editor
          height="400px"
          language={language}
          value={code}
          onChange={handleEditorChange}
          theme="vs-light"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4,
            wordWrap: 'on',
            padding: { top: 16, bottom: 16 },
            ariaLabel: 'Code editor for your solution',
          }}
        />
      </div>

      {/* Code Stats */}
      <div className="mt-3 flex items-center gap-8 text-sm" role="status" aria-live="polite" aria-atomic="true">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-blue-500 rounded-full" aria-hidden="true"></div>
          <span className="text-gray-600 font-medium">Lines: <span className="text-gray-900">{code.split('\n').length}</span></span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-indigo-500 rounded-full" aria-hidden="true"></div>
          <span className="text-gray-600 font-medium">Characters: <span className="text-gray-900">{code.length}</span></span>
        </div>
        {!code && (
          <span className="text-gray-400 ml-auto flex items-center gap-2">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path fillRule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
            Paste your solution code here
          </span>
        )}
      </div>
    </div>
  );
}
