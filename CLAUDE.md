# OATK - OAuth Toolkit

This file provides guidance for AI assistants and contributors working with this repository.

## Project Overview

OATK is a clean, simple Python OAuth toolkit designed for quick prototypes and learning. It provides both synchronous and asynchronous implementations with framework integrations for Flask, Quart, and FastAPI.

The toolkit handles:
- Token creation with RSA private keys
- Token validation with RSA public keys
- JWKS import/export for key distribution
- Provider-based configuration (OpenID Connect)
- Framework-specific decorators and dependency injection

## Current State

The project is in beta (v0.1.5) with full sync and async implementations. Core functionality is stable and tested. Framework integrations (Flask, Quart, FastAPI) are working.

## Architecture

### Package Structure

```
oatk/
  __init__.py          # OAuthToolkit (sync) + exports
  __main__.py          # CLI entry point
  async_toolkit.py     # AsyncOAuthToolkit
  async_client.py      # Async HTTP client wrapper
  fastapi.py           # FastAPI dependency injection
  types.py             # Type definitions
  fake/                # Test server and utilities
    __init__.py
    db.py              # In-memory user database
    routes.py          # Test OAuth server routes
    static/
    templates/
  js/                  # JavaScript utilities
```

### Key Classes

- `OAuthToolkit` - Synchronous toolkit (main class in `__init__.py`)
- `AsyncOAuthToolkit` - Async version (in `async_toolkit.py`)
- `OAuthToolkitDependency` - FastAPI helper (in `fastapi.py`)

### Dependencies

**Core:**
- pyjwt - JWT encoding/decoding
- cryptography - RSA key handling
- authlib - JWKS support
- requests - HTTP client (sync)
- httpx - HTTP client (async)
- fire - CLI framework
- python-dotenv - Environment configuration

**Framework Integrations:**
- flask, flask-cors, flask-restful - Flask support
- quart - Async Flask support
- fastapi - FastAPI support
- pymongo - Database support

## Development Setup

```bash
# Install with all extras
make install

# Or using pip directly
pip install -e .[all]
```

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make install` | Install dependencies with all extras |
| `make sync` | Sync dependencies from lock file |
| `make test` | Run all tests with coverage and checks |
| `make test-all` | Run tests against all Python versions (3.10-3.12) |
| `make test-file FILE=...` | Run specific test file |
| `make test-one TEST=...` | Run specific test |
| `make pytest` | Run pytest without additional checks |
| `make coverage` | Run tests with coverage reporting |
| `make typecheck` | Run mypy type checking |
| `make lint` | Run ruff linting |
| `make format` | Format code with ruff |
| `make format-check` | Check formatting without changes |
| `make check` | Run all checks (typecheck, lint, format-check) |
| `make build` | Build package distributions |
| `make publish` | Build and publish to PyPI |
| `make publish-test` | Build and publish to TestPyPI |
| `make clean` | Remove build artifacts |
| `make clean-all` | Deep clean (removes venv, build artifacts) |
| `make help` | Show all available targets |

## Pre-Commit Requirements

Before any commit, verify:
1. All tests pass: `make test`
2. Type checking passes: `make typecheck`
3. Linting passes: `make lint`
4. Formatting is correct: `make format-check`

Or simply run: `make check`

## Code Style

- Two-space indentation (enforced by ruff)
- 88 character max line length
- Double quotes for strings
- Full type hints required (mypy strict mode)
- Docstrings for public APIs

## Testing

- Test coverage target: >80%
- Tests located in `tests/`
- Framework: pytest with pytest-asyncio
- Coverage: pytest-cov with branch coverage
- Run with: `make test` or `make coverage`

### Test Organization

```
tests/
  conftest.py              # Shared fixtures
  test_oauth_toolkit.py    # Core sync tests
  test_async_toolkit.py    # Core async tests
  test_decorators.py       # Flask decorator tests
  test_async_decorators.py # Async decorator tests
  test_async_client.py     # Async HTTP client tests
  test_fastapi.py          # FastAPI integration tests
  test_quart.py            # Quart integration tests
  test_fake_server.py      # Test server tests
```

## Dependencies

**Core (always installed):**
- pyjwt
- cryptography
- authlib
- requests
- fire
- python-dotenv
- flask
- flask-cors
- flask-restful
- pymongo

**Optional extras:**
- `[dev]` - pytest, ruff, mypy, coverage, tox
- `[async]` - httpx, anyio
- `[quart]` - quart, httpx, anyio
- `[fastapi]` - fastapi, httpx, anyio
- `[docs]` - sphinx, sphinx-rtd-theme, sphinx-autodoc-typehints
- `[all]` - All of the above

## Documentation

- `README.md` - Project overview and quick start
- `docs/` - Sphinx documentation (RST format)
  - `installation.rst` - Installation guide
  - `quickstart.rst` - Quick start tutorial
  - `sync-api.rst` - Synchronous API reference
  - `async-api.rst` - Asynchronous API reference
  - `integrations.rst` - Framework integration guides
  - `api-reference.rst` - Complete API reference

Documentation built with Sphinx and hosted on ReadTheDocs: https://oatk.readthedocs.io

## Framework Integrations

### Flask (Synchronous)

```python
from flask import Flask
from oatk import OAuthToolkit

app = Flask(__name__)
toolkit = OAuthToolkit()
toolkit.with_jwks("certs.json")

@app.route("/protected")
@toolkit.authenticated
def protected():
    return {"message": "authenticated"}
```

### FastAPI (Asynchronous)

```python
from fastapi import FastAPI, Depends
from oatk.async_toolkit import AsyncOAuthToolkit
from oatk.fastapi import OAuthToolkitDependency

app = FastAPI()
toolkit = AsyncOAuthToolkit()
oauth = OAuthToolkitDependency(toolkit)

@app.get("/protected")
async def protected(user = Depends(oauth.get_current_user)):
    return {"user_id": user["sub"]}
```

### Quart (Asynchronous Flask)

```python
from quart import Quart
from oatk.async_toolkit import AsyncOAuthToolkit

app = Quart(__name__)
toolkit = AsyncOAuthToolkit()
await toolkit.with_jwks("certs.json")
```

## Security Considerations

This toolkit is designed primarily for:
- Quick prototypes
- Learning OAuth/JWT concepts
- Development environments

For production systems, consider battle-tested alternatives like Authlib, python-jose, or similar.

## CLI Usage

```bash
# Generate JWKS from public key
oatk with_public public_key.pem jwks

# Create a token
oatk with_private private_key.pem with_jwks certs.json claims '{"user":"alice"}' token

# Validate a token
oatk with_jwks certs.json from_file token.txt validate

# Decode without validation
oatk from_file token.txt decode
```

## Related Projects

- [PyJWT](https://github.com/jpadilla/pyjwt) - JWT library
- [Authlib](https://github.com/lepture/authlib) - OAuth library
- [python-jose](https://github.com/mpdavis/python-jose) - JOSE implementation

## Research

- [Setup Standardization Research](research/2026-05-06-project-setup-standardization/)
- [Project Setup Comparison](analysis/project-setup-comparison.md)
- [Setup Recommendations](analysis/setup-standardization-recommendations.md)