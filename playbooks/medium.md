---
site: medium.com
name: Medium
version: 1.0.0
last_verified: 2026-09-25          # authored from Medium's documented editor; publish path NOT live-run
risk_level: medium
login_signals:
  logged_in:
    - avatar / profile menu (top-right) present
    - "Write" control present in top nav
    - navigating to /new-story opens the editor (no redirect to signin)
  logged_out:
    - "Sign in" / "Get started" primary CTA
    - redirect to medium.com/m/signin or accounts.google.com etc.
capabilities: [draft, publish, publication_submit, tags, images, schedule, edit, delete, import]
irreversible_actions: [publish, delete_story, unpublish, submit_to_publication]
---

# Medium — playbook

Medium has no public write API for new integrations and no MCP server; this is
the flagship browser-operator playbook. Medium's editor is a Draft.js-style
`contenteditable`. **Draft-first, always.**

## Entry points
- New story: `https://medium.com/new-story`
- Drafts / stories list: `https://medium.com/me/stories/drafts`
- Edit a story: open it from the drafts/stories list (Edit)
- Import a story: `https://medium.com/p/import`
- Story settings / publish dialog: reached via the top-right **Publish** button
  inside the editor.

## Selectors as hints (semantic first; Medium ships hashed css — never rely on it)

```
Title field:
  - role: textbox / heading, placeholder: "Title"
  - hint: first large graf at very top of /new-story editor
Subtitle field:
  - hint: the second graf directly under the title (placeholder "Tell your story…"
    becomes subtitle styling when it's the line under the title)
Body:
  - hint: the main contenteditable story area below title/subtitle
Inline "+" inserter:
  - role: button, name/aria: "Add" / plus icon that appears at line start on empty line
    (opens menu: image, unsplash, video, embed, code block, new part)
Publish button:
  - role: button, name: "Publish"  (top-right of editor)
Publish dialog — topics/tags input:
  - role: textbox, placeholder: "Add a topic…"  (max 5)
Publish dialog — "Publish now" button:
  - role: button, name: "Publish now"
"Saved" indicator:
  - text near top: "Saved" / "Saving…" (autosave); a draft id appears in URL
    (medium.com/p/<id>/edit)
```

## Flows

### Flow: Create draft  (reversible — automatic)
- **Goal:** a saved Medium draft with title, optional subtitle, formatted body,
  images.
