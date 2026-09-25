#!/usr/bin/env python3
"""PreToolUse hook: enforce basivo-operator's domain allowlist on navigation.

Reads the tool call from stdin (Claude Code PreToolUse payload), extracts the
target URL, and decides:
  - allowlist file missing  -> allow (don't break setups that haven't configured one)
  - domain not on allowlist -> ask (let the user approve adding it)
  - domain risk == "high" and not enabled -> deny (banking/payments/gov etc.)
  - otherwise                -> allow

Config search order (first found wins):
  $BASIVO_OPERATOR_ALLOWLIST
  $CLAUDE_PLUGIN_ROOT/config/allowed-sites.json
  $CLAUDE_PLUGIN_ROOT/config/allowed-sites.example.json   (fallback = examples)

Never touches credentials or cookies. Fails open on its own errors (so a bug
here can't wedge the browser), but fails CLOSED for high-risk domains.
"""
import json
import os
import sys
from urllib.parse import urlparse


def emit(decision, reason):
    # Modern PreToolUse decision format; reason shown to the user/model.
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,      # "allow" | "ask" | "deny"
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def load_allowlist():
    candidates = [
        os.environ.get("BASIVO_OPERATOR_ALLOWLIST"),
        os.path.join(os.environ.get("CLAUDE_PLUGIN_ROOT", ""), "config", "allowed-sites.json"),
        os.path.join(os.environ.get("CLAUDE_PLUGIN_ROOT", ""), "config", "allowed-sites.example.json"),
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            with open(path) as fh:
                return json.load(fh), path
    return None, None


def registrable(host):
    """Cheap eTLD+1-ish: last two labels. Good enough for allowlist matching."""
    host = (host or "").lower().split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    parts = host.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def extract_url(tool_input):
    for key in ("url", "href", "address", "link"):
        val = tool_input.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        emit("allow", "basivo-operator: could not parse hook payload; allowing.")

    tool_input = payload.get("tool_input") or payload.get("toolInput") or {}
    url = extract_url(tool_input)
    if not url:
        emit("allow", "basivo-operator: no URL in this call; nothing to check.")

    host = urlparse(url if "//" in url else "https://" + url).hostname or ""
    domain = registrable(host)

    allow, source = load_allowlist()
    if allow is None:
        emit("allow", "basivo-operator: no allowlist configured; allowing (configure config/allowed-sites.json to enforce).")

    sites = {registrable(s.get("site", "")): s for s in allow.get("sites", [])}
    entry = sites.get(domain)

    if entry is None:
        emit("ask", f"basivo-operator: {domain} is not on your allowlist. Approve to add it, or deny.")

    if entry.get("enabled", True) is False:
        emit("deny", f"basivo-operator: {domain} is disabled in your allowlist.")

    if str(entry.get("risk_level", "")).lower() == "high" and not entry.get("high_risk_enabled", False):
        emit("deny", f"basivo-operator: {domain} is high-risk (financial/account/gov). "
                     f"Set \"high_risk_enabled\": true for it in {os.path.basename(source or 'allowlist')} to allow.")

    emit("allow", f"basivo-operator: {domain} allowed (risk={entry.get('risk_level','medium')}).")


if __name__ == "__main__":
    main()
