# Code Review: Simple Analytics GTK Viewer

## Executive Summary

This code review examines the Simple Analytics GTK viewer application and its Python API client library. The codebase demonstrates good understanding of GTK4/Libadwaita patterns and threading concepts, but has significant opportunities for improvement in type safety, error handling, threading patterns, and modern Python practices.

**Overall Assessment**: Code is functional but needs modernization for production-quality Python 3.12+ standards.

---

## Critical Issues (Priority: HIGH)

### 1. Threading Safety Violations

**Location**: `analytics_viewer/window.py:565-570, 572-585`

**Issue**: Multiple concurrent threads are spawned without proper synchronization or thread pool management. Race conditions possible.

```python
# CURRENT CODE - PROBLEMATIC
for view, name in views:
    thread = threading.Thread(
        target=self._load_view_data,
        args=(view, name, self.client, self.hostname, start_date, end_date),
        daemon=True
    )
    thread.start()
```

**Problems**:
- No thread pool limits - could spawn hundreds of threads with rapid clicks
- No thread lifecycle management - threads never joined
- No mechanism to cancel in-flight requests when switching websites
- Race condition: `self.client` and `self.hostname` could change while threads are running
- No error aggregation or coordination between threads

**Recommended Fix**:
```python
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
import threading

class AnalyticsWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Limit concurrent API calls
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="api-")
        self._current_load_generation = 0
        self._load_lock = threading.Lock()
        # ... rest of init

    def load_data(self):
        """Load analytics data for the selected website asynchronously."""
        if not self.client or not self.hostname:
            return

        # Cancel any in-flight loads from previous website selection
        with self._load_lock:
            self._current_load_generation += 1
            current_gen = self._current_load_generation

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        # Capture values to avoid race conditions
        client = self.client
        hostname = self.hostname

        views = [
            (self.dashboard_view, "Dashboard"),
            (self.events_view, "Events"),
            (self.pages_view, "Pages"),
            (self.countries_view, "Countries"),
        ]

        for view, name in views:
            self._executor.submit(
                self._load_view_data_safe,
                view, name, client, hostname, start_date, end_date, current_gen
            )

    def _load_view_data_safe(self, view, view_name, client, hostname,
                            start_date, end_date, generation):
        """Load data with generation check to handle cancellation."""
        try:
            # Check if this load was superseded
            with self._load_lock:
                if generation != self._current_load_generation:
                    print(f"Skipping outdated {view_name} load (gen {generation})")
                    return

            view.load_data(client, hostname, start_date, end_date)
        except Exception as e:
            import traceback
            traceback.print_exc()
            GLib.idle_add(self.show_error, f"Error loading {view_name} data: {str(e)}")

    def close(self):
        """Clean shutdown of thread pool."""
        self._executor.shutdown(wait=False, cancel_futures=True)
        super().close()
```

**Priority**: HIGH - Race conditions can cause data corruption and UI inconsistencies

---

### 2. Missing Type Hints Throughout

**Location**: Multiple files - all view classes, window.py, client.py

**Issue**: Type hints are incomplete or missing, reducing code safety and IDE support.

**Examples**:

`analytics_viewer/window.py`:
```python
# CURRENT - No type hints
def __init__(self, **kwargs):
    super().__init__(**kwargs)

# SHOULD BE
def __init__(self, **kwargs: Any) -> None:
    super().__init__(**kwargs)

# CURRENT - Missing return type and parameter types
def load_data(self):

# SHOULD BE
def load_data(self) -> None:
```

`analytics_viewer/views/events.py:93`:
```python
# CURRENT
def load_data(self, client, hostname, start_date, end_date):

# SHOULD BE
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from simple_analytics import SimpleAnalyticsClient

def load_data(
    self,
    client: SimpleAnalyticsClient,
    hostname: str,
    start_date: str,
    end_date: str
) -> None:
```

**Recommended Action**: Add comprehensive type hints to all functions and methods. Use `mypy --strict` to enforce.

**Priority**: HIGH - Type safety is critical for maintainability

---

### 3. Bare Except Clauses and Poor Error Handling

**Location**: Multiple files

**Issues Found**:

1. `analytics_viewer/views/dashboard.py:193-194`:
```python
# PROBLEMATIC - Silently swallows ALL exceptions including SystemExit, KeyboardInterrupt
try:
    events_stats = client.stats.get_events(...)
except:
    pass
```

