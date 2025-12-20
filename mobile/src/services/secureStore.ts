import * as SecureStore from 'expo-secure-store';

const TOKEN_KEY = 'auth_access_token';
const REFRESH_TOKEN_KEY = 'auth_refresh_token';
const USER_KEY = 'auth_user';

export interface StoredUser {
  id: string;
  email: string;
  name: string;
}

export interface Tokens {
  accessToken: string;
  refreshToken: string;
}

/**
 * Secure token storage using Expo SecureStore.
 * Encrypted on device, cleared on logout.
 */
class SecureTokenStore {
  async saveTokens(accessToken: string, refreshToken: string): Promise<void> {
    try {
      await SecureStore.setItemAsync(TOKEN_KEY, accessToken);
      await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, refreshToken);
    } catch (error) {
      console.error('[SecureStore] Failed to save tokens:', error);
      throw new Error('Failed to save authentication tokens');
    }
  }

  async getAccessToken(): Promise<string | null> {
    try {
      return await SecureStore.getItemAsync(TOKEN_KEY);
    } catch (error) {
      console.error('[SecureStore] Failed to get access token:', error);
      return null;
    }
  }

  async getRefreshToken(): Promise<string | null> {
    try {
      return await SecureStore.getItemAsync(REFRESH_TOKEN_KEY);
    } catch (error) {
      console.error('[SecureStore] Failed to get refresh token:', error);
      return null;
    }
  }

  async getTokens(): Promise<Tokens | null> {
    try {
      const accessToken = await this.getAccessToken();
      const refreshToken = await this.getRefreshToken();
      
      if (!accessToken || !refreshToken) {
        return null;
      }
      
      return { accessToken, refreshToken };
    } catch (error) {
      console.error('[SecureStore] Failed to get tokens:', error);
      return null;
    }
  }

  async saveUser(user: StoredUser): Promise<void> {
    try {
      await SecureStore.setItemAsync(USER_KEY, JSON.stringify(user));
    } catch (error) {
      console.error('[SecureStore] Failed to save user:', error);
      throw new Error('Failed to save user data');
    }
  }

  async getUser(): Promise<StoredUser | null> {
    try {
      const userJson = await SecureStore.getItemAsync(USER_KEY);
      if (!userJson) {
        return null;
      }
      return JSON.parse(userJson);
    } catch (error) {
      console.error('[SecureStore] Failed to get user:', error);
      return null;
    }
  }

  async clearAll(): Promise<void> {
    try {
      await SecureStore.deleteItemAsync(TOKEN_KEY);
      await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
      await SecureStore.deleteItemAsync(USER_KEY);
    } catch (error) {
      console.error('[SecureStore] Failed to clear tokens:', error);
      throw new Error('Failed to clear authentication data');
    }
  }

  async hasValidSession(): Promise<boolean> {
    const tokens = await this.getTokens();
    return tokens !== null;
  }
}

export const secureTokenStore = new SecureTokenStore();
