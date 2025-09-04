#!/bin/bash

# Exit on any error
set -e

echo "Initializing development environment..."

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
fi

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e ".[dev]"

echo "Setting up environment variables..."
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your configuration"
fi

echo "Running database migrations..."
alembic upgrade head

echo "Development environment setup complete!"
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo "To start the development server, run:"
echo "  uvicorn app.main:app --reload"