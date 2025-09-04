# Redis and Celery Integration

This document describes the Redis and Celery integration added to the notifications and messages systems.

## Features Implemented

1. **Redis Pub/Sub for Distributed Notifications**
   - Real-time notification distribution across multiple instances
   - User-specific channels for targeted messaging
   - Listener support for real-time processing

2. **Celery/RQ for Asynchronous Processing**
   - Background task processing for notifications and messages
   - Priority-based task queues
   - Retry mechanisms for failed tasks

3. **Rate Limiting**
   - Per-endpoint rate limiting using Redis
   - Configurable limits and windows
   - Automatic retry-after headers

4. **Priority-Based Notifications**
   - Four priority levels: low, normal, high, urgent
   - Immediate processing for high-priority notifications
   - Queued processing for normal/low priority

5. **Message Templates**
   - Predefined templates for common message types
   - Jinja2-based templating system
   - Context-aware rendering

## Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌────────────────┐
│   API Layer     │    │  Redis Pub/  │    │   Listeners    │
│ (FastAPI)       │───▶│  Sub Broker  │───▶│ (Real-time)    │
└─────────────────┘    └──────────────┘    └────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌──────────────┐    ┌────────────────┐
│  Service Layer  │    │   Celery     │    │   Workers      │
│ (Business Logic)│───▶│  Task Queue  │───▶│ (Background)   │
└─────────────────┘    └──────────────┘    └────────────────┘
```

## Usage Examples

### Sending a Priority Notification

```python
from app.domain.notifications.schemas import NotificationCreate
from app.domain.notifications.enums import NotificationPriority

notification_data = NotificationCreate(
    user_id=user_id,
    title="Important Update",
    message="Please review the new terms of service.",
    priority=NotificationPriority.HIGH  # Will be processed immediately
)
```

### Using Message Templates

```python
from app.domain.messages.templates import MessageTemplateType

# In your API endpoint
message_request = MessageSendRequest(
    recipient_id=recipient_id,
    subject="Welcome!",
    content="Welcome to our platform!"
)

# With template
template_type = MessageTemplateType.WELCOME
# The router will automatically render the template with context
```

### Rate Limiting

Rate limiting is automatically applied to endpoints:
- Notifications: 5 requests per minute
- Messages: 10 requests per minute

## Running the System

1. **Start Redis Server**
   ```bash
   redis-server
   ```

2. **Start Celery Workers**
   ```bash
   ./scripts/start_workers.sh
   ```

3. **Start the Main Application**
   ```bash
   uvicorn app.main:app --reload
   ```

## Configuration

Redis configuration is managed through environment variables:
- `REDIS_HOST` (default: localhost)
- `REDIS_PORT` (default: 6379)
- `REDIS_DB` (default: 0)
- `REDIS_PASSWORD` (default: None)

## Examples

See the `examples/` directory for:
- `notification_listener.py`: Example of listening for notifications
- `send_notification.py`: Example of sending notifications with new features