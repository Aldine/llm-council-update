"""
Confucius-inspired Agent Orchestrator
A clean implementation of the orchestration pattern from the Confucius Code Agent paper.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from abc import ABC, abstractmethod


class ActionType(Enum):
    """Types of actions an agent can take"""
    BASH_COMMAND = "bash"
    FILE_EDIT = "file_edit"
    FILE_READ = "file_read"
    FILE_SEARCH = "file_search"
    THINKING = "thinking"
    COMPLETION = "completion"


@dataclass
class Action:
    """Represents a single agent action"""
    type: ActionType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    result: Optional[str] = None
    error: Optional[str] = None


@dataclass
class Message:
    """Represents a message in the conversation"""
    role: str  # "user", "assistant", "system"
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    compressed: bool = False


class Extension(ABC):
    """Base class for modular extensions"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def can_handle(self, action: Action) -> bool:
        """Check if this extension can handle the action"""
        pass
    
    @abstractmethod
    def execute(self, action: Action, context: 'RunContext') -> Action:
        """Execute the action and return updated action with results"""
        pass
    
    def on_input_messages(self, messages: List[Message], context: 'RunContext') -> List[Message]:
        """Hook called before messages are sent to LLM"""
        return messages
    
    def on_llm_output(self, output: str, context: 'RunContext') -> str:
        """Hook called after LLM generates output"""
        return output


@dataclass
class RunContext:
    """Shared context passed to extensions"""
    session_id: str
    memory_manager: 'MemoryManager'
    artifact_store: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_artifact(self, key: str) -> Any:
        return self.artifact_store.get(key)
    
    def set_artifact(self, key: str, value: Any):
        self.artifact_store[key] = value


