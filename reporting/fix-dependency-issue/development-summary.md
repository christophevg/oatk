# Fix Critical Dependency Issue - Development Summary

## What Was Implemented

Fixed the critical dependency issue where Flask and related packages were incorrectly marked as optional dependencies when they are actually required for the package to function.

### Changes Made to `/Users/xtof/Workspace/agentic/oatk/pyproject.toml`

1. **Moved packages from optional to core dependencies:**
   - flask
   - flask-cors
   - flask-restful
   - pymongo

2. **Removed optional dependency groups:**
   - Removed `[project.optional-dependencies] flask` group
   - Removed `[project.optional-dependencies] fake-server` group

3. **Kept existing optional dependency groups:**
   - `dev`: pytest, pytest-asyncio, ruff, mypy, coverage
   - `run`: gunicorn, eventlet
   - `async`: httpx

## Files Modified

- `/Users/xtof/Workspace/agentic/oatk/pyproject.toml`

## Rationale

The issue was identified in the functional review: Flask and related packages are imported unconditionally in the codebase:

- `oatk/__init__.py` (line 15): `from flask import request, Response`
- `oatk/fake/__init__.py` (line 3): `from flask import Flask`
- `oatk/fake/__init__.py` (line 4): `from flask_cors import CORS`
- `oatk/fake/__init__.py` (line 5): `import flask_restful`
- `oatk/fake/db.py` (line 3): `from pymongo import MongoClient`

These imports happen at package load time, making them hard dependencies rather than optional. The fix aligns `pyproject.toml` with the actual code requirements.

## Verification

### Manual Verification Required

The changes need to be verified by running:

```bash
# Synchronize dependencies
uv sync

# Test that the package imports successfully
uv run python -c "import oatk"
```

### Evidence Supporting the Fix

The `requirements.txt` file already includes these packages as core dependencies:
```
pyjwt
cryptography
python-dotenv
fire
authlib
flask
flask_cors
flask_restful
pymongo
requests
```

This confirms that Flask, Flask-CORS, Flask-RESTful, and PyMongo were always meant to be core dependencies.

## Updated Dependencies Section

```toml
dependencies = [
  "pyjwt",
  "cryptography",
  "authlib",
  "requests",
  "fire",
  "python-dotenv",
  "flask",
  "flask-cors",
  "flask-restful",
  "pymongo",
]

[project.optional-dependencies]
dev = [
  "pytest",
  "pytest-asyncio",
  "ruff",
  "mypy",
  "coverage",
]
run = [
  "gunicorn",
  "eventlet",
]
async = [
  "httpx",
]
```

## Decisions Made

1. **Kept pymongo as core dependency** - Although pymongo is only used in `oatk/fake/db.py`, the fake module is imported in `oatk/__init__.py` (line 19: `from oatk import fake`), making it a hard dependency.

2. **Preserved all optional groups** - The `dev`, `run`, and `async` groups remain unchanged as they are truly optional dependencies for development, production deployment, and async support respectively.

## Tests

- No tests were run (requires manual verification with `uv sync`)
- The fix aligns pyproject.toml with requirements.txt, which already lists these dependencies

## Next Steps

1. Run `uv sync` to verify dependencies install correctly
2. Run `uv run python -c "import oatk"` to verify the package imports without errors
3. Run `make lint` to ensure no linting issues
4. Run `make test` to ensure all tests pass