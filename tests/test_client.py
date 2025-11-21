"""Tests for the SimpleAnalyticsClient class."""

import pytest
from unittest.mock import Mock, patch
import requests

from simple_analytics import SimpleAnalyticsClient
from simple_analytics.exceptions import (
    SimpleAnalyticsError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    ServerError,
)


class TestClientInitialization:
    """Tests for client initialization."""

    def test_init_with_credentials(self, api_key, user_id):
        """Test client initializes with API key and user ID."""
        client = SimpleAnalyticsClient(api_key=api_key, user_id=user_id)

        assert client.api_key == api_key
        assert client.user_id == user_id
        assert client.base_url == "https://simpleanalytics.com"
        assert client.timeout == 30

    def test_init_without_credentials(self):
        """Test client initializes without credentials."""
        client = SimpleAnalyticsClient()

        assert client.api_key is None
        assert client.user_id is None

    def test_init_custom_base_url(self):
        """Test client accepts custom base URL."""
        client = SimpleAnalyticsClient(base_url="https://custom.api.com/")

        # Should strip trailing slash
        assert client.base_url == "https://custom.api.com"

    def test_init_custom_timeout(self):
        """Test client accepts custom timeout."""
        client = SimpleAnalyticsClient(timeout=60)

        assert client.timeout == 60

    def test_init_creates_session(self):
        """Test client creates requests session."""
        client = SimpleAnalyticsClient()

        assert hasattr(client, '_session')
        assert isinstance(client._session, requests.Session)

    def test_init_creates_api_instances(self, client):
        """Test client creates Stats, Export, and Admin API instances."""
        from simple_analytics.stats import StatsAPI
        from simple_analytics.export import ExportAPI
        from simple_analytics.admin import AdminAPI

        assert isinstance(client.stats, StatsAPI)
        assert isinstance(client.export, ExportAPI)
        assert isinstance(client.admin, AdminAPI)


class TestGetHeaders:
    """Tests for header generation."""

    def test_headers_without_auth(self):
        """Test headers when no auth is required."""
        client = SimpleAnalyticsClient()
        headers = client._get_headers(require_auth=False)

        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
        assert "Api-Key" not in headers
        assert "User-Id" not in headers

    def test_headers_with_credentials(self, api_key, user_id):
        """Test headers include credentials when provided."""
        client = SimpleAnalyticsClient(api_key=api_key, user_id=user_id)
        headers = client._get_headers(require_auth=False)

        assert headers["Api-Key"] == api_key
        assert headers["User-Id"] == user_id

    def test_headers_require_auth_without_api_key(self):
        """Test raises error when auth required but no API key."""
        client = SimpleAnalyticsClient(user_id="sa_user_id_test")

        with pytest.raises(AuthenticationError) as exc_info:
            client._get_headers(require_auth=True)

        assert "API key is required" in str(exc_info.value)

    def test_headers_require_auth_without_user_id(self):
        """Test raises error when auth required but no user ID."""
        client = SimpleAnalyticsClient(api_key="sa_api_key_test")

        with pytest.raises(AuthenticationError) as exc_info:
            client._get_headers(require_auth=True)

        assert "User ID is required" in str(exc_info.value)

    def test_headers_require_auth_with_both_credentials(self, api_key, user_id):
        """Test no error when auth required and both credentials present."""
        client = SimpleAnalyticsClient(api_key=api_key, user_id=user_id)
        headers = client._get_headers(require_auth=True)

        assert headers["Api-Key"] == api_key
        assert headers["User-Id"] == user_id


class TestHandleResponse:
    """Tests for response handling."""

    def test_handle_json_response(self, client, mock_response):
        """Test handling successful JSON response."""
        response = mock_response(
            status_code=200,
            json_data={"key": "value"},
            content_type="application/json"
        )

        result = client._handle_response(response)

        assert result == {"key": "value"}

    def test_handle_csv_response(self, client, mock_response):
        """Test handling successful CSV response."""
        csv_data = "date,pageviews\n2024-01-01,100"
        response = mock_response(
            status_code=200,
            text=csv_data,
            content_type="text/csv"
        )

        result = client._handle_response(response)

        assert result == csv_data

    def test_handle_text_response(self, client, mock_response):
        """Test handling successful text response."""
        response = mock_response(
            status_code=200,
            text="plain text",
            content_type="text/plain"
        )

        result = client._handle_response(response)

        assert result == "plain text"

    def test_handle_401_error(self, client, mock_response):
        """Test handling 401 authentication error."""
        response = mock_response(
            status_code=401,
            json_data={"error": "Invalid API key"}
        )

        with pytest.raises(AuthenticationError) as exc_info:
            client._handle_response(response)

        assert exc_info.value.status_code == 401
        assert "Invalid API key" in str(exc_info.value)

    def test_handle_403_error(self, client, mock_response):
        """Test handling 403 forbidden error."""
        response = mock_response(
            status_code=403,
            json_data={"error": "Access denied"}
        )

        with pytest.raises(AuthenticationError) as exc_info:
            client._handle_response(response)

        assert exc_info.value.status_code == 403

    def test_handle_404_error(self, client, mock_response):
        """Test handling 404 not found error."""
        response = mock_response(
            status_code=404,
            json_data={"error": "Website not found"}
        )

        with pytest.raises(NotFoundError) as exc_info:
            client._handle_response(response)

        assert exc_info.value.status_code == 404

    def test_handle_422_error(self, client, mock_response):
        """Test handling 422 validation error."""
        response = mock_response(
            status_code=422,
            json_data={"error": "Invalid date format"}
        )

        with pytest.raises(ValidationError) as exc_info:
            client._handle_response(response)

        assert exc_info.value.status_code == 422

    def test_handle_429_error(self, client, mock_response):
        """Test handling 429 rate limit error."""
        response = mock_response(
            status_code=429,
            json_data={"error": "Rate limit exceeded"}
        )

        with pytest.raises(RateLimitError) as exc_info:
            client._handle_response(response)

        assert exc_info.value.status_code == 429

    def test_handle_500_error(self, client, mock_response):
        """Test handling 500 server error."""
        response = mock_response(
            status_code=500,
            json_data={"error": "Internal server error"}
        )

        with pytest.raises(ServerError) as exc_info:
            client._handle_response(response)

        assert exc_info.value.status_code == 500

    def test_handle_502_error(self, client, mock_response):
        """Test handling 502 bad gateway error."""
        response = mock_response(
            status_code=502,
            text="Bad Gateway"
        )

        with pytest.raises(ServerError) as exc_info:
            client._handle_response(response)

        assert exc_info.value.status_code == 502

    def test_handle_unknown_error(self, client, mock_response):
        """Test handling unknown error status."""
        response = mock_response(
            status_code=418,
            json_data={"error": "I'm a teapot"}
        )

        with pytest.raises(SimpleAnalyticsError) as exc_info:
            client._handle_response(response)

        assert exc_info.value.status_code == 418

    def test_handle_error_with_message_field(self, client, mock_response):
        """Test error response with 'message' instead of 'error' field."""
        response = mock_response(
            status_code=400,
            json_data={"message": "Bad request"}
        )

        with pytest.raises(SimpleAnalyticsError) as exc_info:
            client._handle_response(response)

        assert "Bad request" in str(exc_info.value)

    def test_handle_error_non_json_response(self, client, mock_response):
        """Test error response that isn't JSON."""
        response = mock_response(
            status_code=500,
            text="Internal Server Error"
        )
        response.json.side_effect = ValueError("Not JSON")

        with pytest.raises(ServerError) as exc_info:
            client._handle_response(response)

        assert "Internal Server Error" in str(exc_info.value)


