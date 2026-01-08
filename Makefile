.PHONY: help install test lint format clean

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package in editable mode with all dependencies
	pip install -e ".[all]"

test:  ## Run tests with coverage
	pytest tests/ -v --cov=src --cov-report=term-missing

lint:  ## Run ruff linter and formatter checks
	ruff check src/ tests/
	ruff format --check src/ tests/

format:  ## Format code with ruff
	ruff format src/ tests/

clean:  ## Clean up generated files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