2. `analytics_viewer/window.py:496`:
```python
# PROBLEMATIC - Catching too broadly based on string matching
except Exception as e:
    if "dismissed" not in str(e).lower():
        self.show_error(f"Export failed: {str(e)}")
```

**Recommended Fixes**:

```python
# 1. Specific exception handling
from simple_analytics.exceptions import SimpleAnalyticsError

try:
    events_stats = client.stats.get_events(
        hostname, start=start_date, end=end_date
    )
    total_events = sum(e.get("total", 0) for e in events_stats.get("events", []))
except SimpleAnalyticsError as e:
    # Expected API errors - log but continue with N/A
    print(f"Events API unavailable: {e.message}")
    total_events = "N/A"
except Exception as e:
    # Unexpected errors - log and continue
    print(f"Unexpected error fetching events: {e}")
    total_events = "N/A"

# 2. Use proper exception types
from gi.repository import GLib

def on_export_file_selected(self, dialog, result):
    """Handle file selection for export."""
    try:
        file = dialog.save_finish(result)
        if file:
            file_path = file.get_path()
            self.export_data_to_file(file_path)
    except GLib.Error as e:
        # GTK dialog was dismissed/cancelled
        if e.code == Gtk.DialogError.DISMISSED:
            return
        self.show_error(f"File selection failed: {e.message}")
    except Exception as e:
        self.show_error(f"Export failed: {str(e)}")
```

**Priority**: HIGH - Bare except can catch SystemExit and hide critical bugs

---

### 4. No Request Timeout Control in Views

**Location**: All view `load_data` methods

**Issue**: Views make blocking API calls in threads with no timeout control. Network issues could hang threads indefinitely.

**Current**:
```python
def load_data(self, client, hostname, start_date, end_date):
    stats = client.stats.get(hostname, start=start_date, end=end_date, fields=[...])
    # No timeout, no cancellation
```

**Recommended**:
```python
# In client.py - allow per-request timeout override
def request(
    self,
    method: str,
    endpoint: str,
    params: dict | None = None,
    json: dict | None = None,
    require_auth: bool = False,
    timeout: int | tuple[int, int] | None = None,  # NEW
) -> Any:
    """Make an HTTP request to the API."""
    url = f"{self.base_url}{endpoint}"
    headers = self._get_headers(require_auth)

    # Use request-specific timeout or fall back to client default
    request_timeout = timeout if timeout is not None else self.timeout

    try:
        response = self._session.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json,
            timeout=request_timeout,  # Use potentially overridden timeout
        )
    except requests.exceptions.Timeout as e:
        raise NetworkError(f"Request timed out after {request_timeout}s: {e}") from e
    # ... rest of error handling
```

**Priority**: HIGH - Network timeouts can freeze the UI

---

## Medium Priority Issues

### 5. Inconsistent List Clearing Pattern

**Location**: All views with ListBox widgets

**Issue**: Inefficient list clearing using a while loop that could be a simple method call.

**Current** (`dashboard.py:230-235`):
```python
# Inefficient and verbose
while True:
    row = self.pages_list.get_row_at_index(0)
    if row:
        self.pages_list.remove(row)
    else:
        break
```

**Recommended**:
```python
def clear_list_box(list_box: Gtk.ListBox) -> None:
    """Clear all rows from a ListBox efficiently."""
    list_box.remove_all()  # Available in GTK4

# Or if using older GTK version:
def clear_list_box(list_box: Gtk.ListBox) -> None:
    """Clear all rows from a ListBox."""
    while (row := list_box.get_row_at_index(0)) is not None:
        list_box.remove(row)

# Usage
self.clear_list_box(self.pages_list)
```

**Priority**: MEDIUM - Code duplication and inefficiency

---

### 6. No Data Validation in API Client

**Location**: `simple_analytics/client.py:125-165`, `stats.py`

**Issue**: Minimal validation of API responses before returning to caller.

**Current**:
```python
def _handle_response(self, response: requests.Response) -> Any:
    if response.status_code == 200:
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return response.json()  # No schema validation
```

**Recommended** (using Pydantic for validation):

