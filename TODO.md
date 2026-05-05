# TODO

## Backlog

### Phase 1: Infrastructure Modernization

- [ ] **1.2 Configure optional dependency groups**
  - Create `flask` extra: flask, flask-cors, flask-restful
  - Create `async` extra: httpx, aiofiles (or anyio)
  - Create `async-flask` extra: quart (depends on flask + async)
  - Create `fake-server` extra: pymongo, flask
  - Create `dev` extra: pytest, pytest-asyncio, ruff, mypy, coverage
  - Create `run` extra: gunicorn, eventlet
  - Document extras in README

**Note:** Tasks 1.2 (flask/fake-server extras) and 1.10 (pypi-template) were superseded by Task 1.1. Flask packages are now core dependencies, and metadata is in pyproject.toml.

- [ ] **1.5 Configure ruff for linting**
  - Add `[tool.ruff]` section to pyproject.toml
  - Configure target-version = "py39" (or higher)
  - Enable core rules: E (error), F (pyflakes), I (isort)
  - Configure line length (88 or 100)
  - Add `__init__.py` to `extend-ignore` for F401
  - Update Makefile `lint` target to use `uv run ruff`
  - Fix all existing lint errors

**Note:** Task 1.5 (Configure ruff) was completed as part of Task 1.1 - pyproject.toml already includes ruff configuration.

- [ ] **1.6 Configure mypy for type checking**
  - Add `[tool.mypy]` section to pyproject.toml
  - Configure python_version = "3.9" (or higher)
  - Start with permissive settings (warn_return_any = false initially)
  - Add per-file ignores for fake/ module (Flask heavy)
  - Update Makefile to use `uv run mypy`
  - Update pyrightconfig.json to align with mypy settings



- [ ] **1.9 Create CHANGELOG.md**
  - Initialize with existing version history (0.1.5)
  - Document format: [Unreleased], [0.2.0], etc.
  - Add placeholder for Phase 1 completion
  - Follow Keep a Changelog format

- [ ] **1.10 Remove .pypi-template dependency**
  - Extract all metadata from .pypi-template
  - Incorporate into pyproject.toml
  - Delete .pypi-template file
  - Update any CI/CD that references it

### Phase 2: Async Implementation

- [ ] **2.1 Add async HTTP client support**
  - Add `httpx` as optional dependency for async HTTP
  - Consider also supporting `aiohttp` (or just httpx for both)
  - Create `oatk/async_client.py` module
  - Implement async HTTP client abstraction
  - Keep requests for sync operations

- [ ] **2.2 Design AsyncOAuthToolkit class API**
  - Create `oatk/async_toolkit.py` module
  - Define class `AsyncOAuthToolkit`
  - Mirror OAuthToolkit API for async operations
  - Implement `async using_provider()` method
  - Implement `async init_from_provider()` method
  - Implement `async with_jwks()` (if async file I/O needed)

- [ ] **2.3 Implement async token operations**
  - Implement `async validate()` method
  - Consider `run_in_executor` for CPU-bound JWT validation
  - Implement `async decode()` method (mostly sync, but async-compatible)
  - Ensure token generation remains sync (CPU-bound)

- [ ] **2.4 Create async decorators**
  - Create `authenticated_async` decorator for ASGI frameworks
  - Create `authenticated_with_claims_async` decorator
  - Make decorators framework-agnostic (work with any ASGI app)
  - Add support for request context in async context

- [ ] **2.5 Add Quart integration**
  - Create `oatk/quart.py` module
  - Implement Quart-specific decorators
  - Maintain compatibility with Flask decorators
  - Add example in `examples/quart_example.py`

- [ ] **2.6 Add FastAPI dependency injection**
  - Create `oatk/fastapi.py` module
  - Implement `OAuthToolkitDependency` class
  - Create `get_current_user` dependency
  - Create `require_claims` dependency
  - Add example in `examples/fastapi_example.py`

- [ ] **2.7 Update __init__.py exports**
  - Export `AsyncOAuthToolkit` from main module
  - Add `__all__` list to control exports
  - Update docstring with async usage examples
  - Maintain backward compatibility (OAuthToolkit unchanged)

- [ ] **2.8 Write async unit tests**
  - Create `tests/test_async_toolkit.py`
  - Test async provider initialization
  - Test async token validation
  - Test async decorators
  - Use `pytest-asyncio` for async test support

- [ ] **2.9 Add async integration tests**
  - Create `tests/integration/test_quart.py`
  - Create `tests/integration/test_fastapi.py`
  - Test async decorator with actual ASGI server
  - Use `httpx` async client for testing

### Phase 3: Testing & Documentation

- [ ] **3.1 Achieve 80% test coverage for sync code**
  - Create `tests/test_oauth_toolkit.py`
  - Test all public methods in OAuthToolkit
  - Test token creation and validation
  - Test JWKS handling
  - Test provider initialization
  - Test file and clipboard operations
  - Mock external HTTP calls (requests)

