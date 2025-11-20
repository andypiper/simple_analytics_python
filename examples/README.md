# Simple Analytics Python Examples

This directory contains example scripts demonstrating how to use the Simple Analytics Python client.

## UV Runnable Examples

These examples use [UV](https://docs.astral.sh/uv/) inline script dependencies, making them easy to run without manual dependency management.

### Prerequisites

1. Install UV: https://docs.astral.sh/uv/getting-started/installation/
2. (Optional) Set your Simple Analytics credentials:
   ```bash
   export SA_API_KEY="sa_api_key_xxxx"
   export SA_USER_ID="sa_user_id_xxxx"
   ```

### Running the Examples

All examples can be run from the repository root directory:

```bash
# Basic stats (works without auth for public sites)
uv run examples/uv_basic_stats.py

# Histogram chart with terminal visualization
uv run examples/uv_histogram_chart.py

# Top pages horizontal bar chart
uv run examples/uv_pages_chart.py

# Country breakdown charts
uv run examples/uv_country_chart.py

# Data export (requires authentication)
uv run examples/uv_export_data.py
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SA_API_KEY` | For auth endpoints | Your Simple Analytics API key (starts with `sa_api_key_`) |
| `SA_USER_ID` | For auth endpoints | Your Simple Analytics User ID (starts with `sa_user_id_`) |
| `SA_HOSTNAME` | For some examples | Website hostname to query (defaults to `simpleanalytics.com`) |

Get your credentials from: https://simpleanalytics.com/account

### Example Descriptions

#### `uv_basic_stats.py`
Basic usage showing how to:
- Get overall pageview and visitor counts
- List top pages with view counts
- Get histogram (time-series) data
- View referrer statistics
- See country breakdown
- List your websites (with auth)

#### `uv_histogram_chart.py`
Terminal visualization showing:
- Daily pageviews as a bar chart
- Daily visitors as a bar chart
- Combined line chart comparing pageviews vs visitors
- Summary statistics (totals, averages, peaks)

Uses the `plotext` library for terminal-based charts.

#### `uv_pages_chart.py`
Terminal visualization showing:
- Top pages as horizontal bar charts (by pageviews and visitors)
- Detailed table with pageviews, visitors, and views-per-visitor ratio

#### `uv_country_chart.py`
Terminal visualization showing:
- Country breakdown as horizontal bar chart
- Top 10 countries as vertical bar chart
- Percentage breakdown with ASCII bar representation
- Browser and device type statistics

#### `uv_export_data.py`
Data export demonstration showing:
- Export pageviews as JSON
- Export pageviews as CSV
- Export with detailed fields
- Save exports to files
- Export events

**Note:** This example requires authentication.

## Traditional Examples

The `basic_usage.py` and `export_data.py` files are traditional Python scripts that require manual dependency installation:

```bash
# Install the library first
pip install -e ..

# Then run
python basic_usage.py
python export_data.py
```

## Customizing Examples

### Using Your Own Website

Set the `SA_HOSTNAME` environment variable:

```bash
export SA_HOSTNAME="your-website.com"
uv run examples/uv_histogram_chart.py
```

### Changing Date Ranges

Most charting examples default to the last 30 days. Edit the `start_date` and `end_date` variables in the scripts to customize:

```python
from datetime import datetime, timedelta

# Last 90 days
end_date = datetime.now().strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
```

### Terminal Chart Customization

The charting examples use [plotext](https://github.com/piccolomo/plotext). You can customize:

- Chart size: `plt.plot_size(width=100, height=30)`
- Colors: `plt.bar(..., color="blue")`
- Themes: `plt.theme("dark")` or `plt.theme("clear")`

See the [plotext documentation](https://github.com/piccolomo/plotext/blob/master/readme/basic.md) for more options.

## Troubleshooting

### "No data available"

- Make sure the website is public or you have authentication set up
- Check that the hostname is correct
- Try using `simpleanalytics.com` as a test (it's public)

### Authentication Errors

- Verify your API key starts with `sa_api_key_`
- Verify your User ID starts with `sa_user_id_`
- Check that you have access to the website in your Simple Analytics account

### Chart Display Issues

- Ensure your terminal supports Unicode characters
- Try running in a larger terminal window
- Some terminals may not render all plotext features correctly

## Additional Resources

- [Simple Analytics API Documentation](https://docs.simpleanalytics.com/api)
- [UV Documentation](https://docs.astral.sh/uv/)
- [Plotext Documentation](https://github.com/piccolomo/plotext)
