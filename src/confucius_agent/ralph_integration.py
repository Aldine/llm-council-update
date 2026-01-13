"""
Ralph Loop Integration with Confucius Orchestrator
Combines autonomous iteration with structured agent scaffolding
"""

import time
from typing import Callable, Dict, Any, Optional
from pathlib import Path

from .orchestrator import Orchestrator, MemoryManager, Extension
from .notes import NoteStore, NoteTakingAgent


class RalphLoopConfig:
    """Configuration for Ralph loop behavior"""
    
    def __init__(
        self,
        completion_promise: str = "TASK_COMPLETE",
        max_iterations: int = 20,
        delay_seconds: int = 2,
        enable_notes: bool = True,
        notes_path: Optional[str] = None,
        verbose: bool = True
    ):
        self.completion_promise = completion_promise
        self.max_iterations = max_iterations
        self.delay_seconds = delay_seconds
        self.enable_notes = enable_notes
        self.notes_path = notes_path or "./notes"
        self.verbose = verbose


class RalphOrchestrator:
    """
    Enhanced orchestrator combining Ralph loop pattern with Confucius scaffolding
    
    This integrates:
    - Ralph Wiggum's autonomous iteration until completion
    - Confucius's hierarchical memory and context compression
    - Note-taking for persistent learning
    - Extension system for modular tools
    """
    
    def __init__(
        self,
        llm_client: Callable,
        extensions: list[Extension],
        config: RalphLoopConfig,
        system_prompt: str = ""
    ):
        self.config = config
        self.llm_client = llm_client
        
        # Initialize Confucius components
        self.memory_manager = MemoryManager()
        self.orchestrator = Orchestrator(
            llm_client=llm_client,
            extensions=extensions,
            memory_manager=self.memory_manager,
            max_iterations=config.max_iterations,
            system_prompt=system_prompt
        )
        
        # Initialize note-taking if enabled
        self.note_store = None
        self.note_agent = None
        if config.enable_notes:
            self.note_store = NoteStore(Path(config.notes_path))
            self.note_agent = NoteTakingAgent(self.note_store)
    
    def run_ralph_loop(self, task: str) -> Dict[str, Any]:
        """
        Execute task with Ralph loop pattern:
        - Iterate until completion promise found or max iterations reached
        - Store trajectory and create notes
        - Return comprehensive results
        """
        iteration = 0
        completed = False
        trajectory = []
        
        print("🎭 Ralph Loop + Confucius Orchestrator Starting...")
        print(f"Task: {task}")
        print(f"Completion Promise: '{self.config.completion_promise}'")
        print(f"Max Iterations: {self.config.max_iterations}")
        print("=" * 70)
        
        while iteration < self.config.max_iterations and not completed:
            iteration += 1
            
            if self.config.verbose:
                print(f"\n{'='*70}")
                print(f"[RALPH ITERATION {iteration}/{self.config.max_iterations}]")
                print(f"{'='*70}")
            
            # Execute one orchestrator run
            result = self.orchestrator.run(task)
            
            # Log to trajectory
            trajectory.append({
                'iteration': iteration,
                'result': result,
                'timestamp': time.time()
            })
            
            # Check for completion promise in output
            final_output = result.get('final_output', '')
            if self.config.completion_promise in final_output:
                completed = True
                if self.config.verbose:
                    print(f"\n✅ Completion promise found: '{self.config.completion_promise}'")
                    print(f"Task completed after {iteration} Ralph iterations!")
                break
            
            # Check if orchestrator signaled completion
            if result.get('success', False):
                completed = True
                if self.config.verbose:
                    print(f"\n✅ Orchestrator signaled completion")
                break
            
            # Delay before next iteration
            if iteration < self.config.max_iterations:
                if self.config.verbose:
                    print(f"\n⏳ Waiting {self.config.delay_seconds}s before next iteration...")
                time.sleep(self.config.delay_seconds)
        
        print("\n" + "=" * 70)
        
        # Distill trajectory into notes
        notes_created = []
        if self.config.enable_notes and self.note_agent:
            session_id = f"ralph_session_{int(time.time())}"
            outcome = "completed" if completed else "max_iterations_reached"
            notes_created = self.note_agent.distill_session(
                session_id, trajectory, outcome
            )
            
            if self.config.verbose:
                print(f"\n📝 Created {len(notes_created)} notes in {self.config.notes_path}")
        
        # Final results
        final_result = {
            'success': completed,
            'ralph_iterations': iteration,
            'total_orchestrator_iterations': sum(
                r['result'].get('iterations', 0) for r in trajectory
            ),
            'completion_promise_found': completed,
            'trajectory': trajectory,
            'notes_created': [n.path for n in notes_created],
            'memory_hierarchy': self.memory_manager.hierarchy
        }
        
        if completed:
            print("🎉 Ralph Loop Completed Successfully!")
        else:
            print(f"⚠️  Ralph Loop stopped after {self.config.max_iterations} iterations")
            print(f"   Completion promise '{self.config.completion_promise}' not found")
        
        print(f"\nTotal Ralph iterations: {iteration}")
        print(f"Total orchestrator iterations: {final_result['total_orchestrator_iterations']}")
        
        return final_result
    
    def check_past_failures(self, error_message: str) -> list:
        """
        Check note store for similar past failures
        Key feature from F2: Learn from hindsight notes
        """
        if not self.note_store:
            return []
        
        return self.note_store.search_failures(error_message)
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of current memory state"""
        return {
            'message_count': len(self.memory_manager.messages),
            'estimated_tokens': self.memory_manager._estimate_tokens(),
            'hierarchy': self.memory_manager.hierarchy,
            'compressed_messages': sum(
                1 for msg in self.memory_manager.messages if msg.compressed
            )
        }


def create_coding_agent(
    llm_client: Callable,
    workspace_root: str,
    ralph_config: Optional[RalphLoopConfig] = None
) -> RalphOrchestrator:
    """
    Factory function to create a complete coding agent
    Combines all components like the Confucius Code Agent
    """
    from .extensions import (
        BashExtension,
        FileEditExtension,
        FileReadExtension,
        FileSearchExtension,
        ThinkingExtension,
        PlanningExtension
    )
    
    # Default Ralph config
    if ralph_config is None:
        ralph_config = RalphLoopConfig()
    
    # Create extensions bundle
    extensions = [
        PlanningExtension(),
        BashExtension(working_dir=workspace_root),
        FileEditExtension(workspace_root=workspace_root),
        FileReadExtension(workspace_root=workspace_root),
        FileSearchExtension(workspace_root=workspace_root),
        ThinkingExtension()
    ]
    
    # System prompt for coding tasks
    system_prompt = """You are an expert software engineering agent.

Your capabilities:
- <bash>command</bash> - Execute shell commands
- <file_edit path="file.py">content</file_edit> - Edit/create files
- <file_read>path/to/file</file_read> - Read file contents
- <search pattern="*.py"> - Search for files
- <thinking>reasoning</thinking> - Internal reasoning (not executed)

When you complete the task, include the completion signal in your response.

Work step-by-step:
1. Understand the task and plan your approach
2. Execute necessary actions (read files, run tests, edit code)
3. Verify your changes work
4. Signal completion when done"""
    
    return RalphOrchestrator(
        llm_client=llm_client,
        extensions=extensions,
        config=ralph_config,
        system_prompt=system_prompt
    )


# Export
__all__ = ['RalphLoopConfig', 'RalphOrchestrator', 'create_coding_agent']
