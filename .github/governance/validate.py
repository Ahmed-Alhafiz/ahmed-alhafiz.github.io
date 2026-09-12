#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = {
    "PROJECT_CONSTITUTION.md": 4000,
    "PRODUCT_SPEC.md": 2500,
    "DECISIONS.md": 1000,
    "QUALITY_GATES.md": 2500,
    "AGENTS.md": 2500,
    "HANDOFF_TEMPLATE.md": 600,
    "PROJECT_STATE_TEMPLATE.json": 200,
    "PROJECT_OS.json": 700,
    "DEVICE_HANDOFF_PROTOCOL.md": 1200,
    "BRANCH_PROTECTION.md": 1000,
    ".github/governance/pr_policy.py": 3000,
    ".github/workflows/pr-policy.yml": 500,
    ".github/PULL_REQUEST_TEMPLATE.md": 1000,
}
errors: list[str] = []
for name, minimum in REQUIRED.items():
    path = ROOT / name
    if not path.is_file():
        errors.append(f"missing required governance file: {name}")
        continue
    raw = path.read_bytes()
    if len(raw) < minimum:
        errors.append(f"{name} is unexpectedly small: {len(raw)} bytes < {minimum}")
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError:
        errors.append(f"{name} is not valid UTF-8")

constitution = (ROOT / "PROJECT_CONSTITUTION.md").read_text(encoding="utf-8") if (ROOT / "PROJECT_CONSTITUTION.md").is_file() else ""
agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8") if (ROOT / "AGENTS.md").is_file() else ""
quality = (ROOT / "QUALITY_GATES.md").read_text(encoding="utf-8") if (ROOT / "QUALITY_GATES.md").is_file() else ""
pr_template = (ROOT / ".github/PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8") if (ROOT / ".github/PULL_REQUEST_TEMPLATE.md").is_file() else ""

for required_ref in ("PROJECT_CONSTITUTION.md", "PRODUCT_SPEC.md", "DECISIONS.md", "QUALITY_GATES.md", "AGENTS.md"):
    if required_ref not in constitution:
        errors.append(f"PROJECT_CONSTITUTION.md does not reference {required_ref}")
for required_ref in ("PROJECT_CONSTITUTION.md", "PRODUCT_SPEC.md", "DECISIONS.md", "QUALITY_GATES.md", "HANDOFF.md"):
    if required_ref not in agents:
        errors.append(f"AGENTS.md does not require reading {required_ref}")
if "Red Team" not in agents and "مراجعة نقدية" not in agents:
    errors.append("AGENTS.md is missing an explicit adversarial/critical review step")
if "منجز" not in quality and "done" not in quality.lower():
    errors.append("QUALITY_GATES.md is missing an explicit done/acceptance standard")
for heading in ("## الهدف", "## مستوى المخاطر", "## التحقق", "## مراجعة نقدية / Red Team", "## ما لم يُفحص", "## الرجوع"):
    if heading not in pr_template:
        errors.append(f"PR template missing required heading: {heading}")

for json_name in ("PROJECT_STATE_TEMPLATE.json", "PROJECT_STATE.json"):
    path = ROOT / json_name
    if not path.is_file():
        continue
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if json_name == "PROJECT_STATE_TEMPLATE.json":
            for key in ("project", "branch", "head_sha", "status", "next_action", "last_verified"):
                if key not in data:
                    errors.append(f"PROJECT_STATE_TEMPLATE.json missing key: {key}")
    except json.JSONDecodeError as exc:
        errors.append(f"{json_name} is invalid JSON: {exc}")

os_path = ROOT / "PROJECT_OS.json"
if os_path.is_file():
    try:
        os_data = json.loads(os_path.read_text(encoding="utf-8"))
        if os_data.get("schema_version") != 2:
            errors.append("PROJECT_OS.json schema_version must be 2")
        enforcement = os_data.get("enforcement", {})
        expected = {
            "branch_protection_required": True,
            "direct_push_to_main_allowed": False,
            "force_push_allowed": False,
            "pull_request_required": True,
            "pr_policy_required": True,
            "red_team_required": True,
        }
        for key, value in expected.items():
            if enforcement.get(key) is not value:
                errors.append(f"PROJECT_OS.json enforcement mismatch: {key} must be {value}")
        handoff = os_data.get("handoff", {})
        if handoff.get("source_of_truth") != "GitHub":
            errors.append("PROJECT_OS.json must define GitHub as handoff source_of_truth")
        if handoff.get("concurrent_work_on_same_branch_allowed") is not False:
            errors.append("PROJECT_OS.json must forbid concurrent work on the same branch")
    except json.JSONDecodeError as exc:
        errors.append(f"PROJECT_OS.json is invalid JSON: {exc}")

if errors:
    print("Governance integrity FAILED")
    for item in errors:
        print(f"- {item}")
    raise SystemExit(1)
print("Governance integrity PASSED")
print("Project OS v2 files, precedence, PR evidence, handoff protocol, and enforcement metadata are valid.")
