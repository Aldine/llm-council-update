import axios, { AxiosInstance } from 'axios';
import { Platform } from 'react-native';
import { API_CONFIG, getApiUrl } from '../constants/config';
import type { Conversation, AskResponse } from '../types';
import { secureTokenStore } from './secureStore';

// Redact sensitive data from logs
const redactToken = (token: string | null): string => {
  if (!token) return 'null';
  if (token.length < 10) return '***';
  return `${token.slice(0, 4)}...${token.slice(-4)}`;
};

class ApiService {
  private client: AxiosInstance;
  private isRefreshing = false;
  private refreshSubscribers: Array<(token: string) => void> = [];

  constructor() {
    const baseURL = getApiUrl(Platform.OS as 'android' | 'ios' | 'web');
    
    this.client = axios.create({
      baseURL,
      timeout: API_CONFIG.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor - attach auth token
    this.client.interceptors.request.use(
      async (config) => {
        const token = await secureTokenStore.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        
        // Log without sensitive data
        if (__DEV__) {
          console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
          if (config.headers.Authorization) {
            console.log(`[API] Auth: Bearer ${redactToken(token)}`);
          }
        }
        
        return config;
      },
      (error) => {
        console.error('[API] Request error:', error.message);
        return Promise.reject(error);
      }
    );

    // Response interceptor - handle 401 with refresh
    this.client.interceptors.response.use(
      (response) => {
        if (__DEV__) {
          console.log(`[API] Response ${response.status} from ${response.config.url}`);
        }
        return response;
      },
      async (error) => {
        const originalRequest = error.config;

        // Handle 401 Unauthorized
        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            // Wait for refresh to complete
            return new Promise((resolve) => {
              this.refreshSubscribers.push((token: string) => {
                originalRequest.headers.Authorization = `Bearer ${token}`;
                resolve(this.client(originalRequest));
              });
            });
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            const refreshToken = await secureTokenStore.getRefreshToken();
            if (!refreshToken) {
              throw new Error('No refresh token');
            }

            // Call refresh endpoint
            const response = await axios.post(
              `${this.client.defaults.baseURL}/api/auth/refresh`,
              { refresh_token: refreshToken }
            );

            const { access_token, refresh_token: new_refresh } = response.data;
            await secureTokenStore.saveTokens(access_token, new_refresh);

            // Retry all queued requests
            this.refreshSubscribers.forEach((callback) => callback(access_token));
            this.refreshSubscribers = [];

            // Retry original request
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return this.client(originalRequest);
          } catch (refreshError) {
            // Refresh failed - clear tokens and force reauth
            await secureTokenStore.clearAll();
            return Promise.reject(refreshError);
          } finally {
            this.isRefreshing = false;
          }
        }

        // Log errors without sensitive data
        if (__DEV__) {
          console.error('[API] Response error:', error.message);
        } else {
          // Production: only log non-sensitive errors
          console.error('[API] Request failed');
        }
        
        return Promise.reject(error);
      }
    );
  }

  async getConversations(): Promise<Conversation[]> {
    const response = await this.client.get<Conversation[]>('/api/conversations');
    return response.data;
  }

  async getConversation(id: string): Promise<Conversation> {
    const response = await this.client.get<Conversation>(`/api/conversations/${id}`);
    return response.data;
  }

  async createConversation(): Promise<Conversation> {
    const response = await this.client.post<Conversation>('/api/conversations');
    return response.data;
  }

  async askQuestion(question: string, conversationId?: string): Promise<AskResponse> {
    const response = await this.client.post<AskResponse>('/api/ask', {
      question,
      conversation_id: conversationId,
    });
    return response.data;
  }

  // Health check endpoint
  async checkConnection(): Promise<boolean> {
    try {
      await this.client.get('/api/conversations');
      return true;
    } catch {
      return false;
    }
  }
}

export const apiService = new ApiService();
