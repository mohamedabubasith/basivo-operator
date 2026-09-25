#!/usr/bin/env python3
"""Validate the basivo-operator plugin: manifest, frontmatter, links, playbook schema,
no secrets, no stray absolute paths. Exit 0 = clean, 1 = errors.

Usage: scripts/validate-plugin.py            (validates the plugin root)
       scripts/validate-plugin.py <path>      (validate one playbook or dir)
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []
warns = []


def err(msg):
    errors.append(msg)


def warn(msg):
    warns.append(msg)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def parse_frontmatter(text):
    """Return (frontmatter_str, body) or (None, text). Naive YAML-ish, no deps."""
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    return text[3:end].strip(), text[end + 4:]


# ---- manifest ----------------------------------------------------------------
def check_manifest():
    path = os.path.join(ROOT, ".claude-plugin", "plugin.json")
    if not os.path.isfile(path):
        err(".claude-plugin/plugin.json missing")
        return
    try:
        data = json.loads(read(path))
    except json.JSONDecodeError as e:
        err(f"plugin.json invalid JSON: {e}")
        return
    for key in ("name", "version", "description"):
        if not data.get(key):
            err(f"plugin.json missing required key: {key}")
    if data.get("name") and not re.match(r"^[a-z0-9-]+$", data["name"]):
        err(f"plugin.json name should be kebab-case: {data['name']}")
    if data.get("version") and not re.match(r"^\d+\.\d+\.\d+", data["version"]):
        err(f"plugin.json version should be semver: {data['version']}")


# ---- md frontmatter (skills/commands/agents) ---------------------------------
def check_md_frontmatter():
    specs = [
        ("commands", ("description",)),
        ("agents", ("name", "description")),
    ]
    for folder, required in specs:
        base = os.path.join(ROOT, folder)
        for name in sorted(os.listdir(base)) if os.path.isdir(base) else []:
            if not name.endswith(".md"):
                continue
            fm, _ = parse_frontmatter(read(os.path.join(base, name)))
            if fm is None:
                err(f"{folder}/{name}: missing frontmatter")
                continue
            for key in required:
                if not re.search(rf"^{key}\s*:", fm, re.M):
                    err(f"{folder}/{name}: frontmatter missing '{key}'")
    # skills
    skills = os.path.join(ROOT, "skills")
    for d in sorted(os.listdir(skills)) if os.path.isdir(skills) else []:
        sp = os.path.join(skills, d, "SKILL.md")
        if not os.path.isfile(sp):
            err(f"skills/{d}: SKILL.md missing")
            continue
        fm, _ = parse_frontmatter(read(sp))
        if fm is None:
            err(f"skills/{d}/SKILL.md: missing frontmatter")
            continue
        for key in ("name", "description"):
            if not re.search(rf"^{key}\s*:", fm, re.M):
                err(f"skills/{d}/SKILL.md: frontmatter missing '{key}'")


# ---- playbook schema ---------------------------------------------------------
REQUIRED_PB_KEYS = ["site", "name", "version", "last_verified", "risk_level",
                    "login_signals", "capabilities", "irreversible_actions"]
REQUIRED_PB_SECTIONS = ["# ", "## Entry points", "## Flows", "## Verification recipe",
                        "## Change log"]


def check_playbook(path):
    text = read(path)
    fm, body = parse_frontmatter(text)
    rel = os.path.relpath(path, ROOT)
    if fm is None:
        err(f"{rel}: missing frontmatter")
        return
    for key in REQUIRED_PB_KEYS:
        if not re.search(rf"^{key}\s*:", fm, re.M):
            err(f"{rel}: playbook frontmatter missing '{key}'")
    m = re.search(r"^risk_level\s*:\s*(\w+)", fm, re.M)
    if m and m.group(1) not in ("low", "medium", "high"):
        err(f"{rel}: risk_level must be low|medium|high (got {m.group(1)})")
    m = re.search(r"^last_verified\s*:\s*(\S+)", fm, re.M)
    if m and not re.match(r"\d{4}-\d{2}-\d{2}", m.group(1)):
        err(f"{rel}: last_verified must be YYYY-MM-DD (got {m.group(1)})")
    for sec in REQUIRED_PB_SECTIONS:
        if sec not in text:
            err(f"{rel}: missing required section starting '{sec.strip()}'")


def check_playbooks():
    base = os.path.join(ROOT, "playbooks")
    if not os.path.isdir(base):
        err("playbooks/ missing")
        return
    files = [f for f in os.listdir(base) if f.endswith(".md")]
    if not files:
        err("playbooks/ has no playbooks")
    for f in sorted(files):
        check_playbook(os.path.join(base, f))


# ---- secrets & absolute paths ------------------------------------------------
SECRET_RE = re.compile(r"(?i)(password|api[_-]?key|secret|bearer\s+[a-z0-9._-]{12,}|xox[baprs]-)\s*[:=]\s*['\"]?[a-z0-9._\-]{8,}")
ABS_PATH_RE = re.compile(r"(?<!\$\{)(/Users/|/home/[a-z])")


def check_no_secrets_or_abspaths():
    for dirpath, dirs, files in os.walk(ROOT):
        if "/.git" in dirpath or "/dist" in dirpath:
            continue
        for f in files:
            if not f.endswith((".md", ".json", ".py", ".sh")):
                continue
            p = os.path.join(dirpath, f)
            text = read(p)
            rel = os.path.relpath(p, ROOT)
            if SECRET_RE.search(text):
                err(f"{rel}: looks like it contains a hard-coded secret")
            if rel == "scripts/validate-plugin.py":
                continue  # this file necessarily contains the abspath regex literal
            for ln, line in enumerate(text.splitlines(), 1):
                # allow example/setup command lines that reference $HOME-style paths
                if ABS_PATH_RE.search(line) and "$HOME" not in line and "example" not in rel.lower():
                    if "/Applications/Google Chrome.app" in line:
                        continue  # documented launch command
                    warn(f"{rel}:{ln}: stray absolute path (prefer ${{CLAUDE_PLUGIN_ROOT}}/$HOME): {line.strip()[:80]}")


# ---- relative links ----------------------------------------------------------
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def check_relative_links():
    for dirpath, dirs, files in os.walk(ROOT):
        for f in files:
            if not f.endswith(".md"):
                continue
            p = os.path.join(dirpath, f)
            for target in LINK_RE.findall(read(p)):
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                target = target.split("#")[0]
                if not target:
                    continue
                resolved = os.path.normpath(os.path.join(dirpath, target))
                if not os.path.exists(resolved):
                    warn(f"{os.path.relpath(p, ROOT)}: broken relative link -> {target}")


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if os.path.isfile(arg):
            check_playbook(arg)
        else:
            for f in sorted(os.listdir(arg)):
                if f.endswith(".md"):
                    check_playbook(os.path.join(arg, f))
    else:
        check_manifest()
        check_md_frontmatter()
        check_playbooks()
        check_no_secrets_or_abspaths()
        check_relative_links()

    for w in warns:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{len(errors)} error(s), {len(warns)} warning(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
