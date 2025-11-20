"""Stats API wrapper for Simple Analytics."""

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import SimpleAnalyticsClient


class StatsAPI:
    """
    Interface to the Simple Analytics Stats API.

    The Stats API provides aggregated analytics data for your websites.
    Access this through the main client: `client.stats.get(...)`.

    Example:
        >>> stats = client.stats.get("example.com", fields=["pageviews", "visitors"])
        >>> print(stats["pageviews"])
    """

    def __init__(self, client: "SimpleAnalyticsClient"):
        self._client = client

    def get(
        self,
        hostname: str,
        path: str | None = None,
        start: str | None = None,
        end: str | None = None,
        timezone: str | None = None,
        fields: list[str] | None = None,
        limit: int | None = None,
        info: bool = True,
        interval: str | None = None,
        events: str | list[str] | None = None,
        filters: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Get aggregated statistics for a website.

        Args:
            hostname: The website domain (e.g., "example.com").
            path: Optional specific page path (e.g., "/about").
            start: Start date in YYYY-MM-DD format (default: 1 month ago).
            end: End date in YYYY-MM-DD format (default: today).
            timezone: Timezone for date calculations (e.g., "Europe/Amsterdam").
            fields: List of fields to retrieve. Options include:
                - pageviews, visitors: Aggregated counts
                - histogram: Daily pageviews and visitors array
                - pages, countries, referrers: Breakdown lists
                - utm_sources, utm_mediums, utm_campaigns, utm_contents, utm_terms
                - browser_names, os_names, device_types
                - seconds_on_page: Median time spent on page
            limit: Maximum number of results (1-1000).
            info: Whether to include field metadata (default: True).
            interval: Histogram granularity: hour, day, week, month, or year.
            events: Event names to retrieve, or "*" for all events (max 1000).
            filters: Dictionary of filter parameters. Available filters:
                - page, pages, country, referrer
                - utm_source, utm_medium, utm_campaign, utm_content, utm_term
                - browser_name, os_name, device_type
                Filters support wildcards with "*" (e.g., "/blog*").

        Returns:
            Dictionary containing requested statistics data.

        Example:
            >>> # Get basic stats
            >>> stats = client.stats.get("example.com")
            >>>
            >>> # Get specific fields with filters
            >>> stats = client.stats.get(
            ...     "example.com",
            ...     start="2024-01-01",
            ...     end="2024-01-31",
            ...     fields=["pageviews", "visitors", "pages", "referrers"],
            ...     filters={"country": "US"},
            ...     limit=50
            ... )
            >>>
            >>> # Get page-specific stats
            >>> stats = client.stats.get("example.com", path="/pricing")
            >>>
            >>> # Get events
            >>> stats = client.stats.get("example.com", events=["signup", "purchase"])
        """
        # Build endpoint
        if path:
            path = path.lstrip("/")
            endpoint = f"/{hostname}/{path}.json"
        else:
            endpoint = f"/{hostname}.json"

        # Build parameters
        params: dict[str, Any] = {
            "version": self._client.API_VERSION,
            "info": str(info).lower(),
        }

        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if timezone:
            params["timezone"] = timezone
        if limit:
            params["limit"] = limit
        if interval:
            params["interval"] = interval

        if fields:
            params["fields"] = ",".join(fields)

        if events:
            if isinstance(events, list):
                params["events"] = ",".join(events)
            else:
                params["events"] = events

        # Add filters
        if filters:
            for key, value in filters.items():
                params[key] = value

        # Determine if auth is required (non-public websites need it)
        require_auth = bool(self._client.api_key)

        return self._client.get(endpoint, params=params, require_auth=False)

    def get_events(
        self,
        hostname: str,
        events: str | list[str] = "*",
        start: str | None = None,
        end: str | None = None,
        timezone: str | None = None,
    ) -> dict[str, Any]:
        """
        Get event statistics for a website.

        This is a convenience method for retrieving event data.

        Args:
            hostname: The website domain.
            events: Event names to retrieve, or "*" for all events (default).
            start: Start date in YYYY-MM-DD format.
            end: End date in YYYY-MM-DD format.
            timezone: Timezone for date calculations.

        Returns:
            Dictionary containing event statistics.

        Example:
            >>> events = client.stats.get_events("example.com")
            >>> for event in events.get("events", []):
            ...     print(f"{event['name']}: {event['total']}")
        """
        return self.get(
            hostname,
            start=start,
            end=end,
            timezone=timezone,
            events=events,
        )

    def get_histogram(
        self,
        hostname: str,
        start: str | None = None,
        end: str | None = None,
        interval: str = "day",
        timezone: str | None = None,
    ) -> dict[str, Any]:
        """
        Get histogram data for a website.

        This is a convenience method for retrieving time-series data.

        Args:
            hostname: The website domain.
            start: Start date in YYYY-MM-DD format.
            end: End date in YYYY-MM-DD format.
            interval: Granularity: hour, day, week, month, or year (default: day).
            timezone: Timezone for date calculations.

        Returns:
            Dictionary containing histogram data.

        Example:
            >>> data = client.stats.get_histogram("example.com", interval="week")
            >>> for point in data.get("histogram", []):
            ...     print(f"{point['date']}: {point['pageviews']} pageviews")
        """
        return self.get(
            hostname,
            start=start,
            end=end,
            timezone=timezone,
            fields=["histogram"],
            interval=interval,
        )
