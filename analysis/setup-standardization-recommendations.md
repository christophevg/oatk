# Setup Standardization Recommendations

**Generated**: 2026-05-06
**Research**: [research/2026-05-06-project-setup-standardization/](../research/2026-05-06-project-setup-standardization/)
**Comparison**: [analysis/project-setup-comparison.md](./project-setup-comparison.md)

---

## Executive Summary

This document presents specific, actionable recommendations for standardizing project setup across repositories. All recommendations are based on the comparative analysis of oatk, yoker, and the C3 harness. **No changes will be implemented without user approval.**

---

## Best Practices Identified

### 1. Build System & Dependency Management

**Best Practice**: Use uv with src/ layout

**Rationale**:
- uv is 10-100x faster than pip
- src/ layout prevents import issues during development
- Lock files ensure reproducible builds
- Explicit Python version files help pyenv users

**Standard Configuration**:
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build]
sources = ["src"]

[tool.hatch.build.targets.wheel]
packages = ["src/{package_name}"]
```

**Migration Path** (if currently using flat layout):
1. Move `{package}/` to `src/{package}/`
2. Update build configuration in pyproject.toml
3. Update all imports and test references
4. Update coverage configuration
5. Update Makefile paths

**Estimated Effort**: 2-4 hours for migration

---

### 2. Makefile Organization

**Best Practice**: Well-organized Makefile with help target and convenience features

**Rationale**:
- Self-documenting Makefile improves discoverability
- Convenience targets (test-file, test-one) improve DX
- Section headers make navigation easier
- Standard targets ensure consistency across projects

**Standard Structure**:
```makefile
-include ~/.claude/Makefile

.PHONY: install sync test test-all test-file test-one \
        typecheck lint format check build publish \
        clean clean-all help docs docs-view

## Setup

install: ## Install package in development mode with all extras
  uv sync --all-extras

sync: ## Sync dependencies from lock file
  uv sync --frozen --all-extras

## Testing

test: ## Run all tests with coverage
  uv run pytest

test-file: ## Run specific test file (usage: make test-file FILE=tests/test_x.py)
  uv run pytest $(FILE)

test-one: ## Run specific test (usage: make test-one TEST=tests/test_x.py::test_func)
  uv run pytest $(TEST)

test-all: ## Run tests against all supported Python versions
  uv run tox

## Code Quality

typecheck: ## Run mypy type checking
  uv run mypy --strict src

lint: ## Run ruff linting
  uv run ruff check src tests

format: ## Format code with ruff
  uv run ruff format src tests

check: typecheck lint ## Run all checks

## Build & Publish

build: ## Build package distributions
  uv build

publish: build ## Build and publish to PyPI
  uv publish

## Documentation

docs: ## Build HTML documentation
  cd docs; uv run sphinx-build -M html . _build

docs-view: docs ## Build and open documentation in browser
  @if command -v open >/dev/null; then open docs/_build/html/index.html; fi

## Cleanup

clean: ## Remove build artifacts
  rm -rf build/ dist/ *.egg-info
  find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

clean-all: clean ## Remove virtual environment and lock file
  rm -rf .venv uv.lock

## Help

help: ## Show this help message
  @echo "Usage: make [target]"
  @echo ""
  @grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | \
  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
```

**Key Features**:
- Section headers with ## comments
- Self-documenting targets with ## descriptions
- help target that auto-generates documentation
- Convenience targets for specific test execution
- Standard check target combining typecheck + lint

**Estimated Effort**: 1-2 hours to implement

---

### 3. GitHub Actions CI/CD

**Best Practice**: Comprehensive CI/CD with matrix testing

**Rationale**:
- Automated testing on every push/PR
- Multi-OS testing catches platform-specific issues
- Multi-Python testing ensures compatibility
- Separate jobs for lint, typecheck, and test
- Coverage reporting for visibility

**Standard Configuration** (`.github/workflows/test.yaml`):
```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: ["ubuntu-latest", "macos-latest", "windows-latest"]
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v5

      - name: Install uv
        uses: astral-sh/setup-uv@v6
        with:
          version: "latest"

      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync --frozen --all-extras

      - name: Run tests
        run: uv run pytest -v --cov=src --cov-report=xml

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: astral-sh/setup-uv@v6
      - run: uv sync --frozen --all-extras
      - run: uv run ruff check src tests
      - run: uv run ruff format --check src tests

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: astral-sh/setup-uv@v6
      - run: uv sync --frozen --all-extras
      - run: uv run mypy src
