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
Terminal chart example showing visitor breakdown by country.

Run with: uv run examples/uv_country_chart.py

This example fetches country statistics from Simple Analytics and displays
them as bar charts and a pie-like visualization in your terminal.

Before running, optionally set your credentials:
    export SA_API_KEY="sa_api_key_xxxx"
    export SA_USER_ID="sa_user_id_xxxx"

Note: Stats for public websites work without authentication.
"""

import os
import sys

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
    num_countries = 15

    print(f"Fetching country statistics for {hostname}...")
    print()

    # Get country statistics
    stats = client.stats.get(
        hostname,
        fields=["countries", "pageviews", "visitors"],
        limit=50  # Get more to calculate totals
    )

    if "countries" not in stats or not stats["countries"]:
        print("No country data available")
        return

    countries = stats["countries"]

    # Extract country names and pageviews
    all_names = [c.get("value", "Unknown") for c in countries]
    all_pageviews = [c.get("pageviews", 0) for c in countries]

    # Get top N for charts
    top_names = all_names[:num_countries]
    top_pageviews = all_pageviews[:num_countries]

    # Calculate "Other" for remaining countries
    other_pageviews = sum(all_pageviews[num_countries:])
    if other_pageviews > 0:
        chart_names = top_names + ["Other"]
        chart_pageviews = top_pageviews + [other_pageviews]
    else:
        chart_names = top_names
        chart_pageviews = top_pageviews

    # Reverse for horizontal bar chart (top at top)
    chart_names_rev = chart_names[::-1]
    chart_pageviews_rev = chart_pageviews[::-1]

    # Chart 1: Horizontal bar chart
    plt.clear_figure()
    plt.theme("clear")
    plt.plot_size(width=100, height=len(chart_names) + 8)

    # Color "Other" differently
    colors = ["cyan"] * len(chart_names_rev)
    if other_pageviews > 0:
        colors[0] = "gray"  # "Other" is first after reversing

    plt.bar(
        chart_names_rev,
        chart_pageviews_rev,
        orientation="horizontal",
        marker="sd",
        color=colors
    )
    plt.title(f"Pageviews by Country - {hostname}")
    plt.xlabel("Pageviews")
    plt.ylabel("Country")

    plt.show()
    print()

    # Chart 2: Simple bar chart for top 10
    plt.clear_figure()
    plt.theme("clear")
    plt.plot_size(width=100, height=20)

    top10_names = all_names[:10]
    top10_pageviews = all_pageviews[:10]

    plt.bar(top10_names, top10_pageviews, marker="sd", color="green")
    plt.title(f"Top 10 Countries by Pageviews - {hostname}")
    plt.xlabel("Country")
    plt.ylabel("Pageviews")

    plt.show()
    print()

    # Print detailed statistics
    total_pageviews = sum(all_pageviews)

    print("=" * 65)
    print(f"{'Country':<25} {'Pageviews':>12} {'Percentage':>12} {'Bar':>12}")
    print("=" * 65)

    for i, country in enumerate(countries[:num_countries]):
        name = country.get("value", "Unknown")
        pv = country.get("pageviews", 0)
        pct = (pv / total_pageviews * 100) if total_pageviews > 0 else 0

        # Create a simple bar
        bar_length = int(pct / 2)  # Scale to ~50 char max
        bar = "#" * bar_length

        print(f"{name:<25} {pv:>12,} {pct:>11.1f}% {bar}")

    if other_pageviews > 0:
        other_pct = (other_pageviews / total_pageviews * 100) if total_pageviews > 0 else 0
        bar_length = int(other_pct / 2)
        bar = "#" * bar_length
        print(f"{'Other':<25} {other_pageviews:>12,} {other_pct:>11.1f}% {bar}")

    print("=" * 65)
    print(f"{'Total':<25} {total_pageviews:>12,} {'100.0%':>12}")
    print("=" * 65)

    # Browser and device breakdown
    print()
    print("Fetching browser and device statistics...")

    stats = client.stats.get(
        hostname,
        fields=["browser_names", "device_types"],
        limit=10
    )

    if "browser_names" in stats:
        print()
        print("Top Browsers")
        print("-" * 45)
        for browser in stats["browser_names"][:5]:
            name = browser.get("value", "Unknown")
            pv = browser.get("pageviews", 0)
            print(f"  {name:<25} {pv:>12,}")

    if "device_types" in stats:
        print()
        print("Device Types")
        print("-" * 45)
        for device in stats["device_types"]:
            name = device.get("value", "Unknown").title()
            pv = device.get("pageviews", 0)
            print(f"  {name:<25} {pv:>12,}")


if __name__ == "__main__":
    main()
