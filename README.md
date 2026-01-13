# 🎭 Confucius Agent

**AI Agent Scaffold with Ralph Wiggum Loop Pattern**

A production-ready, globally-installable agent framework that combines:
- **Confucius Paper's** hierarchical memory, note-taking, and modular extensions
- **Ralph Wiggum's** autonomous iteration until completion pattern
- **Multi-provider support**: Claude, GPT-5.2, Gemini, and 100+ models via OpenRouter

## 🚀 Quick Install (Global)

```bash
# Install with all providers
pip install confucius-agent[all]

# Or install specific providers only
pip install confucius-agent[anthropic]      # Claude only
pip install confucius-agent[openai]         # GPT/OpenAI only
pip install confucius-agent[google]         # Gemini only
pip install confucius-agent[openrouter]     # OpenRouter (100+ models)
```

Or from source:
```powershell
# Windows
cd confucius-agent
.\install.ps1

# Linux/Mac
cd confucius-agent
chmod +x install.sh
./install.sh
```

## 🤖 Supported LLM Providers

| Provider | Models | Environment Variable |
|----------|--------|---------------------|
| **Anthropic** | claude-4, claude-sonnet-4, claude-opus-4 | `ANTHROPIC_API_KEY` |
| **OpenAI** | gpt-5.2, gpt-4, gpt-4o, o1, o3 | `OPENAI_API_KEY` |
| **Google** | gemini-2.0-flash, gemini-1.5-pro, gemini-pro | `GOOGLE_API_KEY` |
| **OpenRouter** | 100+ models from all providers | `OPENROUTER_API_KEY` |

### Model Aliases
```python
# These shortcuts work:
"claude"     → claude-sonnet-4-20250514
"gpt-5.2"    → gpt-5.2-turbo
"gpt5"       → gpt-5.2-turbo
"gemini"     → gemini-2.0-flash
"llama"      → meta-llama/llama-3.1-405b-instruct (via OpenRouter)
```

## 📦 What You Get

After installation, these tools are available **globally** in any terminal:

| Command | Description |
|---------|-------------|
| `confucius run "task"` | Run AI agent on a coding task |
| `ralph-loop "cmd"` | Loop a command until completion |
| `confucius notes` | Search past session notes |
| `confucius init` | Initialize in current workspace |
| `cca` | Alias for `confucius` |

## 🎯 Usage

### Run AI Agent on a Task
```bash
confucius run "Fix the failing tests in auth.py" -w ./my-project -v
```

### Ralph Loop (Simple Command Iteration)
```bash
ralph-loop "npm test" --completion "All tests passed" --max-iter 20
ralph-loop "pytest" --completion "passed" --max-iter 10 --delay 3
```

### Python API
```python
from confucius_agent import create_agent

agent = create_agent(
    workspace="./my-project",
    model="claude-sonnet-4-20250514",
    completion_promise="TASK_COMPLETE",
    max_iterations=20
)

result = agent.run_ralph_loop("Fix the bug in auth.py")
print(f"Success: {result['success']}")
print(f"Iterations: {result['ralph_iterations']}")
```

## 🖥️ VS Code Integration

After installation, tasks are available in **all VS Code instances**:

1. Press `Ctrl+Shift+P` → "Tasks: Run Task"
2. Look for tasks starting with 🎭:
   - **🎭 Confucius: Run AI Agent**
   - **🎭 Ralph Loop: Run Command Until Complete**
   - **🎭 Ralph Loop: Quick npm test**
   - **🎭 Ralph Loop: Quick pytest**
   - **🎭 Confucius: Search Notes**

### Keyboard Shortcuts
- `Ctrl+Shift+C` - Run AI Agent
- `Ctrl+Shift+R` - Start Ralph Loop

## 🏗️ Architecture

