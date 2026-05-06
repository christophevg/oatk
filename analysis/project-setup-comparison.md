# Project Setup Comparison: oatk vs yoker vs C3

**Generated**: 2026-05-06
**Research**: [research/2026-05-06-project-setup-standardization/](../research/2026-05-06-project-setup-standardization/)

---

## Executive Summary

This document provides a side-by-side comparison of project setup patterns across three sources: oatk, yoker, and the C3 harness's start-baseweb-project skill. The comparison reveals that **yoker represents the most mature and comprehensive setup**, while oatk has gaps in CI/CD, project documentation, and developer experience features.

---

## Comparison Tables

### 1. Build System & Dependency Management

| Aspect | oatk | yoker | C3 start-baseweb | Best Practice |
|--------|------|-------|-------------------|---------------|
| **Build backend** | hatchling | hatchling | N/A (template) | hatchling |
| **Package manager** | uv | uv | pyenv + pip | uv (modern, fast) |
| **Source layout** | flat | src/ | flat | src/ (prevents import issues) |
| **Version management** | dynamic (from file) | static in file | N/A | Both valid |
| **Dependency groups** | 7 groups (all, dev, run, async, quart, fastapi, docs) | 2 groups (dev, docs) | N/A | Context-dependent |
| **Lock file** | uv.lock | uv.lock | N/A | Required for reproducibility |
| **Python version file** | ✗ | ✓ (.python-version) | ✗ | Recommended for pyenv |

---

### 2. Makefile Targets

| Target | oatk | yoker | C3 start-baseweb | Notes |
|--------|------|-------|------------------|-------|
| **install** | ✓ | ✓ | ✓ | uv sync --all-extras |
| **sync** | ✓ | ✓ | ✗ | uv sync --frozen |
| **test** | ✓ (all checks) | ✓ (pytest only) | ✓ (coverage) | oatk runs all checks by default |
| **test-all** | ✓ | ✓ | ✗ | Multi-version testing with tox |
| **test-file** | ✗ | ✓ | ✗ | Run specific test file |
| **test-one** | ✗ | ✓ | ✗ | Run specific test function |
| **test-3.x** | ✗ | ✓ | ✗ | Version-specific testing |
| **pytest** | ✓ | ✗ | ✗ | oatk separates pytest |
| **coverage** | ✓ | ✗ | ✓ | Standalone coverage |
| **docs** | ✗ | ✓ | ✗ | Build documentation |
| **docs-view** | ✗ | ✓ | ✗ | Build and open docs |
| **demo/demos** | ✗ | ✓ | ✗ | Screenshot generation |
| **typecheck** | ✓ | ✓ | ✗ | mypy --strict |
| **lint** | ✓ | ✓ | ✓ | ruff check |
| **format** | ✓ | ✓ | ✗ | ruff format |
| **format-check** | ✓ | ✗ | ✗ | Format validation |
| **check** | ✗ | ✓ | ✗ | Combined typecheck + lint |
| **build** | ✗ (dist target) | ✓ | ✗ | Build package |
| **publish** | ✗ | ✓ | ✗ | Publish to PyPI |
| **publish-test** | ✓ | ✓ | ✗ | Publish to TestPyPI |
| **dist** | ✓ | ✗ | ✗ | Build distributions |
| **clean** | ✓ (minimal) | ✓ (comprehensive) | ✓ | Clean artifacts |
| **clean-all** | ✗ | ✓ | ✗ | Deep clean (removes .venv) |
| **clean-venv** | ✓ | ✗ | ✗ | Remove venv only |
| **reinstall** | ✓ | ✗ | ✗ | Clean venv + install |
| **upgrade** | ✓ | ✗ | ✗ | Upgrade all packages |
| **help** | ✗ | ✓ | ✗ | Auto-generated help |

**Summary**: yoker has 27 targets vs oatk's 19. yoker's help target and convenience targets (test-file, test-one, test-3.x) improve developer experience significantly.

