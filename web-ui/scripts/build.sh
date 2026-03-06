#!/bin/bash

set -e

echo "=========================================="
echo "Sentinel Prime - Multi-Platform Build"
echo "=========================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WEB_UI_DIR="$PROJECT_ROOT/web-ui/web-ui"
DESKTOP_DIR="$PROJECT_ROOT/web-ui/desktop"

cd "$PROJECT_ROOT"

show_usage() {
    echo "Usage: $0 <platform>"
    echo ""
    echo "Platforms:"
    echo "  web        - Build web version (React Native Web)"
    echo "  android    - Build Android APK (requires Android SDK)"
    echo "  ios        - Build iOS (requires macOS and Xcode)"
    echo "  desktop    - Build Electron desktop app (Windows/Linux/Mac)"
    echo "  all        - Build all platforms"
    echo ""
    echo "Examples:"
    echo "  $0 web           # Build web version"
    echo "  $0 android      # Build Android APK"
    echo "  $0 desktop      # Build desktop app"
    echo "  $0 all          # Build everything"
}

build_web() {
    echo "Building web version..."
    cd "$WEB_UI_DIR"
    npx expo export --platform web
    mkdir -p "$DESKTOP_DIR/web-build"
    cp -r dist/* "$DESKTOP_DIR/web-build/" 2>/dev/null || true
    echo "Web build complete!"
}

build_android() {
    echo "Building Android APK..."
    cd "$WEB_UI_DIR"
    
    if ! command -v expo &> /dev/null; then
        echo "Error: Expo CLI not found. Install with: npm install -g expo-cli"
        exit 1
    fi
    
    npx expo prebuild --platform android
    cd android
    ./gradlew assembleRelease
    echo "Android APK built successfully!"
}

build_ios() {
    echo "Building iOS app..."
    cd "$WEB_UI_DIR"
    
    if [[ "$OSTYPE" != "darwin"* ]]; then
        echo "Error: iOS builds require macOS"
        exit 1
    fi
    
    npx expo prebuild --platform ios
    cd ios
    xcodebuild -workspace Runner.xcworkspace -scheme Runner -configuration Release archive
    echo "iOS build complete!"
}

build_desktop() {
    echo "Building desktop app..."
    cd "$DESKTOP_DIR"
    
    npm install
    
    echo "Building web assets first..."
    cd "$WEB_UI_DIR"
    npx expo export --platform web
    
    mkdir -p "$DESKTOP_DIR/web-build"
    cp -r "$WEB_UI_DIR/dist/"* "$DESKTOP_DIR/web-build/" 2>/dev/null || true
    
    cd "$DESKTOP_DIR"
    
    if [ "$1" = "win" ]; then
        npx electron-builder --win
    elif [ "$1" = "linux" ]; then
        npx electron-builder --linux
    elif [ "$1" = "mac" ]; then
        npx electron-builder --mac
    else
        npx electron-builder -mwl
    fi
    
    echo "Desktop build complete!"
}

build_all() {
    build_web
    build_desktop all
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        build_ios
    fi
    
    if command -v adb &> /dev/null; then
        build_android
    fi
    
    echo "All builds complete!"
}

PLATFORM="${1:-all}"

case $PLATFORM in
    web)
        build_web
        ;;
    android)
        build_android
        ;;
    ios)
        build_ios
        ;;
    desktop)
        build_desktop all
        ;;
    all)
        build_all
        ;;
    *)
        echo "Error: Unknown platform '$PLATFORM'"
        show_usage
        exit 1
        ;;
esac

echo "=========================================="
echo "Build finished!"
echo "=========================================="
