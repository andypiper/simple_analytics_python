"""Dashboard view showing overview statistics."""

import gi
from datetime import datetime

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw


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

        # Chart placeholder
        chart_card = Adw.Clamp()
        chart_card.set_maximum_size(1200)

        chart_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        chart_box.add_css_class("card")
        chart_box.set_spacing(12)

        chart_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        chart_header.set_margin_top(16)
        chart_header.set_margin_start(16)
        chart_header.set_margin_end(16)

        chart_title = Gtk.Label(label="Pageviews Over Time")
        chart_title.add_css_class("title-3")
        chart_title.set_halign(Gtk.Align.START)
        chart_header.append(chart_title)

        chart_box.append(chart_header)

        # Chart area (will show ASCII art chart)
        self.chart_text = Gtk.TextView()
        self.chart_text.set_editable(False)
        self.chart_text.set_monospace(True)
        self.chart_text.set_margin_start(16)
        self.chart_text.set_margin_end(16)
        self.chart_text.set_margin_bottom(16)
        self.chart_text.set_wrap_mode(Gtk.WrapMode.NONE)

        chart_scroll = Gtk.ScrolledWindow()
        chart_scroll.set_min_content_height(300)
        chart_scroll.set_child(self.chart_text)

        chart_box.append(chart_scroll)

        chart_card.set_child(chart_box)
        self.main_box.append(chart_card)

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

            # Draw histogram chart
            self.draw_histogram(stats.get("histogram", []))

            # Update pages list
            self.update_pages_list(stats.get("pages", []))

        except Exception as e:
            print(f"Error loading dashboard data: {e}")

    def draw_histogram(self, histogram):
        """Draw an ASCII histogram."""
        if not histogram:
            buffer = self.chart_text.get_buffer()
            buffer.set_text("No data available")
            return

        # Get last 30 days
        recent = histogram[-30:]

        # Find max value for scaling
        max_value = max(p.get("pageviews", 0) for p in recent)

        if max_value == 0:
            buffer = self.chart_text.get_buffer()
            buffer.set_text("No data available")
            return

        # Build chart
        lines = []
        lines.append("Pageviews per day (last 30 days)")
        lines.append("")

        for point in recent:
            date = point.get("date", "")
            pageviews = point.get("pageviews", 0)

            # Scale bar
            bar_length = int((pageviews / max_value) * 50)
            bar = "█" * bar_length

            lines.append(f"{date}  {pageviews:>6,}  {bar}")

        buffer = self.chart_text.get_buffer()
        buffer.set_text("\n".join(lines))

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
