---
site: example.com                 # bare domain, lowercase
name: Example                     # human name
version: 1.0.0                    # semver; bump on flow changes
last_verified: 2026-09-25         # YYYY-MM-DD; when a human/live run last confirmed this
risk_level: medium                # low | medium | high  (drives Safety Gate strictness)
login_signals:
  logged_in:                      # any one strong signal ⇒ logged in
    - avatar/profile menu present
    - "New post" control present
  logged_out:
    - "Sign in" primary CTA
    - redirect to /login
capabilities: [draft, publish, tags, images]   # subset of: draft, publish, publication_submit, tags, images, schedule, edit, delete
irreversible_actions: [publish, delete_post]   # every action requiring the Safety Gate
---

# Example — playbook

> One-line description of what this playbook covers.

## Entry points
- New item: `https://example.com/new`
- Drafts list: `https://example.com/me/drafts`
- Edit item: `https://example.com/p/<id>/edit`

## Selectors as hints (semantic first)
For each target: primary semantic target, then fallbacks. Never rely on hashed
css alone.

```
Title field:
  - role: textbox, name/placeholder: "Title"
  - hint: first large input at top of editor
  - css (hint only): input[name="title"]

Publish button:
  - role: button, name: "Publish"
  - hint: top-right primary button
```

## Flows
Each flow: **Goal → Steps → Verification → Failure modes**.

### Flow: Create draft
- **Goal:** a saved draft containing title + body (+ images/tags).
- **Steps:**
  1. Open entry point.
  2. Set title (semantic target above).
  3. Insert body (see rich-text-editors reference; paste-style, per-block for long).
  4. Add images/tags if provided.
  5. Wait for autosave ("Saved" / draft id in URL).
- **Verification:** draft appears in drafts list; reopening shows title + body.
- **Failure modes:** EDITOR_NOT_READY, UPLOAD_FAILED, CONTENT_MISMATCH.

### Flow: Publish (IRREVERSIBLE)
- **Goal:** the verified draft becomes public.
- **Steps:** open draft → Safety Gate → click Publish → confirm dialog fields
  (tags, audience) → Publish now.
- **Verification:** live public URL renders title + body; status = published.
- **Failure modes:** RATE_LIMITED, CAPTCHA/BOT_CHALLENGE, PAGE_CHANGED.

## Editor quirks
- Editor type (contenteditable / ProseMirror / Draft.js / …), markdown shortcuts
  supported, title/subtitle/body split, Enter vs Shift+Enter, autosave text.

## Known challenges / rate limits / ToS notes
- Bot detection, rate limits, ToS stance on automation, recommended volume.

## Verification recipe
- URL pattern of the result, on-page text to check, element/state confirming success.

## Change log
- 1.0.0 (2026-09-25): initial. Steps marked `unverified` where not live-confirmed.
