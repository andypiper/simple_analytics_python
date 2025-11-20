#!/usr/bin/env python3
"""
Basic usage examples for the Simple Analytics Python client.

Before running, set your credentials:
    export SA_API_KEY="sa_api_key_xxxx"
    export SA_USER_ID="sa_user_id_xxxx"
"""

import os
from simple_analytics import SimpleAnalyticsClient


def main():
    # Get credentials from environment
    api_key = os.environ.get("SA_API_KEY")
    user_id = os.environ.get("SA_USER_ID")

    # Initialize client
    client = SimpleAnalyticsClient(
        api_key=api_key,
        user_id=user_id
    )

    # Example 1: Get basic stats (works for public websites without auth)
    print("=== Basic Stats ===")
    stats = client.stats.get("simpleanalytics.com")
    print(f"Pageviews: {stats.get('pageviews')}")
    print(f"Visitors: {stats.get('visitors')}")
    print()

    # Example 2: Get stats with specific fields
    print("=== Stats with Specific Fields ===")
    stats = client.stats.get(
        "simpleanalytics.com",
        fields=["pageviews", "visitors", "pages"],
        limit=5
    )
    print(f"Pageviews: {stats.get('pageviews')}")
    if "pages" in stats:
        print("Top pages:")
        for page in stats["pages"][:5]:
            print(f"  {page['value']}: {page['pageviews']} views")
    print()

    # Example 3: Get histogram data
    print("=== Histogram Data ===")
    data = client.stats.get_histogram(
        "simpleanalytics.com",
        interval="day"
    )
    if "histogram" in data:
        print("Recent daily data:")
        for point in data["histogram"][-5:]:
            print(f"  {point['date']}: {point['pageviews']} pageviews")
    print()

    # Example 4: Get events (if you have auth configured)
    if api_key:
        print("=== Events ===")
        events = client.stats.get_events("simpleanalytics.com")
        if "events" in events:
            for event in events["events"][:5]:
                print(f"  {event['name']}: {event['total']}")
        print()

        # Example 5: List websites (requires auth)
        print("=== Your Websites ===")
        try:
            websites = client.admin.list_websites()
            for site in websites:
                print(f"  {site.get('hostname')} ({site.get('timezone', 'UTC')})")
        except Exception as e:
            print(f"  Could not list websites: {e}")

    print("\nDone!")


if __name__ == "__main__":
    main()
