import { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
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
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [currentView, setCurrentView] = useState('deliberation'); // 'deliberation', 'history', 'settings'

  const loadConversations = async () => {
    try {
      const convs = await api.listConversations();
      setConversations(convs);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const loadConversation = async (id) => {
    try {
      const conv = await api.getConversation(id);
      setCurrentConversation(conv);
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  };

  // Load conversations on mount (only when authenticated)
  useEffect(() => {
    if (state === 'AUTHENTICATED') {
      loadConversations();
    }
  }, [state]);

  // Load conversation details when selected
  useEffect(() => {
    if (currentConversationId && state === 'AUTHENTICATED') {
      loadConversation(currentConversationId);
    }
  }, [currentConversationId, state]);

  // Show loading spinner during initialization
  if (state === 'INITIALIZING') {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        background: 'var(--background)',
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
      window.location.href = 'http://localhost:8001/bff/auth/login';
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
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const handleSelectConversation = (id) => {
    setCurrentConversationId(id);
    setCurrentView('deliberation'); // Switch to deliberation view when selecting a conversation
    setMobileMenuOpen(false);
  };

  const handleSendMessage = async (content) => {
    if (!currentConversationId) return;

    setIsLoading(true);
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

      // Send message with streaming
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
            console.error('Stream error:', event.message);
            setIsLoading(false);
            break;

          default:
            console.log('Unknown event type:', eventType);
        }
      });
    } catch (error) {
      console.error('Failed to send message:', error);
      // Remove optimistic messages on error
      setCurrentConversation((prev) => ({
        ...prev,
        messages: prev.messages.slice(0, -2),
      }));
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background font-sans antialiased">
      <TopNav onToggleSidebar={() => setMobileMenuOpen(!mobileMenuOpen)} />
      <div className="flex relative">
        <Sidebar
          conversations={conversations}
          currentConversationId={currentConversationId}
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
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
        <main className="flex-1 min-w-0">
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
      <AppContent />
    </AuthProvider>
  );
}

export default App;
