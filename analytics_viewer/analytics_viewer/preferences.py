"""Preferences dialog."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject


class PreferencesDialog(Adw.PreferencesWindow):
    """Preferences dialog for managing credentials."""

    __gsignals__ = {
        "credentials-updated": (
            GObject.SignalFlags.RUN_FIRST,
            None,
            (str, str, str),
        )
    }

    def __init__(self, parent, api_key="", user_id="", hostname=""):
        super().__init__()

        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_title("Preferences")

        # Create preferences page
        page = Adw.PreferencesPage()
        page.set_title("API Credentials")
        page.set_icon_name("dialog-password-symbolic")

        # Create group
        group = Adw.PreferencesGroup()
        group.set_title("Simple Analytics API")
        group.set_description(
            "Enter your API credentials from https://simpleanalytics.com/account"
        )

        # API Key entry
        self.api_key_row = Adw.PasswordEntryRow()
        self.api_key_row.set_title("API Key")
        self.api_key_row.set_text(api_key)
        group.add(self.api_key_row)

        # User ID entry
        self.user_id_row = Adw.PasswordEntryRow()
        self.user_id_row.set_title("User ID")
        self.user_id_row.set_text(user_id)
        group.add(self.user_id_row)

        # Hostname entry
        self.hostname_row = Adw.EntryRow()
        self.hostname_row.set_title("Default Hostname")
        self.hostname_row.set_text(hostname)
        group.add(self.hostname_row)

        # Add save button
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_margin_top(20)
        button_box.set_margin_bottom(20)
        button_box.set_spacing(12)

        save_button = Gtk.Button(label="Save Credentials")
        save_button.add_css_class("suggested-action")
        save_button.add_css_class("pill")
        save_button.connect("clicked", self.on_save_clicked)

        button_box.append(save_button)

        group.add(button_box)

        page.add(group)
        self.add(page)

    def on_save_clicked(self, button):
        """Handle save button click."""
        api_key = self.api_key_row.get_text()
        user_id = self.user_id_row.get_text()
        hostname = self.hostname_row.get_text()

        self.emit("credentials-updated", api_key, user_id, hostname)
        self.close()


# Register signal
GObject.signal_new(
    "credentials-updated",
    PreferencesDialog,
    GObject.SignalFlags.RUN_FIRST,
    None,
    (str, str, str),
)
