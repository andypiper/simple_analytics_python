"""Main client class for the Simple Analytics API."""

import requests
from typing import Any

from .exceptions import (
    SimpleAnalyticsError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    ServerError,
    NetworkError,
)

# Version is defined here to avoid circular import
__version__ = "0.1.0"


class SimpleAnalyticsClient:
    """
    Client for interacting with the Simple Analytics API.

    This client provides access to the Stats API, Export API, and Admin API.

    Args:
        api_key: Your Simple Analytics API key (starts with 'sa_api_key_').
        user_id: Your Simple Analytics user ID (starts with 'sa_user_id_').
        base_url: Base URL for the API (default: https://simpleanalytics.com).
        timeout: Request timeout in seconds (default: 30).
        user_agent: Custom User-Agent header (default: sa-python-api/{version}).

    Example:
        >>> from simple_analytics import SimpleAnalyticsClient
        >>> client = SimpleAnalyticsClient(
        ...     api_key="sa_api_key_xxxx",
        ...     user_id="sa_user_id_xxxx"
        ... )
        >>> stats = client.stats.get("example.com")
    """

    DEFAULT_BASE_URL = "https://simpleanalytics.com"
    API_VERSION = 5
    DEFAULT_USER_AGENT = f"sa-python-api/{__version__}"

    def __init__(
        self,
        api_key: str | None = None,
        user_id: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 30,
        user_agent: str | None = None,
    ):
        self.api_key = api_key
        self.user_id = user_id
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.user_agent = user_agent or self.DEFAULT_USER_AGENT
        self._session = requests.Session()

        # Import here to avoid circular imports
        from .stats import StatsAPI
        from .export import ExportAPI
        from .admin import AdminAPI

        self.stats = StatsAPI(self)
        self.export = ExportAPI(self)
        self.admin = AdminAPI(self)

    def _get_headers(self, require_auth: bool = False) -> dict[str, str]:
        """Get request headers with optional authentication."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }

        if self.api_key:
            headers["Api-Key"] = self.api_key
        elif require_auth:
            raise AuthenticationError("API key is required for this operation")

        if self.user_id:
            headers["User-Id"] = self.user_id
        elif require_auth:
            raise AuthenticationError("User ID is required for this operation")

        return headers

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response and raise appropriate exceptions."""
        if response.status_code == 200:
            # Check content type
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return response.json()
            elif "text/csv" in content_type:
                return response.text
            else:
                return response.text

        # Handle error responses
        error_data: dict | None = None
        try:
            error_data = response.json()
            message = error_data.get("error", error_data.get("message", "Unknown error"))
        except (ValueError, requests.exceptions.JSONDecodeError):
            message = response.text or f"HTTP {response.status_code}"

        if response.status_code == 401:
            raise AuthenticationError(message, response.status_code, error_data)
        elif response.status_code == 403:
            raise AuthenticationError(message, response.status_code, error_data)
        elif response.status_code == 404:
            raise NotFoundError(message, response.status_code, error_data)
        elif response.status_code == 422:
            raise ValidationError(message, response.status_code, error_data)
        elif response.status_code == 429:
            raise RateLimitError(message, response.status_code, error_data)
        elif response.status_code >= 500:
            raise ServerError(message, response.status_code, error_data)
        else:
            raise SimpleAnalyticsError(message, response.status_code, error_data)

    def request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        json: dict | None = None,
        require_auth: bool = False,
    ) -> Any:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint path.
            params: Query parameters.
            json: JSON body data.
            require_auth: Whether authentication is required.

        Returns:
            Parsed response data.
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(require_auth)

        try:
            response = self._session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json,
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"Request timed out: {e}") from e
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {e}") from e
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Request failed: {e}") from e

        return self._handle_response(response)

    def get(self, endpoint: str, params: dict | None = None, require_auth: bool = False) -> Any:
        """Make a GET request."""
        return self.request("GET", endpoint, params=params, require_auth=require_auth)

    def post(self, endpoint: str, json: dict | None = None, require_auth: bool = False) -> Any:
        """Make a POST request."""
        return self.request("POST", endpoint, json=json, require_auth=require_auth)

    def close(self):
        """Close the HTTP session."""
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
