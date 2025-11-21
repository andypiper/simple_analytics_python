"""Shared test fixtures for Simple Analytics tests."""

import pytest
from unittest.mock import Mock
import requests

from simple_analytics import SimpleAnalyticsClient


@pytest.fixture
def api_key():
    """Sample API key for testing."""
    return "sa_api_key_test123"


@pytest.fixture
def user_id():
    """Sample user ID for testing."""
    return "sa_user_id_test456"


@pytest.fixture
def client(api_key, user_id):
    """Create a client instance for testing."""
    client = SimpleAnalyticsClient(
        api_key=api_key,
        user_id=user_id,
        base_url="https://simpleanalytics.com",
        timeout=30
    )
    yield client
    client.close()


@pytest.fixture
def unauthenticated_client():
    """Create a client without authentication."""
    client = SimpleAnalyticsClient()
    yield client
    client.close()


@pytest.fixture
def mock_response():
    """Factory fixture for creating mock responses."""
    def _create_response(
        status_code=200,
        json_data=None,
        text="",
        content_type="application/json"
    ):
        response = Mock(spec=requests.Response)
        response.status_code = status_code
        response.headers = {"Content-Type": content_type}
        response.text = text

        if json_data is not None:
            response.json.return_value = json_data
        else:
            response.json.side_effect = ValueError("No JSON")

        return response

    return _create_response


# Sample response data fixtures
@pytest.fixture
def sample_stats_response():
    """Sample stats API response."""
    return {
        "pageviews": 1000,
        "visitors": 500,
        "histogram": [
            {"date": "2024-01-01", "pageviews": 100, "visitors": 50},
            {"date": "2024-01-02", "pageviews": 150, "visitors": 75},
        ],
        "pages": [
            {"value": "/", "pageviews": 500, "visitors": 250},
            {"value": "/about", "pageviews": 200, "visitors": 100},
        ]
    }


@pytest.fixture
def sample_websites_response():
    """Sample admin API websites response."""
    return [
        {
            "hostname": "example.com",
            "timezone": "UTC",
            "public": True,
            "label": "Main Site"
        },
        {
            "hostname": "blog.example.com",
            "timezone": "America/New_York",
            "public": False,
            "label": "Blog"
        }
    ]


@pytest.fixture
def sample_export_response():
    """Sample export API response."""
    return [
        {
            "added_iso": "2024-01-01T10:00:00Z",
            "path": "/",
            "country_code": "US",
            "device_type": "desktop"
        },
        {
            "added_iso": "2024-01-01T11:00:00Z",
            "path": "/about",
            "country_code": "GB",
            "device_type": "mobile"
        }
    ]
