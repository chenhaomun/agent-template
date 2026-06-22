# Canonical verification entrypoints. Agents prefer these over raw commands
# (see AGENTS.md "Commands / Verify"). Flutter/Dart is the primary stack;
# adjust the analyze/test/format targets for other stacks.

PYTHON ?= python3
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: help verify analyze test format format-check tool-tests map check-map check-template

help: ## List available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "} {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

verify: check-template check-map analyze test format-check tool-tests ## Run integrity, analysis, tests, and format checks

analyze: ## Static analysis
	@if [ -f pubspec.yaml ]; then \
		if grep -q 'sdk: flutter' pubspec.yaml; then flutter analyze; else dart analyze; fi; \
	else echo "SKIP analyze: no pubspec.yaml"; fi

test: ## Run tests
	@if [ -f pubspec.yaml ]; then \
		if grep -q 'sdk: flutter' pubspec.yaml; then flutter test; else dart test; fi; \
	else echo "SKIP Dart/Flutter tests: no pubspec.yaml"; fi

format: ## Apply Dart formatting in place
	@if [ -f pubspec.yaml ]; then dart format .; else echo "SKIP format: no pubspec.yaml"; fi

format-check: ## Fail if any file is unformatted
	@if [ -f pubspec.yaml ]; then dart format --output=none --set-exit-if-changed .; \
	else echo "SKIP format check: no pubspec.yaml"; fi

tool-tests: ## Test shared agent enforcement tools
	$(PYTHON) -m unittest discover -s .agents/tests -p 'test_*.py'

map: ## Regenerate the project map
	$(PYTHON) .agents/tools/generate_project_map.py --write

check-map: ## Verify mapped folders exist and detected areas are mapped
	$(PYTHON) .agents/tools/check_project_map.py

check-template: ## Verify shared Claude/Codex template integrity
	$(PYTHON) .agents/tools/check_template.py