---

### 3. Code Quality Tools

| Tool | oatk | yoker | C3 start-baseweb | Notes |
|------|------|-------|------------------|-------|
| **Linter** | ruff | ruff | ruff | Modern replacement for flake8 |
| **Formatter** | ruff format | ruff format | N/A | Modern replacement for black |
| **Type checker** | mypy (strict) | mypy (strict) | N/A | Both use strict mode |
| **Test runner** | pytest | pytest | pytest | Standard |
| **Coverage** | pytest-cov | pytest-cov | coverage | Standard |
| **Multi-version** | tox-uv | tox-uv | N/A | Both use tox with uv |

---

### 4. Ruff Configuration

| Setting | oatk | yoker | Best Practice |
|---------|------|-------|---------------|
| **target-version** | py310 | py310 | Match requires-python |
| **line-length** | 88 | 100 | 88-100 (subjective) |
| **indent-width** | 2 | 2 | Consistent |
| **quote-style** | double | default | Consistent |
| **docstring-code-format** | true | default | Nice to have |
| **lint select** | E, W, F, I, B, C4, UP, ARG, SIM | E, W, F, I, B, C4, UP | oatk has more rules |
| **lint ignore** | E501, B008 | E501 | Both ignore line-too-long |

**Analysis**: oatk has stricter linting with ARG (unused arguments) and SIM (simplify) rules. Both configurations are valid.

---

### 5. Mypy Configuration

| Setting | oatk | yoker | Notes |
|---------|------|-------|-------|
| **python_version** | 3.10 | 3.10 | Consistent |
| **warn_return_any** | true | true | Strict |
| **disallow_untyped_defs** | true | true | Strict |
| **disallow_incomplete_defs** | true | true | Strict |
| **check_untyped_defs** | true | true | Strict |
| **disallow_untyped_decorators** | ✗ | true | yoker stricter |
| **warn_no_return** | ✗ | true | yoker stricter |
| **strict_equality** | ✗ | true | yoker stricter |
| **show_error_context** | true | ✗ | oatk more verbose |
| **show_column_numbers** | true | ✗ | oatk more verbose |
| **Module overrides** | Extensive | None | oatk has many third-party overrides |

**Analysis**: yoker has stricter core settings, oatk has more verbose output and extensive module overrides for third-party libraries.

---

### 6. CI/CD Configuration

| Feature | oatk | yoker | C3 start-baseweb |
|---------|------|-------|-------------------|
| **GitHub Actions** | ✗ | ✓ | ✗ |
| **Workflow file** | N/A | test.yaml | N/A |
| **Multi-OS testing** | N/A | ✓ (Ubuntu, macOS, Windows) | N/A |
| **Multi-Python testing** | N/A | ✓ (3.10, 3.11, 3.12) | N/A |
| **Test job** | N/A | ✓ | N/A |
| **Lint job** | N/A | ✓ | N/A |
| **Typecheck job** | N/A | ✓ | N/A |
| **uv setup action** | N/A | ✓ (setup-uv@v6) | N/A |
| **Coverage reporting** | N/A | ✓ (--cov-report=xml) | N/A |
| **Matrix strategy** | N/A | ✓ | N/A |

**Critical Gap**: oatk has no CI/CD. This is a significant gap for modern projects.

---

### 7. Project Documentation

| Feature | oatk | yoker | C3 start-baseweb |
|---------|------|-------|-------------------|
| **README.md** | ✓ (212 lines) | ✓ (209 lines) | ✓ (template) |
| **CLAUDE.md** | ✗ | ✓ (317 lines) | ✗ |
| **AGENTS.md** | ✗ | ✗ | ✓ (template) |
| **docs/ directory** | ✓ (11 RST files) | ✓ (5 MD files) | ✗ |
| **analysis/ directory** | ✗ | ✓ | ✗ |
| **examples/ directory** | ✗ | ✓ | ✗ |
| **media/ directory** | ✗ | ✓ (screenshots) | ✗ |
| **Doc format** | reStructuredText | MyST (Markdown) | N/A |
| **README badges** | 3 | 8 | N/A |

