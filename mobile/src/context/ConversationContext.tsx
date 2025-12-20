import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { apiService } from '../services/api';
import type { Conversation, Message } from '../types';

interface ConversationContextType {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  isLoading: boolean;
  error: string | null;
  loadConversations: () => Promise<void>;
  loadConversation: (id: string) => Promise<void>;
  createNewConversation: () => Promise<void>;
  sendMessage: (question: string) => Promise<void>;
  clearError: () => void;
}

const ConversationContext = createContext<ConversationContextType | undefined>(undefined);

export const ConversationProvider = ({ children }: { children: ReactNode }) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadConversations = useCallback(async () => {
    try {
      setError(null);
      const data = await apiService.getConversations();
      setConversations(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load conversations');
      console.error('Load conversations error:', err);
    }
  }, []);

  const loadConversation = useCallback(async (id: string) => {
    try {
      setError(null);
      setIsLoading(true);
      const data = await apiService.getConversation(id);
      setCurrentConversation(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load conversation');
      console.error('Load conversation error:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createNewConversation = useCallback(async () => {
    try {
      setError(null);
      const newConv = await apiService.createConversation();
      setCurrentConversation(newConv);
      setConversations(prev => [newConv, ...prev]);
    } catch (err: any) {
      setError(err.message || 'Failed to create conversation');
      console.error('Create conversation error:', err);
    }
  }, []);

  const sendMessage = useCallback(async (question: string) => {
    try {
      setError(null);
      setIsLoading(true);

      // Add user message immediately
      const userMessage: Message = {
        role: 'user',
        content: question,
      };

      setCurrentConversation(prev => {
        if (!prev) return null;
        return {
          ...prev,
          messages: [...prev.messages, userMessage],
        };
      });

      // Call API
      const response = await apiService.askQuestion(
        question,
        currentConversation?.id
      );

      // Add assistant message with stages
      const assistantMessage: Message = {
        role: 'assistant',
        stage1: response.stage1,
        stage2: response.stage2,
        stage3: response.stage3,
        metadata: response.metadata,
      };

      setCurrentConversation(prev => {
        if (!prev) {
          // Create new conversation with both messages
          return {
            id: response.conversation_id,
            title: question.slice(0, 50),
            created_at: new Date().toISOString(),
            messages: [userMessage, assistantMessage],
          };
        }
        return {
          ...prev,
          id: response.conversation_id,
          messages: [...prev.messages, assistantMessage],
        };
      });

      // Refresh conversation list
      await loadConversations();
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
      console.error('Send message error:', err);
    } finally {
      setIsLoading(false);
    }
  }, [currentConversation, loadConversations]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return (
    <ConversationContext.Provider
      value={{
        conversations,
        currentConversation,
        isLoading,
        error,
        loadConversations,
        loadConversation,
        createNewConversation,
        sendMessage,
        clearError,
      }}
    >
      {children}
    </ConversationContext.Provider>
  );
};

export const useConversation = () => {
  const context = useContext(ConversationContext);
  if (!context) {
    throw new Error('useConversation must be used within ConversationProvider');
  }
  return context;
};
