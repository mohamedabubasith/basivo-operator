# Runtime detection & login signals

## Load browser tools (once, batched)

If Claude in Chrome tools are deferred, load the core set in ONE `ToolSearch` call:

```
select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__find,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__form_input,mcp__claude-in-chrome__file_upload,mcp__claude-in-chrome__javascript_tool,mcp__claude-in-chrome__tabs_create_mcp
```

Add `read_console_messages` / `read_network_requests` only if debugging.

## Runtime priority

| Order | Runtime | Tools | When |
|------|---------|-------|------|
| 1 | Claude in Chrome | `mcp__claude-in-chrome__*` | Primary. Real logged-in Chrome (Cowork). |
| 2 | Attached Playwright | `mcp__*__browser_*` | Fallback (Claude Code). Extension mode or `--cdp-endpoint` to user's Chrome+profile. Ship via `.mcp.json`, opt-in. |
| 3 | None | — | STOP. Give setup steps. Never use a headless/fresh profile. |

Probe: try to list tabs. Chrome: `tabs_context_mcp`. Playwright: `browser_tabs`.
First one that returns tabs wins. If both fail → runtime #3.

### Reality: a fresh browser gets walled
A brand-new automated browser (Playwright's bundled Chromium, no history) is
routinely blocked by bot protection — Google returns HTTP 429 (`/sorry`),
Cloudflare-fronted sites like Medium return HTTP 403 ("Attention Required"). This
is expected and is the whole reason we drive the user's *real, logged-in*
browser: that session has cookies and a trust history, so it passes. If you're
on a fresh browser and hit 429/403 at the front door, that's runtime #3 in
disguise — stop and route the user to the extension, don't fight the wall.

### No-runtime message (copy)
> I can't reach your logged-in browser (a fresh automated browser just gets
> blocked by Google/Cloudflare, so that's not an option). To let me operate your
> real session:
>
> **Recommended — Claude in Chrome extension:** install it, sign in to the site
> in your normal Chrome, and I'll drive that window directly.
>
> **Power-user alternative — attach to Chrome over CDP.** Note: since Chrome 136,
> remote debugging is IGNORED if `--user-data-dir` points at your *default*
> profile. Use a DEDICATED profile dir and sign in there once (it persists):
> ```
> "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
>   --remote-debugging-port=9222 \
>   --user-data-dir="$HOME/.chrome-basivo"
> ```
> First run: sign in to your sites in that window. Then enable the
> Playwright-attach config (`.mcp.json`) and re-try.
>
> I won't use a fresh/headless browser — it wouldn't be signed in as you, and
> it'd just get bot-walled.

## Login detection is SEMANTIC, never credential-based

Navigate to the authenticated landing page and read the accessibility tree /
page text. Decide from **signals**, not by logging in.

Generic logged-in signals (any one strong signal ≈ logged in):
- Avatar / profile menu button present
- Primary create control present ("Write", "New post", "Create", "Compose", "New story")
- Account/settings menu reachable
- User's name/handle rendered in a nav

Generic logged-out signals:
- "Sign in" / "Log in" / "Get started" as primary CTA
- Redirect to `/login`, `/signin`, `accounts.google.com`, SSO host
- Marketing landing page with no app chrome

Per-site exact signals live in each playbook's `login_signals` front-matter.

### If logged out → hand over, wait, resume
STOP. Do not touch any field. This is the **login handover protocol** (SKILL.md
step 2), and it applies both at task start and to a mid-task login wall (session
expired, step-up/re-auth):

1. Hand it to the user:
   > You're not signed in to <site>. Please sign in yourself in the open browser
   > window — I won't type credentials. Tell me **"done"** when you're in, or
   > **"no"** to cancel.
2. **Pause and yield — end your turn here.** Do not poll, loop, or re-check on a
   timer, and run no further task steps until the user replies.
3. On their reply, branch:
   - **done / yes / logged in** → re-check the signals above. Logged in now →
     continue the task. Still logged out → say so and hand back again (offer to
     keep waiting).
   - **no / cancel / stop** → stop cleanly; take no further action.
   - **ambiguous** → treat as not-ready; ask again. Do not proceed.
4. If the user pastes a password, do NOT use it; tell them to rotate it and sign
   in themselves. Never type into login / SSO / OAuth / 2FA / CAPTCHA fields, ever.

### Ambiguous (some signals both ways)
Take a screenshot, show it, ask the user to confirm they're signed in before
proceeding. Do not guess into an irreversible flow.
