---
site: dev.to
name: Dev.to
version: 1.0.0
last_verified: 2026-09-25          # authored from documented UI; publish NOT live-run
risk_level: low
login_signals:
  logged_in:
    - "Create Post" button in top nav
    - user avatar menu top-right
  logged_out:
    - "Log in" / "Create account" CTA
capabilities: [draft, publish, tags, images]
irreversible_actions: [publish]
---

# Dev.to — playbook

Dev.to's editor is genuinely **markdown-native** (a real markdown textarea plus
a rich toggle), which makes it the easiest target: the content-to-web plan can be
inserted almost verbatim. Note: Dev.to also has a public API — prefer it if the
user has a token, but this playbook covers the no-API browser path. Risk is
**low** (easy to edit/unpublish; no email blast).

## Entry points
- New post: `https://dev.to/new`
- Dashboard / drafts: `https://dev.to/dashboard`

## Selectors as hints (semantic first)
```
Title:        role: textbox, placeholder "New post title here…"
Tags:         role: textbox, placeholder "Add up to 4 tags…"  (max 4)
Body:         the markdown textarea (accepts raw markdown directly)
Add cover image: "Add a cover image" button
Save draft:   button "Save draft"
Publish:      button "Publish"
```

## Flows

### Flow: Create draft (reversible)
- **Steps:** open `/new` → title → tags (up to 4; type + Enter/space per tag,
  verify chips) → paste the **raw markdown** body directly into the body textarea
  (no per-block shortcut dance needed) → optional cover image via upload, verify →
  "Save draft".
- **Verification:** draft in dashboard; reopen shows markdown; preview renders
  headings/code/links/images.
- **Failure modes:** UPLOAD_FAILED, CONTENT_MISMATCH (rare — markdown is literal).

### Flow: Publish (IRREVERSIBLE, low risk)
- **Steps:** verify draft → **Safety Gate** (title, tags, word count, images) →
  click **Publish**.
- **Verification:** live URL `dev.to/<user>/<slug>` renders; status published.
- **Failure modes:** RATE_LIMITED, PAGE_CHANGED.

## Editor quirks
- Markdown-native: front-matter-like fields (title, tags, cover) are separate
  inputs; body is raw markdown — insert verbatim from the content-to-web plan.
- Max 4 tags.

## Known challenges / ToS notes
- Low friction; standard "personal use, no spam". Public API exists (prefer if
  the user has a key).

## Verification recipe
- `dev.to/<user>/<slug>` loads with rendered markdown; dashboard shows published.

## Change log
- 1.0.0 (2026-09-25): initial; publish path `unverified` (not live-run).