```python
# In types.py
from pydantic import BaseModel, Field, field_validator
from datetime import date

class StatsResponse(BaseModel):
    """Validated response from Stats API."""
    pageviews: int = Field(ge=0)
    visitors: int = Field(ge=0)
    pages: list[PageStats] = Field(default_factory=list)
    histogram: list[HistogramPoint] = Field(default_factory=list)

    class Config:
        extra = "allow"  # Allow additional fields from API

class PageStats(BaseModel):
    value: str
    pageviews: int = Field(ge=0)
    visitors: int = Field(ge=0, default=0)

class HistogramPoint(BaseModel):
    date: str
    pageviews: int = Field(ge=0)
    visitors: int = Field(ge=0)

    @field_validator('date')
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Ensure date is in YYYY-MM-DD format."""
        try:
            date.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid date format: {v}")

# In stats.py
def get(self, hostname: str, ...) -> StatsResponse:
    """Get aggregated statistics (now returns validated model)."""
    raw_data = self._client.get(endpoint, params=params, require_auth=False)

    try:
        return StatsResponse.model_validate(raw_data)
    except ValidationError as e:
        raise SimpleAnalyticsError(f"Invalid API response: {e}")
```

**Priority**: MEDIUM - Improves reliability and type safety

---

### 7. Password Storage in Plain Text

**Location**: `window.py:601-608`, `preferences.py`

**Issue**: API credentials stored in GSettings without encryption.

**Current**:
```python
# Saved as plain text
self.settings.set_string("api-key", api_key)
```

**Security Concern**: GSettings stores data in plain text in `~/.config/dconf/user`. API keys can be extracted easily.

**Recommended Solution** (using Secret Service API):

```python
# NEW FILE: analytics_viewer/keyring.py
"""Secure credential storage using libsecret."""

import gi
gi.require_version('Secret', '1')
from gi.repository import Secret

SCHEMA = Secret.Schema.new(
    "org.andypiper.SimpleAnalyticsViewer",
    Secret.SchemaFlags.NONE,
    {
        "credential-type": Secret.SchemaAttributeType.STRING,
    }
)

class CredentialManager:
    """Manages secure storage of API credentials."""

    @staticmethod
    def store_api_key(api_key: str) -> bool:
        """Store API key securely in system keyring."""
        return Secret.password_store_sync(
            SCHEMA,
            {"credential-type": "api-key"},
            Secret.COLLECTION_DEFAULT,
            "Simple Analytics API Key",
            api_key,
            None
        )

    @staticmethod
    def retrieve_api_key() -> str | None:
        """Retrieve API key from secure storage."""
        return Secret.password_lookup_sync(
            SCHEMA,
            {"credential-type": "api-key"},
            None
        )

    @staticmethod
    def clear_api_key() -> bool:
        """Remove API key from secure storage."""
        return Secret.password_clear_sync(
            SCHEMA,
            {"credential-type": "api-key"},
            None
        )

# Usage in window.py
from .keyring import CredentialManager

# Store
CredentialManager.store_api_key(api_key)
CredentialManager.store_user_id(user_id)

# Retrieve
self.api_key = CredentialManager.retrieve_api_key() or os.environ.get("SA_API_KEY", "")
```

**Priority**: MEDIUM - Security concern for production use

---

### 8. No Logging Framework

**Location**: Throughout codebase - using `print()` statements

**Issue**: Using `print()` for debugging instead of proper logging.

**Examples**:
- `window.py:64, 71, 390, 406, 413, 427, 542, 553`
- `dashboard.py:205`
- `events.py:124`

**Recommended**:

```python
# NEW FILE: analytics_viewer/logging_config.py
"""Logging configuration for the application."""

import logging
import sys
from pathlib import Path

def setup_logging(verbose: bool = False) -> None:
    """Configure application logging.

    Args:
        verbose: Enable DEBUG level logging
    """
    level = logging.DEBUG if verbose else logging.INFO

    # Create logs directory
    log_dir = Path.home() / ".local" / "share" / "simple-analytics-viewer" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler with rotation
            logging.handlers.RotatingFileHandler(
                log_dir / "app.log",
                maxBytes=10_485_760,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
        ]
    )

    # Quiet noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

# In window.py
import logging

logger = logging.getLogger(__name__)

class AnalyticsWindow(Adw.ApplicationWindow):
    def authenticate(self):
        """Authenticate with Simple Analytics API."""
        logger.info("Starting authentication")

        if not self.api_key or not self.user_id:
            logger.warning("Missing credentials, showing auth dialog")
            self.show_auth_dialog()
            return

        try:
            self.client = SimpleAnalyticsClient(...)
            logger.info("Client initialized successfully")

            self.websites = self.client.admin.list_websites()
            logger.debug(f"Retrieved {len(self.websites)} websites")

        except AuthenticationError as e:
            logger.error(f"Authentication failed: {e.message}", exc_info=True)
            self.show_error(f"Authentication failed: {e.message}")
```

