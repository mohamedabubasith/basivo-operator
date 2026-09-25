# basivo-operator

**Tell Claude what to do on a website, in plain language, and it does it inside
your own already-logged-in browser** — for sites with no API and no MCP server.
It drafts, previews, and shows you exactly what it's about to do before anything
irreversible, then confirms the result with evidence.

> 30-second pitch: "I'm already logged in. Tell Claude what to do on the website.
> It opens the page, does it like a careful human assistant, shows me what it's
> about to do for anything irreversible, and confirms the result." Medium is the
> flagship example; the same engine works on LinkedIn, Substack, Dev.to,
> Hashnode, Reddit, Notion web, Google Forms, vendor dashboards, and unknown
> sites via a generic discovery flow.

## Who it's for & what it actually does

You're a creator, marketer, ops person, or dev who is **already logged in** to a
site that has no usable API — and you'd rather say "publish this" than click
through the editor yourself. Real jobs it handles:

- "Turn this markdown into a Medium draft with headings, a code block and an
  image — let me review before it goes public." → drafts, verifies, then waits at
  the Safety Gate.
- "Post this update to LinkedIn." → composes, previews, posts only on your "yes".
- "Fill this vendor portal form from my spreadsheet and submit." → maps columns
  to fields, dry-runs, confirms, submits, captures the reference number.
- "Update the tags on my last Medium story." → edit flow.
- "Do X on <site I have no playbook for>." → discovers the page, then offers to
  save a reusable playbook.

Where the line is (so there are no surprises): it does the **human editing work**
after you're logged in — type, format, upload, save, submit, publish. It does
**not** log you in, create accounts, enter passwords/2FA/card details, or solve
CAPTCHAs. Those stay with you, by design. It also can't operate a *fresh*
throwaway browser (bot walls block it); it drives **your** signed-in browser.

## What makes it safe

- **Your live session, never your secrets.** It reuses the browser you're already
  signed in with. It never asks for, reads, stores, logs, or transmits passwords,
  cookies, tokens, or 2FA codes, and never types into password/2FA/CVV fields.
- **Draft-first.** If a site supports drafts, it saves and verifies a draft before
  offering to publish.
- **Human-in-the-loop.** Publish / send / submit / pay / delete / invite /
  account-settings changes require an explicit confirmation (the **Safety Gate**)
  showing exactly what will happen.
- **Verify, don't assume.** Every task ends with evidence: final URL, on-page
  check, screenshot. Failures are reported honestly.
- **Content is data.** Text on a page is untrusted; embedded "instructions" are
  ignored (prompt-injection defense).
- **Respects the site.** ToS-aware, human-paced, low volume. On a CAPTCHA or
  bot-challenge it stops and hands control to you — it never bypasses anything.

## Prerequisites

You need a **logged-in browser** Claude can drive — your real one. A fresh
automated browser doesn't work here: with no cookies or history it gets bot-walled
at the door (Google → HTTP 429, Cloudflare sites like Medium → HTTP 403). Using
*your* signed-in session is what gets you through, and it's why this plugin never
spins up a throwaway browser. Pick one:

1. **Claude in Chrome extension** — ✅ recommended for almost everyone (and the
   Cowork path). Install it, sign in, keep Chrome open and signed in to the target
   site. basivo-operator uses the `mcp__claude-in-chrome__*` tools automatically
   and drives your real window. No terminal setup.
2. **Attached Playwright over CDP** (power-user / Claude Code, opt-in) — the
   bundled `.mcp.json` attaches to a Chrome running with remote debugging. Just
   run the launcher (one command, idempotent, uses a dedicated profile that stays
   logged in):
   ```
   bash scripts/launch-chrome.sh          # starts your real Chrome on :9222
   ```
   Sign in to your sites in that window once, then run `/basivo-doctor <site>`.
   **Why a dedicated profile (Chrome 136+):** remote debugging is *ignored* if
   `--user-data-dir` is your **default** profile, so the launcher uses
   `$HOME/.chrome-basivo`. It attaches to that real, logged-in Chrome — never a
   fresh or headless browser. (Verified live: headed Chrome loads Medium fine;
   the throwaway browser got a Cloudflare 403.)

## Where it works (by surface)