class MemoryManager:
    """
    Hierarchical working memory manager
    Implements F1: Context Management from the paper
    """
    
    def __init__(self, max_tokens: int = 100000, compression_threshold: float = 0.8):
        self.messages: List[Message] = []
        self.max_tokens = max_tokens
        self.compression_threshold = compression_threshold
        self.hierarchy = {
            'session': {},
            'entry': {},
            'runnable': {}
        }
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to working memory"""
        msg = Message(
            role=role,
            content=content,
            metadata=metadata or {},
            compressed=False
        )
        self.messages.append(msg)
        
        # Check if compression needed
        if self._estimate_tokens() > self.max_tokens * self.compression_threshold:
            self._compress_history()
    
    def get_messages(self) -> List[Message]:
        """Get all messages for LLM prompt"""
        return self.messages
    
    def store_in_hierarchy(self, scope: str, key: str, value: Any):
        """Store data in hierarchical memory"""
        if scope in self.hierarchy:
            self.hierarchy[scope][key] = value
    
    def get_from_hierarchy(self, scope: str, key: str) -> Any:
        """Retrieve data from hierarchical memory"""
        return self.hierarchy.get(scope, {}).get(key)
    
    def _estimate_tokens(self) -> int:
        """Rough token estimation (4 chars ≈ 1 token)"""
        total_chars = sum(len(msg.content) for msg in self.messages)
        return total_chars // 4
    
    def _compress_history(self):
        """
        Compress older messages while keeping recent ones
        Implements adaptive context compression from F1
        """
        if len(self.messages) < 10:
            return
        
        # Keep last 5 messages untouched
        recent_messages = self.messages[-5:]
        older_messages = self.messages[:-5]
        
        # Create structured summary of older messages
        summary = self._create_summary(older_messages)
        
        # Replace older messages with compressed summary
        summary_msg = Message(
            role="assistant",
            content=f"[COMPRESSED CONTEXT]\n{summary}",
            metadata={"compressed": True, "original_count": len(older_messages)},
            compressed=True
        )
        
        self.messages = [summary_msg] + recent_messages
    
    def _create_summary(self, messages: List[Message]) -> str:
        """Create structured summary of messages"""
        # In production, this would call an "Architect" agent
        # For now, we do simple extraction
        
        actions_taken = []
        errors = []
        decisions = []
        
        for msg in messages:
            if msg.role == "assistant":
                # Extract actions
                if "bash" in msg.content.lower() or "file" in msg.content.lower():
                    actions_taken.append(msg.content[:200])
            if "error" in msg.content.lower() or "failed" in msg.content.lower():
                errors.append(msg.content[:150])
        
        summary = "## Session Summary\n\n"
        if actions_taken:
            summary += "### Actions Taken:\n" + "\n".join(f"- {a}" for a in actions_taken[:5]) + "\n\n"
        if errors:
            summary += "### Errors Encountered:\n" + "\n".join(f"- {e}" for e in errors[:3]) + "\n\n"
        
        return summary


class Orchestrator:
    """
    Main agent orchestrator implementing Algorithm 1 from the paper
    Coordinates LLM calls, action parsing, and extension execution
    """
    
    def __init__(
        self,
        llm_client: Callable,
        extensions: List[Extension],
        memory_manager: Optional[MemoryManager] = None,
        max_iterations: int = 50,
        system_prompt: str = ""
    ):
        self.llm_client = llm_client
        self.extensions = extensions
        self.memory_manager = memory_manager or MemoryManager()
        self.max_iterations = max_iterations
        self.system_prompt = system_prompt
        self.context = RunContext(
            session_id="session_0",
            memory_manager=self.memory_manager
        )
    
    def run(self, initial_prompt: str) -> Dict[str, Any]:
        """
        Main orchestration loop (Algorithm 1)
        """
        # Initialize
        self.memory_manager.add_message("user", initial_prompt)
        iteration = 0
        completed = False
        
        results = {
            "success": False,
            "iterations": 0,
            "final_output": "",
            "actions": []
        }
        
        while iteration < self.max_iterations and not completed:
            iteration += 1
            print(f"\n{'='*60}")
            print(f"[Iteration {iteration}/{self.max_iterations}]")
            print(f"{'='*60}")
            
            # Step 3: Invoke LLM
            messages = self._prepare_messages()
            llm_output = self._call_llm(messages)
            
            # Step 4: Parse LLM output into actions
            actions = self._parse_actions(llm_output)
            
            if not actions:
                # No actions = completion signal
                print("✓ Agent signaled completion (no further actions)")
                completed = True
                results["final_output"] = llm_output
                break
            
            # Step 5-12: Execute actions
            for action in actions:
                print(f"\n[Action: {action.type.value}]")
                
                # Step 6: Route to extension
                executed = self._execute_action(action)
                results["actions"].append({
                    "type": action.type.value,
                    "success": executed.error is None
                })
                
                # Step 7: Update memory with results
                if executed.result:
                    self.memory_manager.add_message(
                        "user",
                        f"<result>{executed.result}</result>"
                    )
                elif executed.error:
                    self.memory_manager.add_message(
                        "user",
                        f"<error>{executed.error}</error>"
                    )
                
                # Step 8-10: Check for continuation
                if action.type == ActionType.COMPLETION:
                    completed = True
                    results["final_output"] = action.content
                    break
            
            # Step 13: Check for completion
            if self._check_completion(llm_output):
                completed = True
                results["final_output"] = llm_output
        
        results["success"] = completed
        results["iterations"] = iteration
        
        return results
    
    def _prepare_messages(self) -> List[Dict]:
        """Prepare messages for LLM with extension hooks"""
        messages = self.memory_manager.get_messages()
        
        # Apply extension hooks
        for ext in self.extensions:
            messages = ext.on_input_messages(messages, self.context)
        
        # Format for LLM
        formatted = []
        if self.system_prompt:
            formatted.append({"role": "system", "content": self.system_prompt})
        
        for msg in messages:
            formatted.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return formatted
    
    def _call_llm(self, messages: List[Dict]) -> str:
        """Call LLM and get response"""
        # This is a placeholder - in production, would call actual LLM API
        # For now, return mock response
        output = self.llm_client(messages)
        
        # Apply extension hooks
        for ext in self.extensions:
            output = ext.on_llm_output(output, self.context)
        
        # Store in memory
        self.memory_manager.add_message("assistant", output)
        
        return output
    
    def _parse_actions(self, output: str) -> List[Action]:
        """
        Parse LLM output into structured actions
        Supports both XML tags and native tool calls
        """
        actions = []
        
        # Parse XML-style tags (for models without native tool use)
        tag_patterns = {
            ActionType.BASH_COMMAND: r'<bash>(.*?)</bash>',
            ActionType.FILE_EDIT: r'<file_edit\s+path="([^"]+)">(.*?)</file_edit>',
            ActionType.FILE_READ: r'<file_read>(.*?)</file_read>',
            ActionType.FILE_SEARCH: r'<search\s+pattern="([^"]+)">',
            ActionType.THINKING: r'<thinking>(.*?)</thinking>',
        }
        
        for action_type, pattern in tag_patterns.items():
            matches = re.finditer(pattern, output, re.DOTALL)
            for match in matches:
                if action_type == ActionType.FILE_EDIT:
                    actions.append(Action(
                        type=action_type,
                        content=match.group(2).strip(),
                        metadata={"path": match.group(1)}
                    ))
                else:
                    actions.append(Action(
                        type=action_type,
                        content=match.group(1).strip()
                    ))
        
        # Check for completion signals
        if any(phrase in output.lower() for phrase in ["task complete", "finished", "done with task"]):
            actions.append(Action(
                type=ActionType.COMPLETION,
                content=output
            ))
        
        return actions
    
    def _execute_action(self, action: Action) -> Action:
        """Execute action by routing to appropriate extension"""
        for ext in self.extensions:
            if ext.can_handle(action):
                print(f"  → Handling with {ext.name}")
                return ext.execute(action, self.context)
        
        # No handler found
        action.error = f"No extension found to handle {action.type}"
        print(f"  ⚠ {action.error}")
        return action
    
    def _check_completion(self, output: str) -> bool:
        """Check if agent signals completion"""
        completion_signals = [
            "task complete",
            "finished successfully",
            "done with all steps",
            "no further actions needed"
        ]
        return any(signal in output.lower() for signal in completion_signals)


# Export main classes
__all__ = [
    'Orchestrator',
    'Extension',
    'Action',
    'ActionType',
    'Message',
    'MemoryManager',
    'RunContext'
]
