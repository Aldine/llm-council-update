import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

function deAnonymizeText(text, labelToModel) {
  if (!labelToModel) return text;

  let result = text;
  // Replace each "Response X" with the actual model name
  Object.entries(labelToModel).forEach(([label, model]) => {
    const modelShortName = model.split('/')[1] || model;
    result = result.replace(new RegExp(label, 'g'), `**${modelShortName}**`);
  });
  return result;
}

export default function Stage2({ rankings, labelToModel, aggregateRankings }) {
  const [activeTab, setActiveTab] = useState(0);

  if (!rankings || rankings.length === 0) {
    return null;
  }

  return (
    <div className="border border-border rounded-sm bg-card overflow-hidden">
      <div className="px-4 py-3 border-b border-border bg-muted/30 flex items-center justify-between">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Stage 2: Peer Rankings
        </h3>
        <span className="text-[10px] bg-accent/10 text-accent px-2 py-0.5 rounded-sm font-medium">
          Consensus Building
        </span>
      </div>

      <div className="p-4 border-b border-border bg-card/50">
        <p className="text-xs text-muted-foreground leading-relaxed">
          Each model evaluated all responses (anonymized as Response A, B, C, etc.) and provided rankings.
          Below, model names are shown in <strong className="text-foreground font-medium">bold</strong> for readability, but the original evaluation used anonymous labels.
        </p>
      </div>

      <div className="flex overflow-x-auto border-b border-border scrollbar-hide">
        {rankings.map((rank, index) => (
          <button
            key={index}
            className={`px-4 py-2 text-xs font-medium whitespace-nowrap transition-colors border-b-2 ${
              activeTab === index
                ? 'border-accent text-foreground bg-accent/5'
                : 'border-transparent text-muted-foreground hover:text-foreground hover:bg-muted/50'
            }`}
            onClick={() => setActiveTab(index)}
          >
            {rank.model.split('/')[1] || rank.model}
          </button>
        ))}
      </div>

      <div className="p-4 bg-card">
        <div className="mb-3 flex items-center gap-2">
          <span className="text-xs text-muted-foreground">Evaluator:</span>
          <code className="text-xs bg-muted px-1.5 py-0.5 rounded-sm font-mono text-foreground">
            {rankings[activeTab].model}
          </code>
        </div>
        <div className="markdown-content text-sm text-muted-foreground leading-relaxed">
          <ReactMarkdown>
            {deAnonymizeText(rankings[activeTab].ranking, labelToModel)}
          </ReactMarkdown>
        </div>

        {rankings[activeTab].parsed_ranking &&
         rankings[activeTab].parsed_ranking.length > 0 && (
          <div className="mt-4 p-3 bg-muted/30 rounded-sm border border-border">
            <strong className="text-xs font-medium text-foreground block mb-2">Extracted Ranking:</strong>
            <ol className="list-decimal list-inside text-xs text-muted-foreground space-y-1">
              {rankings[activeTab].parsed_ranking.map((label, i) => (
                <li key={i}>
                  {labelToModel && labelToModel[label]
                    ? labelToModel[label].split('/')[1] || labelToModel[label]
                    : label}
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>

      {aggregateRankings && aggregateRankings.length > 0 && (
        <div className="border-t border-border p-4 bg-muted/10">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
            Aggregate Rankings (Street Cred)
          </h4>
          <div className="space-y-2">
            {aggregateRankings.map((agg, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-card border border-border rounded-sm">
                <div className="flex items-center gap-3">
                  <span className={`w-5 h-5 flex items-center justify-center rounded-full text-[10px] font-bold ${
                    index === 0 ? 'bg-accent text-accent-foreground' : 'bg-muted text-muted-foreground'
                  }`}>
                    #{index + 1}
                  </span>
                  <span className="text-sm font-medium text-foreground">
                    {agg.model.split('/')[1] || agg.model}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <span>Avg: {agg.average_rank.toFixed(2)}</span>
                  <span>({agg.rankings_count} votes)</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
