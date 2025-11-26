#!/bin/bash
# Installation script for Simple Analytics Viewer
# This script installs the application and sets up required system files

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Simple Analytics Viewer Installation${NC}"
echo "========================================"
echo

# Determine install location
if [ "$1" == "--user" ] || [ -z "$1" ]; then
    INSTALL_MODE="user"
    SCHEMA_DIR="$HOME/.local/share/glib-2.0/schemas"
    DESKTOP_DIR="$HOME/.local/share/applications"
    METAINFO_DIR="$HOME/.local/share/metainfo"
    echo -e "Installing for ${YELLOW}current user${NC} only"
elif [ "$1" == "--system" ]; then
    INSTALL_MODE="system"
    SCHEMA_DIR="/usr/share/glib-2.0/schemas"
    DESKTOP_DIR="/usr/share/applications"
    METAINFO_DIR="/usr/share/metainfo"
    echo -e "Installing ${YELLOW}system-wide${NC} (requires sudo)"
else
    echo -e "${RED}Usage: $0 [--user|--system]${NC}"
    echo "  --user     Install for current user (default)"
    echo "  --system   Install system-wide (requires sudo)"
    exit 1
fi

echo

# Check for required directories
echo "Creating directories..."
mkdir -p "$SCHEMA_DIR"
mkdir -p "$DESKTOP_DIR"
mkdir -p "$METAINFO_DIR"

# Install GSettings schema
echo "Installing GSettings schema..."
if [ "$INSTALL_MODE" == "system" ]; then
    sudo cp analytics_viewer/org.andypiper.SimpleAnalyticsViewer.gschema.xml "$SCHEMA_DIR/"
    sudo glib-compile-schemas "$SCHEMA_DIR"
else
    cp analytics_viewer/org.andypiper.SimpleAnalyticsViewer.gschema.xml "$SCHEMA_DIR/"
    glib-compile-schemas "$SCHEMA_DIR"
fi
echo -e "${GREEN}✓${NC} GSettings schema installed"

# Install desktop file
echo "Installing desktop file..."
if [ "$INSTALL_MODE" == "system" ]; then
    sudo cp data/org.andypiper.SimpleAnalyticsViewer.desktop "$DESKTOP_DIR/"
    sudo update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
else
    cp data/org.andypiper.SimpleAnalyticsViewer.desktop "$DESKTOP_DIR/"
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi
echo -e "${GREEN}✓${NC} Desktop file installed"

# Install metainfo file
echo "Installing AppData metadata..."
if [ "$INSTALL_MODE" == "system" ]; then
    sudo cp data/org.andypiper.SimpleAnalyticsViewer.metainfo.xml "$METAINFO_DIR/"
else
    cp data/org.andypiper.SimpleAnalyticsViewer.metainfo.xml "$METAINFO_DIR/"
fi
echo -e "${GREEN}✓${NC} Metadata installed"

# Install Python package
echo
echo "Installing Python package..."
if [ "$INSTALL_MODE" == "system" ]; then
    sudo pip install -e .
else
    pip install --user -e .
fi
echo -e "${GREEN}✓${NC} Python package installed"

echo
echo -e "${GREEN}Installation complete!${NC}"
echo
echo "You can now launch the app from your application menu"
echo "or run 'analytics-viewer' from the command line."
echo
echo "Note: You may need to log out and back in for the"
echo "application menu entry to appear."