**Analysis**: yoker has comprehensive project documentation with CLAUDE.md providing detailed guidance for both humans and AI assistants. oatk has more extensive API documentation (11 RST files) but lacks project-level documentation.

---

### 8. README Content

| Section | oatk | yoker |
|---------|------|-------|
| **Installation** | ✓ | ✓ |
| **Quick Start** | ✓ (sync + async) | ✓ (with screenshot) |
| **Why this project?** | ✗ | ✓ ("Why Yoker?") |
| **Features** | ✓ | ✓ (current + planned) |
| **Framework integrations** | ✓ (Flask, FastAPI) | ✗ |
| **Configuration** | ✗ | ✓ (TOML) |
| **Architecture** | ✗ | ✓ (with diagram) |
| **CLI usage** | ✓ | ✓ (via --help) |
| **Documentation links** | ✓ | ✓ |
| **Use cases** | ✓ | ✗ |
| **Development setup** | ✗ | ✓ (make setup) |
| **Contributing** | ✗ | ✓ |
| **Changelog** | ✗ | ✓ |
| **License** | ✓ | ✓ |
| **Security disclaimer** | ✓ | ✗ |
| **Name etymology** | ✗ | ✓ |

---

### 9. Git Configuration

| Feature | oatk | yoker |
|---------|------|-------|
| **.gitignore size** | 18 lines | 54 lines |
| **Build artifacts** | ✓ | ✓ (more comprehensive) |
| **Python cache** | ✓ | ✓ |
| **Virtual env** | ✓ | ✓ |
| **Testing artifacts** | ✓ | ✓ (more comprehensive) |
| **Type checking cache** | ✗ | ✓ (.mypy_cache) |
| **IDE configs** | ✗ | ✓ (.idea, .vscode) |
| **OS files** | ✓ | ✓ |
| **Documentation builds** | ✓ | ✓ |
| **Project-specific** | ✓ (pem, certs) | ✓ (context, logs, jsonl) |
| **Local configs** | ✓ (*.local) | ✓ (yoker.toml, .env.local) |
| **Generated files** | ✗ | ✓ (media/session.jsonl) |

**Analysis**: yoker's .gitignore is more comprehensive and better organized.

---

### 10. Package Structure

| Aspect | oatk | yoker |
|--------|------|-------|
| **Layout** | flat | src/ |
| **Package location** | ./oatk | ./src/yoker |
| **Main module size** | 259 lines (__init__.py) | 111 lines (__init__.py) |
| **Architecture** | Flat, functional | Modular, hierarchical |
| **Submodules** | fake/, js/ | agents/, commands/, config/, context/, events/, exceptions/, logging/, thinking/, tools/ |
| **Test organization** | Flat, comprehensive | Hierarchical |
| **Number of test files** | 10 | 1+ per module |

**Analysis**: yoker's src/ layout and modular architecture is more maintainable. oatk's flat layout is simpler but doesn't scale as well.

---

### 11. Testing Setup

| Feature | oatk | yoker |
|---------|------|-------|
| **Framework** | pytest | pytest |
| **Async support** | ✓ (pytest-asyncio) | ✓ (pytest-asyncio) |
| **Coverage tool** | pytest-cov | pytest-cov |
| **Mocking** | ✗ | ✓ (pytest-mock) |
| **HTTP testing** | ✓ (pytest-httpx) | ✗ |
| **Coverage source** | oatk (incorrectly says yoker in tox) | src |
| **Coverage branches** | true | true |
| **Coverage omits** | tests, __main__.py | None explicit |
| **Test files** | 10 | 1+ per module |

---

### 12. Tox Configuration

