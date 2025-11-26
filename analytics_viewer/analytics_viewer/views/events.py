"""Events view showing event analytics."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib


class EventsView(Gtk.ScrolledWindow):
    """Events view."""

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

        # Event type cards
        self.type_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.type_box.set_spacing(12)
        self.type_box.set_homogeneous(True)

        self.automated_card = self.create_stat_card("Automated Events", "0")
        self.custom_card = self.create_stat_card("Custom Events", "0")
        self.total_card = self.create_stat_card("Total Events", "0")

        self.type_box.append(self.automated_card)
        self.type_box.append(self.custom_card)
        self.type_box.append(self.total_card)

        self.main_box.append(self.type_box)

        # Events list
        events_card = Adw.Clamp()
        events_card.set_maximum_size(1200)

        events_group = Adw.PreferencesGroup()
        events_group.set_title("All Events")

        self.events_list = Gtk.ListBox()
        self.events_list.add_css_class("boxed-list")
        self.events_list.set_selection_mode(Gtk.SelectionMode.NONE)
        events_group.add(self.events_list)

        events_card.set_child(events_group)
        self.main_box.append(events_card)

        # Clamp container
        clamp = Adw.Clamp()
        clamp.set_child(self.main_box)

        self.set_child(clamp)

    def create_stat_card(self, title, value):
        """Create a statistics card."""
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        card.add_css_class("card")
        card.set_spacing(12)

        # Title
        title_label = Gtk.Label(label=title)
        title_label.add_css_class("title-4")
        title_label.set_halign(Gtk.Align.START)
        title_label.set_margin_top(16)
        title_label.set_margin_start(16)
        title_label.set_margin_end(16)
        card.append(title_label)

        # Value
        value_label = Gtk.Label(label=value)
        value_label.add_css_class("title-1")
        value_label.set_halign(Gtk.Align.START)
        value_label.set_margin_start(16)
        value_label.set_margin_end(16)
        value_label.set_margin_bottom(16)
        card.append(value_label)

        # Store reference
        card.value_label = value_label

        return card

    def load_data(self, client, hostname, start_date, end_date):
        """Load events data (thread-safe)."""
        try:
            # Get events (happens in background thread)
            stats = client.stats.get_events(
                hostname,
                start=start_date,
                end=end_date
            )

            events = stats.get("events", [])

            # Categorize events
            automated_count = 0
            custom_count = 0
            total_count = 0

            for event in events:
                name = event.get("name", "")
                count = event.get("total", 0)
                total_count += count

                if name.startswith(("outbound", "click_email", "download_")):
                    automated_count += count
                else:
                    custom_count += count

            # Schedule UI updates on main thread
            GLib.idle_add(self._update_ui, automated_count, custom_count, total_count, events)

        except Exception as e:
            print(f"Error loading events data: {e}")

    def _update_ui(self, automated_count, custom_count, total_count, events):
        """Update UI with loaded data (runs on main thread)."""
        self.automated_card.value_label.set_text(f"{automated_count:,}")
        self.custom_card.value_label.set_text(f"{custom_count:,}")
        self.total_card.value_label.set_text(f"{total_count:,}")
        self.update_events_list(events)
        return False  # Don't repeat

    def update_events_list(self, events):
        """Update the events list."""
        # Clear existing rows efficiently
        while (row := self.events_list.get_row_at_index(0)) is not None:
            self.events_list.remove(row)

        if not events:
            # Show empty state
            row = Adw.ActionRow()
            row.set_title("No events found")
            row.set_subtitle("Enable automated events or add custom events to your site")
            self.events_list.append(row)
            return

        # Add events
        for event in events:
            name = event.get("name", "Unknown")
            total = event.get("total", 0)

            # Determine event type
            if name.startswith(("outbound", "click_email", "download_")):
                event_type = "Automated"
                icon_name = "emblem-ok-symbolic"
            else:
                event_type = "Custom"
                icon_name = "starred-symbolic"

            row = Adw.ActionRow()
            row.set_title(name)
            row.set_subtitle(f"{total:,} occurrences • {event_type}")
            row.set_activatable(False)

            # Add icon
            icon = Gtk.Image.new_from_icon_name(icon_name)
            icon.add_css_class("dim-label")
            row.add_prefix(icon)

            # Add count badge
            count_label = Gtk.Label(label=str(total))
            count_label.add_css_class("dim-label")
            row.add_suffix(count_label)

            self.events_list.append(row)
