# Task 1.1: Create pyproject.toml with hatchling backend

**Status:** ✓ Complete
**Date:** 2026-05-05

## What was implemented

Migrated from legacy `setup.py` to modern PEP 621 compliant `pyproject.toml` with hatchling build backend.

### Files created

1. **pyproject.toml** - Complete project configuration with:
   - PEP 621 compliant metadata
   - Hatchling build backend with dynamic version extraction
   - Core dependencies (10 packages)
   - Optional dependency groups (dev, run, async)
   - Tool configurations (ruff, mypy, pytest, coverage)

2. **.python-version** - Python 3.11.12 for pyenv/uv compatibility

### Key decisions

1. **Flask packages as core dependencies**: Flask, flask-cors, flask-restful, and pymongo are imported unconditionally at module level, making them hard dependencies (not optional).

2. **Kept setup.py**: Preserved for backward compatibility during transition period.

3. **Version extraction**: Dynamic version from `oatk/__init__.py` using regex pattern.

4. **Optional dependency strategy**:
   - `dev`: Testing and linting tools (pytest, pytest-asyncio, ruff, mypy, coverage)
   - `run`: Production deployment (gunicorn, eventlet)
   - `async`: Future async support (httpx)

## Verification

- ✓ `uv sync` completed successfully (72 packages resolved)
- ✓ Package built and installed correctly
- ✓ `import oatk` works without errors
- ✓ Version correctly extracted: 0.1.5
- ✓ All imports satisfied by dependencies

## Dependencies

### Core (required)

- pyjwt - JWT token handling
- cryptography - Key serialization
- authlib - JWKS handling
- requests - HTTP requests
- fire - CLI interface
- python-dotenv - Environment configuration
- flask - Web framework (unconditional import)
- flask-cors - CORS support (unconditional import)
- flask-restful - REST API (unconditional import)
- pymongo - MongoDB client (unconditional import)

### Optional

- `dev`: pytest, pytest-asyncio, ruff, mypy, coverage
- `run`: gunicorn, eventlet
- `async`: httpx

## Tool configurations

- **ruff**: Line length 88, target py39, rules E/W/F/I/B/C4/UP/ARG/SIM
- **mypy**: Python 3.9, strict mode with third-party library overrides
- **pytest**: Test discovery configured
- **coverage**: Branch coverage for oatk package

## Issues resolved

### Critical: Dependency structure flaw

**Problem:** Flask packages were initially listed as optional dependencies but imported unconditionally at module level, causing `ModuleNotFoundError` on basic install.

**Fix:** Moved flask, flask-cors, flask-restful, and pymongo to core dependencies.

**Files affected:**
- `oatk/__init__.py` (line 15): `from flask import request, Response`
- `oatk/fake/__init__.py` (lines 3-5): Flask imports
- `oatk/fake/db.py` (line 3): `from pymongo import MongoClient`

## Next steps

Task 1.1 is complete. Proceeding to:
- **Task 1.3**: Migrate from pyenv virtualenvs to uv managed environments
- **Task 1.4**: Add test infrastructure
- **Task 1.5**: Configure ruff for linting
- **Task 1.6**: Configure mypy for type checking
- **Task 1.7**: Add type hints to existing code
- **Task 1.8**: Update Makefile for uv workflow
- **Task 1.9**: Create CHANGELOG.md

**Note:** Tasks 1.2 (Configure optional dependency groups) and 1.10 (Remove .pypi-template dependency) were superseded by Task 1.1.

## Lessons learned

1. **Import analysis critical for dependency classification**: Module-level imports must be core dependencies, not optional.
2. **Verify with actual import**: Running `import oatk` catches dependency issues early.
3. **Check requirements.txt alignment**: Existing requirements.txt provides validation for pyproject.toml dependencies.