import React, { useState } from 'react';

export default function Settings() {
  // Initialize state with localStorage value
  const [apiKey, setApiKey] = useState(() => {
    const saved = localStorage.getItem('openrouter_api_key') || '';
    return saved ? '••••••••' + saved.slice(-4) : '';
  });
  
  const [useCrewAI, setUseCrewAI] = useState(() => {
    return localStorage.getItem('use_crewai') === 'true';
  });
  
  const [models] = useState({
    council: ['openai/gpt-4o', 'anthropic/claude-3.5-sonnet', 'google/gemini-pro-1.5'],
    chairman: 'openai/gpt-4o'
  });

  const toggleCrewAI = () => {
    const newValue = !useCrewAI;
    setUseCrewAI(newValue);
    localStorage.setItem('use_crewai', newValue.toString());
  };

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-4xl mx-auto p-6 space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Settings</h1>
        <p className="text-muted-foreground">Configure your LLM Council experience</p>
      </div>

      {/* API Configuration */}
      <div className="border border-border rounded-lg bg-card p-6 space-y-4">
        <div>
          <h2 className="text-xl font-semibold mb-1">API Configuration</h2>
          <p className="text-sm text-muted-foreground">Manage your OpenRouter API credentials</p>
        </div>
        
        <div className="space-y-2">
          <label className="text-sm font-medium" htmlFor="api-key">
            OpenRouter API Key
          </label>
          <div className="flex gap-2">
            <input
              id="api-key"
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="sk-or-v1-..."
              className="flex-1 h-10 px-3 py-2 text-sm border border-border rounded-sm bg-background focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <button className="px-4 py-2 bg-primary text-primary-foreground rounded-sm text-sm font-medium hover:bg-primary/90 transition-colors">
              Save
            </button>
          </div>
          <p className="text-xs text-muted-foreground">
            Get your API key from <a href="https://openrouter.ai" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">openrouter.ai</a>
          </p>
        </div>
      </div>

      {/* Council Models */}
      <div className="border border-border rounded-lg bg-card p-6 space-y-4">
        <div>
          <h2 className="text-xl font-semibold mb-1">Council Models</h2>
          <p className="text-sm text-muted-foreground">Configure which models participate in deliberation</p>
        </div>

        <div className="space-y-3">
          {models.council.map((model, index) => (
            <div key={index} className="flex items-center gap-3 p-3 border border-border rounded-sm bg-secondary/20">
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-xs font-medium">
                {index + 1}
              </div>
              <div className="flex-1">
                <div className="text-sm font-medium">{model}</div>
                <div className="text-xs text-muted-foreground">Council Member</div>
              </div>
              <button className="p-2 hover:bg-accent/50 rounded-sm transition-colors">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ))}
          
          <button className="w-full h-10 px-4 py-2 border border-dashed border-border rounded-sm text-sm font-medium text-muted-foreground hover:text-foreground hover:border-primary/50 transition-colors">
            + Add Council Member
          </button>
        </div>
      </div>

      {/* Chairman Model */}
      <div className="border border-border rounded-lg bg-card p-6 space-y-4">
        <div>
          <h2 className="text-xl font-semibold mb-1">Chairman Model</h2>
          <p className="text-sm text-muted-foreground">Model responsible for final synthesis</p>
        </div>

        <div className="p-3 border border-border rounded-sm bg-accent/10">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="flex-1">
              <div className="text-sm font-medium">{models.chairman}</div>
              <div className="text-xs text-muted-foreground">Chairman</div>
            </div>
            <button className="px-3 py-1.5 text-xs font-medium border border-border rounded-sm hover:bg-accent/50 transition-colors">
              Change
            </button>
          </div>
        </div>
      </div>

      {/* Deliberation Mode Explainer */}
      <div className="border border-accent/30 rounded-lg bg-card p-6 space-y-4">
        <div>
          <h2 className="text-xl font-semibold mb-1">Deliberation Modes</h2>
          <p className="text-sm text-muted-foreground">Choose how AI agents collaborate to answer your questions</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Standard Council Mode */}
          <div className={`p-4 border rounded-sm transition-all ${!useCrewAI ? 'border-primary bg-primary/5' : 'border-border bg-secondary/20'}`}>
            <div className="flex items-start gap-3 mb-3">
              <div className="w-8 h-8 rounded-sm bg-primary/20 flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-semibold mb-1">Standard Council</h3>
                <span className="inline-block text-[10px] px-2 py-0.5 rounded-full bg-muted text-muted-foreground mb-2">Default Mode</span>
              </div>
            </div>
            <ul className="space-y-2 text-xs text-muted-foreground">
              <li className="flex items-start gap-2">
                <span className="text-accent mt-0.5">•</span>
                <span><strong>3-Stage Deliberation:</strong> Individual responses → Peer review → Chairman synthesis</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-accent mt-0.5">•</span>
                <span><strong>Parallel Processing:</strong> All models respond simultaneously for speed</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-accent mt-0.5">•</span>
                <span><strong>Anonymous Review:</strong> Models rank responses without bias</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-accent mt-0.5">•</span>
                <span><strong>Best for:</strong> Fast, diverse perspectives with democratic consensus</span>
              </li>
            </ul>
          </div>

          {/* CrewAI Mode */}
          <div className={`p-4 border rounded-sm transition-all ${useCrewAI ? 'border-primary bg-primary/5' : 'border-border bg-secondary/20'}`}>
            <div className="flex items-start gap-3 mb-3">
              <div className="w-8 h-8 rounded-sm bg-accent/20 flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-semibold mb-1">CrewAI Orchestration</h3>
                <span className="inline-block text-[10px] px-2 py-0.5 rounded-full bg-accent/20 text-accent mb-2">Enhanced Mode</span>
              </div>
            </div>
            <ul className="space-y-2 text-xs text-muted-foreground">
              <li className="flex items-start gap-2">
                <span className="text-accent mt-0.5">•</span>
                <span><strong>Role-Based Agents:</strong> Specialized agents with defined expertise and goals</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-accent mt-0.5">•</span>
                <span><strong>Sequential Tasks:</strong> Agents collaborate in a structured workflow</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-accent mt-0.5">•</span>
                <span><strong>Context Sharing:</strong> Agents build on each other's work iteratively</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-accent mt-0.5">•</span>
                <span><strong>Best for:</strong> Deep analysis, complex reasoning, and coordinated problem-solving</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Preferences */}
      <div className="border border-border rounded-lg bg-card p-6 space-y-4">
        <div>
          <h2 className="text-xl font-semibold mb-1">Preferences</h2>
          <p className="text-sm text-muted-foreground">Customize your experience</p>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 border border-border rounded-sm bg-primary/5">
            <div className="flex-1">
              <div className="text-sm font-medium">🤖 Use CrewAI Multi-Agent Orchestration</div>
              <div className="text-xs text-muted-foreground">
                Enable role-based agents with sequential task execution for deeper analysis
              </div>
            </div>
            <button 
              onClick={toggleCrewAI}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors flex-shrink-0 ml-4 ${
                useCrewAI ? 'bg-primary' : 'bg-muted'
              }`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                useCrewAI ? 'translate-x-6' : 'translate-x-1'
              }`} />
            </button>
          </div>

          <div className="flex items-center justify-between p-3 border border-border rounded-sm">
            <div>
              <div className="text-sm font-medium">Show Stage Progress</div>
              <div className="text-xs text-muted-foreground">Display each deliberation stage as it completes</div>
            </div>
            <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-primary transition-colors">
              <span className="inline-block h-4 w-4 transform translate-x-6 rounded-full bg-white transition-transform" />
            </button>
          </div>

          <div className="flex items-center justify-between p-3 border border-border rounded-sm">
            <div>
              <div className="text-sm font-medium">Auto-generate Titles</div>
              <div className="text-xs text-muted-foreground">Automatically create conversation titles</div>
            </div>
            <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-primary transition-colors">
              <span className="inline-block h-4 w-4 transform translate-x-6 rounded-full bg-white transition-transform" />
            </button>
          </div>

          <div className="flex items-center justify-between p-3 border border-border rounded-sm">
            <div>
              <div className="text-sm font-medium">Dark Mode</div>
              <div className="text-xs text-muted-foreground">Use dark color scheme</div>
            </div>
            <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-muted transition-colors">
              <span className="inline-block h-4 w-4 transform translate-x-1 rounded-full bg-white transition-transform" />
            </button>
          </div>
        </div>
      </div>

      {/* About */}
      <div className="border border-border rounded-lg bg-card p-6">
        <h2 className="text-xl font-semibold mb-3">About LLM Council</h2>
        <div className="space-y-2 text-sm text-muted-foreground">
          <p>Version 1.0.0</p>
          <p>A 3-stage deliberation system where multiple LLMs collaborate to answer questions through parallel querying, anonymized peer review, and final synthesis.</p>
          <div className="pt-3 flex gap-4">
            <a href="#" className="text-primary hover:underline">Documentation</a>
            <a href="#" className="text-primary hover:underline">GitHub</a>
            <a href="#" className="text-primary hover:underline">Report Issue</a>
          </div>
        </div>
      </div>
      </div>
    </div>
  );
}
