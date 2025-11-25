"""Native Cairo-based chart widgets for GTK4.

This module provides truly native GNOME charts using Cairo drawing,
which is more performant and better integrated than matplotlib.
"""

import gi
import math
from typing import Any

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gdk


class HistogramChart(Gtk.DrawingArea):
    """A native GTK histogram/line chart widget using Cairo."""

    def __init__(self, histogram: list[dict[str, Any]] = None):
        super().__init__()

        self.histogram = histogram or []
        self.set_draw_func(self._draw)
        self.set_content_width(800)
        self.set_content_height(400)

    def set_data(self, histogram: list[dict[str, Any]]):
        """Update the histogram data and redraw."""
        self.histogram = histogram
        self.queue_draw()

    def _draw(self, area, cr, width, height):
        """Draw function called by GTK."""
        if not self.histogram:
            self._draw_empty(cr, width, height)
            return

        # Margins
        margin_left = 60
        margin_right = 20
        margin_top = 40
        margin_bottom = 60

        plot_width = width - margin_left - margin_right
        plot_height = height - margin_top - margin_bottom

        # Extract data
        dates = [p.get("date", "") for p in self.histogram]
        pageviews = [p.get("pageviews", 0) for p in self.histogram]
        visitors = [p.get("visitors", 0) for p in self.histogram]

        max_value = max(max(pageviews), max(visitors))
        if max_value == 0:
            max_value = 1

        # Draw background
        cr.set_source_rgb(1, 1, 1)
        cr.paint()

        # Draw title
        cr.set_source_rgb(0, 0, 0)
        cr.select_font_face("Sans", 0, 1)  # Bold
        cr.set_font_size(16)
        cr.move_to(margin_left, 25)
        cr.show_text("Pageviews & Visitors Over Time")

        # Draw grid lines
        cr.set_source_rgba(0.8, 0.8, 0.8, 0.5)
        cr.set_line_width(1)
        for i in range(6):
            y = margin_top + (plot_height / 5) * i
            cr.move_to(margin_left, y)
            cr.line_to(margin_left + plot_width, y)
            cr.stroke()

        # Draw axes
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(2)
        cr.move_to(margin_left, margin_top)
        cr.line_to(margin_left, margin_top + plot_height)
        cr.line_to(margin_left + plot_width, margin_top + plot_height)
        cr.stroke()

        # Draw y-axis labels
        cr.select_font_face("Sans", 0, 0)
        cr.set_font_size(10)
        for i in range(6):
            value = max_value - (max_value / 5) * i
            y = margin_top + (plot_height / 5) * i
            label = f"{int(value):,}"
            extents = cr.text_extents(label)
            cr.move_to(margin_left - extents.width - 10, y + 4)
            cr.show_text(label)

        # Draw x-axis labels (every 5th date)
        step = max(1, len(dates) // 10)
        for i in range(0, len(dates), step):
            x = margin_left + (plot_width / (len(dates) - 1)) * i
            label = dates[i][5:] if len(dates[i]) >= 10 else dates[i]
            extents = cr.text_extents(label)
            cr.save()
            cr.translate(x, margin_top + plot_height + 15)
            cr.rotate(math.pi / 4)
            cr.move_to(0, 0)
            cr.show_text(label)
            cr.restore()

        # Draw pageviews line
        cr.set_source_rgb(0.11, 0.44, 0.85)  # Blue
        cr.set_line_width(2)
        for i, value in enumerate(pageviews):
            x = margin_left + (plot_width / (len(pageviews) - 1)) * i
            y = margin_top + plot_height - (value / max_value) * plot_height

            if i == 0:
                cr.move_to(x, y)
            else:
                cr.line_to(x, y)
        cr.stroke()

        # Draw pageviews points
        for i, value in enumerate(pageviews):
            x = margin_left + (plot_width / (len(pageviews) - 1)) * i
            y = margin_top + plot_height - (value / max_value) * plot_height
            cr.arc(x, y, 3, 0, 2 * math.pi)
            cr.fill()

        # Draw visitors line
        cr.set_source_rgb(0.15, 0.64, 0.41)  # Green
        cr.set_line_width(2)
        for i, value in enumerate(visitors):
            x = margin_left + (plot_width / (len(visitors) - 1)) * i
            y = margin_top + plot_height - (value / max_value) * plot_height

            if i == 0:
                cr.move_to(x, y)
            else:
                cr.line_to(x, y)
        cr.stroke()

        # Draw visitors points
        for i, value in enumerate(visitors):
            x = margin_left + (plot_width / (len(visitors) - 1)) * i
            y = margin_top + plot_height - (value / max_value) * plot_height
            cr.arc(x, y, 3, 0, 2 * math.pi)
            cr.fill()

        # Draw legend
        legend_x = margin_left + plot_width - 150
        legend_y = margin_top + 20

        # Pageviews legend
        cr.set_source_rgb(0.11, 0.44, 0.85)
        cr.rectangle(legend_x, legend_y, 15, 15)
        cr.fill()
        cr.set_source_rgb(0, 0, 0)
        cr.move_to(legend_x + 20, legend_y + 12)
        cr.show_text("Pageviews")

        # Visitors legend
        cr.set_source_rgb(0.15, 0.64, 0.41)
        cr.rectangle(legend_x, legend_y + 25, 15, 15)
        cr.fill()
        cr.set_source_rgb(0, 0, 0)
        cr.move_to(legend_x + 20, legend_y + 37)
        cr.show_text("Visitors")

    def _draw_empty(self, cr, width, height):
        """Draw empty state."""
        cr.set_source_rgb(1, 1, 1)
        cr.paint()

        cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.select_font_face("Sans", 0, 0)
        cr.set_font_size(14)
        text = "No data available"
        extents = cr.text_extents(text)
        cr.move_to((width - extents.width) / 2, height / 2)
        cr.show_text(text)


class HorizontalBarChart(Gtk.DrawingArea):
    """A native GTK horizontal bar chart widget using Cairo."""

    def __init__(self, data: list[tuple[str, int]] = None, title: str = "Chart"):
        super().__init__()

        self.data = data or []
        self.title = title
        self.set_draw_func(self._draw)

        # Calculate height based on data
        height = max(300, len(self.data) * 35 + 100)
        self.set_content_width(800)
        self.set_content_height(height)

    def set_data(self, data: list[tuple[str, int]], title: str = None):
        """Update the data and redraw."""
        self.data = data
        if title:
            self.title = title

        # Update height
        height = max(300, len(self.data) * 35 + 100)
        self.set_content_height(height)

        self.queue_draw()

    def _draw(self, area, cr, width, height):
        """Draw function called by GTK."""
        if not self.data:
            self._draw_empty(cr, width, height)
            return

        # Margins
        margin_left = 250
        margin_right = 80
        margin_top = 60
        margin_bottom = 20

        plot_width = width - margin_left - margin_right
        plot_height = height - margin_top - margin_bottom

        # Reverse data for top-down display
        data = self.data[::-1]
        labels, values = zip(*data)

        max_value = max(values)
        if max_value == 0:
            max_value = 1

        bar_height = plot_height / len(data)

        # Draw background
        cr.set_source_rgb(1, 1, 1)
        cr.paint()

        # Draw title
        cr.set_source_rgb(0, 0, 0)
        cr.select_font_face("Sans", 0, 1)  # Bold
        cr.set_font_size(16)
        extents = cr.text_extents(self.title)
        cr.move_to((width - extents.width) / 2, 30)
        cr.show_text(self.title)

        # Draw bars and labels
        cr.select_font_face("Sans", 0, 0)
        cr.set_font_size(10)

        for i, (label, value) in enumerate(zip(labels, values)):
            y = margin_top + i * bar_height + bar_height / 4

            # Truncate long labels
            display_label = label[:35] + "..." if len(label) > 35 else label

            # Draw label
            cr.set_source_rgb(0, 0, 0)
            extents = cr.text_extents(display_label)
            cr.move_to(margin_left - extents.width - 10, y + bar_height / 4 + 3)
            cr.show_text(display_label)

            # Draw bar
            bar_width = (value / max_value) * plot_width
            cr.set_source_rgb(0.11, 0.44, 0.85)  # Blue
            cr.rectangle(margin_left, y, bar_width, bar_height / 2)
            cr.fill()

            # Draw value
            cr.set_source_rgb(0, 0, 0)
            value_text = f"{value:,}"
            cr.move_to(margin_left + bar_width + 5, y + bar_height / 4 + 3)
            cr.show_text(value_text)

    def _draw_empty(self, cr, width, height):
        """Draw empty state."""
        cr.set_source_rgb(1, 1, 1)
        cr.paint()

        cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.select_font_face("Sans", 0, 0)
        cr.set_font_size(14)
        text = "No data available"
        extents = cr.text_extents(text)
        cr.move_to((width - extents.width) / 2, height / 2)
        cr.show_text(text)