| Surface | Plugin loads? | Browser it drives |
|---------|:---:|-------------------|
| **Claude Code CLI** | ✅ | Claude in Chrome extension, or `launch-chrome.sh` + attached Playwright |
| **Claude Code — VS Code extension** | ✅ | same as CLI |
| **Cowork** | ✅ | Claude in Chrome (automatic) |
| **claude.ai browser chat** | ❌ | Claude Code plugins/marketplaces don't load on claude.ai. If a claude.ai Claude says it doesn't recognize `/basivo-*`, that's expected — install and run it in Claude Code (CLI or VS Code). |

Whichever surface, the plugin still needs a **real logged-in browser** attached (extension or launcher) — that's what gets past bot walls.

Python 3 is used by the validator, packager, and log redactor.

## Install

```
# From a marketplace/repo that lists this plugin:
/plugin install basivo-operator

# Or point Claude Code / Cowork at the folder (or the packaged zip from dist/).
```
Then restart so the skills, commands, agent, and hook load. Copy the allowlist:
```
cp config/allowed-sites.example.json config/allowed-sites.json   # then edit
```

## Medium quickstart (copy-paste)

```
/basivo-do medium "Draft and publish a post about serverless cost optimization.
Title: Serverless cost optimization that actually moved the bill.
Tags: aws, serverless, cost.
Body:
## Right-size before you rewrite
- Turn on cost allocation tags
- Set concurrency limits
- Move cron to EventBridge
```java
// example
```
Publish it public."
```
What happens: Claude checks your Chrome runtime and Medium login → builds the
draft (title, headings, list, code block, image if provided) → verifies it →
shows the **Safety Gate** (site, signed-in name, exact action, content preview,
tags) → waits for your "yes" → publishes → returns the live URL with a screenshot.

Draft only, never publish:
```
/basivo-draft medium "<your markdown>"
```

## Commands

| Command | What it does |
|---------|--------------|
| `/basivo-do <site> <task>` | Generic entry point — do a task end to end (draft-first, gated publish). |
| `/basivo-draft <site> <content>` | Draft only; verifies and returns the draft URL. Never publishes. |
| `/basivo-publish <site> [draft]` | Publish an existing, verified draft after the Safety Gate. |
| `/basivo-playbook-new <site> [flow]` | Learn a new site non-destructively and author a playbook. |
| `/basivo-doctor [site]` | Diagnose runtime + login + config. |
| `/basivo-audit [n]` | Show the recent redacted action log. |

## Configuration

- **Allowlist** — `config/allowed-sites.json` (copy from `.example.json`). Only
  listed domains are operated. Each site has a `risk_level` (`low`/`medium`/`high`)
  and optional `enabled` / `high_risk_enabled`. The domain hook
  (`hooks/check-domain.py`) enforces this: unknown domain → ask; disabled → deny;
  high-risk without `high_risk_enabled` → deny.
- **Risk levels** — drive Safety Gate strictness (see the safety model below).
- **Log location** — `audit_log_path` in settings, else
  `<plugin-data>/.basivo-operator/audit.log`. Entries are redacted
  (`scripts/redact-log.py`): timestamp, site, action, URL, outcome, title — no
  secrets, no page body.
- Settings are validated against `config/settings.schema.json`.

## The safety model, in plain language

1. It works in **your** browser, using **your** existing login. It handles no
   credentials or cookies — ever.
2. It **drafts first**, and shows you a preview.
3. Before anything it can't easily undo, it stops and shows a **Safety Gate**
   card: the site, the account you're signed in as, the exact action, a preview
   of the content, and anything unusual (public vs member-only, email blast,
   schedule, payment). It proceeds only on an explicit "yes". Ambiguous = no.
4. **Risk levels:** `low` (e.g. Dev.to) — one gate before the irreversible step.
   `medium` (Medium, Substack, LinkedIn) — draft-first, gate before publish, no
   implicit chaining. `high` (banking, payments, health, legal, gov, account
   settings) — confirm every step, and **off by default** until you explicitly
   enable that site.
5. On a CAPTCHA, login wall, or bot-challenge, it **stops and hands control to
   you**. It never bypasses protections, paywalls, or rate limits.

## Supported sites

