"""Custom exceptions for the application."""
from fastapi import status


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class FileParsingError(AppException):
    """Raised when file parsing fails."""

    def __init__(self, message: str):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class UnsupportedFileTypeError(AppException):
    """Raised when file type is not supported."""

    def __init__(self, content_type: str):
        super().__init__(
            f"Unsupported media type: {content_type}",
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )


class FileSizeExceededError(AppException):
    """Raised when file size exceeds limit."""

    def __init__(self, size_mb: int, max_size_mb: int):
        super().__init__(
            f"File size ({size_mb}MB) exceeds maximum allowed ({max_size_mb}MB)",
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        )


class BedrockInvocationError(AppException):
    """Raised when Bedrock API call fails."""

    def __init__(self, message: str, original_error: Exception | None = None):
        self.original_error = original_error
        super().__init__(f"Bedrock invocation failed: {message}", status.HTTP_502_BAD_GATEWAY)


class BedrockThrottlingError(AppException):
    """Raised when Bedrock API is throttling requests."""

    def __init__(self, message: str = "Request throttled by Bedrock. Please retry later."):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS)


class ValidationError(AppException):
    """Raised when validation fails."""

    def __init__(self, message: str):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)
