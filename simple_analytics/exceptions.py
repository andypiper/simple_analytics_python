"""Custom exceptions for the Simple Analytics API client."""


class SimpleAnalyticsError(Exception):
    """Base exception for Simple Analytics API errors."""

    def __init__(self, message: str, status_code: int | None = None, response: dict | None = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class AuthenticationError(SimpleAnalyticsError):
    """Raised when authentication fails."""

    pass


class RateLimitError(SimpleAnalyticsError):
    """Raised when API rate limit is exceeded."""

    pass


class NotFoundError(SimpleAnalyticsError):
    """Raised when a requested resource is not found."""

    pass


class ValidationError(SimpleAnalyticsError):
    """Raised when request parameters are invalid."""

    pass


class ServerError(SimpleAnalyticsError):
    """Raised when the server returns a 5xx error."""

    pass


class NetworkError(SimpleAnalyticsError):
    """Raised when a network error occurs (timeout, connection error, etc.)."""

    pass
