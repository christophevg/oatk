# Functional Review: Task 1.1 - Create pyproject.toml with hatchling backend

**Review Date:** 2026-05-05
**Reviewer:** Functional Analyst
**Task:** Create pyproject.toml with PEP 621 compliant metadata and hatchling backend

---

## Executive Summary

**Status: ✗ FAIL**

The implementation has a **critical dependency structure issue** that will prevent the package from being imported correctly. While most requirements are met, the core dependencies are incorrectly classified, which breaks the basic functionality of the package.

---

## Requirements Verification

### Requirement 1: Create `pyproject.toml` with PEP 621 compliant metadata

**Status: ✓ PASS**

The `pyproject.toml` file exists and uses PEP 621 compliant format:
- `[project]` section with all required fields
- `[build-system]` properly configured
- `[project.urls]` for project links
- `[project.scripts]` for CLI entry point

### Requirement 2: Configure hatchling as build backend

**Status: ✓ PASS**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Correctly configured with hatchling as the build backend.

### Requirement 3: Set version as dynamic (extracted from `oatk/__init__.py`)

**Status: ✓ PASS**

```toml
[project]
dynamic = ["version"]

[tool.hatch.version]
path = "oatk/__init__.py"
pattern = "__version__ = ['\"](?P<version>[^'\"]+)['\"]"
```

Version extraction correctly configured. The pattern matches `__version__ = "0.1.5"` in `oatk/__init__.py`.

### Requirement 4: Migrate author, description, classifiers from setup.py

**Status: ✓ PASS (with notes)**

All metadata correctly migrated:

| Field | setup.py | pyproject.toml | Status |
|-------|----------|----------------|--------|
| Author | Christophe VG | ✓ Correct | ✓ |
| Email | contact@christophe.vg | ✓ Correct | ✓ |
| Description | A collection of useful functions for dealing with OAuth | ✓ Correct | ✓ |
| License | MIT | ✓ Correct | ✓ |
| Keywords | oauth human | ✓ Correct | ✓ |

**Classifiers comparison:**

| Classifier | setup.py | pyproject.toml | Notes |
|------------|----------|----------------|-------|
| Topic :: Security :: Cryptography | ✓ | ✓ | ✓ |
| Programming Language :: Python :: 3 | ✓ | ✓ | ✓ |
| Programming Language :: Python :: 3.8 | ✓ | ✗ | Removed (EOL) |
| Programming Language :: Python :: 3.9 | ✗ | ✓ | Added |
| Programming Language :: Python :: 3.10 | ✗ | ✓ | Added |
| Programming Language :: Python :: 3.11 | ✗ | ✓ | Added |
| Programming Language :: Python :: 3.12 | ✗ | ✓ | Added |
| Programming Language :: Python :: 3.13 | ✗ | ✓ | Added |
| Development Status :: 4 - Beta | ✓ | ✓ | ✓ |

**Note:** Python 3.8 was removed and versions 3.9-3.13 were added. This is actually an improvement since Python 3.8 reached EOL on 2024-10-07. The `requires-python = ">=3.9"` correctly reflects this change.

### Requirement 5: Define core dependencies in `[project.dependencies]`

**Status: ✗ FAIL - Critical Issue**

**Core dependencies in pyproject.toml:**
```toml
dependencies = [
  "pyjwt",
  "cryptography",
  "authlib",
  "requests",
  "fire",
  "python-dotenv",
]
```

**Core dependencies in setup.py (INSTALL_REQUIRES):**
```python
INSTALL_REQUIRES = [
  "pyjwt",
  "cryptography",
  "python-dotenv",
  "fire",
  "authlib",
  "flask",          # ✗ MISSING in pyproject.toml core dependencies
  "flask_cors",     # ✗ MISSING in pyproject.toml core dependencies
  "flask_restful",  # ✗ MISSING in pyproject.toml core dependencies
  "pymongo",        # ✗ MISSING in pyproject.toml core dependencies
  "requests",
]
```

**Critical Issue:** Flask, flask-cors, flask-restful, and pymongo are **core dependencies** because they are imported unconditionally at module level:

1. **Flask** - Imported in `oatk/__init__.py` line 15:
   ```python
   from flask import request, Response
   ```

2. **Flask, flask_cors, flask_restful** - Imported in `oatk/fake/__init__.py`:
   ```python
   from flask import Flask
   from flask_cors import CORS
   import flask_restful
   ```

3. **pymongo** - Imported in `oatk/fake/db.py` line 3:
   ```python
   from pymongo import MongoClient
   ```

4. **fake module** - Imported in `oatk/__init__.py` line 19:
   ```python
   from oatk import fake
   ```

**Impact:** A user installing `oatk` with `pip install oatk` will NOT get Flask and related packages installed. When they try to `import oatk`, they will get an immediate `ImportError: No module named 'flask'`.

**Evidence from code inspection:**

The `oatk/__init__.py` imports Flask at the module level:
```python
from flask import request, Response
from oatk import fake
```

