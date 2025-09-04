#!/bin/bash

# Start Celery workers for notifications and messages

# Exit on any error
set -e

echo "Starting Celery workers..."

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Start notification worker
echo "Starting notification worker..."
celery -A app.core.celery_app worker --loglevel=info --queues=notifications &

# Start message worker
echo "Starting message worker..."
celery -A app.core.celery_app worker --loglevel=info --queues=messages &

# Start Celery beat for scheduled tasks (optional)
# echo "Starting Celery beat..."
# celery -A app.core.celery_app beat --loglevel=info &

echo "All workers started!"
echo "Press Ctrl+C to stop workers"

# Wait for background processes
wait