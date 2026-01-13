"""
PRACTICAL INTEGRATION EXAMPLE: Confucius Agent with Context Scaffolding

This demonstrates how to use confucius-agent to build agents with:
1. Persistent context across sessions
2. Ralph loop autonomous iteration
3. Custom extensions for domain-specific tools
4. Memory management and learning

Run this to see confucius-agent in action!
"""

import os
import json
from pathlib import Path
from confucius_agent import (
    Orchestrator,
    MemoryManager,
    RalphOrchestrator,
    RalphLoopConfig
)
from confucius_agent.orchestrator import Extension, Action, RunContext, ActionType
from confucius_agent.notes import NoteStore, NoteTakingAgent


class CodeAnalysisExtension(Extension):
    """Example extension for analyzing code"""
    
    def __init__(self):
        super().__init__("code_analysis")
    
    def can_handle(self, action: Action) -> bool:
        return action.type == ActionType.FILE_READ
    
    def execute(self, action: Action, context: RunContext) -> Action:
        """Analyze code file and store insights"""
        try:
            filepath = action.content
            if Path(filepath).exists():
                # Read file
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Simple analysis
                lines = len(content.split('\n'))
                functions = content.count('def ')
                classes = content.count('class ')
                
                # Store in context for future use
                context.set_artifact(f"analysis_{filepath}", {
                    "lines": lines,
                    "functions": functions,
                    "classes": classes
                })
                
                action.result = f"Analyzed {filepath}: {lines} lines, {functions} functions, {classes} classes"
            else:
                action.error = f"File not found: {filepath}"
        except Exception as e:
            action.error = str(e)
        
        return action


# =============================================================================
# EXAMPLE 1: Basic Agent with Memory Scaffolding
# =============================================================================

def example_1_memory_scaffolding():
    """Demonstrates context persistence across 'sessions'"""
    
    print("\n" + "="*70)
    print("EXAMPLE 1: Memory Scaffolding & Context Persistence")
    print("="*70 + "\n")
    
    # Session 1: Build up context
    print("📝 Session 1: Building context...")
    memory = MemoryManager()
    
    # Add information to short-term memory
    memory.add_to_short_term("project_name", "LLM Council")
    memory.add_to_short_term("tech_stack", {
        "backend": "FastAPI",
        "frontend": "React",
        "database": "SQLite"
    })
    memory.add_to_short_term("current_task", "Optimize API payloads")
    
    # Promote important info to long-term
    memory.promote_to_long_term(["project_name", "tech_stack"])
    
    print(f"   Short-term: {list(memory.short_term_memory.keys())}")
    print(f"   Long-term: {list(memory.long_term_memory.keys())}")
    
    # Persist context to disk
    context_file = Path("session_context.json")
    with open(context_file, 'w') as f:
        json.dump(memory.export_state(), f, indent=2)
    
    print(f"   ✅ Context saved to {context_file}")
    
    # Session 2: Restore context
    print(f"\n📂 Session 2: Restoring context...")
    with open(context_file, 'r') as f:
        state = json.load(f)
    
    memory_restored = MemoryManager()
    memory_restored.import_state(state)
    
    # Context is intact!
    project = memory_restored.get_from_long_term("project_name")
    stack = memory_restored.get_from_long_term("tech_stack")
    
    print(f"   ✅ Restored context successfully")
    print(f"   Project: {project}")
    print(f"   Stack: {stack}")
    print(f"\n✨ Context persisted across 'sessions'!")


# =============================================================================
# EXAMPLE 2: Ralph Loop with Autonomous Iteration
# =============================================================================

def example_2_ralph_loop():
    """Demonstrates autonomous task completion"""
    
    print("\n" + "="*70)
    print("EXAMPLE 2: Ralph Loop - Autonomous Iteration")
    print("="*70 + "\n")
    
    # Mock LLM for demonstration
    iteration_count = [0]  # Mutable to track across calls
    
    def mock_llm(messages):
        """Simulates LLM that completes after 3 iterations"""
        iteration_count[0] += 1
        
        if iteration_count[0] < 3:
            return f"Working on task... (iteration {iteration_count[0]})"
        else:
            return "Task completed successfully! TASK_COMPLETE"
    
    # Configure Ralph loop
    config = RalphLoopConfig(
        completion_promise="TASK_COMPLETE",
        max_iterations=10,
        delay_seconds=1,
        enable_notes=True,
        notes_path="./example_notes",
        verbose=True
    )
    
    # Create Ralph orchestrator
    ralph = RalphOrchestrator(
        llm_client=mock_llm,
        extensions=[],
        config=config,
        system_prompt="You are a helpful assistant."
    )
    
    print("🎭 Starting Ralph loop...")
    print("   Task: 'Complete the deployment'")
    print("   Will iterate until 'TASK_COMPLETE' is returned\n")
    
    # Run autonomously
    result = ralph.run_ralph_loop("Complete the deployment")
    
    print(f"\n✨ Completed in {result['iterations']} iterations!")
    print(f"   Completion detected: {result['completion_detected']}")
    print(f"   Total time: {result.get('total_time', 0):.2f}s")


# =============================================================================
# EXAMPLE 3: Custom Extensions with Shared Context
# =============================================================================

