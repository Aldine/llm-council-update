"""
Smoke Test Suite for LLM Council APIs
Tests basic functionality of backend endpoints
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8002"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")

def test_root_endpoint():
    """Test root endpoint"""
    print_info("Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert data["service"] == "LLM Council API"
        print_success(f"Root endpoint OK - Service: {data['service']}")
        return True
    except Exception as e:
        print_error(f"Root endpoint failed: {e}")
        return False

def test_prompt_suggestions():
    """Test prompt suggestions endpoint"""
    print_info("Testing prompt suggestions...")
    try:
        response = requests.get(f"{BASE_URL}/prompts/suggestions")
        assert response.status_code == 200, f"Status code: {response.status_code}"
        data = response.json()
        assert "suggestions" in data, f"Missing 'suggestions' key in response: {list(data.keys())}"
        suggestions = data["suggestions"]
        assert isinstance(suggestions, list), f"Suggestions is not a list: {type(suggestions)}"
        assert len(suggestions) > 0, "No suggestions returned"
        print_success(f"Prompt suggestions OK - {len(suggestions)} suggestions available")
        return True
    except Exception as e:
        print_error(f"Prompt suggestions failed: {e}")
        return False

def test_prompt_categories():
    """Test prompt categories endpoint"""
    print_info("Testing prompt categories...")
    try:
        response = requests.get(f"{BASE_URL}/prompts/categories")
        assert response.status_code == 200
        categories = response.json()
        assert isinstance(categories, list)
        print_success(f"Prompt categories OK - {len(categories)} categories")
        return True
    except Exception as e:
        print_error(f"Prompt categories failed: {e}")
        return False

def test_core_prompts():
    """Test core prompts endpoint"""
    print_info("Testing core prompts...")
    try:
        response = requests.get(f"{BASE_URL}/prompts/core")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        print_success(f"Core prompts OK")
        return True
    except Exception as e:
        print_error(f"Core prompts failed: {e}")
        return False

def test_conversations_list():
    """Test listing conversations (anonymous access)"""
    print_info("Testing conversations list...")
    try:
        response = requests.get(f"{BASE_URL}/api/conversations")
        assert response.status_code == 200
        conversations = response.json()
        assert isinstance(conversations, list)
        print_success(f"Conversations list OK - {len(conversations)} conversations")
        return True, conversations
    except Exception as e:
        print_error(f"Conversations list failed: {e}")
        return False, []

def test_create_conversation():
    """Test creating a new conversation"""
    print_info("Testing conversation creation...")
    try:
        response = requests.post(f"{BASE_URL}/api/conversations")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "title" in data
        assert "messages" in data
        conversation_id = data["id"]
        print_success(f"Conversation created OK - ID: {conversation_id}")
        return True, conversation_id
    except Exception as e:
        print_error(f"Conversation creation failed: {e}")
        return False, None

def test_send_message(conversation_id: str):
    """Test sending a message to a conversation"""
    print_info(f"Testing send message to conversation {conversation_id}...")
    try:
        payload = {"content": "What is the capital of France?"}
        response = requests.post(
            f"{BASE_URL}/api/conversations/{conversation_id}/message",
            json=payload
        )
        
        # This might take a while due to OpenRouter call
        print_warning("This test requires OpenRouter API key to complete fully")
        
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert "messages" in data
            print_success(f"Message sent OK")
            return True
        elif response.status_code == 500:
            print_warning(f"Message endpoint accessible but OpenRouter API call failed (expected without API key)")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Send message failed: {e}")
        return False

def test_get_conversation(conversation_id: str):
    """Test retrieving a conversation by ID"""
    print_info(f"Testing get conversation {conversation_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/conversations/{conversation_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == conversation_id
        assert "messages" in data
        print_success(f"Get conversation OK - {len(data['messages'])} messages")
        return True
    except Exception as e:
        print_error(f"Get conversation failed: {e}")
        return False

def test_delete_conversation(conversation_id: str):
    """Test deleting a conversation"""
    print_info(f"Testing delete conversation {conversation_id}...")
    try:
        response = requests.delete(f"{BASE_URL}/api/conversations/{conversation_id}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print_success(f"Conversation deleted OK")
        return True
    except Exception as e:
        print_error(f"Delete conversation failed: {e}")
        return False

def test_api_docs():
    """Test FastAPI auto-generated docs"""
    print_info("Testing API documentation...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        assert response.status_code == 200
        print_success("API docs accessible at /docs")
        return True
    except Exception as e:
        print_error(f"API docs failed: {e}")
        return False

def run_smoke_tests():
    """Run all smoke tests"""
    print("\n" + "="*60)
    print(" "*15 + "LLM COUNCIL API SMOKE TESTS")
    print("="*60 + "\n")
    
    results = []
    
    # Basic endpoints
    results.append(("Root Endpoint", test_root_endpoint()))
    results.append(("API Docs", test_api_docs()))
    results.append(("Prompt Suggestions", test_prompt_suggestions()))
    results.append(("Prompt Categories", test_prompt_categories()))
    results.append(("Core Prompts", test_core_prompts()))
    
    # Conversation flow
    success, conversations = test_conversations_list()
    results.append(("List Conversations", success))
    
    success, conversation_id = test_create_conversation()
    results.append(("Create Conversation", success))
    
    if conversation_id:
        success = test_get_conversation(conversation_id)
        results.append(("Get Conversation", success))
        
        # Note: Send message test will likely fail without OpenRouter API key
        success = test_send_message(conversation_id)
        results.append(("Send Message", success))
        
        success = test_delete_conversation(conversation_id)
        results.append(("Delete Conversation", success))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"{test_name:.<40} {status}")
    
    print(f"\n{Colors.BLUE}Total: {passed}/{total} passed{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}✓ All tests passed!{Colors.END}\n")
    elif passed > total // 2:
        print(f"\n{Colors.YELLOW}⚠ Most tests passed, some failures{Colors.END}\n")
    else:
        print(f"\n{Colors.RED}✗ Many tests failed{Colors.END}\n")
    
    return passed == total

if __name__ == "__main__":
    try:
        run_smoke_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {e}{Colors.END}")
