import axios, { AxiosInstance } from 'axios';
import { Platform } from 'react-native';
import { API_CONFIG, getApiUrl } from '../constants/config';
import type { Conversation, AskResponse } from '../types';

class ApiService {
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

    // Request interceptor for debugging
    this.client.interceptors.request.use(
      (config) => {
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('[API] Request error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => {
        console.log(`[API] Response ${response.status} from ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error('[API] Response error:', error.message);
        if (error.response) {
          console.error('[API] Error data:', error.response.data);
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
