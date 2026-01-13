import { describe, it, expect, vi, beforeEach } from 'vitest';
import { api } from '../api';

// Mock fetch globally
globalThis.fetch = vi.fn();

describe('API Client', () => {
  beforeEach(() => {
    fetch.mockClear();
    localStorage.clear();
  });

  describe('listConversations', () => {
    it('should fetch conversations list', async () => {
      const mockConversations = [
        { id: '1', title: 'Test 1', created_at: '2025-01-01', message_count: 5 },
        { id: '2', title: 'Test 2', created_at: '2025-01-02', message_count: 3 },
      ];

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockConversations,
      });

      const result = await api.listConversations();

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8002/api/conversations',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
      expect(result).toEqual(mockConversations);
    });

    it('should throw error on failed request', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
      });

      await expect(api.listConversations()).rejects.toThrow('Failed to list conversations');
    });
  });

  describe('createConversation', () => {
    it('should create new conversation', async () => {
      const mockConversation = {
        id: 'new-id',
        title: 'New Conversation',
        created_at: '2025-01-01',
        messages: [],
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockConversation,
      });

      const result = await api.createConversation();

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8002/api/conversations',
        expect.objectContaining({
          method: 'POST',
        })
      );
      expect(result).toEqual(mockConversation);
    });
  });

  describe('deleteConversation', () => {
    it('should delete conversation', async () => {
      const conversationId = 'test-id';
      const mockResponse = { message: 'Conversation deleted successfully', id: conversationId };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await api.deleteConversation(conversationId);

      expect(fetch).toHaveBeenCalledWith(
        `http://localhost:8002/api/conversations/${conversationId}`,
        expect.objectContaining({
          method: 'DELETE',
        })
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('sendMessage', () => {
    it('should use standard endpoint when CrewAI is disabled', async () => {
      localStorage.getItem.mockReturnValue('false');
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      });

      await api.sendMessage('conv-id', 'Hello');

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8002/api/conversations/conv-id/message',
        expect.any(Object)
      );
    });

    it('should use CrewAI endpoint when enabled', async () => {
      localStorage.getItem.mockReturnValue('true');
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      });

      await api.sendMessage('conv-id', 'Hello');

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8002/api/conversations/conv-id/message/crew',
        expect.any(Object)
      );
    });
  });
});
