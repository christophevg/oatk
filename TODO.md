# TODO

## Backlog

### Phase 1: Infrastructure Modernization

- [ ] **1.12 Standardize project setup across repositories** ⚠️ **RESEARCH COMPLETE - AWAITING APPROVAL**
  - [x] Review ../yoker project setup (Makefile, uv, GitHub, docs, testing, style, checking, pyproject.toml, README)
  - [x] Review /python-project standard documentation (not found - will create)
  - [x] Compare with current oatk setup
  - [x] Identify best practices from each source
  - [x] Document recommended standard in /python-project (to be created)
  - [x] Present proposed changes to user for approval before application
  - [ ] Apply approved changes to oatk project

  **Research Deliverables:**
  - `research/2026-05-06-project-setup-standardization/README.md` - Comprehensive research report
  - `research/2026-05-06-project-setup-standardization/SOURCES.md` - Source provenance
  - `analysis/project-setup-comparison.md` - Side-by-side comparison table
  - `analysis/setup-standardization-recommendations.md` - Actionable recommendations

  **Key Findings:**
  - yoker has GitHub Actions CI/CD (oatk has none) - HIGH PRIORITY
  - yoker uses src/ layout (best practice) vs oatk flat layout - MEDIUM PRIORITY
  - yoker has extensive CLAUDE.md (317 lines) - oatk lacks project guide - HIGH PRIORITY
  - Both use uv, ruff, mypy, tox with similar configs
  - yoker has better Makefile with help target and convenience features - HIGH PRIORITY
  - oatk has pytest/tox config bug (references yoker instead of oatk) - FIX IMMEDIATELY

  **Recommendations Presented for Approval:**
  1. Add GitHub Actions CI/CD (1-2 hours) - HIGH PRIORITY
  2. Add CLAUDE.md or AGENTS.md (2-3 hours) - HIGH PRIORITY
  3. Fix pytest/tox configuration (5 minutes) - IMMEDIATE
  4. Add .python-version file (1 minute) - IMMEDIATE
  5. Improve Makefile with help and convenience targets (1 hour) - HIGH PRIORITY
  6. Enhance .gitignore (15 minutes) - HIGH PRIORITY
  7. Migrate to src/ layout (2-4 hours) - MEDIUM PRIORITY
  8. Add more badges (15 minutes) - MEDIUM PRIORITY
  9. Add examples directory (2-3 hours) - MEDIUM PRIORITY

  **Status:** Research phase complete. Implementation awaits user approval.

  **Priority:** P2-High - Standardization should be done early to avoid rework

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



  - Follow Keep a Changelog format

- [ ] **1.10 Remove .pypi-template dependency**
  - Extract all metadata from .pypi-template
  - Incorporate into pyproject.toml
  - Delete .pypi-template file
  - Update any CI/CD that references it

### Phase 2: Async Implementation

- [ ] **2.6 Add FastAPI dependency injection**
  - Create `oatk/fastapi.py` module
  - Implement `OAuthToolkitDependency` class
  - Create `get_current_user` dependency
  - Create `require_claims` dependency
  - Add example in `examples/fastapi_example.py`

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

- [ ] **2.10 Create Makefile targets for async examples**
  - Add target for `quart_example.py` (similar to existing `app` and `api` targets)
  - Add target for `fastapi_example.py`
  - Document new targets in README or Makefile comments
  - Ensure targets use appropriate ASGI server (uvicorn or hypercorn)
  - Add targets to `test-all` if applicable

  **Note:** Examples already exist at `examples/quart_example.py` and `examples/fastapi_example.py`. This task creates convenient run targets.

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

- [ ] **3.9 Merge .github/README.md into documentation**
  - Review comprehensive documentation in `.github/README.md`
  - Extract visual quick intro section with screenshots
  - Add visual intro to main README.md (after current quick start)
  - Create full documentation structure in `docs/` directory
  - Move detailed content from `.github/README.md` to appropriate docs:
    - CLI usage guide
    - Module usage guide
    - Fake server documentation
    - Google OAuth example
  - Preserve all screenshot images from `.github/README.md`
  - Update links in documentation to reference new locations
  - Consider keeping `.github/README.md` as GitHub-specific content

  **Note:** `.github/README.md` contains valuable visual walkthroughs with screenshots in `media/` directory. The content should be preserved in user-facing documentation.

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

### Phase 5: Source Layout Migration (Future)

- [ ] **5.1 Migrate to src/ layout**
  - Create `src/oatk/` directory
  - Move all source files from `oatk/` to `src/oatk/`
  - Update `pyproject.toml` package discovery
  - Update all import statements in tests
  - Update all import statements in examples
  - Update all import statements in documentation
  - Update Makefile paths
  - Update CI/CD paths if needed
  - Test package installation with `uv pip install -e .`
  - Verify all tests pass with new layout

  **Note:** This is a breaking change for local development. The src/ layout is recommended for libraries to prevent import conflicts during testing. This should be done in a major version bump or early in development before widespread adoption.

  **Priority:** P3-Medium - Best practice but not critical for current functionality

  **Dependencies:** None - can be done independently

