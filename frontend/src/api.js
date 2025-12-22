/**
 * API client for the LLM Council backend.
 */

const API_BASE = 'http://localhost:8002';

// Helper to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_access_token');
  const headers = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
};

export const api = {
  /**
   * List all conversations.
   */
  async listConversations() {
    const response = await fetch(`${API_BASE}/api/conversations`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to list conversations');
    }
    return response.json();
  },

  /**
   * Create a new conversation.
   */
  async createConversation() {
    const response = await fetch(`${API_BASE}/api/conversations`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({}),
    });
    if (!response.ok) {
      throw new Error('Failed to create conversation');
    }
    return response.json();
  },

  /**
   * Get a specific conversation.
   */
  async getConversation(conversationId) {
    const response = await fetch(
      `${API_BASE}/api/conversations/${conversationId}`,
      {
        headers: getAuthHeaders(),
      }
    );
    if (!response.ok) {
      throw new Error('Failed to get conversation');
    }
    return response.json();
  },

  /**
   * Delete a conversation.
   */
  async deleteConversation(conversationId) {
    const response = await fetch(
      `${API_BASE}/api/conversations/${conversationId}`,
      {
        method: 'DELETE',
        headers: getAuthHeaders(),
      }
    );
    if (!response.ok) {
      throw new Error('Failed to delete conversation');
    }
    return response.json();
  },

  /**
   * Send a message in a conversation.
   */
  async sendMessage(conversationId, content) {
    // Check if CrewAI mode is enabled
    const useCrewAI = localStorage.getItem('use_crewai') === 'true';
    const endpoint = useCrewAI ? 'message/crew' : 'message';
    
    const response = await fetch(
      `${API_BASE}/api/conversations/${conversationId}/${endpoint}`,
      {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ content }),
      }
    );
    if (!response.ok) {
      throw new Error('Failed to send message');
    }
    return response.json();
  },

  /**
   * Send a message and receive streaming updates.
   * @param {string} conversationId - The conversation ID
   * @param {string} content - The message content
   * @param {function} onEvent - Callback function for each event: (eventType, data) => void
   * @returns {Promise<void>}
   */
  async sendMessageStream(conversationId, content, onEvent) {
    const response = await fetch(
      `${API_BASE}/api/conversations/${conversationId}/message/stream`,
      {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ content }),
      }
    );

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          try {
            const event = JSON.parse(data);
            onEvent(event.type, event);
          } catch (e) {
            console.error('Failed to parse SSE event:', e);
          }
        }
      }
    }
  },

  /**
   * Get prompt suggestions to help craft better questions.
   */
  async getPromptSuggestions(query = null, category = null, limit = 10) {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    if (category) params.append('category', category);
    params.append('limit', limit.toString());

    const response = await fetch(
      `${API_BASE}/prompts/suggestions?${params.toString()}`,
      {
        headers: getAuthHeaders(),
      }
    );
    if (!response.ok) {
      throw new Error('Failed to get prompt suggestions');
    }
    return response.json();
  },

  /**
   * Get all available prompt categories.
   */
  async getPromptCategories() {
    const response = await fetch(`${API_BASE}/prompts/categories`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to get prompt categories');
    }
    return response.json();
  },

  /**
   * Get the INEVITABLE Core Prompt Pack.
   */
  async getCorePrompts() {
    const response = await fetch(`${API_BASE}/prompts/core`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to get core prompts');
    }
    return response.json();
  },
};