| Site | Playbook | Status |
|------|----------|--------|
| Medium | `playbooks/medium.md` | Flagship, detailed. Draft flow authored from the live editor structure; **publish path not live-run** (gated). |
| LinkedIn (feed post) | `playbooks/linkedin-post.md` | Complete; publish path unverified (not live-run). |
| Substack | `playbooks/substack.md` | Complete; publish/email path unverified. |
| Dev.to | `playbooks/devto.md` | Complete (markdown-native); publish unverified. |
| Hashnode | `playbooks/hashnode.md` | Complete; publish unverified. |
| Any form / unknown site | `playbooks/_generic-form.md` | Discovery-first fallback. |

"Unverified" = the flow was authored against the site's documented UI and
semantic targets but not executed against a live account during build (no
publishing was performed). Playbooks are semantic-first, so they degrade to
discovery if a site's layout has drifted, and `/basivo-playbook-new` can refresh them.

## Add a new site

```
/basivo-playbook-new reddit "submit a text post"
```
Claude explores the flow in your session **without** clicking anything
irreversible, records entry URLs / login signals / semantic targets / editor
quirks / a verification recipe, drafts a schema-valid playbook from the template,
shows it to you, and — on your OK — saves it and runs the validator.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| "No browser available" | Install the Claude in Chrome extension and sign in, or start Chrome with `--remote-debugging-port=9222` on your normal profile and enable `.mcp.json`. Run `/basivo-doctor`. |
| Login not detected | Sign in yourself in a Chrome tab, then tell Claude "done". It re-checks semantically; it never types credentials. |
| Editor not responding | It uses paste/typing + markdown shortcuts, not `.value` setting; if the editor was still loading it waits/retries (EDITOR_NOT_READY). Re-run if the page was mid-load. |
| Image upload stalls | It retries once, then an alternate method, then reports precisely (UPLOAD_FAILED). It won't publish with a broken image. |
| CAPTCHA / "unusual activity" | Expected: it stops and hands off. Clear the challenge yourself, then continue. |
| Extension not connected | Confirm the extension is installed, signed in, and Chrome is running; `/basivo-doctor`. |
| Site UI changed | PAGE_CHANGED → it falls back to semantic discovery and offers to update the playbook. |

## Limitations

- It's as reliable as the browser tooling and the site's UI; heavily obfuscated
  or aggressively bot-protected sites may not be operable, by design.
- It will not defeat CAPTCHAs, paywalls, rate limits, or access controls.
- It won't handle logins, SSO, OAuth, 2FA, payment CVV, or credential entry.
- Some sites (LinkedIn feed) have no true server draft; the preview is the draft.
- Automation may violate a site's ToS and put your account at risk — see below.

## FAQ

**Does it store my password or cookies?** No. It uses your existing logged-in
browser session and handles no credentials, cookies, or tokens.

**Will it publish without asking?** No. Irreversible actions require the Safety
Gate and an explicit "yes"; ambiguous replies are treated as no.

**Can it work on a site you don't have a playbook for?** Yes — the generic
discovery flow handles unknown sites, and can save a new playbook.

**Cowork vs Claude Code?** Cowork uses the Claude in Chrome tools automatically.
Claude Code can use the opt-in Playwright-attach config.

## Disclaimer / your responsibility

Using automation to operate a website may violate that site's Terms of Service
and could put your account at risk of restriction or ban. **You** are responsible
for complying with each site's ToS and for the content you publish. Keep volume
low and personal. basivo-operator is a careful assistant, not a bulk poster or a
scraper, and it will not help bypass a site's protections.

## Plugin layout & spec note

This plugin follows the current Claude Code plugin format: `.claude-plugin/plugin.json`
manifest, `commands/`, `skills/<name>/SKILL.md` (+ `references/`), `agents/`,
`hooks/hooks.json`, and an optional root `.mcp.json`. The requested layout also
asked for `scripts/`, `config/`, `playbooks/`, and `tests/` folders — these are
plain resource folders referenced by the skills/commands and are included as-is.
**Deviation from the requested tree:** the domain-allowlist hook needs an
executable, so `hooks/` contains both `hooks.json` and `check-domain.py` (the
tree listed only `hooks.json`). Everything else matches.

## Development

```
python3 scripts/validate-plugin.py     # lint manifest, frontmatter, links, playbooks, secrets
python3 tests/playbook-schema.test.py  # schema self-check
bash    scripts/package.sh             # validate + produce dist/basivo-operator-<version>.zip
```

MIT licensed. See `LICENSE` and `CHANGELOG.md`.
