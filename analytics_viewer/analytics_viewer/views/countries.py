"""Countries view showing geographic analytics."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw


def country_code_to_flag(country_code: str) -> str:
    """
    Convert ISO 3166-1 alpha-2 country code to flag emoji.

    Uses Unicode Regional Indicator Symbols to generate flag emojis
    for any country code. Works with all valid ISO country codes.

    Args:
        country_code: Two-letter ISO country code (e.g., "US", "GB", "DE")

    Returns:
        Flag emoji string (e.g., "🇺🇸") or globe emoji if invalid

    Example:
        >>> country_code_to_flag("US")
        '🇺🇸'
        >>> country_code_to_flag("JP")
        '🇯🇵'
    """
    if not country_code or len(country_code) != 2:
        return "🌍"

    # Convert to uppercase
    country_code = country_code.upper()

    # Regional Indicator Symbol Letters start at U+1F1E6 (🇦)
    # Each letter maps to: base (0x1F1E6) + letter_offset
    try:
        flag_chars = [
            chr(0x1F1E6 + ord(char) - ord('A'))
            for char in country_code
        ]
        return ''.join(flag_chars)
    except (ValueError, TypeError):
        return "🌍"


class CountriesView(Gtk.ScrolledWindow):
    """Countries view with devices information."""

    def __init__(self):
        super().__init__()

        self.set_vexpand(True)
        self.set_hexpand(True)

        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)
        main_box.set_spacing(24)

        # Countries list
        countries_card = Adw.Clamp()
        countries_card.set_maximum_size(1200)

        countries_group = Adw.PreferencesGroup()
        countries_group.set_title("Countries")
        countries_group.set_description("Sorted by pageviews")

        self.countries_list = Gtk.ListBox()
        self.countries_list.add_css_class("boxed-list")
        self.countries_list.set_selection_mode(Gtk.SelectionMode.NONE)
        countries_group.add(self.countries_list)

        countries_card.set_child(countries_group)
        main_box.append(countries_card)

        # Devices expandable row
        devices_card = Adw.Clamp()
        devices_card.set_maximum_size(1200)

        devices_group = Adw.PreferencesGroup()
        devices_group.set_title("Devices and Browsers")
        devices_group.set_description("Device types, browsers, and operating systems")

        # Device types expander
        self.device_types_expander = Adw.ExpanderRow()
        self.device_types_expander.set_title("Device Types")
        self.device_types_expander.set_subtitle("Desktop, mobile, and tablet")
        self.device_types_expander.set_icon_name("computer-symbolic")
        devices_group.add(self.device_types_expander)

        # Browsers expander
        self.browsers_expander = Adw.ExpanderRow()
        self.browsers_expander.set_title("Browsers")
        self.browsers_expander.set_subtitle("Top web browsers")
        self.browsers_expander.set_icon_name("web-browser-symbolic")
        devices_group.add(self.browsers_expander)

        # Operating systems expander
        self.os_expander = Adw.ExpanderRow()
        self.os_expander.set_title("Operating Systems")
        self.os_expander.set_subtitle("Desktop and mobile OS")
        self.os_expander.set_icon_name("system-run-symbolic")
        devices_group.add(self.os_expander)

        devices_card.set_child(devices_group)
        main_box.append(devices_card)

        # Track child rows for clearing
        self.device_type_rows = []
        self.browser_rows = []
        self.os_rows = []

        # Clamp container
        clamp = Adw.Clamp()
        clamp.set_child(main_box)

        self.set_child(clamp)

    def load_data(self, client, hostname, start_date, end_date):
        """Load countries and devices data."""
        try:
            # Get countries data
            stats = client.stats.get(
                hostname,
                start=start_date,
                end=end_date,
                fields=["countries", "device_types", "browser_names", "os_names"],
                limit=100
            )

            countries = stats.get("countries", [])
            total_pageviews = sum(c.get("pageviews", 0) for c in countries)
            self.update_countries_list(countries, total_pageviews)

            # Load devices data
            device_types = stats.get("device_types", [])
            browsers = stats.get("browser_names", [])
            operating_systems = stats.get("os_names", [])

            self.update_device_types(device_types)
            self.update_browsers(browsers)
            self.update_os(operating_systems)

        except Exception as e:
            print(f"Error loading data: {e}")

    def update_countries_list(self, countries, total_pageviews):
        """Update the countries list."""
        # Clear existing
        while True:
            row = self.countries_list.get_row_at_index(0)
            if row:
                self.countries_list.remove(row)
            else:
                break

        if not countries:
            row = Adw.ActionRow()
            row.set_title("No country data found")
            self.countries_list.append(row)
            return

        # Add countries
        for i, country in enumerate(countries):
            code = country.get("value", "Unknown")
            pageviews = country.get("pageviews", 0)
            visitors = country.get("visitors", 0)

            # Calculate percentage
            percentage = (pageviews / total_pageviews * 100) if total_pageviews > 0 else 0

            row = Adw.ActionRow()

            # Generate flag emoji dynamically from country code
            flag = country_code_to_flag(code)
            row.set_title(f"{flag}  {code}")
            row.set_subtitle(
                f"{pageviews:,} pageviews • {visitors:,} visitors • {percentage:.1f}%"
            )

            # Add rank
            rank_label = Gtk.Label(label=f"#{i + 1}")
            rank_label.add_css_class("dim-label")
            rank_label.set_width_chars(4)
            row.add_prefix(rank_label)

            # Add progress bar
            progress = Gtk.ProgressBar()
            progress.set_fraction(percentage / 100)
            progress.set_valign(Gtk.Align.CENTER)
            progress.set_size_request(100, -1)
            row.add_suffix(progress)

            self.countries_list.append(row)

    def update_device_types(self, device_types):
        """Update device types expander."""
        # Clear existing rows
        for row in self.device_type_rows:
            self.device_types_expander.remove(row)
        self.device_type_rows.clear()

        if not device_types:
            return

        total = sum(dt.get("pageviews", 0) for dt in device_types)

        for device_type in device_types:
            value = device_type.get("value", "Unknown")
            pageviews = device_type.get("pageviews", 0)
            percentage = (pageviews / total * 100) if total > 0 else 0

            row = Adw.ActionRow()
            row.set_title(value)
            row.set_subtitle(f"{pageviews:,} pageviews ({percentage:.1f}%)")

            # Add progress bar
            progress = Gtk.ProgressBar()
            progress.set_fraction(percentage / 100)
            progress.set_valign(Gtk.Align.CENTER)
            progress.set_size_request(100, -1)
            row.add_suffix(progress)

            self.device_types_expander.add_row(row)
            self.device_type_rows.append(row)

    def update_browsers(self, browsers):
        """Update browsers expander."""
        # Clear existing rows
        for row in self.browser_rows:
            self.browsers_expander.remove(row)
        self.browser_rows.clear()

        if not browsers:
            return

        total = sum(b.get("pageviews", 0) for b in browsers)

        for i, browser in enumerate(browsers[:10]):
            value = browser.get("value", "Unknown")
            pageviews = browser.get("pageviews", 0)
            percentage = (pageviews / total * 100) if total > 0 else 0

            row = Adw.ActionRow()
            row.set_title(f"#{i + 1} {value}")
            row.set_subtitle(f"{pageviews:,} pageviews ({percentage:.1f}%)")

            # Add progress bar
            progress = Gtk.ProgressBar()
            progress.set_fraction(percentage / 100)
            progress.set_valign(Gtk.Align.CENTER)
            progress.set_size_request(100, -1)
            row.add_suffix(progress)

            self.browsers_expander.add_row(row)
            self.browser_rows.append(row)

    def update_os(self, operating_systems):
        """Update operating systems expander."""
        # Clear existing rows
        for row in self.os_rows:
            self.os_expander.remove(row)
        self.os_rows.clear()

        if not operating_systems:
            return

        total = sum(os.get("pageviews", 0) for os in operating_systems)

        for i, os_entry in enumerate(operating_systems[:10]):
            value = os_entry.get("value", "Unknown")
            pageviews = os_entry.get("pageviews", 0)
            percentage = (pageviews / total * 100) if total > 0 else 0

            row = Adw.ActionRow()
            row.set_title(f"#{i + 1} {value}")
            row.set_subtitle(f"{pageviews:,} pageviews ({percentage:.1f}%)")

            # Add progress bar
            progress = Gtk.ProgressBar()
            progress.set_fraction(percentage / 100)
            progress.set_valign(Gtk.Align.CENTER)
            progress.set_size_request(100, -1)
            row.add_suffix(progress)

            self.os_expander.add_row(row)
            self.os_rows.append(row)
