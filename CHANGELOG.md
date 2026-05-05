# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Type hints to entire codebase for better IDE support and type checking
- Comprehensive test infrastructure with pytest
- Modern uv-based project setup with pyproject.toml
- Type aliases in oatk/types.py (ClaimsDict, JWKSDict, Decorator, etc.)

### Changed

- Migrated from setup.py to pyproject.toml (PEP 621 compliant)
- Migrated from pyenv virtualenvs to uv managed environments
- Updated Makefile to use uv commands
- Flask packages are now core dependencies (not optional)

### Development

- Added mypy for type checking
- Added ruff for linting
- Added pytest for testing
- Added coverage for test coverage reporting
- Configured Python 3.9+ as minimum version

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