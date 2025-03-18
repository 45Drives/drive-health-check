#!/bin/bash
set -x
set -e

# Configuration: Set your remote hosts
WIN_HOST="user@192.168.209.83"
MAC_HOST="45drives@192.168.210.11"
LINUX_HOST="root@192.168.123.5"

REMOTE_BUILD_DIR="build_temp"
LOCAL_APP_DIR="$(dirname "$0")/app"
LOCAL_OUTPUT_DIR="$(dirname "$0")/builds"

mkdir -p "$LOCAL_OUTPUT_DIR"

# # Build on Windows
# echo "🔧 Building on Windows..."
# ssh "$WIN_HOST" "cmd.exe /c \"if not exist build_temp mkdir build_temp && if not exist build_temp\\app mkdir build_temp\\app\""
# scp -r "$LOCAL_APP_DIR" "$WIN_HOST:$REMOTE_BUILD_DIR"
# ssh "$WIN_HOST" "cd $REMOTE_BUILD_DIR && pyinstaller --onefile app/drive-checker.py --add-data app/bin/smartctl.exe;bin --add-binary bin/*.dll;."
# scp "$WIN_HOST:$REMOTE_BUILD_DIR/dist/drive-checker.exe" "$LOCAL_OUTPUT_DIR/drive-checker-windows.exe"

# # Build on Linux
# echo "🐧 Building on Linux..."
# ssh "$LINUX_HOST" "rm -rf $REMOTE_BUILD_DIR && mkdir -p $REMOTE_BUILD_DIR"
# scp -r "$LOCAL_APP_DIR" "$LINUX_HOST:$REMOTE_BUILD_DIR/app"
# ssh "$LINUX_HOST" "cd $REMOTE_BUILD_DIR && pyinstaller --onefile app/drive-checker.py --add-data 'app/bin/smartctl:bin'"
# scp "$LINUX_HOST:$REMOTE_BUILD_DIR/dist/drive-checker" "$LOCAL_OUTPUT_DIR/drive-checker-linux"

# Build on macOS
echo "🍏 Building on macOS..."
ssh "$MAC_HOST" "rm -rf $REMOTE_BUILD_DIR && mkdir -p $REMOTE_BUILD_DIR"
scp -r "$LOCAL_APP_DIR" "$MAC_HOST:$REMOTE_BUILD_DIR/app"

# Activate the Python environment and build
ssh "$MAC_HOST" "
    export PATH=\"/opt/homebrew/bin:\$PATH\" && \
    python3 -m venv drive-check && \
    source drive-check/bin/activate && \
    brew install gtk+3 gobject-introspection && \
    cd $REMOTE_BUILD_DIR && \
    pip install -r app/requirements.txt && \
    pyinstaller --onefile app/drive-checker.py --add-data 'app/bin_mac_arm/smartctl:bin'
"
scp "$MAC_HOST:$REMOTE_BUILD_DIR/dist/drive-checker" "$LOCAL_OUTPUT_DIR/drive-checker-mac"

echo "✅ All builds completed. Output is in: $LOCAL_OUTPUT_DIR"
