#!/usr/bin/env python3
"""Shared PII / secret masker for basivo-operator.

Single source of truth for turning sensitive substrings into typed tags like
[EMAIL], [TOKEN], [PASSWORD], [CARD]. Used by:
  - redact-log.py       (audit log — never store secrets)
  - the engine's Report/echo step (never surface creds back to the user in logs)

IMPORTANT: mask() is for LOGS, REPORTS, and echoes — NOT for the content the
engine types into a page. The user's actual post/body is inserted verbatim; you
only mask what gets recorded or shown back. See
skills/browser-operator/references/pii-and-secret-handling.md.

CLI:
  echo "token=abc123..." | python3 scripts/mask_pii.py     # mask stdin
  python3 scripts/mask_pii.py --selftest                   # run asserts
"""
import re
import sys

# Ordered most-specific → least. Each: (compiled regex, replacement).
# Replacement may reference groups (e.g. keep the key name, mask the value).
_RULES = [
    # Structured secrets (provider-shaped) — match before generic rules.
    (re.compile(r"\beyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}"), "[JWT]"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[AWS_KEY]"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"), "[GITHUB_TOKEN]"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "[SLACK_TOKEN]"),
    (re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"), "[GOOGLE_API_KEY]"),
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "[API_KEY]"),
    (re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{10,}"), "Bearer [TOKEN]"),
    # key = value  credential pairs (keep the key name, mask the value).
    (re.compile(
        r"(?i)\b(password|passwd|pwd|secret|token|api[_-]?key|access[_-]?token|"
        r"refresh[_-]?token|client[_-]?secret|auth|otp|2fa|cvv|pin)\b"
        r"(\s*[:=]\s*|\s+is\s+|\s+)"
        r"[\"']?[^\s\"',;]{3,}"),
     r"\1=[REDACTED]"),
    # Payment card (13–19 digits, optional spaces/dashes) — Luhn-checked below.
    (re.compile(r"\b(?:\d[ -]?){13,19}\b"), "[CARD]"),
    # US SSN.
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN]"),
    # Email.
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"), "[EMAIL]"),
    # IPv4.
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "[IP]"),
    # URL query secrets: ?token=... &access_token=... &code=...
    (re.compile(r"(?i)([?&](?:access_token|token|code|session|sig|auth|key)=)[^&\s]+"),
     r"\1[REDACTED]"),
]

# Generic high-entropy blob: 32+ chars mixing letters AND digits. Gated (see
# note) to avoid mangling ordinary long words. ponytail: heuristic — length+mix
# only; upgrade to real entropy scoring if false positives matter.
_GENERIC = re.compile(r"\b(?=[A-Za-z0-9_\-]{32,}\b)(?=[^\s]*[A-Za-z])(?=[^\s]*\d)[A-Za-z0-9_\-]{32,}\b")


def _luhn_ok(digits):
    total, alt = 0, False
    for d in reversed(digits):
        n = int(d)
        if alt:
            n *= 2
            if n > 9:
                n -= 9
        total += n
        alt = not alt
    return total % 10 == 0


def _mask_card(m):
    digits = re.sub(r"\D", "", m.group(0))
    return "[CARD]" if 13 <= len(digits) <= 19 and _luhn_ok(digits) else m.group(0)


def mask(text, aggressive=True):
    """Return text with PII/secrets replaced by typed tags.

    aggressive=True (default) also masks generic high-entropy blobs — right for
    logs and reports. Set False to only mask the clearly-typed patterns.
    """
    if text is None:
        return ""
    out = str(text)
    for rx, repl in _RULES:
        if repl == "[CARD]":
            out = rx.sub(_mask_card, out)
        else:
            out = rx.sub(repl, out)
    if aggressive:
        out = _GENERIC.sub("[SECRET]", out)
    return out


def _selftest():
    cases = [
        ("my password: hunter2secret", "[REDACTED]", "hunter2secret"),
        ("token=abcdef123456xyz", "[REDACTED]", "abcdef123456xyz"),
        ("email me at jane.doe@example.com", "[EMAIL]", "jane.doe@example.com"),
        ("Authorization: Bearer abcdefghijklmnop", "[TOKEN]", "abcdefghijklmnop"),
        ("gho_ABCDEFGHIJKLMNOPQRSTUVWXYZ012345", "[GITHUB_TOKEN]", "gho_ABCDEFG"),
        ("card 4111 1111 1111 1111 ok", "[CARD]", "4111 1111 1111 1111"),
        ("ssn 123-45-6789", "[SSN]", "123-45-6789"),
        ("key AKIAIOSFODNN7EXAMPLE end", "[AWS_KEY]", "AKIAIOSFODNN7EXAMPLE"),
        ("visit https://x.com/p?access_token=SEKRETVALUE12 now", "[REDACTED]", "SEKRETVALUE12"),
    ]
    for text, must_have, must_not in cases:
        got = mask(text)
        assert must_have in got, f"expected {must_have!r} in {got!r}"
        assert must_not not in got, f"leaked {must_not!r} in {got!r}"
    # A card number that fails Luhn is NOT masked (avoid false positives).
    assert "[CARD]" not in mask("order 1234567890123 placed")
    # Plain prose is left alone.
    assert mask("Publish a post about serverless costs") == "Publish a post about serverless costs"
    print("mask_pii selftest: all cases passed")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    else:
        data = " ".join(a for a in sys.argv[1:] if a != "--selftest") or sys.stdin.read()
        sys.stdout.write(mask(data))