**Priority**: MEDIUM - Essential for debugging production issues

---

### 9. Magic Numbers and String Literals

**Location**: Throughout codebase

**Issue**: Hard-coded values that should be constants.

**Examples**:

`window.py:504, 551`:
```python
# Magic number - should be constant
start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
```

`dashboard.py:220`:
```python
# Magic number for histogram length
self.histogram_chart.set_data(histogram[-30:])
```

**Recommended**:

```python
# NEW FILE: analytics_viewer/constants.py
"""Application constants."""

from datetime import timedelta

class DateRanges:
    """Date range constants for analytics queries."""
    DEFAULT_RANGE = timedelta(days=30)
    MAX_HISTOGRAM_POINTS = 30

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

# Usage
from .constants import DateRanges, UI

class AnalyticsWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_default_size(UI.WINDOW_DEFAULT_WIDTH, UI.WINDOW_DEFAULT_HEIGHT)
        self.set_size_request(UI.WINDOW_MIN_SIZE, UI.WINDOW_MIN_SIZE)

    def load_data(self):
        end_date = datetime.now()
        start_date = end_date - DateRanges.DEFAULT_RANGE
        # ...
```

**Priority**: MEDIUM - Improves maintainability

---

## Low Priority Issues

### 10. Missing Docstrings and Documentation

**Location**: Multiple methods lack docstrings

**Examples**:

`window.py:240, 257, 265, 279`:
```python
# Missing docstrings
def _on_dropdown_list_setup(self, factory, list_item):
    """Set up list item widget for dropdown menu (full hostname with icon)."""
    # Implementation...

def _on_dropdown_list_bind(self, factory, list_item):
    # MISSING DOCSTRING
    box = list_item.get_child()
```

**Recommended** (Google-style docstrings):

```python
def _on_dropdown_list_bind(self, factory: Gtk.SignalListItemFactory,
                          list_item: Gtk.ListItem) -> None:
    """Bind website hostname data to dropdown list item.

    Called by GTK when a list item needs to display data from the model.
    Extracts the hostname string and sets it as the label text.

    Args:
        factory: The factory that created this binding request
        list_item: The list item to populate with data

    Note:
        This is a GTK signal callback - signature is determined by the signal.
    """
    box = list_item.get_child()
    label = box.get_last_child()  # Label is the last child after icon
    string_object = list_item.get_item()
    if string_object:
        label.set_text(string_object.get_string())
```

**Priority**: LOW - Documentation gap but code is fairly readable

---

### 11. No Unit Tests

**Location**: No test files found

**Issue**: Zero test coverage makes refactoring dangerous.

**Recommended Structure**:

```
analytics_viewer/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # pytest fixtures
│   ├── test_window.py
│   ├── test_views/
│   │   ├── test_dashboard.py
│   │   ├── test_events.py
│   │   └── test_pages.py
│   └── test_keyring.py
└── simple_analytics/
    └── tests/
        ├── __init__.py
        ├── conftest.py
        ├── test_client.py
        ├── test_stats.py
        └── test_exceptions.py
```

**Example Test**:

```python
# analytics_viewer/tests/conftest.py
"""Pytest fixtures for GTK testing."""

import pytest
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

@pytest.fixture
def gtk_app():
    """Create a minimal GTK application for testing."""
    app = Adw.Application(application_id="org.andypiper.test")
    yield app
    app.quit()

@pytest.fixture
def mock_client(mocker):
    """Create a mock SimpleAnalyticsClient."""
    client = mocker.Mock()
    client.stats.get.return_value = {
        "pageviews": 1000,
        "visitors": 500,
        "pages": [],
        "histogram": []
    }
    return client

# analytics_viewer/tests/test_views/test_events.py
"""Tests for EventsView."""

import pytest
from analytics_viewer.views.events import EventsView

def test_events_view_initialization():
    """Test EventsView initializes correctly."""
    view = EventsView()
    assert view is not None
    assert hasattr(view, 'events_list')

def test_load_data_updates_ui(mock_client, mocker):
    """Test load_data updates UI correctly."""
    view = EventsView()

    # Mock the API response
    mock_client.stats.get_events.return_value = {
        "events": [
            {"name": "click", "total": 100},
            {"name": "outbound_example.com", "total": 50}
        ]
    }

    # Mock GLib.idle_add to run immediately
    mocker.patch('gi.repository.GLib.idle_add', side_effect=lambda f, *args: f(*args))

    # Load data
    view.load_data(mock_client, "example.com", "2024-01-01", "2024-01-31")

    # Verify UI was updated
    assert view.total_card.value_label.get_text() == "150"
    assert view.automated_card.value_label.get_text() == "50"
    assert view.custom_card.value_label.get_text() == "100"
```

