import { useState, useEffect, useCallback } from 'react';
import { api } from '../api';

export default function PromptHelper({ onSelectPrompt, placement = 'modal' }) {
  const [isOpen, setIsOpen] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [corePrompts, setCorePrompts] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const loadCategories = useCallback(async () => {
    try {
      const data = await api.getPromptCategories();
      setCategories(data.categories || []);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  }, []);

  const loadSuggestions = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await api.getPromptSuggestions(
        searchQuery || null,
        selectedCategory,
        15
      );
      setSuggestions(data.suggestions || []);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, selectedCategory]);

  const loadCorePrompts = useCallback(async () => {
    try {
      const data = await api.getCorePrompts();
      setCorePrompts(data.prompts || []);
    } catch (error) {
      console.error('Failed to load core prompts:', error);
    }
  }, []);

  useEffect(() => {
    loadCategories();
  }, [loadCategories]);

  useEffect(() => {
    if (isOpen) {
      loadCorePrompts();
      loadSuggestions();
    }
  }, [isOpen, loadCorePrompts, loadSuggestions]);

  const handleSelectPrompt = (prompt) => {
    onSelectPrompt(prompt.text);
    setIsOpen(false);
  };

  const handleSelectCore = (prompt) => {
    onSelectPrompt(prompt.template);
    setIsOpen(false);
  };

  const panel = (
    <div className="bg-card border border-border rounded-lg shadow-2xl max-w-4xl w-full max-h-[70vh] flex flex-col">
      {/* Header */}
      <div className="px-6 py-4 border-b border-border flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Prompt Library</h2>
          <p className="text-sm text-muted-foreground">3000+ prompts to help you ask better questions</p>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="p-2 hover:bg-accent/10 rounded-sm transition-colors"
          aria-label="Close prompt library"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Search and Filters */}
      <div className="px-6 py-4 border-b border-border space-y-3">
        {corePrompts.length > 0 && (
          <div className="space-y-2">
            <div className="text-xs font-semibold tracking-wide uppercase text-muted-foreground">
              INEVITABLE Core Prompt Pack
            </div>
            <div className="flex flex-wrap gap-2">
              {corePrompts.map((p) => (
                <button
                  key={p.name}
                  onClick={() => handleSelectCore(p)}
                  className="px-3 py-1.5 text-xs font-medium rounded-sm border border-border hover:bg-accent/10 hover:border-accent transition-colors"
                  title={p.purpose}
                >
                  {p.name}
                </button>
              ))}
            </div>
          </div>
        )}

        <input
          type="text"
          placeholder="Search prompts..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full h-10 px-3 py-2 text-sm border border-border rounded-sm bg-background focus:outline-none focus:ring-2 focus:ring-primary"
        />
        
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`px-3 py-1.5 text-xs font-medium rounded-sm transition-colors ${
              selectedCategory === null
                ? 'bg-primary text-primary-foreground'
                : 'border border-border hover:bg-accent/10'
            }`}
          >
            All
          </button>
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-3 py-1.5 text-xs font-medium rounded-sm transition-colors ${
                selectedCategory === category
                  ? 'bg-primary text-primary-foreground'
                  : 'border border-border hover:bg-accent/10'
              }`}
            >
              {category}
            </button>
          ))}
        </div>
      </div>

      {/* Suggestions List */}
      <div className="flex-1 overflow-y-auto p-6">
        {isLoading ? (
          <div className="text-center py-8 text-muted-foreground">
            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
            Loading suggestions...
          </div>
        ) : suggestions.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p>No prompts found matching your criteria</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {suggestions.map((prompt, index) => (
              <button
                key={index}
                onClick={() => handleSelectPrompt(prompt)}
                className="text-left p-4 border border-border rounded-sm hover:bg-accent/10 hover:border-accent transition-all group"
              >
                <div className="flex items-start gap-3 mb-2">
                  <span className="text-xs px-2 py-0.5 rounded-full bg-accent/20 text-accent font-medium">
                    {prompt.category}
                  </span>
                </div>
                <h3 className="text-sm font-medium mb-2 group-hover:text-primary transition-colors">
                  {prompt.title}
                </h3>
                <p className="text-xs text-muted-foreground line-clamp-2">
                  {prompt.text}
                </p>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-6 py-3 border-t border-border bg-muted/30 text-xs text-muted-foreground">
        💡 Tip: Click any prompt to use it as a starting point for your question
      </div>
    </div>
  );

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium border border-border rounded-sm hover:bg-accent/10 hover:border-accent transition-colors"
        title="Get prompt suggestions from 3000+ library"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        Prompt Library
      </button>
    );
  }

  if (placement === 'inline') {
    return (
      <div className="relative w-full flex justify-center">
        <button
          onClick={() => setIsOpen(false)}
          className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium border border-border rounded-sm bg-card hover:bg-accent/10 hover:border-accent transition-colors"
          title="Close prompt library"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
          Prompt Library
        </button>

        <div className="absolute bottom-full mb-3 left-0 right-0 z-40 px-2">
          <div className="mx-auto w-full max-w-4xl">
            {panel}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      {panel}
    </div>
  );
}