def example_3_custom_extensions():
    """Demonstrates building custom extensions that share context"""
    
    print("\n" + "="*70)
    print("EXAMPLE 3: Custom Extensions with Shared Context")
    print("="*70 + "\n")
    
    # Mock LLM
    def mock_llm(messages):
        return "Analysis complete"
    
    # Create memory and context
    memory = MemoryManager()
    context = RunContext(
        session_id="example-session",
        memory_manager=memory
    )
    
    # Create custom extension
    code_ext = CodeAnalysisExtension()
    
    # Simulate analyzing multiple files
    files = ["backend/main.py", "backend/models.py", "frontend/App.jsx"]
    
    print("🔍 Analyzing codebase with custom extension...\n")
    
    for filepath in files:
        # Create action
        action = Action(
            type=ActionType.FILE_READ,
            content=filepath
        )
        
        # Execute through extension
        result_action = code_ext.execute(action, context)
        
        if result_action.result:
            print(f"   ✅ {result_action.result}")
        else:
            print(f"   ⚠️  {result_action.error}")
    
    # Show accumulated context
    print(f"\n📊 Context accumulated:")
    for key, value in context.artifact_store.items():
        print(f"   {key}: {value}")
    
    print(f"\n✨ Extensions can share data through RunContext!")


# =============================================================================
# EXAMPLE 4: Multi-Agent Collaboration with Shared Memory
# =============================================================================

def example_4_multi_agent_collaboration():
    """Demonstrates multiple agents sharing memory"""
    
    print("\n" + "="*70)
    print("EXAMPLE 4: Multi-Agent Collaboration (Shared Memory)")
    print("="*70 + "\n")
    
    # Shared memory across all agents
    memory = MemoryManager()
    
    # Mock LLMs with different "personalities"
    def architect_llm(messages):
        # Architect adds design to memory
        memory.add_to_short_term("design", "REST API with 3 endpoints")
        return "Design: REST API with /users, /posts, /comments"
    
    def implementer_llm(messages):
        # Implementer reads design from memory
        design = memory.get_from_short_term("design")
        memory.add_to_short_term("implementation", "FastAPI code written")
        return f"Implemented: {design} using FastAPI"
    
    def reviewer_llm(messages):
        # Reviewer reads both design and implementation
        design = memory.get_from_short_term("design")
        impl = memory.get_from_short_term("implementation")
        return f"Review: {design} + {impl} looks good!"
    
    # Create three agents sharing memory
    print("👥 Creating collaborative agent team...\n")
    
    architect = Orchestrator(
        llm_client=architect_llm,
        extensions=[],
        memory_manager=memory,
        system_prompt="You are a software architect"
    )
    
    implementer = Orchestrator(
        llm_client=implementer_llm,
        extensions=[],
        memory_manager=memory,  # Same memory!
        system_prompt="You are a developer"
    )
    
    reviewer = Orchestrator(
        llm_client=reviewer_llm,
        extensions=[],
        memory_manager=memory,  # Same memory!
        system_prompt="You are a code reviewer"
    )
    
    # Collaborative workflow
    print("🏗️  Architect designs...")
    design_result = architect.run("Design user management API")
    print(f"   Result: {design_result.get('response', 'N/A')[:60]}...\n")
    
    print("💻 Implementer codes...")
    impl_result = implementer.run("Implement the design")
    print(f"   Result: {impl_result.get('response', 'N/A')[:60]}...\n")
    
    print("🔍 Reviewer checks...")
    review_result = reviewer.run("Review the implementation")
    print(f"   Result: {review_result.get('response', 'N/A')[:60]}...\n")
    
    # Show shared memory
    print("💾 Shared Memory State:")
    print(f"   Short-term keys: {list(memory.short_term_memory.keys())}")
    print(f"\n✨ All agents collaborated through shared memory!")


# =============================================================================
# MAIN: Run All Examples
# =============================================================================

def main():
    """Run all integration examples"""
    
    print("\n" + "🌟"*35)
    print(" "*20 + "CONFUCIUS AGENT")
    print(" "*15 + "Integration Examples")
    print("🌟"*35)
    
    try:
        # Example 1: Memory & Context
        example_1_memory_scaffolding()
        
        # Example 2: Ralph Loop
        example_2_ralph_loop()
        
        # Example 3: Custom Extensions
        example_3_custom_extensions()
        
        # Example 4: Multi-Agent
        example_4_multi_agent_collaboration()
        
        print("\n" + "="*70)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"\n📚 Key Takeaways:")
        print(f"   1. Use MemoryManager for context persistence")
        print(f"   2. Use RalphOrchestrator for autonomous iteration")
        print(f"   3. Build Extension classes for custom tools")
        print(f"   4. Share RunContext for multi-agent collaboration")
        print(f"\n🚀 Ready to build production agents with confucius-agent!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # First, verify the dependency is installed
    print("\n🔍 Checking confucius-agent installation...")
    
    try:
        import confucius_agent
        print(f"✅ confucius-agent v{confucius_agent.__version__} found\n")
    except ImportError:
        print("❌ confucius-agent not installed!")
        print("   Install with: pip install confucius-agent")
        print("   Or dev mode: pip install -e /path/to/confucius-agent")
        exit(1)
    
    # Run examples
    main()
