# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-XX

### Added
- Initial release of Confucius Agent
- Core orchestrator based on Confucius Code Agent paper
- Ralph Wiggum loop integration for autonomous iteration
- Multi-provider LLM support:
  - Anthropic (Claude 4 Opus, Sonnet, Haiku)
  - OpenAI (GPT-5.2, GPT-4o, GPT-4.1, o1, o3)
  - Google (Gemini 2.5, 2.0, 1.5)
  - OpenRouter (100+ models)
- Hierarchical memory management (session/entry/runnable scopes)
- Note-taking system with hindsight notes for failures
- Modular extension system:
  - BashExtension
  - FileEditExtension
  - FileReadExtension
  - FileSearchExtension
  - PlanningExtension
  - ThinkingExtension
- CLI tools: `confucius`, `ralph-loop`, `cca`
- VS Code integration via global tasks
- Model aliases for convenience (e.g., `gpt-5`, `sonnet`, `gemini`)
- Mock client for testing without API keys

### Features
- F1: Hierarchical memory with automatic context compression
- F2: Note-taking with hindsight learning from failures
- F3: Modular extensions for file editing, bash, search
- Ralph loop: Iterate until completion promise found

### Documentation
- Comprehensive README with usage examples
- Contributing guidelines
- MIT License

[0.1.0]: https://github.com/Aldine/confucius-agent/releases/tag/v0.1.0
