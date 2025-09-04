.PHONY: help install install-dev test test-cov lint format check-quality run dev docs clean

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run code linting"
	@echo "  format       - Format code with black"
	@echo "  check-quality - Run all quality checks"
	@echo "  run          - Run the application"
	@echo "  dev          - Run the application in development mode"
	@echo "  docs         - Generate documentation (placeholder)"
	@echo "  clean        - Clean up generated files"

# Install production dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install -e ".[dev]"

# Run tests
test:
	pytest

# Run tests with coverage
test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

# Run code linting
lint:
	ruff check .

# Format code with black
format:
	black .

# Run all quality checks
check-quality:
	black --check .
	ruff check .
	mypy --package app

# Run the application
run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run the application in development mode
dev:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Generate documentation (placeholder)
docs:
	@echo "Documentation generation placeholder"

# Clean up generated files
clean:
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf .ruff_cache
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete