#!/bin/bash

# Exit on any error
set -e

echo "Verifying project setup..."

# Check if we're in the project directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found. Please run this script from the project root directory."
    exit 1
fi

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Warning: Virtual environment not activated. Consider activating it with:"
    echo "  source venv/bin/activate"
fi

# Check if required files exist
required_files=(
    "requirements.txt"
    "requirements-dev.txt"
    "pyproject.toml"
    "setup.py"
    "setup.cfg"
    "README.md"
    ".gitignore"
    "Dockerfile"
    "docker-compose.yml"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "Error: Required file $file not found."
        exit 1
    fi
done

# Check if required directories exist
required_dirs=(
    "app"
    "tests"
    "alembic"
    ".github/workflows"
    "scripts"
    "docs"
)

for dir in "${required_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "Error: Required directory $dir not found."
        exit 1
    fi
done

# Check if required workflow files exist
required_workflows=(
    ".github/workflows/ci.yml"
    ".github/workflows/deploy.yml"
)

for workflow in "${required_workflows[@]}"; do
    if [ ! -f "$workflow" ]; then
        echo "Error: Required workflow file $workflow not found."
        exit 1
    fi
done

# Check if required scripts exist and are executable
required_scripts=(
    "scripts/init-dev.sh"
    "scripts/code-quality.sh"
    "scripts/test-coverage.sh"
    "scripts/verify-setup.sh"
)

for script in "${required_scripts[@]}"; do
    if [ ! -f "$script" ]; then
        echo "Error: Required script $script not found."
        exit 1
    fi
    
    if [ ! -x "$script" ]; then
        echo "Error: Script $script is not executable."
        exit 1
    fi
done

echo "All required files and directories are present."
echo "Setup verification completed successfully!"