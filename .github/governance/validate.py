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
state_template = ROOT / "PROJECT_STATE_TEMPLATE.json"
if state_template.is_file():
    try:
        data = json.loads(state_template.read_text(encoding="utf-8"))
        for key in ("project", "branch", "head_sha", "status", "next_action", "last_verified"):
            if key not in data:
                errors.append(f"PROJECT_STATE_TEMPLATE.json missing key: {key}")
    except json.JSONDecodeError as exc:
        errors.append(f"PROJECT_STATE_TEMPLATE.json is invalid JSON: {exc}")
live_state = ROOT / "PROJECT_STATE.json"
if live_state.is_file():
    try:
        json.loads(live_state.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"PROJECT_STATE.json is invalid JSON: {exc}")
if errors:
    print("Governance integrity FAILED")
    for item in errors:
        print(f"- {item}")
    raise SystemExit(1)
print("Governance integrity PASSED")
print("Required governance files, precedence references, review step, and state schema are present.")
