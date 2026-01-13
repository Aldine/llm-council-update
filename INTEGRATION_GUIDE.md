# 🎯 Confucius Agent Integration Guide

## Status: READY FOR PRODUCTION

**Integration Health Score:** 83.3% ✅  
**Core Components:** Fully operational  
**Context Scaffolding:** ✅ Working  
**Ralph Loops:** ✅ Working  
**Memory Persistence:** ✅ Working

---

## 🚀 Quick Start Integration

### 1. Install the Dependency

```bash
# Option A: Install from pip (when published)
pip install confucius-agent

# Option B: Dev mode (current setup)
cd /path/to/confucius-agent
pip install -e .
```

### 2. Verify Integration

```bash
python verify_confucius_dependency.py
```

**Expected:** 83-100% health score

### 3. Configure API Keys

Create `.env` file:
```bash
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
```

### 4. Test Basic Usage

```python
from confucius_agent import Orchestrator, MemoryManager

memory = MemoryManager()
agent = Orchestrator(
    llm_client=your_llm,
    extensions=[],
    memory_manager=memory
)

result = agent.run("Your task here")
```

---

## 📚 Core Integration Patterns

### Pattern 1: Context Scaffolding (Session Persistence)

**Use Case:** Maintain context across multiple sessions or agent runs

```python
from confucius_agent import MemoryManager
import json

# Session 1: Build context
memory = MemoryManager()
memory.add_to_short_term("project_name", "LLM Council")
memory.add_to_short_term("tech_stack", ["FastAPI", "React"])
memory.promote_to_long_term(["project_name", "tech_stack"])

# Save context
with open("context.json", "w") as f:
    json.dump(memory.export_state(), f)

# Session 2: Restore context
with open("context.json", "r") as f:
    state = json.load(f)
    
memory = MemoryManager()
memory.import_state(state)

# Context is restored!
project = memory.get_from_long_term("project_name")
```

**Benefits:**
- ✅ Persist agent knowledge across runs
- ✅ No need for lengthy context in every prompt
- ✅ Hierarchical memory (short-term vs long-term)
- ✅ Automatic compression when memory fills

---

### Pattern 2: Ralph Loop (Autonomous Iteration)

**Use Case:** Run tasks that require multiple attempts until completion

```python
from confucius_agent import RalphOrchestrator, RalphLoopConfig

config = RalphLoopConfig(
    completion_promise="TASK_COMPLETE",  # LLM signals completion
    max_iterations=20,                    # Safety limit
    delay_seconds=2,                      # Rate limit protection
    enable_notes=True,                    # Learn from experience
    notes_path="./agent_notes"
)

ralph = RalphOrchestrator(
    llm_client=your_llm,
    extensions=[bash_ext, file_ext],
    config=config
)

# Run autonomously until complete
result = ralph.run_ralph_loop("Deploy application to production")

print(f"Completed in {result['iterations']} iterations")
```

**Benefits:**
- ✅ No manual iteration loops
- ✅ Automatic completion detection
- ✅ Note-taking for learning
- ✅ Safety limits (max iterations)
- ✅ Rate limit protection

---

### Pattern 3: Custom Extensions (Domain Tools)

**Use Case:** Add domain-specific capabilities to agents

```python
from confucius_agent.orchestrator import Extension, Action, RunContext

class DatabaseExtension(Extension):
    def __init__(self, db_connection):
        super().__init__("database")
        self.db = db_connection
    
    def can_handle(self, action: Action) -> bool:
        return action.type.value == "database_query"
    
    def execute(self, action: Action, context: RunContext) -> Action:
        try:
            query = action.content
            results = self.db.execute(query)
            
            # Store in shared context
            context.set_artifact("query_results", results)
            
            action.result = f"Query returned {len(results)} rows"
        except Exception as e:
            action.error = str(e)
        
        return action

# Use in orchestrator
agent = Orchestrator(
    llm_client=llm,
    extensions=[DatabaseExtension(db)],
    memory_manager=memory
)
```

**Benefits:**
- ✅ Modular tool system
- ✅ Shared context via `RunContext`
- ✅ Lifecycle hooks (input/output transformation)
- ✅ Clean separation of concerns

---

### Pattern 4: Multi-Agent Collaboration (Shared Memory)

**Use Case:** Multiple specialized agents working on same task