- [ ] **3.2 Write comprehensive tests for Flask decorators**
  - Create `tests/test_decorators.py`
  - Test `@authenticated` decorator
  - Test `@authenticated_with_claims` decorator
  - Test missing authorization header
  - Test invalid token handling
  - Test claim validation (exact, list, callable)
  - Use Flask test client

- [ ] **3.3 Write tests for fake OAuth server**
  - Create `tests/test_fake_server.py`
  - Test server initialization
  - Test route handlers (mock MongoDB)
  - Test token generation
  - Test authorization flow

- [ ] **3.4 Add API documentation**
  - Add docstrings to all public methods in OAuthToolkit
  - Add docstrings to AsyncOAuthToolkit
  - Add docstrings to module level
  - Use Google-style docstrings (compatible with Sphinx)
  - Document parameters, return types, exceptions

- [ ] **3.5 Create examples for async usage**
  - Create `examples/async_example.py`
  - Create `examples/quart_example.py`
  - Create `examples/fastapi_example.py`
  - Update README with async examples

- [ ] **3.6 Write migration guide**
  - Create `docs/migration.md`
  - Document differences between sync and async APIs
  - Provide code examples for common migrations
  - Document breaking changes (none expected)
  - Document new dependencies required

- [ ] **3.7 Update README with async documentation**
  - Add async section to README
  - Document installation with extras: `pip install oatk[async]`
  - Document AsyncOAuthToolkit usage
  - Document framework-specific integrations
  - Update all examples to show both sync and async

- [ ] **3.8 Set up CI/CD pipeline**
  - Create `.github/workflows/test.yml`
  - Run tests on Python 3.9, 3.10, 3.11, 3.12, 3.13
  - Run linting with ruff
  - Run type checking with mypy
  - Run security audit with pip-audit
  - Upload coverage to codecov (optional)

### Phase 4: Release Preparation

- [ ] **4.1 Update version to 0.2.0**
  - Update `__version__` in `oatk/__init__.py`
  - Update CHANGELOG.md with 0.2.0 section
  - Tag release in git

- [ ] **4.2 Create release checklist**
  - Verify all tests pass
  - Verify linting passes
  - Verify type checking passes
  - Verify documentation builds
  - Verify examples work
  - Verify backward compatibility

- [ ] **4.3 Publish to TestPyPI**
  - Build distribution: `uv build`
  - Upload to TestPyPI: `uv publish --repository testpypi`
  - Verify installation from TestPyPI
  - Test in clean environment

- [ ] **4.4 Publish to PyPI**
  - Upload to PyPI: `uv publish`
  - Verify installation from PyPI
  - Verify README renders correctly
  - Create GitHub release

- [ ] **4.5 Update documentation online**
  - Update README on GitHub
  - Create GitHub Pages or ReadTheDocs (optional)
  - Archive old documentation

- [ ] **4.6 Communicate release**
  - Create GitHub release notes
  - Update any related repositories
  - Announce in relevant channels

## Done

### Phase 1: Infrastructure Modernization

- [x] **1.1 Create pyproject.toml with hatchling backend**
  - Created `pyproject.toml` with PEP 621 compliant metadata
  - Configured hatchling as build backend with dynamic version extraction
  - Migrated all metadata from setup.py (author, description, classifiers, etc.)
  - Defined core dependencies: pyjwt, cryptography, authlib, requests, fire, python-dotenv, flask, flask-cors, flask-restful, pymongo
  - Defined optional dependency groups: dev (testing tools), run (production), async (future async support)
  - Configured ruff, mypy, pytest, and coverage tools
  - Kept setup.py temporarily for backward compatibility
  - Verified: `uv sync` works, package imports successfully
  - **Decision:** Flask packages moved to core dependencies (not optional) because they're imported unconditionally at module level

- [x] **1.3 Migrate from pyenv virtualenvs to uv managed environments**
  - Updated Makefile to use uv commands
  - Simplified environment management (single .venv)
  - Kept pyenv for Python version management
  - Verified: make install, make lint work correctly

- [x] **1.4 Add test infrastructure**
  - Created tests/ directory with comprehensive structure
  - Added conftest.py with reusable fixtures (keys, JWKS, tokens)
  - Created test_oauth_toolkit.py with 31 smoke tests (26 passing)
  - Created test_decorators.py with 18 stub tests
  - Created test_fake_server.py with 31 stub tests
  - Pytest configuration already in pyproject.toml
  - Verified: Tests run successfully, majority pass

**Note:** Task 1.6 (Configure mypy) was completed as part of Task 1.1.

- [x] **1.8 Update Makefile for uv workflow**
  - Replaced pyenv-based env creation with uv (done in Task 1.3)
  - Updated install target to use uv sync
  - Updated test target to use uv run pytest
  - Updated lint target to use uv run ruff
  - Kept pyenv for Python version management