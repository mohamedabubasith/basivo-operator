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

### No-runtime message (copy)
> I can't reach a logged-in browser. To let me operate your session, either:
> 1. Install the **Claude in Chrome** extension and sign in to the site in Chrome, or
> 2. Start Chrome with remote debugging on your normal profile:
>    `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222 --user-data-dir="$HOME/Library/Application Support/Google/Chrome"`
>    then enable the Playwright-attach config (`.mcp.json`).
> I won't use a fresh/headless browser — it wouldn't be signed in as you.

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

### If logged out
STOP. Do not touch any field. Say:
> You're not signed in to <site>. Please sign in yourself in your browser tab,
> then tell me "done" and I'll re-check.
Wait. Re-check the same signals. Never type into login/SSO/2FA forms, ever.

### Ambiguous (some signals both ways)
Take a screenshot, show it, ask the user to confirm they're signed in before
proceeding. Do not guess into an irreversible flow.
