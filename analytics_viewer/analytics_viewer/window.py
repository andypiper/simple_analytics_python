"""Main application window."""

import gi
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib, Gio, GObject

from simple_analytics import SimpleAnalyticsClient, AuthenticationError
from . import __version__ as app_version

from .views.dashboard import DashboardView
from .views.events import EventsView
from .views.pages import PagesView
from .views.countries import CountriesView
from .preferences import PreferencesDialog
from .shortcuts import create_shortcuts_window


class AnalyticsWindow(Adw.ApplicationWindow):
    """Main application window."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Set window properties
        self.set_default_size(1200, 800)
        self.set_size_request(360, 360)  # GNOME HIG minimum
        self.set_title("Simple Analytics Viewer")

        # Initialize GSettings for credential persistence
        # Check if schema is installed first to avoid fatal GLib error
        schema_source = Gio.SettingsSchemaSource.get_default()
        schema_id = "org.andypiper.SimpleAnalyticsViewer"
        old_schema_id = "com.simpleanalytics.viewer"

        if schema_source and schema_source.lookup(schema_id, False):
            self.settings = Gio.Settings.new(schema_id)

            # Check if we need to migrate from old schema
            if schema_source.lookup(old_schema_id, False):
                old_settings = Gio.Settings.new(old_schema_id)
                old_api_key = old_settings.get_string("api-key")
                old_user_id = old_settings.get_string("user-id")
                old_hostname = old_settings.get_string("hostname")

                # Migrate if old values exist and new values don't
                if old_api_key and not self.settings.get_string("api-key"):
                    self.settings.set_string("api-key", old_api_key)
                if old_user_id and not self.settings.get_string("user-id"):
                    self.settings.set_string("user-id", old_user_id)
                if old_hostname and not self.settings.get_string("hostname"):
                    self.settings.set_string("hostname", old_hostname)

            # Try GSettings first, fallback to env vars
            saved_api_key = self.settings.get_string("api-key")
            saved_user_id = self.settings.get_string("user-id")
            saved_hostname = self.settings.get_string("hostname")

            print(f"__init__: Read from GSettings: hostname='{saved_hostname}'")

            # Use saved values or fall back to env vars
            self.api_key = saved_api_key or os.environ.get("SA_API_KEY", "")
            self.user_id = saved_user_id or os.environ.get("SA_USER_ID", "")
            self.hostname = saved_hostname or os.environ.get("SA_HOSTNAME", "")

            print(f"__init__: Final hostname after fallback: '{self.hostname}'")

            # If we got values from env vars, save them to GSettings for next time
            if not saved_api_key and self.api_key:
                self.settings.set_string("api-key", self.api_key)
            if not saved_user_id and self.user_id:
                self.settings.set_string("user-id", self.user_id)
            if not saved_hostname and self.hostname:
                self.settings.set_string("hostname", self.hostname)

            # Force sync to ensure writes are persisted
            Gio.Settings.sync()
        else:
            # Fallback if schema not installed
            self.settings = None
            self.api_key = os.environ.get("SA_API_KEY", "")
            self.user_id = os.environ.get("SA_USER_ID", "")
            self.hostname = os.environ.get("SA_HOSTNAME", "")

            print("Note: GSettings schema not installed - credentials won't persist between sessions")
            print("See analytics_viewer/INSTALL_GSETTINGS.md for installation instructions")

        # Thread pool for API calls (limit concurrent requests)
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="api-")
        self._current_load_generation = 0
        self._load_lock = threading.Lock()

        self.client = None
        self.websites = []

        # Create UI
        self.setup_ui()

        # Setup actions and keyboard shortcuts
        self.setup_actions()

        # Defer authentication to allow window to show immediately
        # This improves perceived performance by showing UI before API calls
        if self.api_key and self.user_id:
            GLib.idle_add(self.authenticate)
        else:
            GLib.idle_add(self.show_auth_dialog)

        # Connect cleanup handler
        self.connect("close-request", self.on_close_request)

    def on_close_request(self, *args):
        """Clean up resources before closing."""
        print("Window closing - shutting down thread pool")
        self._executor.shutdown(wait=False, cancel_futures=True)
        return False  # Allow window to close

    def setup_ui(self):
        """Set up the user interface."""
        # Create header bar
        self.header_bar = Adw.HeaderBar()

        # Website dropdown with custom factory for compact display
        self.website_dropdown = Gtk.DropDown()
        self._website_changed_handler_id = self.website_dropdown.connect("notify::selected", self.on_website_changed)

        # Create factory for list items (shown in dropdown menu)
        list_factory = Gtk.SignalListItemFactory()
        list_factory.connect("setup", self._on_dropdown_list_setup)
        list_factory.connect("bind", self._on_dropdown_list_bind)
        self.website_dropdown.set_list_factory(list_factory)

        # Create factory for selected item (shown in header bar) - more compact
        selected_factory = Gtk.SignalListItemFactory()
        selected_factory.connect("setup", self._on_dropdown_selected_setup)
        selected_factory.connect("bind", self._on_dropdown_selected_bind)
        self.website_dropdown.set_factory(selected_factory)

        self.header_bar.pack_start(self.website_dropdown)

        # Refresh button
        refresh_button = Gtk.Button(icon_name="view-refresh-symbolic")
        refresh_button.set_tooltip_text("Refresh data")
        refresh_button.connect("clicked", self.on_refresh_clicked)
        self.header_bar.pack_end(refresh_button)

        # Export button
        export_button = Gtk.Button(icon_name="document-save-symbolic")
        export_button.set_tooltip_text("Export data")
        export_button.connect("clicked", self.on_export_clicked)
        self.header_bar.pack_end(export_button)

        # Menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.set_tooltip_text("Main Menu")

        # Build primary menu
        menu = Gio.Menu()

        # View submenu
        view_menu = Gio.Menu()
        view_menu.append("Dashboard", "win.view-dashboard")
        view_menu.append("Events", "win.view-events")
        view_menu.append("Pages", "win.view-pages")
        view_menu.append("Countries", "win.view-countries")
        menu.append_submenu("View", view_menu)

        # Actions section
        actions_section = Gio.Menu()
        actions_section.append("Refresh", "win.refresh")
        actions_section.append("Export…", "win.export")
        menu.append_section(None, actions_section)

        # App section
        app_section = Gio.Menu()
        app_section.append("Preferences", "app.preferences")
        app_section.append("Keyboard Shortcuts", "win.show-help-overlay")
        app_section.append("About", "app.about")
        menu.append_section(None, app_section)

        menu.append("Quit", "app.quit")

        menu_button.set_menu_model(menu)
        self.header_bar.pack_end(menu_button)

        # Create main content
        self.toolbox = Adw.ToolbarView()
        self.toolbox.add_top_bar(self.header_bar)

        # Create view switcher
        self.view_stack = Adw.ViewStack()
        self.view_stack.set_vexpand(True)

        # Create view stack first
        # (views will be added after stack creation)

        # Create views (pass view_stack to dashboard for navigation)
        self.dashboard_view = DashboardView(view_stack=self.view_stack)
        self.view_stack.add_titled(
            self.dashboard_view, "dashboard", "Dashboard"
        ).set_icon_name("view-grid-symbolic")

        self.events_view = EventsView()
        self.view_stack.add_titled(
            self.events_view, "events", "Events"
        ).set_icon_name("emblem-system-symbolic")

        self.pages_view = PagesView()
        self.view_stack.add_titled(
            self.pages_view, "pages", "Pages"
        ).set_icon_name("text-x-generic-symbolic")

        self.countries_view = CountriesView()
        self.view_stack.add_titled(
            self.countries_view, "countries", "Countries"
        ).set_icon_name("mark-location-symbolic")

        # View switcher bar
        view_switcher = Adw.ViewSwitcher()
        view_switcher.set_stack(self.view_stack)
        view_switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)

        # View switcher title (for narrow layouts)
        self.view_switcher_title = Adw.ViewSwitcherTitle()
        self.view_switcher_title.set_stack(self.view_stack)
        self.view_switcher_title.set_title("Simple Analytics")
        self.header_bar.set_title_widget(self.view_switcher_title)

        # Bottom bar for narrow mode
        self.view_switcher_bar = Adw.ViewSwitcherBar()
        self.view_switcher_bar.set_stack(self.view_stack)

        # Bind view switcher title visibility to bar reveal
        # When title is not visible (wide mode), hide the bar
        # When title is visible (narrow mode), show the bar
        self.view_switcher_title.bind_property(
            "title-visible",
            self.view_switcher_bar,
            "reveal",
            GObject.BindingFlags.SYNC_CREATE,
        )

        # Add to toolbar
        self.toolbox.set_content(self.view_stack)
        self.toolbox.add_bottom_bar(self.view_switcher_bar)

        self.set_content(self.toolbox)

    def _on_dropdown_list_setup(self, factory, list_item):
        """Set up list item widget for dropdown menu (full hostname with icon)."""
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        box.set_margin_start(8)
        box.set_margin_end(8)
        box.set_margin_top(4)
        box.set_margin_bottom(4)

        icon = Gtk.Image.new_from_icon_name("network-server-symbolic")
        box.append(icon)

        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        box.append(label)

        list_item.set_child(box)

    def _on_dropdown_list_bind(self, factory, list_item):
        """Bind data to list item in dropdown menu."""
        box = list_item.get_child()
        label = box.get_last_child()  # Label is the last child after icon
        string_object = list_item.get_item()
        if string_object:
            label.set_text(string_object.get_string())

    def _on_dropdown_selected_setup(self, factory, list_item):
        """Set up selected item widget (compact - just icon)."""
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)

        icon = Gtk.Image.new_from_icon_name("network-server-symbolic")
        box.append(icon)

        label = Gtk.Label()
        label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
        label.set_max_width_chars(20)  # Limit width
        box.append(label)

        list_item.set_child(box)

    def _on_dropdown_selected_bind(self, factory, list_item):
        """Bind data to selected item (shows in header bar)."""
        box = list_item.get_child()
        label = box.get_last_child()  # Label is the last child after icon
        string_object = list_item.get_item()
        if string_object:
            hostname = string_object.get_string()
            # Show shortened version (remove www. and truncate)
            if hostname.startswith("www."):
                hostname = hostname[4:]
            label.set_text(hostname)

    def setup_actions(self):
        """Set up window actions and keyboard shortcuts."""
        # Refresh action
        refresh_action = Gio.SimpleAction.new("refresh", None)
        refresh_action.connect("activate", lambda a, p: self.on_refresh_clicked(None))
        self.add_action(refresh_action)
        self.get_application().set_accels_for_action("win.refresh", ["<Ctrl>R", "F5"])

        # Export action
        export_action = Gio.SimpleAction.new("export", None)
        export_action.connect("activate", lambda a, p: self.on_export_clicked(None))
        self.add_action(export_action)
        self.get_application().set_accels_for_action("win.export", ["<Ctrl>E"])

        # Keyboard shortcuts action
        shortcuts_action = Gio.SimpleAction.new("show-help-overlay", None)
        shortcuts_action.connect("activate", lambda a, p: self.show_shortcuts())
        self.add_action(shortcuts_action)
        self.get_application().set_accels_for_action("win.show-help-overlay", ["<Ctrl>question"])

        # View switching actions (4 views only)
        view_actions = [
            ("view-dashboard", "dashboard", ["<Ctrl>1", "<Alt>1"]),
            ("view-events", "events", ["<Ctrl>2", "<Alt>2"]),
            ("view-pages", "pages", ["<Ctrl>3", "<Alt>3"]),
            ("view-countries", "countries", ["<Ctrl>4", "<Alt>4"]),
        ]

        for action_name, view_name, accels in view_actions:
            action = Gio.SimpleAction.new(action_name, None)
            action.connect("activate", lambda a, p, v=view_name: self.switch_to_view(v))
            self.add_action(action)
            self.get_application().set_accels_for_action(f"win.{action_name}", accels)

    def switch_to_view(self, view_name):
        """Switch to a specific view."""
        self.view_stack.set_visible_child_name(view_name)

    def show_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        shortcuts_dialog = create_shortcuts_window(self)
        # Check if it's an Adw.Dialog (new style) or GtkShortcutsWindow (legacy)
        if hasattr(shortcuts_dialog, 'present') and callable(shortcuts_dialog.present):
            # New Adw.Dialog API
            if isinstance(shortcuts_dialog, Adw.Dialog):
                shortcuts_dialog.present(self)
            else:
                # Legacy GtkShortcutsWindow
                shortcuts_dialog.present()

    def show_auth_dialog(self):
        """Show authentication dialog."""
        dialog = Adw.MessageDialog.new(self)
        dialog.set_heading("Authentication Required")
        dialog.set_body(
            "Please enter your Simple Analytics API credentials.\n\n"
            "You can find these at:\nhttps://simpleanalytics.com/account"
        )

        dialog.add_response("cancel", "Cancel")
        dialog.add_response("authenticate", "Authenticate")
        dialog.set_response_appearance("authenticate", Adw.ResponseAppearance.SUGGESTED)

        dialog.connect("response", self.on_auth_dialog_response)
        dialog.present()

    def on_auth_dialog_response(self, dialog, response):
        """Handle authentication dialog response."""
        if response == "authenticate":
            self.show_preferences()
        elif response == "cancel":
            self.close()

    def authenticate(self):
        """Authenticate with Simple Analytics API."""
        if not self.api_key or not self.user_id:
            self.show_auth_dialog()
            return

        try:
            self.client = SimpleAnalyticsClient(
                api_key=self.api_key,
                user_id=self.user_id,
                user_agent=f"simple-analytics-viewer/{app_version} (GTK4/libadwaita)"
            )

            # Fetch websites
            self.websites = self.client.admin.list_websites()

            # Validate websites is a list
            if not isinstance(self.websites, list):
                self.show_error(f"Unexpected response from API: {self.websites}")
                return

            if not self.websites:
                self.show_error("No websites found in your account. Please add a website at simpleanalytics.com")
                return

            # Block signal before setting model - prevents callback during initialization
            print(f"authenticate: Blocking signal handler")
            self.website_dropdown.handler_block(self._website_changed_handler_id)

            # Update website dropdown
            string_list = Gtk.StringList()
            for website in self.websites:
                if isinstance(website, dict):
                    string_list.append(website.get("hostname", "Unknown"))
                else:
                    print(f"Warning: Unexpected website format: {website}")

            self.website_dropdown.set_model(string_list)

            # Select the saved hostname or fall back to first website
            selected_index = 0  # Default to first
            print(f"authenticate: self.hostname = '{self.hostname}'")
            print(f"authenticate: Available websites: {[w.get('hostname') for w in self.websites if isinstance(w, dict)]}")

            if self.hostname:
                # Try to find the saved hostname
                for i, website in enumerate(self.websites):
                    if isinstance(website, dict) and website.get("hostname") == self.hostname:
                        selected_index = i
                        print(f"authenticate: Found saved hostname at index {i}")
                        break
                else:
                    print(f"authenticate: Saved hostname '{self.hostname}' not found in website list")
                # If not found, keep selected_index = 0 but don't change saved hostname
            else:
                print(f"authenticate: No saved hostname, using first website")
                # No saved hostname, use first website and save it
                if self.websites and isinstance(self.websites[0], dict):
                    self.hostname = self.websites[0].get("hostname", "")
                    if self.settings:
                        self.settings.set_string("hostname", self.hostname)

            # Set selection while signal is still blocked
            print(f"authenticate: Setting dropdown to index {selected_index} (hostname: {self.hostname})")
            self.website_dropdown.set_selected(selected_index)

            # Unblock signal after everything is set up
            print(f"authenticate: Unblocking signal handler")
            self.website_dropdown.handler_unblock(self._website_changed_handler_id)

            # Now load data with the correct hostname
            self.load_data()

        except AuthenticationError as e:
            self.show_error(f"Authentication failed: {e.message}")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def on_website_changed(self, dropdown, param):
        """Handle website selection change."""
        selected = dropdown.get_selected()
        print(f"on_website_changed: selected index = {selected}")
        if selected != Gtk.INVALID_LIST_POSITION and self.websites:
            if isinstance(self.websites[selected], dict):
                new_hostname = self.websites[selected].get("hostname", "")
                print(f"on_website_changed: changing from {self.hostname} to {new_hostname}")
                self.hostname = new_hostname

                # Save the selected hostname to GSettings
                if self.settings:
                    self.settings.set_string("hostname", self.hostname)
                    print(f"on_website_changed: saved {self.hostname} to GSettings")

                self.load_data()
            else:
                print(f"on_website_changed: Invalid website at index {selected}: {self.websites[selected]}")

    def on_refresh_clicked(self, button):
        """Handle refresh button click."""
        self.load_data()

    def on_export_clicked(self, button):
        """Handle export button click."""
        if not self.client or not self.hostname:
            self.show_error("No data to export. Please select a website first.")
            return

        # Create file chooser dialog
        dialog = Gtk.FileDialog()
        dialog.set_title("Export Analytics Data")
        dialog.set_initial_name(f"{self.hostname}_analytics.csv")

        # Set up filters
        csv_filter = Gtk.FileFilter()
        csv_filter.set_name("CSV Files")
        csv_filter.add_pattern("*.csv")

        filter_list = Gio.ListStore.new(Gtk.FileFilter)
        filter_list.append(csv_filter)
        dialog.set_filters(filter_list)

        # Show save dialog
        dialog.save(self, None, self.on_export_file_selected)

    def on_export_file_selected(self, dialog, result):
        """Handle file selection for export."""
        try:
            file = dialog.save_finish(result)
            if file:
                file_path = file.get_path()
                self.export_data_to_file(file_path)
        except Exception as e:
            if "dismissed" not in str(e).lower():
                self.show_error(f"Export failed: {str(e)}")

    def export_data_to_file(self, file_path):
        """Export data to CSV file."""
        try:
            # Calculate date range (last 30 days)
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

            # Use the Export API to get CSV data
            csv_data = self.client.export.to_csv(
                self.hostname,
                start=start_date,
                end=end_date,
                fields=[
                    "added_iso",
                    "hostname",
                    "path",
                    "country_code",
                    "device_type",
                    "browser_name",
                    "os_name",
                    "referrer_hostname",
                ],
            )

            # Write to file
            with open(file_path, "w") as f:
                f.write(csv_data)

            # Show success message
            dialog = Adw.MessageDialog.new(self)
            dialog.set_heading("Export Successful")
            dialog.set_body(f"Data exported to:\n{file_path}")
            dialog.add_response("ok", "OK")
            dialog.present()

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.show_error(f"Export failed: {str(e)}")

    def load_data(self):
        """Load analytics data for the selected website asynchronously."""
        if not self.client:
            print("No client available")
            return

        if not self.hostname:
            print("No hostname selected")
            return

        # Cancel any in-flight loads from previous website selection
        with self._load_lock:
            self._current_load_generation += 1
            current_gen = self._current_load_generation

        # Calculate date range (last 30 days)
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        # Capture values to avoid race conditions
        client = self.client
        hostname = self.hostname

        print(f"Loading data for {hostname} from {start_date} to {end_date} (gen {current_gen})")

        # Load each view in parallel using thread pool
        # This limits concurrent requests and allows cancellation
        views = [
            (self.dashboard_view, "Dashboard"),
            (self.events_view, "Events"),
            (self.pages_view, "Pages"),
            (self.countries_view, "Countries"),
        ]

        for view, name in views:
            self._executor.submit(
                self._load_view_data,
                view, name, client, hostname, start_date, end_date, current_gen
            )

    def _load_view_data(self, view, view_name, client, hostname, start_date, end_date, generation):
        """Load data for a single view with generation check for cancellation."""
        try:
            # Check if this load was superseded by a newer request
            with self._load_lock:
                if generation != self._current_load_generation:
                    print(f"Skipping outdated {view_name} load (gen {generation})")
                    return

            print(f"Loading {view_name} data in background (gen {generation})...")
            view.load_data(client, hostname, start_date, end_date)
            print(f"{view_name} data loaded successfully (gen {generation})")
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Schedule error display on main thread
            GLib.idle_add(
                self.show_error,
                f"Error loading {view_name} data: {str(e)}"
            )

    def show_preferences(self):
        """Show preferences dialog."""
        dialog = PreferencesDialog(self, self.api_key, self.user_id, self.hostname)
        dialog.connect("credentials-updated", self.on_credentials_updated)
        dialog.present()

    def on_credentials_updated(self, dialog, api_key, user_id, hostname):
        """Handle updated credentials."""
        self.api_key = api_key
        self.user_id = user_id
        self.hostname = hostname

        # Save to GSettings for persistence
        if self.settings:
            self.settings.set_string("api-key", api_key)
            self.settings.set_string("user-id", user_id)
            self.settings.set_string("hostname", hostname)

        # Save to environment (for session only)
        os.environ["SA_API_KEY"] = api_key
        os.environ["SA_USER_ID"] = user_id
        os.environ["SA_HOSTNAME"] = hostname

        # Re-authenticate
        self.authenticate()

    def show_error(self, message):
        """Show error dialog."""
        dialog = Adw.MessageDialog.new(self)
        dialog.set_heading("Error")
        dialog.set_body(message)
        dialog.add_response("ok", "OK")
        dialog.present()
