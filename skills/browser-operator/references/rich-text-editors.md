# Rich-text editors

Most blog/social editors are `contenteditable` (Medium=Draft.js-like,
Substack/Dev.to/Notion/Ghost=ProseMirror/TipTap variants, LinkedIn=custom,
Quill, Slate, CodeMirror for code). **Setting `.value` does nothing** on these —
they ignore it and re-render from their own model. Insert content the way a user
would, then verify from the rendered DOM.

## Insertion strategy ladder

1. **Focus the editor first.** Click into the body area; confirm caret/focus.
2. **Paste-style insertion (preferred for long/formatted content).** Dispatch a
   `paste` event carrying `text/html` (and `text/plain` fallback) via the JS
   tool, or use the clipboard. Editors run their own paste handler and build
   correct internal nodes. Verify the rendered nodes afterward.
3. **Typing (short text / titles / when paste is blocked).** Type via
   `form_input` / keyboard. Use markdown shortcuts the editor understands (below).
4. **Per-block insertion (very long posts).** Split into blocks/paragraphs,
   insert one at a time, verify each, watch for autosave — avoids UI freezes and
   lost input on big documents.

Never simulate thousands of keystrokes for a full article if paste works.

## Formatting via markdown shortcuts (most ProseMirror/Draft editors)

| Want | Type |
|------|------|
| H1 / H2 / H3 | `# ` / `## ` / `### ` then space, at line start |
| Bold / italic | `**bold**` / `*italic*` (or select + Ctrl/Cmd-B / -I) |
| Bullet list | `- ` or `* ` + space |
| Numbered list | `1. ` + space |
| Block quote | `> ` + space |
| Code block | ` ``` ` (three backticks) then Enter; language name may be typed |
| Inline code | `` `code` `` |
| Horizontal rule | `---` on its own line + Enter |
| Link | select text → Ctrl/Cmd-K → paste URL; or markdown link syntax if the editor supports it |

Medium quirks: Draft.js. Title vs subtitle vs body are separate grafs. `## `
gives a large header, `### ` a small header. `> ` + text = pull quote. Three
backticks = code block. Image: `+` menu or paste. Verify each transform rendered
(the toolbar / node type changes) rather than assuming the shortcut fired.

## Title / subtitle / body & Enter semantics

- Title, subtitle, and body are usually **separate fields**. Set them
  individually; don't dump everything into the body.
- `Enter` = new block/paragraph. `Shift+Enter` = soft line break within a block.
  Use `Shift+Enter` for line breaks inside a paragraph, `Enter` between paragraphs.

## Images

- Local file: use the file-upload tool on the editor's image/upload control
  (`file-and-image-upload.md`). Wait for upload to complete.
- Remote URL: some editors accept a pasted image URL and fetch it; others need
  an actual upload. Prefer upload when unsure.
- **Always confirm the `<img>` rendered** (element present, natural width > 0)
  before moving on. Uploads stall silently — see UPLOAD_FAILED in `error-taxonomy.md`.

## Autosave / draft detection

Watch for "Saved", "Draft saved", "Saving…", "All changes saved" indicators, or
a draft id appearing in the URL. Wait for a *settled* saved state before
navigating away or before the Safety Gate. Details in `waiting-and-retries.md`.

## Verification

After insertion, read the rendered DOM/text back and diff against the intended
content: headings are headings, list items count matches, code block preserved,
links point where intended, images present. If mismatch → CONTENT_MISMATCH,
re-do the affected block, don't publish.
