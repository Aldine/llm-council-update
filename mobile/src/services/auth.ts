import axios, { AxiosInstance, AxiosError } from 'axios';
import { Platform } from 'react-native';
import { API_CONFIG, getApiUrl } from '../constants/config';
import { secureTokenStore, StoredUser } from './secureStore';

interface LoginCredentials {
  email: string;
  password: string;
}

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: StoredUser;
}

/**
 * Authentication service with token management.
 * Handles login, logout, token refresh, and session restore.
 */
class AuthService {
  private client: AxiosInstance;

  constructor() {
    const baseURL = getApiUrl(Platform.OS as 'android' | 'ios' | 'web');
    
    this.client = axios.create({
      baseURL,
      timeout: API_CONFIG.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Login with email and password.
   * Stores tokens securely on success.
   */
  async login(credentials: LoginCredentials): Promise<StoredUser> {
    try {
      const response = await this.client.post<TokenResponse>(
        '/api/auth/login',
        credentials
      );

      const { access_token, refresh_token, user } = response.data;

      // Store tokens and user securely
      await secureTokenStore.saveTokens(access_token, refresh_token);
      await secureTokenStore.saveUser(user);

      console.log('[Auth] Login successful');
      return user;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<{ detail: string }>;
        throw new Error(axiosError.response?.data?.detail || 'Login failed');
      }
      throw new Error('Login failed');
    }
  }

  /**
   * Refresh access token using refresh token.
   */
  async refreshToken(): Promise<string> {
    try {
      const refreshToken = await secureTokenStore.getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token');
      }

      const response = await this.client.post<TokenResponse>(
        '/api/auth/refresh',
        { refresh_token: refreshToken }
      );

      const { access_token, refresh_token: new_refresh_token } = response.data;

      // Store new tokens
      await secureTokenStore.saveTokens(access_token, new_refresh_token);

      console.log('[Auth] Token refreshed');
      return access_token;
    } catch (error) {
      console.error('[Auth] Token refresh failed:', error);
      // Clear invalid tokens
      await this.logout();
      throw new Error('Session expired');
    }
  }

  /**
   * Logout and clear all stored tokens.
   */
  async logout(): Promise<void> {
    try {
      const accessToken = await secureTokenStore.getAccessToken();
      
      // Attempt to call logout endpoint (best effort)
      if (accessToken) {
        try {
          await this.client.post('/api/auth/logout', {}, {
            headers: { Authorization: `Bearer ${accessToken}` }
          });
        } catch (error) {
          // Ignore logout endpoint errors
          console.warn('[Auth] Logout endpoint failed (ignoring):', error);
        }
      }
    } finally {
      // Always clear local tokens
      await secureTokenStore.clearAll();
      console.log('[Auth] Logged out');
    }
  }

  /**
   * Check if user has valid session on app start.
   */
  async hasValidSession(): Promise<boolean> {
    return await secureTokenStore.hasValidSession();
  }

  /**
   * Get stored user without making network request.
   */
  async getStoredUser(): Promise<StoredUser | null> {
    return await secureTokenStore.getUser();
  }

  /**
   * Verify current session by calling /api/auth/me.
   */
  async verifySession(): Promise<StoredUser> {
    try {
      const accessToken = await secureTokenStore.getAccessToken();
      if (!accessToken) {
        throw new Error('No access token');
      }

      const response = await this.client.get<StoredUser>('/api/auth/me', {
        headers: { Authorization: `Bearer ${accessToken}` }
      });

      return response.data;
    } catch (error) {
      // Try refresh on 401
      if (axios.isAxiosError(error) && error.response?.status === 401) {
        await this.refreshToken();
        // Retry with new token
        return await this.verifySession();
      }
      throw error;
    }
  }
}

export const authService = new AuthService();
