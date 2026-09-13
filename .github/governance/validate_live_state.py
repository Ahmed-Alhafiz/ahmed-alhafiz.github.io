#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
errors: list[str] = []

state_path = ROOT / "PROJECT_STATE.json"
handoff_path = ROOT / "HANDOFF.md"
os_path = ROOT / "PROJECT_OS.json"

for path in (state_path, handoff_path, os_path):
    if not path.is_file():
        errors.append(f"missing required live governance file: {path.name}")

state: dict = {}
if state_path.is_file():
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"PROJECT_STATE.json is invalid JSON: {exc}")

    for key in (
        "schema_version",
        "project",
        "source_of_truth",
        "branch",
        "head_sha",
        "status",
        "updated_at",
        "current_task",
        "next_action",
        "last_verified",
        "unverified",
        "blockers",
        "local_only_items",
    ):
        if key not in state:
            errors.append(f"PROJECT_STATE.json missing key: {key}")

    if state.get("project") != "ahmed-alhafiz.github.io":
        errors.append("PROJECT_STATE.json project must be ahmed-alhafiz.github.io")
    if state.get("source_of_truth") != "GitHub":
        errors.append("PROJECT_STATE.json source_of_truth must be GitHub")
    if not isinstance(state.get("branch"), str) or not state.get("branch"):
        errors.append("PROJECT_STATE.json branch must be a non-empty string")
    if not re.fullmatch(r"[0-9a-f]{40}", str(state.get("head_sha", ""))):
        errors.append("PROJECT_STATE.json head_sha must be a 40-character Git SHA")
    if not isinstance(state.get("last_verified"), dict):
        errors.append("PROJECT_STATE.json last_verified must be an object")
    for key in ("unverified", "blockers", "local_only_items"):
        if not isinstance(state.get(key), list):
            errors.append(f"PROJECT_STATE.json {key} must be a list")

if handoff_path.is_file():
    handoff = handoff_path.read_text(encoding="utf-8")
    for heading in (
        "## الحالة الحالية",
        "## ما تم فعليًا",
        "## ما يجري العمل عليه الآن",
        "## التحقق المنجز",
        "## ما لم يُفحص / حدود الدليل",
        "## المخاطر أو الـblockers",
        "## الخطوة التالية الدقيقة",
        "## ملفات أو بيانات محلية لا تنتقل عبر Git",
        "## فحص الاستلام على الجهاز الآخر",
    ):
        if heading not in handoff:
            errors.append(f"HANDOFF.md missing required heading: {heading}")
    if "PROJECT_STATE.json" not in handoff:
        errors.append("HANDOFF.md must reference PROJECT_STATE.json")
    if "GitHub" not in handoff:
        errors.append("HANDOFF.md must identify GitHub as the source of truth")

if os_path.is_file():
    try:
        os_data = json.loads(os_path.read_text(encoding="utf-8"))
        handoff_cfg = os_data.get("handoff", {})
        if handoff_cfg.get("live_state_file") != "PROJECT_STATE.json":
            errors.append("PROJECT_OS.json handoff.live_state_file must be PROJECT_STATE.json")
        if handoff_cfg.get("live_handoff_file") != "HANDOFF.md":
            errors.append("PROJECT_OS.json handoff.live_handoff_file must be HANDOFF.md")
        governance_paths = set(os_data.get("path_policy", {}).get("governance", []))
        for required in (
            "HANDOFF.md",
            "HANDOFF_TEMPLATE.md",
            "PROJECT_STATE.json",
            "PROJECT_STATE_TEMPLATE.json",
        ):
            if required not in governance_paths:
                errors.append(f"PROJECT_OS.json governance policy does not protect {required}")
    except json.JSONDecodeError as exc:
        errors.append(f"PROJECT_OS.json is invalid JSON: {exc}")

if errors:
    print("Live governance state FAILED")
    for item in errors:
        print(f"- {item}")
    raise SystemExit(1)

print("Live governance state PASSED")
print("PROJECT_STATE.json, HANDOFF.md, and PROJECT_OS.json are present and internally linked.")
