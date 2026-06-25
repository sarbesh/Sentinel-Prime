#!/bin/bash

# Generate version SHA for the UI build
# This SHA is used for client-side version checking

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_UI_DIR="$SCRIPT_DIR/web-ui"
VERSION_FILE="$SCRIPT_DIR/backend/ui_version.json"

echo "Generating UI version SHA..."

cd "$WEB_UI_DIR/web-ui"

# Export web build
npx expo export --platform web --output-dir dist 2>&1 | tail -3

# Generate SHA256 hash of the main JS bundle
if [ -f "dist/_expo/static/js/web/index-"*.js ]; then
    JS_FILE=$(ls dist/_expo/static/js/web/index-*.js | head -1)
    SHA=$(sha256sum "$JS_FILE" | cut -d' ' -f1 | cut -c1-16)
    echo "UI Version SHA: $SHA"
    
    # Create version file
    cat > "$VERSION_FILE" << EOF
{
    "sha": "$SHA",
    "timestamp": "$(date -Iseconds)",
    "build": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')"
}
EOF
    
    echo "Version file created: $VERSION_FILE"
    cat "$VERSION_FILE"
else
    echo "Error: JS bundle not found"
    exit 1
fi

# Copy files to docker folder
cp -r dist/* "$WEB_UI_DIR/docker/" 2>/dev/null || true

echo "Done!"
