#MODEL=qwen3.5:397b-cloud
#ARGS += --plugin-dir ./
ARGS += --agent c3:project-manager
ARGS += --plugin-dir ../c3

-include ~/.claude/Makefile

-include .env

# colors

GREEN=\033[0;32m
RED=\033[0;31m
BLUE=\033[0;34m
NC=\033[0m

# Python version for ruff

RUFF_PYTHON_VERSION ?= py311

PROJECT=$(shell basename $(CURDIR))

PACKAGE_NAME=`cat .pypi-template | grep "^package_module_name" | cut -d":" -f2 | xargs`

LOG_LEVEL?=INFO

# if we're inside our own repo folder, use the local module folder, else cli cmd
ifeq ($(wildcard pypi_template),)
  PYPI_TEMPLATE = pypi-template
else
  PYPI_TEMPLATE = python -m pypi_template
endif

RUN_CMD?=LOG_LEVEL=$(LOG_LEVEL) uv run python -m $(PACKAGE_NAME)
RUN_ARGS?=

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

# apply current pypi-template configuration, typically after upgrading it
apply: RUN_CMD=$(PYPI_TEMPLATE)
apply: RUN_ARGS=verbose apply
apply: run

# apply and reinstall
update: apply reinstall

# functional targets

run:
	@echo "👷‍♂️ $(BLUE)running$(GREEN) $(RUN_CMD) $(RUN_ARGS)$(NC)"
	@$(RUN_CMD) $(RUN_ARGS)

test: lint pytest

pytest:
	@echo "👷‍♂️ $(BLUE)running tests$(NC)"
	@uv run --extra dev pytest -v

coverage:
	@echo "👷‍♂️ $(BLUE)running tests with coverage$(NC)"
	@uv run --extra dev pytest --cov=oatk --cov-report=term --cov-report=html --cov-report=lcov

lint:
	@echo "👷‍♂️ $(BLUE)running linter$(NC)"
	@uv run --extra dev ruff check --target-version=$(RUFF_PYTHON_VERSION) .

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