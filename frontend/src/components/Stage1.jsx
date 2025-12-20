import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

export default function Stage1({ responses }) {
  const [activeTab, setActiveTab] = useState(0);

  if (!responses || responses.length === 0) {
    return null;
  }

  return (
    <div className="border border-border rounded-sm bg-card overflow-hidden">
      <div className="px-4 py-3 border-b border-border bg-muted/30 flex items-center justify-between">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Stage 1: Individual Responses
        </h3>
        <span className="text-[10px] bg-accent/10 text-accent px-2 py-0.5 rounded-sm font-medium">
          {responses.length} Models
        </span>
      </div>

      <div className="flex overflow-x-auto border-b border-border scrollbar-hide">
        {responses.map((resp, index) => (
          <button
            key={index}
            className={`px-4 py-2 text-xs font-medium whitespace-nowrap transition-colors border-b-2 ${
              activeTab === index
                ? 'border-accent text-foreground bg-accent/5'
                : 'border-transparent text-muted-foreground hover:text-foreground hover:bg-muted/50'
            }`}
            onClick={() => setActiveTab(index)}
          >
            {resp.model.split('/')[1] || resp.model}
          </button>
        ))}
      </div>

      <div className="p-4 bg-card">
        <div className="mb-3 flex items-center gap-2">
          <span className="text-xs text-muted-foreground">Model:</span>
          <code className="text-xs bg-muted px-1.5 py-0.5 rounded-sm font-mono text-foreground">
            {responses[activeTab].model}
          </code>
        </div>
        <div className="markdown-content text-sm text-muted-foreground leading-relaxed">
          <ReactMarkdown>{responses[activeTab].response}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
