"""Application constants using modern Python patterns."""

from datetime import timedelta
from enum import StrEnum


class EventType(StrEnum):
    """Event type categories."""
    AUTOMATED = "automated"
    CUSTOM = "custom"


class SortOrder(StrEnum):
    """Sort ordering options."""
    PAGEVIEWS_DESC = "pageviews_desc"
    PAGEVIEWS_ASC = "pageviews_asc"
    ALPHABETICAL = "alphabetical"
    VISITORS_DESC = "visitors_desc"


class DateRange(StrEnum):
    """Available date range options."""
    SEVEN_DAYS = "7"
    FOURTEEN_DAYS = "14"
    THIRTY_DAYS = "30"


class ColorScheme(StrEnum):
    """Available chart color schemes."""
    DEFAULT = "default"
    PURPLE_ORANGE = "purple_orange"
    GREEN_BLUE = "green_blue"


class DateRanges:
    """Date range constants for analytics queries."""
    DEFAULT_RANGE = timedelta(days=30)
    MAX_HISTOGRAM_POINTS = 30

    # Map enum values to timedeltas
    RANGE_MAP = {
        DateRange.SEVEN_DAYS: timedelta(days=7),
        DateRange.FOURTEEN_DAYS: timedelta(days=14),
        DateRange.THIRTY_DAYS: timedelta(days=30),
    }


class Limits:
    """API and UI limits."""
    MAX_CONCURRENT_THREADS = 4
    DEFAULT_API_TIMEOUT = 30
    PAGE_LIST_LIMIT = 100


class UI:
    """UI-related constants."""
    WINDOW_DEFAULT_WIDTH = 1200
    WINDOW_DEFAULT_HEIGHT = 800
    WINDOW_MIN_SIZE = 360
    CARD_MIN_WIDTH = 180
    MAX_HOSTNAME_DISPLAY_CHARS = 20
