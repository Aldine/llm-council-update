# Contributing to Confucius Agent

Thank you for your interest in contributing! 🎭

## Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/confucius-agent.git
   cd confucius-agent
   ```

3. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

4. **Install in development mode**
   ```bash
   pip install -e ".[dev,all]"
   ```

## Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**

3. **Run tests**
   ```bash
   pytest tests/
   ```

4. **Format code**
   ```bash
   black src/
   isort src/
   ```

5. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request**

## Code Style

- Use [Black](https://black.readthedocs.io/) for formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Add type hints where possible
- Document public APIs with docstrings

## Project Structure

```
confucius-agent/
├── src/confucius_agent/     # Main package
│   ├── orchestrator.py      # Core orchestration
│   ├── notes.py             # Note-taking system
│   ├── extensions.py        # Tool extensions
│   ├── llm_clients.py       # LLM API clients
│   ├── ralph_integration.py # Ralph loop pattern
│   └── cli.py               # Command-line interface
├── tests/                   # Test suite
├── vscode-extension/        # VS Code extension
└── docs/                    # Documentation
```

## Adding a New LLM Provider

1. Open `src/confucius_agent/llm_clients.py`
2. Create a new client class inheriting from `LLMClient`
3. Implement the `generate()` method
4. Add to `create_llm_client()` factory
5. Add model aliases to `MODEL_ALIASES`
6. Update `pyproject.toml` with optional dependency
7. Update README with documentation

Example:
```python
class MyProviderClient(LLMClient):
    """Client for MyProvider API."""
    
    def __init__(self, model: str = "my-model"):
        try:
            from myprovider import Client
            self.client = Client(api_key=os.environ.get("MY_PROVIDER_API_KEY"))
        except ImportError:
            raise ImportError("pip install myprovider")
        self.model = model
    
    def generate(self, messages: List[Dict], **kwargs) -> str:
        response = self.client.chat(
            model=self.model,
            messages=messages
        )
        return response.text
```

## Adding a New Extension

1. Open `src/confucius_agent/extensions.py`
2. Create a new class inheriting from `Extension`
3. Implement `get_actions()` and `execute()`
4. Export from `__init__.py`

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding or fixing tests
- `chore:` Maintenance tasks

## Questions?

Open an issue or discussion on GitHub!
