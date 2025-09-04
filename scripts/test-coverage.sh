#!/bin/bash

# Exit on any error
set -e

echo "Running tests with coverage..."

pytest --cov=app --cov-report=html --cov-report=term --cov-report=xml

echo "Test coverage report generated in htmlcov/"
echo "Coverage XML report generated in coverage.xml"