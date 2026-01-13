"""
Extension System - F3: Modular tool abstractions
Concrete implementations for coding tasks
"""

import subprocess
import os
from typing import List, Optional
from pathlib import Path
import tempfile
import re

from .orchestrator import Extension, Action, ActionType, RunContext, Message


class BashExtension(Extension):
    """
    Execute bash/shell commands with safety guardrails
    """
    
    def __init__(self, working_dir: Optional[str] = None, timeout: int = 30):
        super().__init__("bash")
        self.working_dir = working_dir or os.getcwd()
        self.timeout = timeout
        self.blocked_commands = ['rm -rf /', 'mkfs', 'dd if=']
    
    def can_handle(self, action: Action) -> bool:
        return action.type == ActionType.BASH_COMMAND
    
    def execute(self, action: Action, context: RunContext) -> Action:
        """Execute bash command with safety checks"""
        command = action.content.strip()
        
        # Safety check
        if any(blocked in command for blocked in self.blocked_commands):
            action.error = f"Blocked dangerous command: {command}"
            return action
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.working_dir
            )
            
            output = result.stdout + result.stderr
            action.result = output[:2000]  # Truncate long outputs
            
            if result.returncode != 0:
                action.error = f"Command failed with exit code {result.returncode}"
            
            # Store in context
            context.metadata['last_command'] = command
            context.metadata['last_exit_code'] = result.returncode
            
        except subprocess.TimeoutExpired:
            action.error = f"Command timed out after {self.timeout}s"
        except Exception as e:
            action.error = f"Execution error: {str(e)}"
        
        return action


class FileEditExtension(Extension):
    """
    Edit files with various operations (create, edit, append, delete)
    """
    
    def __init__(self, workspace_root: str):
        super().__init__("file_edit")
        self.workspace_root = Path(workspace_root)
    
    def can_handle(self, action: Action) -> bool:
        return action.type == ActionType.FILE_EDIT
    
    def execute(self, action: Action, context: RunContext) -> Action:
        """Execute file edit operation"""
        file_path = action.metadata.get('path', '')
        if not file_path:
            action.error = "No file path specified"
            return action
        
        full_path = self.workspace_root / file_path
        
        # Ensure file is within workspace
        try:
            full_path.resolve().relative_to(self.workspace_root.resolve())
        except ValueError:
            action.error = f"File path outside workspace: {file_path}"
            return action
        
        # Determine operation
        operation = action.metadata.get('operation', 'write')
        
        try:
            if operation == 'create' or operation == 'write':
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(action.content, encoding='utf-8')
                action.result = f"File written successfully: {file_path}"
            
            elif operation == 'append':
                with open(full_path, 'a', encoding='utf-8') as f:
                    f.write(action.content)
                action.result = f"Content appended to: {file_path}"
            
            elif operation == 'delete':
                if full_path.exists():
                    full_path.unlink()
                    action.result = f"File deleted: {file_path}"
                else:
                    action.error = f"File not found: {file_path}"
            
            elif operation == 'patch':
                # Apply patch-style edit
                self._apply_patch(full_path, action.content)
                action.result = f"Patch applied to: {file_path}"
            
            else:
                action.error = f"Unknown operation: {operation}"
        
        except Exception as e:
            action.error = f"File operation failed: {str(e)}"
        
        return action
    
    def _apply_patch(self, file_path: Path, patch_content: str):
        """Apply a search-replace patch"""
        if not file_path.exists():
            raise FileNotFoundError(f"{file_path} does not exist")
        
        # Parse patch format: <<<SEARCH>>> ... <<<REPLACE>>> ...
        search_pattern = r'<<<SEARCH>>>(.*?)<<<REPLACE>>>(.*?)(?:<<<|$)'
        matches = re.finditer(search_pattern, patch_content, re.DOTALL)
        
        content = file_path.read_text(encoding='utf-8')
        
        for match in matches:
            search = match.group(1).strip()
            replace = match.group(2).strip()
            if search in content:
                content = content.replace(search, replace, 1)
        
        file_path.write_text(content, encoding='utf-8')


class FileReadExtension(Extension):
    """
    Read file contents
    """
    
    def __init__(self, workspace_root: str):
        super().__init__("file_read")
        self.workspace_root = Path(workspace_root)
    
    def can_handle(self, action: Action) -> bool:
        return action.type == ActionType.FILE_READ
    
    def execute(self, action: Action, context: RunContext) -> Action:
        """Read file contents"""
        file_path = action.content.strip()
        full_path = self.workspace_root / file_path
        
        # Security check
        try:
            full_path.resolve().relative_to(self.workspace_root.resolve())
        except ValueError:
            action.error = f"File path outside workspace: {file_path}"
            return action
        
        try:
            if not full_path.exists():
                action.error = f"File not found: {file_path}"
                return action
            
            content = full_path.read_text(encoding='utf-8')
            
            # Truncate very large files
            if len(content) > 10000:
                action.result = content[:10000] + f"\n\n[... truncated {len(content) - 10000} characters ...]"
            else:
                action.result = content
            
            # Store in context for future reference
            context.set_artifact(f"file:{file_path}", content)
        
        except Exception as e:
            action.error = f"Failed to read file: {str(e)}"
        
        return action


