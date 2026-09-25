# Waiting, pacing & retries

## Wait for state, not for time

Prefer waiting on an observable condition over fixed sleeps:
- element present / gone, text appeared ("Saved"), URL changed, spinner cleared,
  `<img>` resolved.
Use `browser_wait_for` (Playwright) or poll `read_page`/`find` (Chrome) in a
short loop with a timeout (default ~15s, uploads ~30s).

## Human-like pacing

Add small **randomized** delays (roughly 300–1200 ms) between discrete actions —
typing, clicking, submitting. This respects the site and avoids tripping
rate/bot heuristics. Never hammer: no tight loops of clicks, no rapid-fire
navigation. If the site clearly rate-limits (429, "slow down", throttle banner)
→ RATE_LIMITED: stop, wait, or hand off. Never try to defeat the limit.

## Autosave / draft-saved detection

After editing, wait for a settled saved state before navigating or gating:
- indicators: "Saved", "Draft saved", "All changes saved", "Saving…" → gone
- or a draft/post id appearing/stabilizing in the URL
Give autosave a beat; don't race it to the Publish button.

## Retry ladder (max 2 retries per action, then escalate)

An action that "didn't work" is not retried the same way. Each retry changes
strategy, moving DOWN the targeting ladder (`element-targeting.md`):

1. Attempt: primary semantic target.
2. Retry 1: alternate semantic target (different role/name or visible text) —
   after re-reading the page (it may have changed/loaded).
3. Retry 2: structural/attribute hint, or keyboard instead of click (or click
   instead of keyboard).
4. Still failing → STOP. Screenshot. Ask the user a specific question, or map to
   the matching code in `error-taxonomy.md`.

Do NOT loop the same action 3+ times. Do NOT silently keep going after a failed
verification — a step whose effect you couldn't confirm is a failed step.
