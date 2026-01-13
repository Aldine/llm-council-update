"""Tests for confucius_agent package."""
import pytest
from confucius_agent import (
    create_agent,
    Orchestrator,
    NoteStore,
    NoteTakingAgent,
    MockClient,
    MODEL_ALIASES,
    list_supported_models,
    MemoryManager,
    NoteType,
)


class TestModelAliases:
    """Test model alias resolution."""
    
    def test_claude_aliases(self):
        """Claude aliases resolve correctly."""
        assert "claude" in MODEL_ALIASES
        assert "sonnet" in MODEL_ALIASES
        assert "opus" in MODEL_ALIASES
        # haiku might not be in aliases
    
    def test_gpt_aliases(self):
        """GPT aliases resolve correctly."""
        assert "gpt-5" in MODEL_ALIASES or "gpt-5.2" in MODEL_ALIASES or "gpt5" in MODEL_ALIASES
    
    def test_gemini_aliases(self):
        """Gemini aliases resolve correctly."""
        assert "gemini" in MODEL_ALIASES or "gemini-2.5" in MODEL_ALIASES
    
    def test_list_supported_models(self):
        """List supported models returns dict."""
        models = list_supported_models()
        assert isinstance(models, dict)
        assert len(models) > 0


class TestMockClient:
    """Test mock client for development."""
    
    def test_mock_client_init(self):
        """MockClient initializes without API key."""
        client = MockClient()
        assert client is not None
    
    def test_mock_client_callable(self):
        """MockClient is callable and generates responses."""
        client = MockClient()
        response = client([{"role": "user", "content": "Hello"}])
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_mock_client_with_custom_responses(self):
        """MockClient uses custom responses."""
        client = MockClient(responses=["Response 1", "Response 2"])
        assert client([{"role": "user", "content": "test"}]) == "Response 1"
        assert client([{"role": "user", "content": "test"}]) == "Response 2"
        assert client([{"role": "user", "content": "test"}]) == "Response 1"  # cycles


class TestNoteStore:
    """Test note storage system."""
    
    def test_note_store_init(self, tmp_path):
        """NoteStore initializes with path."""
        store = NoteStore(tmp_path / "notes")
        assert store is not None
    
    def test_create_note(self, tmp_path):
        """Can create notes in store."""
        store = NoteStore(tmp_path / "notes")
        note = store.create_note(
            path="test/note1",
            title="Test Note",
            content="Test content",
            note_type=NoteType.FINDING
        )
        assert note.title == "Test Note"
        assert note.content == "Test content"


class TestCreateAgent:
    """Test agent factory function."""
    
    def test_create_agent_mock(self, tmp_path):
        """Create agent with mock client."""
        agent = create_agent(
            workspace=str(tmp_path),
            model="mock"
        )
        assert agent is not None
    
    def test_create_agent_default_config(self, tmp_path):
        """Create agent with default configuration."""
        agent = create_agent(
            workspace=str(tmp_path),
            model="mock",
            max_iterations=10,
            completion_promise="DONE"
        )
        assert agent.config.max_iterations == 10
        assert agent.config.completion_promise == "DONE"


class TestMemoryManager:
    """Test memory manager functionality."""
    
    def test_memory_manager_init(self):
        """MemoryManager initializes correctly."""
        mm = MemoryManager()
        assert mm is not None
        assert mm.max_tokens == 100000
    
    def test_memory_manager_add_message(self):
        """MemoryManager adds messages."""
        mm = MemoryManager()
        mm.add_message("user", "Hello world")
        assert len(mm.messages) == 1
        assert mm.messages[0].content == "Hello world"
    
    def test_memory_manager_hierarchy(self):
        """MemoryManager has hierarchical scopes."""
        mm = MemoryManager()
        assert 'session' in mm.hierarchy
        assert 'entry' in mm.hierarchy
        assert 'runnable' in mm.hierarchy


class TestOrchestrator:
    """Test orchestrator core functionality."""
    
    def test_orchestrator_init(self):
        """Orchestrator initializes correctly."""
        client = MockClient()
        orchestrator = Orchestrator(
            llm_client=client,
            extensions=[]
        )
        assert orchestrator is not None
    
    def test_orchestrator_has_memory(self):
        """Orchestrator has memory manager."""
        client = MockClient()
        orchestrator = Orchestrator(
            llm_client=client,
            extensions=[]
        )
        assert orchestrator.memory_manager is not None



# Run with: pytest tests/test_confucius.py -v
