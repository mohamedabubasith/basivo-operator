# Changelog

All notable changes to **basivo-operator** are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/); versioning is [SemVer](https://semver.org/).

## [0.4.1] - 2026-09-28

### Changed
- **Naming cleanup across Basivo plugins.** Author is now "Basivo"
  (basivo.in) with the real homepage and repository URLs (the placeholder
  `github.com/your-org/...` is gone); LICENSE holder corrected from an old
  project name to Basivo.
- **Install through the shared `basivo` marketplace**
  (`mohamedabubasith/basivo-plugins`), which lists basivo-operator and
  basivo-qa: `claude plugin install basivo-operator@basivo`. This repo's own
  marketplace still works for existing installs.

## [0.4.0] - 2026-09-28

Lessons from a full live run (draft, rewrite, images, topics, publish, live
edit). Changes are site-agnostic except the Medium playbook refresh.

### Added
- **Token budget reference** (`references/token-budget.md`) and golden rule 8:
  scoped/file snapshots or compact JS probes instead of full-page dumps, insert
  big payloads once, screenshots only at checkpoints (element-level, CSS scale,
  one montage for many images), batch deterministic steps and split at modals.
- **Tag/chip input pattern** (suggestion-click vs Enter-to-commit, count chips
  after each) and **focus rule** (bring tab to front; background tabs drop
  keystrokes) in `element-targeting.md`.
- **Caret & block operations** in `rich-text-editors.md`: Range-based caret
  (not `End`), placeholder-first multi-insert, deleting embedded media, whole-
  body replace, toggle-menu and "not stable" handling.
- **Chooser/modal handling, allowed upload roots, image sizing, stock pickers,
  HTML-rendered diagrams** in `file-and-image-upload.md`.
- `/basivo-doctor` reports the running plugin version.

### Changed
- **Safety Gate** now shows how others will see the result (preview/share image
  and crop, preview title/subtitle, committed tags), treats follow-up questions
  as not-a-yes, and gates edits to live content.
- `content-to-web`: media plan, broad-plus-specific tag strategy, build the
  payload once.
- `site-playbook-authoring`: capture silent-failure quirks; explore cheaply.
- **Medium playbook 1.1.0**: verified end-to-end; topics commit on Enter,
  publish dialog page/labels, "Save and publish" for live edits, image swap,
  preview-card check, cover sizing, Unsplash credit.
- `.mcp.json`: Playwright `--output-dir` moved out of the repo;
  `.playwright-mcp/` git-ignored.

### Fixed
- **Masker no longer hides URLs**: long slugs/hashes in URL paths were replaced
  with `[SECRET]` in the audit log. Query-string secrets are still masked.

## [0.3.2] - 2026-09-25

### Changed
- **Handover now pauses and yields the turn** — on hitting a login wall the
  engine ends its turn and waits for the user instead of polling or pushing
  ahead, resuming only after a "done"/"yes" reply and a confirmed logged-in
  re-check. Wired the full yes/no/done branching into the `/basivo-do` and
  `/basivo-publish` commands so they no longer just say "ask the user to sign in".

## [0.3.1] - 2026-09-25

### Changed
- **Explicit login-handover protocol** in the core skill (step 2) and the
  session-detection reference: whenever a site needs login — at task start OR on
  a mid-task login wall (expired session, step-up/re-auth) — the engine STOPS,
  hands sign-in to the user, and waits for **"done"/"yes"** (re-check, then
  continue), **"no"** (cancel cleanly), or ambiguous (ask again). If the user
  pastes a password, it is not used and they're told to rotate it. Credentials /
  SSO / OAuth / 2FA / CAPTCHA fields are never touched. Mapped to NOT_LOGGED_IN.

## [0.3.0] - 2026-09-25

### Added
- **Shared PII/secret masker `scripts/mask_pii.py`** — single source of truth
  that turns credentials/PII into typed tags (`[PASSWORD]`, `[TOKEN]`, `[EMAIL]`,
  `[CARD]`, `[SSN]`, `[AWS_KEY]`, `[JWT]`, `[GITHUB_TOKEN]`, …). Covers `key=value`
  credential pairs, provider-shaped tokens, Bearer tokens, Luhn-checked cards,
  SSN, email, phone, IP, URL query secrets, and generic high-entropy blobs.
  Luhn-checks card candidates and leaves plain prose untouched. CLI + `--selftest`.
- **`references/pii-and-secret-handling.md`** — rules for user-supplied creds/PII:
  mask in every log/report/echo, never type credentials into a page, and never
  mask the actual content being published.
- **`tests/mask-pii.test.py`** — verifies masking rules and that `redact-log.py`
  routes through the masker with no leaks.

### Changed
- `redact-log.py` now delegates to `mask_pii.mask()` (one source of truth) instead
  of its own thinner pattern list.
- Core skill: golden rule #1, the Report step, and the Log step now explicitly
  require masking any user-supplied credential/PII.

## [0.2.0] - 2026-09-25

### Added
- **`scripts/launch-chrome.sh`** — one-command launcher that starts the user's
  real Chrome with remote debugging on a dedicated profile (`$HOME/.chrome-basivo`),
  idempotent, macOS/Linux (+ Windows instructions). Removes the manual-flag setup
  friction for the attached-Playwright path.
- **`.claude-plugin/marketplace.json`** so the plugin is installable via
  `/plugin marketplace add` + `/plugin install`.
- **"Where it works (by surface)"** table in the README: Claude Code CLI ✅,
  VS Code extension ✅, Cowork ✅, claude.ai browser chat ❌ (Claude Code plugins
  don't load there).

### Verified live
- End-to-end on this machine: launcher → attached-Playwright connected to real
  Chrome → **Medium loaded with no Cloudflare 403** (a headless/throwaway browser
  got 403) → semantic login detection correctly reported "logged out" → stopped
  at the credential boundary without typing anything.

## [0.1.1] - 2026-09-25

### Fixed
- **Chrome 136+ remote-debugging gotcha.** Corrected the Playwright-attach setup
  everywhere (README, `.mcp.json`, session-detection reference): since Chrome 136
  `--remote-debugging-port` is ignored when `--user-data-dir` is the default
  profile. Docs now use a dedicated profile dir (`$HOME/.chrome-basivo`) the user
  signs into once — the previous default-profile command silently failed.

### Changed
- Made the **Claude in Chrome extension the clearly-recommended path**; CDP-attach
  is now framed as the power-user alternative.
- Documented the **bot-wall reality** (fresh automated browsers get Google HTTP
  429 / Cloudflare HTTP 403) in the README and runtime-detection reference, so a
  429/403 at the front door is treated as "route to the real logged-in browser,"
  not a bug to fight — verified live during testing.
- Added a **"Who it's for & what it actually does"** section to the README with
  concrete customer jobs and an explicit statement of the signup/credential line.

## [0.1.0] - 2026-09-25

### Added
- Core engine skill `browser-operator` implementing the Intake → Preflight → Session check → Plan → Execute → Safety Gate → Verify → Report → Log state machine.
- Runtime auto-detection across Claude in Chrome tools (primary) and Playwright-attach (fallback); explicit stop-and-instruct when no logged-in browser is available.
- Reference library: session/login detection, element targeting, rich-text editors, file/image upload, waiting & retries, safety gate, prompt-injection defense, error taxonomy.
- Site playbooks: Medium (flagship, detailed), LinkedIn post, Substack, Dev.to, Hashnode, and a generic-form discovery fallback.
- `site-playbook-authoring` skill + template for learning new sites and writing schema-valid playbooks.
- `content-to-web` skill for mapping markdown/blog input onto what web editors accept.
- Commands: `/basivo-do`, `/basivo-draft`, `/basivo-publish`, `/basivo-playbook-new`, `/basivo-doctor`, `/basivo-audit`.
- Independent `basivo-task-verifier` subagent for evidence checking on high-stakes tasks.
- Domain-allowlist enforcement hook.
- Config: allowlist example + settings JSON schema.
- Scripts: plugin validator, audit-log redactor, packager.
- Tests: playbook-schema test, safety-gate scenarios, injection scenarios, manual E2E checklist.

### Notes
- Medium playbook flows were authored against Medium's documented editor structure and semantic targeting; live-verification status is marked per flow. Publish paths are gated behind the Safety Gate and were **not** exercised against a live account during build.