**Setup Testing Dependencies**:

```toml
# pyproject.toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "pytest-cov>=4.1",
    "pytest-mock>=3.12",
    "ruff>=0.1.0",
    "mypy>=1.7",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --cov=analytics_viewer --cov-report=html --cov-report=term"

[tool.coverage.run]
source = ["analytics_viewer", "simple_analytics"]
omit = ["*/tests/*", "*/test_*.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

**Priority**: LOW - Important for long-term maintenance but app is small

---

### 12. Use Modern Python Patterns

**Location**: Multiple files

**Issue**: Not leveraging Python 3.12+ features.

**Examples**:

1. **Use `match` statements** (`events.py:115-118`):

```python
# CURRENT
if name.startswith(("outbound", "click_email", "download_")):
    automated_count += count
else:
    custom_count += count

# MODERN (Python 3.10+)
match name:
    case str() if name.startswith(("outbound", "click_email", "download_")):
        automated_count += count
    case _:
        custom_count += count
```

2. **Use walrus operator** (already done well in countries.py:31):
```python
# Good use in countries.py
if not country_code or len(country_code) != 2:
    return "🌍"
```

3. **Use `StrEnum` for constants**:

```python
# NEW - Python 3.11+
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
```

4. **Use `contextlib.suppress`**:

```python
# CURRENT - dashboard.py:193-194
try:
    events_stats = client.stats.get_events(...)
except:
    pass

# MODERN
from contextlib import suppress

with suppress(SimpleAnalyticsError):
    events_stats = client.stats.get_events(...)
```

**Priority**: LOW - Nice-to-have improvements

---

## Performance Optimizations

### 13. Inefficient String Formatting

**Location**: Multiple files

**Current**:
```python
# Using old-style formatting
f"{pageviews:,} pageviews • {visitors:,} visitors"
```

**Recommendation**: This is actually fine! f-strings are the modern standard. Good job!

---

### 14. Missing Connection Pooling Configuration

**Location**: `simple_analytics/client.py:59`

**Current**:
```python
self._session = requests.Session()
```

**Recommended** (add connection pooling):

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def __init__(self, api_key: str | None = None, ...):
    self.api_key = api_key
    self.user_id = user_id
    self.base_url = base_url.rstrip("/")
    self.timeout = timeout
    self.user_agent = user_agent or self.DEFAULT_USER_AGENT

    # Configure session with connection pooling and retries
    self._session = requests.Session()

    # Retry strategy for transient failures
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )

    # Connection pooling adapter
    adapter = HTTPAdapter(
        pool_connections=10,
        pool_maxsize=20,
        max_retries=retry_strategy
    )

    self._session.mount("http://", adapter)
    self._session.mount("https://", adapter)
```

**Priority**: MEDIUM - Improves reliability and performance

---

## Code Quality Issues

### 15. Inconsistent Error Messages

**Location**: Throughout codebase

**Issue**: Error messages lack context for debugging.

**Examples**:

`window.py:542`:
```python
print("No client available")  # Which method? Why?
```

**Recommended**:
```python
logger.error("load_data: Cannot load data - client not initialized")
```

**Priority**: LOW - Minor quality issue

---

### 16. Missing `__all__` Exports

**Location**: All module files

**Issue**: Public API not explicitly defined.

**Recommended**:

```python
# analytics_viewer/views/__init__.py
"""View classes for the analytics viewer."""

from .dashboard import DashboardView
from .events import EventsView
from .pages import PagesView
from .countries import CountriesView

__all__ = [
    "DashboardView",
    "EventsView",
    "PagesView",
    "CountriesView",
]

# simple_analytics/__init__.py
"""Simple Analytics API client library."""

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

__version__ = "0.1.0"

__all__ = [
    "SimpleAnalyticsClient",
    "SimpleAnalyticsError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
    "ServerError",
    "NetworkError",
]
```

**Priority**: LOW - Good practice for library code

