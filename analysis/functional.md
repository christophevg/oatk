# Functional Analysis: OATK (OAuth Toolkit)

**Project:** oatk - OAuth Toolkit
**Version:** 0.1.5
**Analysis Date:** 2026-05-05
**Analyst:** Eira (Functional Analyst Agent)

---

## Executive Summary

The OATK project is a Python library providing OAuth/JWT token handling capabilities, published on PyPI. The project requires modernization from legacy `setup.py` packaging to contemporary `uv`-based tooling, and the addition of async support alongside the existing synchronous implementation while maintaining backward compatibility.

---

## 1. Current Architecture Analysis

### 1.1 Project Structure

```
oatk/
├── oatk/                    # Main package (flat layout, not src/)
│   ├── __init__.py          # OAuthToolkit class (sync implementation)
│   ├── __main__.py          # CLI entry point (Fire-based)
│   ├── fake/                # Fake OAuth server
│   │   ├── __init__.py
│   │   ├── db.py
│   │   ├── routes.py
│   │   ├── templates/
│   │   └── static/
│   └── js/                  # JavaScript client library
│       ├── __init__.py
│       └── oatk.js
├── examples/                # Example applications
│   ├── web.py
│   ├── create-and-validate.py
│   ├── client/
│   └── google/
├── setup.py                 # Legacy packaging
├── requirements.txt         # Runtime dependencies
├── requirements.run.txt     # Additional runtime deps (gunicorn, eventlet)
├── Makefile                 # Build/test automation
└── .pypi-template          # Package metadata template
```

### 1.2 Core Components

#### OAuthToolkit Class (`oatk/__init__.py`)

The main class provides:

| Component | Description | Sync/Async |
|-----------|-------------|------------|
| `with_private(path)` | Load private key from file | Sync only |
| `with_public(path)` | Load public key from file | Sync only |
| `using_provider(url)` | Configure from OpenID provider | Sync only |
| `with_jwks(source)` | Import JWKS for validation | Sync only |
| `from_clipboard()` | Read token from macOS clipboard | Sync only |
| `from_file(path)` | Read token from file | Sync only |
| `claims(dict)` | Set token claims | Sync only |
| `token` (property) | Generate signed JWT | Sync only |
| `validate(token)` | Validate JWT signature | Sync only |
| `decode(token)` | Decode JWT without verification | Sync only |
| `authenticated` (decorator) | Flask route protection | Sync only |
| `authenticated_with_claims` (decorator) | Flask route protection with claims | Sync only |
| `execute_authenticated` | Core decorator implementation | Sync only |
| `jwks` (property) | Generate JWKS from public key | Sync only |
| `with_client_id(id)` | Set client ID for validation | Sync only |
| `init_from_provider()` | Fetch OpenID config and JWKS | Sync only (uses `requests`) |

#### Key Dependencies

| Package | Purpose | Async Alternative |
|---------|---------|-------------------|
| `pyjwt` | JWT encoding/decoding | `pyjwt` (supports async) |
| `cryptography` | RSA key handling | `cryptography` (async-compatible) |
| `requests` | HTTP client for provider config | `aiohttp` or `httpx` |
| `flask` | Web framework (decorators) | `quart` or `fastapi` |
| `flask_restful` | REST API framework | Async-compatible alternatives |
| `flask_cors` | CORS support | Async-compatible alternatives |
| `fire` | CLI interface | No change needed |
| `python-dotenv` | Environment loading | No change needed |
| `authlib` | JWK handling | `authlib` (async-compatible) |
| `pymongo` | MongoDB for fake server | `motor` (async) |

### 1.3 Current Build System

- **Packaging:** Legacy `setup.py` with `setuptools`
- **Dependency Management:** `requirements.txt` files
- **Environment Management:** `pyenv` with multiple virtual envs
- **Testing:** `tox` (configured but no actual tests)
- **Version Management:** Extracted from `oatk/__init__.py`
- **Distribution:** `build` + `twine` for PyPI

### 1.4 Current State Assessment

| Aspect | Status | Issues |
|--------|--------|--------|
| Packaging | Legacy | setup.py deprecated, no pyproject.toml |
| Dependency Management | Manual | No lock files, version pinning inconsistent |
| Source Layout | Flat | Works but not recommended for libraries |
| Test Coverage | None | .pypi-template explicitly skips tests |
| Python Versions | 3.9-3.12 | Inconsistent metadata (setup.py says 3.8) |
| Async Support | None | All operations are synchronous |
| Type Hints | None | No typing annotations |
| Documentation | README only | No API docs, no docstrings |