And the `OAuthToolkit` class uses Flask's `request` and `Response` objects in the `execute_authenticated` method (lines 182-213).

### Requirement 6: Define optional dependencies in `[project.optional-dependencies]`

**Status: ✗ FAIL - Incorrect grouping**

The optional dependencies are defined, but Flask and related packages should be in core dependencies, not optional:

```toml
[project.optional-dependencies]
flask = [
  "flask",
  "flask-cors",
  "flask-restful",
]
fake-server = [
  "pymongo",
  "flask",
]
```

**Correct structure should be:**

Core dependencies should include:
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

Optional dependency groups should be:
- **dev**: pytest, pytest-asyncio, ruff, mypy, coverage
- **run**: gunicorn, eventlet
- **async**: httpx

### Requirement 7: Keep setup.py temporarily for backward compatibility

**Status: ✓ PASS**

The `setup.py` file still exists and remains unchanged, providing backward compatibility during the transition period.

---

## Additional Verification Checks

### Check 1: Can dependencies be synced with `uv sync`?

**Status: ✗ FAIL**

Running `uv sync` would create an incorrect environment because Flask and related packages are not in core dependencies. The package would fail to import after sync.

### Check 2: Can the package be built?

**Status: ✗ FAIL**

The package can technically be built, but it will produce a broken distribution because:
1. Core dependencies are missing from `project.dependencies`
2. Users installing the package won't get Flask installed
3. Import will fail immediately

### Check 3: Is the version correctly extracted from `oatk/__init__.py`?

**Status: ✓ PASS**

The pattern `__version__ = ['\"](?P<version>[^'\"]+)['\"]` correctly matches:
```python
__version__ = "0.1.5"
```

### Check 4: Are all metadata fields correctly migrated?

**Status: ✓ PASS**

All required PEP 621 metadata fields are present:
- name ✓
- dynamic version ✓
- description ✓
- readme ✓
- license ✓
- authors ✓
- keywords ✓
- classifiers ✓
- requires-python ✓
- dependencies ✓ (content incorrect, but structure correct)
- optional-dependencies ✓ (grouping incorrect, but structure correct)
- urls ✓
- scripts ✓

### Check 5: Are optional dependency groups correctly defined?

**Status: ✗ FAIL**

The groups are defined but incorrectly:
- `flask` and `fake-server` groups should not exist as optional - these should be core dependencies
- `dev`, `run`, and `async` groups are correctly placed as optional

### Check 6: Is the package importable after install?

**Status: ✗ FAIL**

After `pip install oatk`, the import will fail because Flask is not installed:
```python
>>> import oatk
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File ".../oatk/__init__.py", line 15, in <module>
    from flask import request, Response
ModuleNotFoundError: No module named 'flask'
```

---

## Summary of Issues

### Critical Issues (Must Fix)

1. **Flask dependencies incorrectly classified as optional**
   - Flask, flask-cors, flask-restful, and pymongo are imported unconditionally at module level
   - They MUST be in `project.dependencies`, not `project.optional-dependencies`
   - **Impact:** Package cannot be imported after basic installation

### Minor Issues (Should Address)

2. **Python version classifiers changed**
   - Python 3.8 was removed from classifiers
   - Python 3.9-3.13 were added
   - **Note:** This is actually correct (3.8 is EOL), but should be documented as a deliberate change

---

## Recommended Fixes

### Fix 1: Move Flask dependencies to core

Update `pyproject.toml`:

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

### Alternative: Make Flask imports lazy

If Flask dependencies should remain optional (to keep core package lightweight), the code must be refactored to use lazy imports:

1. Remove Flask imports from `oatk/__init__.py` module level
2. Move Flask imports inside the methods that use them
3. Add try/except to provide helpful error messages
4. Update documentation to indicate Flask is optional

**However, this requires significant code changes and is not recommended for this task.**

---

## Acceptance Criteria Status

| Criterion | Status | Notes |
|-----------|--------|-------|
| PEP 621 compliant | ✓ | Correct structure |
| Hatchling backend | ✓ | Correctly configured |
| Dynamic version | ✓ | Pattern matches |
| Migrate metadata | ✓ | All fields migrated |
| Core dependencies | ✗ | Flask missing from core |
| Optional dependencies | ✗ | Incorrect grouping |
| Backward compatibility | ✓ | setup.py preserved |
| Package importable | ✗ | Import fails without Flask |

**Overall Status: ✗ FAIL**

---

## Conclusion

The implementation demonstrates good technical understanding of PEP 621 and hatchling configuration, but has a **critical flaw in dependency classification** that breaks the package's basic functionality. The developer correctly identified that Flask is used for optional features, but failed to recognize that the imports are unconditional at module level, making Flask a hard dependency.

**Recommendation:** Fix the critical dependency issue before proceeding to the next task. This can be done quickly by moving Flask and related packages to the core dependencies section.

---

**Reviewer Signature:** Functional Analyst
**Date:** 2026-05-05