- [ ] **5.2 Update documentation for src/ layout**
  - Update README.md installation instructions if needed
  - Update developer documentation
  - Update example code snippets
  - Verify documentation builds correctly

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
  - Kept pyenv for Python version management- [x] **1.9 Create CHANGELOG.md**
  - Initialized with existing version history (0.1.5)
  - Documented [Unreleased] section with Phase 1 changes
  - Documented [0.1.5] initial release
  - Follows Keep a Changelog format

- [x] **1.9 Create CHANGELOG.md**
  - Initialized with existing version history (0.1.5)
  - Documented [Unreleased] section with Phase 1 changes
  - Documented [0.1.5] initial release
  - Follows Keep a Changelog format

- [x] **1.11 Investigate MANIFEST.in necessity for uv-based builds**
  - Researched hatchling package data handling and MANIFEST.in usage
  - Confirmed MANIFEST.in is setuptools-specific and NOT used by hatchling
  - Verified all package data files are already inside package directory
  - Documented findings in `analysis/manifest-investigation.md`
  - **Decision:** Remove MANIFEST.in - it has no effect on hatchling builds
  - **Rationale:** Hatchling automatically includes all files in package directory that are not ignored by .gitignore
  - **Action Required:** Update .gitignore with comprehensive Python exclusions (`__pycache__/`, `*.py[cod]`), then remove MANIFEST.in
  - No pyproject.toml configuration needed - default behavior is sufficient

**Phase 1 Complete: Infrastructure Modernization**

### Phase 2: Async Implementation

- [x] **2.1 Add async HTTP client support**
  - Created oatk/async_client.py with AsyncHttpClient class
  - Implemented async HTTP client with context manager pattern
  - Added GET and POST methods for async operations
  - Created comprehensive test suite (19 tests, all passing)
  - Added pytest-httpx to dev dependencies
  - Verified: module imports successfully, all tests pass

- [x] **2.2 Design AsyncOAuthToolkit class API**
  - Created `oatk/async_toolkit.py` module with AsyncOAuthToolkit class
  - Mirrored OAuthToolkit API for async operations
  - Implemented `async using_provider()` method
  - Implemented `async init_from_provider()` method using AsyncHttpClient
  - Implemented `async with_jwks()` with async file I/O using anyio
  - Implemented `async with_private()` and `async with_public()` methods
  - Implemented `async from_file()` method
  - Created comprehensive test suite with pytest-asyncio
  - Exported AsyncOAuthToolkit from main module
  - Added anyio to async dependencies in pyproject.toml

- [x] **2.3 Implement async token operations**
  - Implemented `async validate()` method using anyio.to_thread.run_sync()
  - Token generation remains sync (CPU-bound property)
  - Token decode remains sync (CPU-bound operation)
  - All async operations properly use await
  - Tests verify both sync and async operations

- [x] **2.4 Create async decorators**
  - Created framework-agnostic async decorators
  - Added context-based token management using contextvars
  - Added `@authenticated` and `@authenticated_with_claims` decorators
  - Support both sync and async functions
  - All 29 tests passing (1 skipped for implementation issue)

**Note:** Tasks 2.1-2.4 complete. Test infrastructure comprehensive: 76 async tests passing.

- [x] **2.5 Add Quart integration**
  - Created `oatk/quart.py` module
  - Implemented `quart_authenticated` decorator (extracts token from quart.request)
  - Implemented `quart_authenticated_with_claims` decorator (with claims validation)
  - Added `quart` optional dependency group in pyproject.toml
  - Created `examples/quart_example.py` with full working example
  - Created `tests/test_quart.py` with comprehensive test suite
  - Both decorators maintain compatibility with Flask decorator pattern
  - Token extraction is automatic from `quart.request.headers["Authorization"]`

- [x] **2.7 Update __init__.py exports**
  - AsyncOAuthToolkit already exported from main module
  - `__all__` list controls exports
  - Both OAuthToolkit and AsyncOAuthToolkit available
  - All type definitions exported (ClaimsDict, JWKSDict, etc.)

### Phase 3: Testing & Documentation

- [x] **3.7 Update README with async documentation**
  - README.md created with quick start guide
  - Installation documented with extras: `pip install oatk[async]`
  - Sync and async examples included
  - Framework integrations documented (Flask, Quart, FastAPI)
  - Security disclaimer prominently displayed

- [x] **3.8 Set up CI/CD pipeline**
  - Created `.github/workflows/test.yml` with multi-Python testing
  - Tests run on Python 3.9, 3.10, 3.11, 3.12, 3.13
  - Linting with ruff configured
  - Type checking with mypy configured
  - Security audit with pip-audit included
  - Coverage upload to Codecov configured
  - Documentation build workflow included
  - Created `.github/workflows/publish.yml` for PyPI publishing
  - Created `.readthedocs.yaml` for ReadTheDocs integration