---

## 2. Modernization Requirements

### 2.1 Packaging Modernization (uv-based)

Following the `/python-project` skill standards:

| Current | Target |
|---------|--------|
| `setup.py` | `pyproject.toml` (PEP 621) |
| `requirements.txt` | `pyproject.toml` [project.dependencies] |
| `requirements.run.txt` | `pyproject.toml` [project.optional-dependencies] |
| `pyenv` virtual envs | `uv` managed environments |
| Manual version extraction | `hatchling` or `setuptools_scm` |
| `.pypi-template` | Native pyproject.toml metadata |

#### Target Structure

```
pyproject.toml
├── [project]
│   ├── name = "oatk"
│   ├── version (dynamic from hatchling)
│   ├── dependencies
│   ├── optional-dependencies
│   │   ├── run = ["gunicorn", "eventlet"]
│   │   └── dev = ["pytest", "ruff", "mypy", ...]
├── [build-system]
│   └── hatchling backend
├── [tool.hatch]
│   └── version, envs, build
├── [tool.ruff]
├── [tool.mypy]
└── [tool.pytest]
```

### 2.2 Async Implementation Strategy

#### Design Principles

1. **Dual API Surface**: Maintain sync API alongside new async API
2. **Naming Convention**: Async methods prefixed with `async_` or use `AsyncOAuthToolkit` class
3. **Framework Agnostic**: Async decorators should work with any ASGI framework
4. **Backward Compatible**: All existing sync code must continue to work unchanged

#### Async Components Required

| Sync Method | Async Alternative | Implementation Notes |
|-------------|-------------------|---------------------|
| `using_provider(url)` | `async_using_provider(url)` | Use `aiohttp`/`httpx` instead of `requests` |
| `init_from_provider()` | `async_init_from_provider()` | Async HTTP calls |
| `from_clipboard()` | N/A | Clipboard access is inherently sync, keep as-is |
| `from_file(path)` | `async_from_file(path)` | Use `aiofiles` for async file I/O |
| `validate(token)` | `async_validate(token)` | JWT validation is CPU-bound, consider `run_in_executor` |
| `execute_authenticated()` | `async_execute_authenticated()` | Framework-agnostic async decorator |

#### Async Decorator Strategy

For async web frameworks, provide:

```python
# Option 1: Separate async class
from oatk import AsyncOAuthToolkit

auth = AsyncOAuthToolkit()
await auth.using_provider("https://provider.example.com/.well-known/openid-configuration")

@auth.authenticated_async
async def protected_route():
    return {"message": "authenticated"}

# Option 2: Hybrid approach
from oatk import OAuthToolkit

auth = OAuthToolkit()
auth.using_provider("...")  # sync initialization

@auth.authenticated_async  # async decorator
async def protected_route():
    return {"message": "authenticated"}
```

#### Framework-Specific Integrations

| Framework | Integration Type | Notes |
|-----------|-----------------|-------|
| Flask | Existing sync decorators | No changes |
| Quart | New async decorators | Drop-in Flask async alternative |
| FastAPI | New dependency injection | Use FastAPI's Depends() pattern |
| Starlette | New middleware | ASGI middleware approach |

---

## 3. Migration Strategy

### Phase 1: Infrastructure Modernization (No Breaking Changes)

**Goal:** Modernize build system without changing functionality

1. Create `pyproject.toml` with hatchling backend
2. Migrate all dependencies to pyproject.toml
3. Configure uv for environment management
4. Add basic test infrastructure (empty tests passing)
5. Configure ruff for linting
6. Configure mypy for type checking
7. Update Makefile for uv-based workflow
8. Add type hints to existing code

**Acceptance Criteria:**
- `uv run pytest` runs (even without tests)
- `uv run ruff check .` passes
- `uv run mypy oatk` passes
- `uv build` produces valid distribution
- Existing functionality unchanged

### Phase 2: Async Implementation

**Goal:** Add async capabilities alongside sync API

1. Add async HTTP client support (`httpx` or `aiohttp`)
2. Implement `AsyncOAuthToolkit` class
3. Add async file operations (`aiofiles` or `anyio`)
4. Create async decorators for ASGI frameworks
5. Add Quart integration (Flask async alternative)
6. Add FastAPI dependency injection helper
7. Write tests for async functionality

**Acceptance Criteria:**
- All sync tests continue to pass
- New async tests pass
- Both sync and async APIs documented
- Performance comparison documented

### Phase 3: Testing & Documentation

**Goal:** Comprehensive test coverage and documentation

