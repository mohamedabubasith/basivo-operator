---
description: Show the recent basivo-operator action log (redacted) — what was done, on which site, when, and the outcome.
argument-hint: [n]   number of recent entries (default 20)
---

Show the recent action audit log. Read-only.

Input (optional count, default 20): `$ARGUMENTS`

1. Resolve the log path: the `audit_log_path` in settings, else the default
   `<plugin-data>/.basivo-operator/audit.log`.
2. If it doesn't exist, say so (no actions logged yet) and stop.
3. Print the last N entries as a compact table: timestamp · site · action · URL ·
   outcome. Entries contain no secrets and no page content beyond titles (they
   are written through `scripts/redact-log.py`).
4. If the user asks, summarize (e.g. counts by site/outcome) — but never invent
   entries; only report what's in the log.

Do not modify or delete the log from this command.
