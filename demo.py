#!/usr/bin/env python3
"""
Confucius Agent Demo
Shows all the main features of the agent framework
"""

from confucius_agent import (
    create_agent,
    list_supported_models,
    MockClient,
    NoteStore,
    NoteType,
    MemoryManager,
    Orchestrator,
)
from pathlib import Path


def demo_models():
    """Demo: List all supported models"""
    print("\n" + "="*60)
    print("DEMO 1: Supported Models & Aliases")
    print("="*60)
    
    models = list_supported_models()
    
    print("\n📦 Providers:")
    for provider in ["anthropic", "openai", "google", "openrouter"]:
        if provider in models:
            print(f"\n  {provider.upper()}:")
            if isinstance(models[provider], list):
                for model in models[provider][:3]:  # Show first 3
                    print(f"    • {model}")
                if len(models[provider]) > 3:
                    print(f"    ... and {len(models[provider]) - 3} more")
    
    print("\n🏷️  Quick Aliases:")
    if "aliases" in models:
        for alias in models["aliases"][:8]:  # Show first 8
            print(f"    • {alias}")


def demo_mock_client():
    """Demo: Using the mock client for testing"""
    print("\n" + "="*60)
    print("DEMO 2: Mock Client (No API Key Required)")
    print("="*60)
    
    client = MockClient(responses=[
        "Hello! I can help with that.",
        "Let me analyze the code...",
        "TASK_COMPLETE: All done!"
    ])
    
    print("\n📞 Calling mock client:")
    for i in range(3):
        response = client([{"role": "user", "content": f"Test {i+1}"}])
        print(f"  Call {i+1}: {response[:50]}...")


def demo_memory_manager():
    """Demo: Hierarchical memory management"""
    print("\n" + "="*60)
    print("DEMO 3: Hierarchical Memory Manager")
    print("="*60)
    
    mm = MemoryManager(max_tokens=100000)
    
    print(f"\n📝 Memory Configuration:")
    print(f"  Max tokens: {mm.max_tokens:,}")
    print(f"  Compression threshold: {mm.compression_threshold:.1%}")
    
    # Add messages
    mm.add_message("system", "You are a helpful coding assistant.")
    mm.add_message("user", "Fix the bug in auth.py")
    mm.add_message("assistant", "I'll analyze the authentication code...")
    
    print(f"\n💬 Messages: {len(mm.messages)}")
    print(f"  Hierarchical scopes: {', '.join(mm.hierarchy.keys())}")


def demo_notes():
    """Demo: Note-taking with hindsight"""
    print("\n" + "="*60)
    print("DEMO 4: Note Storage & Hindsight Learning")
    print("="*60)
    
    import tempfile
    temp_dir = Path(tempfile.mkdtemp())
    
    store = NoteStore(temp_dir / "notes")
    
    # Create a regular note
    note = store.create_note(
        path="architecture/api_design",
        title="API Design Decisions",
        content="We chose REST over GraphQL for simplicity.",
        note_type=NoteType.DECISION,
        tags=["api", "architecture"]
    )
    
    print(f"\n📄 Created note: {note.title}")
    print(f"  Type: {note.note_type.value}")
    print(f"  Path: {note.path}")
    print(f"  Tags: {', '.join(note.tags)}")
    
    # Create a hindsight note
    failure_note = store.create_hindsight_note(
        path="failures/auth_bug",
        title="Authentication Token Expiry Bug",
        problem_description="Tokens were expiring too quickly",
        error_message="TokenExpiredError: Token expired at 2026-01-12",
        attempted_solutions=["Increased timeout", "Changed algorithm"],
        resolution="Fixed by updating token refresh logic"
    )
    
    print(f"\n⚠️  Created hindsight note: {failure_note.title}")
    print(f"  Attempted solutions: {len(failure_note.attempted_solutions)}")
    print(f"  Resolution: {failure_note.resolution[:50]}...")
    
    print(f"\n📚 Total notes in store: {len(store.index)}")


def demo_agent_creation():
    """Demo: Creating and configuring agents"""
    print("\n" + "="*60)
    print("DEMO 5: Agent Creation & Configuration")
    print("="*60)
    
    # Different provider examples
    providers = [
        ("mock", "Mock Client (Testing)"),
        ("claude", "Anthropic Claude"),
        ("gpt-5.2", "OpenAI GPT-5.2"),
        ("gemini", "Google Gemini"),
    ]
    
    print("\n🤖 Creating agents with different providers:\n")
    
    for model, description in providers:
        try:
            agent = create_agent(
                workspace=".",
                model=model,
                max_iterations=5,
                completion_promise="TASK_COMPLETE"
            )
            print(f"  ✅ {description:30} → {type(agent).__name__}")
        except ImportError as e:
            print(f"  ⚠️  {description:30} → {str(e)[:40]}...")


def demo_orchestrator():
    """Demo: Orchestrator with extensions"""
    print("\n" + "="*60)
    print("DEMO 6: Orchestrator with Extensions")
    print("="*60)
    
    from confucius_agent import (
        BashExtension,
        FileReadExtension,
        ThinkingExtension,
    )
    
    client = MockClient()
    extensions = [
        BashExtension(),
        FileReadExtension(workspace_root="."),
        ThinkingExtension(),
    ]
    
    orchestrator = Orchestrator(
        llm_client=client,
        extensions=extensions,
        max_iterations=5
    )
    
    print(f"\n⚙️  Orchestrator configured:")
    print(f"  Extensions: {len(orchestrator.extensions)}")
    print(f"  Max iterations: {orchestrator.max_iterations}")
    print(f"  Memory manager: {type(orchestrator.memory_manager).__name__}")
    
    print("\n  Extension list:")
    for ext in extensions:
        print(f"    • {ext.name}")


def main():
    """Run all demos"""
    print("\n" + "🎭 " * 20)
    print("CONFUCIUS AGENT - FEATURE DEMONSTRATIONS")
    print("🎭 " * 20)
    
    try:
        demo_models()
        demo_mock_client()
        demo_memory_manager()
        demo_notes()
        demo_agent_creation()
        demo_orchestrator()
        
        print("\n" + "="*60)
        print("✨ All demos completed successfully!")
        print("="*60)
        print("\n🚀 Next steps:")
        print("  1. Set API keys: export ANTHROPIC_API_KEY=...")
        print("  2. Run: confucius run 'your task'")
        print("  3. View docs: https://github.com/Aldine/llm-council-update")
        print()
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
