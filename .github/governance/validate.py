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
    "LAPTOP_CREDIT_POLICY.md": 2500,
    "BRANCH_PROTECTION.md": 1000,
    ".github/governance/pr_policy.py": 3500,
    ".github/workflows/pr-policy.yml": 500,
    ".github/workflows/governance-integrity.yml": 700,
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
credit = (ROOT / "LAPTOP_CREDIT_POLICY.md").read_text(encoding="utf-8") if (ROOT / "LAPTOP_CREDIT_POLICY.md").is_file() else ""
pr_template = (ROOT / ".github/PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8") if (ROOT / ".github/PULL_REQUEST_TEMPLATE.md").is_file() else ""
pr_policy_source = (ROOT / ".github/governance/pr_policy.py").read_text(encoding="utf-8") if (ROOT / ".github/governance/pr_policy.py").is_file() else ""

for required_ref in ("PROJECT_CONSTITUTION.md", "PRODUCT_SPEC.md", "DECISIONS.md", "QUALITY_GATES.md", "AGENTS.md"):
    if required_ref not in constitution:
        errors.append(f"PROJECT_CONSTITUTION.md does not reference {required_ref}")
for required_ref in ("PROJECT_CONSTITUTION.md", "PRODUCT_SPEC.md", "DECISIONS.md", "QUALITY_GATES.md", "LAPTOP_CREDIT_POLICY.md", "HANDOFF.md"):
    if required_ref not in agents:
        errors.append(f"AGENTS.md does not require reading {required_ref}")
if "Red Team" not in agents and "مراجعة نقدية" not in agents:
    errors.append("AGENTS.md is missing an explicit adversarial/critical review step")
if "منجز" not in quality and "done" not in quality.lower():
    errors.append("QUALITY_GATES.md is missing an explicit done/acceptance standard")
if "الجودة" not in credit or "الرصيد" not in credit:
    errors.append("LAPTOP_CREDIT_POLICY.md must explicitly define quality-first credit control")

for heading in ("## الهدف", "## مستوى المخاطر", "## التحقق", "## مراجعة نقدية / Red Team", "## ما لم يُفحص", "## الرجوع"):
    if heading not in pr_template:
        errors.append(f"PR template missing required heading: {heading}")
current_placeholders = (
    "اشرح النتيجة المطلوبة ولماذا هذا التغيير ضروري.",
    "اذكر الأوامر أو الفحوص التي شُغلت فعليًا ونتيجتها. لا تذكر فحصًا لم يُشغّل.",
    "اذكر عيبًا أو حالة فشل بحثت عنها عمدًا، وما الذي أثبت أو نفى وجودها.",
    "اكتب ما لم يُفحص فعليًا، أو اكتب بوضوح أنه لا يوجد شيء معروف خارج الفحوص المذكورة.",
    "اشرح طريقة آمنة ومحددة للتراجع عن التغيير إذا ظهر regression.",
)
for marker in current_placeholders:
    if marker not in pr_template:
        errors.append(f"PR template prompt changed without governance update: {marker}")
    if marker not in pr_policy_source:
        errors.append(f"PR policy detector is not synchronized with template prompt: {marker}")

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
        if os_data.get("policy_version") != "2.1":
            errors.append("PROJECT_OS.json policy_version must be 2.1")
        enforcement = os_data.get("enforcement", {})
        expected = {
            "branch_protection_required": True,
            "direct_push_to_main_allowed": False,
            "force_push_allowed": False,
            "pull_request_required": True,
            "pr_policy_required": True,
            "red_team_required": True,
            "explicit_unverified_section_required": True,
        }
        for key, value in expected.items():
            if enforcement.get(key) is not value:
                errors.append(f"PROJECT_OS.json enforcement mismatch: {key} must be {value}")
        handoff = os_data.get("handoff", {})
        if handoff.get("source_of_truth") != "GitHub":
            errors.append("PROJECT_OS.json must define GitHub as handoff source_of_truth")
        if handoff.get("concurrent_work_on_same_branch_allowed") is not False:
            errors.append("PROJECT_OS.json must forbid concurrent work on the same branch")
        cost = os_data.get("cost_control", {})
        expected_cost = {
            "policy_file": "LAPTOP_CREDIT_POLICY.md",
            "quality_first": True,
            "heavy_ci_before_ready_pr": False,
            "prefer_local_or_targeted_checks_during_iteration": True,
            "reuse_valid_evidence_when_inputs_are_unchanged": True,
            "avoid_redundant_parallel_agents": True,
            "checkpoint_before_credit_exhaustion": True,
            "quality_may_not_be_reduced_to_save_cost": True,
        }
        for key, value in expected_cost.items():
            if cost.get(key) != value:
                errors.append(f"PROJECT_OS.json cost_control mismatch: {key} must be {value!r}")
        path_policy = os_data.get("path_policy", {})
        for group in ("code", "ui", "sensitive", "tests", "governance"):
            if not isinstance(path_policy.get(group), list) or not path_policy.get(group):
                errors.append(f"PROJECT_OS.json path_policy.{group} must be a non-empty list")
        governance_paths = set(path_policy.get("governance", []))
        for required_path in ("PROJECT_OS.json", "AGENTS.md", "QUALITY_GATES.md", "DEVICE_HANDOFF_PROTOCOL.md", "LAPTOP_CREDIT_POLICY.md", "BRANCH_PROTECTION.md", ".github/governance/**", ".github/workflows/pr-policy.yml", ".github/workflows/governance-integrity.yml", ".github/PULL_REQUEST_TEMPLATE.md"):
            if required_path not in governance_paths:
                errors.append(f"PROJECT_OS.json governance policy does not protect {required_path}")
    except json.JSONDecodeError as exc:
        errors.append(f"PROJECT_OS.json is invalid JSON: {exc}")

if errors:
    print("Governance integrity FAILED")
    for item in errors:
        print(f"- {item}")
    raise SystemExit(1)
print("Governance integrity PASSED")
print("Project OS v2.1, credit policy, PR evidence, handoff protocol, and enforcement metadata are internally consistent.")
