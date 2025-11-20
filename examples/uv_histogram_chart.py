#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "simple-analytics-python @ file://${PROJECT_ROOT}",
#     "plotext>=5.2.8",
# ]
# [tool.uv]
# exclude-newer = "2025-01-01"
# ///
"""
Terminal chart example showing pageviews histogram over time.

Run with: uv run examples/uv_histogram_chart.py

This example fetches histogram data from Simple Analytics and displays
it as a bar chart directly in your terminal using plotext.

Before running, optionally set your credentials:
    export SA_API_KEY="sa_api_key_xxxx"
    export SA_USER_ID="sa_user_id_xxxx"

Note: Stats for public websites work without authentication.
"""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import plotext as plt
from simple_analytics import SimpleAnalyticsClient


def main():
    # Get credentials from environment (optional for public websites)
    api_key = os.environ.get("SA_API_KEY")
    user_id = os.environ.get("SA_USER_ID")

    # Initialize client
    client = SimpleAnalyticsClient(
        api_key=api_key,
        user_id=user_id
    )

    # Use simpleanalytics.com as example (it's public)
    hostname = os.environ.get("SA_HOSTNAME", "simpleanalytics.com")

    # Calculate date range (last 30 days)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    print(f"Fetching histogram data for {hostname}...")
    print(f"Date range: {start_date} to {end_date}")
    print()

    # Get histogram data
    data = client.stats.get_histogram(
        hostname,
        start=start_date,
        end=end_date,
        interval="day"
    )

    if "histogram" not in data or not data["histogram"]:
        print("No histogram data available")
        return

    histogram = data["histogram"]

    # Extract dates and values
    dates = [point.get("date", "") for point in histogram]
    pageviews = [point.get("pageviews", 0) for point in histogram]
    visitors = [point.get("visitors", 0) for point in histogram]

    # Shorten dates for display (MM-DD format)
    short_dates = [d[5:] if len(d) >= 10 else d for d in dates]

    # Chart 1: Pageviews bar chart
    plt.clear_figure()
    plt.theme("clear")
    plt.plot_size(width=100, height=20)

    plt.bar(short_dates, pageviews, marker="sd", color="cyan")
    plt.title(f"Daily Pageviews - {hostname}")
    plt.xlabel("Date")
    plt.ylabel("Pageviews")

    # Show every 5th date label to avoid crowding
    plt.show()
    print()

    # Chart 2: Visitors bar chart
    plt.clear_figure()
    plt.theme("clear")
    plt.plot_size(width=100, height=20)

    plt.bar(short_dates, visitors, marker="sd", color="green")
    plt.title(f"Daily Visitors - {hostname}")
    plt.xlabel("Date")
    plt.ylabel("Visitors")

    plt.show()
    print()

    # Chart 3: Combined line chart
    plt.clear_figure()
    plt.theme("clear")
    plt.plot_size(width=100, height=25)

    # Use numeric x-axis for cleaner plotting
    x = list(range(len(dates)))
    plt.plot(x, pageviews, marker="braille", label="Pageviews", color="cyan")
    plt.plot(x, visitors, marker="braille", label="Visitors", color="green")

    plt.title(f"Pageviews vs Visitors - {hostname}")
    plt.xlabel("Days")
    plt.ylabel("Count")

    # Set x-axis ticks
    tick_indices = list(range(0, len(dates), 5))
    tick_labels = [short_dates[i] for i in tick_indices]
    plt.xticks(tick_indices, tick_labels)

    plt.show()
    print()

    # Print summary statistics
    print("=" * 60)
    print("Summary Statistics")
    print("=" * 60)
    print(f"  Total Pageviews:   {sum(pageviews):>12,}")
    print(f"  Total Visitors:    {sum(visitors):>12,}")
    print(f"  Avg Pageviews/day: {sum(pageviews) // len(pageviews):>12,}")
    print(f"  Avg Visitors/day:  {sum(visitors) // len(visitors):>12,}")
    print(f"  Peak Pageviews:    {max(pageviews):>12,} ({dates[pageviews.index(max(pageviews))]})")
    print(f"  Peak Visitors:     {max(visitors):>12,} ({dates[visitors.index(max(visitors))]})")
    print("=" * 60)


if __name__ == "__main__":
    main()
