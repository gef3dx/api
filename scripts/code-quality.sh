#!/bin/bash

# Exit on any error
set -e

echo "Running code quality checks..."

echo "Checking code formatting with black..."
black --check .

echo "Linting with ruff..."
ruff check .

echo "Type checking with mypy..."
mypy --package app

echo "All code quality checks passed!"