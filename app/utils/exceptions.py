from typing import Any, Dict, Optional


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationException(AppException):
    """Exception raised for authentication errors."""

    def __init__(
        self,
        message: str = "Authentication required",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "AUTHENTICATION_ERROR", details)


class AuthorizationException(AppException):
    """Exception raised for authorization errors."""

    def __init__(
        self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "AUTHORIZATION_ERROR", details)


class ValidationException(AppException):
    """Exception raised for validation errors."""

    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "VALIDATION_ERROR", details)


class NotFoundException(AppException):
    """Exception raised when a resource is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "NOT_FOUND", details)


class ConflictException(AppException):
    """Exception raised when there's a conflict."""

    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "CONFLICT", details)
