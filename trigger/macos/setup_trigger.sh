#!/bin/bash
# ---------------------------------------------------------------
# macOS: Install a LaunchAgent that triggers the backup tool
# whenever the USB stick volume is mounted.
#
# Usage:
#   chmod +x setup_trigger.sh
#   ./setup_trigger.sh "MY-USB-STICK"
#
# Replace MY-USB-STICK with the exact volume name of the stick
# as shown in /Volumes/ when plugged in.
# ---------------------------------------------------------------

VOLUME_NAME="${1:?Usage: $0 <volume-name>}"
PLIST_NAME="com.usb-backup.plist"
PLIST_SRC="$(cd "$(dirname "$0")" && pwd)/$PLIST_NAME"
PLIST_DST="$HOME/Library/LaunchAgents/$PLIST_NAME"

mkdir -p "$HOME/Library/LaunchAgents"

sed "s|__VOLUME_NAME__|$VOLUME_NAME|g" "$PLIST_SRC" > "$PLIST_DST"
launchctl load "$PLIST_DST"

echo ""
echo "LaunchAgent installed."
echo "The backup tool will launch when volume '$VOLUME_NAME' is mounted."
echo ""
echo "To uninstall:"
echo "  launchctl unload $PLIST_DST && rm $PLIST_DST"
echo ""
echo "Fallback: Double-click START_BACKUP.command on the USB stick."
