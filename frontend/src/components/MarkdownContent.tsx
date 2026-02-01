import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownContentProps {
  content: string;
}

export default function MarkdownContent({ content }: MarkdownContentProps) {
  return (
    <div className="markdown-content">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
        // Headings
        h1: ({ children }) => (
          <h1 className="text-2xl font-bold text-slate-900 mb-4 mt-6 first:mt-0 pb-2 border-b-2 border-slate-200">
            {children}
          </h1>
        ),
        h2: ({ children }) => (
          <h2 className="text-xl font-bold text-slate-800 mb-3 mt-5 first:mt-0 pb-1 border-b border-slate-200">
            {children}
          </h2>
        ),
        h3: ({ children }) => (
          <h3 className="text-lg font-semibold text-slate-800 mb-2 mt-4 first:mt-0">
            {children}
          </h3>
        ),
        h4: ({ children }) => (
          <h4 className="text-base font-semibold text-slate-700 mb-2 mt-3 first:mt-0">
            {children}
          </h4>
        ),
        
        // Paragraphs
        p: ({ children }) => (
          <p className="text-slate-700 leading-relaxed mb-4 last:mb-0">
            {children}
          </p>
        ),
        
        // Lists
        ul: ({ children }) => (
          <ul className="list-disc list-outside ml-6 mb-4 space-y-2 text-slate-700">
            {children}
          </ul>
        ),
        ol: ({ children }) => (
          <ol className="list-decimal list-outside ml-6 mb-4 space-y-2 text-slate-700">
            {children}
          </ol>
        ),
        li: ({ children }) => (
          <li className="leading-relaxed pl-1">
            {children}
          </li>
        ),
        
        // Emphasis
        strong: ({ children }) => (
          <strong className="font-bold text-slate-900">
            {children}
          </strong>
        ),
        em: ({ children }) => (
          <em className="italic text-slate-800">
            {children}
          </em>
        ),
        
        // Code
        code: ({ inline, children }) => {
          if (inline) {
            return (
              <code className="px-1.5 py-0.5 bg-slate-100 text-slate-800 rounded text-sm font-mono border border-slate-200">
                {children}
              </code>
            );
          }
          return (
            <code className="block p-4 bg-slate-800 text-slate-100 rounded-lg overflow-x-auto text-sm font-mono leading-relaxed my-4">
              {children}
            </code>
          );
        },
        pre: ({ children }) => (
          <pre className="my-4 overflow-x-auto">
            {children}
          </pre>
        ),
        
        // Blockquotes
        blockquote: ({ children }) => (
          <blockquote className="border-l-4 border-blue-400 pl-4 py-2 my-4 bg-blue-50 text-slate-700 italic">
            {children}
          </blockquote>
        ),
        
        // Links
        a: ({ href, children }) => (
          <a 
            href={href} 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 underline font-medium"
          >
            {children}
          </a>
        ),
        
        // Horizontal rule
        hr: () => (
          <hr className="my-6 border-t-2 border-slate-200" />
        ),
        
        // Tables
        table: ({ children }) => (
          <div className="overflow-x-auto my-4">
            <table className="min-w-full border-collapse border border-slate-300">
              {children}
            </table>
          </div>
        ),
        thead: ({ children }) => (
          <thead className="bg-slate-100">
            {children}
          </thead>
        ),
        tbody: ({ children }) => (
          <tbody className="bg-white">
            {children}
          </tbody>
        ),
        tr: ({ children }) => (
          <tr className="border-b border-slate-200">
            {children}
          </tr>
        ),
        th: ({ children }) => (
          <th className="px-4 py-2 text-left font-semibold text-slate-800 border border-slate-300">
            {children}
          </th>
        ),
        td: ({ children }) => (
          <td className="px-4 py-2 text-slate-700 border border-slate-300">
            {children}
          </td>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
    </div>
  );
}
