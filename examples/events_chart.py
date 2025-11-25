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
Terminal chart example showing event statistics and tracking.

Run with: uv run examples/events_chart.py

This example fetches event data from Simple Analytics and displays
it as charts in your terminal, including both custom events and
automated events (outbound links, email clicks, downloads).

Before running, set your credentials:
    export SA_API_KEY="sa_api_key_xxxx"
    export SA_USER_ID="sa_user_id_xxxx"
    export SA_HOSTNAME="your-website.com"

Note: Event data typically requires authentication.
"""

import os
from datetime import datetime, timedelta

import plotext as plt
from simple_analytics import SimpleAnalyticsClient, AuthenticationError


def main():
    # Get credentials from environment
    api_key = os.environ.get("SA_API_KEY")
    user_id = os.environ.get("SA_USER_ID")
    hostname = os.environ.get("SA_HOSTNAME", "simpleanalytics.com")

    if not api_key or not user_id:
        print("Error: Authentication required for event data")
        print()
        print("Please set these environment variables:")
        print("  export SA_API_KEY='sa_api_key_xxxx'")
        print("  export SA_USER_ID='sa_user_id_xxxx'")
        print("  export SA_HOSTNAME='your-website.com'")
        print()
        print("Get your credentials from:")
        print("  https://simpleanalytics.com/account")
        return

    # Initialize client
    with SimpleAnalyticsClient(api_key=api_key, user_id=user_id) as client:
        try:
            print(f"Fetching event data for {hostname}...")
            print()

            # Calculate date range (last 30 days)
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

            # Get all events
            stats = client.stats.get_events(
                hostname,
                start=start_date,
                end=end_date
            )

            if "events" not in stats or not stats["events"]:
                print("No event data available for this website")
                print()
                print("To track events:")
                print("  1. Add the Simple Analytics script to your site")
                print("  2. Enable automated events (outbound, email, downloads)")
                print("  3. Or add custom events with sa_event()")
                print()
                print("See: https://docs.simpleanalytics.com/events")
                return

            events = stats["events"]

            # Categorize events
            automated_events = []
            custom_events = []

            for event in events:
                name = event.get("name", "")
                # Automated events typically start with these prefixes
                if name.startswith(("outbound", "click_email", "download_")):
                    automated_events.append(event)
                else:
                    custom_events.append(event)

            print("Event Summary")
            print("=" * 60)
            print(f"  Date range:       {start_date} to {end_date}")
            print(f"  Total events:     {len(events)}")
            print(f"  Automated events: {len(automated_events)}")
            print(f"  Custom events:    {len(custom_events)}")
            print("=" * 60)
            print()

            # Chart 1: Top events bar chart
            if events:
                top_events = events[:20]
                names = [e.get("name", "Unknown") for e in top_events]
                totals = [e.get("total", 0) for e in top_events]

                # Reverse for horizontal bar chart
                names_rev = names[::-1]
                totals_rev = totals[::-1]

                plt.clear_figure()
                plt.theme("clear")
                plt.plot_size(width=100, height=min(len(names) + 8, 30))

                # Color automated events differently
                colors = []
                for name in names_rev:
                    if name.startswith(("outbound", "click_email", "download_")):
                        colors.append("green")
                    else:
                        colors.append("cyan")

                plt.bar(
                    names_rev,
                    totals_rev,
                    orientation="horizontal",
                    marker="sd",
                    color=colors
                )
                plt.title(f"Top Events - {hostname}")
                plt.xlabel("Event Count")
                plt.ylabel("Event Name")

                plt.show()
                print()

            # Chart 2: Event type comparison
            if automated_events or custom_events:
                plt.clear_figure()
                plt.theme("clear")
                plt.plot_size(width=80, height=15)

                labels = []
                values = []

                if automated_events:
                    labels.append("Automated")
                    values.append(sum(e.get("total", 0) for e in automated_events))

                if custom_events:
                    labels.append("Custom")
                    values.append(sum(e.get("total", 0) for e in custom_events))

                plt.bar(labels, values, marker="sd", color=["green", "cyan"])
                plt.title("Automated vs Custom Events")
                plt.xlabel("Event Type")
                plt.ylabel("Total Count")

                plt.show()
                print()

            # Detailed table
            print("Detailed Event Breakdown")
            print("=" * 80)
            print(f"{'Event Name':<40} {'Type':<12} {'Count':>10} {'Bar'}")
            print("=" * 80)

            for event in events[:25]:
                name = event.get("name", "Unknown")
                total = event.get("total", 0)

                # Determine type
                if name.startswith(("outbound", "click_email", "download_")):
                    event_type = "Automated"
                else:
                    event_type = "Custom"

                # Truncate long names
                display_name = name[:38] + "..." if len(name) > 38 else name

                # Create bar
                max_total = max(e.get("total", 0) for e in events)
                bar_length = int((total / max_total * 20)) if max_total > 0 else 0
                bar = "█" * bar_length

                print(f"{display_name:<40} {event_type:<12} {total:>10,} {bar}")

            print("=" * 80)
            print()

            # Show automated event details if present
            if automated_events:
                print("Automated Event Details")
                print("-" * 60)

                # Count by type
                outbound_count = sum(
                    e.get("total", 0) for e in automated_events
                    if e.get("name", "").startswith("outbound")
                )
                email_count = sum(
                    e.get("total", 0) for e in automated_events
                    if e.get("name", "").startswith("click_email")
                )
                download_count = sum(
                    e.get("total", 0) for e in automated_events
                    if e.get("name", "").startswith("download_")
                )

                if outbound_count:
                    print(f"  Outbound Links:  {outbound_count:>8,}")
                if email_count:
                    print(f"  Email Clicks:    {email_count:>8,}")
                if download_count:
                    print(f"  Downloads:       {download_count:>8,}")

                print()

                # Show top outbound destinations
                outbound = [e for e in automated_events if e.get("name", "").startswith("outbound")]
                if outbound:
                    print("  Top Outbound Destinations:")
                    for event in outbound[:5]:
                        name = event.get("name", "").replace("outbound_", "")
                        total = event.get("total", 0)
                        print(f"    {name:<35} {total:>8,}")
                    print()

            # Show custom event details if present
            if custom_events:
                print("Custom Event Details")
                print("-" * 60)
                for event in custom_events[:10]:
                    name = event.get("name", "Unknown")
                    total = event.get("total", 0)
                    print(f"  {name:<40} {total:>10,}")
                print()

            # Summary
            print("=" * 60)
            print("Tip: To track more events, use sa_event() in your JavaScript:")
            print("  sa_event('button_click');")
            print()
            print("Or enable automated events:")
            print("  https://docs.simpleanalytics.com/automated-events")
            print("=" * 60)

        except AuthenticationError as e:
            print(f"Authentication error: {e}")
            print()
            print("Please check your credentials")
        except Exception as e:
            print(f"Error: {e}")

    print()
    print("Done!")


if __name__ == "__main__":
    main()
