"""Admin API wrapper for Simple Analytics."""

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import SimpleAnalyticsClient


class AdminAPI:
    """
    Interface to the Simple Analytics Admin API.

    The Admin API allows you to manage your websites and account settings.
    Access this through the main client: `client.admin.list_websites()`.

    Note: Some operations require a Business or Enterprise plan.

    Example:
        >>> websites = client.admin.list_websites()
        >>> for site in websites:
        ...     print(site["hostname"])
    """

    def __init__(self, client: "SimpleAnalyticsClient"):
        self._client = client

    def list_websites(self) -> list[dict[str, Any]]:
        """
        List all websites in your account.

        Returns:
            List of website dictionaries containing hostname, timezone,
            public status, and other configuration.

        Example:
            >>> websites = client.admin.list_websites()
            >>> for site in websites:
            ...     print(f"{site['hostname']} ({site['timezone']})")
        """
        endpoint = "/api/websites"
        return self._client.get(endpoint, require_auth=True)

    def add_website(
        self,
        hostname: str,
        timezone: str = "UTC",
        public: bool = False,
        label: str | None = None,
    ) -> dict[str, Any]:
        """
        Add a new website to your account.

        Note: This endpoint requires a Business or Enterprise plan.

        Args:
            hostname: The website domain (e.g., "example.com").
            timezone: Timezone for the website (default: "UTC").
            public: Whether the stats should be publicly viewable.
            label: Optional label for the website.

        Returns:
            Dictionary containing the created website information.

        Example:
            >>> site = client.admin.add_website(
            ...     "newsite.com",
            ...     timezone="America/New_York",
            ...     public=False,
            ...     label="New Project"
            ... )
            >>> print(f"Added: {site['hostname']}")
        """
        endpoint = "/api/websites/add"

        data: dict[str, Any] = {
            "hostname": hostname,
            "timezone": timezone,
            "public": public,
        }

        if label:
            data["label"] = label

        return self._client.post(endpoint, json=data, require_auth=True)

    def get_website(self, hostname: str) -> dict[str, Any] | None:
        """
        Get information about a specific website.

        This is a convenience method that filters list_websites().

        Args:
            hostname: The website domain to find.

        Returns:
            Website dictionary if found, None otherwise.

        Example:
            >>> site = client.admin.get_website("example.com")
            >>> if site:
            ...     print(f"Timezone: {site['timezone']}")
        """
        websites = self.list_websites()
        for site in websites:
            if site.get("hostname") == hostname:
                return site
        return None
