"""Main application window."""

import gi
import os
from datetime import datetime, timedelta

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib, Gio, GObject

from simple_analytics import SimpleAnalyticsClient, AuthenticationError

from .views.dashboard import DashboardView
from .views.events import EventsView
from .views.pages import PagesView
from .views.countries import CountriesView
from .preferences import PreferencesDialog


class AnalyticsWindow(Adw.ApplicationWindow):
    """Main application window."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Set window properties
        self.set_default_size(1200, 800)
        self.set_title("Simple Analytics Viewer")

        # Load credentials from environment
        self.api_key = os.environ.get("SA_API_KEY", "")
        self.user_id = os.environ.get("SA_USER_ID", "")
        self.hostname = os.environ.get("SA_HOSTNAME", "")

        self.client = None
        self.websites = []

        # Create UI
        self.setup_ui()

        # Check authentication
        if self.api_key and self.user_id:
            self.authenticate()
        else:
            self.show_auth_dialog()

    def setup_ui(self):
        """Set up the user interface."""
        # Create header bar
        self.header_bar = Adw.HeaderBar()

        # Website dropdown
        self.website_dropdown = Gtk.DropDown()
        self.website_dropdown.connect("notify::selected", self.on_website_changed)
        self.header_bar.pack_start(self.website_dropdown)

        # Refresh button
        refresh_button = Gtk.Button(icon_name="view-refresh-symbolic")
        refresh_button.set_tooltip_text("Refresh data")
        refresh_button.connect("clicked", self.on_refresh_clicked)
        self.header_bar.pack_end(refresh_button)

        # Menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")

        menu = Gio.Menu()
        menu.append("Preferences", "app.preferences")
        menu.append("About", "app.about")
        menu.append("Quit", "app.quit")

        menu_button.set_menu_model(menu)
        self.header_bar.pack_end(menu_button)

        # Create main content
        self.toolbox = Adw.ToolbarView()
        self.toolbox.add_top_bar(self.header_bar)

        # Create view switcher
        self.view_stack = Adw.ViewStack()
        self.view_stack.set_vexpand(True)

        # Create views
        self.dashboard_view = DashboardView()
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
        view_switcher_title = Adw.ViewSwitcherTitle()
        view_switcher_title.set_stack(self.view_stack)
        view_switcher_title.set_title("Simple Analytics")
        self.header_bar.set_title_widget(view_switcher_title)

        # Bottom bar for narrow mode
        view_switcher_bar = Adw.ViewSwitcherBar()
        view_switcher_bar.set_stack(self.view_stack)

        # Bind view switcher to window width
        self.bind_property(
            "default-width",
            view_switcher_bar,
            "reveal",
            GObject.BindingFlags.SYNC_CREATE,
            lambda binding, width: width < 600,
        )

        # Add to toolbar
        self.toolbox.set_content(self.view_stack)
        self.toolbox.add_bottom_bar(view_switcher_bar)

        self.set_content(self.toolbox)

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
                user_id=self.user_id
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

            # Update website dropdown
            string_list = Gtk.StringList()
            for website in self.websites:
                if isinstance(website, dict):
                    string_list.append(website.get("hostname", "Unknown"))
                else:
                    print(f"Warning: Unexpected website format: {website}")

            self.website_dropdown.set_model(string_list)

            # Select first website or the one from env
            if self.hostname:
                for i, website in enumerate(self.websites):
                    if isinstance(website, dict) and website.get("hostname") == self.hostname:
                        self.website_dropdown.set_selected(i)
                        break
            elif self.websites:
                self.website_dropdown.set_selected(0)

            # Load data only if we have a valid website selected
            if self.website_dropdown.get_selected() != Gtk.INVALID_LIST_POSITION:
                self.load_data()

        except AuthenticationError as e:
            self.show_error(f"Authentication failed: {e.message}")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def on_website_changed(self, dropdown, param):
        """Handle website selection change."""
        selected = dropdown.get_selected()
        if selected != Gtk.INVALID_LIST_POSITION and self.websites:
            if isinstance(self.websites[selected], dict):
                self.hostname = self.websites[selected].get("hostname", "")
                print(f"Website changed to: {self.hostname}")
                self.load_data()
            else:
                print(f"Invalid website at index {selected}: {self.websites[selected]}")

    def on_refresh_clicked(self, button):
        """Handle refresh button click."""
        self.load_data()

    def load_data(self):
        """Load analytics data for the selected website."""
        if not self.client:
            print("No client available")
            return

        if not self.hostname:
            print("No hostname selected")
            return

        # Calculate date range (last 30 days)
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        try:
            print(f"Loading data for {self.hostname} from {start_date} to {end_date}")

            # Load data for each view
            self.dashboard_view.load_data(
                self.client, self.hostname, start_date, end_date
            )
            self.events_view.load_data(
                self.client, self.hostname, start_date, end_date
            )
            self.pages_view.load_data(
                self.client, self.hostname, start_date, end_date
            )
            self.countries_view.load_data(
                self.client, self.hostname, start_date, end_date
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.show_error(f"Error loading data: {str(e)}")

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
