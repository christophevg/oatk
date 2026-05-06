# Research Index

This index tracks all research conducted for the oatk project.

---

### Project Setup Standardization

**Folder**: `2026-05-06-project-setup-standardization/`
**Date**: 2026-05-06
**Status**: Complete

**Summary**: Comparative analysis of project setup patterns across oatk, yoker, and C3 harness to identify best practices for standardization.

**Key Findings**:
- yoker has more comprehensive CI/CD with GitHub Actions (oatk has none)
- yoker uses src/ layout (best practice) vs oatk flat layout
- yoker has extensive CLAUDE.md with project conventions
- Both use uv for dependency management
- yoker has better structured documentation (docs/, analysis/, examples/)
- Both use ruff for linting/formatting with similar configs
- yoker has more comprehensive .gitignore

**Sources**: 18 local files analyzed

**Keywords**: project-setup, makefile, pyproject.toml, uv, ruff, mypy, tox, github-actions, documentation, best-practices