1. Unit tests for all sync methods
2. Unit tests for all async methods
3. Integration tests for Flask decorators
4. Integration tests for async decorators
5. Performance benchmarks
6. API documentation with docstrings
7. Migration guide for existing users
8. Examples for async usage

**Acceptance Criteria:**
- 80%+ test coverage
- All public APIs documented
- Working examples for both sync and async

### Phase 4: Release Preparation

**Goal:** Prepare for 0.2.0 release

1. Update version to 0.2.0
2. Update README with async examples
3. Create CHANGELOG.md
4. Set up CI/CD pipeline
5. Publish to TestPyPI first
6. Verify installation from TestPyPI
7. Publish to PyPI

---

## 4. Backward Compatibility Considerations

### Must Maintain

1. **Public API Surface**: All existing methods and properties
2. **Decorator Behavior**: Existing Flask decorators must work identically
3. **CLI Interface**: `oatk` command-line tool unchanged
4. **Import Paths**: `from oatk import OAuthToolkit` must continue to work
5. **Method Signatures**: All existing method signatures preserved
6. **Return Types**: All existing return types unchanged

### Allowed Changes

1. **Internal Implementation**: Refactoring internals
2. **New Dependencies**: Adding optional dependencies
3. **New Classes**: Adding `AsyncOAuthToolkit`
4. **New Methods**: Adding async methods to existing class
5. **Type Hints**: Adding type annotations (non-breaking)
6. **Documentation**: Improving docs

### Breaking Changes (Future Major Version)

For future 1.0.0, consider:
- Removing deprecated methods
- Requiring async for provider initialization
- Changing to src/ layout
- Dropping older Python versions

---

## 5. Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Dependency conflicts with async libraries | High | Medium | Use extras, make async dependencies optional |
| Breaking changes in sync API | High | Low | Comprehensive test suite before changes |
| Performance regression in sync path | Medium | Low | Benchmark before/after |
| Complex migration for users | Medium | Medium | Clear migration guide, gradual rollout |
| CI/CD complexity | Low | Medium | Start simple, iterate |

---

## 6. Dependencies Analysis

### Core Dependencies (Required)

| Package | Version | Async Support | Notes |
|---------|---------|---------------|-------|
| `pyjwt` | >=2.0 | Yes | Core functionality |
| `cryptography` | >=3.0 | Yes | Key handling |
| `authlib` | >=1.0 | Yes | JWK handling |
| `python-dotenv` | >=1.0 | N/A | Config loading |

### HTTP Dependencies (Required for Provider Config)

| Package | Current | Async Alternative |
|---------|---------|-------------------|
| `requests` | Yes | `httpx` (supports both sync/async) |
| | | `aiohttp` (async only) |

### Web Framework Dependencies (Optional)

| Package | Type | Async Version |
|---------|------|---------------|
| `flask` | Sync | `quart` (drop-in replacement) |
| `flask-restful` | Sync | `quart` + custom or `fastapi` |
| `flask-cors` | Sync | `quart-cors` |

### Optional Dependencies

| Package | Purpose | Condition |
|---------|---------|-----------|
| `gunicorn` | WSGI server | Only for deployment |
| `eventlet` | Async workers | Only for Flask async |
| `pymongo` | Fake server DB | Only for testing |
| `fire` | CLI | Core functionality |

---

## 7. Recommended Dependency Strategy

```toml
[project]
dependencies = [
    "pyjwt>=2.0",
    "cryptography>=3.0",
    "authlib>=1.0",
    "python-dotenv>=1.0",
    "fire>=0.5",
]

[project.optional-dependencies]
flask = ["flask>=2.0", "flask-cors>=3.0", "flask-restful>=0.3"]
async = ["httpx>=0.24", "aiofiles>=23.0"]
async-flask = ["oatk[flask,async]", "quart>=0.18"]
fake-server = ["pymongo>=4.0", "flask>=2.0"]
dev = ["pytest>=7.0", "pytest-asyncio>=0.21", "ruff>=0.1", "mypy>=1.0"]
run = ["gunicorn>=21.0", "eventlet>=0.33"]
```

---

## 8. Quality Metrics

### Current State

| Metric | Value | Target |
|--------|-------|--------|
| Test Coverage | 0% | 80%+ |
| Type Hint Coverage | 0% | 90%+ |
| Documentation Coverage | ~10% | 100% public API |
| Linting | Ruff configured | All pass |
| Type Checking | Not configured | All pass (strict) |

### Target Metrics (Post-Migration)

