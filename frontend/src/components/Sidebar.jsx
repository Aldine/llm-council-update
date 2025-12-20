import React from 'react';

export default function Sidebar({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  isOpen,
  onClose
}) {
  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-background/80 backdrop-blur-sm z-30 md:hidden"
          onClick={onClose}
        />
      )}
      
      <aside className={`
        w-80 border-r border-border bg-card/50 flex flex-col 
        h-[calc(100vh-3.5rem)] 
        fixed md:sticky top-14 left-0 z-40
        transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        <div className="p-4 border-b border-border">
          <button 
            onClick={onNewConversation}
            className="w-full bg-primary text-primary-foreground hover:bg-primary/90 h-9 px-4 py-2 inline-flex items-center justify-center whitespace-nowrap rounded-sm text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
          >
            <span className="mr-2">+</span> New Session
          </button>
        </div>

        <div className="flex-1 overflow-y-auto py-2">
          <div className="px-4 pb-4">
            <div className="flex items-center gap-2 text-xs text-muted-foreground bg-secondary/50 px-3 py-1.5 rounded-sm border border-border justify-center">
              <span className="w-2 h-2 rounded-full bg-accent animate-pulse"></span>
              System Operational
            </div>
          </div>

          <div className="px-4 py-2">
            <h2 className="mb-2 px-2 text-xs font-semibold tracking-tight text-primary uppercase">
              Recent Sessions
            </h2>
            <div className="space-y-1">
              {conversations.length === 0 ? (
                <div className="px-2 py-4 text-sm text-muted-foreground text-center italic">
                  No history available
                </div>
              ) : (
                conversations.map((conv) => (
                  <button
                    key={conv.id}
                    onClick={() => onSelectConversation(conv.id)}
                    className={`group w-full text-left px-3 py-2 text-sm transition-colors rounded-sm flex flex-col gap-0.5 border ${
                      conv.id === currentConversationId 
                        ? 'bg-primary/15 border-primary/50 text-foreground font-medium shadow-[inset_0_0_0_1px_hsl(var(--primary))]' 
                        : 'bg-card/60 border-border text-muted-foreground hover:bg-accent/10 hover:border-accent/40 hover:text-foreground'
                    }`}
                  >
                    <span className="truncate block w-full">
                      {conv.title || 'Untitled Session'}
                    </span>
                    <span className={`text-[10px] ${
                      conv.id === currentConversationId ? 'text-foreground/80' : 'text-muted-foreground/70 group-hover:text-foreground/70'
                    }`}>
                      {conv.message_count} messages
                    </span>
                  </button>
                ))
              )}
            </div>
          </div>
        </div>
        
        <div className="p-4 border-t border-border mt-auto">
          <nav className="flex flex-col gap-1 mb-4">
            <a href="#" className="flex items-center gap-2 px-2 py-1.5 text-sm font-medium text-foreground bg-accent/10 rounded-sm transition-colors">
              <span>Deliberation</span>
            </a>
            <a href="#" className="flex items-center gap-2 px-2 py-1.5 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted/50 rounded-sm transition-colors">
              <span>History</span>
            </a>
            <a href="#" className="flex items-center gap-2 px-2 py-1.5 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted/50 rounded-sm transition-colors">
              <span>Settings</span>
            </a>
          </nav>

          <div className="flex items-center gap-3 px-2 pt-4 border-t border-border">
            <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-xs font-medium">
              US
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-medium">User</span>
              <span className="text-xs text-muted-foreground">Pro Plan</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}

