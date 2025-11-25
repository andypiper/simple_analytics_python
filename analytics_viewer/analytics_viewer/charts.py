"""Chart utilities for rendering matplotlib charts in GTK."""

import gi
import io
from typing import Any

gi.require_version("Gtk", "4.0")
gi.require_version("GdkPixbuf", "2.0")

from gi.repository import Gtk, GdkPixbuf, Gdk

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from PIL import Image


def create_chart_image(figure: Figure, width: int = 800, height: int = 400) -> Gtk.Picture:
    """
    Convert a matplotlib figure to a GTK Picture widget.

    Args:
        figure: Matplotlib figure to render
        width: Width in pixels
        height: Height in pixels

    Returns:
        GTK Picture widget containing the rendered chart
    """
    # Set figure size
    dpi = 100
    figure.set_size_inches(width / dpi, height / dpi)
    figure.set_dpi(dpi)

    # Render to buffer
    buf = io.BytesIO()
    figure.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
    buf.seek(0)

    # Load as PIL Image
    pil_image = Image.open(buf)

    # Convert to GdkPixbuf
    img_bytes = io.BytesIO()
    pil_image.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    # Create GdkPixbuf from bytes
    loader = GdkPixbuf.PixbufLoader.new_with_type('png')
    loader.write(img_bytes.read())
    loader.close()
    pixbuf = loader.get_pixbuf()

    # Create GTK Picture
    texture = Gdk.Texture.new_for_pixbuf(pixbuf)
    picture = Gtk.Picture.new_for_paintable(texture)
    picture.set_can_shrink(True)
    picture.set_content_fit(Gtk.ContentFit.SCALE_DOWN)

    plt.close(figure)

    return picture


def create_histogram_chart(histogram: list[dict[str, Any]],
                          title: str = "Pageviews Over Time",
                          width: int = 800,
                          height: int = 400) -> Gtk.Picture:
    """
    Create a line chart for histogram data.

    Args:
        histogram: List of histogram data points
        title: Chart title
        width: Width in pixels
        height: Height in pixels

    Returns:
        GTK Picture widget with the chart
    """
    if not histogram:
        # Return empty picture
        return Gtk.Picture()

    # Extract data
    dates = [point.get("date", "") for point in histogram]
    pageviews = [point.get("pageviews", 0) for point in histogram]
    visitors = [point.get("visitors", 0) for point in histogram]

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 4))

    # Plot lines
    ax.plot(range(len(dates)), pageviews, marker='o', linewidth=2,
            markersize=4, label='Pageviews', color='#1c71d8')
    ax.plot(range(len(dates)), visitors, marker='o', linewidth=2,
            markersize=4, label='Visitors', color='#26a269')

    # Styling
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=10)
    ax.set_ylabel('Count', fontsize=10)
    ax.legend(loc='upper left', frameon=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--')

    # Set x-axis labels (show every 5th date)
    step = max(1, len(dates) // 10)
    tick_indices = list(range(0, len(dates), step))
    tick_labels = [dates[i][5:] if len(dates[i]) >= 10 else dates[i] for i in tick_indices]
    ax.set_xticks(tick_indices)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right')

    # Format y-axis with commas
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

    fig.tight_layout()

    return create_chart_image(fig, width, height)


def create_bar_chart(data: list[tuple[str, int]],
                     title: str = "Top Items",
                     xlabel: str = "Count",
                     color: str = '#1c71d8',
                     width: int = 800,
                     height: int = 400,
                     max_items: int = 10) -> Gtk.Picture:
    """
    Create a horizontal bar chart.

    Args:
        data: List of (label, value) tuples
        title: Chart title
        xlabel: X-axis label
        color: Bar color
        width: Width in pixels
        height: Height in pixels
        max_items: Maximum number of items to show

    Returns:
        GTK Picture widget with the chart
    """
    if not data:
        return Gtk.Picture()

    # Limit and reverse for top-down display
    data = data[:max_items]
    labels, values = zip(*data)
    labels = list(labels)[::-1]
    values = list(values)[::-1]

    # Truncate long labels
    labels = [label[:40] + '...' if len(label) > 40 else label for label in labels]

    # Create figure
    fig, ax = plt.subplots(figsize=(8, max(4, len(labels) * 0.4)))

    # Create bars
    bars = ax.barh(range(len(labels)), values, color=color, alpha=0.8)

    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, values)):
        ax.text(value, i, f' {value:,}', va='center', fontsize=9)

    # Styling
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.grid(True, alpha=0.3, axis='x', linestyle='--')

    # Format x-axis with commas
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

    fig.tight_layout()

    return create_chart_image(fig, width, height)


def create_pie_chart(data: list[tuple[str, int]],
                     title: str = "Distribution",
                     width: int = 600,
                     height: int = 400,
                     max_items: int = 10) -> Gtk.Picture:
    """
    Create a pie chart.

    Args:
        data: List of (label, value) tuples
        title: Chart title
        width: Width in pixels
        height: Height in pixels
        max_items: Maximum number of slices (rest grouped as "Other")

    Returns:
        GTK Picture widget with the chart
    """
    if not data:
        return Gtk.Picture()

    # Group items beyond max_items as "Other"
    if len(data) > max_items:
        top_items = data[:max_items]
        other_value = sum(value for _, value in data[max_items:])
        data = top_items + [("Other", other_value)]

    labels, values = zip(*data)

    # Create figure
    fig, ax = plt.subplots(figsize=(6, 4))

    # Create pie chart
    colors = plt.cm.Set3(range(len(labels)))
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        textprops={'fontsize': 9}
    )

    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')

    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

    fig.tight_layout()

    return create_chart_image(fig, width, height)
