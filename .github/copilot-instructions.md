# LLM Council - AI Agent Instructions

## Architecture Overview

This is a 3-stage LLM deliberation system where multiple models collaboratively answer questions through parallel querying, anonymized peer review, and final synthesis. **Key innovation**: Stage 2 anonymizes responses as "Response A, B, C..." to prevent bias, then de-anonymizes client-side for transparency.

**Tech Stack**: FastAPI backend (Python 3.10+, async httpx, OpenRouter API) + React/Vite frontend + JSON file storage

**Critical Ports**: Backend runs on **8001** (not 8000), frontend on 5173

## Project-Specific Patterns

### Backend Structure (`backend/`)

**Module Execution**: Always run backend as `uv run python -m backend.main` from project root. All imports use relative syntax (`from .config import ...`) - this is intentional for Python's module system.

**3-Stage Flow** (`backend/council.py`):
1. `stage1_collect_responses()`: Parallel queries via `asyncio.gather()`, returns list of `{model, response}` dicts
2. `stage2_collect_rankings()`: Creates `label_to_model` mapping, prompts models with strict format requirements, returns `(rankings_list, label_to_model_dict)` tuple
3. `stage3_synthesize_final()`: Chairman synthesizes final answer with full context

**Graceful Degradation**: If individual models fail in `openrouter.py`, return `None` for that model but continue with successful responses. Never fail entire request due to single model failure.

**Prompt Engineering**: Stage 2 prompt requires strict format (`FINAL RANKING:` header + numbered list) to enable reliable parsing. See `parse_ranking_from_text()` for format expectations and fallback regex.

**Configuration** (`backend/config.py`): Models are OpenRouter identifiers (e.g., `"openai/gpt-5.1"`). Chairman can be same as council member. Uses `.env` for `OPENROUTER_API_KEY`.

**Storage** (`backend/storage.py`): JSON files in `data/conversations/`. Metadata (label_to_model, aggregate_rankings) is **NOT persisted** - only returned in API responses and stored in UI state.

### Frontend Patterns (`frontend/src/`)

**Data Flow**: `App.jsx` orchestrates state, passes metadata to child components. Assistant messages structure: `{role, stage1, stage2, stage3, metadata}` where metadata includes `labelToModel` and `aggregateRankings`.

**De-anonymization** (`Stage2.jsx`): Models receive anonymous labels, but UI shows real names in **bold** via `deAnonymizeText()` function. Display includes raw evaluation text + extracted ranking for validation/transparency.

**Styling Convention**: All ReactMarkdown components must be wrapped in `<div className="markdown-content">` for proper 12px padding (defined globally in `index.css`). Light mode theme with #4a90e2 primary color.

**API Client** (`api.js`): Hardcoded to `http://localhost:8001`. Update CORS in `backend/main.py` if changing ports (currently allows 5173, 3000).

### Development Workflow

**Start Application**:
```bash
# Option 1: Use start script (spawns both processes)
./start.sh

# Option 2: Manual (two terminals)
# Terminal 1:
uv run python -m backend.main

# Terminal 2:
cd frontend && npm run dev
```

**Dependency Management**: `uv sync` for Python (uses `pyproject.toml`), `npm install` for frontend

**Model Configuration**: Edit `COUNCIL_MODELS` and `CHAIRMAN_MODEL` in `backend/config.py` - no UI configuration yet

## Common Gotchas

- **Import errors**: Never run backend from `backend/` directory or use absolute imports
- **Parse failures**: If models don't follow Stage 2 format, fallback extracts any "Response X" patterns in order seen
- **CORS issues**: Frontend origin must match allowed list in `main.py` middleware
- **Metadata loss**: Metadata only exists in API responses + UI state, not persisted to JSON

## Key Files Reference

- `backend/council.py`: Core 3-stage logic, prompt engineering, ranking parser
- `backend/openrouter.py`: Parallel async queries with graceful degradation
- `backend/storage.py`: JSON persistence (excludes metadata deliberately)
- `frontend/src/App.jsx`: State orchestration, metadata management
- `frontend/src/components/Stage2.jsx`: Client-side de-anonymization example
- `CLAUDE.md`: Detailed architectural decisions and future enhancement ideas
