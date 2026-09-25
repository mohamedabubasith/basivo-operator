#!/usr/bin/env bash
# Launch the user's real Chrome with remote debugging on a DEDICATED profile, so
# the plugin's playwright-attached MCP (.mcp.json, CDP :9222) can drive a real,
# logged-in browser. Idempotent: if :9222 already answers, it just says so.
#
# Why a dedicated profile: since Chrome 136, --remote-debugging-port is IGNORED
# when --user-data-dir is your default profile. This profile persists, so you
# sign in to your sites ONCE and stay logged in across launches.
#
# Usage:  bash scripts/launch-chrome.sh [port]      (default port 9222)
set -euo pipefail

PORT="${1:-9222}"
PROFILE="${CHROME_BASIVO_PROFILE:-$HOME/.chrome-basivo}"

# Already listening? Then we're done.
if curl -fsS "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
  echo "✅ Chrome remote debugging already up on 127.0.0.1:${PORT}."
  echo "   Profile: ${PROFILE}"
  echo "   If you're not signed in to your target site yet, do it in that window."
  exit 0
fi

# Find a Chrome binary for this OS.
CHROME=""
case "$(uname -s)" in
  Darwin)
    for c in \
      "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
      "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta" \
      "/Applications/Chromium.app/Contents/MacOS/Chromium"; do
      [ -x "$c" ] && CHROME="$c" && break
    done
    ;;
  Linux)
    for c in google-chrome google-chrome-stable chromium chromium-browser; do
      command -v "$c" >/dev/null 2>&1 && CHROME="$(command -v "$c")" && break
    done
    ;;
  *)
    echo "⚠️  Unsupported OS for auto-launch. On Windows, run in PowerShell:"
    echo '   & "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port='"${PORT}"' --user-data-dir="$env:USERPROFILE\.chrome-basivo"'
    exit 1
    ;;
esac

if [ -z "$CHROME" ]; then
  echo "❌ Could not find Chrome/Chromium. Install Chrome, or set CHROME env var to its path."
  exit 1
fi

mkdir -p "$PROFILE"
echo "==> Launching: $CHROME"
echo "    port=${PORT}  profile=${PROFILE}"
# Detach so it keeps running after this script exits.
nohup "$CHROME" \
  --remote-debugging-port="${PORT}" \
  --user-data-dir="${PROFILE}" \
  --no-first-run --no-default-browser-check \
  >/dev/null 2>&1 &

# Wait briefly for the debug endpoint.
for _ in $(seq 1 20); do
  if curl -fsS "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
    echo "✅ Up on 127.0.0.1:${PORT}."
    echo "   NEXT: in the Chrome window that opened, sign in to your site(s) once."
    echo "   Then in Claude Code run:  /basivo-doctor <site>"
    exit 0
  fi
  sleep 0.5
done

echo "⚠️  Launched Chrome but :${PORT} didn't answer yet. Give it a moment, then"
echo "    check:  curl http://127.0.0.1:${PORT}/json/version"