```

**Key Features**:
- Matrix strategy for OS and Python versions
- Uses setup-uv action (official, maintained)
- Frozen sync for reproducibility
- Separate lint and typecheck jobs
- Coverage reporting with XML format

**Estimated Effort**: 1-2 hours to implement

---

### 4. Project Documentation

**Best Practice**: Comprehensive CLAUDE.md/AGENTS.md file

**Rationale**:
- Provides context for AI assistants
- Documents project conventions and patterns
- Reduces onboarding time for new contributors
- Serves as quick reference during development

**Standard Structure** (CLAUDE.md or AGENTS.md):
```markdown
# {Project Name}

This file provides guidance for AI assistants and contributors working with this repository.

## Project Overview

[2-3 sentence description of what the project does]

## Current State

[Description of current implementation status]

## Architecture

[High-level architecture description]

### Package Structure

[Directory structure with purpose]

## Development Setup

[Setup instructions using uv]

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make install` | Install dependencies |
| `make test` | Run tests with coverage |
| `make check` | Run all checks |
| ... | ... |

## Pre-Commit Requirements

Before any commit, verify:
1. All tests pass: `make test`
2. Type checking passes: `make typecheck`
3. Linting passes: `make lint`

## Code Style

- Two-space indentation
- [Line length] character max
- Full type hints required (mypy strict mode)
- [Other conventions]

## Testing

- Test coverage target: [X%]
- Tests located in tests/
- [Testing conventions]

## Dependencies

**Core:**
- [List of core dependencies with versions]

**Dev:**
- [List of dev dependencies]

## Documentation

- `README.md` - Project overview
- `docs/` - [Documentation system]
- [Other documentation locations]

## Related Projects

- [Links to related projects]

## Research

- [Links to research documents]
```

**Estimated Effort**: 2-3 hours to create comprehensive guide

---

### 5. .gitignore Configuration

**Best Practice**: Comprehensive .gitignore covering all common patterns

**Standard Configuration**:
```gitignore
# Build artifacts
build/
dist/
*.egg-info/
*.egg

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/
coverage.xml

# Type checking
.mypy_cache/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store

# Documentation
docs/_build/

# Project specific
# [Add project-specific patterns]

# Local configuration
*.local
.env.local
[project].toml

# Generated files
# [Add patterns for generated files]

# Environment files with secrets
.env
.env.local
```

**Estimated Effort**: 15 minutes to implement

---

### 6. README Badges

**Best Practice**: Informative badges for project visibility

**Standard Badges**:
```markdown
[![PyPI version](https://img.shields.io/pypi/v/{package}.svg)](https://pypi.org/project/{package}/)
[![PyPI downloads](https://img.shields.io/pypi/dm/{package}.svg)](https://pypistats.org/packages/{package})
[![Python versions](https://img.shields.io/pypi/pyversions/{package}.svg)](https://pypi.org/project/{package}/)
[![License](https://img.shields.io/github/license/{user}/{repo})](https://github.com/{user}/{repo}/blob/master/LICENSE)
[![Documentation Status](https://readthedocs.org/projects/{project}/badge/?version=latest)](https://{project}.readthedocs.io/)
[![Tests](https://github.com/{user}/{repo}/actions/workflows/test.yml/badge.svg)](https://github.com/{user}/{repo}/actions/workflows/test.yml)
[![Coverage Status](https://img.shields.io/coveralls/github/{user}/{repo}.svg)](https://coveralls.io/github/{user}/{repo})
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-7c85a3.svg)](https://docs.astral.sh/ruff/)
```

**Estimated Effort**: 15 minutes to add

---

### 7. Python Version File

**Best Practice**: Explicit .python-version file

**Rationale**: Allows pyenv users to automatically select the correct Python version

**Standard Configuration** (.python-version):
```
3.12
```

**Estimated Effort**: 1 minute to create

---

### 8. Ruff Configuration

**Best Practice**: Comprehensive ruff setup with sensible defaults

**Standard Configuration**:
```toml
[tool.ruff]
line-length = 88  # or 100, be consistent
target-version = "py310"
indent-width = 2

[tool.ruff.lint]
select = [
  "E",   # pycodestyle errors
  "W",   # pycodestyle warnings
  "F",   # pyflakes
  "I",   # isort
  "B",   # flake8-bugbear
  "C4",  # flake8-comprehensions
  "UP",  # pyupgrade
  "ARG", # flake8-unused-arguments
  "SIM", # flake8-simplify
]
ignore = [
  "E501",  # line too long (handled by formatter)
]

[tool.ruff.lint.isort]
known-first-party = ["{package_name}"]
```

**Note**: Both 88 and 100 character line lengths are acceptable. Choose one and be consistent across projects.

**Estimated Effort**: 5 minutes to configure

---

### 9. Mypy Configuration

