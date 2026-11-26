.PHONY: default
default: help

.PHONY: help
help:
	@echo help      -- display this help
	@echo format    -- apply ruff import sorting and formatting
	@echo lint      -- check with ruff (lint and formatting)
	@echo test      -- run tests through pytest
	@echo coverage  -- run tests with coverage report
	@echo docs      -- build the Sphinx HTML documentation

.PHONY: format
format:
	uv run ruff check --fix .
	uv run ruff format .

.PHONY: lint
lint:
	uv run ruff check .
	uv run ruff format --check .

.PHONY: test
test:
	uv run pytest

.PHONY: coverage
coverage:
	uv run pytest --cov=biomedsheets --cov-report=term-missing --cov-report=html

.PHONY: docs
docs:
	uv run $(MAKE) -C docs html
