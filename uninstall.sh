#!/bin/zsh
set -e

echo "🧹 Uninstalling macOS Downloads Organizer..."

PLIST_LABEL="com.$USER.downloads.organizer"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_LABEL.plist"
INSTALL_BIN="$HOME/.local/bin/organize_downloads.py"

# Unload service
if [[ -f "$PLIST_PATH" ]]; then
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
    rm -f "$PLIST_PATH"
    echo "✅ Unloaded and removed LaunchAgent."
fi

# Remove binary
if [[ -f "$INSTALL_BIN" ]]; then
    rm -f "$INSTALL_BIN"
    echo "✅ Removed script from $INSTALL_BIN."
fi

echo "🎉 Uninstallation complete. (Your existing folders in ~/Downloads were untouched)."
