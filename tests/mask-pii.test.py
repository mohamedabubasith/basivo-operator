#!/usr/bin/env python3
"""Self-check for the shared PII/secret masker. Run directly:
    python3 tests/mask-pii.test.py
Exit 0 = pass. Covers the masker rules and that redact-log routes through it.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from mask_pii import mask  # noqa: E402


def test_masks_common_secrets():
    samples = {
        "password: hunter2secret": ("[REDACTED]", "hunter2secret"),
        "token=abcdef123456xyz": ("[REDACTED]", "abcdef123456xyz"),
        "reach me jane.doe@example.com": ("[EMAIL]", "jane.doe@example.com"),
        "Authorization: Bearer abcdefghijklmnop": ("[TOKEN]", "abcdefghijklmnop"),
        "4111 1111 1111 1111": ("[CARD]", "4111 1111 1111 1111"),
        "123-45-6789": ("[SSN]", "123-45-6789"),
    }
    for text, (want, leak) in samples.items():
        out = mask(text)
        assert want in out, f"{want!r} not in {out!r}"
        assert leak not in out, f"leaked {leak!r} in {out!r}"
    print("PASS  common secrets masked")


def test_leaves_plain_prose():
    prose = "Publish a Medium post about serverless cost optimization"
    assert mask(prose) == prose, "plain prose should be untouched"
    # Luhn-invalid long number is not a card.
    assert "[CARD]" not in mask("order id 1234567890123")
    print("PASS  plain content untouched; non-card numbers not masked")


def test_redact_log_uses_masker(tmp="/tmp/basivo-mask.test.log"):
    if os.path.exists(tmp):
        os.remove(tmp)
    subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "redact-log.py"),
         "--log", tmp,
         "--site", "medium.com", "--action", "publish",
         "--url", "https://medium.com/p/x?access_token=SEKRETVALUE12",
         "--outcome", "success",
         "--title", "post password: hunter2secret token=abcdef123456"],
        check=True, capture_output=True)
    logged = open(tmp).read()
    for leak in ("SEKRETVALUE12", "hunter2secret", "abcdef123456"):
        assert leak not in logged, f"redact-log leaked {leak!r}: {logged!r}"
    os.remove(tmp)
    print("PASS  redact-log routes through the masker (no leaks)")


if __name__ == "__main__":
    test_masks_common_secrets()
    test_leaves_plain_prose()
    test_redact_log_uses_masker()
    print("\nAll mask-pii tests passed.")