Based on the [Confucius Code Agent paper](https://arxiv.org/abs/2512.10398):

```
┌─────────────────────────────────────────────────────────┐
│                   Ralph Loop Controller                  │
│        (Iterate until completion promise found)          │
├─────────────────────────────────────────────────────────┤
│                 Confucius Orchestrator                   │
│    ┌─────────────┬──────────────┬─────────────────┐     │
│    │   Memory    │  Extensions  │   Note-Taking   │     │
│    │  Manager    │   System     │     Agent       │     │
│    │ (F1: AX)    │  (F3: DX)    │   (F2: AX/UX)   │     │
│    └─────────────┴──────────────┴─────────────────┘     │
├─────────────────────────────────────────────────────────┤
│                    LLM Clients                           │
│   (Claude, GPT-5.2, Gemini, OpenRouter, Mock)           │
└─────────────────────────────────────────────────────────┘
```

### Key Features

**F1: Hierarchical Memory & Context Compression**
- Session/entry/runnable memory scopes
- Automatic compression when context grows
- Preserves essential state for long-horizon reasoning

**F2: Note-Taking with Hindsight**
- Persistent Markdown notes per session
- Special "hindsight notes" for failures
- Searchable across sessions

**F3: Modular Extensions**
- BashExtension - Execute shell commands
- FileEditExtension - Create/edit/delete files
- FileReadExtension - Read file contents
- FileSearchExtension - Search codebase
- PlanningExtension - Task decomposition
- Easy to add custom extensions

## 📁 Project Structure

```
confucius-agent/
├── src/confucius_agent/
│   ├── __init__.py        # Main exports & create_agent()
│   ├── orchestrator.py    # Core orchestration loop
│   ├── notes.py           # Note-taking system
│   ├── extensions.py      # Tool extensions
│   ├── ralph_integration.py  # Ralph loop pattern
│   ├── llm_clients.py     # LLM API clients
│   └── cli.py             # Command-line interface
├── vscode-extension/      # VS Code extension
├── global-tasks.json      # User-level VS Code tasks
├── install.ps1            # Windows installer
├── install.sh             # Linux/Mac installer
└── pyproject.toml         # Package configuration
```

## 🤖 LLM Provider Support

Supports multiple LLM providers with easy model aliases:

### Supported Providers

| Provider | Models | Env Variable |
|----------|--------|--------------|
| **Anthropic** | Claude 4 Opus, Sonnet, Haiku | `ANTHROPIC_API_KEY` |
| **OpenAI** | GPT-5.2, GPT-4o, GPT-4.1, o1, o3 | `OPENAI_API_KEY` |
| **Google** | Gemini 2.5, 2.0, 1.5 Pro/Flash | `GOOGLE_API_KEY` |
| **OpenRouter** | Any model via unified API | `OPENROUTER_API_KEY` |

### Model Aliases

Use convenient aliases instead of full model names:

```python
# Claude aliases
"claude-opus", "opus"           → claude-sonnet-4-20250514 (Claude 4 Opus)
"claude-sonnet", "sonnet"       → claude-sonnet-4-20250514
"claude-haiku", "haiku"         → claude-3-5-haiku-20241022

# GPT aliases  
"gpt-5", "gpt-5.2"              → gpt-5.2-preview-2025-06-30
"gpt-4o", "4o"                  → gpt-4o
"gpt-4.1"                       → gpt-4.1-2025-04-14
"o1", "o1-preview"              → o1-preview
"o3", "o3-preview"              → o3-preview-2025-06-01

# Gemini aliases
"gemini-2.5", "gemini-pro"      → gemini-2.5-pro
"gemini-2.0", "gemini-flash"    → gemini-2.0-flash
"gemini-1.5"                    → gemini-1.5-pro
```

### Usage with Different Providers

```python
from confucius_agent import create_agent

# Claude (default)
agent = create_agent(model="claude-sonnet")

# GPT-5.2
agent = create_agent(model="gpt-5.2")

# Gemini
agent = create_agent(model="gemini-2.5")

# OpenRouter (any model)
agent = create_agent(model="openrouter/anthropic/claude-sonnet-4")
```

### CLI with Different Models

```bash
# Use GPT-5.2
confucius run "Fix the bug" --model gpt-5.2

# Use Gemini
confucius run "Refactor this code" --model gemini-2.5

# Use OpenRouter
confucius run "Write tests" --model openrouter/openai/gpt-4o
```

## 🔧 Configuration

### Environment Variables
```bash
# Anthropic (Claude)
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenAI (GPT-5.2, GPT-4o, o1, o3)
export OPENAI_API_KEY="sk-..."

# Google (Gemini)
export GOOGLE_API_KEY="..."

# OpenRouter (unified access to all models)
export OPENROUTER_API_KEY="sk-or-..."
```

### VS Code Settings
```json
{
    "confucius.model": "claude-sonnet-4-20250514",
    "confucius.maxIterations": 20,
    "confucius.completionPromise": "TASK_COMPLETE",
    "confucius.enableNotes": true
}
```

### Workspace Config
Run `confucius init` to create `.confucius/config.toml`:
```toml
[agent]
model = "claude-sonnet-4-20250514"
max_iterations = 20
completion_promise = "TASK_COMPLETE"

[notes]
enabled = true
path = ".confucius/notes"
```

## 🧪 Testing Without API

Use the mock client for testing:
```python
from confucius_agent import create_agent, MockClient

agent = create_agent(
    workspace=".",
    model="mock"  # Uses MockClient
)
```

## 🆚 Comparison with Original Tools

| Feature | Claude Code Ralph Wiggum | This Implementation |
|---------|-------------------------|---------------------|
| Dependencies | Claude Code, jq | Python only |
| Platform | Limited | Windows, Linux, Mac |
| VS Code Integration | Plugin only | Global + Extension |
| Customizable | Limited | Full source access |
| Note-taking | No | Yes (from Confucius) |
| Memory management | Basic | Hierarchical |

## 📚 Learn More

- [Confucius Code Agent Paper](https://arxiv.org/abs/2512.10398)
- [Ralph Wiggum Pattern (Claude Code)](https://forum.cursor.com/t/introduce-ralph-in-cursor/147764)
- [SWE-Agent (Similar Tool)](https://github.com/SWE-agent/SWE-agent)
- [OpenHands SDK](https://github.com/OpenHands/software-agent-sdk)

## 📄 License

MIT License - Free to use and modify.