```python
from confucius_agent import Orchestrator, MemoryManager

# ONE shared memory for all agents
memory = MemoryManager()

# Create specialized agents
architect = Orchestrator(
    llm_client=claude,
    memory_manager=memory,  # Shared!
    system_prompt="You are a software architect"
)

implementer = Orchestrator(
    llm_client=gpt,
    memory_manager=memory,  # Shared!
    system_prompt="You are a developer"
)

reviewer = Orchestrator(
    llm_client=gemini,
    memory_manager=memory,  # Shared!
    system_prompt="You are a code reviewer"
)

# Workflow
design = architect.run("Design user API")
code = implementer.run("Implement the design")  # Reads from memory
review = reviewer.run("Review the implementation")  # Reads from memory
```

**Benefits:**
- ✅ Agents share context automatically
- ✅ No explicit data passing needed
- ✅ Hierarchical memory management
- ✅ Support for different LLMs per agent

---

## 🔧 Integration Checklist

Use this when integrating confucius-agent into a new project:

### Setup Phase
- [ ] Install: `pip install confucius-agent` or `pip install -e .`
- [ ] Verify: Run `python verify_confucius_dependency.py`
- [ ] Configure: Create `.env` with API keys
- [ ] Test: Run `python examples/integration_demo.py`

### Development Phase
- [ ] Import core classes: `Orchestrator`, `MemoryManager`
- [ ] Create memory manager for context persistence
- [ ] Build custom `Extension` classes for domain tools
- [ ] Use `RalphOrchestrator` for autonomous tasks
- [ ] Enable note-taking in `RalphLoopConfig`

### Production Phase
- [ ] Add `.github/copilot-instructions.md` to repository
- [ ] Document custom extensions
- [ ] Set up context persistence strategy
- [ ] Configure logging and monitoring
- [ ] Test with real LLM providers

---

## 🎓 Learning Resources

### Example Files
1. **`examples/integration_demo.py`** - Complete integration examples
2. **`verify_confucius_dependency.py`** - Health check script
3. **`.github/copilot-instructions.md`** - Copilot integration guide

### Key Documentation
- **Memory Management:** See `src/confucius_agent/orchestrator.py`
- **Ralph Loops:** See `src/confucius_agent/ralph_integration.py`
- **Extensions:** See `src/confucius_agent/extensions.py`
- **Notes:** See `src/confucius_agent/notes.py`

---

## 🚨 Common Integration Issues

### Issue 1: "Module not found"
**Solution:**
```bash
pip install -e /path/to/confucius-agent
# Then restart your editor
```

### Issue 2: Ralph loop not stopping
**Check:**
- LLM prompt includes instruction to return completion promise
- `config.completion_promise` matches LLM output
- `max_iterations` is reasonable (start with 10-20)

### Issue 3: Memory not persisting
**Check:**
- Call `memory.promote_to_long_term()` for important data
- Use `memory.export_state()` / `import_state()` for cross-session
- Verify JSON serialization of stored data

### Issue 4: Copilot not suggesting confucius-agent
**Solution:**
1. Ensure `.github/copilot-instructions.md` exists
2. Restart VS Code
3. Verify with `python verify_confucius_dependency.py`
4. Check that import works: `from confucius_agent import Orchestrator`

---

## 📊 Integration Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| **Health Score** | >80% | 83.3% ✅ |
| **Core Classes Available** | All | All ✅ |
| **Extension System** | Working | Working ✅ |
| **Memory Persistence** | Working | Working ✅ |
| **Ralph Loops** | Working | Working ✅ |
| **LLM Clients** | Optional | Partial ⚠️ |

---

## 🎯 Next Steps

### For New Projects
1. Copy `.github/copilot-instructions.md` to your repo
2. Create custom extensions for your domain
3. Set up memory persistence strategy
4. Configure Ralph loops for autonomous tasks

### For Existing Projects
1. Refactor manual loops → `RalphOrchestrator`
2. Replace dict state → `MemoryManager`
3. Convert helper functions → `Extension` classes
4. Add cross-session context persistence

---

## ✅ Production Readiness

**Status:** READY ✅

The confucius-agent dependency is properly integrated and ready for production use:

- ✅ Package properly installed and importable
- ✅ Core orchestration working
- ✅ Memory scaffolding operational
- ✅ Ralph loop pattern functional
- ✅ Extension system available
- ✅ Copilot instructions configured
- ✅ Example code provided
- ✅ Verification script available

**Recommended:** Start with Pattern 1 (Context Scaffolding) and Pattern 2 (Ralph Loops) for immediate value.

---

*Last updated: January 13, 2026*  
*Integration Health: 83.3%*  
*Status: Production Ready*
