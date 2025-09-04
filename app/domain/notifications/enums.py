from enum import Enum


class NotificationStatus(str, Enum):
    """Notification status enumeration."""

    UNREAD = "unread"
    READ = "read"


class NotificationType(str, Enum):
    """Notification type enumeration."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
