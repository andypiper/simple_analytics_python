"""Dashboard view showing overview statistics.

Uses modern Cairo rendering with Adwaita styling for beautiful charts.
"""

import gi
from datetime import datetime

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw

# Use modern Adwaita-styled Cairo charts
from ..modern_charts import ModernHistogramChart


class DashboardView(Gtk.ScrolledWindow):
    """Main dashboard view."""

    def __init__(self):
        super().__init__()

        self.set_vexpand(True)
        self.set_hexpand(True)

        # Main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.main_box.set_margin_top(24)
        self.main_box.set_margin_bottom(24)
        self.main_box.set_margin_start(24)
        self.main_box.set_margin_end(24)
        self.main_box.set_spacing(24)

        # Stats cards container
        self.stats_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.stats_box.set_spacing(12)
        self.stats_box.set_homogeneous(True)

        # Pageviews card
        self.pageviews_card = self.create_stat_card(
            "Pageviews", "0", "view-grid-symbolic"
        )
        self.stats_box.append(self.pageviews_card)

        # Visitors card
        self.visitors_card = self.create_stat_card(
            "Visitors", "0", "system-users-symbolic"
        )
        self.stats_box.append(self.visitors_card)

        # Events card
        self.events_card = self.create_stat_card(
            "Events", "0", "emblem-system-symbolic"
        )
        self.stats_box.append(self.events_card)

        self.main_box.append(self.stats_box)

        # Chart area - no card, blends into window background
        chart_clamp = Adw.Clamp()
        chart_clamp.set_maximum_size(1200)

        # Modern chart widget (no background box)
        self.histogram_chart = ModernHistogramChart()

        chart_clamp.set_child(self.histogram_chart)
        self.main_box.append(chart_clamp)

        # Top pages list
        pages_card = Adw.Clamp()
        pages_card.set_maximum_size(1200)

        pages_group = Adw.PreferencesGroup()
        pages_group.set_title("Top Pages")

        self.pages_list = Gtk.ListBox()
        self.pages_list.add_css_class("boxed-list")
        pages_group.add(self.pages_list)

        pages_card.set_child(pages_group)
        self.main_box.append(pages_card)

        # Clamp container
        clamp = Adw.Clamp()
        clamp.set_child(self.main_box)

        self.set_child(clamp)

    def create_stat_card(self, title, value, icon_name):
        """Create a statistics card."""
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        card.add_css_class("card")
        card.set_spacing(12)

        # Header with icon
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header.set_spacing(8)
        header.set_margin_top(16)
        header.set_margin_start(16)
        header.set_margin_end(16)

        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.add_css_class("dim-label")
        header.append(icon)

        title_label = Gtk.Label(label=title)
        title_label.add_css_class("title-4")
        title_label.set_halign(Gtk.Align.START)
        title_label.set_hexpand(True)
        header.append(title_label)

        card.append(header)

        # Value
        value_label = Gtk.Label(label=value)
        value_label.add_css_class("title-1")
        value_label.set_halign(Gtk.Align.START)
        value_label.set_margin_start(16)
        value_label.set_margin_end(16)
        value_label.set_margin_bottom(16)
        card.append(value_label)

        # Store reference to value label
        card.value_label = value_label

        return card

    def load_data(self, client, hostname, start_date, end_date):
        """Load dashboard data."""
        try:
            # Get basic stats
            stats = client.stats.get(
                hostname,
                start=start_date,
                end=end_date,
                fields=["pageviews", "visitors", "pages", "histogram"]
            )

            # Update stat cards
            pageviews = stats.get("pageviews", 0)
            visitors = stats.get("visitors", 0)

            self.pageviews_card.value_label.set_text(f"{pageviews:,}")
            self.visitors_card.value_label.set_text(f"{visitors:,}")

            # Get events count
            try:
                events_stats = client.stats.get_events(
                    hostname,
                    start=start_date,
                    end=end_date
                )
                total_events = sum(
                    e.get("total", 0) for e in events_stats.get("events", [])
                )
                self.events_card.value_label.set_text(f"{total_events:,}")
            except:
                self.events_card.value_label.set_text("N/A")

            # Update histogram chart with native Cairo rendering
            histogram = stats.get("histogram", [])
            if histogram:
                # Use last 30 days
                self.histogram_chart.set_data(histogram[-30:])

            # Update pages list
            self.update_pages_list(stats.get("pages", []))

        except Exception as e:
            print(f"Error loading dashboard data: {e}")

    def update_pages_list(self, pages):
        """Update the top pages list."""
        # Clear existing
        while True:
            row = self.pages_list.get_row_at_index(0)
            if row:
                self.pages_list.remove(row)
            else:
                break

        # Add pages
        for i, page in enumerate(pages[:10]):
            path = page.get("value", "/")
            pageviews = page.get("pageviews", 0)

            row = Adw.ActionRow()
            row.set_title(path)
            row.set_subtitle(f"{pageviews:,} pageviews")

            # Add rank badge
            rank_label = Gtk.Label(label=f"#{i + 1}")
            rank_label.add_css_class("dim-label")
            row.add_prefix(rank_label)

            self.pages_list.append(row)
