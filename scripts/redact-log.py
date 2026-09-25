#!/usr/bin/env python3
"""Append a redacted entry to the basivo-operator audit log.

The log records ONLY: timestamp, site, action type, URL, outcome. No secrets, no
page content beyond a title. This script also scrubs anything that looks like a
credential/token/cookie from the fields it's given, as a belt-and-suspenders
guard, and truncates any title.

Usage:
  redact-log.py --site medium.com --action publish --url https://... --outcome success [--title "..."] [--log PATH]

Reading back is done by /basivo-audit; this script only writes.
"""
import argparse
import datetime as dt
import os
import re
import sys

# Patterns that must never land in the log.
SECRET_PATTERNS = [
    re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*\S+"),
    re.compile(r"(?i)(authorization|bearer)\s+\S+"),
    re.compile(r"(?i)(token|api[_-]?key|secret|session|cookie|csrf|otp|2fa)\s*[:=]\s*\S+"),
    re.compile(r"(?i)\bcvv\b\s*[:=]?\s*\d{3,4}"),
    re.compile(r"\b\d{13,19}\b"),                       # long digit runs (card-ish)
    re.compile(r"[?&](access_token|token|code|session|sig|auth)=[^&\s]+"),  # URL secrets in query
]


def scrub(text):
    if text is None:
        return ""
    out = str(text)
    for pat in SECRET_PATTERNS:
        out = pat.sub("[REDACTED]", out)
    return out.replace("\n", " ").strip()


def strip_query_secrets(url):
    # keep the path, drop obviously-sensitive query params
    return scrub(url)


def default_log_path():
    root = os.environ.get("CLAUDE_PLUGIN_ROOT", os.getcwd())
    return os.path.join(os.path.dirname(root.rstrip("/")), ".basivo-operator", "audit.log")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True)
    ap.add_argument("--action", required=True)
    ap.add_argument("--url", default="")
    ap.add_argument("--outcome", required=True)
    ap.add_argument("--title", default="")
    ap.add_argument("--log", default=os.environ.get("BASIVO_OPERATOR_AUDIT_LOG", ""))
    args = ap.parse_args()

    path = args.log or default_log_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)

    ts = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    title = scrub(args.title)[:120]
    fields = [
        ts,
        scrub(args.site),
        scrub(args.action),
        strip_query_secrets(args.url),
        scrub(args.outcome),
        title,
    ]
    line = "\t".join(fields)

    with open(path, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")

    print(f"logged: {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
