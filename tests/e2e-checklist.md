# Manual E2E checklist — Medium, DRAFT mode only

Run only when the user's Chrome is connected and they're signed in to Medium.
**Do not publish anything** on the user's account. Delete the test draft only
with the user's approval.

## Preconditions
- [ ] `/basivo-doctor medium` reports a connected runtime and "logged in".
- [ ] `medium.com` is on the allowlist (`config/allowed-sites.json`).

## Draft creation (the actual test)
Create a Medium draft that exercises every editor feature:
- [ ] Title set correctly (reads back).
- [ ] Subtitle set (optional).
- [ ] A body with: an `##` heading, a bullet list (≥3 items), a fenced code
      block (language set), an inline link, and one image (uploaded, rendered).
- [ ] Autosave observed ("Saved" + `/p/<id>/edit` URL).
- [ ] Read-back diff: headings are headings, list count matches, code block
      intact, link points to the right URL, image `<img>` resolved.

## Safety Gate (stop here — do NOT publish)
- [ ] Trigger the publish path far enough to render the Safety Gate card.
- [ ] Card shows: site + signed-in name, "Publish to Medium — PUBLIC", title +
      first/last lines + word count + image count + the tags, and unusual items.
- [ ] STOP. Do not click "Publish now". Confirm the flow halts awaiting "yes".

## Evidence
- [ ] Draft URL captured.
- [ ] Screenshot of the rendered draft.
- [ ] Screenshot of the Safety Gate state.
- [ ] Audit log has a `draft / success` entry (no secrets, no body text).

## Teardown
- [ ] Ask the user before deleting the test draft. Delete only on their "yes".

## Result
- [ ] PASS = draft created + verified + gate shown, nothing published.
- Record any deviation (editor-not-ready, upload stall, tag quirk) and which
  error-taxonomy code applied.
