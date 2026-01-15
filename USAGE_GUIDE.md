# How to Use the Subagent Test Prompts

## Quick Start

### Test 1: Basic Sanity Check (5 minutes)
Tests if extension routing works.

```bash
cd llm-council-update-new

# Copy prompt to clipboard, then run:
confucius run "$(cat PROMPT_2_SANITY_TEST.md)" -w . -v
```

**Expected output:**
- 5-step plan
- Extension trace showing FileReadExtension, FileSearchExtension, etc.
- Real line numbers from README.md

---

### Test 2: Full Accessibility Audit (15 minutes)
Tests end-to-end workflow with computed values.

**Setup a test app first:**
```bash
# In another terminal, start a simple web server
cd test-webapp  # your test app directory
python -m http.server 3000
# Or: npm run dev
```

**Run the audit:**
```bash
cd llm-council-update-new
confucius run "$(cat PROMPT_1_FULL_AUDIT.md)" -w ../test-webapp -v
```

**Expected output:**
- 6+ UI elements audited
- Exact contrast ratios (e.g., 4.73:1, not "~4.7")
- CSS patch diffs
- Before/after verification table
- Extension trace OR subagent trace

---

## With Subagent Support (Advanced)

### Install with subagent extension:
```bash
cd llm-council-update-new
pip install -e .
```

### Run with Python API:
```python
from confucius_agent import create_subagent_enabled_agent, create_llm_client

# Create agent with subagents enabled
agent = create_subagent_enabled_agent(
    llm_client=create_llm_client('gpt-4'),
    workspace='../test-webapp',
    enable_subagents=True,
    verbose=True
)

# Load prompt
with open('PROMPT_1_FULL_AUDIT.md') as f:
    prompt = f.read()

# Run audit
result = agent.run_ralph_loop(prompt)

# Print subagent trace
for ext in agent.orchestrator.extensions:
    if hasattr(ext, 'get_trace_summary'):
        print('\n' + ext.get_trace_summary())

# Check results
print(f"\nSuccess: {result['success']}")
print(f"Ralph iterations: {result['ralph_iterations']}")
```

---

## What The Prompts Test

### PROMPT_2_SANITY_TEST.md
- ✓ Extension routing works
- ✓ File operations execute
- ✓ Trace captures tool names
- ✓ Output contains real data from files

### PROMPT_1_FULL_AUDIT.md  
- ✓ Multi-phase planning
- ✓ Computed contrast ratios (no guessing)
- ✓ Code patch generation
- ✓ Before/after verification
- ✓ Focus ring audit
- ✓ Subagent delegation (if enabled)
- ✓ Traceable execution log

---

## Interpreting Results

### ✅ PASS Criteria
- Plan section present with steps
- Trace shows real SDK extension names:
  - `BashExtension`, `FileReadExtension`, `FileEditExtension`, etc.
- Contrast ratios are exact decimals (4.73:1, 12.05:1, etc.)
- Colors are hex values extracted from files (#1a1a1a, #ffffff)
- Patch diffs reference actual files in workspace
- Verification shows different values than audit (changes applied)

### ❌ FAIL Criteria
- No trace section
- Invented tool names ("ColorExtractor", "ContrastChecker")
- Vague ratios ("approximately 4:1", "around 3.5:1")
- Made-up colors not in your CSS files
- Verification identical to audit (nothing changed)

---

## Debugging

### If extensions don't execute:
```python
# Check available extensions
from confucius_agent import create_agent
agent = create_agent()
for ext in agent.orchestrator.extensions:
    print(f"- {ext.name}: {ext.__class__.__name__}")
```

### If subagents don't work:
```python
# Verify SubagentExtension is loaded
has_subagents = any(
    ext.__class__.__name__ == 'SubagentExtension' 
    for ext in agent.orchestrator.extensions
)
print(f"Subagents available: {has_subagents}")
```

### If contrast ratios are wrong:
The formula is:
```python
def luminance(r, g, b):
    """r, g, b in range [0, 255]"""
    r, g, b = r/255, g/255, b/255
    r = r/12.92 if r <= 0.03928 else ((r+0.055)/1.055)**2.4
    g = g/12.92 if g <= 0.03928 else ((g+0.055)/1.055)**2.4
    b = b/12.92 if b <= 0.03928 else ((b+0.055)/1.055)**2.4
    return 0.2126*r + 0.7152*g + 0.0722*b

def contrast_ratio(fg_hex, bg_hex):
    """e.g., contrast_ratio('#333333', '#ffffff')"""
    fg = luminance(int(fg_hex[1:3], 16), int(fg_hex[3:5], 16), int(fg_hex[5:7], 16))
    bg = luminance(int(bg_hex[1:3], 16), int(bg_hex[3:5], 16), int(bg_hex[5:7], 16))
    l1, l2 = max(fg, bg), min(fg, bg)
    return (l1 + 0.05) / (l2 + 0.05)

# Test
print(contrast_ratio('#333333', '#ffffff'))  # Should be 12.63:1
```

---

## Environment Variables

```bash
# For GPT models
export OPENAI_API_KEY=sk-...

# For Claude models (alternative)
export ANTHROPIC_API_KEY=sk-ant-...

# For Gemini models (alternative)
export GOOGLE_API_KEY=...

# For OpenRouter (100+ models)
export OPENROUTER_API_KEY=sk-or-v1-...
```

---

## Next Steps

1. **Run PROMPT_2** first to verify basic functionality
2. **If PROMPT_2 passes**, run PROMPT_1 with a real web app
3. **Check traces** - do they show real SDK tool names?
4. **Verify computed values** - are contrast ratios exact decimals?
5. **Test patches** - do the diffs reference real files?

If everything passes, your Confucius Agent SDK is working correctly for planning, delegation, and verification! 🎉
