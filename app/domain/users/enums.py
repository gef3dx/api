from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""

    CLIENT = "client"
    EXECUTOR = "executor"
    ADMIN = "admin"
