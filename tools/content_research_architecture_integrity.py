#!/usr/bin/env python3
"""Validate the reference-grade Teaching the Names research architecture.

This gate cannot adjudicate theology, semantics, or machine understanding. It
can, however, prevent known editorial failures: using the author's manuscript
as empirical evidence, treating an unverified attribution as a source,
allowing one-way claim citations, presenting a planning register as a public
publication, or letting frontier preprints carry a central conclusion.
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
PLANNING = ROOT / ".github/teaching_names_ai_source_register.json"
VERIFIED = ROOT / ".github/teaching_names_ai_verified_manifest.json"
TAFSIR = ROOT / ".github/TEACHING_NAMES_TAFSIR_VERIFICATION_2026-09-03.md"
AUDIT = ROOT / ".github/CONTENT_AUDIT_2026-09-03_BATCH_1.md"
DRAFT = ROOT / ".github/drafts/TEACHING_NAMES_ARABIC_DRAFT_01_QURANIC_UNIT.md"

EXPECTED_CLAIMS = [f"C{i:02d}" for i in range(1, 15)]
EXPECTED_SOURCES = [f"R{i:02d}" for i in range(1, 7)] + [f"A{i:02d}" for i in range(1, 23)]
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


def validate_https(url: str, context: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        fail(f"{context}: expected absolute HTTPS URL, found {url!r}")


def validate_required_files() -> None:
    for path in (STANDARD, ARCHITECTURE, PLANNING, VERIFIED, TAFSIR, AUDIT, DRAFT):
        if not path.is_file():
            fail(f"required file missing: {path.relative_to(ROOT)}")
        minimum = 900 if path.suffix == ".json" else 1_000
        if path.stat().st_size < minimum:
            fail(f"required file is suspiciously small: {path.relative_to(ROOT)}")


def validate_standard_and_architecture() -> None:
    standard = STANDARD.read_text(encoding="utf-8")
    for token in (
        "بوابات رفض لا يعوضها مجموع النقاط",
        "سلامة المجال الديني",
        "سلامة المجال العلمي",
        "استقلال الدليل",
        "قابلية الفحص",
        "85–100: ركيزة مرجعية",
        "أقوى ثلاثة اعتراضات",
        "نسخة إنجليزية تحريرية كاملة",
        "لا تُبنى حلقة استشهاد ذاتي",
    ):
        if token not in standard:
            fail(f"reference-grade standard lost required rule: {token}")

    architecture = ARCHITECTURE.read_text(encoding="utf-8")
    for token in (
        "مصفوفة الاسم–العالم–المسؤولية",
        "الوحدة الحجاجية هي البقرة 30–33",
        "الوعي ليس «الطبقة السابعة»",
        "بروتوكول الاختبار الخصومي",
        "أقوى الاعتراضات",
        "لا تُجعل «الأسماء» مرادفة آليًا لـtokens",
        "منشأً موضوعيًا للسؤال لا دليلًا تقنيًا",
        "نتيجة 85/100 فأكثر",
    ):
        if token not in architecture:
            fail(f"Teaching the Names architecture lost required element: {token}")

    headings = set(re.findall(r"^### (C\d{2})\b", architecture, flags=re.MULTILINE))
    if headings != set(EXPECTED_CLAIMS):
        fail(f"architecture claim headings mismatch: {sorted(headings)}")
    if len(re.findall(r"^\| [1-6]\. ", architecture, flags=re.MULTILINE)) != 6:
        fail("architecture must contain exactly six matrix layers")


def validate_planning_state() -> None:
    data = load_json(PLANNING)
    if data.get("schema_version") != "0.2-planning":
        fail("planning register schema version drifted")
    if data.get("status") != "research_architecture_complete_article_not_yet_rewritten":
        fail("planning register falsely implies a completed public rewrite")
    origin = data.get("pillar", {}).get("thematic_origin", {})
    if origin.get("relationship") != "thematic_origin_not_empirical_evidence":
        fail("planning register promoted the author's manuscript to empirical evidence")
    if len(data.get("claims", [])) != 14 or len(data.get("sources", [])) != 28:
        fail("planning register inventory must remain 14 claims and 28 sources")


def validate_tafsir_record() -> None:
    text = TAFSIR.read_text(encoding="utf-8")
    required = (
        "PRIMARY_TEXT_VERIFIED_PREPUBLICATION",
        "الوحدة الحجاجية ليست عبارة ﴿وعلّم آدم الأسماء كلها﴾ وحدها",
        "نقل الطبري القول بأسماء كل شيء، لكنه رجح قراءة أضيق",
        "فرّق القرطبي بين الاسم بوصفه عبارة",
        "عرض الرازي وناصر قراءة",
        "ربط ابن عاشور ﴿وعلم آدم الأسماء كلها﴾ مباشرة",
        "أبو حيان — البحر المحيط",
        "يُحذف الراغب مؤقتًا",
        "لا يُنسب اسم «مصفوفة الاسم–العالم–المسؤولية» إلى المفسرين",
        "المراجعة الشرعية/التفسيرية المستقلة: لم تتم بعد",
    )
    for token in required:
        if token not in text:
            fail(f"primary-tafsir verification record lost required correction: {token}")


def validate_verified_manifest() -> None:
    data = load_json(VERIFIED)
    if data.get("schema_version") != "1.0-prepublication":
        fail("verified manifest schema version mismatch")
    if data.get("status") != "verified_claim_evidence_manifest_article_draft_pending":
        fail("verified manifest status mismatch")
    if data.get("publication_state") != "not_public_not_merged":
        fail("verified manifest must not claim publication")

    pillar = data.get("pillar", {})
    if pillar.get("framework_ar") != "مصفوفة الاسم–العالم–المسؤولية":
        fail("verified manifest Arabic framework name mismatch")
    if pillar.get("framework_en") != "The Name–World–Responsibility Matrix":
        fail("verified manifest English framework name mismatch")
    if pillar.get("thematic_origin", {}).get("evidentiary_role") != "question_origin_only":
        fail("thematic manuscript must remain question origin only")
    if pillar.get("external_review") != "not_completed":
        fail("verified manifest falsely implies external review")

    claims = data.get("claims")
    sources = data.get("sources")
    if not isinstance(claims, list) or not isinstance(sources, list):
        fail("verified manifest claims and sources must be arrays")
    if [claim.get("id") for claim in claims] != EXPECTED_CLAIMS:
        fail("verified manifest claim IDs/order must be C01–C14")
    if [source.get("id") for source in sources] != EXPECTED_SOURCES:
        fail("verified manifest source IDs/order must be R01–R06 then A01–A22")

    claim_map = {claim["id"]: claim for claim in claims}
    source_map = {source["id"]: source for source in sources}
    if len(claim_map) != 14 or len(source_map) != 28:
        fail("duplicate claim or source IDs detected")

    for claim in claims:
        cid = claim["id"]
        for field in (
            "domain",
            "type",
            "confidence",
            "claim_ar",
            "claim_en",
            "supports",
            "qualifies",
            "limit_ar",
            "limit_en",
        ):
            if field not in claim or claim[field] in (None, ""):
                fail(f"{cid}: missing field {field}")
        if claim["type"] not in ALLOWED_CLAIM_TYPES:
            fail(f"{cid}: invalid claim type {claim['type']!r}")
        if claim["confidence"] not in ALLOWED_CONFIDENCE:
            fail(f"{cid}: invalid confidence {claim['confidence']!r}")
        if claim["type"] in {"contested_synthesis", "author_synthesis"} and claim["confidence"] != "open":
            fail(f"{cid}: synthesis must remain open")
        if not isinstance(claim["supports"], list) or not claim["supports"]:
            fail(f"{cid}: support list must be non-empty")
        if not isinstance(claim["qualifies"], list):
            fail(f"{cid}: qualifies must be an array")
        unknown = sorted((set(claim["supports"]) | set(claim["qualifies"])) - set(source_map))
        if unknown:
            fail(f"{cid}: unknown source IDs {unknown}")
        if len(claim["claim_ar"].split()) < 8 or len(claim["claim_en"].split()) < 8:
            fail(f"{cid}: bilingual claim is too short")
        if len(claim["limit_ar"].split()) < 5 or len(claim["limit_en"].split()) < 5:
            fail(f"{cid}: bilingual limitation is too short")
        for sid in claim["supports"]:
            if cid not in source_map[sid].get("supports_claims", []):
                fail(f"reciprocity failure: {cid} supports {sid}, but {sid} does not support {cid}")
        for sid in claim["qualifies"]:
            if cid not in source_map[sid].get("qualifies_claims", []):
                fail(f"reciprocity failure: {cid} is qualified by {sid}, but {sid} does not qualify {cid}")

    for source in sources:
        sid = source["id"]
        for field in (
            "domain",
            "type",
            "title",
            "url",
            "verification_status",
            "supports_claims",
            "qualifies_claims",
        ):
            if field not in source or source[field] in (None, ""):
                fail(f"{sid}: missing field {field}")
        validate_https(source["url"], sid)
        if not isinstance(source["supports_claims"], list) or not isinstance(source["qualifies_claims"], list):
            fail(f"{sid}: reciprocal claim lists must be arrays")
        unknown = sorted((set(source["supports_claims"]) | set(source["qualifies_claims"])) - set(claim_map))
        if unknown:
            fail(f"{sid}: unknown claim IDs {unknown}")
        for cid in source["supports_claims"]:
            if sid not in claim_map[cid]["supports"]:
                fail(f"reciprocity failure: {sid} supports {cid}, but {cid} does not cite {sid}")
        for cid in source["qualifies_claims"]:
            if sid not in claim_map[cid]["qualifies"]:
                fail(f"reciprocity failure: {sid} qualifies {cid}, but {cid} does not cite {sid}")

    for rid in EXPECTED_SOURCES[:6]:
        if source_map[rid]["verification_status"] != "primary_text_verified":
            fail(f"{rid}: tafsir/Qur'an source is not marked primary-text verified")
    if "Abu Hayyan" not in source_map["R06"]["title"] or "albahr-almuheet" not in source_map["R06"]["url"]:
        fail("R06 must be the verified Abu Hayyan source")
    if "Hewitt and Liang" not in source_map["A15"]["title"] or source_map["A15"]["url"] != "https://aclanthology.org/D19-1275/":
        fail("A15 must be the primary control-task probing paper")
    if source_map["A22"]["verification_status"] != "frontier_excluded_from_central_conclusion":
        fail("A22 frontier result must remain outside the central conclusion")

    excluded = data.get("excluded_pending_verification", [])
    if not any("Raghib" in item.get("source", "") for item in excluded if isinstance(item, dict)):
        fail("unverified al-Raghib attribution is not explicitly excluded")


def validate_internal_draft() -> None:
    text = DRAFT.read_text(encoding="utf-8")
    for token in (
        "مسودة داخلية غير منشورة",
        "البقرة 30–33",
        "الخلافة",
        "لا علم لنا إلا ما علمتنا",
        "الطبري",
        "القرطبي",
        "الرازي",
        "ابن عاشور",
        "أبو حيان",
        "حد المقارنة مع الذكاء الاصطناعي",
        "لا تعني token",
        "لم تتم مراجعة شرعية مستقلة",
    ):
        if token not in text:
            fail(f"internal Qur'anic-unit draft lost required element: {token}")
    if len(text.split()) < 1_100:
        fail("internal Qur'anic-unit draft is below the 1,100-word minimum")


def main() -> None:
    validate_required_files()
    validate_standard_and_architecture()
    validate_planning_state()
    validate_tafsir_record()
    validate_verified_manifest()
    validate_internal_draft()
    print(
        "Reference-grade research architecture passed: primary tafsir corrections recorded; "
        "14 bilingual claims and 28 sources are fully reciprocal; Abu Hayyan replaces the "
        "unverified al-Raghib attribution; Hewitt–Liang replaces the temporary probe source; "
        "frontier evidence is contained; and the first Qur'anic-unit draft remains explicitly unpublished."
    )


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
