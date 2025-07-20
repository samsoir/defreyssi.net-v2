# defreyssi.net Hugo Site Makefile

# Variables
VENV_DIR := venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip
PYTEST := $(VENV_DIR)/bin/pytest
HUGO := hugo
PORT := 1313

# Default target
.DEFAULT_GOAL := help

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

.PHONY: help install test test-verbose clean serve build fetch-youtube dev setup

help: ## Show this help message
	@echo "$(BLUE)defreyssi.net Hugo Site$(NC)"
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

setup: ## Set up development environment (create venv and install dependencies)
	@echo "$(YELLOW)Setting up development environment...$(NC)"
	python -m venv $(VENV_DIR)
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Development environment ready!$(NC)"
	@echo "$(BLUE)Activate with: source $(VENV_DIR)/bin/activate$(NC)"

install: ## Install Python dependencies (requires existing venv)
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "$(RED)Error: Virtual environment not found. Run 'make setup' first.$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Installing Python dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

test: ## Run unit tests
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "$(RED)Error: Virtual environment not found. Run 'make setup' first.$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Running tests...$(NC)"
	PYTHONPATH=scripts $(PYTEST) tests/ -q
	@echo "$(GREEN)✓ All tests passed$(NC)"

test-verbose: ## Run unit tests with verbose output
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "$(RED)Error: Virtual environment not found. Run 'make setup' first.$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Running tests (verbose)...$(NC)"
	PYTHONPATH=scripts $(PYTEST) tests/ -v

test-coverage: ## Run tests with coverage report
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "$(RED)Error: Virtual environment not found. Run 'make setup' first.$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Running tests with coverage...$(NC)"
	PYTHONPATH=scripts $(PYTEST) tests/ --cov=scripts --cov-report=term-missing

fetch-youtube: ## Fetch latest YouTube data (requires YOUTUBE_API_KEY)
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "$(RED)Error: Virtual environment not found. Run 'make setup' first.$(NC)"; \
		exit 1; \
	fi
	@if [ -z "$$YOUTUBE_API_KEY" ]; then \
		echo "$(RED)Error: YOUTUBE_API_KEY environment variable not set$(NC)"; \
		echo "$(YELLOW)Set it with: export YOUTUBE_API_KEY=\"your-api-key\"$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Fetching YouTube data...$(NC)"
	$(PYTHON) scripts/fetch-youtube-data.py
	@echo "$(GREEN)✓ YouTube data updated$(NC)"

build: ## Build Hugo site (production)
	@echo "$(YELLOW)Building Hugo site...$(NC)"
	$(HUGO) --minify
	@echo "$(GREEN)✓ Site built to public/$(NC)"

serve: ## Start Hugo development server
	@echo "$(YELLOW)Starting Hugo development server on http://localhost:$(PORT)$(NC)"
	@echo "$(BLUE)Press Ctrl+C to stop$(NC)"
	$(HUGO) server --buildDrafts --port $(PORT)

serve-with-youtube: fetch-youtube serve ## Fetch YouTube data and start development server

dev: ## Full development workflow (fetch YouTube + serve)
dev: serve-with-youtube

clean: ## Clean build artifacts and caches
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	rm -rf public/
	rm -rf resources/
	rm -rf .hugo_build.lock
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Clean complete$(NC)"

clean-test-data: ## Clean any leaked test data from production directories
	@echo "$(YELLOW)Cleaning test data leaks...$(NC)"
	@rm -f data/youtube/UCtest123.json data/youtube/UCempty.json 2>/dev/null || true
	@rm -rf content/youtube/test-channel content/youtube/empty-channel 2>/dev/null || true
	@echo "$(GREEN)✓ Test data cleaned$(NC)"

clean-all: clean ## Clean everything including venv
	@echo "$(YELLOW)Removing virtual environment...$(NC)"
	rm -rf $(VENV_DIR)
	@echo "$(GREEN)✓ Everything cleaned$(NC)"

check: ## Run all checks (tests + build)
	@echo "$(BLUE)Running full check pipeline...$(NC)"
	@$(MAKE) test
	@$(MAKE) build
	@echo "$(GREEN)✓ All checks passed$(NC)"

# Development workflow targets
quick-test: ## Quick test run (no coverage)
	@PYTHONPATH=scripts $(PYTEST) tests/ -x -q

watch-tests: ## Watch for changes and run tests automatically
	@if command -v entr >/dev/null 2>&1; then \
		find tests/ scripts/ -name "*.py" | entr -c $(MAKE) quick-test; \
	else \
		echo "$(RED)Error: 'entr' not found. Install with: sudo pacman -S entr$(NC)"; \
	fi

# Info targets
status: ## Show project status
	@echo "$(BLUE)Project Status:$(NC)"
	@echo "  Virtual environment: $(if $(wildcard $(VENV_DIR)),$(GREEN)✓ Present$(NC),$(RED)✗ Missing$(NC))"
	@echo "  Hugo version: $$($(HUGO) version 2>/dev/null | head -1 || echo '$(RED)Not found$(NC)')"
	@echo "  Python version: $$($(if $(wildcard $(VENV_DIR)),$(PYTHON),python) --version 2>/dev/null || echo '$(RED)Not found$(NC)')"
	@echo "  YouTube API key: $(if $(YOUTUBE_API_KEY),$(GREEN)✓ Set$(NC),$(YELLOW)Not set$(NC))"
	@echo "  Last build: $(if $(wildcard public/index.html),$$(stat -c %y public/index.html 2>/dev/null || echo 'Unknown'),$(YELLOW)Never built$(NC))"

deps: ## Show dependency information
	@echo "$(BLUE)Dependencies:$(NC)"
	@echo "  Required: hugo, python3, make"
	@echo "  Optional: entr (for watch-tests)"
	@echo "  Python packages:"
	@if [ -f requirements.txt ]; then cat requirements.txt | sed 's/^/    /'; fi