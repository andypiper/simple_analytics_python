"""Countries view showing geographic analytics."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw


# Country code to flag emoji mapping
COUNTRY_FLAGS = {
    "US": "🇺🇸", "GB": "🇬🇧", "DE": "🇩🇪", "FR": "🇫🇷", "NL": "🇳🇱",
    "CA": "🇨🇦", "AU": "🇦🇺", "ES": "🇪🇸", "IT": "🇮🇹", "BR": "🇧🇷",
    "IN": "🇮🇳", "JP": "🇯🇵", "CN": "🇨🇳", "KR": "🇰🇷", "MX": "🇲🇽",
    "SE": "🇸🇪", "NO": "🇳🇴", "DK": "🇩🇰", "FI": "🇫🇮", "PL": "🇵🇱",
    "BE": "🇧🇪", "CH": "🇨🇭", "AT": "🇦🇹", "PT": "🇵🇹", "IE": "🇮🇪",
}


class CountriesView(Gtk.ScrolledWindow):
    """Countries view."""

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

        # Clamp container
        clamp = Adw.Clamp()
        clamp.set_child(main_box)

        self.set_child(clamp)

    def load_data(self, client, hostname, start_date, end_date):
        """Load countries data."""
        try:
            stats = client.stats.get(
                hostname,
                start=start_date,
                end=end_date,
                fields=["countries"],
                limit=100
            )

            countries = stats.get("countries", [])
            total_pageviews = sum(c.get("pageviews", 0) for c in countries)

            self.update_countries_list(countries, total_pageviews)

        except Exception as e:
            print(f"Error loading countries data: {e}")

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

            # Add flag emoji if available
            flag = COUNTRY_FLAGS.get(code, "🌍")
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
