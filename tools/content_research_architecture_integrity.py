#!/usr/bin/env python3
"""Validate the pre-publication Teaching the Names research base.

This gate does not claim to decide theological truth, semantic understanding,
or consciousness by code. It enforces the inspectable conditions that the
project has adopted: source separation, corrected attributions, reciprocal
claim/evidence links, explicit review and publication state, substantive
religious and technical units, and containment of frontier evidence.
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
VERIFIED = ROOT / ".github/teaching_names_ai_verified_claims.json"
TAFSIR = ROOT / ".github/TEACHING_NAMES_TAFSIR_VERIFICATION_2026-09-03.md"
TECHNICAL = ROOT / ".github/TEACHING_NAMES_TECHNICAL_VERIFICATION_2026-09-03.md"
AUDIT = ROOT / ".github/CONTENT_AUDIT_2026-09-03_BATCH_1.md"
DRAFT_QURANIC = ROOT / ".github/drafts/TEACHING_NAMES_ARABIC_DRAFT_01_QURANIC_UNIT.md"
DRAFT_TECHNICAL = ROOT / ".github/drafts/TEACHING_NAMES_ARABIC_DRAFT_02_TECHNICAL_UNIT.md"

CLAIM_IDS = [f"C{i:02d}" for i in range(1, 15)]
SOURCE_IDS = [f"R{i:02d}" for i in range(1, 7)] + [f"A{i:02d}" for i in range(1, 23)]
ALLOWED_CONFIDENCE = {"high", "medium", "open"}
ALLOWED_TYPES = {
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


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"cannot read {path.relative_to(ROOT)}: {exc}")


def load(path: Path) -> dict:
    try:
        return json.loads(read(path))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")


def words(text: str) -> int:
    return len(re.findall(r"[\w\u0600-\u06FF]+", text, flags=re.UNICODE))


def require_tokens(path: Path, tokens: tuple[str, ...], label: str) -> str:
    text = read(path)
    missing = [token for token in tokens if token not in text]
    if missing:
        fail(f"{label} lost required elements: {missing}")
    return text


def require_https(url: str, context: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        fail(f"{context}: expected an absolute HTTPS URL, found {url!r}")


def validate_files() -> None:
    files = (
        STANDARD,
        ARCHITECTURE,
        PLANNING,
        VERIFIED,
        TAFSIR,
        TECHNICAL,
        AUDIT,
        DRAFT_QURANIC,
        DRAFT_TECHNICAL,
    )
    for path in files:
        if not path.is_file():
            fail(f"required file missing: {path.relative_to(ROOT)}")
        floor = 900 if path.suffix == ".json" else 1_000
        if path.stat().st_size < floor:
            fail(f"required file is suspiciously small: {path.relative_to(ROOT)}")


def validate_governing_documents() -> None:
    require_tokens(
        STANDARD,
        (
            "بوابات رفض لا يعوضها مجموع النقاط",
            "سلامة المجال الديني",
            "سلامة المجال العلمي",
            "استقلال الدليل",
            "قابلية الفحص",
            "85–100: ركيزة مرجعية",
            "أقوى ثلاثة اعتراضات",
            "نسخة إنجليزية تحريرية كاملة",
            "لا تُبنى حلقة استشهاد ذاتي",
        ),
        "reference-grade standard",
    )
    architecture = require_tokens(
        ARCHITECTURE,
        (
            "مصفوفة الاسم–العالم–المسؤولية",
            "الوحدة الحجاجية هي البقرة 30–33",
            "الوعي ليس «الطبقة السابعة»",
            "بروتوكول الاختبار الخصومي",
            "أقوى الاعتراضات",
            "لا تُجعل «الأسماء» مرادفة آليًا لـtokens",
            "منشأً موضوعيًا للحجة",
            "نتيجة 85/100 فأكثر",
        ),
        "Teaching the Names architecture",
    )
    headings = set(re.findall(r"^### (C\d{2})\b", architecture, flags=re.MULTILINE))
    if headings != set(CLAIM_IDS):
        fail(f"architecture claim headings mismatch: {sorted(headings)}")
    if len(re.findall(r"^\| [1-6]\. ", architecture, flags=re.MULTILINE)) != 6:
        fail("architecture must contain exactly six matrix layers")


def validate_retired_planning_register() -> None:
    data = load(PLANNING)
    if data.get("schema_version") != "0.3-superseded":
        fail("retired planning-register schema mismatch")
    if data.get("status") != "superseded_by_verified_claim_register":
        fail("old planning register is not quarantined")
    if data.get("publication_state") != "article_not_yet_rewritten_or_published":
        fail("old planning register falsely implies publication")

    pillar = data.get("pillar", {})
    if pillar.get("external_review") != "not_completed":
        fail("old planning register falsely implies external review")
    if pillar.get("thematic_origin", {}).get("relationship") != "question_origin_only_not_empirical_evidence":
        fail("old planning register promotes the manuscript to evidence")

    expected_paths = {
        "primary_tafsir_verification": ".github/TEACHING_NAMES_TAFSIR_VERIFICATION_2026-09-03.md",
        "primary_technical_verification": ".github/TEACHING_NAMES_TECHNICAL_VERIFICATION_2026-09-03.md",
        "verified_claim_evidence_register": ".github/teaching_names_ai_verified_claims.json",
        "quranic_unit_draft": ".github/drafts/TEACHING_NAMES_ARABIC_DRAFT_01_QURANIC_UNIT.md",
        "technical_unit_draft": ".github/drafts/TEACHING_NAMES_ARABIC_DRAFT_02_TECHNICAL_UNIT.md",
    }
    actual_paths = data.get("authoritative_research_files", {})
    for key, expected in expected_paths.items():
        if actual_paths.get(key) != expected:
            fail(f"retired register points {key} to the wrong file")

    corrections = " ".join(
        f"{item.get('issue', '')} {item.get('correction', '')}"
        for item in data.get("supersession_reasons", [])
        if isinstance(item, dict)
    )
    for token in ("al-Raghib", "Abu Hayyan", "A15", "Hewitt and Liang", "reciprocal"):
        if token not in corrections:
            fail(f"retired register lost correction record: {token}")


def validate_verification_records() -> None:
    tafsir = require_tokens(
        TAFSIR,
        (
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
        ),
        "primary-tafsir verification record",
    )
    # These are measured completeness guards; word count is not a quality score.
    if words(tafsir) < 1_500:
        fail("primary-tafsir verification record is below the 1,500-word floor")

    technical = require_tokens(
        TECHNICAL,
        (
            "PRIMARY_TECHNICAL_EVIDENCE_VERIFIED_PREPUBLICATION",
            "Othello-GPT",
            "20 مليون",
            "0.01%",
            "0.12",
            "Hewitt & Liang",
            "الانتقائية",
            "التجريد السببي",
            "75%",
            "60 إلى 89",
            "25 نقطة",
            "PaLM-E",
            "الوعي ليس نتيجة لازمة",
            "المراجعة الخارجية من اختصاصي تعلم آلة",
        ),
        "primary technical verification record",
    )
    if words(technical) < 2_000:
        fail("primary technical verification record is below the 2,000-word floor")


def validate_verified_claim_graph() -> None:
    data = load(VERIFIED)
    if data.get("schema_version") != "1.0-prepublication":
        fail("verified-register schema mismatch")
    if data.get("status") != "verified_claim_evidence_manifest_article_draft_pending":
        fail("verified-register status mismatch")
    if data.get("publication_state") != "not_public_not_merged":
        fail("verified register falsely claims publication")

    pillar = data.get("pillar", {})
    if pillar.get("framework_ar") != "مصفوفة الاسم–العالم–المسؤولية":
        fail("Arabic framework name mismatch")
    if pillar.get("framework_en") != "The Name–World–Responsibility Matrix":
        fail("English framework name mismatch")
    if pillar.get("thematic_origin", {}).get("evidentiary_role") != "question_origin_only":
        fail("manuscript is not restricted to question-origin status")
    if pillar.get("external_review") != "not_completed":
        fail("verified register falsely claims external review")

    claims = data.get("claims")
    sources = data.get("sources")
    if not isinstance(claims, list) or not isinstance(sources, list):
        fail("claims and sources must be arrays")
    if [claim.get("id") for claim in claims] != CLAIM_IDS:
        fail("claim IDs/order must be C01–C14")
    if [source.get("id") for source in sources] != SOURCE_IDS:
        fail("source IDs/order must be R01–R06 then A01–A22")

    claim_map = {claim["id"]: claim for claim in claims}
    source_map = {source["id"]: source for source in sources}
    if len(claim_map) != 14 or len(source_map) != 28:
        fail("duplicate claim or source IDs detected")

    for claim in claims:
        cid = claim["id"]
        required = (
            "domain",
            "type",
            "confidence",
            "claim_ar",
            "claim_en",
            "supports",
            "qualifies",
            "limit_ar",
            "limit_en",
        )
        missing = [key for key in required if key not in claim or claim[key] in (None, "")]
        if missing:
            fail(f"{cid}: missing fields {missing}")
        if claim["type"] not in ALLOWED_TYPES:
            fail(f"{cid}: invalid type {claim['type']!r}")
        if claim["confidence"] not in ALLOWED_CONFIDENCE:
            fail(f"{cid}: invalid confidence {claim['confidence']!r}")
        if claim["type"] in {"contested_synthesis", "author_synthesis"} and claim["confidence"] != "open":
            fail(f"{cid}: synthesis must remain open")
        if not isinstance(claim["supports"], list) or not claim["supports"]:
            fail(f"{cid}: support list must be non-empty")
        if not isinstance(claim["qualifies"], list):
            fail(f"{cid}: qualification list must be an array")
        unknown = sorted((set(claim["supports"]) | set(claim["qualifies"])) - set(source_map))
        if unknown:
            fail(f"{cid}: unknown sources {unknown}")
        if len(claim["claim_ar"].split()) < 8 or len(claim["claim_en"].split()) < 8:
            fail(f"{cid}: bilingual claim is too short")
        if len(claim["limit_ar"].split()) < 5 or len(claim["limit_en"].split()) < 5:
            fail(f"{cid}: bilingual limitation is too short")
        for sid in claim["supports"]:
            if cid not in source_map[sid].get("supports_claims", []):
                fail(f"reciprocity failure: {cid} cites {sid} as support")
        for sid in claim["qualifies"]:
            if cid not in source_map[sid].get("qualifies_claims", []):
                fail(f"reciprocity failure: {cid} cites {sid} as qualification")

    for source in sources:
        sid = source["id"]
        required = (
            "domain",
            "type",
            "title",
            "url",
            "verification_status",
            "supports_claims",
            "qualifies_claims",
        )
        missing = [key for key in required if key not in source or source[key] in (None, "")]
        if missing:
            fail(f"{sid}: missing fields {missing}")
        require_https(source["url"], sid)
        if not isinstance(source["supports_claims"], list) or not isinstance(source["qualifies_claims"], list):
            fail(f"{sid}: reciprocal claim lists must be arrays")
        unknown = sorted((set(source["supports_claims"]) | set(source["qualifies_claims"])) - set(claim_map))
        if unknown:
            fail(f"{sid}: unknown claims {unknown}")
        for cid in source["supports_claims"]:
            if sid not in claim_map[cid]["supports"]:
                fail(f"reciprocity failure: {sid} supports {cid}")
        for cid in source["qualifies_claims"]:
            if sid not in claim_map[cid]["qualifies"]:
                fail(f"reciprocity failure: {sid} qualifies {cid}")

    for rid in SOURCE_IDS[:6]:
        if source_map[rid]["verification_status"] != "primary_text_verified":
            fail(f"{rid}: Qur'an/tafsir source is not primary-text verified")
    if "Abu Hayyan" not in source_map["R06"]["title"] or "albahr-almuheet" not in source_map["R06"]["url"]:
        fail("R06 must remain the verified Abu Hayyan source")
    if "Hewitt and Liang" not in source_map["A15"]["title"] or source_map["A15"]["url"] != "https://aclanthology.org/D19-1275/":
        fail("A15 must remain the primary control-task probing paper")
    if source_map["A22"]["verification_status"] != "frontier_excluded_from_central_conclusion":
        fail("A22 frontier result must remain outside the central conclusion")

    excluded = data.get("excluded_pending_verification", [])
    if not any("Raghib" in item.get("source", "") for item in excluded if isinstance(item, dict)):
        fail("the unverified al-Raghib attribution is not explicitly excluded")


def validate_drafts() -> None:
    quranic = require_tokens(
        DRAFT_QURANIC,
        (
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
        ),
        "internal Qur'anic-unit draft",
    )
    if words(quranic) < 1_900:
        fail("Qur'anic-unit draft is below the 1,900-word floor")

    technical = require_tokens(
        DRAFT_TECHNICAL,
        (
            "مسودة داخلية غير منشورة",
            "Othello-GPT",
            "قابلية الفك",
            "الدور السببي",
            "Hewitt",
            "75%",
            "Qwen",
            "PaLM-E",
            "مصفوفة الاسم–العالم–المسؤولية",
            "الوعي الظاهراتي",
            "لم تتم مراجعة مستقلة",
        ),
        "internal technical-unit draft",
    )
    if words(technical) < 3_500:
        fail("technical-unit draft is below the 3,500-word floor")

    if "filecite" in quranic or "filecite" in technical:
        fail("ChatGPT-only citation syntax leaked into repository drafts")


def main() -> None:
    validate_files()
    validate_governing_documents()
    validate_retired_planning_register()
    validate_verification_records()
    validate_verified_claim_graph()
    validate_drafts()
    print(
        "Reference-grade research base passed: old planning is quarantined; primary "
        "tafsir and technical verification are present; 14 bilingual claims and 28 "
        "sources are reciprocal; Abu Hayyan and Hewitt–Liang corrections are locked; "
        "frontier evidence is contained; and both Arabic units remain unpublished."
    )


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
