# PII & secret handling

Users sometimes paste sensitive data into a task — a username, password, API
token, session cookie, card number, OTP, or other PII. Handle it so it never
leaks and never lands where it shouldn't.

## The three rules

1. **Never store or surface secrets.** Anything that goes to the **audit log**,
   a **progress line**, a **report**, or an **echo of the user's input** must be
   run through the masker first (`scripts/mask_pii.py` → `mask()`), turning
   secrets/PII into typed tags like `[PASSWORD]`, `[TOKEN]`, `[EMAIL]`, `[CARD]`.
   `redact-log.py` already uses it; use it for reports/echoes too.
2. **Never type credentials into a page.** Passwords, 2FA/OTP codes, and card
   CVV are a hard refuse (golden rule #1). If a task can't proceed without one,
   STOP and hand off to the user — do not ask them to paste it to you either.
3. **Don't mask the actual content being published.** The masker is for logs,
   reports, and echoes — NOT for the body the engine types into the editor. The
   user's real post/body goes in verbatim. Only what gets *recorded or shown
   back* is masked. (If the user's *published content itself* contains a real
   secret, that's a different problem — flag it and confirm before publishing.)

## When the user pastes a credential

- If it's a credential meant for signing in: don't take it. Say you don't handle
  credentials; ask them to sign in themselves in their browser (login is theirs).
- If it appears incidentally in a task/payload: mask it in everything you echo or
  log, and only insert the literal value into a page if that's unambiguously the
  intended content (rare) — and even then, warn first.
- Never put PII/secrets into URL query strings, and never send them to any
  endpoint/recipient not explicitly part of the user's task.

## What the masker catches

Emails, phone numbers, IPv4, US SSN, Luhn-valid card numbers, JWTs, AWS keys,
GitHub/Slack/Google/`sk-` tokens, `Bearer` tokens, `key=value` credential pairs
(`password=`, `token=`, `api_key=`, `client_secret=`, `otp=`, `cvv=`, …), URL
query secrets, and generic high-entropy blobs (32+ chars mixing letters+digits).
It Luhn-checks card candidates to avoid masking ordinary long numbers, and leaves
plain prose untouched.

Quick use:
```
python3 scripts/mask_pii.py "some text with a token=abc123..."   # → masked
python3 scripts/mask_pii.py --selftest                            # verify rules
```

## Screenshots & page reads

Don't screenshot or read regions containing credentials/financial/health data
beyond what the task needs (prompt-injection defense reference covers the
untrusted-content side). Evidence screenshots at checkpoints should avoid
credential fields; if one is unavoidable in frame, note it and keep it out of any
persisted artifact.
