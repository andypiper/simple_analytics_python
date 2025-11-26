#!/bin/bash
# Uninstallation script for Simple Analytics Viewer

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Simple Analytics Viewer Uninstallation${NC}"
echo "=========================================="
echo

# Determine install location
if [ "$1" == "--user" ] || [ -z "$1" ]; then
    INSTALL_MODE="user"
    SCHEMA_DIR="$HOME/.local/share/glib-2.0/schemas"
    DESKTOP_DIR="$HOME/.local/share/applications"
    METAINFO_DIR="$HOME/.local/share/metainfo"
    echo -e "Uninstalling for ${YELLOW}current user${NC}"
elif [ "$1" == "--system" ]; then
    INSTALL_MODE="system"
    SCHEMA_DIR="/usr/share/glib-2.0/schemas"
    DESKTOP_DIR="/usr/share/applications"
    METAINFO_DIR="/usr/share/metainfo"
    echo -e "Uninstalling ${YELLOW}system-wide${NC} (requires sudo)"
else
    echo -e "${RED}Usage: $0 [--user|--system]${NC}"
    echo "  --user     Uninstall for current user (default)"
    echo "  --system   Uninstall system-wide (requires sudo)"
    exit 1
fi

echo

# Uninstall Python package
echo "Uninstalling Python package..."
if [ "$INSTALL_MODE" == "system" ]; then
    sudo pip uninstall -y simple-analytics-viewer || true
else
    pip uninstall -y simple-analytics-viewer || true
fi
echo -e "${GREEN}✓${NC} Python package uninstalled"

# Remove GSettings schema
echo "Removing GSettings schema..."
if [ "$INSTALL_MODE" == "system" ]; then
    sudo rm -f "$SCHEMA_DIR/org.andypiper.SimpleAnalyticsViewer.gschema.xml"
    sudo glib-compile-schemas "$SCHEMA_DIR" 2>/dev/null || true
else
    rm -f "$SCHEMA_DIR/org.andypiper.SimpleAnalyticsViewer.gschema.xml"
    glib-compile-schemas "$SCHEMA_DIR" 2>/dev/null || true
fi
echo -e "${GREEN}✓${NC} GSettings schema removed"

# Remove desktop file
echo "Removing desktop file..."
if [ "$INSTALL_MODE" == "system" ]; then
    sudo rm -f "$DESKTOP_DIR/org.andypiper.SimpleAnalyticsViewer.desktop"
    sudo update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
else
    rm -f "$DESKTOP_DIR/org.andypiper.SimpleAnalyticsViewer.desktop"
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi
echo -e "${GREEN}✓${NC} Desktop file removed"

# Remove metainfo file
echo "Removing AppData metadata..."
if [ "$INSTALL_MODE" == "system" ]; then
    sudo rm -f "$METAINFO_DIR/org.andypiper.SimpleAnalyticsViewer.metainfo.xml"
else
    rm -f "$METAINFO_DIR/org.andypiper.SimpleAnalyticsViewer.metainfo.xml"
fi
echo -e "${GREEN}✓${NC} Metadata removed"

echo
echo -e "${GREEN}Uninstallation complete!${NC}"
echo
echo "Note: Your settings and credentials in GSettings/dconf are preserved."
echo "To remove them as well, run:"
echo "  dconf reset -f /org/andypiper/simpleanalytics/"
