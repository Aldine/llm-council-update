import React, { useState } from 'react';

export default function Sidebar({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  isOpen,
  onClose,
  currentView = 'deliberation',
  onViewChange,
  user,
  onLogout
}) {
  const [showUserMenu, setShowUserMenu] = useState(false);
  
  // Get user initials for avatar
  const getUserInitials = () => {
    if (!user) return 'US';
    if (user.name) {
      const names = user.name.split(' ');
      return names.length > 1 
        ? `${names[0][0]}${names[1][0]}`.toUpperCase()
        : names[0].substring(0, 2).toUpperCase();
    }
    return user.email ? user.email.substring(0, 2).toUpperCase() : 'US';
  };
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
            <button 
              onClick={() => onViewChange('deliberation')}
              className={`flex items-center gap-2 px-2 py-1.5 text-sm font-medium rounded-sm transition-colors ${
                currentView === 'deliberation'
                  ? 'text-foreground bg-accent/10'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              <span>Deliberation</span>
            </button>
            <button 
              onClick={() => onViewChange('history')}
              className={`flex items-center gap-2 px-2 py-1.5 text-sm font-medium rounded-sm transition-colors ${
                currentView === 'history'
                  ? 'text-foreground bg-accent/10'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>History</span>
            </button>
            <button 
              onClick={() => onViewChange('settings')}
              className={`flex items-center gap-2 px-2 py-1.5 text-sm font-medium rounded-sm transition-colors ${
                currentView === 'settings'
                  ? 'text-foreground bg-accent/10'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span>Settings</span>
            </button>
          </nav>

          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="w-full flex items-center gap-3 px-2 pt-4 border-t border-border hover:bg-accent/50 rounded-sm transition-colors"
            >
              <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-xs font-semibold text-primary border border-primary/30">
                {getUserInitials()}
              </div>
              <div className="flex-1 flex flex-col items-start min-w-0">
                <span className="text-sm font-medium truncate w-full">{user?.name || 'User'}</span>
                <span className="text-xs text-muted-foreground">Pro Plan</span>
              </div>
              <svg className={`w-4 h-4 text-muted-foreground transition-transform ${showUserMenu ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {/* User Menu Dropdown */}
            {showUserMenu && (
              <div className="absolute bottom-full left-2 right-2 mb-2 bg-card border border-border rounded-lg shadow-lg overflow-hidden">
                <div className="p-3 border-b border-border bg-accent/5">
                  <div className="font-medium text-sm">{user?.name || 'User'}</div>
                  <div className="text-xs text-muted-foreground truncate">{user?.email || 'demo@llmcouncil.com'}</div>
                </div>
                <div className="p-1">
                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      onViewChange('settings');
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent/50 rounded-sm transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Account Settings
                  </button>
                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      onViewChange('history');
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent/50 rounded-sm transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    View History
                  </button>
                  <div className="my-1 border-t border-border"></div>
                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      onLogout();
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-sm text-destructive hover:bg-destructive/10 rounded-sm transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    Logout
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </aside>
    </>
  );
}

