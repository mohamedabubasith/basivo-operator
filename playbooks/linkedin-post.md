---
site: linkedin.com
name: LinkedIn (feed post)
version: 1.0.0
last_verified: 2026-09-25          # authored from documented UI; post path NOT live-run
risk_level: medium
login_signals:
  logged_in:
    - "Start a post" box on the home feed
    - "Me" avatar menu top-right
  logged_out:
    - "Sign in" / "Join now" CTA
    - redirect to linkedin.com/login
capabilities: [publish, images, tags]     # LinkedIn feed posts have no true draft; a local composer exists
irreversible_actions: [publish]
---

# LinkedIn — feed post playbook

LinkedIn has no public write API for personal feed posts and no MCP. Feed posts
are effectively **publish-only** (no persistent server draft like Medium), so
the preview IS the draft — Safety Gate is essential.

## Entry points
- Home feed: `https://www.linkedin.com/feed/`
- Composer opens from the **"Start a post"** button.

## Selectors as hints (semantic first)
```
Start a post:     role: button, name contains "Start a post"
Post editor:      role: textbox / contenteditable in the "Create a post" dialog
Add media:        role: button, name/aria: "Add a photo" / image icon in composer
Post button:      role: button, name: "Post"  (bottom-right of composer, enabled once text present)
Audience control: button near top of composer ("Anyone", "Connections only")
```

## Flows

### Flow: Create & publish a post (IRREVERSIBLE)
- **Goal:** a public (or chosen-audience) feed post with text + optional image.
- **Steps:**
  1. Open the feed; click "Start a post". Confirm composer dialog open — else
     EDITOR_NOT_READY.
  2. Focus the editor; insert the text (contenteditable; paste-style, verify).
     LinkedIn has no markdown; hashtags are literal `#word` tokens, @mentions
     require selecting a suggestion — only add mentions the user specified.
  3. Add image(s) via the media control + file-upload tool; wait + verify render.
  4. Check audience control; set only if the user specified (default is fine).
  5. **Safety Gate:** show signed-in name, "Publish LinkedIn post — audience:
     <Anyone/…>", full text preview + image count. Wait for "yes".
  6. On confirm: click **Post**.
- **Verification:** composer closes; the new post appears at top of the feed /
  on the user's profile activity. Open it; confirm text + image render. Return
  the post URL. High-stakes → `basivo-task-verifier`.
- **Failure modes:** EDITOR_NOT_READY, UPLOAD_FAILED, RATE_LIMITED, CAPTCHA/BOT_CHALLENGE.

## Editor quirks
- contenteditable, no markdown. Line breaks via Enter. Hashtags literal;
  mentions need suggestion selection. No server-side draft — don't promise "saved
  as draft"; if the user wants to hold it, keep the composer open and confirm later.

## Known challenges / ToS notes
- LinkedIn actively detects automation; keep volume low, human pacing. On any
  challenge → hand off. Do not auto-connect/message people (separate irreversible
  actions, high nuisance risk).

## Verification recipe
- Post visible at top of feed / profile activity; text + media present.

## Change log
- 1.0.0 (2026-09-25): initial; publish path `unverified` (not live-run).
