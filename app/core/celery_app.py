from celery import Celery

from app.core.config import settings

# Create Celery app instance
celery_app = Celery("notification_app")

# Configure Celery
celery_app.conf.update(
    broker_url=f"redis://{settings.REDIS_HOST or 'localhost'}:{settings.REDIS_PORT or 6379}/{settings.REDIS_DB or 0}",
    result_backend=f"redis://{settings.REDIS_HOST or 'localhost'}:{settings.REDIS_PORT or 6379}/{settings.REDIS_DB or 0}",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "app.tasks.notification_tasks.send_notification": {"queue": "notifications"},
        "app.tasks.message_tasks.send_message": {"queue": "messages"},
    },
)


# Auto-discover tasks
celery_app.autodiscover_tasks(
    [
        "app.tasks",
    ]
)


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery setup."""
    print(f"Request: {self.request!r}")
