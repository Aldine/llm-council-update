"""
Note-Taking Agent Module
Implements F2: Persistent note storage with hindsight for failures
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import json
from datetime import datetime
from enum import Enum


class NoteType(Enum):
    """Types of notes that can be stored"""
    ARCHITECTURE = "architecture"
    DECISION = "decision"
    SOLUTION = "solution"
    FAILURE = "failure"  # Hindsight notes
    RESEARCH = "research"
    FINDING = "finding"
    PATTERN = "pattern"


@dataclass
class Note:
    """Represents a single note"""
    title: str
    content: str
    note_type: NoteType
    path: str
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_markdown(self) -> str:
        """Convert note to Markdown format"""
        md = f"# {self.title}\n\n"
        md += f"**Type:** {self.note_type.value}  \n"
        md += f"**Created:** {self.created_at}  \n"
        md += f"**Updated:** {self.updated_at}  \n"
        
        if self.tags:
            md += f"**Tags:** {', '.join(self.tags)}  \n"
        
        md += "\n---\n\n"
        md += self.content
        md += "\n\n---\n\n"
        
        if self.metadata:
            md += "## Metadata\n\n"
            md += "```json\n"
            md += json.dumps(self.metadata, indent=2)
            md += "\n```\n"
        
        return md
    
    @classmethod
    def from_markdown(cls, path: str, content: str) -> 'Note':
        """Parse note from Markdown content"""
        lines = content.split('\n')
        title = ""
        note_type = NoteType.FINDING
        tags = []
        metadata = {}
        created_at = datetime.now().isoformat()
        updated_at = created_at
        
        # Parse frontmatter
        for line in lines[:10]:
            if line.startswith('# '):
                title = line[2:].strip()
            elif '**Type:**' in line:
                type_str = line.split('**Type:**')[1].strip()
                try:
                    note_type = NoteType(type_str)
                except ValueError:
                    pass
            elif '**Tags:**' in line:
                tags_str = line.split('**Tags:**')[1].strip()
                tags = [t.strip() for t in tags_str.split(',')]
            elif '**Created:**' in line:
                created_at = line.split('**Created:**')[1].strip()
            elif '**Updated:**' in line:
                updated_at = line.split('**Updated:**')[1].strip()
        
        # Extract main content (between first --- and second ---)
        content_parts = content.split('---')
        main_content = content_parts[1].strip() if len(content_parts) > 1 else content
        
        return cls(
            title=title,
            content=main_content,
            note_type=note_type,
            path=path,
            tags=tags,
            metadata=metadata,
            created_at=created_at,
            updated_at=updated_at
        )


@dataclass
class HindsightNote(Note):
    """
    Special note type for capturing failures and their resolutions
    Key feature from F2 in the paper
    """
    error_message: str = ""
    stack_trace: str = ""
    attempted_solutions: List[str] = field(default_factory=list)
    resolution: Optional[str] = None
    prevention_tips: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.note_type = NoteType.FAILURE
        self.tags = self.tags + ["failure", "hindsight"]
    
    def to_markdown(self) -> str:
        """Enhanced Markdown with failure-specific sections"""
        md = f"# {self.title}\n\n"
        md += f"**Type:** {self.note_type.value} (Hindsight)  \n"
        md += f"**Created:** {self.created_at}  \n"
        md += f"**Tags:** {', '.join(self.tags)}  \n"
        md += "\n---\n\n"
        
        md += "## Problem Description\n\n"
        md += self.content + "\n\n"
        
        if self.error_message:
            md += "## Error Message\n\n"
            md += f"```\n{self.error_message}\n```\n\n"
        
        if self.stack_trace:
            md += "## Stack Trace\n\n"
            md += f"```\n{self.stack_trace}\n```\n\n"
        
        if self.attempted_solutions:
            md += "## Attempted Solutions\n\n"
            for i, solution in enumerate(self.attempted_solutions, 1):
                md += f"{i}. {solution}\n"
            md += "\n"
        
        if self.resolution:
            md += "## Resolution\n\n"
            md += self.resolution + "\n\n"
        
        if self.prevention_tips:
            md += "## Prevention Tips\n\n"
            for tip in self.prevention_tips:
                md += f"- {tip}\n"
            md += "\n"
        
        return md


class NoteStore:
    """
    File-system-based hierarchical note storage
    Implements persistent memory from F2
    """
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.index: Dict[str, Note] = {}
        self._load_index()
    
    def create_note(
        self,
        path: str,
        title: str,
        content: str,
        note_type: NoteType = NoteType.FINDING,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> Note:
        """Create a new note"""
        note = Note(
            title=title,
            content=content,
            note_type=note_type,
            path=path,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        self._write_note(note)
        self.index[path] = note
        return note
    
    def create_hindsight_note(
        self,
        path: str,
        title: str,
        problem_description: str,
        error_message: str = "",
        stack_trace: str = "",
        attempted_solutions: Optional[List[str]] = None,
        resolution: Optional[str] = None
    ) -> HindsightNote:
        """Create a hindsight note for a failure"""
        note = HindsightNote(
            title=title,
            content=problem_description,
            note_type=NoteType.FAILURE,
            path=path,
            tags=["failure", "hindsight"],
            error_message=error_message,
            stack_trace=stack_trace,
            attempted_solutions=attempted_solutions or [],
            resolution=resolution
        )
        
        self._write_note(note)
        self.index[path] = note
        return note
    
    def read_note(self, path: str) -> Optional[Note]:
        """Read a note by path"""
        if path in self.index:
            return self.index[path]
        
        file_path = self._get_file_path(path)
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            note = Note.from_markdown(path, content)
            self.index[path] = note
            return note
        
        return None
    
    def update_note(self, path: str, content: str) -> Optional[Note]:
        """Update an existing note"""
        note = self.read_note(path)
        if not note:
            return None
        
        note.content = content
        note.updated_at = datetime.now().isoformat()
        self._write_note(note)
        return note
    
    def delete_note(self, path: str) -> bool:
        """Delete a note"""
        file_path = self._get_file_path(path)
        if file_path.exists():
            file_path.unlink()
            if path in self.index:
                del self.index[path]
            return True
        return False
    
    def search_notes(
        self,
        query: str = "",
        note_type: Optional[NoteType] = None,
        tags: Optional[List[str]] = None
    ) -> List[Note]:
        """Search notes by query, type, or tags"""
        results = []
        
        for note in self.index.values():
            # Filter by type
            if note_type and note.note_type != note_type:
                continue
            
            # Filter by tags
            if tags and not any(tag in note.tags for tag in tags):
                continue
            
            # Filter by query (search in title and content)
            if query:
                search_text = f"{note.title} {note.content}".lower()
                if query.lower() not in search_text:
                    continue
            
            results.append(note)
        
        return results
    
    def search_failures(self, error_pattern: str) -> List[HindsightNote]:
        """
        Search for hindsight notes matching an error pattern
        Key feature for learning from past failures
        """
        failures = self.search_notes(note_type=NoteType.FAILURE)
        matching = []
        
        for note in failures:
            if isinstance(note, HindsightNote):
                search_in = f"{note.error_message} {note.stack_trace}".lower()
                if error_pattern.lower() in search_in:
                    matching.append(note)
        
        return matching
    
    def list_all_paths(self) -> List[str]:
        """List all note paths"""
        return list(self.index.keys())
    
    def get_hierarchy(self) -> Dict[str, Any]:
        """Get hierarchical view of notes"""
        hierarchy = {}
        
        for path in self.index.keys():
            parts = path.split('/')
            current = hierarchy
            
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Leaf node
            current[parts[-1]] = self.index[path]
        
        return hierarchy
    
    def _get_file_path(self, note_path: str) -> Path:
        """Convert note path to file system path"""
        # Ensure .md extension
        if not note_path.endswith('.md'):
            note_path += '.md'
        return self.base_path / note_path
    
    def _write_note(self, note: Note):
        """Write note to disk"""
        file_path = self._get_file_path(note.path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(note.to_markdown(), encoding='utf-8')
    
    def _load_index(self):
        """Load all existing notes into index"""
        for md_file in self.base_path.rglob('*.md'):
            rel_path = str(md_file.relative_to(self.base_path))
            content = md_file.read_text(encoding='utf-8')
            note = Note.from_markdown(rel_path, content)
            self.index[rel_path] = note


class NoteTakingAgent:
    """
    Agent that distills trajectories into structured notes
    Implements F2 note-taking from the paper
    """
    
    def __init__(self, note_store: NoteStore):
        self.note_store = note_store
    
    def distill_session(
        self,
        session_id: str,
        trajectory: List[Dict[str, Any]],
        outcome: str
    ) -> List[Note]:
        """
        Distill a session trajectory into notes
        In production, this would use an LLM to analyze the trajectory
        """
        notes_created = []
        
        # Extract key decisions
        decisions = self._extract_decisions(trajectory)
        if decisions:
            note = self.note_store.create_note(
                path=f"{session_id}/decisions.md",
                title=f"Decisions from {session_id}",
                content="\n\n".join(f"- {d}" for d in decisions),
                note_type=NoteType.DECISION,
                tags=["session", session_id]
            )
            notes_created.append(note)
        
        # Extract failures
        failures = self._extract_failures(trajectory)
        for i, failure in enumerate(failures):
            note = self.note_store.create_hindsight_note(
                path=f"{session_id}/failures/failure_{i}.md",
                title=f"Failure {i+1}: {failure.get('title', 'Unknown')}",
                problem_description=failure.get('description', ''),
                error_message=failure.get('error', ''),
                stack_trace=failure.get('trace', ''),
                attempted_solutions=failure.get('attempts', []),
                resolution=failure.get('resolution')
            )
            notes_created.append(note)
        
        # Overall session summary
        summary_note = self.note_store.create_note(
            path=f"{session_id}/summary.md",
            title=f"Session Summary: {session_id}",
            content=f"## Outcome\n\n{outcome}\n\n## Actions Taken\n\n{len(trajectory)} total actions",
            note_type=NoteType.FINDING,
            tags=["summary", session_id]
        )
        notes_created.append(summary_note)
        
        return notes_created
    
    def _extract_decisions(self, trajectory: List[Dict]) -> List[str]:
        """Extract key decisions from trajectory"""
        decisions = []
        for event in trajectory:
            if event.get('type') == 'decision':
                decisions.append(event.get('content', ''))
        return decisions
    
    def _extract_failures(self, trajectory: List[Dict]) -> List[Dict]:
        """Extract failures and their context"""
        failures = []
        for i, event in enumerate(trajectory):
            if 'error' in event or 'exception' in event.get('content', '').lower():
                failure = {
                    'title': event.get('action', 'Unknown action'),
                    'description': event.get('content', ''),
                    'error': event.get('error', ''),
                    'trace': event.get('trace', ''),
                    'attempts': [],
                    'resolution': None
                }
                
                # Look ahead for resolution
                for future_event in trajectory[i+1:i+10]:
                    if 'success' in future_event.get('content', '').lower():
                        failure['resolution'] = future_event.get('content')
                        break
                
                failures.append(failure)
        
        return failures


# Export
__all__ = ['Note', 'HindsightNote', 'NoteType', 'NoteStore', 'NoteTakingAgent']
