#!/usr/bin/env python3
"""
Simple Analytics Viewer - GNOME GTK4 Application

A beautiful Adwaita-styled application for viewing your Simple Analytics data.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for development (so simple_analytics can be imported)
# This allows running the app without installing the simple_analytics package
repo_root = Path(__file__).parent.parent.parent
if repo_root.exists() and (repo_root / "simple_analytics").exists():
    sys.path.insert(0, str(repo_root))

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gio, GLib

from .window import AnalyticsWindow


class AnalyticsApplication(Adw.Application):
    """Main application class."""

    def __init__(self):
        super().__init__(
            application_id="com.simpleanalytics.viewer",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.window = None

    def do_activate(self):
        """Called when the application is activated."""
        if not self.window:
            self.window = AnalyticsWindow(application=self)
        self.window.present()

    def do_startup(self):
        """Called when the application starts."""
        Adw.Application.do_startup(self)

        # Create actions
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda *_: self.quit())
        self.add_action(quit_action)
        self.set_accels_for_action("app.quit", ["<Ctrl>Q"])

        preferences_action = Gio.SimpleAction.new("preferences", None)
        preferences_action.connect("activate", self.on_preferences)
        self.add_action(preferences_action)
        self.set_accels_for_action("app.preferences", ["<Ctrl>comma"])

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about)
        self.add_action(about_action)

    def on_preferences(self, action, param):
        """Show preferences dialog."""
        if self.window:
            self.window.show_preferences()

    def on_about(self, action, param):
        """Show about dialog."""
        about = Adw.AboutWindow(
            transient_for=self.window,
            application_name="Simple Analytics Viewer",
            application_icon="org.gnome.Analytics",
            developer_name="Simple Analytics Python Contributors",
            version="0.1.0",
            website="https://github.com/andypiper/simple_analytics_python",
            issue_url="https://github.com/andypiper/simple_analytics_python/issues",
            license_type=Gtk.License.MIT_X11,
            developers=["Simple Analytics Python Contributors"],
            copyright="© 2024 Simple Analytics Python Contributors",
        )
        about.present()


def main():
    """Main entry point."""
    app = AnalyticsApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
