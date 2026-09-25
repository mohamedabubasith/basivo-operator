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
import sys

# Shared masker is the single source of truth for PII/secret scrubbing.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mask_pii import mask  # noqa: E402


def scrub(text):
    if text is None:
        return ""
    return mask(str(text)).replace("\n", " ").strip()


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
