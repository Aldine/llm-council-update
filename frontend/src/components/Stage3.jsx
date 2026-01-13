import ReactMarkdown from 'react-markdown';

export default function Stage3({ finalResponse }) {
  if (!finalResponse) {
    return null;
  }

  return (
    <div className="border border-accent/30 rounded-sm bg-card overflow-hidden shadow-[0_0_15px_-3px_rgba(var(--accent),0.1)]">
      <div className="px-4 py-3 border-b border-accent/20 bg-accent/5 flex items-center justify-between">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-accent">
          Stage 3: Final Council Answer
        </h3>
        <span className="text-[10px] bg-accent text-accent-foreground px-2 py-0.5 rounded-sm font-bold">
          VERDICT
        </span>
      </div>

      <div className="p-6 bg-card">
        <div className="mb-4 flex items-center gap-2">
          <span className="text-xs text-muted-foreground">Synthesized by Chairman:</span>
          <code className="text-xs bg-accent/10 text-accent px-1.5 py-0.5 rounded-sm font-mono font-medium">
            {finalResponse.model.split('/')[1] || finalResponse.model}
          </code>
        </div>
        <div className="markdown-content text-sm text-foreground leading-relaxed">
          <ReactMarkdown>{finalResponse.response}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
