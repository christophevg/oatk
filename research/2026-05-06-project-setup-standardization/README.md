# Project Setup Standardization

**Research Date:** 2026-05-06
**Purpose:** Determine best practices from multiple sources and standardize across repositories
**Previous Research:** none

---

## Executive Summary

This research compared project setup patterns across three sources: the current oatk project, the yoker project, and the C3 harness's start-baseweb-project skill. The analysis reveals that **yoker represents the most mature and comprehensive setup**, incorporating industry best practices that oatk lacks. Key findings include: yoker uses GitHub Actions for CI/CD (oatk has none), follows src/ layout convention (oatk uses flat layout), has extensive project documentation in CLAUDE.md (oatk lacks this), and has better-structured documentation directories. Both projects use uv for dependency management and ruff for linting/formatting with similar configurations. The recommendation is to migrate oatk toward yoker's patterns while documenting these standards in the C3 harness.

---

## 1. Project Structure Comparison

### 1.1 Source Layout

**yoker**: Uses `src/` layout (modern best practice)
```
yoker/
├── src/yoker/          # Package source code
│   ├── __init__.py
│   ├── agent.py
│   └── ...
├── tests/              # Tests outside source
├── docs/               # Documentation
├── analysis/           # Architecture docs
└── examples/           # Usage examples
```

**oatk**: Uses flat layout (older pattern)
```
oatk/
├── oatk/              # Package at root level
│   ├── __init__.py
│   └── ...
├── tests/
└── docs/
```

**Best Practice**: The `src/` layout is recommended by setuptools and prevents import issues during testing. yoker follows this pattern.

