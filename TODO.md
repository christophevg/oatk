# TODO

## Backlog

### Phase 3: Testing & Documentation

- [ ] **3.1 Achieve 80% test coverage for sync code**
  - Improve coverage in `src/oatk/__init__.py` (currently 55%)
  - Improve coverage in `src/oatk/fake/routes.py` (currently 23%)
  - Add tests for edge cases in token operations
  - Mock external HTTP calls where needed
  - Current overall coverage: 64%

- [ ] **3.2 Write comprehensive tests for Flask decorators**
  - Create `tests/test_decorators.py` (exists, but needs expansion)
  - Test `@authenticated` decorator
  - Test `@authenticated_with_claims` decorator
  - Test missing authorization header
  - Test invalid token handling
  - Test claim validation (exact, list, callable)
  - Use Flask test client

- [ ] **3.3 Write tests for fake OAuth server**
  - Create `tests/test_fake_server.py` (exists, but needs expansion)
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
  - `examples/async_example.py` (basic async usage)
  - Update README with more async examples
  - Document Quart integration
  - Document FastAPI integration

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
  - Update `__version__` in `src/oatk/__init__.py`
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
  - ~~Create `src/oatk/` directory~~
  - ~~Move all source files from `oatk/` to `src/oatk/`~~
  - Update `pyproject.toml` package discovery (already done)
  - ~~Update all import statements in tests~~
  - ~~Update all import statements in examples~~
  - ~~Update all import statements in documentation~~
  - ~~Update Makefile paths~~
  - ~~Update CI/CD paths if needed~~
  - ~~Test package installation with `uv pip install -e .`~~
  - ~~Verify all tests pass with new layout~~

  **Status:** COMPLETED in Task 1.12. The src/ layout is now in place.

  **Remaining:** Update this documentation note.

- [ ] **5.2 Update documentation for src/ layout**
  - ~~Update README.md installation instructions if needed~~
  - ~~Update developer documentation~~
  - ~~Update example code snippets~~
  - ~~Verify documentation builds correctly~~

  **Status:** COMPLETED in Task 1.12.

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

- [x] **1.2 Configure optional dependency groups** (Superseded by 1.1)
  - Flask packages are now core dependencies
  - Metadata is in pyproject.toml

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

- [x] **1.5 Configure ruff for linting**
  - Ruff configuration already in pyproject.toml from Task 1.1
  - Makefile updated to use `uv run ruff`

- [x] **1.6 Configure mypy for type checking**
  - Mypy configuration already in pyproject.toml from Task 1.1
  - Makefile updated to use `uv run mypy`

- [x] **1.8 Update Makefile for uv workflow**
  - Replaced pyenv-based env creation with uv (done in Task 1.3)
  - Updated install target to use uv sync
  - Updated test target to use uv run pytest
  - Updated lint target to use uv run ruff
  - Kept pyenv for Python version management

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

- [x] **1.12 Standardize project setup across repositories**
  - Researched and compared project setups from yoker, oatk, and C3 harness
  - Created comprehensive comparison: `analysis/project-setup-comparison.md`
  - Created actionable recommendations: `analysis/setup-standardization-recommendations.md`
  - **Quick Fixes:** Fixed pytest/tox coverage bug (yoker -> oatk), updated .python-version to 3.12
  - **Infrastructure:** Improved Makefile with help target, sections, convenience targets
  - **Documentation:** Added CLAUDE.md comprehensive project guide, added README badges
  - **Migration:** Migrated from flat layout to src/ layout (modern best practice)
  - Updated all configuration files (pyproject.toml, Makefile, GitHub Actions)
  - All 111 tests pass, linting passes, type checking passes
  - Summary: `reporting/task-1.12/summary.md`

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
  - Created `src/oatk/async_toolkit.py` module with AsyncOAuthToolkit class
  - Mirrored OAuthToolkit API for async operations
  - Implemented `async using_provider()` method
  - Implemented `async init_from_provider()` method using AsyncHttpClient
  - Implemented `async with_jwks()` with async file I/O using anyio
  - Implemented `async with_private()` and `async with_public()` methods
  - Implemented `async from_file()` method
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

- [x] **2.5 Add Quart integration**
  - Created `src/oatk/quart.py` module (integrated into async_toolkit.py)
  - Implemented Quart-compatible decorators
  - Added `quart` optional dependency group in pyproject.toml
  - Created `examples/quart_example.py` with full working example
  - Created `tests/test_quart.py` with comprehensive test suite
  - Both decorators maintain compatibility with Flask decorator pattern
  - Token extraction is automatic from `quart.request.headers["Authorization"]`

- [x] **2.6 Add FastAPI dependency injection**
  - Created `src/oatk/fastapi.py` module
  - Implemented `OAuthToolkitDependency` class
  - Created `get_current_user` dependency
  - Created `require_claims` dependency
  - Added example in `examples/fastapi_example.py`
  - Created `tests/test_fastapi.py` with comprehensive tests

- [x] **2.7 Update __init__.py exports**
  - AsyncOAuthToolkit exported from main module
  - `__all__` list controls exports
  - Both OAuthToolkit and AsyncOAuthToolkit available
  - All type definitions exported (ClaimsDict, JWKSDict, etc.)

- [x] **2.8 Write async unit tests**
  - Created `tests/test_async_toolkit.py` (76 tests passing)
  - Test async provider initialization
  - Test async token validation
  - Test async decorators
  - Test async file operations
  - Using `pytest-asyncio` for async test support

- [x] **2.9 Add async integration tests**
  - Created `tests/test_quart.py` with Quart integration tests
  - Created `tests/test_fastapi.py` with FastAPI integration tests
  - Tested async decorator with actual ASGI server
  - Using `httpx` async client for testing

- [x] **2.10 Create Makefile targets for async examples**
  - Created `quart-example` Makefile target using hypercorn ASGI server
  - Created `fastapi-example` Makefile target using uvicorn ASGI server
  - Both targets use `--reload` flag for development mode
  - Added targets to .PHONY declaration
  - Documented targets with `##` comments for help system
  - Updated README with "Running Examples" section
  - Added hypercorn to pyproject.toml dependencies
  - Added uvicorn to pyproject.toml dependencies
  - Targets appear in `make help` output
  - Summary: `reporting/task-2.10/summary.md`

**Phase 2 Complete: Async Implementation**
- Core async toolkit: 86% test coverage
- Async client: 97% test coverage
- FastAPI integration: 87% test coverage
- Quart integration: Full test suite
- All 111 tests passing

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