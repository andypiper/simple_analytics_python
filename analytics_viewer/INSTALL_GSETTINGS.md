# Installing GSettings Schema

For credential persistence to work, you need to install the GSettings schema.

## User Install (Recommended)

Install the schema for your user only (no sudo required):

```bash
# From the analytics_viewer directory
mkdir -p ~/.local/share/glib-2.0/schemas/
cp analytics_viewer/org.andypiper.SimpleAnalyticsViewer.gschema.xml ~/.local/share/glib-2.0/schemas/
glib-compile-schemas ~/.local/share/glib-2.0/schemas/
```

## System Install (Alternative)

Install system-wide (requires sudo):

```bash
# From the analytics_viewer directory
sudo cp analytics_viewer/org.andypiper.SimpleAnalyticsViewer.gschema.xml /usr/share/glib-2.0/schemas/
sudo glib-compile-schemas /usr/share/glib-2.0/schemas/
```

## Verify Installation

```bash
# Check if schema is installed
gsettings list-schemas | grep org.andypiper.SimpleAnalyticsViewer

# View current settings (use dconf commands to read/verify the actual values)
dconf list /org/andypiper/simpleanalytics/

# Get specific settings
dconf read /org/andypiper/simpleanalytics/api-key
dconf read /org/andypiper/simpleanalytics/user-id
dconf read /org/andypiper/simpleanalytics/hostname
```

## Migrating from Old Schema

If you were using the old `com.simpleanalytics.viewer` schema, the app will automatically migrate your settings. To clean up the old schema:

```bash
# Remove old values from dconf
dconf reset -f /com/simpleanalytics/viewer/

# Remove old schema file (user install)
rm ~/.local/share/glib-2.0/schemas/com.simpleanalytics.viewer.gschema.xml
glib-compile-schemas ~/.local/share/glib-2.0/schemas/

# Or for system install (requires sudo)
sudo rm /usr/share/glib-2.0/schemas/com.simpleanalytics.viewer.gschema.xml
sudo glib-compile-schemas /usr/share/glib-2.0/schemas/
```

## Uninstall

User install:
```bash
rm ~/.local/share/glib-2.0/schemas/org.andypiper.SimpleAnalyticsViewer.gschema.xml
glib-compile-schemas ~/.local/share/glib-2.0/schemas/
```

System install:
```bash
sudo rm /usr/share/glib-2.0/schemas/org.andypiper.SimpleAnalyticsViewer.gschema.xml
sudo glib-compile-schemas /usr/share/glib-2.0/schemas/
```

## Without GSettings

If you don't install the schema, the app will still work but credentials won't persist between sessions. You'll need to re-enter them each time you run the app, or use environment variables:

```bash
export SA_API_KEY="your-api-key"
export SA_USER_ID="your-user-id"
python -m analytics_viewer.main
```
