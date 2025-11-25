"""Keyboard shortcuts dialog using Adwaita 1.8."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw


def create_shortcuts_window(parent):
    """Create and return shortcuts dialog (Adwaita 1.8)."""
    # Try to use Adw.Dialog if available (Adwaita 1.8+)
    # Fall back to GtkShortcutsWindow for older versions
    try:
        # Create an Adwaita Dialog with shortcuts content
        dialog = Adw.Dialog()
        dialog.set_title("Keyboard Shortcuts")
        dialog.set_content_width(600)
        dialog.set_content_height(500)

        # Create toolbar
        toolbar = Adw.ToolbarView()
        header = Adw.HeaderBar()
        header.set_show_title(True)
        toolbar.add_top_bar(header)

        # Create scrolled window for content
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)

        # Create content box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(24)
        content_box.set_margin_start(24)
        content_box.set_margin_end(24)

        # Views section
        views_clamp = Adw.Clamp()
        views_clamp.set_maximum_size(600)
        views_group = Adw.PreferencesGroup()
        views_group.set_title("Views")

        views_group.add(_create_shortcut_row("Dashboard", "Ctrl+1"))
        views_group.add(_create_shortcut_row("Events", "Ctrl+2"))
        views_group.add(_create_shortcut_row("Pages", "Ctrl+3"))
        views_group.add(_create_shortcut_row("Countries", "Ctrl+4"))

        views_clamp.set_child(views_group)
        content_box.append(views_clamp)

        # Actions section
        actions_clamp = Adw.Clamp()
        actions_clamp.set_maximum_size(600)
        actions_group = Adw.PreferencesGroup()
        actions_group.set_title("Actions")

        actions_group.add(_create_shortcut_row("Refresh Data", "Ctrl+R, F5"))
        actions_group.add(_create_shortcut_row("Export Data", "Ctrl+E"))

        actions_clamp.set_child(actions_group)
        content_box.append(actions_clamp)

        # General section
        general_clamp = Adw.Clamp()
        general_clamp.set_maximum_size(600)
        general_group = Adw.PreferencesGroup()
        general_group.set_title("General")

        general_group.add(_create_shortcut_row("Preferences", "Ctrl+,"))
        general_group.add(_create_shortcut_row("Keyboard Shortcuts", "Ctrl+?"))
        general_group.add(_create_shortcut_row("Quit", "Ctrl+Q"))

        general_clamp.set_child(general_group)
        content_box.append(general_clamp)

        scrolled.set_child(content_box)
        toolbar.set_content(scrolled)
        dialog.set_child(toolbar)

        return dialog
    except:
        # Fall back to GtkShortcutsWindow for older Adwaita versions
        return _create_legacy_shortcuts_window(parent)


def _create_shortcut_row(title, accelerator):
    """Create a row showing a keyboard shortcut."""
    row = Adw.ActionRow()
    row.set_title(title)

    # Create keyboard shortcut label
    shortcut_label = Gtk.ShortcutLabel()
    shortcut_label.set_accelerator(accelerator)
    shortcut_label.set_valign(Gtk.Align.CENTER)
    row.add_suffix(shortcut_label)

    return row


def _create_legacy_shortcuts_window(parent):
    """Create legacy GTK shortcuts window for older versions."""
    builder = Gtk.Builder()
    builder.add_from_string(
        """<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <object class="GtkShortcutsWindow" id="shortcuts_window">
    <property name="modal">1</property>
    <child>
      <object class="GtkShortcutsSection">
        <property name="section-name">shortcuts</property>
        <property name="max-height">12</property>
        <child>
          <object class="GtkShortcutsGroup">
            <property name="title" translatable="yes" context="shortcut window">Views</property>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes" context="shortcut window">Dashboard</property>
                <property name="accelerator">&lt;Control&gt;1</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes" context="shortcut window">Events</property>
                <property name="accelerator">&lt;Control&gt;2</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes" context="shortcut window">Pages</property>
                <property name="accelerator">&lt;Control&gt;3</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes" context="shortcut window">Countries</property>
                <property name="accelerator">&lt;Control&gt;4</property>
              </object>
            </child>
          </object>
        </child>
        <child>
          <object class="GtkShortcutsGroup">
            <property name="title" translatable="yes" context="shortcut window">Actions</property>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes" context="shortcut window">Refresh Data</property>
                <property name="accelerator">&lt;Control&gt;R F5</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes" context="shortcut window">Export Data</property>
                <property name="accelerator">&lt;Control&gt;E</property>
              </object>
            </child>
          </object>
        </child>
        <child>
          <object class="GtkShortcutsGroup">
            <property name="title" translatable="yes" context="shortcut window">General</property>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes" context="shortcut window">Preferences</property>
                <property name="accelerator">&lt;Control&gt;comma</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes" context="shortcut window">Keyboard Shortcuts</property>
                <property name="accelerator">&lt;Control&gt;question</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes" context="shortcut window">Quit</property>
                <property name="accelerator">&lt;Control&gt;Q</property>
              </object>
            </child>
          </object>
        </child>
      </object>
    </child>
  </object>
</interface>
"""
    )

    window = builder.get_object("shortcuts_window")
    window.set_transient_for(parent)
    return window