- **Steps:**
  1. Open `https://medium.com/new-story`. Confirm editor loaded (title
     placeholder visible) — else EDITOR_NOT_READY (wait/re-focus).
  2. Click the title graf; type the title (short → typing is fine).
  3. Press Enter; type the subtitle if provided (the line under the title renders
     as subtitle).
  4. Press Enter into the body. Insert the body per
     `browser-operator/references/rich-text-editors.md`:
     - Prefer paste-style HTML insertion for the full body; for very long posts,
       insert per section and verify each.
     - Formatting via markdown shortcuts at line start: `## ` big header,
       `### ` small header, `- ` bullet, `1. ` numbered, `> ` pull quote,
       ` ``` ` code block, `---` divider. Links: select text → Cmd/Ctrl-K → URL.
  5. Images: on an empty line, use the "+" inserter → image → upload the local
     file via the file-upload tool; wait for the `<img>` to resolve; verify it
     rendered (`file-and-image-upload.md`). Add caption only if provided.
  6. Wait for autosave: "Saved" and a `medium.com/p/<id>/edit` URL.
- **Verification:** draft shows in `/me/stories/drafts`; reopening shows title,
  subtitle, body formatting, images. Read the rendered DOM back and diff against
  the intended content (headings are headings, list counts match, code block
  intact, links correct). Mismatch → CONTENT_MISMATCH, fix the block, don't publish.
- **Failure modes:** EDITOR_NOT_READY, UPLOAD_FAILED, CONTENT_MISMATCH.

### Flow: Publish  (IRREVERSIBLE — Safety Gate required)
- **Goal:** a verified draft becomes a public (or member-only) story.
- **Preconditions:** draft created and verified above.
- **Steps:**
  1. In the editor, click **Publish** (top-right). The publish dialog opens.
  2. Read the dialog. Note/collect:
     - **Topics/tags** — up to **5**. Type each in the "Add a topic…" box and
       select the suggestion. (Tag input quirk: you must pick the suggested chip;
       a raw typed word may not register — verify chips appear.)
     - **Preview** title, subtitle, preview image (Medium auto-picks; change only
       if the user asked).
     - **Add to publication** — only if the user requested a specific publication
       (this is `submit_to_publication`, also irreversible per publication rules).
     - **Story settings** — member-only / paywall toggle, distribution/"Allow
       responses", scheduled time, canonical link — set ONLY what the user asked;
       otherwise leave Medium defaults.
  3. **Safety Gate** (`browser-operator/references/safety-gate.md`): show the
     card with site + signed-in name, "Publish story to Medium — PUBLIC (or
     member-only)", title + first/last lines + word count + image count + the
     tags, and anything unusual (publication target, paywall on, schedule).
     Wait for explicit "yes".
  4. On confirm: click **Publish now** (or **Schedule** if scheduling). Do not
     click through any unexpected native dialog — UNEXPECTED_DIALOG → stop.
- **Verification:** Medium redirects to the live story URL (e.g.
  `medium.com/@user/<slug>-<hash>` or a publication URL). Reload it; confirm
  title, subtitle, body, images render and status is published (not draft).
  For high-stakes, invoke `basivo-task-verifier`. Return the live URL in the Report.
- **Failure modes:** RATE_LIMITED / "Something went wrong" toast (retry once with
  pacing, then stop), CAPTCHA/BOT_CHALLENGE (hand off), tag input quirk
  (re-enter, verify chips), PAGE_CHANGED.

### Flow: Import a story  (alternative)
Use `https://medium.com/p/import` when the source already lives at a public URL
and the user wants Medium to pull title/body/canonical automatically (sets the
canonical link to the original — good for cross-posting). Paste the URL →
Import → it creates a **draft** → then follow Verify + Publish gate as above.
Prefer this over manual insertion when a canonical source URL exists.

### Flow: Edit existing story  (e.g. update tags)
- Open the story from `/me/stories/drafts` or the public story → **Edit**
  (or the story's "..." menu → Edit).
- Make the change. For tags: open the Publish/story-settings dialog, adjust
  topics (max 5), verify chips.
- Re-saving an edit to a **published** story republishes changes → treat the
  save/update as irreversible: Safety Gate before applying.

### Flow: Unpublish / delete  (IRREVERSIBLE)
- Story "..." menu → "Unpublish" or "Delete story". Both irreversible
  (delete especially). Safety Gate with an explicit warning; require "yes".

### Flow: List my drafts
- Open `/me/stories/drafts`, read titles + last-edited. Read-only; no gate.

## Editor quirks
- Draft.js contenteditable — **do not set `.value`**; use paste/typing + markdown
  shortcuts (`rich-text-editors.md`).
- Title / subtitle / body are distinct grafs; set them separately.
- `Enter` = new block, `Shift+Enter` = soft break within a block.
- Autosave: "Saved" indicator + `/p/<id>/edit` in URL — wait for it before the gate.
- Tag input requires selecting the suggested chip; verify chips render; max 5.
- Preview image is auto-chosen from body images; change only on request.

## Known challenges / rate limits / ToS notes
- Medium's Terms restrict automation; keep volume **low and personal**. This
  playbook is for a human publishing their own content, not bulk posting.
- Medium runs bot detection; on any CAPTCHA / "unusual activity" / challenge →
  STOP and hand control to the user. Never attempt to bypass.
- "Something went wrong" toasts happen on flaky saves; retry once with human
  pacing, then stop and report.

## Verification recipe
- Draft: appears in `/me/stories/drafts`; reopen → title+body+images present.
- Published: final URL under `medium.com/@user/...` or publication path loads;
  title + body + images render; status published; tags present (≤5).
- Screenshot the live page at the Report step.

## Change log
- 1.0.0 (2026-09-25): initial. Draft flow authored against Medium's documented
  editor structure and semantic targets. Publish/import/edit/delete paths
  authored but **not live-run** (no publishing done during build) — marked
  `unverified` for the irreversible steps; re-verify on first live use.
