import { useState, useEffect, useCallback } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider, useToast } from './components/Toast';
import Login from './components/Login';
import Sidebar from './components/Sidebar';
import TopNav from './components/TopNav';
import ChatInterface from './components/ChatInterface';
import History from './components/History';
import Settings from './components/Settings';
import { api } from './api';

// Toggle between JWT and BFF auth modes
const USE_BFF_AUTH = false; // Set to true to use BFF OAuth instead of JWT

function AppContent() {
  const { state, user, logout } = useAuth();
  const { showError, showSuccess } = useToast();
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [currentView, setCurrentView] = useState('deliberation'); // 'deliberation', 'history', 'settings'

  const loadConversations = useCallback(async () => {
    try {
      const convs = await api.listConversations();
      setConversations(convs);
    } catch {
      showError('Failed to load conversations');
    }
  }, [showError]);

  const loadConversation = useCallback(async (id) => {
    try {
      const conv = await api.getConversation(id);
      console.log('[LoadConversation] Loaded:', conv);
      setCurrentConversation(conv);
    } catch (error) {
      console.error('[LoadConversation] Error:', error);
      showError('Failed to load conversation');
    }
  }, [showError]);

  const handleDeleteConversation = async (id) => {
    try {
      // Optimistically remove from UI
      setConversations(conversations.filter(c => c.id !== id));
      if (currentConversationId === id) {
        setCurrentConversationId(null);
        setCurrentConversation(null);
      }
      // Delete from backend
      await api.deleteConversation(id);
      showSuccess('Conversation deleted successfully');
    } catch {
      showError('Failed to delete conversation');
      // Reload conversations on error
      loadConversations();
    }
  };

  // Load conversations on mount (only when authenticated)
  useEffect(() => {
    if (state === 'AUTHENTICATED') {
      loadConversations();
    }
  }, [state, loadConversations]);

  // Load conversation details when selected
  useEffect(() => {
    if (currentConversationId && state === 'AUTHENTICATED') {
      loadConversation(currentConversationId);
    }
  }, [currentConversationId, state, loadConversation]);

  // Show loading spinner during initialization
  if (state === 'INITIALIZING') {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
           background: 'var(--color-background)',
        color: 'var(--primary)',
      }}>
        <div>Loading...</div>
      </div>
    );
  }

  // Show login screen if not authenticated
  if (state === 'UNAUTHENTICATED' || state === 'AUTHENTICATING' || state === 'ERROR') {
    // Redirect to BFF OAuth if enabled
    if (USE_BFF_AUTH && state === 'UNAUTHENTICATED') {
      return <div style={{ padding: '40px', textAlign: 'center' }}>Redirecting to OAuth login...</div>;
    }
    return <Login />;
  }

  const handleNewConversation = async () => {
    try {
      const newConv = await api.createConversation();
      setConversations([
        { id: newConv.id, created_at: newConv.created_at, message_count: 0 },
        ...conversations,
      ]);
      setCurrentConversationId(newConv.id);
    } catch {
      showError('Failed to create conversation');
    }
  };

  const handleSelectConversation = (id) => {
    console.log('[SelectConversation] ID:', id);
    setCurrentConversationId(id);
    setCurrentView('deliberation'); // Switch to deliberation view when selecting a conversation
    setMobileMenuOpen(false);
  };

  const handleSendMessage = async (content) => {
    if (!currentConversationId) return;

    setIsLoading(true);
    
    // Check if CrewAI mode is enabled
    const useCrewAI = localStorage.getItem('use_crewai') === 'true';
    
    try {
      // Optimistically add user message to UI
      const userMessage = { role: 'user', content };
      setCurrentConversation((prev) => ({
        ...prev,
        messages: [...prev.messages, userMessage],
      }));

      // Create a partial assistant message that will be updated progressively
      const assistantMessage = {
        role: 'assistant',
        stage1: null,
        stage2: null,
        stage3: null,
        metadata: null,
        loading: {
          stage1: false,
          stage2: false,
          stage3: false,
        },
      };

      // Add the partial assistant message
      setCurrentConversation((prev) => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
      }));

      // If CrewAI mode, use non-streaming API
      if (useCrewAI) {
        const response = await api.sendMessage(currentConversationId, content);
        
        console.log('[CrewAI] Response received:', response);
        
        // Update the assistant message with the complete response
        setCurrentConversation((prev) => {
          const messages = [...prev.messages];
          const lastMsg = messages[messages.length - 1];
          lastMsg.stage1 = response.stage1;
          lastMsg.stage2 = response.stage2;
          lastMsg.stage3 = response.stage3;
          lastMsg.metadata = response.metadata;
          lastMsg.loading = {
            stage1: false,
            stage2: false,
            stage3: false,
          };
          console.log('[CrewAI] Updated message:', lastMsg);
          return { ...prev, messages };
        });
        
        // Reload conversations list to get updated title
        await loadConversations();
        setIsLoading(false);
        return;
      }

      // Regular streaming mode
      await api.sendMessageStream(currentConversationId, content, (eventType, event) => {
        switch (eventType) {
          case 'stage1_start':
            setCurrentConversation((prev) => {
              const messages = [...prev.messages];
              const lastMsg = messages[messages.length - 1];
              lastMsg.loading.stage1 = true;
              return { ...prev, messages };
            });
            break;

          case 'stage1_complete':
            setCurrentConversation((prev) => {
              const messages = [...prev.messages];
              const lastMsg = messages[messages.length - 1];
              lastMsg.stage1 = event.data;
              lastMsg.loading.stage1 = false;
              return { ...prev, messages };
            });
            break;

          case 'stage2_start':
            setCurrentConversation((prev) => {
              const messages = [...prev.messages];
              const lastMsg = messages[messages.length - 1];
              lastMsg.loading.stage2 = true;
              return { ...prev, messages };
            });
            break;

          case 'stage2_complete':
            setCurrentConversation((prev) => {
              const messages = [...prev.messages];
              const lastMsg = messages[messages.length - 1];
              lastMsg.stage2 = event.data;
              lastMsg.metadata = event.metadata;
              lastMsg.loading.stage2 = false;
              return { ...prev, messages };
            });
            break;

          case 'stage3_start':
            setCurrentConversation((prev) => {
              const messages = [...prev.messages];
              const lastMsg = messages[messages.length - 1];
              lastMsg.loading.stage3 = true;
              return { ...prev, messages };
            });
            break;

          case 'stage3_complete':
            setCurrentConversation((prev) => {
              const messages = [...prev.messages];
              const lastMsg = messages[messages.length - 1];
              lastMsg.stage3 = event.data;
              lastMsg.loading.stage3 = false;
              return { ...prev, messages };
            });
            break;

          case 'title_complete':
            // Reload conversations to get updated title
            loadConversations();
            break;

          case 'complete':
            // Stream complete, reload conversations list
            loadConversations();
            setIsLoading(false);
            break;

          case 'error':
            showError(event.message || 'An error occurred during streaming');
            setIsLoading(false);
            break;

          default:
            console.log('Unknown event type:', eventType);
        }
      });
    } catch {
      showError('Failed to send message');
      // Remove optimistic messages on error
      setCurrentConversation((prev) => ({
        ...prev,
        messages: prev.messages.slice(0, -2),
      }));
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen bg-background font-sans antialiased flex flex-col">
      <TopNav onToggleSidebar={() => setMobileMenuOpen(!mobileMenuOpen)} />
      <div className="flex flex-1 relative overflow-hidden">
        <Sidebar
          conversations={conversations}
          currentConversationId={currentConversationId}
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
          onDeleteConversation={handleDeleteConversation}
          isOpen={mobileMenuOpen}
          onClose={() => setMobileMenuOpen(false)}
          currentView={currentView}
          onViewChange={(view) => {
            setCurrentView(view);
            setMobileMenuOpen(false);
          }}
          user={user}
          onLogout={logout}
        />
        <main className="flex-1 min-w-0 overflow-hidden">
          {currentView === 'deliberation' && (
            <ChatInterface
              conversation={currentConversation}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
            />
          )}
          {currentView === 'history' && (
            <History
              conversations={conversations}
              onSelectConversation={handleSelectConversation}
              currentConversationId={currentConversationId}
            />
          )}
          {currentView === 'settings' && (
            <Settings />
          )}
        </main>
      </div>

      {/* Status Indicator - Fixed Bottom Right */}
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <AppContent />
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
