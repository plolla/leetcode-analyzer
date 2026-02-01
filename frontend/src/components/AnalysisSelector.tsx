import { useState } from 'react';

export type AnalysisType = 'complexity' | 'hints' | 'optimization' | 'debugging';

interface AnalysisSelectorProps {
  onAnalysisSelect: (type: AnalysisType) => void;
  disabled?: boolean;
}

interface AnalysisOption {
  type: AnalysisType;
  title: string;
  description: string;
  icon: string;
}

const ANALYSIS_OPTIONS: AnalysisOption[] = [
  {
    type: 'complexity',
    title: 'Time Complexity',
    description: 'Analyze Big O time and space complexity',
    icon: '⏱️'
  },
  {
    type: 'hints',
    title: 'Get Hints',
    description: 'Receive progressive hints without spoilers',
    icon: '💡'
  },
  {
    type: 'optimization',
    title: 'Optimize Solution',
    description: 'Find ways to improve your working code',
    icon: '🚀'
  },
  {
    type: 'debugging',
    title: 'Debug Code',
    description: 'Identify and fix bugs in your solution',
    icon: '🐛'
  }
];

export default function AnalysisSelector({ onAnalysisSelect, disabled = false }: AnalysisSelectorProps) {
  const [selectedType, setSelectedType] = useState<AnalysisType | null>(null);

  const handleSelect = (type: AnalysisType) => {
    if (disabled) return;
    setSelectedType(type);
    onAnalysisSelect(type);
  };

  const handleKeyDown = (e: React.KeyboardEvent, type: AnalysisType) => {
    if (disabled) return;
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleSelect(type);
    }
  };

  return (
    <div className="w-full">
      <div 
        className="grid grid-cols-1 md:grid-cols-2 gap-4"
        role="radiogroup"
        aria-label="Analysis type selection"
        aria-describedby={disabled ? "analysis-disabled-message" : undefined}
      >
        {ANALYSIS_OPTIONS.map((option) => (
          <button
            key={option.type}
            onClick={() => handleSelect(option.type)}
            onKeyDown={(e) => handleKeyDown(e, option.type)}
            disabled={disabled}
            role="radio"
            aria-checked={selectedType === option.type}
            aria-label={`${option.title}: ${option.description}`}
            tabIndex={disabled ? -1 : 0}
            className={`
              group relative p-6 rounded-xl text-left transition-all duration-200
              ${disabled 
                ? 'bg-gray-50 border-2 border-gray-200 cursor-not-allowed opacity-60' 
                : 'hover:border-blue-500 hover:bg-gradient-to-br hover:from-blue-50 hover:to-indigo-50 hover:shadow-xl cursor-pointer transform hover:-translate-y-1 hover:scale-[1.02] focus:outline-none focus:ring-4 focus:ring-blue-100'
              }
              ${selectedType === option.type && !disabled
                ? 'border-2 border-blue-600 bg-gradient-to-br from-blue-100 to-indigo-100 shadow-xl ring-4 ring-blue-100'
                : 'border-2 border-gray-200 bg-white'
              }
            `}
          >
            <div className="flex items-start gap-4">
              <div className={`
                flex items-center justify-center w-12 h-12 rounded-xl text-2xl transition-transform
                ${selectedType === option.type && !disabled ? 'scale-110' : 'group-hover:scale-110'}
                ${disabled ? 'bg-gray-100' : 'bg-gradient-to-br from-blue-100 to-indigo-100'}
              `} aria-hidden="true">
                {option.icon}
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-bold text-gray-900 mb-1.5">
                  {option.title}
                </h3>
                <p className="text-sm text-gray-600 leading-relaxed">
                  {option.description}
                </p>
              </div>

            </div>
          </button>
        ))}
      </div>

      {/* Guidance message when disabled */}
      {disabled && (
        <div id="analysis-disabled-message" className="mt-5 p-5 bg-amber-50 border-l-4 border-amber-400 rounded-lg" role="alert">
          <div>
            <p className="text-sm font-semibold text-amber-900 mb-1">
              Complete the required inputs first
            </p>
            <p className="text-sm text-amber-800">
              Please provide both a valid LeetCode problem URL and your solution code to enable analysis options.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