| Metric | Target | Verification |
|--------|--------|--------------|
| Test Coverage | 80% | `pytest --cov` |
| Type Coverage | 90% | `mypy --strict` |
| Lint Score | 10/10 | `ruff check` |
| Security Issues | 0 | `pip-audit` |
| Dependencies Audit | Pass | `pip-audit` |

---

## 9. Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Infrastructure | 2-3 days | None |
| Phase 2: Async Implementation | 5-7 days | Phase 1 |
| Phase 3: Testing & Docs | 3-5 days | Phase 2 |
| Phase 4: Release Prep | 1-2 days | Phase 3 |
| **Total** | **11-17 days** | |

---

## 10. Open Questions

1. **Async HTTP Client Choice**: Prefer `httpx` (unified sync/async) or `aiohttp` (async-only)?
2. **Async Framework Support**: Start with Quart only, or also add FastAPI support?
3. **Source Layout**: Migrate to `src/` layout or keep flat layout?
4. **Python Version Support**: Drop Python 3.9 or keep it?
5. **Fake Server**: Migrate to async or keep sync for simplicity?
6. **JavaScript Client**: Needs updates for async endpoints?

---

## 11. Recommendations Summary

### Immediate Priorities

1. **Create pyproject.toml** - Foundation for all other work
2. **Add test infrastructure** - Safety net for refactoring
3. **Add type hints** - Enable better IDE support and type checking
4. **Implement AsyncOAuthToolkit** - New async capabilities

### Long-term Considerations

1. **Deprecation Policy**: Define timeline for sync-only support
2. **Framework Integrations**: Expand to FastAPI, Starlette, etc.
3. **Security Audits**: Regular dependency security scanning
4. **Performance Monitoring**: Benchmarks for each release

---

## Appendix A: Current API Surface

```python
class OAuthToolkit:
    # Properties
    version: str
    jwks: str
    token: str | None

    # Configuration Methods (returns self for chaining)
    def with_private(self, path: str) -> 'OAuthToolkit'
    def with_public(self, path: str) -> 'OAuthToolkit'
    def using_provider(self, provider_url: str) -> 'OAuthToolkit'
    def with_client_id(self, client_id: str) -> 'OAuthToolkit'
    def with_jwks(self, path_or_string_or_obj) -> 'OAuthToolkit'
    def claims(self, claimsdict=None, **claimset) -> 'OAuthToolkit'

    # Token Input Methods (returns self for chaining)
    def from_clipboard(self) -> 'OAuthToolkit'
    def from_file(self, path: str) -> 'OAuthToolkit'

    # Token Operations
    def header(self, token=None) -> dict
    def validate(self, token=None) -> dict
    def decode(self, token=None) -> dict

    # Internal Methods
    def init_from_provider(self) -> 'OAuthToolkit'

    # Flask Decorators
    def authenticated(self, f) -> Callable
    def authenticated_with_claims(self, **required_claims) -> Callable
    def execute_authenticated(self, f, required_claims=None, *args, **kwargs)

    # Internal Attributes
    _encoded: str | None
    _provider_url: str | None
    _certs: dict
    _private_key: RSAPrivateKey | None
    _public_key: RSAPublicKey | None
    _alg: str
    _kid: str
    _claims: dict
    _client_id: str | None

    # Fake Server
    server: module  # oatk.fake module
```

---

## Appendix B: File Inventory

### Source Files

| File | Lines | Purpose | Async Compatible |
|------|-------|---------|-------------------|
| `oatk/__init__.py` | 228 | Main class | Partial (JWT ops OK) |
| `oatk/__main__.py` | 32 | CLI entry | Yes |
| `oatk/fake/__init__.py` | 44 | Server setup | No (Flask) |
| `oatk/fake/routes.py` | 241 | Server routes | No (Flask) |
| `oatk/fake/db.py` | ? | Database | No (pymongo) |
| `oatk/js/__init__.py` | 9 | JS loader | Yes |

### Configuration Files

| File | Purpose | Migration Needed |
|------|---------|-----------------|
| `setup.py` | Legacy packaging | Yes -> pyproject.toml |
| `requirements.txt` | Dependencies | Yes -> pyproject.toml |
| `requirements.run.txt` | Extra deps | Yes -> pyproject.toml |
| `Makefile` | Build automation | Yes (uv targets) |
| `.pypi-template` | Package metadata | Yes -> pyproject.toml |
| `pyrightconfig.json` | Type checker | No (keep) |

### Documentation Files

| File | Purpose | Status |
|------|---------|--------|
| `.github/README.md` | Main docs | Needs async section |
| `examples/` | Usage examples | Needs async examples |

---

**End of Functional Analysis**