---

## Recommendations Summary

### Immediate Actions (Do First)

1. **Fix threading** - Implement ThreadPoolExecutor with cancellation
2. **Add type hints** - Start with public APIs and work inward
3. **Fix bare except** - Replace with specific exception types
4. **Add timeouts** - Ensure all network calls have timeouts
5. **Setup logging** - Replace print() with proper logging

### Short-term Improvements (Next Sprint)

6. **Add tests** - Start with critical paths (API client, data loading)
7. **Implement proper error handling** - Specific exceptions, user-friendly messages
8. **Add data validation** - Use Pydantic for API responses
9. **Extract constants** - Remove magic numbers
10. **Add docstrings** - Document public APIs

### Long-term Enhancements (Future)

11. **Secure credentials** - Implement keyring storage
12. **Performance monitoring** - Add metrics and profiling
13. **Comprehensive testing** - Aim for >80% coverage
14. **CI/CD pipeline** - Automated testing and linting

---

## Modern Python Tooling Setup

Replace current dev dependencies with modern tools:

```toml
# pyproject.toml
[project.optional-dependencies]
dev = [
    "ruff>=0.1.9",        # Fast linter + formatter (replaces black, isort, flake8)
    "mypy>=1.8",          # Type checking
    "pytest>=7.4",        # Testing
    "pytest-cov>=4.1",    # Coverage
    "pytest-mock>=3.12",  # Mocking
    "pytest-asyncio>=0.23", # Async testing
]

[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "SIM", # flake8-simplify
    "RUF", # Ruff-specific rules
]
ignore = ["E501"]  # Line too long (handled by formatter)

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
```

**Usage**:
```bash
# Format code
ruff format .

# Lint code
ruff check . --fix

# Type check
mypy analytics_viewer simple_analytics

# Run tests with coverage
pytest --cov
```

---

## Security Considerations

### Current Security Issues:

1. **Credentials in plain text** (GSettings) - MEDIUM risk
2. **No input sanitization** for hostnames - LOW risk
3. **No HTTPS verification config** - requests uses good defaults
4. **Environment variables logged** - Could leak in debug mode

### Recommendations:

```python
# 1. Sanitize hostname input
import re

def validate_hostname(hostname: str) -> str:
    """Validate and sanitize hostname.

    Args:
        hostname: Raw hostname input

    Returns:
        Validated hostname

    Raises:
        ValidationError: If hostname is invalid
    """
    # Remove whitespace
    hostname = hostname.strip()

    # Basic hostname validation (RFC 1123)
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'

    if not re.match(pattern, hostname):
        raise ValidationError(f"Invalid hostname: {hostname}")

    if len(hostname) > 253:
        raise ValidationError("Hostname too long (max 253 characters)")

    return hostname.lower()

# 2. Redact sensitive data in logs
class SensitiveFormatter(logging.Formatter):
    """Formatter that redacts sensitive information."""

    SENSITIVE_PATTERNS = [
        (re.compile(r'(api[_-]?key["\s:=]+)([a-zA-Z0-9_-]+)', re.I), r'\1***REDACTED***'),
        (re.compile(r'(user[_-]?id["\s:=]+)([a-zA-Z0-9_-]+)', re.I), r'\1***REDACTED***'),
    ]

    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            msg = pattern.sub(replacement, msg)
        return msg
```

---

## Conclusion

The codebase is functional and demonstrates good understanding of GTK4/Libadwaita patterns. However, it needs significant improvements to meet modern Python 3.12+ standards:

**Strengths:**
- Good GTK4/Libadwaita usage
- Clean separation of concerns (views, client, window)
- Threading for async operations (concept is right)
- Modern f-string formatting
- Proper use of type unions (`str | None`)

**Critical Gaps:**
- Threading safety and resource management
- Type hints coverage
- Error handling specificity
- Testing infrastructure
- Logging framework

**Effort Estimate:**
- High priority fixes: ~3-4 days
- Medium priority: ~1 week
- Low priority + testing: ~2 weeks
- **Total: ~3-4 weeks** for production-ready code

**Recommended Next Steps:**
1. Set up ruff + mypy in CI
2. Fix threading (ThreadPoolExecutor)
3. Add type hints to public APIs
4. Write tests for critical paths
5. Replace print() with logging
6. Document deployment and contribution guidelines

The application shows promise and with these improvements will be a solid, maintainable Python 3.12+ project.
