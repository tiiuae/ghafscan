# SPDX-FileCopyrightText: 2023 Technology Innovation Institute (TII)
#
# SPDX-License-Identifier: Apache-2.0

SHELL := bash
PYTHON_TARGETS := $(shell find . -name "*.py" ! -path "*venv*" ! -path "*eggs*")

define target_success
	@printf "\033[32m==> Target \"$(1)\" passed\033[0m\n\n"
endef

.DEFAULT_GOAL := help

TARGET: ## DESCRIPTION
	@echo "TARGET is here only to provide the header for 'help'"

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?##.*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}'

pre-push: test black style pylint reuse-lint ## Run tests, style checks, pylint, reuse-lint
	$(call target_success,$@)

test: ## Run tests
	pytest -vx tests/
	$(call target_success,$@)

black: clean ## Reformat with black
	@for py in $(PYTHON_TARGETS); \
		do echo "$$py:"; \
		black -q $$py; \
	done
	$(call target_success,$@)

style: clean ## Check with pycodestyle (pep8)
	pycodestyle --max-line-length 90 --exclude='venv/' .
	$(call target_success,$@)

pylint: clean ## Check with pylint
	pylint -rn $(PYTHON_TARGETS) || exit 1
	$(call target_success,$@)

reuse-lint: clean ## Check with reuse lint
	reuse lint
	$(call target_success,$@)

clean: ## Remove build artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	find . -name '.eggs' -exec rm -rf {} +
	rm -fr .pytest_cache/
	$(call target_success,$@)

pristine: clean ## Pristine clean: remove all untracked files and folders
	git clean -f -d -x
	$(call target_success,$@)
