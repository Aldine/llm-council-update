"""
Subagent Extension - Isolated agent spawning for delegation
Adds true subagent capability to Confucius Agent SDK
"""

import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field

from .orchestrator import (
    Extension,
    Action,
    ActionType,
    RunContext,
    Orchestrator,
    MemoryManager
)


@dataclass
class SubagentCall:
    """Traceable subagent invocation record"""
    name: str                           # Subagent name (Scout, Builder, etc.)
    input_summary: str                  # Task delegated (truncated)
    output_summary: str                 # Result returned (truncated)
    full_output: str                    # Complete output for merging
    timestamp: float                    # Unix timestamp
    call_index: int                     # Sequential call number
    iteration: int                      # Parent iteration when called
    actions_taken: List[str]            # Extension types used
    memory_snapshot: Dict[str, Any]     # Metadata (iterations, success, etc.)
    status: str                         # "success", "failed", "timeout"
    duration_ms: int                    # Execution time


class SubagentExtension(Extension):
    """
    Extension that spawns isolated subagents for delegation
    
    Usage in agent prompt:
        <subagent name="Scout">
        Extract computed colors from 6 UI elements:
        - body text
        - h1 heading
        ...
        Return a structured JSON with foreground/background colors.
        </subagent>
    
    The extension:
    1. Parses <subagent> tags from LLM output
    2. Spawns isolated orchestrator with fresh memory
    3. Runs subagent with limited iterations
    4. Records call trace for verification
    5. Returns result to parent agent
    """
    
    def __init__(
        self,
        llm_client: Callable,
        available_extensions: List[Extension],
        max_depth: int = 2,
        max_subagent_iterations: int = 10,
        verbose: bool = True
    ):
        super().__init__("subagent")
        self.llm_client = llm_client
        self.available_extensions = available_extensions
        self.max_depth = max_depth
        self.max_subagent_iterations = max_subagent_iterations
        self.verbose = verbose
        
        # Trace for verification
        self.call_trace: List[SubagentCall] = []
        self.current_depth = 0
    
    def can_handle(self, action: Action) -> bool:
        """Check if action is a subagent delegation"""
        # We don't handle parsed actions directly
        # Instead, we hook into on_llm_output to parse <subagent> tags
        return False
    
    def execute(self, action: Action, context: RunContext) -> Action:
        """Not used - we intercept via on_llm_output"""
        return action
    
    def on_llm_output(self, output: str, context: RunContext) -> str:
        """
        Hook called after LLM generates output
        Parse and execute any <subagent> tags
        """
        import re
        
        # Find all subagent tags
        pattern = r'<subagent\s+name="([^"]+)">(.*?)</subagent>'
        matches = list(re.finditer(pattern, output, re.DOTALL))
        
        if not matches:
            return output
        
        # Check depth limit
        if self.current_depth >= self.max_depth:
            return output.replace(
                matches[0].group(0),
                f"[ERROR: Subagent depth limit reached ({self.max_depth})]"
            )
        
        # Execute each subagent and replace tag with result
        modified_output = output
        for match in matches:
            subagent_name = match.group(1)
            subagent_task = match.group(2).strip()
            
            # Spawn subagent
            call_record = self._spawn_subagent(
                name=subagent_name,
                task=subagent_task,
                parent_context=context
            )
            
            # Replace tag with result
            result_block = self._format_result(call_record)
            modified_output = modified_output.replace(
                match.group(0),
                result_block
            )
        
        return modified_output
    
    def _spawn_subagent(
        self,
        name: str,
        task: str,
        parent_context: RunContext
    ) -> SubagentCall:
        """Spawn isolated subagent and record call"""
        
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"🤖 SPAWNING SUBAGENT: {name}")
            print(f"{'='*70}")
            print(f"Task: {task[:100]}...")
        
        start_time = time.time()
        
        # Create isolated memory (no access to parent memory)
        sub_memory = MemoryManager()
        
        # Create subagent orchestrator with filtered extensions
        # (exclude SubagentExtension to prevent recursive spawning at depth)
        sub_extensions = [
            ext for ext in self.available_extensions
            if not isinstance(ext, SubagentExtension)
        ]
        
        sub_orchestrator = Orchestrator(
            llm_client=self.llm_client,
            extensions=sub_extensions,
            memory_manager=sub_memory,
            max_iterations=self.max_subagent_iterations,
            system_prompt=f"You are {name}, a specialized subagent."
        )
        
        # Increment depth
        self.current_depth += 1
        
        try:
            # Run subagent
            result = sub_orchestrator.run(task)
            
            status = "success" if result['success'] else "failed"
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Create call record
            call = SubagentCall(
                name=name,
                input_summary=task[:150],
                output_summary=result['final_output'][:200],
                full_output=result['final_output'],
                timestamp=start_time,
                call_index=len(self.call_trace),
                iteration=parent_context.metadata.get('current_iteration', 0),
                actions_taken=[a['type'] for a in result.get('actions', [])],
                memory_snapshot={
                    'iterations': result.get('iterations', 0),
                    'success': result.get('success', False),
                    'action_count': len(result.get('actions', []))
                },
                status=status,
                duration_ms=duration_ms
            )
            
            self.call_trace.append(call)
            
            if self.verbose:
                print(f"\n✓ Subagent {name} completed:")
                print(f"  Status: {status}")
                print(f"  Iterations: {result['iterations']}")
                print(f"  Actions: {len(result['actions'])}")
                print(f"  Duration: {duration_ms}ms")
            
            return call
            
        except Exception as e:
            # Handle errors
            duration_ms = int((time.time() - start_time) * 1000)
            call = SubagentCall(
                name=name,
                input_summary=task[:150],
                output_summary=f"ERROR: {str(e)[:100]}",
                full_output=f"Subagent failed with error: {str(e)}",
                timestamp=start_time,
                call_index=len(self.call_trace),
                iteration=parent_context.metadata.get('current_iteration', 0),
                actions_taken=[],
                memory_snapshot={'error': str(e)},
                status="error",
                duration_ms=duration_ms
            )
            self.call_trace.append(call)
            
            if self.verbose:
                print(f"\n✗ Subagent {name} failed: {str(e)}")
            
            return call
            
        finally:
            # Decrement depth
            self.current_depth -= 1
    
    def _format_result(self, call: SubagentCall) -> str:
        """Format subagent result for insertion into parent output"""
        return f"""<subagent_result name="{call.name}" call_index="{call.call_index}">
{call.full_output}
</subagent_result>"""
    
    def get_trace_summary(self) -> str:
        """Generate formatted trace for verification"""
        if not self.call_trace:
            return "No subagent calls recorded."
        
        lines = ["Subagent Trace:", "=" * 70]
        
        for call in self.call_trace:
            lines.append(f"\n[{call.call_index}] {call.name}")
            lines.append(f"    Task: {call.input_summary}")
            lines.append(f"    Actions: {call.actions_taken}")
            lines.append(f"    Output: {call.output_summary}")
            lines.append(f"    Timestamp: {call.timestamp}")
            lines.append(f"    Duration: {call.duration_ms}ms")
            lines.append(f"    Status: {call.status} {'✓' if call.status == 'success' else '✗'}")
        
        return "\n".join(lines)
    
    def clear_trace(self):
        """Clear call trace (for new session)"""
        self.call_trace = []
        self.current_depth = 0


