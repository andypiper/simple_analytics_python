# Simple Analytics Viewer

A beautiful GNOME GTK4 application for viewing your Simple Analytics data with an Adwaita design.

![GTK4](https://img.shields.io/badge/GTK-4-blue)
![Adwaita](https://img.shields.io/badge/Adwaita-1-orange)
![Python](https://img.shields.io/badge/Python-3.12+-green)

## Features

- 📊 **Dashboard** - Overview of pageviews, visitors, and events with ASCII charts
- 🎯 **Events Tracking** - View custom and automated events (outbound links, downloads, email clicks)
- 📄 **Pages Analytics** - Detailed breakdown of page performance
- 🌍 **Geographic Data** - Country-wise visitor breakdown with flag emojis
- 🎨 **Beautiful UI** - Native GNOME Adwaita design that fits perfectly with your desktop
- 🔐 **Secure** - Credentials stored in environment variables
- 🔄 **Real-time Refresh** - Update your data with a single click

## Screenshots

The app features:
- Clean, modern Adwaita interface
- View switcher for easy navigation
- Responsive design that adapts to window size
- Statistical cards showing key metrics
- ASCII charts for visualizing trends
- List views with proper hierarchy and icons

## Installation

### Prerequisites

1. **Python 3.12+**
2. **GTK4 and Adwaita** (usually pre-installed on GNOME)
3. **PyGObject** for Python GTK bindings

#### On Ubuntu/Debian:

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1
```

#### On Fedora:

```bash
sudo dnf install python3-gobject gtk4 libadwaita
```

#### On Arch Linux:

```bash
sudo pacman -S python-gobject gtk4 libadwaita
```

### Install the Application

```bash
cd analytics_viewer
pip install -e .
```

## Configuration

Set your Simple Analytics credentials as environment variables:

```bash
export SA_API_KEY="sa_api_key_xxxxxxxxxxxxxxxxxxxx"
export SA_USER_ID="sa_user_id_00000000-0000-0000-0000-000000000000"
export SA_HOSTNAME="your-website.com"  # Optional default website
```

Get your credentials from: https://simpleanalytics.com/account

### Persistent Configuration

To make credentials persist across sessions, add them to your `~/.bashrc` or `~/.profile`:

```bash
echo 'export SA_API_KEY="sa_api_key_xxxx"' >> ~/.bashrc
echo 'export SA_USER_ID="sa_user_id_xxxx"' >> ~/.bashrc
echo 'export SA_HOSTNAME="your-website.com"' >> ~/.bashrc
```

## Usage

### Running the App

```bash
# From anywhere (if installed)
analytics-viewer

# Or run directly
python -m analytics_viewer.src.main
```

### First Launch

1. If credentials aren't set, you'll be prompted to enter them
2. Click "Preferences" to configure your API key and User ID
3. Select a website from the dropdown in the header bar
4. Explore your analytics across different views!

### Navigation

- **Dashboard** - Overview with key metrics and charts
- **Events** - View all events (custom and automated)
- **Pages** - Detailed page-by-page analytics
- **Countries** - Geographic breakdown of visitors

### Keyboard Shortcuts

- `Ctrl+Q` - Quit the application
- `F10` - Open menu
- `Alt+←/→` - Navigate between views (if supported by your desktop)

## Features in Detail

### Dashboard View

- **Stats Cards**: Pageviews, visitors, and events at a glance
- **Histogram Chart**: ASCII visualization of pageviews over time (last 30 days)
- **Top Pages**: Quick list of your most visited pages

### Events View

- **Event Categories**: Separate counts for automated and custom events
- **Event Types**:
  - 🔗 Automated: outbound links, email clicks, downloads
  - ⭐ Custom: Your sa_event() tracked events
- **Detailed List**: All events with occurrence counts

### Pages View

- **Complete List**: All pages sorted by pageviews
- **Metrics**: Pageviews and unique visitors per page
- **Rankings**: See which content performs best

### Countries View

- **Flag Emojis**: Visual country identification
- **Progress Bars**: Percentage of total traffic per country
- **Detailed Stats**: Pageviews and visitors per country

## Development

### Project Structure

```
analytics_viewer/
├── src/
│   ├── main.py           # Application entry point
│   ├── window.py         # Main window class
│   ├── preferences.py    # Preferences dialog
│   └── views/
│       ├── dashboard.py  # Dashboard view
│       ├── events.py     # Events view
│       ├── pages.py      # Pages view
│       └── countries.py  # Countries view
├── pyproject.toml        # Project configuration
└── README.md            # This file
```

### Running in Development Mode

```bash
cd analytics_viewer
python -m src.main
```

### Architecture

The app follows the GNOME Human Interface Guidelines:
- Uses libadwaita for modern GNOME styling
- Implements proper view hierarchy with ViewStack
- Responsive design with ViewSwitcherBar for narrow windows
- Follows Adwaita color scheme and design patterns

## Troubleshooting

### "No module named 'gi'"

Install PyGObject:
```bash
pip install PyGObject
```

### "Cannot open display"

Make sure you're running on a system with a display server (X11 or Wayland).

### "Authentication error"

Double-check your API credentials:
- API key starts with `sa_api_key_`
- User ID starts with `sa_user_id_`
- Both can be found at https://simpleanalytics.com/account

### "No data available"

- Ensure the website has data for the selected date range
- Check that the website is added to your Simple Analytics account
- Try refreshing with the refresh button

## Contributing

Contributions are welcome! Some ideas for improvements:

- [ ] Add date range picker
- [ ] Export data to CSV/JSON
- [ ] Real-time updates with intervals
- [ ] More chart types (using matplotlib in a canvas)
- [ ] Referrer analytics view
- [ ] UTM parameter tracking view
- [ ] Browser/OS breakdown view
- [ ] Dark mode support (Adwaita handles this automatically!)

## License

MIT License - see the parent project's LICENSE file.

## Credits

- Built with [GTK4](https://gtk.org/) and [libadwaita](https://gnome.pages.gitlab.gnome.org/libadwaita/)
- Uses [Simple Analytics Python Client](https://github.com/andypiper/simple_analytics_python)
- Follows [GNOME Human Interface Guidelines](https://developer.gnome.org/hig/)

## Related Projects

- [Simple Analytics](https://simpleanalytics.com) - Privacy-friendly analytics
- [Simple Analytics Python Client](../simple_analytics/) - The underlying Python library
- [Terminal Examples](../examples/) - CLI examples with charts
