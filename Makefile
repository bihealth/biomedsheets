.PHONY:
default: help

.PHONY: help
help:
	@echo help      -- display this help
	@echo black     -- apply black code formatter
	@echo lint      -- run linters
	@echo test      -- run tests through pytest
	@echo isort     -- run isort

.PHONY: black
black:
	black -l 100 .

.PHONY: snakefmt
snakefmt:
	snakefmt -l 100 . --include '(\.smk$$|\.rules$$|^Snakefile)'

.PHONY: lint
lint: flake8 lint-black lint-isort

.PHONY: isort
isort:
	isort --force-sort-within-sections --profile=black .

.PHONY: flake8
flake8:
	flake8

.PHONY: lint-black
lint-black:
	black -l 100 --check .

.PHONY: lint-snakefmt
lint-snakefmt:
	snakefmt -l 100 . --include '(\.smk$$|\.rules$$|^Snakefile)' --check

.PHONY: lint-isort
lint-isort:
	isort --force-sort-within-sections --profile=black --check .

test:
	py.test

coverage:
	coverage report
	coverage html
