# Token budget — operate cheaply

Browser tools are the most expensive thing this plugin does. Every snapshot,
screenshot, and echoed script lands in context and is paid for again on every
later turn. A single careless page snapshot can cost more than the whole post.
Follow these rules on every site.

## 1. Read small, not whole pages

- **Never take a full-page accessibility snapshot of a content-heavy page**
  (editors, feeds, dashboards). Use one of:
  - a **scoped** snapshot: pass the container ref/selector (`target`) or a
    `depth` limit;
  - a **file** snapshot (`filename`) and then search it for the few lines you
    need, instead of reading it all;
  - a **JS probe** that returns only the facts you need (see §2).
- Read the page **once per step**. Don't re-snapshot unchanged UI to "check
  again"; re-read only after an action that changed it.

## 2. Probe with one compact JSON result

Replace chains of snapshot → click → snapshot with a single script
(`browser_evaluate` / `browser_run_code_unsafe` / `javascript_tool`) that acts
and returns a **small** summary object:

```js
// good: ~200 bytes back
return { url: location.href, h: q('h2,h3').length, li: q('li').length,
         imgs: q('figure img').length, empties: q('p:empty').length,
         saved: /Saved/.test(document.body.innerText) };
```

Verification uses these **counts + first/last line + a forbidden-pattern
check** (e.g. leftover old text, em dashes the user banned) — not a full text
read-back. Read full text only when a count doesn't match.

## 3. Don't echo big payloads twice

Some runtimes print back the entire script you send. A 5 KB HTML body inside a
paste script is paid for on every call that carries it.

- Insert large content **once**. Never put the full body into a retry, a
  verification, or a "just in case" re-run.
- Keep the payload in a file the runtime can load (`filename` parameter) where
  supported, and keep verification scripts separate and tiny.
- On a mismatch, fix **only the failing block**, not the whole body.
- Never return the inserted content from the script — return counts.

## 4. Screenshots only at checkpoints

Take a screenshot at most: after composing content, before the Safety Gate,
and after the irreversible action. Rules:
- Prefer an **element** screenshot of the part that matters (the image, the
  preview card, the tag box) over the full viewport.
- Use CSS scale, not device scale (Retina doubles the pixels).
- Reviewing several generated images? Stitch them into **one downscaled
  montage** and look once, instead of one read per image.
- Don't screenshot to "see if it worked" when a JS probe can answer.

## 5. Batch deterministic steps; split at modals

- Steps with no decision between them (focus → type → Enter → read chip count)
  go in **one** script.
- **Split at anything that opens a modal or native chooser** (file upload,
  print, download, auth popup). The runtime pauses the script there; a loop that
  expects to continue past a chooser breaks and wastes calls. One upload per
  call: open chooser → hand the file → probe result.
- Waits belong **inside** the script (`waitForTimeout`, condition polling) — not
  as separate wait tool calls between actions.

## 6. Research and reading the web

- Fetch articles through an indexing/search tool when one is available and
  query only the facts you need; don't paste whole pages into context.
- Batch multiple search questions in one call.

## 7. Talk less

- The plan is ≤ 8 lines; the report is 2–4 sentences plus the URL.
- Don't narrate each click. Don't restate tool output the user can't see —
  summarize the result.

## Quick self-check before each browser call

1. Will this return more than ~2 KB? → scope it, file it, or probe instead.
2. Am I re-sending a payload I already inserted? → don't.
3. Is a screenshot needed, or will a count do? → prefer the count.
4. Can the next 2–3 deterministic steps ride in this same script? → batch.
