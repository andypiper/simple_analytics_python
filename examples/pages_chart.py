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
Terminal chart example showing top pages as a horizontal bar chart.

Run with: uv run examples/pages_chart.py
    or: python examples/pages_chart.py (requires plotext)

This example fetches page statistics from Simple Analytics and displays
them as a horizontal bar chart in your terminal.

Before running, optionally set your credentials:
    export SA_API_KEY="sa_api_key_xxxx"
    export SA_USER_ID="sa_user_id_xxxx"

Note: Stats for public websites work without authentication.
"""

import os

import plotext as plt
from simple_analytics import SimpleAnalyticsClient


def main():
    # Get credentials from environment (optional for public websites)
    api_key = os.environ.get("SA_API_KEY")
    user_id = os.environ.get("SA_USER_ID")

    # Use simpleanalytics.com as example (it's public)
    hostname = os.environ.get("SA_HOSTNAME", "simpleanalytics.com")
    num_pages = 15

    print(f"Fetching top pages for {hostname}...")
    print()

    # Initialize client with context manager for proper cleanup
    with SimpleAnalyticsClient(api_key=api_key, user_id=user_id) as client:
        # Get page statistics
        stats = client.stats.get(
            hostname,
            fields=["pages", "pageviews", "visitors"],
            limit=num_pages
        )

        if "pages" not in stats or not stats["pages"]:
            print("No page data available")
            return

        pages = stats["pages"][:num_pages]

        # Extract page paths and pageviews
        # Truncate long paths for display
        max_label_length = 35
        labels = []
        for page in pages:
            path = page.get("value", "/")
            if len(path) > max_label_length:
                path = "..." + path[-(max_label_length - 3):]
            labels.append(path)

        pageviews = [page.get("pageviews", 0) for page in pages]
        visitors = [page.get("visitors", 0) for page in pages]

        # Reverse for horizontal bar chart (top at top)
        labels = labels[::-1]
        pageviews = pageviews[::-1]
        visitors = visitors[::-1]

        # Chart 1: Pageviews horizontal bar chart
        plt.clear_figure()
        plt.theme("clear")
        plt.plot_size(width=100, height=num_pages + 8)

        plt.bar(labels, pageviews, orientation="horizontal", marker="sd", color="cyan")
        plt.title(f"Top {num_pages} Pages by Pageviews - {hostname}")
        plt.xlabel("Pageviews")
        plt.ylabel("Page")

        plt.show()
        print()

        # Chart 2: Visitors horizontal bar chart
        plt.clear_figure()
        plt.theme("clear")
        plt.plot_size(width=100, height=num_pages + 8)

        plt.bar(labels, visitors, orientation="horizontal", marker="sd", color="green")
        plt.title(f"Top {num_pages} Pages by Visitors - {hostname}")
        plt.xlabel("Visitors")
        plt.ylabel("Page")

        plt.show()
        print()

        # Print detailed table
        print("=" * 75)
        print(f"{'Page':<40} {'Pageviews':>12} {'Visitors':>10} {'Views/Vis':>10}")
        print("=" * 75)

        # Re-reverse for table display (top pages first)
        for page in stats["pages"][:num_pages]:
            path = page.get("value", "/")
            if len(path) > 38:
                path = path[:35] + "..."
            pv = page.get("pageviews", 0)
            vis = page.get("visitors", 0)
            ratio = pv / vis if vis > 0 else 0
            print(f"{path:<40} {pv:>12,} {vis:>10,} {ratio:>10.2f}")

        print("=" * 75)
        print(f"{'Total':<40} {stats.get('pageviews', 0):>12,} {stats.get('visitors', 0):>10,}")
        print("=" * 75)


if __name__ == "__main__":
    main()
