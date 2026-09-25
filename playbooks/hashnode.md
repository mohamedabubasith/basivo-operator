---
site: hashnode.com
name: Hashnode
version: 1.0.0
last_verified: 2026-09-25          # authored from documented UI; publish NOT live-run
risk_level: low
login_signals:
  logged_in:
    - "Write" / pencil "New article" control in top nav
    - user avatar menu
  logged_out:
    - "Sign in" CTA / redirect to hashnode.com/onboard
capabilities: [draft, publish, tags, images]
irreversible_actions: [publish]
---

# Hashnode — playbook

Hashnode's editor is markdown-friendly (markdown shortcuts + slash commands).
Posts publish to the user's blog/publication. Risk **low** (editable, unpublish
available; no forced email blast by default).

## Entry points
- New article: `https://hashnode.com/draft` (or "Write" in nav)
- Drafts: dashboard → Drafts

## Selectors as hints (semantic first)
```
Title:        role: textbox, placeholder "Article Title…"
Body:         main contenteditable (markdown shortcuts + "/" slash menu)
Slash menu:   type "/" at line start → image, code block, embed, etc.
Add tags:     tags input in the publish/preview panel (up to 5)
Publish:      button "Publish" (opens preview/settings), then confirm publish
Save draft:   autosaves; "Saved" indicator
```

## Flows

### Flow: Create draft (reversible)
- **Steps:** open `/draft` → title → body via markdown shortcuts / slash menu
  (`## `, `- `, ` ``` `, `> `, links; `/image` to upload) → images upload +
  verify → autosave "Saved".
- **Verification:** draft in dashboard Drafts; reopen shows content + preview.
- **Failure modes:** EDITOR_NOT_READY, UPLOAD_FAILED, CONTENT_MISMATCH.

### Flow: Publish (IRREVERSIBLE, low risk)
- **Steps:** open Publish → set tags (≤5), cover image if provided, publication
  target → **Safety Gate** (title, tags, word count, images, target blog) →
  confirm Publish.
- **Verification:** live URL on the user's Hashnode blog renders; status published.
- **Failure modes:** RATE_LIMITED, PAGE_CHANGED.

## Editor quirks
- Markdown shortcuts + "/" slash commands. Title separate. Up to 5 tags. Autosave.

## Known challenges / ToS notes
- Low friction; personal-use norms. Public GraphQL API exists (prefer if user
  has a token).

## Verification recipe
- Blog post URL loads with rendered content; dashboard shows published.

## Change log
- 1.0.0 (2026-09-25): initial; publish path `unverified` (not live-run).
