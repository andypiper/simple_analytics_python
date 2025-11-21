"""Tests for custom exceptions."""

import pytest

from simple_analytics.exceptions import (
    SimpleAnalyticsError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    ServerError,
)


class TestSimpleAnalyticsError:
    """Tests for the base exception class."""

    def test_init_with_message_only(self):
        """Test exception with message only."""
        exc = SimpleAnalyticsError("Something went wrong")

        assert exc.message == "Something went wrong"
        assert exc.status_code is None
        assert exc.response is None
        assert str(exc) == "Something went wrong"

    def test_init_with_all_attributes(self):
        """Test exception with all attributes."""
        response = {"error": "details"}
        exc = SimpleAnalyticsError("Error", status_code=400, response=response)

        assert exc.message == "Error"
        assert exc.status_code == 400
        assert exc.response == response

    def test_exception_inheritance(self):
        """Test SimpleAnalyticsError inherits from Exception."""
        exc = SimpleAnalyticsError("test")

        assert isinstance(exc, Exception)


class TestAuthenticationError:
    """Tests for AuthenticationError."""

    def test_inheritance(self):
        """Test AuthenticationError inherits from SimpleAnalyticsError."""
        exc = AuthenticationError("Invalid credentials", 401)

        assert isinstance(exc, SimpleAnalyticsError)
        assert isinstance(exc, Exception)

    def test_attributes(self):
        """Test AuthenticationError preserves attributes."""
        exc = AuthenticationError("Invalid API key", 401)

        assert exc.message == "Invalid API key"
        assert exc.status_code == 401


class TestRateLimitError:
    """Tests for RateLimitError."""

    def test_inheritance(self):
        """Test RateLimitError inherits from SimpleAnalyticsError."""
        exc = RateLimitError("Rate limit exceeded", 429)

        assert isinstance(exc, SimpleAnalyticsError)

    def test_attributes(self):
        """Test RateLimitError preserves attributes."""
        exc = RateLimitError("Too many requests", 429)

        assert exc.status_code == 429


class TestNotFoundError:
    """Tests for NotFoundError."""

    def test_inheritance(self):
        """Test NotFoundError inherits from SimpleAnalyticsError."""
        exc = NotFoundError("Website not found", 404)

        assert isinstance(exc, SimpleAnalyticsError)


class TestValidationError:
    """Tests for ValidationError."""

    def test_inheritance(self):
        """Test ValidationError inherits from SimpleAnalyticsError."""
        exc = ValidationError("Invalid date format", 422)

        assert isinstance(exc, SimpleAnalyticsError)


class TestServerError:
    """Tests for ServerError."""

    def test_inheritance(self):
        """Test ServerError inherits from SimpleAnalyticsError."""
        exc = ServerError("Internal server error", 500)

        assert isinstance(exc, SimpleAnalyticsError)

    def test_various_5xx_codes(self):
        """Test ServerError with various 5xx status codes."""
        for code in [500, 502, 503, 504]:
            exc = ServerError(f"Server error {code}", code)
            assert exc.status_code == code


class TestExceptionRaising:
    """Tests for exception raising and catching."""

    def test_catch_specific_exception(self):
        """Test catching specific exception type."""
        with pytest.raises(AuthenticationError):
            raise AuthenticationError("test", 401)

    def test_catch_base_exception(self):
        """Test catching base exception catches all."""
        with pytest.raises(SimpleAnalyticsError):
            raise RateLimitError("test", 429)

    def test_exception_message_in_str(self):
        """Test exception message appears in string representation."""
        exc = ValidationError("Invalid field: foo", 422)

        assert "Invalid field: foo" in str(exc)
