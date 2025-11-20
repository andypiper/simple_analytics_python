"""Export API wrapper for Simple Analytics."""

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import SimpleAnalyticsClient


class ExportAPI:
    """
    Interface to the Simple Analytics Export API.

    The Export API allows you to export raw data points from your analytics.
    Access this through the main client: `client.export.datapoints(...)`.

    Example:
        >>> data = client.export.datapoints(
        ...     "example.com",
        ...     start="2024-01-01",
        ...     end="2024-01-31",
        ...     format="json"
        ... )
    """

    def __init__(self, client: "SimpleAnalyticsClient"):
        self._client = client

    def datapoints(
        self,
        hostname: str,
        start: str,
        end: str,
        format: str = "json",
        fields: list[str] | None = None,
        timezone: str | None = None,
        robots: bool = False,
        data_type: str = "pageviews",
    ) -> Any:
        """
        Export raw data points for a website.

        Args:
            hostname: The website domain (e.g., "example.com").
            start: Start date/time. Formats:
                - Date: "YYYY-MM-DD" (e.g., "2024-01-01")
                - Hourly: "YYYY-MM-DDTHH" (e.g., "2024-01-01T14")
            end: End date/time (same formats as start).
            format: Output format - "json" or "csv" (default: "json").
            fields: List of fields to include. Available fields:
                - added_iso, added_unix: Timestamps
                - hostname, path, query: URL components
                - is_unique: Whether visitor is unique
                - utm_source, utm_medium, utm_campaign, utm_content, utm_term
                - scrolled_percentage, duration_seconds
                - device_type, country_code
                - browser_name, browser_version
                - os_name, os_version
                - viewport_width, viewport_height
                - screen_width, screen_height
                - language, session_id
                - referrer_hostname, referrer_path
                - datapoint_id
            timezone: Timezone for date calculations (e.g., "Europe/Amsterdam").
            robots: Whether to include bot traffic (default: False).
            data_type: Type of data to export - "pageviews" or "events".

        Returns:
            If format is "json": List of data point dictionaries.
            If format is "csv": CSV string.

        Example:
            >>> # Export as JSON
            >>> data = client.export.datapoints(
            ...     "example.com",
            ...     start="2024-01-01",
            ...     end="2024-01-31",
            ...     fields=["added_iso", "path", "country_code", "device_type"]
            ... )
            >>> for point in data:
            ...     print(f"{point['added_iso']}: {point['path']}")
            >>>
            >>> # Export as CSV
            >>> csv_data = client.export.datapoints(
            ...     "example.com",
            ...     start="2024-01-01",
            ...     end="2024-01-01",
            ...     format="csv"
            ... )
            >>>
            >>> # Export hourly data
            >>> data = client.export.datapoints(
            ...     "example.com",
            ...     start="2024-01-01T00",
            ...     end="2024-01-01T23"
            ... )
        """
        endpoint = "/api/export/datapoints"

        params: dict[str, Any] = {
            "version": self._client.API_VERSION,
            "hostname": hostname,
            "start": start,
            "end": end,
            "format": format,
            "type": data_type,
            "robots": str(robots).lower(),
        }

        if fields:
            params["fields"] = ",".join(fields)
        if timezone:
            params["timezone"] = timezone

        return self._client.get(endpoint, params=params, require_auth=True)

    def pageviews(
        self,
        hostname: str,
        start: str,
        end: str,
        format: str = "json",
        fields: list[str] | None = None,
        timezone: str | None = None,
        robots: bool = False,
    ) -> Any:
        """
        Export pageview data points.

        This is a convenience method that calls datapoints with type="pageviews".

        Args:
            hostname: The website domain.
            start: Start date/time.
            end: End date/time.
            format: Output format - "json" or "csv".
            fields: List of fields to include.
            timezone: Timezone for date calculations.
            robots: Whether to include bot traffic.

        Returns:
            Exported pageview data.
        """
        return self.datapoints(
            hostname=hostname,
            start=start,
            end=end,
            format=format,
            fields=fields,
            timezone=timezone,
            robots=robots,
            data_type="pageviews",
        )

    def events(
        self,
        hostname: str,
        start: str,
        end: str,
        format: str = "json",
        fields: list[str] | None = None,
        timezone: str | None = None,
        robots: bool = False,
    ) -> Any:
        """
        Export event data points.

        This is a convenience method that calls datapoints with type="events".

        Args:
            hostname: The website domain.
            start: Start date/time.
            end: End date/time.
            format: Output format - "json" or "csv".
            fields: List of fields to include.
            timezone: Timezone for date calculations.
            robots: Whether to include bot traffic.

        Returns:
            Exported event data.
        """
        return self.datapoints(
            hostname=hostname,
            start=start,
            end=end,
            format=format,
            fields=fields,
            timezone=timezone,
            robots=robots,
            data_type="events",
        )

    def to_csv(
        self,
        hostname: str,
        start: str,
        end: str,
        fields: list[str] | None = None,
        timezone: str | None = None,
        robots: bool = False,
        data_type: str = "pageviews",
    ) -> str:
        """
        Export data points as CSV.

        This is a convenience method that exports in CSV format.

        Args:
            hostname: The website domain.
            start: Start date/time.
            end: End date/time.
            fields: List of fields to include.
            timezone: Timezone for date calculations.
            robots: Whether to include bot traffic.
            data_type: Type of data - "pageviews" or "events".

        Returns:
            CSV string.
        """
        return self.datapoints(
            hostname=hostname,
            start=start,
            end=end,
            format="csv",
            fields=fields,
            timezone=timezone,
            robots=robots,
            data_type=data_type,
        )
