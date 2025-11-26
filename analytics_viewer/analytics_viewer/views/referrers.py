"""Referrers view showing traffic sources."""

import gi
import logging

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw

logger = logging.getLogger(__name__)


class ReferrersView(Gtk.ScrolledWindow):
    """Referrers view showing traffic sources."""

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

        # Total referrers card
        self.total_card = self.create_stat_card(
            "Total Referrers", "0", "network-workgroup-symbolic"
        )
        self.stats_box.append(self.total_card)

        # Direct traffic card
        self.direct_card = self.create_stat_card(
            "Direct Traffic", "0", "user-home-symbolic"
        )
        self.stats_box.append(self.direct_card)

        # External referrers card
        self.external_card = self.create_stat_card(
            "External", "0", "emblem-shared-symbolic"
        )
        self.stats_box.append(self.external_card)

        self.main_box.append(self.stats_box)

        # Referrers list
        referrers_card = Adw.Clamp()
        referrers_card.set_maximum_size(1200)

        referrers_group = Adw.PreferencesGroup()
        referrers_group.set_title("Top Referrers")
        referrers_group.set_description("Websites sending traffic to your site")

        self.referrers_list = Gtk.ListBox()
        self.referrers_list.add_css_class("boxed-list")
        referrers_group.add(self.referrers_list)

        referrers_card.set_child(referrers_group)
        self.main_box.append(referrers_card)

        # Clamp container
        clamp = Adw.Clamp()
        clamp.set_child(self.main_box)

        self.set_child(clamp)

    def create_stat_card(self, title, value, icon_name):
        """Create a statistics card."""
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        card.add_css_class("card")

        # Content box
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.set_spacing(12)

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

        content.append(header)

        # Value
        value_label = Gtk.Label(label=value)
        value_label.add_css_class("title-1")
        value_label.set_halign(Gtk.Align.START)
        value_label.set_margin_start(16)
        value_label.set_margin_end(16)
        value_label.set_margin_bottom(16)
        content.append(value_label)

        card.append(content)
        card.value_label = value_label

        return card

    def load_data(self, client, hostname, start_date, end_date):
        """Load referrers data."""
        try:
            # Get referrers
            stats = client.stats.get(
                hostname,
                start=start_date,
                end=end_date,
                fields=["pageviews", "referrers"],
            )

            referrers = stats.get("referrers", [])

            # Calculate stats
            total_referrers = len(referrers)
            direct_count = 0
            external_count = 0

            for ref in referrers:
                value = ref.get("value", "")
                if not value or value == "(direct)":
                    direct_count += ref.get("pageviews", 0)
                else:
                    external_count += ref.get("pageviews", 0)

            # Update stat cards
            self.total_card.value_label.set_text(f"{total_referrers:,}")
            self.direct_card.value_label.set_text(f"{direct_count:,}")
            self.external_card.value_label.set_text(f"{external_count:,}")

            # Update referrers list
            self.update_referrers_list(referrers)

        except Exception as e:
            logger.error(f"Error loading referrers data: {e}")

    def update_referrers_list(self, referrers):
        """Update the referrers list."""
        # Clear existing
        while (row := self.referrers_list.get_row_at_index(0)) is not None:
            self.referrers_list.remove(row)

        # Add referrers
        for i, referrer in enumerate(referrers[:20]):
            value = referrer.get("value", "(direct)")
            pageviews = referrer.get("pageviews", 0)

            row = Adw.ActionRow()
            row.set_title(value if value else "(direct)")
            row.set_subtitle(f"{pageviews:,} pageviews")

            # Add rank badge
            rank_label = Gtk.Label(label=f"#{i + 1}")
            rank_label.add_css_class("dim-label")
            row.add_prefix(rank_label)

            # Add icon based on referrer type
            if not value or value == "(direct)":
                icon = Gtk.Image.new_from_icon_name("user-home-symbolic")
            else:
                icon = Gtk.Image.new_from_icon_name("network-workgroup-symbolic")
            icon.add_css_class("dim-label")
            row.add_prefix(icon)

            self.referrers_list.append(row)
