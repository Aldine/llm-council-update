import React from 'react';

// Helper function to format date
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Helper function to group conversations by date
const groupByDate = (conversations) => {
  const groups = {
    today: [],
    yesterday: [],
    thisWeek: [],
    thisMonth: [],
    older: []
  };

  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  const weekAgo = new Date(today);
  weekAgo.setDate(weekAgo.getDate() - 7);
  const monthAgo = new Date(today);
  monthAgo.setMonth(monthAgo.getMonth() - 1);

  conversations.forEach(conv => {
    const date = new Date(conv.created_at);
    const convDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

    if (convDate.getTime() === today.getTime()) {
      groups.today.push(conv);
    } else if (convDate.getTime() === yesterday.getTime()) {
      groups.yesterday.push(conv);
    } else if (convDate >= weekAgo) {
      groups.thisWeek.push(conv);
    } else if (convDate >= monthAgo) {
      groups.thisMonth.push(conv);
    } else {
      groups.older.push(conv);
    }
  });

  return groups;
};

// Conversation Card Component
const ConversationCard = ({ conv, currentConversationId, onSelectConversation }) => (
  <button
    onClick={() => onSelectConversation(conv.id)}
    className={`w-full text-left p-4 border rounded-lg transition-all ${
      conv.id === currentConversationId
        ? 'bg-primary/10 border-primary shadow-md'
        : 'bg-card border-border hover:bg-accent/10 hover:border-accent/40'
    }`}
  >
    <div className="flex items-start justify-between gap-3">
      <div className="flex-1 min-w-0">
        <h3 className="font-medium text-sm mb-1 truncate">
          {conv.title || 'Untitled Session'}
        </h3>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span>{conv.message_count} messages</span>
          <span>•</span>
          <span>{formatDate(conv.created_at)}</span>
        </div>
      </div>
      <div className="flex items-center gap-2">
        {conv.id === currentConversationId && (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-primary/20 text-primary text-[10px] font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></span>
            Active
          </span>
        )}
      </div>
    </div>
  </button>
);

// Conversation Group Component
const ConversationGroup = ({ title, conversations, currentConversationId, onSelectConversation }) => {
  if (conversations.length === 0) return null;

  return (
    <div className="space-y-3">
      <h2 className="text-xs font-semibold tracking-tight text-muted-foreground uppercase px-1">
        {title}
      </h2>
      <div className="space-y-2">
        {conversations.map(conv => (
          <ConversationCard 
            key={conv.id} 
            conv={conv} 
            currentConversationId={currentConversationId}
            onSelectConversation={onSelectConversation}
          />
        ))}
      </div>
    </div>
  );
};

// Main History Component
export default function History({ conversations, onSelectConversation, currentConversationId }) {
  const grouped = groupByDate(conversations);

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">History</h1>
          <p className="text-muted-foreground">
            {conversations.length} conversation{conversations.length !== 1 ? 's' : ''} total
          </p>
        </div>
        
        {conversations.length > 0 && (
          <div className="flex gap-2">
            <button className="px-3 py-2 text-sm font-medium border border-border rounded-sm hover:bg-accent/50 transition-colors">
              Export All
            </button>
            <button className="px-3 py-2 text-sm font-medium text-destructive border border-destructive/50 rounded-sm hover:bg-destructive/10 transition-colors">
              Clear History
            </button>
          </div>
        )}
      </div>

      {conversations.length === 0 ? (
        <div className="text-center py-16 border border-dashed border-border rounded-lg">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
            <svg className="w-8 h-8 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold mb-2">No conversations yet</h3>
          <p className="text-muted-foreground mb-6">Start a new session to begin deliberating with the council</p>
        </div>
      ) : (
        <div className="space-y-8">
          <ConversationGroup 
            title="Today" 
            conversations={grouped.today}
            currentConversationId={currentConversationId}
            onSelectConversation={onSelectConversation}
          />
          <ConversationGroup 
            title="Yesterday" 
            conversations={grouped.yesterday}
            currentConversationId={currentConversationId}
            onSelectConversation={onSelectConversation}
          />
          <ConversationGroup 
            title="This Week" 
            conversations={grouped.thisWeek}
            currentConversationId={currentConversationId}
            onSelectConversation={onSelectConversation}
          />
          <ConversationGroup 
            title="This Month" 
            conversations={grouped.thisMonth}
            currentConversationId={currentConversationId}
            onSelectConversation={onSelectConversation}
          />
          <ConversationGroup 
            title="Older" 
            conversations={grouped.older}
            currentConversationId={currentConversationId}
            onSelectConversation={onSelectConversation}
          />
        </div>
      )}
    </div>
  );
}
