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


# Adwaita color palette
class AdwaitaColors:
    """Adwaita color scheme."""
    BLUE_1 = (0.39, 0.58, 0.93)      # #62a0ea
    BLUE_2 = (0.20, 0.47, 0.90)      # #3584e4
    BLUE_3 = (0.11, 0.44, 0.85)      # #1c71d8
    BLUE_4 = (0.04, 0.37, 0.78)      # #0a57c5
    BLUE_5 = (0.03, 0.31, 0.63)      # #084d9f

    GREEN_1 = (0.55, 0.89, 0.56)     # #8ce98e
    GREEN_2 = (0.38, 0.78, 0.52)     # #57e389
    GREEN_3 = (0.15, 0.64, 0.41)     # #26a269
    GREEN_4 = (0.12, 0.52, 0.36)     # #1e8558
    GREEN_5 = (0.09, 0.43, 0.30)     # #176d4c

    ORANGE_1 = (1.00, 0.75, 0.53)    # #ffc988
    ORANGE_2 = (1.00, 0.62, 0.29)    # #ffa04a
    ORANGE_3 = (1.00, 0.47, 0.16)    # #ff7800
    ORANGE_4 = (0.90, 0.38, 0.07)    # #e66100

    PURPLE_1 = (0.87, 0.68, 0.98)    # #dcadfa
    PURPLE_2 = (0.78, 0.47, 0.99)    # #c778fc
    PURPLE_3 = (0.61, 0.31, 0.85)    # #9b4fd9

    RED_1 = (0.98, 0.55, 0.58)       # #f96f95
    RED_2 = (0.95, 0.26, 0.36)       # #f2355d
    RED_3 = (0.89, 0.15, 0.29)       # #e32649

    GRAY_1 = (0.98, 0.98, 0.98)      # #f9f9f9
    GRAY_2 = (0.95, 0.95, 0.95)      # #f2f2f2
    GRAY_3 = (0.87, 0.87, 0.87)      # #dddddd
    GRAY_4 = (0.80, 0.80, 0.80)      # #cccccc
    GRAY_5 = (0.60, 0.60, 0.60)      # #999999

    BACKGROUND = (1.0, 1.0, 1.0)
    TEXT = (0.13, 0.13, 0.13)        # #212121
    TEXT_SECONDARY = (0.45, 0.45, 0.45)  # #737373


class ModernHistogramChart(Gtk.DrawingArea):
    """A beautiful modern histogram chart with Adwaita styling."""

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

        # Draw background
        cr.set_source_rgb(*AdwaitaColors.BACKGROUND)
        cr.paint()

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

        # Draw pageviews points
        for i, value in enumerate(pageviews):
            x = margin_left + (plot_width / (len(pageviews) - 1)) * i
            y = margin_top + plot_height - (value / max_value) * plot_height

            # Outer glow
            cr.arc(x, y, 5, 0, 2 * math.pi)
            cr.set_source_rgba(*AdwaitaColors.BLUE_2, 0.3)
            cr.fill()

            # Main point
            cr.arc(x, y, 3.5, 0, 2 * math.pi)
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

        # Draw title
        cr.set_source_rgb(*AdwaitaColors.TEXT)
        cr.select_font_face("Sans", 0, 1)
        cr.set_font_size(16)
        title = "Pageviews & Visitors"
        extents = cr.text_extents(title)
        cr.move_to((width - extents.width) / 2, 25)
        cr.show_text(title)

        # Draw legend with rounded rectangles
        legend_x = margin_left + plot_width - 160
        legend_y = margin_top + 15

        # Legend background
        self._draw_rounded_rect(cr, legend_x - 10, legend_y - 8, 150, 45, 8)
        cr.set_source_rgba(*AdwaitaColors.BACKGROUND, 0.95)
        cr.fill_preserve()
        cr.set_source_rgba(*AdwaitaColors.GRAY_3, 0.5)
        cr.set_line_width(1)
        cr.stroke()

        # Pageviews legend
        self._draw_rounded_rect(cr, legend_x, legend_y, 18, 8, 4)
        cr.set_source_rgb(*AdwaitaColors.BLUE_3)
        cr.fill()

        cr.set_source_rgb(*AdwaitaColors.TEXT)
        cr.set_font_size(11)
        cr.select_font_face("Sans", 0, 0)
        cr.move_to(legend_x + 25, legend_y + 8)
        cr.show_text("Pageviews")

        # Visitors legend
        self._draw_rounded_rect(cr, legend_x, legend_y + 20, 18, 8, 4)
        cr.set_source_rgb(*AdwaitaColors.GREEN_3)
        cr.fill()

        cr.set_source_rgb(*AdwaitaColors.TEXT)
        cr.move_to(legend_x + 25, legend_y + 28)
        cr.show_text("Visitors")

    def _draw_rounded_rect(self, cr, x, y, width, height, radius):
        """Draw a rounded rectangle path."""
        cr.new_sub_path()
        cr.arc(x + width - radius, y + radius, radius, -math.pi/2, 0)
        cr.arc(x + width - radius, y + height - radius, radius, 0, math.pi/2)
        cr.arc(x + radius, y + height - radius, radius, math.pi/2, math.pi)
        cr.arc(x + radius, y + radius, radius, math.pi, 3*math.pi/2)
        cr.close_path()

    def _draw_empty(self, cr, width, height):
        """Draw empty state."""
        cr.set_source_rgb(*AdwaitaColors.BACKGROUND)
        cr.paint()

        cr.set_source_rgb(*AdwaitaColors.TEXT_SECONDARY)
        cr.select_font_face("Sans", 0, 0)
        cr.set_font_size(14)
        text = "No data available"
        extents = cr.text_extents(text)
        cr.move_to((width - extents.width) / 2, height / 2)
        cr.show_text(text)