**Sources:**
- [yoker/pyproject.toml](file:///Users/xtof/Workspace/agentic/yoker/pyproject.toml) - Line 67-71
- [oatk/pyproject.toml](file:///Users/xtof/Workspace/agentic/oatk/pyproject.toml)

---

### 1.2 Project Documentation

**yoker**: Comprehensive documentation
```
├── README.md           # Badges, quick start, features
├── CLAUDE.md           # Agent instructions, conventions
├── docs/               # Sphinx documentation
├── analysis/           # Architecture docs
├── examples/           # Code examples
└── media/              # Screenshots, diagrams
```

**oatk**: Basic documentation
```
├── README.md           # Basic badges, usage
├── docs/               # Sphinx docs (extensive)
└── No CLAUDE.md or AGENTS.md
```

**Key Difference**: yoker has a detailed `CLAUDE.md` file (317 lines) providing:
- Project overview and current state
- Architecture details
- Development setup instructions
- Makefile target reference
- Pre-commit requirements
- Code style guidelines
- Testing conventions
- New feature checklists

**Sources:**
- [yoker/CLAUDE.md](file:///Users/xtof/Workspace/agentic/yoker/CLAUDE.md)
- [oatk directory listing](file:///Users/xtof/Workspace/agentic/oatk)

---

## 2. Build System and Dependency Management

### 2.1 Build Backend

**Both projects**: Use hatchling
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**yoker additional config**:
```toml
[tool.hatch.build]
sources = ["src"]

[tool.hatch.build.targets.wheel]
packages = ["src/yoker"]
```

**oatk uses dynamic version**:
```toml
[tool.hatch.version]
path = "oatk/__init__.py"
pattern = "__version__ = ['\"](?P<version>[^'\"]+)['\"]"
```

**Sources:**
- [yoker/pyproject.toml](file:///Users/xtof/Workspace/agentic/yoker/pyproject.toml) - Lines 1-3, 67-71
- [oatk/pyproject.toml](file:///Users/xtof/Workspace/agentic/oatk/pyproject.toml) - Lines 1-3, 95-97

---

### 2.2 Dependency Groups

**yoker**: Clean separation
```toml
dependencies = [...]           # Core dependencies

[project.optional-dependencies]
dev = [...]                   # Development tools
docs = [...]                   # Documentation only
```

**oatk**: Multiple functional groups
```toml
dependencies = [...]           # Core dependencies

[project.optional-dependencies]
all = [...]                    # Meta-group
dev = [...]                    # Development tools
run = [...]                    # Runtime extras
async = [...]                  # Async support
quart = [...]                  # Quart integration
fastapi = [...]                # FastAPI integration
docs = [...]                   # Documentation
```

**Analysis**: oatk's approach is more modular, allowing users to install only what they need for specific use cases. However, the `all` group duplicates dev dependencies. yoker's approach is simpler but less flexible.

**Sources:**
- [yoker/pyproject.toml](file:///Users/xtof/Workspace/agentic/yoker/pyproject.toml) - Lines 27-56
- [oatk/pyproject.toml](file:///Users/xtof/Workspace/agentic/oatk/pyproject.toml) - Lines 24-86

---

### 2.3 UV Configuration

**Both projects**: Use uv for dependency management

**yoker Makefile**:
```makefile
install: ## Install package in development mode with all extras
  uv sync --all-extras

sync: ## Sync dependencies from lock file
  uv sync --frozen --all-extras
```

**oatk Makefile**:
```makefile
install:
  @uv sync --all-extras

sync: ## Sync dependencies from lock file
  uv sync --frozen --all-extras
```

**Difference**: yoker includes explicit install targets for Python versions:
```makefile
install-pythons: ## Install all supported Python versions for tox
  uv python install 3.10 3.11 3.12
```

**Sources:**
- [yoker/Makefile](file:///Users/xtof/Workspace/agentic/yoker/Makefile) - Lines 7-15
- [oatk/Makefile](file:///Users/xtof/Workspace/agentic/oatk/Makefile) - Lines 14-31

---

## 3. Makefile Comparison

### 3.1 Makefile Structure

**yoker Makefile** (119 lines): Well-organized with sections
```makefile
## Setup
## Testing
## Documentation
## Demo Screenshots
## Code Quality
## Build & Publish
## Cleanup
## Help
```

**oatk Makefile** (89 lines): Basic organization
```makefile
# Installation targets
# functional targets
# packaging targets
# include optional a personal/local touch
```

**Sources:**
- [yoker/Makefile](file:///Users/xtof/Workspace/agentic/yoker/Makefile)
- [oatk/Makefile](file:///Users/xtof/Workspace/agentic/oatk/Makefile)

---

### 3.2 Key Makefile Targets

| Target | yoker | oatk | Notes |
|--------|-------|------|-------|
| **install** | `uv sync --all-extras` | `uv sync --all-extras` | Identical |
| **sync** | `uv sync --frozen --all-extras` | `uv sync --frozen --all-extras` | Identical |
| **test** | `uv run pytest` | `format-check lint typecheck pytest` | oatk runs all checks |
| **test-all** | `uv run tox` | `uv run tox` | Identical (multi-version testing) |
| **test-file** | ✓ | ✗ | yoker has convenience target |
| **test-one** | ✓ | ✗ | yoker has convenience target |
| **test-3.x** | ✓ | ✗ | yoker has version-specific targets |
| **docs** | ✓ (with docs-view) | ✗ | yoker has better doc support |
| **demo/demos** | ✓ | ✗ | yoker has screenshot generation |
| **typecheck** | `uv run mypy --strict src` | `uv run mypy --strict oatk` | Similar |
| **lint** | `uv run ruff check src tests` | `uv run ruff check .` | yoker more specific |
| **format** | `uv run ruff format src tests` | `uv run ruff format oatk tests examples` | oatk includes examples |
| **check** | ✓ (typecheck + lint) | ✗ | yoker has combined target |
| **clean** | ✓ (comprehensive) | ✓ (minimal) | yoker more thorough |
| **clean-all** | ✓ (removes .venv) | ✗ | yoker has deep clean |
| **help** | ✓ (detailed) | ✗ | yoker has auto-generated help |

**Sources:**
- [yoker/Makefile](file:///Users/xtof/Workspace/agentic/yoker/Makefile)
- [oatk/Makefile](file:///Users/xtof/Workspace/agentic/oatk/Makefile)

---

### 3.3 C3 Global Makefile

Both projects include the C3 global Makefile:
```makefile
-include ~/.claude/Makefile
```

This provides common Claude/Ollama integration targets like `claude`, `resume`, `assistant`, `project`, `manage`.

**Sources:**
- [~/.claude/Makefile](file:///Users/xtof/.claude/Makefile)

---

## 4. Code Quality Tools

### 4.1 Ruff Configuration

**Both projects**: Similar ruff setup with minor differences

**yoker**:
```toml
[tool.ruff]
line-length = 100
target-version = "py310"
indent-width = 2

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP"]
ignore = ["E501"]

[tool.ruff.lint.isort]
known-first-party = ["yoker"]
```

**oatk**:
```toml
[tool.ruff]
target-version = "py310"
line-length = 88
indent-width = 2

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
docstring-code-format = true

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM"]
ignore = ["E501", "B008"]

[tool.ruff.lint.isort]
known-first-party = ["oatk"]
```

**Differences**:
- yoker: 100 char line length, oatk: 88 char (black default)
- oatk: Additional lint rules (ARG, SIM) and format options
- oatk: More explicit formatter configuration

**Sources:**
- [yoker/pyproject.toml](file:///Users/xtof/Workspace/agentic/yoker/pyproject.toml) - Lines 92-112
- [oatk/pyproject.toml](file:///Users/xtof/Workspace/agentic/oatk/pyproject.toml) - Lines 99-128

---

### 4.2 Mypy Configuration

**Both projects**: Strict type checking

**yoker**:
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
```

**oatk**:
```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
show_error_context = true
show_column_numbers = true
# Plus module overrides for third-party libs
```

**Differences**:
- yoker: `disallow_untyped_decorators = true`, `warn_no_return = true`, `strict_equality = true`
- oatk: `show_error_context = true`, `show_column_numbers = true`, extensive module overrides

**Sources:**
- [yoker/pyproject.toml](file:///Users/xtof/Workspace/agentic/yoker/pyproject.toml) - Lines 78-91
- [oatk/pyproject.toml](file:///Users/xtof/Workspace/agentic/oatk/pyproject.toml) - Lines 129-161

---

### 4.3 Pytest Configuration

**yoker**:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "-v --cov=yoker --cov-report=term-missing"
```

**oatk**:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=yoker --cov-report=term-missing"
```

**Note**: oatk pytest config incorrectly references `yoker` instead of `oatk` for coverage.

**Sources:**
- [yoker/pyproject.toml](file:///Users/xtof/Workspace/agentic/yoker/pyproject.toml) - Lines 73-76
- [oatk/pyproject.toml](file:///Users/xtof/Workspace/agentic/oatk/pyproject.toml) - Lines 167-172

---

### 4.4 Coverage Configuration

**yoker**:
```toml
[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
exclude_lines = [
  "pragma: no cover",
  "def __repr__",
  "raise NotImplementedError",
  "if TYPE_CHECKING:",
]
```

**oatk**:
```toml
[tool.coverage.run]
source = ["oatk"]
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

**Sources:**
- [yoker/pyproject.toml](file:///Users/xtof/Workspace/agentic/yoker/pyproject.toml) - Lines 114-124
- [oatk/pyproject.toml](file:///Users/xtof/Workspace/agentic/oatk/pyproject.toml) - Lines 174-190

---

## 5. Multi-Version Testing (Tox)

### 5.1 Tox Configuration

**Both projects**: Nearly identical tox setup

**yoker**:
```toml
[tool.tox]
env_list = ["py310", "py311", "py312"]

[tool.tox.env_run_base]
description = "run tests with pytest"
commands_pre = [
  ["uv", "pip", "install", "-e", "."],
  ["uv", "pip", "install", "pytest", "pytest-cov", "pytest-asyncio"],
]
commands = [
  ["pytest", "tests", "-v", "--cov=yoker", "--cov-report=term-missing"],
]
```

**oatk**:
```toml
[tool.tox]
env_list = ["py310", "py311", "py312"]

[tool.tox.env_run_base]
description = "run tests with pytest"
commands_pre = [
  ["uv", "pip", "install", "-e", ".[all]"],
  ["uv", "pip", "install", "pytest", "pytest-cov", "pytest-asyncio", ],
]
commands = [
  ["pytest", "tests", "-v", "--cov=yoker", "--cov-report=term-missing"],
]
```

**Differences**:
- oatk installs `[all]` extras during tox run
- Both incorrectly reference `yoker` for coverage

**Sources:**
- [yoker/pyproject.toml](file:///Users/xtof/Workspace/agentic/yoker/pyproject.toml) - Lines 126-146
- [oatk/pyproject.toml](file:///Users/xtof/Workspace/agentic/oatk/pyproject.toml) - Lines 192-213

---

## 6. CI/CD Configuration

### 6.1 GitHub Actions

**yoker**: Comprehensive CI/CD pipeline (45 lines)
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

**oatk**: No GitHub Actions workflows

**Key Features**:
- Multi-OS testing (Ubuntu, macOS, Windows)
- Multi-Python version testing (3.10, 3.11, 3.12)
- Separate lint, typecheck, and test jobs
- Uses modern `setup-uv` action
- Coverage reporting

**Sources:**
- [yoker/.github/workflows/test.yaml](file:///Users/xtof/Workspace/agentic/yoker/.github/workflows/test.yaml)

---

## 7. Git Configuration

### 7.1 .gitignore Comparison

**yoker** (54 lines): Comprehensive
```gitignore
# Build artifacts
build/
dist/
*.egg-info/

# Python
__pycache__/
*.py[cod]
.venv/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Type checking
.mypy_cache/

# IDE
.idea/
.vscode/

# OS
.DS_Store

# Documentation
docs/_build/

# Project specific
/context/
logs/
*.jsonl

# Local configuration
yoker.toml
.env.local

# Generated files
media/session.jsonl
```

**oatk** (18 lines): Minimal
```gitignore
*.pem
venv
dist
*.egg-info
*.pyc
build
.coverage
.tox
docs/_build
*.backup
local
.DS_Store
certs.json
token.txt
*.local
__pycache__/
```

**Sources:**
- [yoker/.gitignore](file:///Users/xtof/Workspace/agentic/yoker/.gitignore)
- [oatk/.gitignore](file:///Users/xtof/Workspace/agentic/oatk/.gitignore)

---

### 7.2 Python Version File

**yoker**: Has `.python-version` file
```
3.12
```

**oatk**: No `.python-version` file

**Purpose**: Allows pyenv to automatically select the correct Python version.

**Sources:**
- [yoker/.python-version](file:///Users/xtof/Workspace/agentic/yoker/.python-version)

---

## 8. Project Metadata

### 8.1 pyproject.toml Metadata

| Field | yoker | oatk |
|-------|-------|------|
| **name** | yoker | oatk |
| **description** | Detailed | Detailed |
| **license** | `{text = "MIT"}` | `"MIT"` |
| **authors** | ✗ (text format) | ✓ (proper format) |
| **keywords** | ✓ | ✓ |
| **classifiers** | ✓ (more detailed) | ✓ |
| **requires-python** | `>=3.10` | `>=3.10` |
| **project.urls** | Homepage, Docs, Repo, Issues | Homepage, Repo |
| **project.scripts** | ✓ | ✓ |

**Sources:**
- [yoker/pyproject.toml](file:///Users/xtof/Workspace/agentic/yoker/pyproject.toml) - Lines 5-65
- [oatk/pyproject.toml](file:///Users/xtof/Workspace/agentic/oatk/pyproject.toml) - Lines 5-93

---

### 8.2 README Badges

**yoker**: 8 badges
- PyPI version
- PyPI downloads
- Python versions
- License
- Documentation Status
- Tests
- Coverage
- Code style

**oatk**: 3 badges
- Latest Version on PyPI
- Supported Implementations
- License

**Sources:**
- [yoker/README.md](file:///Users/xtof/Workspace/agentic/yoker/README.md) - Lines 1-11
- [oatk/README.md](file:///Users/xtof/Workspace/agentic/oatk/README.md) - Lines 1-6

---

## 9. Documentation Structure

### 9.1 README Structure

**yoker README.md** (209 lines):
- Installation
- Quick Start with example session screenshot
- Why Yoker? (rationale)
- Features (current and planned)
- Configuration
- Architecture
- Documentation links
- Development setup
- Contributing
- Changelog
- License
- Name etymology

**oatk README.md** (212 lines):
- Installation
- Quick Start (sync and async)
- Framework integrations (Flask, FastAPI)
- Features
- CLI usage
- Documentation links
- Use cases
- Security disclaimer
- Requirements
- License
- Links

**Analysis**: Both are comprehensive. yoker's README is more user-focused with rationale and feature lists. oatk's README is more code-focused with examples.

**Sources:**
- [yoker/README.md](file:///Users/xtof/Workspace/agentic/yoker/README.md)
- [oatk/README.md](file:///Users/xtof/Workspace/agentic/oatk/README.md)

---

### 9.2 Documentation Directories

**yoker**:
```
docs/
├── index.md           (MyST parser)
├── installation.md
├── quickstart.md
├── rationale.md
├── architecture.md
└── NAME.md
```

**oatk**:
```
docs/
├── index.rst          (reStructuredText)
├── installation.rst
├── quickstart.rst
├── sync-api.rst
├── async-api.rst
├── integrations.rst
├── security.rst
├── api-reference.rst
├── cli.rst
├── examples.rst
└── requirements.txt
```

**Analysis**: oatk has more extensive documentation (11 RST files vs yoker's 5 MD files). yoker uses MyST (Markdown), oatk uses RST.

**Sources:**
- Glob results from both projects

---

## 10. Package Structure

### 10.1 Source Organization

**yoker**: Modular architecture
```
src/yoker/
├── __init__.py           # Public API exports (111 lines)
├── agent.py              # Agent core
├── agents/               # Agent definitions
├── commands/             # Slash commands
├── config/               # Configuration loading
├── context/              # Context management
├── events/               # Event system
├── exceptions.py        # Exception hierarchy
├── logging.py           # Structured logging
├── thinking.py          # Thinking mode
└── tools/               # Tool implementations
    ├── base.py
    ├── read.py
    ├── write.py
    └── ...
```

**oatk**: Flat structure
```
oatk/
├── __init__.py          # Main toolkit (259 lines)
├── __main__.py          # CLI entry
├── types.py             # Type definitions
├── async_toolkit.py     # Async implementation
├── async_client.py      # Async client
├── fastapi.py           # FastAPI integration
├── js/                  # JavaScript helpers
└── fake/                # Test server
    ├── __init__.py
    ├── db.py
    ├── routes.py
    └── templates/
```

**Sources:**
- [yoker/src/yoker/__init__.py](file:///Users/xtof/Workspace/agentic/yoker/src/yoker/__init__.py)
- [oatk/oatk/__init__.py](file:///Users/xtof/Workspace/agentic/oatk/oatk/__init__.py)

---

## 11. Testing Setup

### 11.1 Test Organization

**yoker**:
```
tests/
├── test_agent.py
├── test_tools/
├── test_config/
└── ...
```

**oatk**:
```
tests/
├── __init__.py
├── conftest.py
├── test_oauth_toolkit.py
├── test_decorators.py
├── test_async_toolkit.py
├── test_async_decorators.py
├── test_async_client.py
├── test_fake_server.py
├── test_quart.py
└── test_fastapi.py
```

**Analysis**: oatk has more comprehensive test coverage with framework-specific tests.

**Sources:**
- Glob results from both projects

---

## Resource Comparison

### Configuration Patterns

| Aspect | yoker | oatk | Best Practice |
|--------|-------|------|---------------|
| **Source layout** | src/ | flat | src/ (prevents import issues) |
| **Line length** | 100 | 88 | 88-100 (subjective) |
| **Indentation** | 2 spaces | 2 spaces | 2 spaces (consistent) |
| **Type checking** | strict + decorators | strict + overrides | Both valid |
| **Coverage config** | minimal excludes | explicit omits | Both valid |
| **Tox setup** | identical | identical | Modern tox-uv |
| **UV usage** | ✓ | ✓ | Modern standard |
| **Ruff usage** | ✓ | ✓ | Modern standard |
| **GitHub Actions** | ✓ (comprehensive) | ✗ | Required for CI/CD |
| **CLAUDE.md** | ✓ (detailed) | ✗ | Recommended for AI-assisted development |
| **Makefile targets** | ✓ (help, convenience) | ✗ | Improves DX |
| **Python version file** | ✓ | ✗ | Helpful for pyenv users |
| **Badges** | ✓ (8) | ✓ (3) | More badges = more trust |

---

## Key Findings

### Corroborated Information

Information confirmed across multiple sources:

1. **Both projects use uv**: Confirmed in Makefiles and pyproject.toml
2. **Both use ruff**: Confirmed in pyproject.toml and Makefiles
3. **Both use mypy strict**: Confirmed in pyproject.toml
4. **Both use tox**: Confirmed in pyproject.toml and Makefiles
5. **Both use hatchling**: Confirmed in pyproject.toml
6. **Both support Python 3.10-3.12**: Confirmed in pyproject.toml, tox config, and GitHub Actions

### Unique to yoker

1. **GitHub Actions CI/CD**: Multi-OS, multi-Python testing
2. **src/ layout**: Modern packaging standard
3. **CLAUDE.md**: 317-line comprehensive project guide
4. **Detailed Makefile**: Help target, convenience targets
5. **Better .gitignore**: More comprehensive
6. **python-version file**: For pyenv users
7. **Analysis directory**: Architecture documentation
8. **Examples directory**: Usage examples
9. **Media directory**: Screenshots, diagrams
10. **More badges**: Downloads, tests, coverage, docs status

### Unique to oatk

1. **No CI/CD**: No GitHub Actions
2. **Flat layout**: Older packaging pattern
3. **More dependency groups**: Modular extras (async, quart, fastapi)
4. **More extensive docs**: 11 RST files vs 5 MD files
5. **More framework tests**: Framework-specific test files
6. **Fake test server**: Built-in test infrastructure

---

## Changes from Previous Research

Not applicable - this is the first research on this topic.

---

## Near-Miss Tier

For recommendations that didn't make the top priorities but are still valuable:

### Adopt MyST Parser for Docs — Alternative Documentation Format
- **Why it nearly made the cut**: yoker uses MyST (Markdown with extensions) which is more accessible than RST
- **Why it ranked below**: RST is well-established, Sphinx supports both, migration effort not justified
- **Best for**: New projects or projects where Markdown familiarity is important

### Adopt 100 Character Line Length — Alternative Style Choice
- **Why it nearly made the cut**: yoker uses 100 chars, providing more horizontal space
- **Why it ranked below**: 88 chars (black default) is more widely adopted, no clear benefit
- **Best for**: Teams that prefer more horizontal space and have existing 100-char convention

### Add More Badges — Enhanced Visibility
- **Why it nearly made the cut**: More badges increase project credibility and visibility
- **Why it ranked below**: Cosmetic improvement, doesn't affect functionality
- **Best for**: Projects with active CI/CD and documentation hosting

---

## Key Takeaways

1. **yoker represents the current best practice**: With GitHub Actions CI/CD, src/ layout, comprehensive CLAUDE.md, and detailed Makefile, yoker demonstrates the most mature project setup.

2. **CI/CD is critical for modern projects**: oatk's lack of GitHub Actions is a significant gap. Automated testing across OSes and Python versions should be standard.

3. **Project documentation matters**: The detailed CLAUDE.md file in yoker (317 lines) provides comprehensive guidance for both humans and AI assistants. This should be adopted as a standard.

4. **src/ layout prevents issues**: The src/ layout used by yoker is recommended by setuptools and prevents import-related issues during development.

5. **Makefile convenience targets improve DX**: yoker's help target, test-file, test-one, and version-specific test targets make development more efficient.

6. **Both projects use modern tooling**: uv, ruff, mypy, tox-uv are all modern, fast tools. This is a shared best practice.

7. **Configuration consistency**: Both projects use similar ruff, mypy, pytest, and coverage configurations, showing convergence on best practices.

8. **oatk needs fixes**: The pytest and tox configurations incorrectly reference `yoker` instead of `oatk` for coverage, showing copy-paste errors.

---

## Recommendations for oatk

### High Priority (Should Implement)

1. **Add GitHub Actions CI/CD**
   - Create `.github/workflows/test.yaml` based on yoker's pattern
   - Include test, lint, and typecheck jobs
   - Use matrix testing for OS and Python versions
   - Estimated effort: 1-2 hours

2. **Add CLAUDE.md or AGENTS.md**
   - Create comprehensive project guide similar to yoker's CLAUDE.md
   - Include: project overview, architecture, setup instructions, conventions
   - Document Makefile targets and development workflow
   - Estimated effort: 2-3 hours

3. **Fix pytest and tox configuration**
   - Change `--cov=yoker` to `--cov=oatk` in both configurations
   - Estimated effort: 5 minutes

4. **Add .python-version file**
   - Create file with `3.12` (or preferred version)
   - Helps pyenv users
   - Estimated effort: 1 minute

5. **Improve Makefile**
   - Add help target with auto-generated documentation
   - Add convenience targets: test-file, test-one, test-3.x
   - Add check target (typecheck + lint)
   - Add clean-all target
   - Organize into sections with headers
   - Estimated effort: 1 hour

6. **Enhance .gitignore**
   - Add comprehensive patterns from yoker
   - Include IDE, testing, and documentation patterns
   - Estimated effort: 15 minutes

### Medium Priority (Consider Implementing)

7. **Migrate to src/ layout**
   - Move `oatk/` to `src/oatk/`
   - Update pyproject.toml build configuration
   - Update all imports and references
   - Estimated effort: 2-4 hours

8. **Add more badges**
   - PyPI downloads
   - Tests status (after CI/CD)
   - Coverage status
   - Documentation status
   - Estimated effort: 15 minutes

9. **Add examples directory**
   - Create examples/ with usage examples
   - Document common use cases
   - Estimated effort: 2-3 hours

### Low Priority (Optional)

10. **Consider MyST parser for docs**
    - Evaluate switching from RST to MyST
    - Migration effort vs. benefits
    - Estimated effort: 4-8 hours

11. **Add analysis directory**
    - Document architecture decisions
    - Create architecture diagrams
    - Estimated effort: 4-6 hours

---

## Recommendations for C3 Harness

### Document as Standard

1. **Create python-project skill documentation**
   - Document all best practices identified in this research
   - Include templates for Makefile, pyproject.toml, .gitignore
   - Include GitHub Actions workflow template
   - Include CLAUDE.md template

2. **Update start-baseweb-project skill**
   - Consider migrating from pyenv to uv (currently uses pyenv)
   - Add GitHub Actions setup
   - Add CLAUDE.md template
   - Update Makefile pattern

3. **Create project-setup checklist**
   - Standard checklist for new projects
   - Include all high-priority recommendations
   - Provide migration guide for existing projects

---

## Further Research Needed

1. **Evaluate src/ layout migration**: Assess impact on existing oatk users and documentation
2. **Benchmark CI/CD performance**: Compare yoker's GitHub Actions with alternative CI systems
3. **Survey badge value**: Research correlation between badges and project adoption
4. **Documentation format analysis**: Compare MyST vs RST adoption trends in Python ecosystem

---

## Sources

[1] oatk/Makefile - /Users/xtof/Workspace/agentic/oatk/Makefile - Read 2026-05-06
[2] oatk/pyproject.toml - /Users/xtof/Workspace/agentic/oatk/pyproject.toml - Read 2026-05-06
[3] oatk/README.md - /Users/xtof/Workspace/agentic/oatk/README.md - Read 2026-05-06
[4] oatk/.gitignore - /Users/xtof/Workspace/agentic/oatk/.gitignore - Read 2026-05-06
[5] yoker/Makefile - /Users/xtof/Workspace/agentic/yoker/Makefile - Read 2026-05-06
[6] yoker/pyproject.toml - /Users/xtof/Workspace/agentic/yoker/pyproject.toml - Read 2026-05-06
[7] yoker/README.md - /Users/xtof/Workspace/agentic/yoker/README.md - Read 2026-05-06
[8] yoker/.gitignore - /Users/xtof/Workspace/agentic/yoker/.gitignore - Read 2026-05-06
[9] yoker/CLAUDE.md - /Users/xtof/Workspace/agentic/yoker/CLAUDE.md - Read 2026-05-06
[10] yoker/src/yoker/__init__.py - /Users/xtof/Workspace/agentic/yoker/src/yoker/__init__.py - Read 2026-05-06
[11] yoker/.github/workflows/test.yaml - /Users/xtof/Workspace/agentic/yoker/.github/workflows/test.yaml - Read 2026-05-06
[12] yoker/.python-version - /Users/xtof/Workspace/agentic/yoker/.python-version - Read 2026-05-06
[13] yoker/analysis/architecture.md - /Users/xtof/Workspace/agentic/yoker/analysis/architecture.md - Read 2026-05-06
[14] yoker/tests/test_agent.py - /Users/xtof/Workspace/agentic/yoker/tests/test_agent.py - Read 2026-05-06
[15] c3/skills/start-baseweb-project/SKILL.md - /Users/xtof/Workspace/agentic/c3/skills/start-baseweb-project/SKILL.md - Read 2026-05-06
[16] c3/skills/start-baseweb-project/Makefile - /Users/xtof/Workspace/agentic/c3/skills/start-baseweb-project/Makefile - Read 2026-05-06
[17] c3/skills/start-baseweb-project/requirements.base.txt - /Users/xtof/Workspace/agentic/c3/skills/start-baseweb-project/requirements.base.txt - Read 2026-05-06
[18] ~/.claude/Makefile - /Users/xtof/.claude/Makefile - Read 2026-05-06