class FileSearchExtension(Extension):
    """
    Search for files or content within files
    """
    
    def __init__(self, workspace_root: str):
        super().__init__("file_search")
        self.workspace_root = Path(workspace_root)
    
    def can_handle(self, action: Action) -> bool:
        return action.type == ActionType.FILE_SEARCH
    
    def execute(self, action: Action, context: RunContext) -> Action:
        """Search for files or patterns"""
        pattern = action.metadata.get('pattern', action.content)
        search_type = action.metadata.get('search_type', 'filename')
        
        try:
            if search_type == 'filename':
                results = self._search_files(pattern)
            elif search_type == 'content':
                results = self._search_content(pattern)
            else:
                action.error = f"Unknown search type: {search_type}"
                return action
            
            if results:
                action.result = f"Found {len(results)} matches:\n" + "\n".join(results[:20])
            else:
                action.result = "No matches found"
        
        except Exception as e:
            action.error = f"Search failed: {str(e)}"
        
        return action
    
    def _search_files(self, pattern: str) -> List[str]:
        """Search for files matching pattern"""
        matches = []
        for file_path in self.workspace_root.rglob(pattern):
            if file_path.is_file():
                rel_path = file_path.relative_to(self.workspace_root)
                matches.append(str(rel_path))
        return matches
    
    def _search_content(self, pattern: str) -> List[str]:
        """Search for pattern in file contents (grep-like)"""
        matches = []
        for file_path in self.workspace_root.rglob('*.py'):  # For now, just Python files
            try:
                content = file_path.read_text(encoding='utf-8')
                if pattern in content:
                    rel_path = file_path.relative_to(self.workspace_root)
                    matches.append(str(rel_path))
            except:
                continue
        return matches


class ThinkingExtension(Extension):
    """
    Handle thinking/reasoning tags - doesn't execute, just logs
    """
    
    def __init__(self):
        super().__init__("thinking")
    
    def can_handle(self, action: Action) -> bool:
        return action.type == ActionType.THINKING
    
    def execute(self, action: Action, context: RunContext) -> Action:
        """Log thinking without executing anything"""
        # Store thinking in context for debugging
        thoughts = context.metadata.get('thoughts', [])
        thoughts.append(action.content)
        context.metadata['thoughts'] = thoughts
        
        action.result = "[Thinking logged]"
        return action


class PromptCacheExtension(Extension):
    """
    Add provider-specific caching hints to reduce latency
    """
    
    def __init__(self, provider: str = "anthropic"):
        super().__init__("prompt_cache")
        self.provider = provider
    
    def can_handle(self, action: Action) -> bool:
        return False  # This extension only modifies prompts
    
    def execute(self, action: Action, context: RunContext) -> Action:
        return action
    
    def on_input_messages(self, messages: List[Message], context: RunContext) -> List[Message]:
        """Add cache control hints to system messages"""
        if self.provider == "anthropic":
            for msg in messages:
                if msg.role == "system" and len(msg.content) > 1000:
                    # Mark long system messages for caching
                    msg.metadata['cache_control'] = {'type': 'ephemeral'}
        
        return messages


class PlanningExtension(Extension):
    """
    Add planning/task decomposition before executing
    """
    
    def __init__(self):
        super().__init__("planning")
    
    def can_handle(self, action: Action) -> bool:
        return False  # This extension only modifies prompts
    
    def execute(self, action: Action, context: RunContext) -> Action:
        return action
    
    def on_input_messages(self, messages: List[Message], context: RunContext) -> List[Message]:
        """Inject planning instructions"""
        # If this is the first user message, add planning guidance
        if len(messages) <= 2:  # system + first user message
            planning_msg = Message(
                role="system",
                content=(
                    "Before taking action:\n"
                    "1. Break down the task into steps\n"
                    "2. Identify files/commands needed\n"
                    "3. Consider potential errors\n"
                    "4. Execute step by step\n"
                )
            )
            messages.insert(1, planning_msg)
        
        return messages


# Export all extensions
__all__ = [
    'BashExtension',
    'FileEditExtension',
    'FileReadExtension',
    'FileSearchExtension',
    'ThinkingExtension',
    'PromptCacheExtension',
    'PlanningExtension'
]
