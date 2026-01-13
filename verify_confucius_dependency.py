"""
CONFUCIUS-AGENT DEPENDENCY SANITY CHECKER
Verifies that confucius-agent is properly installed and accessible to Copilot.
Usage: python verify_confucius_dependency.py
"""

import importlib.util
import sys
import os
from pathlib import Path

# ---------------- CONFIGURATION ----------------
TARGET_PKG = 'confucius_agent'
# -----------------------------------------------

score = 0
total_checks = 6

print(f"\n🔍 CONFUCIUS-AGENT INTEGRATION CHECK\n")
print("="*70)

# CHECK 1: Package Findability (16.7%)
spec = importlib.util.find_spec(TARGET_PKG)
if spec is not None:
    print(f"✅ [1/6] Package spec found (Python can locate it)")
    score += 1
else:
    print(f"❌ [1/6] Package spec NOT found")
    print(f"      Fix: pip install confucius-agent")

# CHECK 2: Origin Verification (16.7%)
if spec and spec.origin:
    origin_path = Path(spec.origin)
    print(f"✅ [2/6] Origin verified: {origin_path.parent.name}/{origin_path.name}")
    score += 1
else:
    print(f"❌ [2/6] No origin file found")

# CHECK 3: Import Execution (16.7%)
module = None
try:
    module = importlib.import_module(TARGET_PKG)
    print(f"✅ [3/6] Successfully imported module")
    score += 1
except Exception as e:
    print(f"❌ [3/6] Import crashed: {e}")

# CHECK 4: Core Classes Available (16.7%)
if module:
    required_classes = ['Orchestrator', 'MemoryManager', 'RalphOrchestrator']
    found_classes = []
    missing_classes = []
    
    for cls in required_classes:
        if hasattr(module, cls):
            found_classes.append(cls)
        else:
            missing_classes.append(cls)
    
    if len(found_classes) == len(required_classes):
        print(f"✅ [4/6] All core classes available: {', '.join(found_classes)}")
        score += 1
    else:
        print(f"❌ [4/6] Missing classes: {', '.join(missing_classes)}")
else:
    print(f"❌ [4/6] Cannot check classes (Import failed)")

# CHECK 5: Extension System Available (16.7%)
try:
    from confucius_agent.orchestrator import Extension, Action, RunContext
    print(f"✅ [5/6] Extension system importable (Extension, Action, RunContext)")
    score += 1
except ImportError as e:
    print(f"❌ [5/6] Extension system not available: {e}")

# CHECK 6: LLM Clients Available (16.7%)
try:
    from confucius_agent.llm_clients import LLMClient
    llm_providers = []
    
    # Check which providers are available
    try:
        from confucius_agent.llm_clients import AnthropicClient
        llm_providers.append("Anthropic")
    except:
        pass
    
    try:
        from confucius_agent.llm_clients import OpenAIClient
        llm_providers.append("OpenAI")
    except:
        pass
    
    try:
        from confucius_agent.llm_clients import GeminiClient
        llm_providers.append("Gemini")
    except:
        pass
    
    if llm_providers:
        print(f"✅ [6/6] LLM clients available: {', '.join(llm_providers)}")
        score += 1
    else:
        print(f"⚠️  [6/6] LLM base available but no providers found")
        score += 0.5
except ImportError:
    print(f"❌ [6/6] LLM client system not available")

# ---------------- RESULTS ----------------
percentage = (score / total_checks) * 100
print(f"\n" + "="*70)
print(f"📊 INTEGRATION HEALTH SCORE: {percentage:.1f}%")
print("="*70)

if percentage == 100:
    print(f"🚀 EXCELLENT: Confucius-agent is fully operational!")
    print(f"   Copilot has complete visibility of all components.")
    print(f"\n✨ You can now use:")
    print(f"   • from confucius_agent import Orchestrator, MemoryManager")
    print(f"   • from confucius_agent import RalphOrchestrator, RalphLoopConfig")
    print(f"   • from confucius_agent.orchestrator import Extension, Action")
    print(f"   • from confucius_agent.llm_clients import AnthropicClient")
    
elif percentage >= 66:
    print(f"⚠️  PARTIAL: Some components missing or not accessible.")
    print(f"   Core functionality works but some features unavailable.")
    
elif percentage >= 33:
    print(f"⚠️  LIMITED: Major components missing.")
    print(f"   Package is installed but incomplete.")
    print(f"   Try: pip install --upgrade confucius-agent")
    
else:
    print(f"❌ CRITICAL: Dependency not properly linked.")
    print(f"   Action required:")
    print(f"   1. pip install confucius-agent")
    print(f"   2. OR: pip install -e /path/to/confucius-agent (dev mode)")
    print(f"   3. Restart your editor")

print("\n" + "="*70)

# BONUS: Check for .env configuration
print(f"\n🔑 API KEY CHECK:")
env_file = Path(".env")
if env_file.exists():
    print(f"✅ .env file found")
    
    # Check for LLM API keys
    env_content = env_file.read_text()
    keys_found = []
    
    if "ANTHROPIC_API_KEY" in env_content:
        keys_found.append("Anthropic")
    if "OPENAI_API_KEY" in env_content:
        keys_found.append("OpenAI")
    if "GOOGLE_API_KEY" in env_content:
        keys_found.append("Google")
    if "OPENROUTER_API_KEY" in env_content:
        keys_found.append("OpenRouter")
    
    if keys_found:
        print(f"✅ Configured providers: {', '.join(keys_found)}")
    else:
        print(f"⚠️  No LLM API keys found in .env")
else:
    print(f"⚠️  No .env file found")
    print(f"   Create one with your API keys:")
    print(f"   ANTHROPIC_API_KEY=your_key_here")
    print(f"   OPENAI_API_KEY=your_key_here")

print("="*70 + "\n")

sys.exit(0 if percentage == 100 else 1)
