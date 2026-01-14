#!/usr/bin/env python3
"""
Test GPT integration in Confucius Agent
"""

import sys
sys.path.insert(0, 'src')

from confucius_agent import create_llm_client, MODEL_ALIASES, list_supported_models

print("🧪 Testing GPT Integration\n")
print("=" * 60)

# Test 1: List supported models
print("\n1. Supported Models:")
models = list_supported_models()
print(f"   Providers: {list(models.keys())}")
if 'openai' in models:
    print(f"   OpenAI models: {models['openai']}")

# Test 2: Model aliases
print("\n2. GPT Model Aliases:")
gpt_aliases = {k: v for k, v in MODEL_ALIASES.items() if 'gpt' in k.lower() or 'gpt' in v.lower()}
for alias, full_name in gpt_aliases.items():
    print(f"   {alias:15} → {full_name}")

# Test 3: Create GPT clients
print("\n3. Create GPT Clients:")
test_models = [
    "gpt-4",
    "gpt-5.2",
    "gpt-4o",
]

for model in test_models:
    try:
        client = create_llm_client(model=model)
        print(f"   ✅ {model:20} → {client.__class__.__name__}")
    except Exception as e:
        print(f"   ❌ {model:20} → Error: {str(e)[:50]}")

# Test 4: OpenRouter GPT models
print("\n4. OpenRouter GPT Models:")
openrouter_gpt = [
    "openai/gpt-4",
    "openai/gpt-4-turbo",
    "openai/gpt-5.2",
]

for model in openrouter_gpt:
    try:
        client = create_llm_client(model=model)
        print(f"   ✅ {model:30} → {client.__class__.__name__}")
    except Exception as e:
        print(f"   ❌ {model:30} → Error: {str(e)[:50]}")

# Test 5: Mock client (for testing without API keys)
print("\n5. Mock Client:")
try:
    from confucius_agent import MockClient
    mock = MockClient(responses=["Test response from GPT"])
    test_messages = [{"role": "user", "content": "Hello"}]
    response = mock(test_messages)
    print(f"   ✅ Mock client works")
    print(f"   Response: {response}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ GPT Integration Test Complete!")
print("\nℹ️  To use GPT models, set OPENAI_API_KEY environment variable")
print("ℹ️  Or use OpenRouter with OPENROUTER_API_KEY for 100+ models")
