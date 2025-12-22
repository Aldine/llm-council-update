# Testing Framework Documentation

## Overview

LLM Council now has a comprehensive testing setup with three layers of testing:

1. **Frontend Unit Tests** - Vitest + React Testing Library
2. **Backend Unit Tests** - PyTest with FastAPI TestClient
3. **E2E Tests** - Cypress for full integration testing

## Why These Testing Frameworks?

### Frontend: Vitest ✓
**Chosen over alternatives** (Jest, Mocha, Jasmine)

- **Native Vite integration** - Instant HMR, same config as dev
- **Lightning fast** - Uses esbuild, parallel execution
- **Modern** - ESM support, TypeScript, JSX out-of-the-box
- **Compatible** - Jest-compatible API, easy migration
- **UI mode** - Visual test runner with `npm run test:ui`

### Backend: PyTest ✓
**Chosen over alternatives** (unittest, nose2, Robot Framework)

**Why PyTest for FastAPI:**
- **FastAPI recommended** - Official FastAPI docs use PyTest
- **Async support** - `pytest-asyncio` for async/await patterns
- **Fixtures** - Powerful dependency injection for test setup
- **httpx integration** - Built-in async HTTP client testing
- **Rich ecosystem** - 1000+ plugins, excellent tooling

**Alternatives considered:**
- ❌ **unittest** - Too verbose, no async support, limited fixtures
- ❌ **nose2** - Less active, smaller ecosystem
- ❌ **Robot Framework** - Better for acceptance testing, overkill for API testing
- ❌ **Behave** - BDD framework, not needed for technical API tests

### E2E: Cypress ✓
**Chosen over alternatives** (Playwright, Selenium)

- **Best DX** - Interactive test runner, time-travel debugging
- **Reliable** - Auto-waits, retry logic, screenshot/video capture
- **React support** - Component testing for isolated UI tests
- **Rich API** - Custom commands, network stubbing, fixtures
- **Mature ecosystem** - Large community, excellent docs

## Test Structure

```
llm-council-master/
├── frontend/
│   ├── src/
│   │   └── test/
│   │       ├── setup.js          # Vitest global setup
│   │       └── api.test.js        # API client tests
│   ├── cypress/
│   │   ├── e2e/
│   │   │   └── conversations.cy.js  # E2E user flows
│   │   └── support/
│   │       ├── commands.js        # Custom Cypress commands
│   │       └── e2e.js             # Global test config
│   ├── vitest.config.js
│   └── cypress.config.js
└── tests/
    ├── conftest.py              # PyTest fixtures & config
    ├── test_main.py             # API endpoint tests
    └── test_storage.py          # Storage layer tests
```

## Running Tests

### Frontend Unit Tests (Vitest)

```bash
cd frontend

# Run once
npm test

# Watch mode
npm test -- --watch

# UI mode (interactive)
npm run test:ui

# Coverage report
npm run test:coverage
```

### Backend Tests (PyTest)

```bash
# From project root

# Run all tests
uv run pytest -v

# Run specific test file
uv run pytest tests/test_storage.py -v

# Run with coverage
uv run pytest --cov=backend --cov-report=html

# Run only fast tests (exclude slow/integration)
uv run pytest -m "not slow"

# Parallel execution (install pytest-xdist)
uv run pytest -n auto
```

### E2E Tests (Cypress)

```bash
cd frontend

# Interactive mode (recommended for development)
npm run test:e2e

# Headless mode (CI/CD)
npm run test:e2e:headless
```

**Prerequisites:**
- Backend running on http://localhost:8001
- Frontend running on http://localhost:5173

## Test Coverage

### Frontend (6 tests)
- ✓ API client: list conversations
- ✓ API client: create conversation
- ✓ API client: delete conversation
- ✓ API client: send message (standard mode)
- ✓ API client: send message (CrewAI mode)
- ✓ API client: error handling

