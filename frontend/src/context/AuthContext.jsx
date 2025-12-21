import { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../auth';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [state, setState] = useState('INITIALIZING'); // INITIALIZING, UNAUTHENTICATED, AUTHENTICATING, AUTHENTICATED, ERROR
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);

  // Initialize auth state on mount
  useEffect(() => {
    const initAuth = async () => {
      if (authService.hasValidSession()) {
        try {
          const user = await authService.verifySession();
          setUser(user);
          setState('AUTHENTICATED');
        } catch (error) {
          console.error('Session verification failed:', error);
          setState('UNAUTHENTICATED');
        }
      } else {
        setState('UNAUTHENTICATED');
      }
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    setState('AUTHENTICATING');
    setError(null);

    try {
      const user = await authService.login(email, password);
      setUser(user);
      setState('AUTHENTICATED');
    } catch (error) {
      setError(error.message);
      setState('ERROR');
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setUser(null);
      setState('UNAUTHENTICATED');
    }
  };

  const clearError = () => {
    setError(null);
    if (state === 'ERROR') {
      setState('UNAUTHENTICATED');
    }
  };

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
