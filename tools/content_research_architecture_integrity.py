#!/usr/bin/env python3
"""Validate the reference-grade content standard and Teaching the Names plan.

This gate does not pretend to judge theological or scientific truth by code.
It enforces the minimum inspectable structure required before a public rewrite:
complete source metadata, explicit claim types and limits, valid source links,
religion/science separation, a clean original-framework disclosure, and a ban
on treating the author's book as empirical evidence.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
STANDARD = ROOT / ".github/CONTENT_REFERENCE_GRADE_STANDARD.md"
ARCHITECTURE = ROOT / ".github/TEACHING_NAMES_AI_REBUILD_ARCHITECTURE.md"
REGISTER = ROOT / ".github/teaching_names_ai_source_register.json"
AUDIT = ROOT / ".github/CONTENT_AUDIT_2026-09-03_BATCH_1.md"

EXPECTED_CLAIMS = [f"C{i:02d}" for i in range(1, 15)]
EXPECTED_RELIGIOUS = [f"R{i:02d}" for i in range(1, 7)]
EXPECTED_TECHNICAL = [f"A{i:02d}" for i in range(1, 23)]
ALLOWED_CONFIDENCE = {"high", "medium", "open"}
ALLOWED_CLAIM_TYPES = {
    "documented_interpretive",
    "documented_interpretive_diversity",
    "author_synthesis_from_text",
    "empirical_and_conceptual",
    "contested_synthesis",
    "empirical",
    "methodological",
    "empirical_with_limit",
    "philosophical_interpretation",
    "philosophical_argument",
    "author_synthesis",
    "author_boundary_claim",
}


def fail(message: str) -> None:
    raise SystemExit(f"CONTENT ARCHITECTURE ERROR: {message}")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{path.relative_to(ROOT)} is invalid JSON: {exc}")


def validate_files() -> None:
    for path in (STANDARD, ARCHITECTURE, REGISTER, AUDIT):
        if not path.is_file():
            fail(f"required file missing: {path.relative_to(ROOT)}")
        if path.stat().st_size < 1_000:
            fail(f"required file is suspiciously small: {path.relative_to(ROOT)}")


def validate_standard() -> None:
    text = STANDARD.read_text(encoding="utf-8")
    required = (
        "بوابات رفض لا يعوضها مجموع النقاط",
        "سلامة المجال الديني",
        "سلامة المجال العلمي",
        "استقلال الدليل",
        "قابلية الفحص",
        "85–100: ركيزة مرجعية",
        "أقوى ثلاثة اعتراضات",
        "نسخة إنجليزية تحريرية كاملة",
        "منشأ موضوعي للسؤال",
        "ليس مصدرًا علميًا لإثبات الجواب",
        "لا تُبنى حلقة استشهاد ذاتي",
    )
    for token in required:
        if token not in text:
            fail(f"reference-grade standard lost required rule: {token}")


def validate_architecture() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    required = (
        "مصفوفة الاسم–العالم–المسؤولية",
        "الوحدة الحجاجية هي البقرة 30–33",
        "الوعي ليس «الطبقة السابعة»",
        "بروتوكول الاختبار الخصومي",
        "أقوى الاعتراضات",
        "Turing",
        "Searle",
        "Harnad",
        "Bender & Koller",
        "Piantadosi & Hill",
        "Causal Abstraction",
        "لا تُجعل «الأسماء» مرادفة آليًا لـtokens",
        "منشأ موضوعي للسؤال",
        "نتيجة 85/100 فأكثر",
    )
    for token in required:
        if token not in text:
            fail(f"Teaching the Names architecture lost required element: {token}")

    claim_headings = set(re.findall(r"^### (C\d{2})\b", text, flags=re.MULTILINE))
    if claim_headings != set(EXPECTED_CLAIMS):
        fail(f"architecture claim headings mismatch: {sorted(claim_headings)}")

    matrix_rows = re.findall(r"^\| [1-6]\. ", text, flags=re.MULTILINE)
    if len(matrix_rows) != 6:
        fail(f"expected six matrix layers, found {len(matrix_rows)}")

    if "الوعي" not in text or "سؤال مستقل" not in text:
        fail("consciousness must remain a separate unresolved question")


def validate_url(url: str, context: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        fail(f"{context}: URL must be absolute HTTPS: {url!r}")


def validate_register() -> None:
    data = load_json(REGISTER)
    if data.get("schema_version") != "0.2-planning":
        fail("source register schema version drifted")
    if data.get("status") != "research_architecture_complete_article_not_yet_rewritten":
        fail("source register must not imply the public article was rewritten")

    pillar = data.get("pillar")
    if not isinstance(pillar, dict):
        fail("pillar metadata missing")
    if pillar.get("original_framework_ar") != "مصفوفة الاسم–العالم–المسؤولية":
        fail("Arabic framework name mismatch")
    if pillar.get("original_framework_en") != "The Name–World–Responsibility Matrix":
        fail("English framework name mismatch")
    origin = pillar.get("thematic_origin", {})
    if origin.get("relationship") != "thematic_origin_not_empirical_evidence":
        fail("the author's book must remain thematic origin, not empirical evidence")
    for key in ("arabic_url", "english_url"):
        validate_url(pillar.get(key, ""), f"pillar.{key}")

    claims = data.get("claims")
    sources = data.get("sources")
    if not isinstance(claims, list) or not isinstance(sources, list):
        fail("claims and sources must be arrays")
    if [claim.get("id") for claim in claims] != EXPECTED_CLAIMS:
        fail("claim IDs/order must be C01–C14")
    expected_sources = EXPECTED_RELIGIOUS + EXPECTED_TECHNICAL
    if [source.get("id") for source in sources] != expected_sources:
        fail("source IDs/order must be R01–R06 then A01–A22")

    source_map = {source["id"]: source for source in sources}
    if len(source_map) != len(sources):
        fail("duplicate source IDs")

    for source in sources:
        sid = source["id"]
        for key in ("domain", "type", "title", "url", "status", "role"):
            if not source.get(key):
                fail(f"{sid}: missing source field {key}")
        validate_url(source["url"], sid)
        if sid.startswith("R") and source["domain"] not in {
            "quran",
            "tafsir",
            "quranic_lexicography",
        }:
            fail(f"{sid}: religious source domain mismatch")
        if sid.startswith("A") and source["domain"] in {
            "quran",
            "tafsir",
            "quranic_lexicography",
        }:
            fail(f"{sid}: technical source misclassified as religious")

    for claim in claims:
        cid = claim["id"]
        for key in (
            "domain",
            "claim_ar",
            "claim_en",
            "type",
            "confidence",
            "support",
            "counterweight",
            "limit_ar",
            "limit_en",
        ):
            if key not in claim or claim[key] in (None, ""):
                fail(f"{cid}: missing claim field {key}")
        if claim["type"] not in ALLOWED_CLAIM_TYPES:
            fail(f"{cid}: invalid type {claim['type']!r}")
        if claim["confidence"] not in ALLOWED_CONFIDENCE:
            fail(f"{cid}: invalid confidence {claim['confidence']!r}")
        if claim["type"] in {"author_synthesis", "contested_synthesis"} and claim["confidence"] != "open":
            fail(f"{cid}: synthesis must remain open")
        support = claim["support"]
        counterweight = claim["counterweight"]
        if not isinstance(support, list) or not support:
            fail(f"{cid}: support list must be non-empty")
        if not isinstance(counterweight, list):
            fail(f"{cid}: counterweight must be an array")
        unknown = sorted((set(support) | set(counterweight)) - set(source_map))
        if unknown:
            fail(f"{cid}: unknown source IDs: {unknown}")
        if len(claim["claim_ar"].split()) < 8 or len(claim["claim_en"].split()) < 8:
            fail(f"{cid}: bilingual claim statement too short")
        if len(claim["limit_ar"].split()) < 5 or len(claim["limit_en"].split()) < 5:
            fail(f"{cid}: bilingual limitation too short")

    for cid in ("C01", "C02", "C03", "C14"):
        claim = claims[EXPECTED_CLAIMS.index(cid)]
        if not any(sid.startswith("R") for sid in claim["support"]):
            fail(f"{cid}: religious claim lacks primary religious support")
    for cid in ("C04", "C06", "C07", "C08", "C09", "C10"):
        claim = claims[EXPECTED_CLAIMS.index(cid)]
        if not any(sid.startswith("A") for sid in claim["support"]):
            fail(f"{cid}: technical claim lacks technical support")

    excluded = data.get("source_policy", {}).get("excluded", [])
    if "the author's book as scientific evidence" not in excluded:
        fail("source policy no longer excludes the author's book as scientific evidence")

    frontier = source_map["A22"]
    if frontier.get("status") != "frontier_excluded_from_central_conclusion":
        fail("2026 global-workspace preprint must stay outside central conclusion")

    grouped = [
        source["id"]
        for source in sources
        if source.get("status") == "derived_source_group"
    ]
    if grouped != ["A15"]:
        fail("the temporary grouped source must remain isolated as A15 until replacement")
    next_validation = " ".join(data.get("next_validation", []))
    if "Resolve A15" not in next_validation:
        fail("publication plan must explicitly require replacing grouped pseudo-source A15")


def main() -> None:
    validate_files()
    validate_standard()
    validate_architecture()
    validate_register()
    print(
        "Reference-grade research architecture passed: governing standard present, "
        "six-layer Teaching the Names matrix, 14 bilingual claims, 28 classified planning sources, "
        "valid source references, explicit manuscript/evidence separation, isolated temporary A15, "
        "and frontier-result containment."
    )


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
