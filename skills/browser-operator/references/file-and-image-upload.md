# File & image upload

## Flow

1. **Find the upload control.** Semantic target: `button "Add image"`, a `+`
   inserter menu, a drag-drop zone, or a hidden `<input type=file>`. Some
   editors reveal the input only after clicking an "image" toolbar button.
2. **Trigger the file dialog with the upload tool**, not by opening the native
   OS dialog. Chrome: `mcp__claude-in-chrome__file_upload`. Playwright:
   `browser_file_upload`. These set the file on the input without a native
   dialog (which you must never drive blindly).
3. **Provide an absolute path** to the file. If the user gave a URL, download it
   first to a temp path, or paste the URL if the editor accepts remote images.
4. **Wait for completion.** Upload UIs show a spinner/progress, then swap in the
   final `<img>`. Poll for: spinner gone AND `<img>` with a real `src`
   (not a `blob:` placeholder that never resolves) AND natural width > 0.
   See UPLOAD_FAILED handling below.
5. **Verify** the image rendered in the right position; if the editor added a
   caption field, fill it only if the user provided a caption.

## Chooser / modal handling (Playwright runtimes)

- Clicking an upload control opens a **file-chooser modal**; the runtime pauses
  there and only `browser_file_upload` can proceed. So: **one upload per
  call** — a script clicks the control and returns; next call hands the file;
  next call probes the result. Never loop several uploads in one script.
- If a chooser opens that you didn't expect, **cancel it** (`browser_file_upload`
  with no paths) and re-read state before continuing — don't feed it a file
  blindly.
- **Upload paths must be inside the runtime's allowed roots** (e.g. the
  workspace or the MCP `--output-dir`). Stage generated images there; a path in
  a temp dir outside the roots is rejected.

## Picking and sizing images

- **Cover / hero images:** landscape, about 2:1 (e.g. 1400×700). A tall
  portrait photo as a cover pushes the text far below the fold — avoid it.
- **Share/preview cards crop.** Keep the key subject centred; check the crop in
  the site's preview before the gate.
- **Real vs generated:** follow the user's taste. Built-in stock pickers (e.g.
  an Unsplash button in the editor) give licensed real photos and add the
  credit caption automatically — keep that caption.
- **Diagrams/covers without a design tool:** write a small HTML page with
  inline CSS, open it in a new tab of the same browser, and screenshot the
  element at CSS scale. Plain flat styles (light background, simple cards) read
  as "designed", heavy glows/gradients read as "AI-generated".

## Constraints & etiquette

- Respect the site's file-type and size limits; don't retry-spam a rejected file.
- One image at a time for reliability; verify each before the next.
- Never upload a file the user didn't reference.

## UPLOAD_FAILED recovery

Detection: spinner persists > ~30s, an error toast appears, or the `<img>` never
gets a resolved `src`.

1. Retry once (network blips are common).
2. If it stalls again, try an alternate path: drag-drop zone vs. file input, or
   pasting a URL instead of uploading.
3. If still failing, STOP and report precisely: which image, at which step, what
   the page showed (quote the toast). Do not publish a post with a broken/missing
   image and claim success.
