#!/bin/bash
# Deployment script for The Earth's Pharmacy Public Website
# This script enforces an allowlist policy for GitHub Pages deployment.

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
MANIFEST_PATH="$REPO_ROOT/config/public-content-manifest.json"
DEPLOY_DIR="$REPO_ROOT/deploy_output"

# Clean previous output
rm -rf "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

echo "Starting allowlist-based deployment build..."

# Read approved paths from manifest
APPROVED_PATHS=$(python3 -c "import json; print(' '.join(json.load(open('$MANIFEST_PATH'))['approved_public_paths']))")

for path in $APPROVED_PATHS; do
    if [ -e "$REPO_ROOT/$path" ]; then
        echo "Copying approved path: $path"
        mkdir -p "$DEPLOY_DIR/$(dirname "$path")"
        cp -r "$REPO_ROOT/$path" "$DEPLOY_DIR/$path"
    else
        echo "WARNING: Approved path '$path' not found in repository root."
    fi
done

# Run validation before final approval
python3 "$REPO_ROOT/scripts/validate-deployment.py"
if [ $? -eq 0 ]; then
    echo "Deployment build complete and validated in $DEPLOY_DIR"
else
    echo "CRITICAL: Deployment validation failed. Aborting."
    exit 1
fi
