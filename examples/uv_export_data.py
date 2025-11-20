#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "simple-analytics-python @ file://${PROJECT_ROOT}",
# ]
# [tool.uv]
# exclude-newer = "2025-01-01"
# ///
"""
Data export example for the Simple Analytics Python client.

Run with: uv run examples/uv_export_data.py

This example demonstrates exporting raw data from Simple Analytics
in JSON and CSV formats.

IMPORTANT: This requires authentication with API key and User ID.

Before running, set your credentials:
    export SA_API_KEY="sa_api_key_xxxx"
    export SA_USER_ID="sa_user_id_xxxx"
    export SA_HOSTNAME="your-website.com"
"""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simple_analytics import SimpleAnalyticsClient, AuthenticationError


def main():
    # Get credentials from environment
    api_key = os.environ.get("SA_API_KEY")
    user_id = os.environ.get("SA_USER_ID")
    hostname = os.environ.get("SA_HOSTNAME")

    if not api_key or not user_id:
        print("Error: Authentication required for data export")
        print()
        print("Please set these environment variables:")
        print("  export SA_API_KEY='sa_api_key_xxxx'")
        print("  export SA_USER_ID='sa_user_id_xxxx'")
        print("  export SA_HOSTNAME='your-website.com'")
        print()
        print("Get your credentials from:")
        print("  https://simpleanalytics.com/account")
        return

    if not hostname:
        print("Error: Please set SA_HOSTNAME environment variable")
        print("  export SA_HOSTNAME='your-website.com'")
        return

    # Initialize client
    client = SimpleAnalyticsClient(
        api_key=api_key,
        user_id=user_id
    )

    # Calculate date range (last 7 days)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    print(f"Exporting data for {hostname}")
    print(f"Date range: {start_date} to {end_date}")
    print("=" * 60)
    print()

    try:
        # Example 1: Export pageviews as JSON
        print("1. Exporting pageviews as JSON...")
        data = client.export.pageviews(
            hostname,
            start=start_date,
            end=end_date,
            fields=["added_iso", "path", "country_code", "device_type", "browser_name"]
        )
        print(f"   Exported {len(data)} pageviews")

        if data:
            print("   Sample record:")
            sample = data[0]
            for key, value in sample.items():
                print(f"      {key}: {value}")
        print()

        # Example 2: Export pageviews as CSV
        print("2. Exporting pageviews as CSV...")
        csv_data = client.export.to_csv(
            hostname,
            start=start_date,
            end=end_date,
            fields=["added_iso", "path", "country_code", "device_type"]
        )
        lines = csv_data.strip().split("\n")
        print(f"   Exported {len(lines) - 1} records (plus header)")
        print(f"   Header: {lines[0]}")
        print()

        # Example 3: Export with all fields
        print("3. Exporting with detailed fields...")
        data = client.export.datapoints(
            hostname,
            start=start_date,
            end=end_date,
            fields=[
                "added_iso",
                "path",
                "query",
                "country_code",
                "device_type",
                "browser_name",
                "browser_version",
                "os_name",
                "os_version",
                "duration_seconds",
                "scrolled_percentage",
                "is_unique",
                "utm_source",
                "utm_medium",
                "utm_campaign",
                "referrer_hostname"
            ]
        )
        print(f"   Exported {len(data)} detailed records")
        print()

        # Example 4: Save to files
        print("4. Saving to files...")

        # Save JSON
        import json
        json_filename = f"export_{hostname}_{start_date}_{end_date}.json"
        with open(json_filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"   Saved JSON to: {json_filename}")

        # Save CSV
        csv_filename = f"export_{hostname}_{start_date}_{end_date}.csv"
        with open(csv_filename, "w") as f:
            f.write(csv_data)
        print(f"   Saved CSV to:  {csv_filename}")
        print()

        # Example 5: Export events (if any)
        print("5. Exporting events...")
        events = client.export.events(
            hostname,
            start=start_date,
            end=end_date
        )
        print(f"   Exported {len(events)} events")

        if events:
            # Group events by name
            event_names = {}
            for event in events:
                name = event.get("event_name", "unknown")
                event_names[name] = event_names.get(name, 0) + 1

            print("   Event breakdown:")
            for name, count in sorted(event_names.items(), key=lambda x: -x[1])[:5]:
                print(f"      {name}: {count}")
        print()

        # Summary
        print("=" * 60)
        print("Export Summary")
        print("=" * 60)
        print(f"  Hostname:    {hostname}")
        print(f"  Date range:  {start_date} to {end_date}")
        print(f"  Pageviews:   {len(data)}")
        print(f"  Events:      {len(events)}")
        print(f"  Files saved: {json_filename}, {csv_filename}")
        print("=" * 60)

    except AuthenticationError as e:
        print(f"Authentication error: {e}")
        print()
        print("Please check:")
        print("  - Your API key is correct (starts with 'sa_api_key_')")
        print("  - Your User ID is correct (starts with 'sa_user_id_')")
        print("  - You have access to the specified website")
    except Exception as e:
        print(f"Error: {e}")

    print()
    print("Done!")


if __name__ == "__main__":
    main()
