# Simple Analytics Python

> A Python client library for the [Simple Analytics](https://simpleanalytics.com) API

[![License](https://img.shields.io/github/license/andypiper/simple_analytics_python)](LICENSE)

A comprehensive Python wrapper for the Simple Analytics API, providing easy access to website analytics data, data exports, and account management.

## Table of Contents

- [Background](#background)
- [Install](#install)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Stats API](#stats-api)
  - [Export API](#export-api)
  - [Admin API](#admin-api)
- [API](#api)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Background

[Simple Analytics](https://simpleanalytics.com) is a privacy-friendly analytics platform that doesn't track users or collect personal data. This library provides a Pythonic interface to their API, making it easy to:

- Retrieve aggregated website statistics
- Export raw pageview and event data
- Manage websites in your account
- Build dashboards and reports

## Install

### Requirements

- Python 3.12 or higher
- A Simple Analytics account (for authenticated endpoints)

### Installation

Using pip:

```bash
pip install simple-analytics-python
```

Using uv:

```bash
uv add simple-analytics-python
```

From source:

```bash
git clone https://github.com/andypiper/simple_analytics_python.git
cd simple_analytics_python
pip install -e .
```

## Usage

### Basic Usage

```python
from simple_analytics import SimpleAnalyticsClient

# Initialize client (no auth needed for public website stats)
client = SimpleAnalyticsClient()

# Get basic stats for a public website
stats = client.stats.get(
    "simpleanalytics.com",
    fields=["pageviews", "visitors"]
)
print(f"Pageviews: {stats['pageviews']}")
print(f"Visitors: {stats['visitors']}")
```

### Authentication

For private websites and data exports, you'll need API credentials:

```python
import os
from simple_analytics import SimpleAnalyticsClient

client = SimpleAnalyticsClient(
    api_key=os.environ.get("SA_API_KEY"),
    user_id=os.environ.get("SA_USER_ID")
)
```

Get your credentials from your [Simple Analytics account settings](https://simpleanalytics.com/account).

### Stats API

Retrieve aggregated analytics data:

```python
# Get stats with specific fields
stats = client.stats.get(
    "example.com",
    start="2024-01-01",
    end="2024-01-31",
    fields=["pageviews", "visitors", "pages", "referrers", "countries"],
    limit=50
)

# Get histogram data
histogram = client.stats.get_histogram(
    "example.com",
    interval="day"  # hour, day, week, month, year
)

# Get events
events = client.stats.get_events(
    "example.com",
    events=["signup", "purchase"]
)

# Apply filters
stats = client.stats.get(
    "example.com",
    fields=["pageviews", "pages"],
    filters={
        "country": "US",
        "device_type": "desktop"
    }
)
```

### Export API

Export raw data points (requires authentication):

```python
from datetime import datetime, timedelta

end_date = datetime.now().strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

# Export as JSON
data = client.export.datapoints(
    "example.com",
    start=start_date,
    end=end_date,
    fields=["added_iso", "path", "country_code", "device_type"]
)

# Export as CSV
csv_data = client.export.to_csv(
    "example.com",
    start=start_date,
    end=end_date
)

# Export events
events = client.export.events(
    "example.com",
    start=start_date,
    end=end_date
)
```

### Admin API

Manage your Simple Analytics account (requires authentication):

```python
# List all websites
websites = client.admin.list_websites()

# Add a new website
new_site = client.admin.add_website(
    "newsite.com",
    timezone="America/New_York",
    public=False
)

# Get a specific website
site = client.admin.get_website("example.com")
```

### Context Manager

The client supports context manager usage for proper resource cleanup:

```python
with SimpleAnalyticsClient(api_key=api_key, user_id=user_id) as client:
    stats = client.stats.get("example.com", fields=["pageviews", "visitors"])
    print(stats)
# Session is automatically closed
```

### Error Handling

The library provides specific exceptions for different error cases:

```python
from simple_analytics import SimpleAnalyticsClient
from simple_analytics.exceptions import (
    SimpleAnalyticsError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    ServerError
)

try:
    stats = client.stats.get("example.com", fields=["pageviews"])
except AuthenticationError as e:
    print(f"Auth failed: {e}")
except RateLimitError as e:
    print(f"Rate limited: {e}")
except NotFoundError as e:
    print(f"Website not found: {e}")
except SimpleAnalyticsError as e:
    print(f"API error: {e}")
```

## API

### SimpleAnalyticsClient

The main client class.

#### Constructor

```python
SimpleAnalyticsClient(
    api_key: str | None = None,
    user_id: str | None = None,
    base_url: str = "https://simpleanalytics.com",
    timeout: int = 30
)
```

#### Properties

- `stats` - Access to the Stats API
- `export` - Access to the Export API
- `admin` - Access to the Admin API

### Stats API Methods

#### `client.stats.get()`

Get aggregated statistics for a website.

**Parameters:**
- `hostname` (str): Website domain
- `path` (str, optional): Specific page path
- `start` (str, optional): Start date (YYYY-MM-DD)
- `end` (str, optional): End date (YYYY-MM-DD)
- `timezone` (str, optional): Timezone for calculations
- `fields` (list[str], optional): Fields to retrieve
- `limit` (int, optional): Max results (1-1000)
- `info` (bool, optional): Include metadata (default: True)
- `interval` (str, optional): Histogram granularity
- `events` (str | list[str], optional): Event names
- `filters` (dict, optional): Filter parameters

**Available fields:** `pageviews`, `visitors`, `histogram`, `pages`, `countries`, `referrers`, `utm_sources`, `utm_mediums`, `utm_campaigns`, `utm_contents`, `utm_terms`, `browser_names`, `os_names`, `device_types`, `seconds_on_page`

#### `client.stats.get_histogram()`

Get time-series histogram data.

#### `client.stats.get_events()`

Get event statistics.

### Export API Methods

#### `client.export.datapoints()`

Export raw data points.

**Parameters:**
- `hostname` (str): Website domain
- `start` (str): Start date/time
- `end` (str): End date/time
- `format` (str, optional): "json" or "csv" (default: "json")
- `fields` (list[str], optional): Fields to include
- `timezone` (str, optional): Timezone
- `robots` (bool, optional): Include bot traffic (default: False)
- `data_type` (str, optional): "pageviews" or "events"

#### `client.export.pageviews()`

Export pageview data (convenience method).

#### `client.export.events()`

Export event data (convenience method).

#### `client.export.to_csv()`

Export data as CSV string.

### Admin API Methods

#### `client.admin.list_websites()`

List all websites in your account.

#### `client.admin.add_website()`

Add a new website.

**Parameters:**
- `hostname` (str): Website domain
- `timezone` (str, optional): Timezone (default: "UTC")
- `public` (bool, optional): Public stats (default: False)
- `label` (str, optional): Website label

#### `client.admin.get_website()`

Get a specific website by hostname.

## Examples

The `examples/` directory contains runnable examples:

| Example | Description |
|---------|-------------|
| `basic_stats.py` | Basic client usage and stats retrieval |
| `export_data.py` | Data export examples |
| `histogram_chart.py` | Terminal histogram charts |
| `country_chart.py` | Country breakdown with emoji flags |
| `pages_chart.py` | Top pages visualization |

Run examples with:

```bash
# Set environment variables
export SA_API_KEY="sa_api_key_xxxx"
export SA_USER_ID="sa_user_id_xxxx"
export SA_HOSTNAME="your-website.com"  # Optional

# Run with UV
uv run examples/basic_stats.py

# Or with Python
python examples/basic_stats.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/andypiper/simple_analytics_python.git
cd simple_analytics_python

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linting
ruff check simple_analytics/
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage (requires pytest-cov)
pytest tests/ --cov=simple_analytics --cov-report=term-missing
```

## License

[MIT](LICENSE) - See LICENSE file for details.

## Acknowledgements

- [Simple Analytics](https://simpleanalytics.com) for providing a privacy-friendly analytics platform
- The Simple Analytics team for their comprehensive API documentation
