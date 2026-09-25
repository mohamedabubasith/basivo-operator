# Error taxonomy

Each error has a **detection signal**, an **automatic recovery** (if any), and a
**hand-off point** (when to stop and involve the user). Never claim success on an
unresolved error.

| Code | Detection signal | Auto recovery | Hand off when |
|------|------------------|---------------|---------------|
| **NOT_LOGGED_IN** | "Sign in" CTA, redirect to login/SSO, no create control | none | Immediately — ask user to sign in themselves; never type credentials. |
| **CAPTCHA / BOT_CHALLENGE** | CAPTCHA widget, "verify you're human", challenge/interstitial, unusual-activity page | none — **never solve or bypass** | Immediately — hand control to user, wait for them to clear it. |
| **RATE_LIMITED** | HTTP 429, "slow down", throttle banner, temp block | wait/back off once with human pacing | If it persists — stop, tell user, suggest waiting. Never try to defeat it. |
| **EDITOR_NOT_READY** | contenteditable absent/not focusable, toolbar missing, JS still loading | wait for editor init (poll), re-focus | After 2 waits fail — screenshot + ask. |
| **ELEMENT_NOT_FOUND** | target absent after read_page | move down targeting ladder (2 retries) | After ladder exhausted — screenshot + specific question. |
| **UPLOAD_FAILED** | spinner stuck >30s, error toast, `<img>` src never resolves | retry once, then alternate upload method | Still failing — report which image/step precisely; don't publish. |
| **CONTENT_MISMATCH** | read-back diff ≠ intended (missing heading, wrong list, broken link) | re-do the affected block | Mismatch persists — stop before publish; show diff. |
| **NETWORK** | request failed, offline, timeout, 5xx | retry once after short wait | Repeated failure — report and stop. |
| **PAGE_CHANGED** (stale playbook) | semantic AND css hints all miss; layout differs from playbook | fall back to `_generic-form.md` semantic discovery | After discovery — offer to update the playbook (`/basivo-playbook-new`); proceed only if user confirms the re-mapped flow. |
| **UNEXPECTED_DIALOG** | modal/toast/consent/paywall/native dialog interrupts flow | read it; dismiss only clearly-benign UI (cookie accept if required to proceed) | Anything consequential (native alert/confirm, payment, permission) — stop and ask. Never blind-click through dialogs. |
| **PAYWALL / PERMISSION** | "members only", 403, "you don't have access", feature gated | none | Immediately — report; do not attempt to bypass. |

## Cross-cutting

- **2–3 strikes rule:** the same action failing 2–3 times → stop and ask; do not
  loop.
- **Stale tab id:** on "tab not found", re-fetch tab context; don't reuse old ids.
- **Every hand-off carries evidence:** a screenshot + one specific question, not
  a vague "it didn't work".
- On any unresolved error, the Report step states the failure honestly and the
  Log records the outcome as failed.
