"""
Tests for storage module.
"""
import pytest
from datetime import datetime

from backend import storage


def test_create_conversation():
    """Test creating a new conversation."""
    conv_id = "test-create-123"
    conversation = storage.create_conversation(conv_id)
    
    assert conversation["id"] == conv_id
    assert conversation["title"] == "New Conversation"
    assert conversation["messages"] == []
    assert "created_at" in conversation
    
    # Cleanup
    storage.delete_conversation(conv_id)


def test_get_conversation():
    """Test retrieving a conversation."""
    conv_id = "test-get-456"
    created = storage.create_conversation(conv_id)
    
    retrieved = storage.get_conversation(conv_id)
    
    assert retrieved is not None
    assert retrieved["id"] == conv_id
    assert retrieved["title"] == created["title"]
    
    # Cleanup
    storage.delete_conversation(conv_id)


def test_get_nonexistent_conversation():
    """Test retrieving a conversation that doesn't exist."""
    result = storage.get_conversation("nonexistent-id")
    assert result is None


def test_delete_conversation():
    """Test deleting a conversation."""
    conv_id = "test-delete-789"
    storage.create_conversation(conv_id)
    
    # Delete should succeed
    result = storage.delete_conversation(conv_id)
    assert result is True
    
    # Should no longer exist
    retrieved = storage.get_conversation(conv_id)
    assert retrieved is None


def test_delete_nonexistent_conversation():
    """Test deleting a conversation that doesn't exist."""
    result = storage.delete_conversation("nonexistent-id")
    assert result is False


def test_list_conversations():
    """Test listing all conversations."""
    # Create multiple conversations
    ids = ["list-1", "list-2", "list-3"]
    for conv_id in ids:
        storage.create_conversation(conv_id)
    
    conversations = storage.list_conversations()
    
    assert len(conversations) >= 3
    assert all("id" in c for c in conversations)
    assert all("title" in c for c in conversations)
    assert all("message_count" in c for c in conversations)
    
    # Cleanup
    for conv_id in ids:
        storage.delete_conversation(conv_id)


def test_add_user_message():
    """Test adding a user message to conversation."""
    conv_id = "test-user-msg"
    storage.create_conversation(conv_id)
    
    storage.add_user_message(conv_id, "Hello, world!")
    
    conversation = storage.get_conversation(conv_id)
    assert len(conversation["messages"]) == 1
    assert conversation["messages"][0]["role"] == "user"
    assert conversation["messages"][0]["content"] == "Hello, world!"
    
    # Cleanup
    storage.delete_conversation(conv_id)


def test_add_assistant_message():
    """Test adding an assistant message with stages."""
    conv_id = "test-assistant-msg"
    storage.create_conversation(conv_id)
    
    stage1 = [{"model": "model1", "response": "Response 1"}]
    stage2 = [{"model": "model1", "ranking": [1, 2, 3]}]
    stage3 = "Final synthesized answer"
    
    storage.add_assistant_message(
        conv_id,
        stage1=stage1,
        stage2=stage2,
        stage3=stage3
    )
    
    conversation = storage.get_conversation(conv_id)
    assert len(conversation["messages"]) == 1
    assert conversation["messages"][0]["role"] == "assistant"
    assert conversation["messages"][0]["stage1"] == stage1
    assert conversation["messages"][0]["stage2"] == stage2
    assert conversation["messages"][0]["stage3"] == stage3
    
    # Cleanup
    storage.delete_conversation(conv_id)


def test_update_conversation_title():
    """Test updating conversation title."""
    conv_id = "test-title-update"
    storage.create_conversation(conv_id)
    
    new_title = "Updated Title"
    storage.update_conversation_title(conv_id, new_title)
    
    conversation = storage.get_conversation(conv_id)
    assert conversation["title"] == new_title
    
    # Cleanup
    storage.delete_conversation(conv_id)


def test_update_nonexistent_conversation_title():
    """Test updating title of nonexistent conversation raises error."""
    with pytest.raises(ValueError, match="not found"):
        storage.update_conversation_title("nonexistent-id", "New Title")
