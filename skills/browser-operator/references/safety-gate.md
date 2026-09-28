# Safety Gate

The Safety Gate is the mandatory confirmation before **any irreversible action**.
No irreversible action happens without it. Ambiguous reply = no.

## Irreversible actions (non-exhaustive)

publish · send · submit · post · reply/comment (public) · pay / purchase /
checkout · delete / remove · transfer · invite / share-with-people · change
account settings · schedule (a send/publish) · apply / register · sign / accept
terms.

Reversible (no gate, but still verify): draft save, fill a field, preview,
navigate, read.

## The confirmation card (show this, then wait)

```
┌ CONFIRM BEFORE I <ACTION> ─────────────────────────────
│ Site:     <site>  (you're signed in as <name shown on screen>)
│ Action:   <exact action, e.g. "Publish story to Medium, PUBLIC">
│ Content:  "<title>"
│           <first line …> … <last line>
│           <N words · M images · tags: a, b, c>
│ Preview:  <how others will see it: preview/share image present + crop OK,
│            preview title/subtitle, tags/recipients actually committed>
│ Unusual:  <publication target / member-only paywall ON / scheduled 3pm /
│            audience: Public / canonical link / anything non-default — or "none">
│ Undo:     <can this be undone? how? e.g. "Unpublish possible; comments notify followers">
└────────────────────────────────────────────────────────
Reply "yes" to proceed, or tell me what to change.
```

Only proceed on an explicit affirmative ("yes", "publish", "go ahead", "confirm").
Anything hedged, conditional, or unrelated = do NOT proceed; ask again.

Not a yes: follow-up questions ("still not changed?", "is it done?"),
compliments, or a new request. Reply with a one-line re-confirm.

Before showing the card, **check the preview yourself** (element screenshot of
the preview/share card): a blank or badly cropped preview image, an unstyled
subtitle, or tags that were typed but never committed are the common silent
misses.

## Editing live content

Saving an edit to something already public (a published post, a sent-and-
editable message, a live listing) pushes the change to readers immediately —
buttons are often labelled "Save and publish", "Update", or "Save". Treat it as
irreversible: gate it with the exact change (what's removed, what's added).
After removing media, re-check the preview/share card; it may still point at
the deleted item.

## No implicit chaining

Never chain publish onto a draft step on old authorization. Even if the user
earlier said "post it", after drafting you show the gate again — UNLESS their
message unambiguously said "publish immediately" AND the site `risk_level`
permits skipping in settings. Draft → verify → gate → publish, always in that
order for `risk_level: medium`+.

## Site risk matrix (from playbook `risk_level`, overridable in settings)

| risk_level | Examples | Gate behavior |
|-----------|----------|---------------|
| **low** | Dev.to, Hashnode, personal notes | Single gate before the one irreversible action. |
| **medium** | Medium, Substack, LinkedIn, Reddit, X | Draft-first enforced; gate before publish; no implicit chaining. |
| **high** | banking, payments, health, legal, gov portals, admin/account-settings, anything moving money or granting access | Confirm **each** irreversible step individually. By **default refuse to operate** unless the user has explicitly enabled this site/category in settings. Never store/enter payment CVV or credentials. |

When category is ambiguous, treat as the higher risk.

## Examples

- User: "publish my draft" → still show the card (content preview + PUBLIC +
  tags), wait for "yes".
- User: "just save it as a draft" → no gate needed (reversible); return draft URL.
- User: "pay the invoice on the vendor portal" → high risk: refuse unless
  enabled in settings; if enabled, confirm each step, never enter CVV.
