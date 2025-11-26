"""Beautiful Cairo-based chart widgets for GTK4 with Adwaita styling.

This module provides modern, visually appealing charts that match GNOME's
Adwaita design language with proper colors, gradients, and styling.
"""

import gi
import math
import cairo
from typing import Any

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk


# Adwaita color palette (only colors actually used in charts)
class AdwaitaColors:
    """Adwaita color scheme."""
    BLUE_2 = (0.20, 0.47, 0.90)      # #3584e4
    BLUE_3 = (0.11, 0.44, 0.85)      # #1c71d8

    GREEN_2 = (0.38, 0.78, 0.52)     # #57e389
    GREEN_3 = (0.15, 0.64, 0.41)     # #26a269

    GRAY_3 = (0.87, 0.87, 0.87)      # #dddddd
    GRAY_4 = (0.80, 0.80, 0.80)      # #cccccc

    BACKGROUND = (0.98, 0.98, 0.98)  # #fafafa - matches Adwaita window bg
    TEXT_SECONDARY = (0.45, 0.45, 0.45)  # #737373


class ModernHistogramChart(Gtk.DrawingArea):
    """A beautiful modern histogram chart with Adwaita styling and interactivity."""

    def __init__(self, histogram: list[dict[str, Any]] = None):
        super().__init__()

        self.histogram = histogram or []
        self.set_draw_func(self._draw)
        # Don't set fixed width - let it adapt to container
        # Set minimum size instead
        self.set_size_request(400, 300)  # Min: 400x300
        self.set_hexpand(True)  # Expand horizontally
        self.set_vexpand(False)

        # Interactive features
        self.hovered_bar = -1  # Index of currently hovered bar
        self.bar_positions = []  # Store bar positions for hit detection

        # Enable mouse motion events
        motion_controller = Gtk.EventControllerMotion()
        motion_controller.connect("motion", self._on_motion)
        motion_controller.connect("leave", self._on_leave)
        self.add_controller(motion_controller)

        # Enable tooltips
        self.set_has_tooltip(True)
        self.connect("query-tooltip", self._on_query_tooltip)

    def set_data(self, histogram: list[dict[str, Any]]):
        """Update the histogram data and redraw."""
        self.histogram = histogram
        self.queue_draw()

    def _draw(self, area, cr, width, height):
        """Draw function called by GTK."""
        if not self.histogram:
            self._draw_empty(cr, width, height)
            return

        # Responsive margins - scale down on narrow screens
        if width < 600:
            margin_left = 50
            margin_right = 20
            margin_top = 30
            margin_bottom = 50
        else:
            margin_left = 70
            margin_right = 30
            margin_top = 50
            margin_bottom = 70

        plot_width = width - margin_left - margin_right
        plot_height = height - margin_top - margin_bottom

        # Extract data
        dates = [p.get("date", "") for p in self.histogram]
        pageviews = [p.get("pageviews", 0) for p in self.histogram]
        visitors = [p.get("visitors", 0) for p in self.histogram]

        max_value = max(max(pageviews), max(visitors))
        if max_value == 0:
            max_value = 1

        # Draw background - match window background (transparent effect)
        cr.set_source_rgba(*AdwaitaColors.BACKGROUND, 0.0)
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        # Draw subtle grid lines
        cr.set_source_rgba(*AdwaitaColors.GRAY_3, 0.3)
        cr.set_line_width(1)
        for i in range(6):
            y = margin_top + (plot_height / 5) * i
            cr.move_to(margin_left, y)
            cr.line_to(margin_left + plot_width, y)
            cr.stroke()

        # Draw data area with gradient fill under pageviews line
        cr.save()

        # Create path for pageviews
        for i, value in enumerate(pageviews):
            x = margin_left + (plot_width / (len(pageviews) - 1)) * i
            y = margin_top + plot_height - (value / max_value) * plot_height

            if i == 0:
                cr.move_to(x, y)
            else:
                cr.line_to(x, y)

        # Close path for fill
        cr.line_to(margin_left + plot_width, margin_top + plot_height)
        cr.line_to(margin_left, margin_top + plot_height)
        cr.close_path()

        # Apply gradient fill using Cairo LinearGradient
        pattern = cairo.LinearGradient(0, margin_top, 0, margin_top + plot_height)
        pattern.add_color_stop_rgba(0, *AdwaitaColors.BLUE_2, 0.2)
        pattern.add_color_stop_rgba(1, *AdwaitaColors.BLUE_2, 0.0)
        cr.set_source(pattern)
        cr.fill()

        cr.restore()

        # Draw pageviews line with shadow
        cr.set_line_width(3)
        cr.set_line_cap(1)  # Round caps
        cr.set_line_join(1)  # Round joins

        # Shadow
        for i, value in enumerate(pageviews):
            x = margin_left + (plot_width / (len(pageviews) - 1)) * i
            y = margin_top + plot_height - (value / max_value) * plot_height + 2

            if i == 0:
                cr.move_to(x, y)
            else:
                cr.line_to(x, y)

        cr.set_source_rgba(0, 0, 0, 0.1)
        cr.stroke()

        # Main line
        for i, value in enumerate(pageviews):
            x = margin_left + (plot_width / (len(pageviews) - 1)) * i
            y = margin_top + plot_height - (value / max_value) * plot_height

            if i == 0:
                cr.move_to(x, y)
            else:
                cr.line_to(x, y)

        cr.set_source_rgb(*AdwaitaColors.BLUE_3)
        cr.stroke()

        # Draw pageviews points and track positions for interaction
        self.bar_positions = []
        for i, value in enumerate(pageviews):
            x = margin_left + (plot_width / (len(pageviews) - 1)) * i
            y = margin_top + plot_height - (value / max_value) * plot_height

            # Track position for hit detection (expanded hit area)
            hit_radius = 15
            self.bar_positions.append((x - hit_radius, y - hit_radius, hit_radius * 2, hit_radius * 2))

            # Highlight if hovered
            is_hovered = (i == self.hovered_bar)
            point_size = 5 if is_hovered else 3.5
            glow_size = 8 if is_hovered else 5

            # Outer glow (larger when hovered)
            cr.arc(x, y, glow_size, 0, 2 * math.pi)
            cr.set_source_rgba(*AdwaitaColors.BLUE_2, 0.4 if is_hovered else 0.3)
            cr.fill()

            # Main point (larger when hovered)
            cr.arc(x, y, point_size, 0, 2 * math.pi)
            cr.set_source_rgb(*AdwaitaColors.BLUE_3)
            cr.fill()

            # Inner highlight
            cr.arc(x, y, 2, 0, 2 * math.pi)
            cr.set_source_rgba(1, 1, 1, 0.8)
            cr.fill()

        # Draw visitors line
        cr.set_line_width(3)
        for i, value in enumerate(visitors):
            x = margin_left + (plot_width / (len(visitors) - 1)) * i
            y = margin_top + plot_height - (value / max_value) * plot_height + 2

            if i == 0:
                cr.move_to(x, y)
            else:
                cr.line_to(x, y)

        cr.set_source_rgba(0, 0, 0, 0.1)
        cr.stroke()

        for i, value in enumerate(visitors):
            x = margin_left + (plot_width / (len(visitors) - 1)) * i
            y = margin_top + plot_height - (value / max_value) * plot_height

            if i == 0:
                cr.move_to(x, y)
            else:
                cr.line_to(x, y)

        cr.set_source_rgb(*AdwaitaColors.GREEN_3)
        cr.stroke()

        # Draw visitors points
        for i, value in enumerate(visitors):
            x = margin_left + (plot_width / (len(visitors) - 1)) * i
            y = margin_top + plot_height - (value / max_value) * plot_height

            cr.arc(x, y, 5, 0, 2 * math.pi)
            cr.set_source_rgba(*AdwaitaColors.GREEN_2, 0.3)
            cr.fill()

            cr.arc(x, y, 3.5, 0, 2 * math.pi)
            cr.set_source_rgb(*AdwaitaColors.GREEN_3)
            cr.fill()

            cr.arc(x, y, 2, 0, 2 * math.pi)
            cr.set_source_rgba(1, 1, 1, 0.8)
            cr.fill()

        # Draw axes
        cr.set_source_rgb(*AdwaitaColors.GRAY_4)
        cr.set_line_width(2)
        cr.move_to(margin_left, margin_top)
        cr.line_to(margin_left, margin_top + plot_height)
        cr.line_to(margin_left + plot_width, margin_top + plot_height)
        cr.stroke()

        # Draw y-axis labels
        cr.select_font_face("Sans", 0, 0)
        cr.set_font_size(11)
        cr.set_source_rgb(*AdwaitaColors.TEXT_SECONDARY)

        for i in range(6):
            value = max_value - (max_value / 5) * i
            y = margin_top + (plot_height / 5) * i

            if value >= 1000:
                label = f"{int(value/1000)}k"
            else:
                label = str(int(value))

            extents = cr.text_extents(label)
            cr.move_to(margin_left - extents.width - 12, y + 4)
            cr.show_text(label)

        # Draw x-axis labels
        cr.set_font_size(10)
        step = max(1, len(dates) // 8)

        for i in range(0, len(dates), step):
            x = margin_left + (plot_width / (len(dates) - 1)) * i
            label = dates[i][5:] if len(dates[i]) >= 10 else dates[i]

            extents = cr.text_extents(label)
            cr.save()
            cr.translate(x, margin_top + plot_height + 20)
            cr.rotate(math.pi / 6)
            cr.move_to(0, 0)
            cr.show_text(label)
            cr.restore()

    def _draw_empty(self, cr, width, height):
        """Draw empty state."""
        # Transparent background
        cr.set_source_rgba(*AdwaitaColors.BACKGROUND, 0.0)
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        cr.set_source_rgb(*AdwaitaColors.TEXT_SECONDARY)
        cr.select_font_face("Sans", 0, 0)
        cr.set_font_size(14)
        text = "No data available"
        extents = cr.text_extents(text)
        cr.move_to((width - extents.width) / 2, height / 2)
        cr.show_text(text)

    def _on_motion(self, controller, x, y):
        """Handle mouse motion - detect hovering over data points."""
        if not self.histogram or not self.bar_positions:
            return

        # Check if mouse is over any bar
        hovered = -1
        for i, (bar_x, bar_y, bar_width, bar_height) in enumerate(self.bar_positions):
            if bar_x <= x <= bar_x + bar_width and bar_y <= y <= bar_y + bar_height:
                hovered = i
                break

        if hovered != self.hovered_bar:
            self.hovered_bar = hovered
            self.queue_draw()

    def _on_leave(self, controller):
        """Handle mouse leaving the widget."""
        if self.hovered_bar != -1:
            self.hovered_bar = -1
            self.queue_draw()

    def _on_query_tooltip(self, widget, x, y, keyboard_mode, tooltip):
        """Show tooltip with data when hovering over a bar."""
        if self.hovered_bar >= 0 and self.hovered_bar < len(self.histogram):
            data = self.histogram[self.hovered_bar]
            date = data.get("date", "")
            pageviews = data.get("pageviews", 0)
            visitors = data.get("visitors", 0)

            tooltip_text = f"{date}\n{pageviews:,} pageviews\n{visitors:,} visitors"
            tooltip.set_text(tooltip_text)
            return True

        return False
