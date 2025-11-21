#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "simple-analytics-python @ file://${PROJECT_ROOT}",
#     "plotext>=5.2.8",
# ]
# [tool.uv]
# exclude-newer = "2025-01-01T00:00:00Z"
# ///
"""
Terminal chart example showing pageviews histogram over time.

Run with: uv run examples/histogram_chart.py
    or: python examples/histogram_chart.py (requires plotext)

This example fetches histogram data from Simple Analytics and displays
it as a bar chart directly in your terminal using plotext.

Before running, optionally set your credentials:
    export SA_API_KEY="sa_api_key_xxxx"
    export SA_USER_ID="sa_user_id_xxxx"

Note: Stats for public websites work without authentication.
"""

import os
from datetime import datetime, timedelta

import plotext as plt
from simple_analytics import SimpleAnalyticsClient


def main():
    # Get credentials from environment (optional for public websites)
    api_key = os.environ.get("SA_API_KEY")
    user_id = os.environ.get("SA_USER_ID")

    # Use simpleanalytics.com as example (it's public)
    hostname = os.environ.get("SA_HOSTNAME", "simpleanalytics.com")

    # Calculate date range (last 30 days)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    print(f"Fetching histogram data for {hostname}...")
    print(f"Date range: {start_date} to {end_date}")
    print()

    # Initialize client with context manager for proper cleanup
    with SimpleAnalyticsClient(api_key=api_key, user_id=user_id) as client:
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

        # Safely calculate averages (avoid division by zero)
        avg_pv = sum(pageviews) // len(pageviews) if pageviews else 0
        avg_vis = sum(visitors) // len(visitors) if visitors else 0
        print(f"  Avg Pageviews/day: {avg_pv:>12,}")
        print(f"  Avg Visitors/day:  {avg_vis:>12,}")

        # Safely calculate peaks (avoid max() on empty list)
        if pageviews:
            max_pv = max(pageviews)
            print(f"  Peak Pageviews:    {max_pv:>12,} ({dates[pageviews.index(max_pv)]})")
        if visitors:
            max_vis = max(visitors)
            print(f"  Peak Visitors:     {max_vis:>12,} ({dates[visitors.index(max_vis)]})")
        print("=" * 60)


if __name__ == "__main__":
    main()