def create_subagent_enabled_agent(
    llm_client: Callable,
    workspace: str = ".",
    enable_subagents: bool = True,
    **kwargs
) -> 'RalphOrchestrator':
    """
    Factory to create agent with subagent support
    
    Usage:
        agent = create_subagent_enabled_agent(
            llm_client=create_llm_client("gpt-4"),
            workspace="./my-project",
            enable_subagents=True
        )
        
        result = agent.run_ralph_loop("Audit accessibility")
        
        # Get subagent trace
        for ext in agent.orchestrator.extensions:
            if isinstance(ext, SubagentExtension):
                print(ext.get_trace_summary())
    """
    from .extensions import get_default_extensions
    from .ralph_integration import RalphOrchestrator, RalphLoopConfig
    
    # Get default extensions
    extensions = get_default_extensions(workspace)
    
    # Add SubagentExtension if enabled
    if enable_subagents:
        subagent_ext = SubagentExtension(
            llm_client=llm_client,
            available_extensions=extensions,
            max_depth=kwargs.get('subagent_max_depth', 2),
            max_subagent_iterations=kwargs.get('subagent_max_iterations', 10),
            verbose=kwargs.get('verbose', True)
        )
        extensions.append(subagent_ext)
    
    # Create config
    config = RalphLoopConfig(
        completion_promise=kwargs.get('completion_promise', 'TASK_COMPLETE'),
        max_iterations=kwargs.get('max_iterations', 20),
        enable_notes=kwargs.get('enable_notes', True),
        verbose=kwargs.get('verbose', True)
    )
    
    # Create orchestrator
    return RalphOrchestrator(
        llm_client=llm_client,
        extensions=extensions,
        config=config,
        system_prompt=kwargs.get('system_prompt', '')
    )


__all__ = [
    'SubagentCall',
    'SubagentExtension',
    'create_subagent_enabled_agent'
]
