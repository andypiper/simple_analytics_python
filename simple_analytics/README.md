# Simple Analytics Python Client

A Python wrapper for the [Simple Analytics](https://simpleanalytics.com) API, providing easy access to website statistics, data export, and administrative functions.

## Installation

```bash
pip install simple-analytics-python
```

Or install from source:

```bash
git clone https://github.com/simpleanalytics/python-client.git
cd python-client
pip install -e .
```

## Quick Start

```python
from simple_analytics import SimpleAnalyticsClient

# Initialize the client
client = SimpleAnalyticsClient(
    api_key="sa_api_key_xxxxxxxxxxxxxxxxxxxx",
    user_id="sa_user_id_00000000-0000-0000-0000-000000000000"
)

# Get website statistics
stats = client.stats.get("example.com")
print(f"Pageviews: {stats.get('pageviews')}")
print(f"Visitors: {stats.get('visitors')}")
```

## Authentication

You'll need an API key and User ID from your [Simple Analytics account settings](https://simpleanalytics.com/account).

- **API Key**: Starts with `sa_api_key_`
- **User ID**: Starts with `sa_user_id_`

```python
client = SimpleAnalyticsClient(
    api_key="sa_api_key_xxxx",
    user_id="sa_user_id_xxxx"
)
```

For public websites, you can access the Stats API without authentication:

```python
client = SimpleAnalyticsClient()
stats = client.stats.get("simpleanalytics.com")  # Public website
```

## Stats API

The Stats API provides aggregated analytics data.

### Basic Usage

```python
# Get all available stats
stats = client.stats.get("example.com")

# Get stats for a specific date range
stats = client.stats.get(
    "example.com",
    start="2024-01-01",
    end="2024-01-31"
)

# Get specific fields only
stats = client.stats.get(
    "example.com",
    fields=["pageviews", "visitors", "pages", "referrers"]
)
```

### Available Fields

- `pageviews`, `visitors` - Aggregated counts
- `histogram` - Time-series data (daily/weekly/monthly)
- `pages`, `countries`, `referrers` - Breakdown lists
- `utm_sources`, `utm_mediums`, `utm_campaigns`, `utm_contents`, `utm_terms` - UTM parameters
- `browser_names`, `os_names`, `device_types` - Device/software metrics
- `seconds_on_page` - Median time on page

### Filtering Data

```python
# Filter by country
stats = client.stats.get(
    "example.com",
    filters={"country": "US"}
)

# Filter by page path (supports wildcards)
stats = client.stats.get(
    "example.com",
    filters={"page": "/blog*"}
)

# Multiple filters
stats = client.stats.get(
    "example.com",
    filters={
        "device_type": "mobile",
        "browser_name": "Chrome"
    }
)
```

### Page-Specific Stats

```python
# Get stats for a specific page
stats = client.stats.get("example.com", path="/pricing")
```

### Events

```python
# Get all events
stats = client.stats.get("example.com", events="*")

# Get specific events
stats = client.stats.get("example.com", events=["signup", "purchase"])

# Or use the convenience method
events = client.stats.get_events("example.com")
for event in events.get("events", []):
    print(f"{event['name']}: {event['total']}")
```

### Histogram Data

```python
# Get daily histogram
data = client.stats.get_histogram("example.com", interval="day")

# Get weekly data for a specific period
data = client.stats.get_histogram(
    "example.com",
    start="2024-01-01",
    end="2024-03-31",
    interval="week"
)

for point in data.get("histogram", []):
    print(f"{point['date']}: {point['pageviews']} pageviews")
```

## Export API

The Export API allows you to download raw data points.

### Basic Usage

```python
# Export data as JSON
data = client.export.datapoints(
    "example.com",
    start="2024-01-01",
    end="2024-01-31"
)

for point in data:
    print(f"{point['added_iso']}: {point['path']}")
```

### Export as CSV

```python
# Get CSV data
csv_data = client.export.to_csv(
    "example.com",
    start="2024-01-01",
    end="2024-01-31"
)

# Save to file
with open("export.csv", "w") as f:
    f.write(csv_data)
```

### Select Specific Fields

```python
data = client.export.datapoints(
    "example.com",
    start="2024-01-01",
    end="2024-01-31",
    fields=[
        "added_iso",
        "path",
        "country_code",
        "device_type",
        "browser_name",
        "duration_seconds"
    ]
)
```

### Available Export Fields

- `added_iso`, `added_unix` - Timestamps
- `hostname`, `path`, `query` - URL components
- `is_unique` - Whether visitor is unique
- `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term` - UTM parameters
- `scrolled_percentage`, `duration_seconds` - Engagement metrics
- `device_type`, `country_code` - Device and location
- `browser_name`, `browser_version`, `os_name`, `os_version` - Software
- `viewport_width`, `viewport_height`, `screen_width`, `screen_height` - Screen dimensions
- `language`, `session_id` - Session data
- `referrer_hostname`, `referrer_path` - Referrer info
- `datapoint_id` - Unique identifier

### Export Events

```python
# Export event data
events = client.export.events(
    "example.com",
    start="2024-01-01",
    end="2024-01-31"
)
```

### Hourly Export

```python
# Export data for specific hours
data = client.export.datapoints(
    "example.com",
    start="2024-01-01T09",
    end="2024-01-01T17"
)
```

## Admin API

The Admin API allows you to manage your websites.

### List Websites

```python
websites = client.admin.list_websites()

for site in websites:
    print(f"{site['hostname']} ({site['timezone']})")
    print(f"  Public: {site['public']}")
```

### Get Website Info

```python
site = client.admin.get_website("example.com")
if site:
    print(f"Timezone: {site['timezone']}")
```

### Add Website

Note: Requires Business or Enterprise plan.

```python
site = client.admin.add_website(
    "newsite.com",
    timezone="America/New_York",
    public=False,
    label="My New Project"
)
print(f"Added: {site['hostname']}")
```

## Error Handling

The client raises specific exceptions for different error conditions:

```python
from simple_analytics import (
    SimpleAnalyticsClient,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    ServerError
)

client = SimpleAnalyticsClient(api_key="invalid")

try:
    stats = client.stats.get("example.com")
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
except NotFoundError as e:
    print(f"Website not found: {e.message}")
except RateLimitError as e:
    print(f"Rate limited: {e.message}")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
except ServerError as e:
    print(f"Server error: {e.message}")
```

## Context Manager

The client can be used as a context manager:

```python
with SimpleAnalyticsClient(api_key="...", user_id="...") as client:
    stats = client.stats.get("example.com")
    # Session is automatically closed
```

## Configuration Options

```python
client = SimpleAnalyticsClient(
    api_key="sa_api_key_xxxx",
    user_id="sa_user_id_xxxx",
    base_url="https://simpleanalytics.com",  # Custom base URL
    timeout=60  # Request timeout in seconds
)
```

## API Reference

### SimpleAnalyticsClient

The main client class that provides access to all API endpoints.

**Parameters:**
- `api_key` (str, optional): Your API key
- `user_id` (str, optional): Your user ID
- `base_url` (str): API base URL (default: https://simpleanalytics.com)
- `timeout` (int): Request timeout in seconds (default: 30)

**Properties:**
- `stats`: StatsAPI instance
- `export`: ExportAPI instance
- `admin`: AdminAPI instance

### StatsAPI

Access aggregated statistics.

**Methods:**
- `get()`: Get website statistics with filters and fields
- `get_events()`: Get event statistics
- `get_histogram()`: Get time-series data

### ExportAPI

Export raw data points.

**Methods:**
- `datapoints()`: Export data points (JSON or CSV)
- `pageviews()`: Export pageview data
- `events()`: Export event data
- `to_csv()`: Export as CSV string

### AdminAPI

Manage websites.

**Methods:**
- `list_websites()`: List all websites
- `add_website()`: Add a new website
- `get_website()`: Get specific website info

## License

MIT License - see LICENSE file for details.

## Links

- [Simple Analytics](https://simpleanalytics.com)
- [API Documentation](https://docs.simpleanalytics.com/api)
- [GitHub Repository](https://github.com/simpleanalytics/python-client)
