#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "simple-analytics-python @ file://${PROJECT_ROOT}",
# ]
# [tool.uv]
# exclude-newer = "2025-01-01T00:00:00Z"
# ///
"""
Event timeline example showing individual event occurrences.

Run with: uv run examples/events_timeline.py

This example exports raw event data and displays a timeline of when
events occurred, useful for understanding user behavior patterns.

Before running, set your credentials:
    export SA_API_KEY="sa_api_key_xxxx"
    export SA_USER_ID="sa_user_id_xxxx"
    export SA_HOSTNAME="your-website.com"
"""

import os
from datetime import datetime, timedelta
from collections import defaultdict

from simple_analytics import SimpleAnalyticsClient, AuthenticationError


def main():
    # Get credentials from environment
    api_key = os.environ.get("SA_API_KEY")
    user_id = os.environ.get("SA_USER_ID")
    hostname = os.environ.get("SA_HOSTNAME")

    if not api_key or not user_id or not hostname:
        print("Error: Authentication and hostname required")
        print()
        print("Please set these environment variables:")
        print("  export SA_API_KEY='sa_api_key_xxxx'")
        print("  export SA_USER_ID='sa_user_id_xxxx'")
        print("  export SA_HOSTNAME='your-website.com'")
        return

    # Initialize client
    with SimpleAnalyticsClient(api_key=api_key, user_id=user_id) as client:
        try:
            # Calculate date range (last 7 days)
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

            print(f"Fetching event timeline for {hostname}")
            print(f"Date range: {start_date} to {end_date}")
            print("=" * 70)
            print()

            # Export raw event data
            print("Fetching event data...")
            events = client.export.events(
                hostname,
                start=start_date,
                end=end_date
            )

            if not events:
                print("No events found for this date range")
                return

            print(f"Found {len(events)} events")
            print()

            # Group events by name
            events_by_name = defaultdict(list)
            for event in events:
                name = event.get("event_name", "unknown")
                events_by_name[name].append(event)

            # Show summary
            print("Event Summary")
            print("-" * 70)
            print(f"{'Event Name':<35} {'Count':>10} {'First Seen':<20}")
            print("-" * 70)

            for name, event_list in sorted(
                events_by_name.items(),
                key=lambda x: len(x[1]),
                reverse=True
            ):
                count = len(event_list)
                first_seen = event_list[0].get("added_iso", "Unknown")[:19]
                print(f"{name:<35} {count:>10} {first_seen:<20}")

            print("=" * 70)
            print()

            # Show timeline for each event type
            for name, event_list in sorted(
                events_by_name.items(),
                key=lambda x: len(x[1]),
                reverse=True
            )[:5]:  # Top 5 events
                print(f"\nTimeline: {name}")
                print("-" * 70)

                # Group by day
                daily_counts = defaultdict(int)
                for event in event_list:
                    timestamp = event.get("added_iso", "")
                    if timestamp:
                        date = timestamp[:10]
                        daily_counts[date] += 1

                # Display daily counts
                for date in sorted(daily_counts.keys()):
                    count = daily_counts[date]
                    bar = "█" * min(count, 50)  # Cap at 50 chars
                    print(f"  {date}  {count:>4}x  {bar}")

            print()

            # Show recent events with details
            print("\nRecent Events (Last 20)")
            print("=" * 70)
            print(f"{'Time':<20} {'Event':<25} {'Path':<24}")
            print("-" * 70)

            for event in events[-20:]:
                timestamp = event.get("added_iso", "Unknown")[:19]
                event_name = event.get("event_name", "unknown")[:24]
                path = event.get("path", "/")[:23]

                print(f"{timestamp:<20} {event_name:<25} {path:<24}")

            print("=" * 70)
            print()

            # Automated events analysis
            automated = [
                e for e in events
                if e.get("event_name", "").startswith(("outbound", "click_email", "download_"))
            ]

            if automated:
                print(f"\nAutomated Events: {len(automated)} / {len(events)} total")
                print("-" * 70)

                # Count by type
                outbound = [e for e in automated if e.get("event_name", "").startswith("outbound")]
                email = [e for e in automated if e.get("event_name", "").startswith("click_email")]
                downloads = [e for e in automated if e.get("event_name", "").startswith("download_")]

                if outbound:
                    print(f"  Outbound Links:  {len(outbound):>4}x")
                    # Show unique destinations
                    destinations = set(e.get("event_name", "") for e in outbound)
                    print(f"    Unique destinations: {len(destinations)}")

                if email:
                    print(f"  Email Clicks:    {len(email):>4}x")

                if downloads:
                    print(f"  Downloads:       {len(downloads):>4}x")
                    # Show file types
                    file_types = defaultdict(int)
                    for event in downloads:
                        name = event.get("event_name", "")
                        if "_" in name:
                            file_type = name.split("_")[-1]
                            file_types[file_type] += 1

                    print("    File types:")
                    for file_type, count in sorted(file_types.items(), key=lambda x: -x[1]):
                        print(f"      {file_type}: {count}x")

                print()

            # Device breakdown
            print("Device Breakdown")
            print("-" * 70)
            device_counts = defaultdict(int)
            for event in events:
                device = event.get("device_type", "unknown")
                device_counts[device] += 1

            for device, count in sorted(device_counts.items(), key=lambda x: -x[1]):
                pct = (count / len(events) * 100) if events else 0
                bar = "█" * int(pct / 2)
                print(f"  {device:<15} {count:>5}x  ({pct:>5.1f}%)  {bar}")

            print()

            # Country breakdown
            print("Country Breakdown")
            print("-" * 70)
            country_counts = defaultdict(int)
            for event in events:
                country = event.get("country_code", "unknown")
                country_counts[country] += 1

            for country, count in sorted(country_counts.items(), key=lambda x: -x[1])[:10]:
                pct = (count / len(events) * 100) if events else 0
                bar = "█" * int(pct / 2)
                print(f"  {country:<15} {count:>5}x  ({pct:>5.1f}%)  {bar}")

            print("=" * 70)

        except AuthenticationError as e:
            print(f"Authentication error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    print()
    print("Done!")


if __name__ == "__main__":
    main()
