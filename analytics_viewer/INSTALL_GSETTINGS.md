# Installing GSettings Schema

For credential persistence to work, you need to install the GSettings schema.

## Quick Install (Development)

From the `analytics_viewer` directory, run:

```bash
# Compile and install the schema to your local directory
sudo cp analytics_viewer/com.simpleanalytics.viewer.gschema.xml /usr/share/glib-2.0/schemas/
sudo glib-compile-schemas /usr/share/glib-2.0/schemas/
```

## Verify Installation

```bash
# Check if schema is installed
gsettings list-schemas | grep com.simpleanalytics.viewer

# View current settings
gsettings list-keys com.simpleanalytics.viewer

# Get a specific setting
gsettings get com.simpleanalytics.viewer api-key
```

## Uninstall

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