class TestRequest:
    """Tests for the request method."""

    def test_request_get(self, api_key, user_id):
        """Test making a GET request."""
        with patch('requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"Content-Type": "application/json"}
            mock_response.json.return_value = {"data": "test"}
            mock_session.request.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = SimpleAnalyticsClient(api_key=api_key, user_id=user_id)
            result = client.request("GET", "/test", params={"key": "value"})

            mock_session.request.assert_called_once()
            call_kwargs = mock_session.request.call_args
            assert call_kwargs[1]["method"] == "GET"
            assert call_kwargs[1]["url"] == "https://simpleanalytics.com/test"
            assert call_kwargs[1]["params"] == {"key": "value"}
            assert result == {"data": "test"}

    def test_request_post(self, api_key, user_id):
        """Test making a POST request."""
        with patch('requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"Content-Type": "application/json"}
            mock_response.json.return_value = {"created": True}
            mock_session.request.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = SimpleAnalyticsClient(api_key=api_key, user_id=user_id)
            result = client.request("POST", "/test", json={"name": "test"})

            call_kwargs = mock_session.request.call_args
            assert call_kwargs[1]["method"] == "POST"
            assert call_kwargs[1]["json"] == {"name": "test"}

    def test_request_timeout(self, api_key, user_id):
        """Test request uses configured timeout."""
        with patch('requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"Content-Type": "application/json"}
            mock_response.json.return_value = {}
            mock_session.request.return_value = mock_response
            mock_session_class.return_value = mock_session

            client = SimpleAnalyticsClient(
                api_key=api_key,
                user_id=user_id,
                timeout=60
            )
            client.request("GET", "/test")

            call_kwargs = mock_session.request.call_args
            assert call_kwargs[1]["timeout"] == 60


class TestConvenienceMethods:
    """Tests for get() and post() convenience methods."""

    def test_get_method(self, client):
        """Test get() calls request with GET method."""
        with patch.object(client, 'request') as mock_request:
            mock_request.return_value = {"data": "test"}

            result = client.get("/endpoint", params={"key": "value"})

            mock_request.assert_called_once_with(
                "GET",
                "/endpoint",
                params={"key": "value"},
                require_auth=False
            )
            assert result == {"data": "test"}

    def test_post_method(self, client):
        """Test post() calls request with POST method."""
        with patch.object(client, 'request') as mock_request:
            mock_request.return_value = {"created": True}

            result = client.post("/endpoint", json={"name": "test"})

            mock_request.assert_called_once_with(
                "POST",
                "/endpoint",
                json={"name": "test"},
                require_auth=False
            )


class TestContextManager:
    """Tests for context manager support."""

    def test_context_manager_enter(self, api_key, user_id):
        """Test __enter__ returns client."""
        client = SimpleAnalyticsClient(api_key=api_key, user_id=user_id)

        result = client.__enter__()

        assert result is client

    def test_context_manager_exit_closes_session(self, api_key, user_id):
        """Test __exit__ closes session."""
        with patch('requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session

            client = SimpleAnalyticsClient(api_key=api_key, user_id=user_id)
            client.__exit__(None, None, None)

            mock_session.close.assert_called_once()

    def test_with_statement(self, api_key, user_id):
        """Test using client with 'with' statement."""
        with patch('requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session

            with SimpleAnalyticsClient(api_key=api_key, user_id=user_id) as client:
                assert client.api_key == api_key

            mock_session.close.assert_called_once()

    def test_close_method(self, api_key, user_id):
        """Test close() method closes session."""
        with patch('requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session

            client = SimpleAnalyticsClient(api_key=api_key, user_id=user_id)
            client.close()

            mock_session.close.assert_called_once()