| Feature | oatk | yoker |
|---------|------|-------|
| **Environments** | py310, py311, py312 | py310, py311, py312 |
| **Pre-commands** | uv pip install -e .[all] | uv pip install -e . |
| **Test command** | pytest --cov=yoker (incorrect) | pytest --cov=yoker (incorrect) |
| **Python versions** | Explicit base_python | Explicit base_python |

**Bug**: Both projects have `--cov=yoker` in tox config. oatk should have `--cov=oatk`, yoker is correct.

---

## Best Practices Summary

### From yoker (Should Adopt)

1. **GitHub Actions CI/CD** - Multi-OS, multi-Python automated testing
2. **src/ layout** - Modern packaging standard
3. **CLAUDE.md** - Comprehensive project guide (317 lines)
4. **Help target in Makefile** - Auto-generated documentation
5. **Convenience targets** - test-file, test-one, test-3.x
6. **Comprehensive .gitignore** - Cover all common patterns
7. **.python-version file** - For pyenv users
8. **More README badges** - Downloads, tests, coverage, docs status
9. **Examples directory** - Usage examples
10. **Analysis directory** - Architecture documentation

### From oatk (Keep)

1. **More dependency groups** - Modular extras (async, quart, fastapi)
2. **Format-check target** - Separate validation from formatting
3. **More extensive API docs** - 11 RST files
4. **More framework tests** - Framework-specific test files
5. **Stricter linting rules** - ARG, SIM
6. **More verbose mypy** - show_error_context, show_column_numbers
7. **Built-in test server** - fake/ module for testing

### From C3 start-baseweb (Keep)

1. **AGENTS.md template** - Instructions for AI assistants
2. **Simple Makefile** - Easy to understand for new projects
3. **Pyenv setup** - Alternative to uv (but uv is preferred)

---

## Gap Analysis

### Critical Gaps in oatk

1. **No CI/CD** - No automated testing, linting, or type checking
2. **No CLAUDE.md/AGENTS.md** - No project guide for AI assistants
3. **No help target** - Makefile not self-documenting
4. **Incorrect tox config** - References wrong project for coverage

### Critical Gaps in yoker

1. **Less extensive API docs** - Only 5 MD files vs 11 RST files

### Critical Gaps in C3 start-baseweb

1. **Uses pyenv instead of uv** - Not following modern best practice
2. **No CI/CD template** - Should include GitHub Actions setup
3. **Minimal Makefile** - Missing modern targets
4. **No CLAUDE.md template** - Only AGENTS.md

---

## Standardization Recommendations

### For oatk

**High Priority (Implement Now)**:
1. Add GitHub Actions CI/CD (1-2 hours)
2. Add CLAUDE.md or AGENTS.md (2-3 hours)
3. Fix tox config (5 minutes)
4. Add .python-version file (1 minute)
5. Improve Makefile with help and convenience targets (1 hour)
6. Enhance .gitignore (15 minutes)

**Medium Priority (Consider)**:
7. Migrate to src/ layout (2-4 hours)
8. Add more badges (15 minutes)
9. Add examples directory (2-3 hours)

**Low Priority (Optional)**:
10. Consider MyST parser for docs (4-8 hours)
11. Add analysis directory (4-6 hours)

### For C3 Harness

**Should Create**:
1. **python-project skill** - Document all best practices
2. **GitHub Actions template** - Reusable workflow
3. **CLAUDE.md template** - Standard project guide
4. **Enhanced Makefile template** - With all modern targets
5. **src/ layout template** - Modern packaging pattern
6. **Migration guide** - For upgrading existing projects

---

## Next Steps

1. **Present recommendations to user** for approval
2. **Implement approved changes** in oatk
3. **Create python-project skill** in C3 harness
4. **Update start-baseweb-project** skill with modern patterns
5. **Document standards** in a central location

---

## Sources

See [research/2026-05-06-project-setup-standardization/SOURCES.md](../research/2026-05-06-project-setup-standardization/SOURCES.md) for complete source listing.