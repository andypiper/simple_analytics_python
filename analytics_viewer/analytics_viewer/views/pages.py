"""Pages view showing page analytics."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib


class PagesView(Gtk.ScrolledWindow):
    """Pages view with referrers information."""

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

        # Pages list
        pages_card = Adw.Clamp()
        pages_card.set_maximum_size(1200)

        pages_group = Adw.PreferencesGroup()
        pages_group.set_title("All Pages")
        pages_group.set_description("Sorted by pageviews")

        self.pages_list = Gtk.ListBox()
        self.pages_list.add_css_class("boxed-list")
        self.pages_list.set_selection_mode(Gtk.SelectionMode.NONE)
        pages_group.add(self.pages_list)

        pages_card.set_child(pages_group)
        main_box.append(pages_card)

        # Referrers expandable section
        referrers_card = Adw.Clamp()
        referrers_card.set_maximum_size(1200)

        referrers_group = Adw.PreferencesGroup()
        referrers_group.set_title("Traffic Sources")
        referrers_group.set_description("Where your visitors come from")

        # Referrers expander
        self.referrers_expander = Adw.ExpanderRow()
        self.referrers_expander.set_title("Top Referrers")
        self.referrers_expander.set_subtitle("External and direct traffic")
        self.referrers_expander.set_icon_name("network-workgroup-symbolic")
        referrers_group.add(self.referrers_expander)

        referrers_card.set_child(referrers_group)
        main_box.append(referrers_card)

        # Track referrer rows for clearing
        self.referrer_rows = []

        # Clamp container
        clamp = Adw.Clamp()
        clamp.set_child(main_box)

        self.set_child(clamp)

    def load_data(self, client, hostname, start_date, end_date):
        """Load pages and referrers data (thread-safe)."""
        try:
            # Get stats (happens in background thread)
            stats = client.stats.get(
                hostname,
                start=start_date,
                end=end_date,
                fields=["pages", "referrers"],
                limit=100
            )

            pages = stats.get("pages", [])
            referrers = stats.get("referrers", [])

            # Schedule UI updates on main thread
            GLib.idle_add(self._update_ui, pages, referrers)

        except Exception as e:
            print(f"Error loading pages data: {e}")

    def _update_ui(self, pages, referrers):
        """Update UI with loaded data (runs on main thread)."""
        self.update_pages_list(pages)
        self.update_referrers(referrers)
        return False  # Don't repeat

    def update_pages_list(self, pages):
        """Update the pages list."""
        # Clear existing
        while True:
            row = self.pages_list.get_row_at_index(0)
            if row:
                self.pages_list.remove(row)
            else:
                break

        if not pages:
            row = Adw.ActionRow()
            row.set_title("No pages found")
            self.pages_list.append(row)
            return

        # Add pages
        for i, page in enumerate(pages):
            path = page.get("value", "/")
            pageviews = page.get("pageviews", 0)
            visitors = page.get("visitors", 0)

            row = Adw.ActionRow()
            row.set_title(path)
            row.set_subtitle(f"{pageviews:,} pageviews • {visitors:,} visitors")

            # Add rank
            rank_label = Gtk.Label(label=f"#{i + 1}")
            rank_label.add_css_class("dim-label")
            rank_label.set_width_chars(4)
            row.add_prefix(rank_label)

            # Add chevron
            chevron = Gtk.Image.new_from_icon_name("go-next-symbolic")
            chevron.add_css_class("dim-label")
            row.add_suffix(chevron)

            self.pages_list.append(row)

    def update_referrers(self, referrers):
        """Update referrers expander."""
        # Clear existing rows
        for row in self.referrer_rows:
            self.referrers_expander.remove(row)
        self.referrer_rows.clear()

        if not referrers:
            return

        for i, referrer in enumerate(referrers[:20]):
            value = referrer.get("value", "(direct)")
            pageviews = referrer.get("pageviews", 0)

            row = Adw.ActionRow()
            row.set_title(value if value else "(direct)")
            row.set_subtitle(f"{pageviews:,} pageviews")

            # Add rank
            rank_label = Gtk.Label(label=f"#{i + 1}")
            rank_label.add_css_class("dim-label")
            rank_label.set_width_chars(4)
            row.add_prefix(rank_label)

            # Add icon based on referrer type
            if not value or value == "(direct)":
                icon = Gtk.Image.new_from_icon_name("user-home-symbolic")
            else:
                icon = Gtk.Image.new_from_icon_name("network-workgroup-symbolic")
            icon.add_css_class("dim-label")
            row.add_prefix(icon)

            self.referrers_expander.add_row(row)
            self.referrer_rows.append(row)
