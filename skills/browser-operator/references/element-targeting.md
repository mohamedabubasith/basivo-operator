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

## Focus & keystrokes

- Keystrokes go to the **focused** element of the **foreground** tab. If the
  browser window/tab is in the background, typed text is silently dropped. Bring
  the tab to front (`page.bringToFront()` / select the tab) before typing, then
  confirm `document.activeElement` is the intended field, then type, then read
  the value back.

## Tag / chip / autocomplete inputs (tags, topics, recipients, labels)

Two common patterns — detect which one the site uses, don't assume:
1. **Suggestion list:** type → a listbox/options appear → click the matching
   option.
2. **Enter-to-commit:** no list appears → type the full value → `Enter` (some
   use `,` or `Tab`).

For every value: focus → type → (click option | Enter) → **count the chips**
(e.g. "Remove X" buttons). If the count didn't go up, retry that one value once,
then report it. Typed-but-uncommitted text is not a tag. Respect the max (the
input often disappears once full).

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
