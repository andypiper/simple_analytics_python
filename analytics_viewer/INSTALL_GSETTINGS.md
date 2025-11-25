# Installing GSettings Schema

For credential persistence to work, you need to install the GSettings schema.

## User Install (Recommended)

Install the schema for your user only (no sudo required):

```bash
# From the analytics_viewer directory
mkdir -p ~/.local/share/glib-2.0/schemas/
cp analytics_viewer/com.simpleanalytics.viewer.gschema.xml ~/.local/share/glib-2.0/schemas/
glib-compile-schemas ~/.local/share/glib-2.0/schemas/
```

## System Install (Alternative)

Install system-wide (requires sudo):

```bash
# From the analytics_viewer directory
sudo cp analytics_viewer/com.simpleanalytics.viewer.gschema.xml /usr/share/glib-2.0/schemas/
sudo glib-compile-schemas /usr/share/glib-2.0/schemas/
```

## Verify Installation

```bash
# Check if schema is installed
gsettings list-schemas | grep com.simpleanalytics.viewer

# View current settings (NOTE: Due to a gsettings quirk with schemas that have a path,
# you should use dconf commands to read/verify the actual values)
dconf list /com/simpleanalytics/viewer/

# Get specific settings (use dconf instead of gsettings)
dconf read /com/simpleanalytics/viewer/api-key
dconf read /com/simpleanalytics/viewer/user-id
dconf read /com/simpleanalytics/viewer/hostname
```

## Uninstall

User install:
```bash
rm ~/.local/share/glib-2.0/schemas/com.simpleanalytics.viewer.gschema.xml
glib-compile-schemas ~/.local/share/glib-2.0/schemas/
```

System install:
```bash
sudo rm /usr/share/glib-2.0/schemas/com.simpleanalytics.viewer.gschema.xml
sudo glib-compile-schemas /usr/share/glib-2.0/schemas/
```

## Without GSettings

If you don't install the schema, the app will still work but credentials won't persist between sessions. You'll need to re-enter them each time you run the app, or use environment variables:

```bash
export SA_API_KEY="your-api-key"
export SA_USER_ID="your-user-id"
python -m analytics_viewer.main
```
