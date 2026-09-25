#!/usr/bin/env bash
# Package basivo-operator into an installable archive. Validates first; refuses to
# package if the validator reports errors.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME="$(python3 -c "import json,sys;print(json.load(open('$ROOT/.claude-plugin/plugin.json'))['name'])")"
VERSION="$(python3 -c "import json,sys;print(json.load(open('$ROOT/.claude-plugin/plugin.json'))['version'])")"
OUT="$ROOT/dist/${NAME}-${VERSION}.zip"

echo "==> Validating…"
python3 "$ROOT/scripts/validate-plugin.py"

echo "==> Packaging ${NAME} ${VERSION}…"
mkdir -p "$ROOT/dist"
rm -f "$OUT"

# Zip the plugin, excluding VCS, build output, local config, and audit data.
( cd "$ROOT" && zip -r -q "$OUT" . \
    -x "dist/*" \
    -x ".git/*" \
    -x "**/__pycache__/*" \
    -x "config/allowed-sites.json" \
    -x ".basivo-operator/*" )

echo "==> Wrote $OUT"
ls -lh "$OUT"
