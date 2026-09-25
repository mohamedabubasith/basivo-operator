---
site: substack.com
name: Substack
version: 1.0.0
last_verified: 2026-09-25          # authored from documented UI; publish/send NOT live-run
risk_level: medium
login_signals:
  logged_in:
    - "New post" / "Write" control in the dashboard
    - publication dashboard (yourpub.substack.com/publish) loads without signin redirect
  logged_out:
    - "Sign in" CTA / redirect to substack.com/sign-in
capabilities: [draft, publish, images, schedule]
irreversible_actions: [publish, send_email]     # "Publish" can also email all subscribers
---

# Substack — playbook

Substack's editor is a ProseMirror-based `contenteditable`. It supports proper
server-side drafts. **Critical nuance:** publishing a post can *email every
subscriber* — that email is irreversible and high-nuisance. Treat send-email as
its own confirmation.

## Entry points
- New post: `https://<publication>.substack.com/publish/post?type=newsletter`
  (or dashboard → "New post"). If the publication subdomain is unknown, start at
  `https://substack.com/` → user's profile → publication → New post.
- Drafts: publication dashboard → Posts → Drafts.

## Selectors as hints (semantic first)
```
Title:        role: textbox, placeholder "Title"
Subtitle:     placeholder "Add a subtitle…"
Body:         main ProseMirror contenteditable
Add image:    "+"/image control in the editor toolbar
Continue/Publish: button "Continue" → publish settings → "Send to everyone now" /
                  "Publish now" / "Schedule"
Email toggle: "Send email" / "Email + web" vs "No email, web only" option in
              publish settings
```

## Flows

### Flow: Create draft (reversible)
- **Goal:** saved draft with title, subtitle, body, images.
- **Steps:** open New post → title → subtitle → body (ProseMirror markdown
  shortcuts: `# ## `, `- `, `1. `, `> `, ` ``` `, links via toolbar/Cmd-K) →
  images via editor control + upload, verify → autosave ("Saved").
- **Verification:** draft in dashboard Drafts; reopen shows content.
- **Failure modes:** EDITOR_NOT_READY, UPLOAD_FAILED, CONTENT_MISMATCH.

### Flow: Publish (IRREVERSIBLE — and may email subscribers)
- **Steps:**
  1. Click Continue → publish settings.
  2. Inspect the **email option**: "Email + web", "Web only", audience (everyone
     / paid / free).
  3. **Safety Gate** — MUST state whether an email will be sent and to how many
     (e.g. "Publish + EMAIL all subscribers" vs "Publish web-only, no email"),
     plus title/preview/word count/images. Wait for explicit "yes".
  4. On confirm: click the matching publish/send button.
- **Verification:** live post URL renders; status published; if emailed, note it
  can't be recalled.
- **Failure modes:** RATE_LIMITED, CAPTCHA, PAGE_CHANGED.

## Editor quirks
- ProseMirror; markdown shortcuts work. Title/subtitle/body distinct. Autosave
  "Saved". Publish and email are entangled — always surface the email decision.

## Known challenges / ToS notes
- The email blast is the real irreversible risk; never default to emailing.
  Prefer "web only" unless the user explicitly wants the email sent.

## Verification recipe
- Post URL loads with title+body; dashboard shows published; email status matches
  what the user approved.

## Change log
- 1.0.0 (2026-09-25): initial; publish/email path `unverified` (not live-run).
