#!/bin/zsh
set -e

echo "🚀 Installing macOS Downloads Organizer..."

# Determine python3 executable
PYTHON_BIN=$(which python3)
if [[ -z "$PYTHON_BIN" ]]; then
    echo "❌ Error: Python 3 is not installed or not in PATH."
    exit 1
fi

# Detect absolute real binary path for python3 (important for macOS TCC)
REAL_PYTHON=$("$PYTHON_BIN" -c "import sys; print(sys.executable)")

# Paths
INSTALL_BIN="$HOME/.local/bin/organize_downloads.py"
PLIST_LABEL="com.$USER.downloads.organizer"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_LABEL.plist"
LOG_DIR="$HOME/Library/Logs"

# 1. Install Python script
mkdir -p "$HOME/.local/bin"
cp organize_downloads.py "$INSTALL_BIN"
chmod +x "$INSTALL_BIN"
echo "✅ Installed script to $INSTALL_BIN"

# 2. Setup LaunchAgent plist
mkdir -p "$HOME/Library/LaunchAgents"
cat << PLIST_EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>$REAL_PYTHON</string>
        <string>$INSTALL_BIN</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>StandardOutPath</key>
    <string>$LOG_DIR/downloads-organizer.log</string>
    <key>StandardErrorPath</key>
    <string>$LOG_DIR/downloads-organizer.err.log</string>
</dict>
</plist>
PLIST_EOF
echo "✅ Generated LaunchAgent at $PLIST_PATH"

# 3. Load or reload the launchd service
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load -w "$PLIST_PATH"
echo "✅ Background service loaded (runs every hour & at login)."

# 4. macOS Privacy Notice (Full Disk Access)
echo ""
echo "🔐 IMPORTANT macOS PERMISSION STEP:"
echo "macOS protects ~/Downloads from background processes."
echo "You must grant Full Disk Access to your Python binary:"
echo "👉 $REAL_PYTHON"
echo ""
echo "Opening System Settings > Privacy & Security > Full Disk Access now..."
open "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles" || true
echo "In System Settings:"
echo "  1. Click the '+' button."
echo "  2. Press Cmd + Shift + G and paste: $REAL_PYTHON"
echo "  3. Click Open and toggle it ON."
echo ""
echo "🎉 Installation complete! View logs anytime with:"
echo "   tail -f $LOG_DIR/downloads-organizer.log"
