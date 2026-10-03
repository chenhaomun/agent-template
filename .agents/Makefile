# Portable template checks. Existing project Makefiles may call these targets
# or run this file directly with: make -f .agents/Makefile verify

PYTHON ?= python
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: help verify analyze test format format-check tool-tests context check-context check-template sync install-preview

help: ## List template targets
	@$(PYTHON) .agents/tools/run_checks.py --help

verify: check-template check-context analyze test format-check tool-tests ## Run template and project checks

analyze: ## Run Dart/Flutter static analysis when applicable
	$(PYTHON) .agents/tools/run_checks.py analyze

test: ## Run Dart/Flutter tests when applicable
	$(PYTHON) .agents/tools/run_checks.py test

format: ## Apply Dart formatting
	$(PYTHON) .agents/tools/run_checks.py format

format-check: ## Check Dart formatting
	$(PYTHON) .agents/tools/run_checks.py format-check

tool-tests: ## Test agent tooling
	$(PYTHON) -m unittest discover -s .agents/tests -p 'test_*.py'

context: ## Refresh generated project-context structure
	$(PYTHON) .agents/tools/generate_project_context.py --write

check-context: ## Verify project context
	$(PYTHON) .agents/tools/check_project_context.py

check-template: ## Verify Claude/Codex template integrity
	$(PYTHON) .agents/tools/check_template.py

sync: ## Refresh Claude/Codex adapters
	$(PYTHON) .agents/tools/sync_shared.py

install-preview: ## Preview installation; TARGET=/path/to/project
	$(PYTHON) .agents/tools/install_template.py "$(TARGET)"