**Best Practice**: Strict type checking with sensible output

**Standard Configuration**:
```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
strict_equality = true
show_error_context = true
show_column_numbers = true

[[tool.mypy.overrides]]
module = [
  "third_party_lib.*",
]
ignore_missing_imports = true
```

**Estimated Effort**: 10 minutes to configure

---

### 10. Test Configuration

**Best Practice**: Comprehensive test setup with coverage

**Standard Configuration**:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = "-v --cov={package_name} --cov-report=term-missing"

[tool.coverage.run]
source = ["src"]  # or ["{package_name}"] for flat layout
branch = true
omit = [
  "*/tests/*",
  "*/__main__.py",
]

[tool.coverage.report]
exclude_lines = [
  "pragma: no cover",
  "def __repr__",
  "raise AssertionError",
  "raise NotImplementedError",
  "if __name__ == .__main__.:",
  "if TYPE_CHECKING:",
]
```

**Critical**: Ensure coverage source matches your package name, not copy-pasted from another project!

**Estimated Effort**: 10 minutes to configure

---

## Proposed Changes for oatk

### High Priority (Implement Now)

#### 1. Add GitHub Actions CI/CD

**Files to Create**:
- `.github/workflows/test.yaml` (45 lines)

**Impact**:
- Automated testing on every push/PR
- Multi-OS, multi-Python compatibility verification
- Visibility into test status via badges

**Estimated Effort**: 1-2 hours

**Risks**: None (additive change)

---

#### 2. Add CLAUDE.md or AGENTS.md

**Files to Create**:
- `CLAUDE.md` (~300 lines) or `AGENTS.md` (~150 lines)

**Content**:
- Project overview and current state
- Architecture description
- Development setup instructions
- Makefile target reference
- Pre-commit requirements
- Code style conventions
- Testing conventions
- Dependency information

**Impact**:
- Better AI assistant integration
- Faster contributor onboarding
- Centralized project reference

**Estimated Effort**: 2-3 hours

**Risks**: None (additive change)

---

#### 3. Fix pytest and tox Configuration

**Files to Modify**:
- `pyproject.toml`

**Changes**:
```toml
# Line 172: Change
addopts = "-v --cov=yoker --cov-report=term-missing"
# To
addopts = "-v --cov=oatk --cov-report=term-missing"

# Line 202: Change
["pytest", "tests", "-v", "--cov=yoker", "--cov-report=term-missing"],
# To
["pytest", "tests", "-v", "--cov=oatk", "--cov-report=term-missing"],
```

**Impact**: Correct coverage reporting

**Estimated Effort**: 5 minutes

**Risks**: None (bug fix)

---

#### 4. Add .python-version File

**Files to Create**:
- `.python-version` (1 line)

**Content**:
```
3.12
```

**Impact**: Better pyenv integration

**Estimated Effort**: 1 minute

**Risks**: None (additive change)

---

#### 5. Improve Makefile

**Files to Modify**:
- `Makefile`

**Changes**:
1. Add `.PHONY` declaration at top
2. Organize into sections with headers
3. Add `help` target
4. Add convenience targets: `test-file`, `test-one`, `test-3.10`, `test-3.11`, `test-3.12`
5. Add `check` target
6. Add `clean-all` target

**Impact**: Better developer experience, self-documenting Makefile

**Estimated Effort**: 1 hour

**Risks**: Low (only adding targets, not changing existing behavior)

---

#### 6. Enhance .gitignore

**Files to Modify**:
- `.gitignore`

**Changes**:
Add comprehensive patterns:
```gitignore
# Testing
.pytest_cache/
htmlcov/
.nox/

# Type checking
.mypy_cache/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store

