#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "simple-analytics-python @ file://${PROJECT_ROOT}",
# ]
# [tool.uv]
# exclude-newer = "2025-01-01T00:00:00Z"
# ///
"""
Basic usage example for the Simple Analytics Python client.

Run with: uv run examples/basic_stats.py
    or: python examples/basic_stats.py

Before running, optionally set your credentials for authenticated endpoints:
    export SA_API_KEY="sa_api_key_xxxx"
    export SA_USER_ID="sa_user_id_xxxx"

Note: Stats for public websites (like simpleanalytics.com) work without authentication.
"""

import os

from simple_analytics import SimpleAnalyticsClient, AuthenticationError


def main():
    # Get credentials from environment (optional for public websites)
    api_key = os.environ.get("SA_API_KEY")
    user_id = os.environ.get("SA_USER_ID")

    # Use SA_HOSTNAME or default to simpleanalytics.com (it's public)
    hostname = os.environ.get("SA_HOSTNAME", "simpleanalytics.com")

    print(f"Fetching stats for {hostname}...")
    print("=" * 50)
    print()

    # Initialize client with context manager for proper cleanup
    with SimpleAnalyticsClient(api_key=api_key, user_id=user_id) as client:
        # Example 1: Get basic stats
        print("Basic Stats")
        print("-" * 30)
        stats = client.stats.get(
            hostname,
            fields=["pageviews", "visitors"]
        )
        print(f"  Pageviews: {stats.get('pageviews', 'N/A'):,}")
        print(f"  Visitors:  {stats.get('visitors', 'N/A'):,}")
        print()

        # Example 2: Get stats with specific fields
        print("Top Pages")
        print("-" * 30)
        stats = client.stats.get(
            hostname,
            fields=["pages"],
            limit=10
        )
        if "pages" in stats:
            for i, page in enumerate(stats["pages"][:10], 1):
                views = page.get("pageviews", 0)
                path = page.get("value", "Unknown")
                print(f"  {i:2}. {path[:40]:<40} {views:>8,} views")
        print()

        # Example 3: Get histogram data (last 7 days)
        print("Recent Daily Pageviews")
        print("-" * 30)
        data = client.stats.get_histogram(
            hostname,
            interval="day"
        )
        if "histogram" in data:
            for point in data["histogram"][-7:]:
                date = point.get("date", "Unknown")
                pageviews = point.get("pageviews", 0)
                visitors = point.get("visitors", 0)
                print(f"  {date}: {pageviews:>8,} pageviews, {visitors:>6,} visitors")
        print()

        # Example 4: Get referrer data
        print("Top Referrers")
        print("-" * 30)
        stats = client.stats.get(
            hostname,
            fields=["referrers"],
            limit=5
        )
        if "referrers" in stats:
            for referrer in stats["referrers"][:5]:
                source = referrer.get("value", "Direct")
                visits = referrer.get("pageviews", 0)
                print(f"  {source[:35]:<35} {visits:>8,} visits")
        print()

        # Example 5: Get country breakdown
        print("Top Countries")
        print("-" * 30)
        stats = client.stats.get(
            hostname,
            fields=["countries"],
            limit=10
        )
        if "countries" in stats:
            for country in stats["countries"][:10]:
                name = country.get("value", "Unknown")
                visits = country.get("pageviews", 0)
                print(f"  {name:<30} {visits:>8,} pageviews")
        print()

        # Example 6: Authenticated endpoints (if credentials provided)
        if api_key and user_id:
            print("Your Websites (authenticated)")
            print("-" * 30)
            try:
                response = client.admin.list_websites()
                # Handle different response formats
                if isinstance(response, list):
                    websites = response
                elif isinstance(response, dict):
                    websites = response.get("websites", [])
                else:
                    websites = []

                if websites:
                    for site in websites[:5]:
                        if isinstance(site, dict):
                            name = site.get("hostname", "Unknown")
                            tz = site.get("timezone", "UTC")
                            print(f"  {name} ({tz})")
                        else:
                            print(f"  {site}")
                else:
                    print("  No websites found")
            except AuthenticationError as e:
                print(f"  Auth error: {e}")
            print()

    print("=" * 50)
    print("Done!")


if __name__ == "__main__":
    main()
