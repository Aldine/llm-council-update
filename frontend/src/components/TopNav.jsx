import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import ConfirmModal from './ConfirmModal';

export default function TopNav({ onToggleSidebar }) {
  const { state, user, logout } = useAuth();
  const [isLogoutConfirmOpen, setIsLogoutConfirmOpen] = useState(false);

  const handleLogout = () => {
    setIsLogoutConfirmOpen(true);
  };

  return (
    <header className="h-14 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 flex items-center px-4 md:px-6 sticky top-0 z-50">
      <button 
        onClick={onToggleSidebar}
        className="md:hidden mr-4 p-2 ml-60 text-muted-foreground hover:text-foreground"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="3" y1="12" x2="21" y2="12"></line>
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
      </button>
      <div className="flex items-center gap-2 mr-auto md:mr-40">
        <div className="w-3 h-3 bg-accent rounded-full animate-pulse" />
        <span className="font-semibold tracking-tight text-lg">LLM Council</span>
      </div>
      
      {state === 'AUTHENTICATED' && user && (
        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground hidden md:inline">
            {user.email}
          </span>
          <button
            onClick={handleLogout}
            className="px-3 py-1.5 text-sm rounded-md border border-border hover:bg-accent hover:text-accent-foreground transition-colors"
          >
            Logout
          </button>
        </div>
      )}

      <ConfirmModal
        isOpen={isLogoutConfirmOpen}
        onClose={() => setIsLogoutConfirmOpen(false)}
        onConfirm={logout}
        title="Logout"
        message="Are you sure you want to logout?"
        confirmText="Logout"
        cancelText="Cancel"
        variant="warning"
      />
    </header>
  );
}
