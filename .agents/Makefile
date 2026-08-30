# Portable template checks. Existing project Makefiles may call these targets
# or run this file directly with: make -f .agents/Makefile verify

PYTHON ?= $(shell python3 -c "" >/dev/null 2>&1 && echo python3 || echo python)
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: help verify analyze test format format-check tool-tests context check-context check-template sync install-preview

help: ## List template targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(lastword $(MAKEFILE_LIST)) | \
		awk 'BEGIN {FS = ":.*?## "} {printf "  %-16s %s\n", $$1, $$2}'

verify: check-template check-context analyze test format-check tool-tests ## Run template and project checks

analyze: ## Run Dart/Flutter static analysis when applicable
	@if [ -f pubspec.yaml ]; then \
		if grep -q 'sdk: flutter' pubspec.yaml; then flutter analyze; else dart analyze; fi; \
	else echo "SKIP analyze: no pubspec.yaml"; fi

test: ## Run Dart/Flutter tests when applicable
	@if [ -f pubspec.yaml ]; then \
		if grep -q 'sdk: flutter' pubspec.yaml; then flutter test; else dart test; fi; \
	else echo "SKIP Dart/Flutter tests: no pubspec.yaml"; fi

format: ## Apply Dart formatting
	@if [ -f pubspec.yaml ]; then dart format .; else echo "SKIP format: no pubspec.yaml"; fi

format-check: ## Check Dart formatting
	@if [ -f pubspec.yaml ]; then dart format --output=none --set-exit-if-changed .; \
	else echo "SKIP format check: no pubspec.yaml"; fi

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
