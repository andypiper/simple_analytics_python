"""Devices view showing browser, OS, and device type breakdown."""

import gi
import logging

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw

logger = logging.getLogger(__name__)


class DevicesView(Gtk.ScrolledWindow):
    """Devices view showing browser, OS, and device type breakdown."""

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

        # Device types list
        device_types_card = Adw.Clamp()
        device_types_card.set_maximum_size(1200)

        device_types_group = Adw.PreferencesGroup()
        device_types_group.set_title("Device Types")
        device_types_group.set_description("Desktop, mobile, and tablet breakdown")

        self.device_types_list = Gtk.ListBox()
        self.device_types_list.add_css_class("boxed-list")
        device_types_group.add(self.device_types_list)

        device_types_card.set_child(device_types_group)
        self.main_box.append(device_types_card)

        # Browsers list
        browsers_card = Adw.Clamp()
        browsers_card.set_maximum_size(1200)

        browsers_group = Adw.PreferencesGroup()
        browsers_group.set_title("Browsers")
        browsers_group.set_description("Most popular web browsers")

        self.browsers_list = Gtk.ListBox()
        self.browsers_list.add_css_class("boxed-list")
        browsers_group.add(self.browsers_list)

        browsers_card.set_child(browsers_group)
        self.main_box.append(browsers_card)

        # Operating systems list
        os_card = Adw.Clamp()
        os_card.set_maximum_size(1200)

        os_group = Adw.PreferencesGroup()
        os_group.set_title("Operating Systems")
        os_group.set_description("Desktop and mobile operating systems")

        self.os_list = Gtk.ListBox()
        self.os_list.add_css_class("boxed-list")
        os_group.add(self.os_list)

        os_card.set_child(os_group)
        self.main_box.append(os_card)

        # Clamp container
        clamp = Adw.Clamp()
        clamp.set_child(self.main_box)

        self.set_child(clamp)

    def get_device_icon(self, device_type):
        """Get icon name for device type."""
        device_type_lower = device_type.lower()
        if "mobile" in device_type_lower or "phone" in device_type_lower:
            return "phone-symbolic"
        elif "tablet" in device_type_lower:
            return "tablet-symbolic"
        elif "desktop" in device_type_lower:
            return "computer-symbolic"
        else:
            return "computer-symbolic"

    def get_browser_icon(self, browser_name):
        """Get icon name for browser."""
        browser_lower = browser_name.lower()
        if "firefox" in browser_lower:
            return "web-browser-symbolic"
        elif "chrome" in browser_lower or "chromium" in browser_lower:
            return "web-browser-symbolic"
        elif "safari" in browser_lower:
            return "web-browser-symbolic"
        elif "edge" in browser_lower:
            return "web-browser-symbolic"
        else:
            return "web-browser-symbolic"

    def get_os_icon(self, os_name):
        """Get icon name for operating system."""
        os_lower = os_name.lower()
        if "linux" in os_lower:
            return "computer-symbolic"
        elif "windows" in os_lower:
            return "computer-symbolic"
        elif "mac" in os_lower or "ios" in os_lower:
            return "computer-symbolic"
        elif "android" in os_lower:
            return "phone-symbolic"
        else:
            return "computer-symbolic"

    def load_data(self, client, hostname, start_date, end_date):
        """Load devices data."""
        try:
            # Get device, browser, and OS stats
            stats = client.stats.get(
                hostname,
                start=start_date,
                end=end_date,
                fields=["device_types", "browser_names", "os_names"],
            )

            device_types = stats.get("device_types", [])
            browsers = stats.get("browser_names", [])
            operating_systems = stats.get("os_names", [])

            # Update lists
            self.update_device_types_list(device_types)
            self.update_browsers_list(browsers)
            self.update_os_list(operating_systems)

        except Exception as e:
            logger.error(f"Error loading devices data: {e}")

    def update_device_types_list(self, device_types):
        """Update the device types list."""
        # Clear existing
        while (row := self.device_types_list.get_row_at_index(0)) is not None:
            self.device_types_list.remove(row)

        # Calculate total for percentages
        total = sum(dt.get("pageviews", 0) for dt in device_types)

        # Add device types
        for device_type in device_types:
            value = device_type.get("value", "Unknown")
            pageviews = device_type.get("pageviews", 0)
            percentage = (pageviews / total * 100) if total > 0 else 0

            row = Adw.ActionRow()
            row.set_title(value)
            row.set_subtitle(f"{pageviews:,} pageviews ({percentage:.1f}%)")

            # Add icon
            icon = Gtk.Image.new_from_icon_name(self.get_device_icon(value))
            icon.add_css_class("dim-label")
            row.add_prefix(icon)

            self.device_types_list.append(row)

    def update_browsers_list(self, browsers):
        """Update the browsers list."""
        # Clear existing
        while (row := self.browsers_list.get_row_at_index(0)) is not None:
            self.browsers_list.remove(row)

        # Calculate total for percentages
        total = sum(b.get("pageviews", 0) for b in browsers)

        # Add browsers
        for i, browser in enumerate(browsers[:15]):
            value = browser.get("value", "Unknown")
            pageviews = browser.get("pageviews", 0)
            percentage = (pageviews / total * 100) if total > 0 else 0

            row = Adw.ActionRow()
            row.set_title(value)
            row.set_subtitle(f"{pageviews:,} pageviews ({percentage:.1f}%)")

            # Add rank badge
            rank_label = Gtk.Label(label=f"#{i + 1}")
            rank_label.add_css_class("dim-label")
            row.add_prefix(rank_label)

            # Add icon
            icon = Gtk.Image.new_from_icon_name(self.get_browser_icon(value))
            icon.add_css_class("dim-label")
            row.add_prefix(icon)

            self.browsers_list.append(row)

    def update_os_list(self, operating_systems):
        """Update the operating systems list."""
        # Clear existing
        while (row := self.os_list.get_row_at_index(0)) is not None:
            self.os_list.remove(row)

        # Calculate total for percentages
        total = sum(os.get("pageviews", 0) for os in operating_systems)

        # Add operating systems
        for i, os_entry in enumerate(operating_systems[:15]):
            value = os_entry.get("value", "Unknown")
            pageviews = os_entry.get("pageviews", 0)
            percentage = (pageviews / total * 100) if total > 0 else 0

            row = Adw.ActionRow()
            row.set_title(value)
            row.set_subtitle(f"{pageviews:,} pageviews ({percentage:.1f}%)")

            # Add rank badge
            rank_label = Gtk.Label(label=f"#{i + 1}")
            rank_label.add_css_class("dim-label")
            row.add_prefix(rank_label)

            # Add icon
            icon = Gtk.Image.new_from_icon_name(self.get_os_icon(value))
            icon.add_css_class("dim-label")
            row.add_prefix(icon)

            self.os_list.append(row)
