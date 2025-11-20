"""Type definitions for the Simple Analytics API client."""

from typing import Literal, TypedDict

# API field types
StatsField = Literal[
    "pageviews",
    "visitors",
    "histogram",
    "pages",
    "countries",
    "referrers",
    "utm_sources",
    "utm_mediums",
    "utm_campaigns",
    "utm_contents",
    "utm_terms",
    "browser_names",
    "os_names",
    "device_types",
    "seconds_on_page",
]

ExportField = Literal[
    "added_iso",
    "added_unix",
    "hostname",
    "path",
    "query",
    "is_unique",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_content",
    "utm_term",
    "scrolled_percentage",
    "duration_seconds",
    "device_type",
    "country_code",
    "browser_name",
    "browser_version",
    "os_name",
    "os_version",
    "viewport_width",
    "viewport_height",
    "screen_width",
    "screen_height",
    "language",
    "session_id",
    "referrer_hostname",
    "referrer_path",
    "datapoint_id",
]

FilterField = Literal[
    "page",
    "pages",
    "country",
    "referrer",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_content",
    "utm_term",
    "browser_name",
    "os_name",
    "device_type",
]

Interval = Literal["hour", "day", "week", "month", "year"]
ExportFormat = Literal["csv", "json"]
DataType = Literal["pageviews", "events"]


class HistogramEntry(TypedDict):
    """A single histogram data point."""

    date: str
    pageviews: int
    visitors: int


class PageStats(TypedDict, total=False):
    """Statistics for a single page."""

    value: str
    pageviews: int
    visitors: int
    seconds_on_page: float | None


class WebsiteInfo(TypedDict, total=False):
    """Website information from admin API."""

    hostname: str
    timezone: str
    public: bool
    label: str | None
    created_at: str
