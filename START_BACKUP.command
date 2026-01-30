#!/bin/bash
# USB Backup Tool – macOS launcher
# Double-click this file on the USB stick to launch the backup GUI.

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Try compiled app first, then fall back to Python.
if [ -f "$DIR/USB-Backup-Tool" ]; then
    "$DIR/USB-Backup-Tool" &
elif command -v python3 &>/dev/null; then
    python3 "$DIR/main.py"
else
    osascript -e 'display dialog "Python 3 not found. Please install Python 3.10+." buttons {"OK"} default button "OK"'
fi
