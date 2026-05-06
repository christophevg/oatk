-include ~/.claude/Makefile

.PHONY: install sync test test-all test-file test-one \
        typecheck lint format format-check check build publish \
        publish-test clean clean-all help \
        quart-example fastapi-example

# colors

GREEN=\033[0;32m
RED=\033[0;31m
BLUE=\033[0;34m
NC=\033[0m

RUFF_PYTHON_VERSION ?= py311

## Setup

install: ## Install package in development mode with all extras
	@echo "👷‍♂️ $(BLUE)syncing dependencies with uv$(NC)"
	@uv sync --all-extras

uninstall: clean-venv ## Remove virtual environment

clean-venv: ## Remove virtual environment
	@echo "👷‍♂️ $(RED)removing .venv directory$(NC)"
	@-rm -rf .venv

reinstall: clean-venv install ## Clean install (removes venv and reinstalls)

upgrade: ## Upgrade all packages to latest versions
	@echo "👷‍♂️ $(BLUE)upgrading all packages$(NC)"
	@uv sync --all-extras --upgrade

sync: ## Sync dependencies from lock file
	uv sync --frozen --all-extras

## Testing

test: format-check lint typecheck pytest ## Run all tests with coverage and checks

test-all: ## Run tests against all supported Python versions (3.10, 3.11, 3.12)
	uv run tox

test-file: ## Run specific test file (usage: make test-file FILE=tests/test_x.py)
	uv run pytest $(FILE)

test-one: ## Run specific test (usage: make test-one TEST=tests/test_x.py::test_func)
	uv run pytest $(TEST)

pytest: ## Run tests with pytest
	@echo "👷‍♂️ $(BLUE)running tests$(NC)"
	@uv run --extra all pytest -v

coverage: ## Run tests with coverage reporting
	@echo "👷‍♂️ $(BLUE)running tests with coverage$(NC)"
	@uv run --extra all pytest --cov=src --cov-report=term --cov-report=html --cov-report=lcov

## Code Quality

typecheck: ## Run mypy type checking
	@echo "👷‍♂️ $(BLUE)running type checking$(NC)"
	@uv run mypy --strict src/oatk

lint: ## Run ruff linting
	@echo "👷‍♂️ $(BLUE)running linter$(NC)"
	@uv run --extra dev ruff check --target-version=$(RUFF_PYTHON_VERSION) src/oatk tests examples

format: ## Format code with ruff
	@echo "👷‍♂️ $(BLUE)formatting$(NC)"
	@uv run ruff format src/oatk tests examples

format-check: ## Check formatting without making changes
	@echo "👷‍♂️ $(BLUE)checking formatting$(NC)"
	@uv run ruff format --check src/oatk tests examples

check: typecheck lint format-check ## Run all checks (typecheck, lint, format-check)

## Build & Publish

build: dist ## Build package distributions

publish-test: dist ## Build and publish to TestPyPI
	@echo "👷‍♂️ $(BLUE)publishing to PyPI test$(NC)"
	uv publish --repository testpypi

publish: dist ## Build and publish to PyPI
	@echo "👷‍♂️ $(BLUE)publishing to PyPI$(NC)"
	uv publish

dist: dist-clean ## Build distributions
	@echo "👷‍♂️ $(BLUE)building distribution$(NC)"
	uv build

dist-clean: ## Clean build artifacts
	@rm -rf dist build *.egg-info

## Cleanup

clean: ## Remove build artifacts and backup files
	@find . -type f -name "*.backup" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

clean-all: clean dist-clean clean-venv ## Deep clean (removes venv, build artifacts, caches)

## Examples

quart-example: ## Run Quart OAuth example with automated curl tests
	./examples/quart_test.sh

quart-server: ## Start Quart OAuth example server for manual testing
	@echo "👷‍♂️ $(BLUE)starting Quart server (for manual testing)$(NC)"
	@echo "Server will be available at http://localhost:8000"
	@echo "Press Ctrl+C to stop"
	uv run uvicorn examples.quart_example:app --reload --port 8000

fastapi-example: ## Run FastAPI OAuth example automated test suite
	@echo "👷‍♂️ $(BLUE)running FastAPI example tests$(NC)"
	@echo "FastAPI example does not yet have automated tests"
	@echo "Starting server for manual testing instead..."
	@echo "Server will be available at http://localhost:8001"
	@echo "Press Ctrl+C to stop"
	uv run uvicorn examples.fastapi_example:app --reload --port 8001

fastapi-server: ## Start FastAPI OAuth example server for manual testing
	@echo "👷‍♂️ $(BLUE)starting FastAPI server (for manual testing)$(NC)"
	@echo "Server will be available at http://localhost:8001"
	@echo "Press Ctrl+C to stop"
	uv run uvicorn examples.fastapi_example:app --reload --port 8001

## Help

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# include optional a personal/local touch

-include Makefile.mak
