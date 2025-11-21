"""
Simple Analytics Python API Client.

A Python wrapper for the Simple Analytics API providing easy access to
Stats, Export, and Admin functionality.

Example:
    >>> from simple_analytics import SimpleAnalyticsClient
    >>>
    >>> # Initialize the client
    >>> client = SimpleAnalyticsClient(
    ...     api_key="sa_api_key_xxxx",
    ...     user_id="sa_user_id_xxxx"
    ... )
    >>>
    >>> # Get website statistics
    >>> stats = client.stats.get("example.com")
    >>> print(f"Pageviews: {stats.get('pageviews')}")
    >>>
    >>> # Export data points
    >>> data = client.export.datapoints(
    ...     "example.com",
    ...     start="2024-01-01",
    ...     end="2024-01-31"
    ... )
    >>>
    >>> # List websites
    >>> websites = client.admin.list_websites()
"""

from .client import SimpleAnalyticsClient
from .exceptions import (
    SimpleAnalyticsError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    ServerError,
    NetworkError,
)
from .stats import StatsAPI
from .export import ExportAPI
from .admin import AdminAPI

__version__ = "0.1.0"
__author__ = "Simple Analytics Python Client Contributors"

__all__ = [
    # Main client
    "SimpleAnalyticsClient",
    # API classes
    "StatsAPI",
    "ExportAPI",
    "AdminAPI",
    # Exceptions
    "SimpleAnalyticsError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
    "ServerError",
    "NetworkError",
]
