---
description: Diagnose basivo-operator — which browser runtime is connected, whether you're logged in to a site, and config/allowlist status.
argument-hint: [site]   e.g. medium
---

Diagnose the browser tooling and login state. Report as a checklist; change
nothing.

Input (optional site to check login for): `$ARGUMENTS`

Run these checks and print a ✅/❌/⚠️ line for each:

1. **Runtime.** Probe in order and report which is available:
   - Claude in Chrome (`mcp__claude-in-chrome__*`) — try listing tabs.
   - Attached Playwright (`mcp__*__browser_*`) — try listing tabs.
   - If neither: ❌ and print the exact setup steps (install Claude in Chrome
     extension + sign in, or start Chrome with `--remote-debugging-port=9222` on
     the normal profile and enable `.mcp.json`).
2. **Tabs.** List current open tabs (count + titles) to confirm the runtime
   actually drives the user's browser.
3. **Login (if a site was given).** Open the site's authenticated landing page
   in a new tab and evaluate the playbook's `login_signals` semantically. Report
   logged in / logged out / ambiguous. Never type credentials.
4. **Playbook.** Does `playbooks/<site>.md` exist? Report version + last_verified,
   or note that `_generic-form.md` would be used.
5. **Config.** Is the site on the allowlist (`config/allowed-sites*.json`)? What
   `risk_level`? Where is the audit log configured?

End with a one-line verdict: ready to operate, or the single blocking item to fix.