### Backend (22 tests)
- ✓ API health check
- ✓ List conversations
- ✓ Create conversation
- ✓ Get conversation
- ✓ Delete conversation (NEW)
- ✓ Send message endpoint
- ✓ Authentication (login, token refresh, current user)
- ✓ Storage CRUD operations
- ✓ Conversation title updates
- ✓ Error handling (404s, validation)

### E2E (8 test scenarios)
- ✓ Create new conversation
- ✓ Send message in standard mode
- ✓ Toggle CrewAI mode and send message
- ✓ Delete conversation with confirmation
- ✓ List multiple conversations
- ✓ Switch between conversations
- ✓ API integration (create, delete via REST)
- ✓ Verify deletion (404 response)

## Test Configuration

### Vitest (vitest.config.js)
```javascript
{
  test: {
    globals: true,
    environment: 'jsdom',      // DOM simulation
    setupFiles: './src/test/setup.js',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html']
    }
  }
}
```

### PyTest (pyproject.toml)
```toml
[tool.pytest.ini_options]
pythonpath = [""]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "-ra -q --strict-markers"
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests"
]
```

### Cypress (cypress.config.js)
```javascript
{
  e2e: {
    baseUrl: 'http://localhost:5173',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx}',
  },
  env: {
    apiUrl: 'http://localhost:8001'
  }
}
```

## Best Practices

### Frontend Tests
1. **Mock external dependencies** - Use `vi.fn()` for fetch, localStorage
2. **Test behavior, not implementation** - Focus on user-facing results
3. **Clean up after tests** - Use `afterEach(cleanup)` from @testing-library/react
4. **Isolate tests** - Each test should be independent

### Backend Tests
1. **Use fixtures** - Share setup logic across tests
2. **Test happy and sad paths** - Include error cases (404, validation)
3. **Use TestClient** - Faster than full HTTP server
4. **Mock external APIs** - Don't call OpenRouter in tests
5. **Temporary storage** - Use `tmp_path` for isolated file operations

### E2E Tests
1. **Start with clean state** - Reset database/localStorage before each test
2. **Wait for elements** - Cypress auto-waits, but use explicit waits for async ops
3. **Use data-testid** - More reliable than CSS selectors
4. **Create custom commands** - Reusable actions like `cy.login()`
5. **Mock backend when needed** - Use `cy.intercept()` for API stubs

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: cd frontend && npm install
      - run: cd frontend && npm test -- --run
      
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install uv
      - run: uv sync
      - run: uv run pytest -v
      
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: cypress-io/github-action@v5
        with:
          working-directory: frontend
          start: |
            cd .. && uv run uvicorn backend.main:app
            cd frontend && npm run dev
          wait-on: 'http://localhost:8001, http://localhost:5173'
```

## Troubleshooting

### Vitest: Module not found
- Check `vitest.config.js` has correct `resolve.alias`
- Ensure test files match pattern `*.test.js` or `*.spec.js`

### PyTest: Import errors
- Verify `pythonpath = [""]` in `pyproject.toml`
- Run from project root, not `tests/` directory
- Check `PYTHONPATH` environment variable

### Cypress: Cannot connect
- Verify backend/frontend are running on expected ports
- Check `baseUrl` in `cypress.config.js`
- Review CORS settings in backend

### Coverage not working
- **Vitest**: Install `@vitest/coverage-v8` or `@vitest/coverage-istanbul`
- **PyTest**: Install `pytest-cov` (already in dependencies)

## Next Steps

1. **Add component tests** - Test React components in isolation
2. **Visual regression testing** - Screenshot comparison with Percy/Chromatic
3. **API contract testing** - Pact for consumer-driven contracts
4. **Performance testing** - Lighthouse CI, k6 for load testing
5. **Mutation testing** - Stryker for test quality verification

## Resources

- [Vitest Docs](https://vitest.dev)
- [PyTest Docs](https://docs.pytest.org)
- [Cypress Docs](https://docs.cypress.io)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [React Testing Library](https://testing-library.com/react)
