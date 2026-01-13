"""
Debug script to inspect Stage3 response and metadata structure.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8002"

def inspect_stage3():
    """Create a test message and inspect the Stage3 response."""
    
    print("\n" + "="*60)
    print(" Inspecting Stage3 Response Structure")
    print("="*60)
    
    # Create conversation
    print("\n1. Creating conversation...")
    response = requests.post(f"{BASE_URL}/api/conversations", json={})
    conv_id = response.json()["id"]
    print(f"   Created: {conv_id}")
    
    # Send message
    print("\n2. Sending message to council...")
    print("   Question: 'What is 2+2? Keep it very brief.'")
    
    response = requests.post(
        f"{BASE_URL}/api/conversations/{conv_id}/message",
        json={"content": "What is 2+2? Keep it very brief."},
        timeout=60
    )
    
    if response.status_code != 200:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Response: {response.text}")
        return
    
    result = response.json()
    
    # Inspect structure
    print("\n3. Response structure:")
    print(f"   Keys: {list(result.keys())}")
    
    print("\n4. Stage1 inspection:")
    print(f"   Type: {type(result.get('stage1'))}")
    print(f"   Length: {len(result.get('stage1', []))}")
    if result.get('stage1'):
        print(f"   First item keys: {list(result['stage1'][0].keys())}")
        print(f"   First model: {result['stage1'][0].get('model')}")
        print(f"   Response preview: {result['stage1'][0].get('response', '')[:100]}...")
    else:
        print("   ⚠️  EMPTY!")
    
    print("\n5. Stage2 inspection:")
    print(f"   Type: {type(result.get('stage2'))}")
    print(f"   Length: {len(result.get('stage2', []))}")
    if result.get('stage2'):
        print(f"   First item keys: {list(result['stage2'][0].keys())}")
    else:
        print("   ⚠️  EMPTY!")
    
    print("\n6. Stage3 inspection:")
    stage3 = result.get('stage3', {})
    print(f"   Type: {type(stage3)}")
    print(f"   Keys: {list(stage3.keys())}")
    print(f"   Model: {stage3.get('model')}")
    print(f"   Response: {stage3.get('response', '')[:200]}")
    print(f"   Response length: {len(stage3.get('response', ''))} chars")
    
    print("\n7. Metadata inspection:")
    metadata = result.get('metadata', {})
    print(f"   Type: {type(metadata)}")
    print(f"   Keys: {list(metadata.keys())}")
    for key, value in metadata.items():
        if isinstance(value, dict):
            print(f"   {key}: {list(value.keys())} (dict)")
        elif isinstance(value, list):
            print(f"   {key}: {len(value)} items (list)")
        else:
            print(f"   {key}: {value}")
    
    print("\n8. Full response (formatted):")
    print(json.dumps(result, indent=2)[:1000])
    
    print("\n9. Size analysis:")
    full_json = json.dumps(result)
    print(f"   Total response size: {len(full_json):,} bytes")
    print(f"   Stage1 size: {len(json.dumps(result.get('stage1', []))):,} bytes")
    print(f"   Stage2 size: {len(json.dumps(result.get('stage2', []))):,} bytes")
    print(f"   Stage3 size: {len(json.dumps(result.get('stage3', {}))):,} bytes")
    print(f"   Metadata size: {len(json.dumps(result.get('metadata', {}))):,} bytes")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        # Check backend
        response = requests.get(f"{BASE_URL}/", timeout=2)
        if response.status_code != 200:
            print("❌ Backend not responding")
            exit(1)
        
        inspect_stage3()
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Backend not running. Start with:")
        print("   cd confucius-agent && python -m uvicorn backend.main:app --reload --port 8002")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
