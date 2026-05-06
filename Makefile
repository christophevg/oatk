# colors

GREEN=\033[0;32m
RED=\033[0;31m
BLUE=\033[0;34m
NC=\033[0m

RUFF_PYTHON_VERSION ?= py311

# Installation targets - uv manages virtualenvs automatically

install:
	@echo "👷‍♂️ $(BLUE)syncing dependencies with uv$(NC)"
	@uv sync --all-extras

uninstall: clean-venv

clean-venv:
	@echo "👷‍♂️ $(RED)removing .venv directory$(NC)"
	@-rm -rf .venv

reinstall: clean-venv install

upgrade:
	@echo "👷‍♂️ $(BLUE)upgrading all packages$(NC)"
	@uv sync --all-extras --upgrade

sync: ## Sync dependencies from lock file
	uv sync --frozen --all-extras

# functional targets

test: format-check lint typecheck pytest

test-all: ## Run tests against all supported Python versions (3.10, 3.11, 3.12)
	uv run tox

pytest:
	@echo "👷‍♂️ $(BLUE)running tests$(NC)"
	@uv run --extra dev pytest -v

coverage:
	@echo "👷‍♂️ $(BLUE)running tests with coverage$(NC)"
	@uv run --extra dev pytest --cov=oatk --cov-report=term --cov-report=html --cov-report=lcov

lint:
	@echo "👷‍♂️ $(BLUE)running linter$(NC)"
	@uv run --extra dev ruff check --target-version=$(RUFF_PYTHON_VERSION) .

typecheck:
	@echo "👷‍♂️ $(BLUE)running type checking$(NC)"
	@uv run mypy --strict oatk

format-check:
	@echo "👷‍♂️ $(BLUE)formatting$(NC)"
	@uv run ruff format --check oatk tests examples

format:
	@echo "👷‍♂️ $(BLUE)formatting$(NC)"
	@uv run ruff format oatk tests examples

# packaging targets

publish-test: dist
	@echo "👷‍♂️ $(BLUE)publishing to PyPI test$(NC)"
	uv publish --repository testpypi

publish: dist
	@echo "👷‍♂️ $(BLUE)publishing to PyPI$(NC)"
	uv publish

dist: dist-clean
	@echo "👷‍♂️ $(BLUE)building distribution$(NC)"
	uv build

dist-clean:
	@rm -rf dist build *.egg-info

clean:
	@find . -type f -name "*.backup" -delete

.PHONY: install uninstall clean-venv reinstall upgrade apply update run test pytest coverage lint publish-test publish dist dist-clean clean

# include optional a personal/local touch

-include Makefile.mak
