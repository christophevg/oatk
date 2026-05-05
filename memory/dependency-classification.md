# Dependency Classification Decision

**Date:** 2026-05-05
**Task:** 1.1 - Create pyproject.toml
**Type:** Architecture Decision

## Context

When migrating from `setup.py` to `pyproject.toml`, we needed to classify dependencies as core (required) or optional (extras).

## Decision

Flask and related packages (flask, flask-cors, flask-restful, pymongo) are **core dependencies**, not optional.

## Rationale

These packages are imported **unconditionally at module level**:

- `oatk/__init__.py` (line 15): `from flask import request, Response`
- `oatk/fake/__init__.py` (lines 3-5): Flask imports
- `oatk/fake/db.py` (line 3): `from pymongo import MongoClient`

When Python imports `oatk`, it immediately imports these packages. If they're not installed, the import fails with `ModuleNotFoundError`.

## Impact

- Users running `pip install oatk` will get Flask and dependencies automatically
- Package size increases, but import success is guaranteed
- Optional dependency groups remain for development-only tools

## Alternatives Considered

1. **Lazy imports**: Delay Flask imports until actually needed
   - Rejected: Requires significant refactoring
   - Rejected: Breaks existing API

2. **Import guard**: Use try/except around Flask imports
   - Rejected: Requires error handling throughout codebase
   - Rejected: Confusing for users

## Verification

Verified by running `uv run python -c "import oatk"` after `uv sync`.

## References

- Issue identified in functional review
- Fix applied in second implementation round
- Verified working with all tests passing