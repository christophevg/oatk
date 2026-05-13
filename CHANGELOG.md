# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-05-13

### Added

- **AsyncOAuthToolkit** - Full async support with awaitable methods
- **Async HTTP client** - httpx-based async HTTP operations
- **FastAPI integration** - Dependency injection with `OAuthToolkitDependency`
- **Quart integration** - Async decorators for Quart framework
- **Context-based token management** - Using contextvars for async routes
- **Type hints** - Complete type annotations throughout codebase
- **Test infrastructure** - Comprehensive pytest suite (111 tests)
- **CI/CD pipeline** - GitHub Actions for testing and publishing
- **ReadTheDocs configuration** - Documentation hosting setup

### Changed

- **Packaging** - Migrated from setup.py to pyproject.toml (PEP 621)
- **Project layout** - Migrated from flat layout to src/ layout
- **Development workflow** - Updated to uv-based environment management
- **Dependencies** - Flask packages now core dependencies
- **Python version** - Minimum version updated to 3.10+

### Fixed

- Async decorator context handling
- Quart example async initialization

### Development

- Added mypy for type checking (strict mode)
- Added ruff for linting and formatting
- Added pytest-cov for coverage reporting
- Added tox for multi-version testing
- Configured Python 3.10-3.13 support

## [0.1.5] - 2022-10-15

### Added

- Initial OAuth toolkit implementation
- OAuthToolkit class for token creation and validation
- JWKS (JSON Web Key Set) handling
- Flask route decorators (@authenticated, @authenticated_with_claims)
- Fake OAuth server for testing
- JavaScript client library (oatk.js)
- CLI interface via Fire
- Examples for Flask, Quart, and FastAPI
- Google OAuth integration example

### Features

- Token creation with private key
- Token validation with public key
- Token decoding without verification
- JWKS import from file, string, or URL
- Provider-based configuration
- Method chaining for fluent API
- Clipboard support (macOS)
- File-based token loading

[Unreleased]: https://github.com/christophevg/oatk/compare/v0.1.5...HEAD
[0.1.5]: https://github.com/christophevg/oatk/releases/tag/v0.1.5