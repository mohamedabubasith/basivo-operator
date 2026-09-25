#!/usr/bin/env python3
"""Self-check for the playbook schema validator. No framework — run directly:
    python3 tests/playbook-schema.test.py
Exit 0 = pass. Asserts every shipped playbook is schema-valid AND that a
deliberately-broken playbook is rejected (so the validator isn't a no-op).
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALIDATOR = os.path.join(ROOT, "scripts", "validate-plugin.py")
PLAYBOOKS = os.path.join(ROOT, "playbooks")


def run(path):
    r = subprocess.run([sys.executable, VALIDATOR, path],
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def test_shipped_playbooks_valid():
    code, out = run(PLAYBOOKS)
    assert code == 0, f"shipped playbooks failed validation:\n{out}"
    print("PASS  all shipped playbooks are schema-valid")


def test_broken_playbook_rejected():
    bad = """---
site: broken.com
name: Broken
risk_level: catastrophic
---
# Broken
no required sections here
"""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
        fh.write(bad)
        tmp = fh.name
    try:
        code, out = run(tmp)
        assert code == 1, f"validator should reject a broken playbook but didn't:\n{out}"
        assert "risk_level must be" in out or "missing" in out
        print("PASS  broken playbook is rejected")
    finally:
        os.unlink(tmp)


def test_medium_is_flagship():
    p = os.path.join(PLAYBOOKS, "medium.md")
    assert os.path.isfile(p), "medium.md (flagship) must exist"
    text = open(p, encoding="utf-8").read()
    for marker in ("new-story", "Publish", "Safety Gate", "draft"):
        assert marker in text, f"medium.md should mention '{marker}'"
    print("PASS  medium flagship playbook present and detailed")


if __name__ == "__main__":
    test_shipped_playbooks_valid()
    test_broken_playbook_rejected()
    test_medium_is_flagship()
    print("\nAll playbook-schema tests passed.")
