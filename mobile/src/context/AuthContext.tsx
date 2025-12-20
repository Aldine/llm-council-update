import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';
import { authService } from '../services/auth';
import type { StoredUser } from '../services/secureStore';

type AuthState = 
  | 'INITIALIZING'    // Checking for existing session
  | 'UNAUTHENTICATED' // No session, show login
  | 'AUTHENTICATING'  // Login in progress
  | 'AUTHENTICATED'   // Valid session, show app
  | 'ERROR';          // Auth error, show retry

interface AuthContextType {
  state: AuthState;
  user: StoredUser | null;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [state, setState] = useState<AuthState>('INITIALIZING');
  const [user, setUser] = useState<StoredUser | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Initialize: check for existing session
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      setState('INITIALIZING');
      
      const hasSession = await authService.hasValidSession();
      if (!hasSession) {
        setState('UNAUTHENTICATED');
        return;
      }

      // Try to get stored user
      const storedUser = await authService.getStoredUser();
      if (storedUser) {
        setUser(storedUser);
        setState('AUTHENTICATED');
        
        // Verify session in background
        try {
          const verifiedUser = await authService.verifySession();
          setUser(verifiedUser);
        } catch (verifyError) {
          console.warn('[Auth] Session verification failed, clearing session');
          setState('UNAUTHENTICATED');
          setUser(null);
        }
      } else {
        setState('UNAUTHENTICATED');
      }
    } catch (err: any) {
      console.error('[Auth] Initialize error:', err);
      setState('UNAUTHENTICATED');
    }
  };

  const login = useCallback(async (email: string, password: string) => {
    try {
      setState('AUTHENTICATING');
      setError(null);

      const loggedInUser = await authService.login({ email, password });
      
      setUser(loggedInUser);
      setState('AUTHENTICATED');
    } catch (err: any) {
      console.error('[Auth] Login error:', err);
      setError(err.message || 'Login failed');
      setState('ERROR');
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await authService.logout();
      setUser(null);
      setState('UNAUTHENTICATED');
      setError(null);
    } catch (err: any) {
      console.error('[Auth] Logout error:', err);
      // Still clear state even if logout endpoint fails
      setUser(null);
      setState('UNAUTHENTICATED');
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
    if (state === 'ERROR') {
      setState('UNAUTHENTICATED');
    }
  }, [state]);

  return (
    <AuthContext.Provider
      value={{
        state,
        user,
        error,
        login,
        logout,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
