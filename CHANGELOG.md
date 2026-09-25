# Changelog

All notable changes to **basivo-operator** are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/); versioning is [SemVer](https://semver.org/).

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
