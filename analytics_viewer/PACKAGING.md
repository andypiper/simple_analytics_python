# Packaging Guide

This document explains the packaging setup for Simple Analytics Viewer and how to create distribution packages.

## Package Structure

```
analytics_viewer/
├── analytics_viewer/           # Main Python package
│   ├── *.py                   # Python modules
│   ├── views/                 # View modules
│   ├── style.css              # Application CSS
│   └── *.gschema.xml          # GSettings schema
├── data/                      # Application data files
│   ├── *.desktop              # Desktop entry
│   └── *.metainfo.xml         # AppStream metadata
├── pyproject.toml             # Python package configuration
├── MANIFEST.in                # Package data manifest
├── install.sh                 # Installation script
└── uninstall.sh               # Uninstallation script
```

## Current Packaging Status

### ✅ Completed

- [x] Python package with pyproject.toml (PEP 621)
- [x] Desktop file for application launcher
- [x] AppStream metadata for app stores
- [x] GSettings schema for configuration
- [x] Installation/uninstallation scripts
- [x] Package data configuration
- [x] Console script entry point

### 📋 Future Packaging Options

- [ ] Flatpak manifest (recommended for GNOME apps)
- [ ] .deb package (Debian/Ubuntu)
- [ ] .rpm package (Fedora/RHEL)
- [ ] AUR package (Arch Linux)
- [ ] AppImage (universal Linux)

## Installation Methods

### 1. User Installation (Recommended for Development)

```bash
./install.sh --user
```

Installs to:
- Python: `~/.local/lib/python3.X/site-packages/`
- Binary: `~/.local/bin/analytics-viewer`
- Desktop: `~/.local/share/applications/`
- Schema: `~/.local/share/glib-2.0/schemas/`
- Metainfo: `~/.local/share/metainfo/`

### 2. System Installation (Requires sudo)

```bash
./install.sh --system
```

Installs to:
- Python: `/usr/local/lib/python3.X/site-packages/`
- Binary: `/usr/local/bin/analytics-viewer`
- Desktop: `/usr/share/applications/`
- Schema: `/usr/share/glib-2.0/schemas/`
- Metainfo: `/usr/share/metainfo/`

### 3. Development Mode (No Installation)

```bash
python -m analytics_viewer.main
```

## Building Distribution Packages

### Python Wheel/Source Distribution

```bash
# Install build tools
pip install build

# Build distribution packages
python -m build

# Output in dist/:
# - simple_analytics_viewer-0.1.0-py3-none-any.whl
# - simple_analytics_viewer-0.1.0.tar.gz
```

### Flatpak (Future)

Flatpak is the recommended distribution format for GNOME applications. To create a Flatpak:

1. Create `org.andypiper.SimpleAnalyticsViewer.json` manifest
2. Define runtime (org.gnome.Platform)
3. List dependencies
4. Build with flatpak-builder
5. Submit to Flathub

Benefits:
- Sandboxed security
- Automatic updates
- Works across all distributions
- Available in GNOME Software

### AppImage (Future)

For a portable, distribution-agnostic package:

1. Use linuxdeploy or similar tool
2. Bundle GTK4/Adwaita libraries
3. Create self-contained executable
4. Distribute single .AppImage file

## Validation

### Desktop File

```bash
desktop-file-validate data/org.andypiper.SimpleAnalyticsViewer.desktop
```

### Metainfo File

```bash
appstreamcli validate data/org.andypiper.SimpleAnalyticsViewer.metainfo.xml
```

### GSettings Schema

```bash
glib-compile-schemas --strict --dry-run analytics_viewer/
```

## Dependencies

### Runtime Dependencies

- Python >= 3.12
- PyGObject >= 3.46.0
- GTK4
- libadwaita
- simple-analytics-python (API client)

### Build Dependencies

- setuptools >= 61.0
- wheel
- build (optional, for creating distributions)

### System Dependencies

GTK4 and libadwaita must be installed system-wide (cannot be pip installed).

## Distribution Checklist

Before distributing:

- [ ] Update version in pyproject.toml
- [ ] Update changelog in metainfo.xml
- [ ] Test installation on clean system
- [ ] Verify desktop file appears in application menu
- [ ] Verify GSettings schema is installed correctly
- [ ] Test uninstallation completely removes files
- [ ] Run validation tools on .desktop and .metainfo.xml
- [ ] Update README.md with new features
- [ ] Tag release in git

## Icon

Currently using the generic `org.gnome.Analytics` icon. For production distribution:

1. Create custom icon (SVG preferred)
2. Provide multiple sizes (16x16, 32x32, 48x48, 64x64, 128x128)
3. Follow GNOME icon guidelines
4. Install to `/usr/share/icons/hicolor/` or `~/.local/share/icons/hicolor/`
5. Update icon name in .desktop and metainfo.xml files
6. Run `gtk-update-icon-cache`

## Future Distribution Targets

### Flathub

1. Create Flatpak manifest
2. Test locally with flatpak-builder
3. Submit to flathub/flathub repository
4. Automated builds and updates

### Fedora COPR

1. Create .spec file
2. Set up COPR repository
3. Automatic RPM builds for Fedora/RHEL

### AUR (Arch User Repository)

1. Create PKGBUILD
2. Submit to AUR
3. Community maintenance

## License

Ensure all files include proper license headers (MIT).
