#!/bin/bash

set -euo pipefail

# Deployment script for The Earth's Pharmacy Public Website.
# Builds a fresh GitHub Pages artifact from an explicit allowlist,
# then validates the ACTUAL deploy_output artifact before deployment.

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
MANIFEST_PATH="$REPO_ROOT/config/public-content-manifest.json"
DEPLOY_DIR="$REPO_ROOT/deploy_output"
VALIDATOR="$REPO_ROOT/scripts/validate-deployment.py"

echo "Starting allowlist-based deployment build..."

# Always start from a clean deployment artifact.
rm -rf "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

# Read approved paths safely, one path per line.
mapfile -t APPROVED_PATHS < <(
    python3 - "$MANIFEST_PATH" <<'PY'
import json
import sys

manifest_path = sys.argv[1]

with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

for path in manifest.get("approved_public_paths", []):
    print(path)
PY
)

if [ "${#APPROVED_PATHS[@]}" -eq 0 ]; then
    echo "CRITICAL: No approved public paths found in manifest."
    exit 1
fi

for path in "${APPROVED_PATHS[@]}"; do
    source_path="$REPO_ROOT/$path"
    destination_path="$DEPLOY_DIR/$path"

    if [ ! -e "$source_path" ]; then
        echo "CRITICAL: Approved public path not found: $path"
        exit 1
    fi

    echo "Copying approved path: $path"

    if [ -d "$source_path" ]; then
        mkdir -p "$destination_path"
        cp -R "$source_path"/. "$destination_path"/
    else
        mkdir -p "$(dirname "$destination_path")"
        cp "$source_path" "$destination_path"
    fi
done

echo "Running deployment artifact validation..."

python3 "$VALIDATOR" "$DEPLOY_DIR"

echo "Deployment build complete and validated:"
echo "$DEPLOY_DIR"
