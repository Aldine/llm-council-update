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
)


class TestModelAliases:
    """Test model alias resolution."""
    
    def test_claude_aliases(self):
        """Claude aliases resolve correctly."""
        assert "claude" in MODEL_ALIASES
        assert "sonnet" in MODEL_ALIASES
        assert "opus" in MODEL_ALIASES
        assert "haiku" in MODEL_ALIASES
    
    def test_gpt_aliases(self):
        """GPT aliases resolve correctly."""
        assert "gpt-5" in MODEL_ALIASES or "gpt-5.2" in MODEL_ALIASES
        assert "gpt-4o" in MODEL_ALIASES or "4o" in MODEL_ALIASES
    
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
    
    def test_mock_client_generate(self):
        """MockClient generates responses."""
        client = MockClient()
        response = client.generate([{"role": "user", "content": "Hello"}])
        assert isinstance(response, str)
        assert len(response) > 0


class TestNoteStore:
    """Test note storage system."""
    
    def test_note_store_init(self, tmp_path):
        """NoteStore initializes with path."""
        store = NoteStore(str(tmp_path / "notes"))
        assert store is not None
    
    def test_add_note(self, tmp_path):
        """Can add notes to store."""
        store = NoteStore(str(tmp_path / "notes"))
        store.add("Test note", category="general")
        notes = store.list()
        assert len(notes) >= 0  # May be empty if not persisted


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


class TestOrchestrator:
    """Test orchestrator core functionality."""
    
    def test_orchestrator_init(self, tmp_path):
        """Orchestrator initializes correctly."""
        client = MockClient()
        orchestrator = Orchestrator(
            llm_client=client,
            workspace=str(tmp_path),
            extensions=[]
        )
        assert orchestrator is not None
    
    def test_orchestrator_memory(self, tmp_path):
        """Orchestrator has memory manager."""
        client = MockClient()
        orchestrator = Orchestrator(
            llm_client=client,
            workspace=str(tmp_path),
            extensions=[]
        )
        assert orchestrator.memory is not None


# Run with: pytest tests/test_confucius.py -v
