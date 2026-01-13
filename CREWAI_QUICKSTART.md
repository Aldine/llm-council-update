# 🤖 CrewAI Integration - Quick Start

## What Changed

Your LLM Council now has **two deliberation engines**:

### 1. Standard Mode (Default)
- Direct OpenRouter API calls
- Fast parallel execution
- Simple and reliable

### 2. CrewAI Mode (New!) 
- Multi-agent orchestration
- Role-based specialization
- Advanced reasoning capabilities

## How to Use

### Enable CrewAI Mode

**In the UI:**
1. Click ⚙️ Settings in sidebar
2. Toggle "🤖 Use CrewAI Multi-Agent Orchestration"
3. Start a new conversation

**Programmatically:**
```javascript
localStorage.setItem('use_crewai', 'true');
```

### API Usage

**Standard:**
```bash
curl -X POST http://localhost:8001/api/conversations/{id}/message \
  -H "Content-Type: application/json" \
  -d '{"content": "Your question"}'
```

**CrewAI:**
```bash
curl -X POST http://localhost:8001/api/conversations/{id}/message/crew \
  -H "Content-Type: application/json" \
  -d '{"content": "Your question"}'
```

## Quick Test

```bash
# Test CrewAI integration
uv run python test_crew_integration.py
```

## Key Differences

| Feature | Standard | CrewAI |
|---------|----------|--------|
| **Execution** | Parallel | Sequential |
| **Speed** | Faster | Slower |
| **Context** | Simple | Advanced |
| **Roles** | Generic | Specialized |
| **Coordination** | None | Chairman-led |

## When to Use Each

### Use Standard Mode When:
- ✅ Speed is critical
- ✅ Simple question-answer scenarios
- ✅ Testing/debugging
- ✅ Rate limits are not an issue

### Use CrewAI Mode When:
- ✅ Complex multi-step reasoning needed
- ✅ Need specialized expertise
- ✅ Want better context management
- ✅ Prefer hierarchical coordination

## What's Under the Hood

### CrewAI Agents

1. **Technical Analyst**
   - Role: Provide technically accurate responses
   - Model: First in COUNCIL_MODELS

2. **Critical Evaluator**
   - Role: Spot flaws and evaluate quality
   - Model: Second in COUNCIL_MODELS

3. **Practical Advisor**
   - Role: Focus on actionable insights
   - Model: Third in COUNCIL_MODELS

4. **Comprehensive Synthesizer**
   - Role: Combine perspectives
   - Model: Fourth in COUNCIL_MODELS

5. **Council Chairman**
   - Role: Synthesize final answer
   - Model: CHAIRMAN_MODEL
   - Can delegate to other agents

## Files Modified

```
✅ backend/crew_council.py       (NEW - CrewAI implementation)
✅ backend/main.py               (Added /message/crew endpoint)
✅ frontend/src/components/Settings.jsx  (Added toggle UI)
✅ frontend/src/api.js           (Added mode detection)
✅ pyproject.toml                (Added crewai dependency)
✅ test_crew_integration.py      (NEW - Test script)
✅ CREWAI_INTEGRATION.md         (NEW - Full docs)
```

## Next Steps

1. **Try Both Modes**
   - Ask the same question in both modes
   - Compare response quality and speed

2. **Customize Agents**
   - Edit roles in `backend/crew_council.py`
   - Add new specialized agents

3. **Monitor Performance**
   - Check agent reasoning in verbose mode
   - Optimize for your use case

4. **Experiment with Workflows**
   - Try hierarchical process
   - Enable tool integration
   - Add custom validation

## Support

- Full docs: `CREWAI_INTEGRATION.md`
- Test script: `test_crew_integration.py`
- Config: `backend/config.py`
- Implementation: `backend/crew_council.py`

---

**Pro Tip:** Start with Standard mode for speed, switch to CrewAI mode for complex queries that need deeper reasoning.
