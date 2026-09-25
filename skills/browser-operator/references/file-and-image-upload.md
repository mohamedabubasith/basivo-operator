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