# Generated files
*.jsonl
```

**Impact**: Better coverage of common patterns

**Estimated Effort**: 15 minutes

**Risks**: None (additive change)

---

### Medium Priority (Consider Implementing)

#### 7. Migrate to src/ Layout

**Files to Modify**:
- Move `oatk/` to `src/oatk/`
- `pyproject.toml`
- `Makefile`
- All test files
- Coverage configuration

**Impact**:
- Follows modern packaging best practice
- Prevents import issues during development
- Better alignment with yoker pattern

**Estimated Effort**: 2-4 hours

**Risks**: Medium
- Changes import paths throughout project
- May affect users importing from oatk
- Requires careful testing

---

#### 8. Add More Badges

**Files to Modify**:
- `README.md`

**Changes**:
Add badges after creating GitHub Actions workflow:
```markdown
[![PyPI downloads](https://img.shields.io/pypi/dm/oatk.svg)](https://pypistats.org/packages/oatk)
[![Tests](https://github.com/christophevg/oatk/actions/workflows/test.yml/badge.svg)](https://github.com/christophevg/oatk/actions/workflows/test.yml)
[![Coverage Status](https://img.shields.io/coveralls/github/christophevg/oatk.svg)](https://coveralls.io/github/christophevg/oatk)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-7c85a3.svg)](https://docs.astral.sh/ruff/)
```

**Impact**: Better project visibility

**Estimated Effort**: 15 minutes

**Risks**: None (additive change)

---

#### 9. Add examples Directory

**Files to Create**:
- `examples/` directory
- Example scripts for common use cases

**Impact**: Easier for users to understand usage patterns

**Estimated Effort**: 2-3 hours

**Risks**: None (additive change)

---

### Low Priority (Optional)

#### 10. Consider MyST Parser for Docs

**Files to Modify**:
- `docs/` - Convert RST to MyST (Markdown)
- `pyproject.toml` - Add myst-parser dependency

**Impact**: More accessible documentation format

**Estimated Effort**: 4-8 hours

**Risks**: Medium
- Migration effort
- May lose some RST-specific features
- Need to update all existing docs

---

#### 11. Add analysis Directory

**Files to Create**:
- `analysis/` directory
- Architecture documentation
- Design decision records

**Impact**: Better project documentation

**Estimated Effort**: 4-6 hours

**Risks**: None (additive change)

---

## Proposed Additions to C3 Harness

### Create python-project Skill

**Location**: `c3/skills/python-project/`

**Files to Create**:
- `SKILL.md` - Skill definition and workflow
- `README.md` - Overview
- `templates/Makefile` - Standard Makefile template
- `templates/pyproject.toml` - Standard pyproject.toml template
- `templates/.gitignore` - Standard .gitignore template
- `templates/.python-version` - Python version file
- `templates/CLAUDE.md` - Project guide template
- `templates/.github/workflows/test.yaml` - CI/CD template

**Content**: Document all best practices identified in this research

**Estimated Effort**: 3-4 hours

---

### Update start-baseweb-project Skill

**Changes**:
1. Replace pyenv with uv for dependency management
2. Add GitHub Actions setup step
3. Add CLAUDE.md creation step
4. Update Makefile template with modern targets
5. Add .python-version file creation
6. Enhance .gitignore template

**Estimated Effort**: 2-3 hours

---

### Create Project Setup Checklist

**Content**: Standard checklist for new projects including:
- [ ] GitHub Actions workflow
- [ ] CLAUDE.md or AGENTS.md
- [ ] src/ layout
- [ ] Comprehensive Makefile with help target
- [ ] .python-version file
- [ ] Comprehensive .gitignore
- [ ] README badges
- [ ] Standard tool configurations (ruff, mypy, pytest, coverage, tox)

**Estimated Effort**: 1 hour

---

## Implementation Priority

### Phase 1: Quick Wins (1 day)

1. Fix pytest/tox configuration (5 min)
2. Add .python-version file (1 min)
3. Enhance .gitignore (15 min)
4. Add more README badges (15 min)
5. Improve Makefile (1 hour)

**Total**: ~2 hours

---

### Phase 2: High Value (1-2 days)

6. Add GitHub Actions CI/CD (1-2 hours)
7. Add CLAUDE.md or AGENTS.md (2-3 hours)

**Total**: ~4 hours

---

### Phase 3: Structural Changes (1-2 days)

8. Migrate to src/ layout (2-4 hours)
9. Add examples directory (2-3 hours)

**Total**: ~6 hours

---

### Phase 4: Documentation Enhancement (2-3 days)

10. Consider MyST parser for docs (4-8 hours)
11. Add analysis directory (4-6 hours)

**Total**: ~12 hours

---

### Phase 5: C3 Harness Updates (2-3 days)

12. Create python-project skill (3-4 hours)
13. Update start-baseweb-project skill (2-3 hours)
14. Create project setup checklist (1 hour)

**Total**: ~7 hours

---

## Approval Required

**All changes require user approval before implementation.**

Please review:
1. Which priority level changes to implement
2. Which specific changes to implement
3. Timeline for implementation
4. Any concerns or constraints

---

## Success Metrics

After implementation, measure:
1. **CI/CD**: All PRs automatically tested
2. **Documentation**: CLAUDE.md/AGENTS.md exists and is comprehensive
3. **DX**: Makefile has help target and convenience features
4. **Consistency**: Project follows documented best practices
5. **Visibility**: README has informative badges
6. **Maintainability**: Project structure is clear and documented

---

## Sources

See [research/2026-05-06-project-setup-standardization/SOURCES.md](../research/2026-05-06-project-setup-standardization/SOURCES.md) for complete source listing.