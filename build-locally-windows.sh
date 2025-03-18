#!/bin/bash
set -e  # Exit on error
set -x  # Debug mode

# Define directories
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
APP_DIR="$SCRIPT_DIR/app"
BUILD_DIR="$SCRIPT_DIR/build_temp"
OUTPUT_DIR="$SCRIPT_DIR/builds"

# Ensure output directories exist
mkdir -p "$BUILD_DIR" "$OUTPUT_DIR"

# Copy application files to build directory
echo "🔧 Copying application files..."
rm -rf "$BUILD_DIR"/*
cp -r "$APP_DIR" "$BUILD_DIR"

# Build the Windows executable using PyInstaller
echo "🚀 Building Windows executable..."
cd "$BUILD_DIR"
pyinstaller --onefile "app/drive-checker.py" --add-data "app/bin/smartctl.exe;bin" --add-binary "C:\Program Files\GTK3-Runtime Win64\bin\*.dll;."

# Move the built executable to the output folder
BUILT_EXE="$BUILD_DIR/dist/drive-checker.exe"
if [[ -f "$BUILT_EXE" ]]; then
    mv -f "$BUILT_EXE" "$OUTPUT_DIR/drive-checker-windows.exe"
    echo "✅ Build complete! Executable saved to: $OUTPUT_DIR/drive-checker-windows.exe"
else
    echo "❌ Build failed. Check for errors in PyInstaller output."
    exit 1
fi

# Cleanup build directory (optional)
echo "🧹 Cleaning up temporary files..."
rm -rf "$BUILD_DIR/dist" "$BUILD_DIR/build" "$BUILD_DIR/*.spec"

# Return to original location
cd "$SCRIPT_DIR"
