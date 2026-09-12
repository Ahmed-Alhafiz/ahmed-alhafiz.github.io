#!/usr/bin/env python3
from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVENT = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
PR = EVENT.get("pull_request")
if not PR:
    print("PR policy: no pull_request payload; nothing to validate.")
    raise SystemExit(0)
BODY = PR.get("body") or ""
BASE = PR["base"]["sha"]
HEAD = PR["head"]["sha"]
CONFIG = json.loads((ROOT / "PROJECT_OS.json").read_text(encoding="utf-8"))
POLICY = CONFIG["path_policy"]
errors: list[str] = []

def run(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True, encoding="utf-8", errors="replace")

def matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pat) for pat in patterns)

def section(title: str) -> str:
    m = re.search(rf"(?ms)^##\s+{re.escape(title)}\s*$\n(.*?)(?=^##\s+|\Z)", BODY)
    return m.group(1).strip() if m else ""

for title in ["الهدف", "مستوى المخاطر", "التحقق", "مراجعة نقدية / Red Team", "ما لم يُفحص", "الرجوع"]:
    if len(section(title)) < 20:
        errors.append(f"PR section is missing or too weak: {title}")
for item in ["اشرح النتيجة المطلوبة ولماذا هذا التغيير ضروري", "اذكر الأوامر أو الفحوص", "اذكر عيبًا أو حالة فشل", "اكتب ما لم يُفحص فعليًا", "اشرح طريقة آمنة ومحددة للتراجع"]:
    if item in BODY:
        errors.append(f"PR template placeholder was not replaced: {item}")
risks = re.findall(r"(?mi)^- \[x\] (P[0-3])\b", BODY)
if len(risks) != 1:
    errors.append("Select exactly one risk level P0/P1/P2/P3 in the PR body")
risk = risks[0] if len(risks) == 1 else None

name_status = run("git", "diff", "--name-status", BASE, HEAD)
changes = []
for line in name_status.splitlines():
    if line.strip():
        parts = line.split("\t")
        changes.append((parts[0], parts[-1]))
paths = [p for _, p in changes]
code_changed = any(matches(p, POLICY.get("code", [])) for p in paths)
ui_changed = any(matches(p, POLICY.get("ui", [])) for p in paths)
sensitive_changed = any(matches(p, POLICY.get("sensitive", [])) for p in paths)
governance_changed = any(matches(p, POLICY.get("governance", [])) for p in paths)
test_deleted = any(s.startswith("D") and matches(p, POLICY.get("tests", [])) for s, p in changes)

if code_changed and len(section("التحقق")) < 60:
    errors.append("Code/product changes require concrete verification evidence")
if ui_changed and "- [x] فُحص الهاتف/RTL" not in BODY:
    errors.append("UI changes require the phone/RTL verification checkbox")
if sensitive_changed and risk == "P3":
    errors.append("Sensitive changes cannot be classified as P3")
if sensitive_changed and len(section("الرجوع")) < 40:
    errors.append("Sensitive changes require a substantive rollback plan")
if governance_changed and "- [x] تغيير حوكمة مقصود" not in BODY:
    errors.append("Governance changes require explicit governance-change acknowledgement")
if test_deleted:
    m = re.search(r"(?mi)^مبرر حذف اختبار:\s*(.+)$", BODY)
    if not m or len(m.group(1).strip()) < 15:
        errors.append("Deleting tests requires an explicit 'مبرر حذف اختبار:' justification")

secret_patterns = [
    re.compile(r"ghp_[A-Za-z0-9]{30,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"SUPABASE_SERVICE_ROLE_KEY\s*=\s*['\"]?[A-Za-z0-9._-]{20,}"),
]
for status, path in changes:
    if status.startswith("D") or path.endswith((".md", ".txt")) or path.endswith(".example"):
        continue
    try:
        content = run("git", "show", f"{HEAD}:{path}")
    except subprocess.CalledProcessError:
        continue
    if any(rx.search(content) for rx in secret_patterns):
        errors.append(f"Possible secret/private key detected in changed file: {path}")

if "- [x] راجعت الفرق الكامل" not in BODY:
    errors.append("The PR must confirm that the full diff was reviewed")
if "- [x] نفذت Red Team" not in BODY:
    errors.append("The PR must confirm an explicit Red Team pass")
if "- [x] صرحت بوضوح بما لم يُفحص" not in BODY:
    errors.append("The PR must explicitly acknowledge unverified areas")

if errors:
    print("PR POLICY FAILED")
    print(f"Changed files: {len(paths)} | code={code_changed} ui={ui_changed} sensitive={sensitive_changed} governance={governance_changed}")
    for item in errors:
        print(f"- {item}")
    raise SystemExit(1)
print("PR POLICY PASSED")
print(f"Risk={risk}; changed={len(paths)}; code={code_changed}; ui={ui_changed}; sensitive={sensitive_changed}; governance={governance_changed}")
