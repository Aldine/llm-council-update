"""
Pytest configuration and fixtures for backend tests.
"""
import pytest
import os
from pathlib import Path
from typing import AsyncGenerator

from fastapi.testclient import TestClient
from httpx import AsyncClient

# Import app after setting test environment
os.environ["TESTING"] = "1"
os.environ["OPENROUTER_API_KEY"] = "test-key"

from backend.main import app
from backend import storage


@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory) -> Path:
    """Create temporary data directory for tests."""
    return tmp_path_factory.mktemp("test_data")


@pytest.fixture(autouse=True)
def setup_test_env(test_data_dir, monkeypatch):
    """Setup test environment variables."""
    monkeypatch.setenv("DATA_DIR", str(test_data_dir))
    storage.DATA_DIR = str(test_data_dir)
    yield
    # Cleanup after test
    for file in test_data_dir.glob("*.json"):
        file.unlink()


@pytest.fixture
def client() -> TestClient:
    """Create test client for synchronous tests."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create async client for async tests."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_conversation():
    """Create a sample conversation for testing."""
    conv_id = "test-conversation-id"
    conversation = storage.create_conversation(conv_id)
    yield conversation
    # Cleanup
    try:
        storage.delete_conversation(conv_id)
    except:
        pass


@pytest.fixture
def mock_auth_token():
    """Generate a mock authentication token."""
    from backend.auth import create_access_token
    return create_access_token(data={"sub": "demo@llmcouncil.com"})
