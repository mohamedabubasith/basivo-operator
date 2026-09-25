# Element targeting — semantic first

Brittle selectors are the #1 cause of stale playbooks. Target the way a human
reads the page, not the way a bundler names classes.

## Targeting ladder (try in order)

1. **Accessibility role + name** — `read_page` / `find` for `button "Publish"`,
   `textbox "Title"`, `link "Drafts"`. Most stable.
2. **Visible text** — the exact user-visible label ("Save draft", "Publish now").
3. **ARIA / semantic attributes** — `aria-label`, `role`, `data-testid`,
   `placeholder`, `name`. `data-testid` is stable when present.
4. **Structural hint** — "the first heading-style field at top of the editor",
   "the toolbar button with a chain/link icon".
5. **CSS selector** — ONLY as a playbook hint with a fallback, never the sole
   path. Never depend on hashed class names (`css-1a2b3c`, `jsx-999`).
6. **Pixel coordinates** — last resort, from a fresh screenshot only.

## Rules

- Read the page (accessibility tree) **before** acting, not after.
- If a target isn't found, do NOT immediately retry the same way — move DOWN the
  ladder (see `waiting-and-retries.md`).
- Confirm you found ONE element, not many. If ambiguous, disambiguate by nearby
  text / container, don't click blindly.
- After acting, **read back** the effect (field value, URL, new element) before
  the next step.
- Prefer keyboard where it's more reliable than clicking (Tab to field, Enter to
  submit a known-focused control) — but verify focus first.

## Playbook selectors-as-hints format

Each playbook lists targets as: primary semantic target, then fallbacks.
Example:

```
Title field:
  - role: textbox, name/placeholder: "Title"
  - hint: first large contenteditable at top of /new-story
  - css (hint only): h3.graf--title
```

Always try semantic first; drop to the css hint only if 1–4 fail, and if the
css hint also fails, treat it as PAGE_CHANGED (see `error-taxonomy.md`).
