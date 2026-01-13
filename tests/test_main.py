"""
Tests for FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend import storage


def test_root_endpoint(client):
    """Test root endpoint returns service info."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "LLM Council API"
    assert data["version"] == "1.0.0"
    assert "authentication" in data


def test_list_conversations_endpoint(client):
    """Test listing conversations via API."""
    # Create test conversation
    conv_id = "api-test-list"
    storage.create_conversation(conv_id)
    
    response = client.get("/api/conversations")
    
    assert response.status_code == 200
    conversations = response.json()
    assert isinstance(conversations, list)
    assert any(c["id"] == conv_id for c in conversations)
    
    # Cleanup
    storage.delete_conversation(conv_id)


def test_create_conversation_endpoint(client):
    """Test creating conversation via API."""
    response = client.post("/api/conversations", json={})
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "title" in data
    assert "messages" in data
    assert data["messages"] == []
    
    # Cleanup
    storage.delete_conversation(data["id"])


def test_get_conversation_endpoint(client):
    """Test getting specific conversation via API."""
    conv_id = "api-test-get"
    storage.create_conversation(conv_id)
    
    response = client.get(f"/api/conversations/{conv_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == conv_id
    assert "messages" in data
    
    # Cleanup
    storage.delete_conversation(conv_id)


def test_get_nonexistent_conversation_endpoint(client):
    """Test getting nonexistent conversation returns 404."""
    response = client.get("/api/conversations/nonexistent-id")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_conversation_endpoint(client):
    """Test deleting conversation via API."""
    conv_id = "api-test-delete"
    storage.create_conversation(conv_id)
    
    # Delete via API
    response = client.delete(f"/api/conversations/{conv_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert "deleted" in data["message"].lower()
    assert data["id"] == conv_id
    
    # Verify deletion
    get_response = client.get(f"/api/conversations/{conv_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_conversation_endpoint(client):
    """Test deleting nonexistent conversation returns 404."""
    response = client.delete("/api/conversations/nonexistent-id")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.skip(reason="Requires mocking async council functions - complex integration test")
def test_send_message_endpoint(client, monkeypatch):
    """Test sending message via standard endpoint (mocked)."""
    # Mock the council functions to avoid actual API calls
    def mock_run_full_council(*args, **kwargs):
        return {
            "stage1": [{"model": "test-model", "response": "Test response"}],
            "stage2": [{"model": "test-model", "ranking": [1]}],
            "stage3": "Final test answer"
        }
    
    monkeypatch.setattr("backend.main.run_full_council", mock_run_full_council)
    
    # Create conversation
    conv_id = "api-test-message"
    storage.create_conversation(conv_id)
    
    # Send message
    response = client.post(
        f"/api/conversations/{conv_id}/message",
        json={"content": "What is 2+2?"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "stage1" in data
    assert "stage2" in data
    assert "stage3" in data
    
    # Cleanup
    storage.delete_conversation(conv_id)


def test_send_message_to_nonexistent_conversation(client):
    """Test sending message to nonexistent conversation returns 404."""
    response = client.post(
        "/api/conversations/nonexistent-id/message",
        json={"content": "Hello"}
    )
    
    assert response.status_code == 404


def test_login_endpoint(client):
    """Test login with valid credentials."""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "demo@llmcouncil.com",
            "password": "demo123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_get_current_user(client, mock_auth_token):
    """Test getting current user with valid token."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {mock_auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert data["email"] == "demo@llmcouncil.com"


def test_get_current_user_no_token(client):
    """Test getting current user without token returns 401."""
    response = client.get("/api/auth/me")
    
    assert response.status_code == 401
