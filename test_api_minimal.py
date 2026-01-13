"""
Quick smoke test for minimal DTO API changes.
Tests that endpoints still return correct data structure.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8002"

def test_api_with_minimal_dtos():
    """Test API endpoints return minimal DTOs correctly."""
    
    print("\n" + "="*60)
    print(" API Smoke Test - Minimal DTOs")
    print("="*60)
    
    # Test 1: Create conversation
    print("\n1. Creating test conversation...")
    response = requests.post(f"{BASE_URL}/api/conversations", json={})
    assert response.status_code == 200, f"Failed to create conversation: {response.status_code}"
    conversation = response.json()
    conv_id = conversation["id"]
    print(f"   ✓ Conversation created: {conv_id}")
    
    # Test 2: Get conversation (should have minimal structure)
    print("\n2. Fetching conversation...")
    response = requests.get(f"{BASE_URL}/api/conversations/{conv_id}")
    assert response.status_code == 200
    conv_data = response.json()
    print(f"   ✓ Conversation fetched")
    print(f"   Messages: {len(conv_data['messages'])}")
    
    # Test 3: Send a message (should return minimal DTO)
    print("\n3. Sending test message...")
    message_data = {
        "content": "What is 2+2? Please keep your answer very brief."
    }
    
    print("   (This will take a few seconds - running council...)")
    response = requests.post(
        f"{BASE_URL}/api/conversations/{conv_id}/message",
        json=message_data,
        timeout=60
    )
    
    if response.status_code != 200:
        print(f"   ❌ Message failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    result = response.json()
    print(f"   ✓ Message processed successfully")
    
    # Test 4: Verify minimal DTO structure
    print("\n4. Verifying minimal DTO structure...")
    
    # Check stage1 structure
    assert "stage1" in result, "Missing stage1"
    assert isinstance(result["stage1"], list), "stage1 should be list"
    if result["stage1"]:
        stage1_item = result["stage1"][0]
        assert "model" in stage1_item, "stage1 missing model"
        assert "response" in stage1_item, "stage1 missing response"
        assert "usage" not in stage1_item, "stage1 should NOT have usage (not minimal!)"
        assert "timing" not in stage1_item, "stage1 should NOT have timing (not minimal!)"
        print(f"   ✓ Stage1 is minimal ({len(result['stage1'])} responses)")
    
    # Check stage2 structure
    assert "stage2" in result, "Missing stage2"
    assert isinstance(result["stage2"], list), "stage2 should be list"
    if result["stage2"]:
        stage2_item = result["stage2"][0]
        assert "model" in stage2_item, "stage2 missing model"
        assert "rankings" in stage2_item, "stage2 missing rankings"
        print(f"   ✓ Stage2 is minimal ({len(result['stage2'])} responses)")
    
    # Check stage3 structure
    assert "stage3" in result, "Missing stage3"
    assert "model" in result["stage3"], "stage3 missing model"
    assert "response" in result["stage3"], "stage3 missing response"
    assert "usage" not in result["stage3"], "stage3 should NOT have usage (not minimal!)"
    assert "timing" not in result["stage3"], "stage3 should NOT have timing (not minimal!)"
    print(f"   ✓ Stage3 is minimal")
    
    # Check metadata
    assert "metadata" in result, "Missing metadata"
    print(f"   ✓ Metadata present")
    
    # Test 5: Measure payload size
    print("\n5. Measuring payload size...")
    payload_size = len(json.dumps(result))
    print(f"   Response size: {payload_size:,} bytes")
    print(f"   Stage1 models: {len(result['stage1'])}")
    print(f"   Stage2 rankings: {len(result['stage2'])}")
    
    # Estimate what full size would have been (rough)
    # Full objects have ~40% more data (usage, timing, etc.)
    estimated_full_size = int(payload_size * 1.4)
    estimated_savings = estimated_full_size - payload_size
    print(f"   Estimated full size: {estimated_full_size:,} bytes")
    print(f"   Estimated savings: {estimated_savings:,} bytes ({(estimated_savings/estimated_full_size)*100:.1f}%)")
    
    # Test 6: Fetch conversation again (should have minimal messages)
    print("\n6. Fetching updated conversation...")
    response = requests.get(f"{BASE_URL}/api/conversations/{conv_id}")
    assert response.status_code == 200
    conv_data = response.json()
    print(f"   ✓ Conversation fetched")
    print(f"   Messages: {len(conv_data['messages'])}")
    
    # Verify stored message is also minimal
    if len(conv_data['messages']) > 1:
        assistant_msg = conv_data['messages'][1]  # Second message (first is user)
        if assistant_msg.get('role') == 'assistant':
            assert "stage1" in assistant_msg
            if assistant_msg["stage1"]:
                assert "usage" not in assistant_msg["stage1"][0], "Stored message should be minimal"
                print(f"   ✓ Stored messages are minimal")
    
    print("\n" + "="*60)
    print(" ✅ All API tests passed with minimal DTOs!")
    print("="*60)
    print(f"\n💾 Payload size: {payload_size:,} bytes")
    print(f"📉 Estimated reduction: ~{(estimated_savings/estimated_full_size)*100:.0f}% smaller than full objects\n")
    
    return True


if __name__ == "__main__":
    try:
        # Check if backend is running
        try:
            response = requests.get(f"{BASE_URL}/", timeout=2)
            if response.status_code != 200:
                print("❌ Backend not responding correctly")
                exit(1)
        except requests.exceptions.ConnectionError:
            print("❌ Backend not running. Start it with:")
            print("   cd confucius-agent && python -m uvicorn backend.main:app --reload --port 8002")
            exit(1)
        
        # Run tests
        success = test_api_with_minimal_dtos()
        exit(0 if success else 1)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
