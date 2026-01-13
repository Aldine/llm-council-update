import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import Stage1 from './Stage1';
import Stage2 from './Stage2';
import Stage3 from './Stage3';
import PromptHelper from './PromptHelper';

export default function ChatInterface({
  conversation,
  onSendMessage,
  isLoading,
}) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  if (!conversation) {
    console.log('[ChatInterface] No conversation provided');
    return (
      <div className="h-full flex items-center justify-center bg-background">
        <div className="text-center space-y-4 max-w-md px-6">
          <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-6">
            <div className="w-8 h-8 bg-accent rounded-sm animate-pulse" />
          </div>
          <h2 className="text-2xl font-medium tracking-tight">Welcome to LLM Council</h2>
          <p className="text-muted-foreground">Create a new session to begin the deliberation process.</p>
        </div>
      </div>
    );
  }

  console.log('[ChatInterface] Rendering with conversation:', conversation);
  console.log('[ChatInterface] Messages:', conversation.messages);
  console.log('[ChatInterface] Messages is Array?:', Array.isArray(conversation.messages));
  console.log('[ChatInterface] Messages count:', conversation.messages?.length);

  return (
    <div className="flex flex-col h-full bg-background">
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-8">
        {!conversation.messages || conversation.messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-4 opacity-50">
            <h2 className="text-xl font-medium">Start a conversation</h2>
            <p className="text-sm text-muted-foreground">Ask a question to consult the LLM Council</p>
          </div>
        ) : (
          conversation.messages.map((msg, index) => (
            <div key={index} className="max-w-4xl mx-auto w-full animate-in fade-in slide-in-from-bottom-4 duration-500">
              {msg.role === 'user' ? (
                <div className="flex justify-end mb-8">
                  <div className="bg-primary text-primary-foreground px-5 py-3 rounded-sm max-w-[80%] shadow-sm">
                    <div className="markdown-content">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="space-y-6 mb-12">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-6 h-6 rounded-sm bg-accent flex items-center justify-center">
                      <span className="text-[10px] font-bold text-accent-foreground">AI</span>
                    </div>
                    <span className="text-sm font-medium tracking-wide uppercase text-muted-foreground">Council Deliberation</span>
                  </div>

                  {/* Stage 1 */}
                  {msg.loading?.stage1 && (
                    <div className="flex items-center gap-3 p-4 border border-border rounded-sm bg-card/50 animate-pulse">
                      <div className="w-4 h-4 border-2 border-accent border-t-transparent rounded-full animate-spin" />
                      <span className="text-sm text-muted-foreground">Stage 1: Collecting individual responses...</span>
                    </div>
                  )}
                  {msg.stage1 && <Stage1 responses={msg.stage1} />}

                  {/* Stage 2 */}
                  {msg.loading?.stage2 && (
                    <div className="flex items-center gap-3 p-4 border border-border rounded-sm bg-card/50 animate-pulse">
                      <div className="w-4 h-4 border-2 border-accent border-t-transparent rounded-full animate-spin" />
                      <span className="text-sm text-muted-foreground">Stage 2: Peer rankings in progress...</span>
                    </div>
                  )}
                  {msg.stage2 && (
                    <Stage2
                      rankings={msg.stage2}
                      labelToModel={msg.metadata?.label_to_model}
                      aggregateRankings={msg.metadata?.aggregate_rankings}
                    />
                  )}

                  {/* Stage 3 */}
                  {msg.loading?.stage3 && (
                    <div className="flex items-center gap-3 p-4 border border-border rounded-sm bg-card/50 animate-pulse">
                      <div className="w-4 h-4 border-2 border-accent border-t-transparent rounded-full animate-spin" />
                      <span className="text-sm text-muted-foreground">Stage 3: Synthesizing final answer...</span>
                    </div>
                  )}
                  {msg.stage3 && <Stage3 finalResponse={msg.stage3} />}
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-6 border-t border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="max-w-4xl mx-auto relative">
          <div className="mb-3 flex justify-center">
            <PromptHelper placement="inline" onSelectPrompt={(text) => setInput(text)} />
          </div>

          <form onSubmit={handleSubmit} className="relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask the council..."
              className="w-full min-h-[60px] max-h-[200px] p-4 pr-12 bg-card border border-border rounded-sm focus:outline-none focus:ring-1 focus:ring-ring focus:border-accent resize-none text-sm shadow-sm transition-colors"
              disabled={isLoading}
              rows={1}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="absolute right-3 bottom-3 p-2 text-muted-foreground hover:text-foreground disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </form>
          <div className="text-center mt-2">
            <span className="text-[10px] text-muted-foreground">
              AI Council can make mistakes. Verify important information.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}