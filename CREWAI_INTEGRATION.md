# CrewAI Multi-Agent Integration

## Overview

The LLM Council now supports two deliberation modes:

1. **Standard Mode** - Direct OpenRouter API calls with parallel execution
2. **CrewAI Mode** - Multi-agent orchestration with role-based agents

## Architecture

### CrewAI Agents

Each council member is implemented as a specialized CrewAI Agent:

- **Technical Analyst** - Provides technically accurate and detailed responses
- **Critical Evaluator** - Identifies strengths and weaknesses in reasoning
- **Practical Advisor** - Focuses on actionable insights and real-world applications
- **Comprehensive Synthesizer** - Combines multiple perspectives

### Chairman Agent

The Chairman uses hierarchical delegation to:
- Analyze all responses and rankings
- Identify consensus and key insights
- Resolve contradictions
- Synthesize the final authoritative answer

## Configuration

### Backend Configuration

Models are configured in `backend/config.py`:

```python
COUNCIL_MODELS = [
    "openai/gpt-5.2",
    "google/gemini-3-pro-preview",
    "anthropic/claude-sonnet-4.5",
    "x-ai/grok-4",
]

CHAIRMAN_MODEL = "google/gemini-3-pro-preview"
```

### Frontend Toggle

Enable CrewAI mode in Settings:
1. Navigate to Settings view
2. Toggle "🤖 Use CrewAI Multi-Agent Orchestration"
3. Start a new conversation to use CrewAI mode

## API Endpoints

### Standard Mode
```http
POST /api/conversations/{id}/message
```

### CrewAI Mode
```http
POST /api/conversations/{id}/message/crew
```

Both endpoints accept:
```json
{
  "content": "Your question here"
}
```

Both return:
```json
{
  "stage1": [...],
  "stage2": [...],
  "stage3": {...},
  "metadata": {
    "labelToModel": {...},
    "framework": "crewai"
  }
}
```

## Testing

Run the integration test:

```bash
uv run python test_crew_integration.py
```

## Benefits of CrewAI Mode

### Enhanced Orchestration
- **Role-based specialization** - Each agent has a defined role and expertise
- **Task delegation** - Chairman can delegate subtasks to specialized agents
- **Process control** - Sequential or hierarchical execution patterns

### Better Context Management
- **Agent memory** - Agents maintain context across tasks
- **Shared knowledge** - Agents can access each other's outputs
- **Hierarchical communication** - Chairman coordinates all agents

### Advanced Features
- **Tool integration** - Agents can use external tools
- **Multi-step reasoning** - Complex task decomposition
- **Quality control** - Built-in validation and error handling

## Performance Considerations

### Standard Mode
- ✅ Faster execution (direct parallel API calls)
- ✅ Lower latency
- ✅ Simpler debugging

### CrewAI Mode
- ✅ More sophisticated reasoning
- ✅ Better context awareness
- ✅ Enhanced collaboration patterns
- ⚠️ Slightly higher latency due to orchestration overhead

## Development Notes

### File Structure

```
backend/
├── council.py          # Standard 3-stage implementation
├── crew_council.py     # CrewAI multi-agent implementation
├── config.py          # Model configuration
└── openrouter.py      # Direct OpenRouter API client

frontend/
├── components/
│   └── Settings.jsx   # CrewAI toggle UI
└── api.js             # API client with mode switching
```

### Adding New Agents

To add a new council member in CrewAI mode:

1. Add model to `COUNCIL_MODELS` in `backend/config.py`
2. Add role configuration in `create_council_agents()` in `backend/crew_council.py`:

```python
{
    "role": "New Specialist",
    "goal": "Specific expertise goal",
    "backstory": "Agent's background and capabilities",
}
```

### Custom Workflows

CrewAI supports custom processes:

```python
crew = Crew(
    agents=[...],
    tasks=[...],
    process=Process.hierarchical,  # Chairman directs workflow
    manager_llm=CHAIRMAN_MODEL,
)
```

## Troubleshooting

### "crewAI not found" error
```bash
uv sync  # Reinstall dependencies
```

### Agent execution timeouts
Increase timeout in `backend/crew_council.py`:
```python
agent = Agent(
    ...,
    max_execution_time=300,  # 5 minutes
)
```

### OpenRouter rate limits
- Standard mode makes 4-8 parallel calls (faster but hits rate limits)
- CrewAI mode executes sequentially (slower but more reliable)

## Future Enhancements

- [ ] Streaming support for CrewAI mode
- [ ] Custom agent configurations in UI
- [ ] Tool integration (web search, calculator, etc.)
- [ ] Agent performance metrics and analytics
- [ ] Hybrid mode (combine both approaches)

## References

- [CrewAI Documentation](https://docs.crewai.com/)
- [OpenRouter API](https://openrouter.ai/docs)
- [LLM Council Architecture](./CLAUDE.md)
