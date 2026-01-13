"""
Confucius Agent - AI Agent Scaffold with Ralph Wiggum Loop Pattern

A production-ready agent framework inspired by the Confucius Code Agent paper,
combining hierarchical memory, note-taking, and modular extensions with
the Ralph Wiggum autonomous iteration pattern.

Usage:
    from confucius_agent import create_agent, RalphLoopConfig
    
    agent = create_agent(
        workspace="./my-project",
        model="claude-sonnet-4-20250514"
    )
    result = agent.run("Fix the failing tests")

CLI:
    $ ralph-loop "npm test" --completion "All tests passed" --max-iter 10
    $ confucius run "Fix bug in auth.py"
"""

__version__ = "0.1.0"
__author__ = "Confucius Agent Contributors"

from .orchestrator import (
    Orchestrator,
    Extension,
    Action,
    ActionType,
    Message,
    MemoryManager,
    RunContext,
)

from .notes import (
    Note,
    HindsightNote,
    NoteType,
    NoteStore,
    NoteTakingAgent,
)

from .extensions import (
    BashExtension,
    FileEditExtension,
    FileReadExtension,
    FileSearchExtension,
    ThinkingExtension,
    PlanningExtension,
)

from .ralph_integration import (
    RalphLoopConfig,
    RalphOrchestrator,
    create_coding_agent,
)

from .llm_clients import (
    create_llm_client,
    list_supported_models,
    MODEL_ALIASES,
    AnthropicClient,
    OpenAIClient,
    GoogleGeminiClient,
    OpenRouterClient,
    MockClient,
)

# Convenience factory
def create_agent(
    workspace: str = ".",
    model: str = "claude-sonnet-4-20250514",
    api_key: str = None,
    completion_promise: str = "TASK_COMPLETE",
    max_iterations: int = 20,
    enable_notes: bool = True,
    notes_path: str = None,
) -> RalphOrchestrator:
    """
    Create a fully configured coding agent.
    
    Args:
        workspace: Root directory for file operations
        model: LLM model to use (claude-sonnet-4-20250514, gpt-4, etc.)
        api_key: API key (or set ANTHROPIC_API_KEY/OPENAI_API_KEY env var)
        completion_promise: String that signals task completion
        max_iterations: Maximum Ralph loop iterations
        enable_notes: Whether to enable persistent note-taking
        notes_path: Where to store notes (default: workspace/.confucius/notes)
    
    Returns:
        Configured RalphOrchestrator ready to run tasks
    """
    from pathlib import Path
    
    workspace_path = Path(workspace).resolve()
    
    if notes_path is None:
        notes_path = str(workspace_path / ".confucius" / "notes")
    
    config = RalphLoopConfig(
        completion_promise=completion_promise,
        max_iterations=max_iterations,
        enable_notes=enable_notes,
        notes_path=notes_path,
    )
    
    llm_client = create_llm_client(model=model, api_key=api_key)
    
    return create_coding_agent(
        llm_client=llm_client,
        workspace_root=str(workspace_path),
        ralph_config=config,
    )


__all__ = [
    # Version
    "__version__",
    
    # Main factory
    "create_agent",
    
    # Core components
    "Orchestrator",
    "Extension",
    "Action",
    "ActionType",
    "Message",
    "MemoryManager",
    "RunContext",
    
    # Notes
    "Note",
    "HindsightNote",
    "NoteType",
    "NoteStore",
    "NoteTakingAgent",
    
    # Extensions
    "BashExtension",
    "FileEditExtension",
    "FileReadExtension",
    "FileSearchExtension",
    "ThinkingExtension",
    "PlanningExtension",
    
    # Ralph integration
    "RalphLoopConfig",
    "RalphOrchestrator",
    "create_coding_agent",
    
    # LLM clients
    "create_llm_client",
    "list_supported_models",
    "MODEL_ALIASES",
    "AnthropicClient",
    "OpenAIClient",
    "GoogleGeminiClient",
    "OpenRouterClient",
    "MockClient",
]
