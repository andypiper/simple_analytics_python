#!/usr/bin/env python3
"""
Data export examples for the Simple Analytics Python client.

Before running, set your credentials:
    export SA_API_KEY="sa_api_key_xxxx"
    export SA_USER_ID="sa_user_id_xxxx"
"""

import os
from datetime import datetime, timedelta
from simple_analytics import SimpleAnalyticsClient, AuthenticationError


def main():
    # Get credentials from environment
    api_key = os.environ.get("SA_API_KEY")
    user_id = os.environ.get("SA_USER_ID")

    if not api_key or not user_id:
        print("Error: Please set SA_API_KEY and SA_USER_ID environment variables")
        print("  export SA_API_KEY='sa_api_key_xxxx'")
        print("  export SA_USER_ID='sa_user_id_xxxx'")
        return

    # Initialize client
    client = SimpleAnalyticsClient(
        api_key=api_key,
        user_id=user_id
    )

    # Calculate date range (last 7 days)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    hostname = "example.com"  # Replace with your website

    try:
        # Example 1: Export as JSON
        print("=== Export as JSON ===")
        data = client.export.datapoints(
            hostname,
            start=start_date,
            end=end_date,
            fields=["added_iso", "path", "country_code", "device_type"]
        )
        print(f"Exported {len(data)} data points")
        if data:
            print("First data point:")
            print(f"  {data[0]}")
        print()

        # Example 2: Export as CSV
        print("=== Export as CSV ===")
        csv_data = client.export.to_csv(
            hostname,
            start=start_date,
            end=end_date,
            fields=["added_iso", "path", "country_code"]
        )
        lines = csv_data.strip().split("\n")
        print(f"CSV has {len(lines)} lines (including header)")
        if lines:
            print(f"Header: {lines[0]}")
        print()

        # Example 3: Export with specific fields
        print("=== Export with All Fields ===")
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
                "os_name",
                "duration_seconds",
                "scrolled_percentage",
                "utm_source",
                "utm_medium",
                "utm_campaign"
            ]
        )
        print(f"Exported {len(data)} detailed data points")
        print()

        # Example 4: Save to file
        print("=== Save to File ===")
        csv_data = client.export.to_csv(
            hostname,
            start=start_date,
            end=end_date
        )
        filename = f"export_{hostname}_{start_date}_{end_date}.csv"
        with open(filename, "w") as f:
            f.write(csv_data)
        print(f"Saved to {filename}")

    except AuthenticationError as e:
        print(f"Authentication error: {e}")
        print("Please check your API key and User ID")
    except Exception as e:
        print(f"Error: {e}")

    print("\nDone!")


if __name__ == "__main__":
    main()
