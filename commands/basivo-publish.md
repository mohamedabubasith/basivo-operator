---
description: Publish an already-created, verified draft after showing the Safety Gate and getting explicit confirmation.
argument-hint: <site> [draft url or "my latest draft"]   e.g. medium https://medium.com/p/abc123/edit
---

Publish a draft that already exists. Run the **browser-operator** engine's
publish path.

Input: `$ARGUMENTS`

1. Preflight + Session check.
2. Locate the draft (from the URL/description given, or the site's drafts list;
   if ambiguous, ask which one).
3. **Verify the draft first** — open it, confirm title + body + images are what
   the user intends. If it looks empty/broken, stop and report; do not publish.
4. Collect publish settings from the site's playbook (tags, audience, member-only
   / email option, publication target, schedule) — set only what the user asked.
5. **Safety Gate (mandatory)** — show the confirmation card: site + signed-in
   name, exact action (e.g. "Publish to Medium — PUBLIC" / "Substack — Publish +
   EMAIL all subscribers"), content preview (title + first/last lines + word
   count + images), and anything unusual. Wait for an explicit "yes". Ambiguous =
   no. This gate runs even if the user pre-said "publish".
6. On confirm, publish. **Verify** the live URL renders the published content;
   **Report** the URL; **Log** the outcome (redacted).

Never bypass the gate. Never publish an unverified/empty draft.
