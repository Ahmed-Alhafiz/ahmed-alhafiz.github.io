#!/usr/bin/env python3
"""Validate the bilingual fear-before-diagnosis dossier and evidence package.

This gate protects the contribution that makes dossier 11 more than a long
article: bilingual substantive editions, fourteen classified claims, nineteen
sources, explicit original-synthesis boundaries, reciprocal book links,
portable citations, accessible diagrams, social cards, and medical-safety
language. It also prevents the forthcoming novel from being misrepresented as
evidence.
"""
from __future__ import annotations

import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "diagnostic-uncertainty-family-fear-coercive-authority"
AR_URL = f"https://ahmed-alhafiz.github.io/articles/{SLUG}/"
EN_URL = f"https://ahmed-alhafiz.github.io/en/articles/{SLUG}/"
BOOK_AR = "/books/umm-abbas/"
BOOK_EN = "/en/books/umm-abbas/"
REVIEW = "author_review_complete_specialist_review_pending"

AR_PAGE = ROOT / f"articles/{SLUG}/index.html"
EN_PAGE = ROOT / f"en/articles/{SLUG}/index.html"
AR_EVIDENCE = ROOT / f"articles/{SLUG}/evidence/index.html"
EN_EVIDENCE = ROOT / f"en/articles/{SLUG}/evidence/index.html"
CLAIMS = ROOT / f"articles/{SLUG}/evidence/claims.json"

REQUIRED_FILES = (
    AR_PAGE,
    EN_PAGE,
    AR_EVIDENCE,
    EN_EVIDENCE,
    CLAIMS,
    ROOT / f"articles/{SLUG}/evidence/references.bib",
    ROOT / f"articles/{SLUG}/evidence/references.ris",
    ROOT / f"articles/{SLUG}/citation.bib",
    ROOT / f"articles/{SLUG}/citation.ris",
    ROOT / f"articles/{SLUG}/CITATION.cff",
    ROOT / "assets/figures/fear-certainty-authority-cascade-ar.svg",
    ROOT / "assets/figures/fear-certainty-authority-cascade-en.svg",
    ROOT / "assets/figures/parallel-path-safeguard-ar.svg",
    ROOT / "assets/figures/parallel-path-safeguard-en.svg",
    ROOT / "assets/social/diagnostic-uncertainty-family-fear-ar.png",
    ROOT / "assets/social/diagnostic-uncertainty-family-fear-en.png",
)

SCRIPT_RE = re.compile(
    r"<script\b[^>]*\btype=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)
REF_ID_RE = re.compile(r'id=["\']ref-(\d+)["\']', re.IGNORECASE)


class TextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    @property
    def text(self) -> str:
        return " ".join(" ".join(self.parts).split())


def fail(message: str) -> None:
    raise SystemExit(message)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")


def html_text(path: Path) -> tuple[str, str]:
    html = path.read_text(encoding="utf-8")
    parser = TextParser()
    parser.feed(html)
    return html, parser.text


def walk_json(value: object):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def validate_files() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.is_file()]
    if missing:
        fail(f"Dossier 11 required files missing: {missing}")
    empty = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if path.stat().st_size < 80]
    if empty:
        fail(f"Dossier 11 files suspiciously small: {empty}")


def validate_claims() -> dict:
    data = load_json(CLAIMS)
    dossier = data.get("dossier", {})
    if dossier.get("slug") != SLUG or dossier.get("version") != "1.0":
        fail("claims.json: dossier slug/version mismatch")
    if dossier.get("review_status") != REVIEW:
        fail("claims.json: review status mismatch")
    origin = dossier.get("thematic_origin", {})
    if origin.get("evidentiary_status") != "theme_only_not_evidence":
        fail("claims.json: forthcoming novel must be explicitly theme-only, not evidence")

    claims = data.get("claims")
    sources = data.get("sources")
    if not isinstance(claims, list) or len(claims) != 14:
        fail(f"claims.json: expected 14 claims, found {len(claims) if isinstance(claims, list) else 'invalid'}")
    if not isinstance(sources, list) or len(sources) != 19:
        fail(f"claims.json: expected 19 sources, found {len(sources) if isinstance(sources, list) else 'invalid'}")

    expected_claim_ids = [f"C{i:02d}" for i in range(1, 15)]
    actual_claim_ids = [claim.get("id") for claim in claims]
    if actual_claim_ids != expected_claim_ids:
        fail(f"claims.json: claim IDs/order mismatch: {actual_claim_ids}")

    expected_source_ids = [f"S{i:02d}" for i in range(1, 20)]
    actual_source_ids = [source.get("id") for source in sources]
    if actual_source_ids != expected_source_ids:
        fail(f"claims.json: source IDs/order mismatch: {actual_source_ids}")
    source_map = {source["id"]: source for source in sources}

    allowed_types = {"documented", "contextual_association", "author_synthesis"}
    allowed_confidence = {"high", "medium", "open"}
    for claim in claims:
        cid = claim["id"]
        missing = [key for key in ("claim_ar", "claim_en", "type", "confidence", "evidence", "caveat_ar", "caveat_en") if not claim.get(key)]
        if missing:
            fail(f"claims.json {cid}: missing {missing}")
        if claim["type"] not in allowed_types:
            fail(f"claims.json {cid}: invalid type {claim['type']}")
        if claim["confidence"] not in allowed_confidence:
            fail(f"claims.json {cid}: invalid confidence {claim['confidence']}")
        if claim["type"] == "author_synthesis" and claim["confidence"] != "open":
            fail(f"claims.json {cid}: author synthesis must remain open")
        if claim["type"] == "documented" and claim["confidence"] == "open":
            fail(f"claims.json {cid}: documented claim cannot be labelled open")
        evidence = claim["evidence"]
        if not isinstance(evidence, list) or not evidence:
            fail(f"claims.json {cid}: evidence list missing")
        unknown = sorted(set(evidence) - set(source_map))
        if unknown:
            fail(f"claims.json {cid}: unknown source IDs {unknown}")
        for sid in evidence:
            supports = source_map[sid].get("supports", [])
            if cid not in supports:
                fail(f"claims.json: source {sid} does not reciprocally declare support for {cid}")

    for source in sources:
        sid = source["id"]
        if not source.get("title") or not source.get("url") or not source.get("type"):
            fail(f"claims.json {sid}: title/url/type missing")
        for cid in source.get("supports", []):
            if cid not in actual_claim_ids:
                fail(f"claims.json {sid}: unknown supported claim {cid}")
            claim = claims[expected_claim_ids.index(cid)]
            if sid not in claim["evidence"]:
                fail(f"claims.json: claim {cid} does not reciprocally cite {sid}")

    for cid in ("C12", "C13", "C14"):
        claim = claims[expected_claim_ids.index(cid)]
        if claim["type"] != "author_synthesis" or claim["confidence"] != "open":
            fail(f"claims.json {cid}: original framework/normative synthesis not explicitly open")

    return data


def validate_pages() -> None:
    pairs = (
        (AR_PAGE, "ar", BOOK_AR, "سلسلة الخوف–اليقين–السلطة", "مسار الأمان الموازي"),
        (EN_PAGE, "en", BOOK_EN, "Fear–Certainty–Authority Cascade", "Parallel-Path Safeguard"),
    )
    for path, language, book, framework1, framework2 in pairs:
        html, text = html_text(path)
        rel = path.relative_to(ROOT)
        if f'<html lang="{language}"' not in html:
            fail(f"{rel}: language declaration mismatch")
        if book not in html:
            fail(f"{rel}: reciprocal link to related book missing")
        if framework1 not in text or framework2 not in text:
            fail(f"{rel}: original frameworks missing from visible text")
        expected_badge = "مراجعة خارجية معلّقة" if language == "ar" else "External review pending"
        if expected_badge not in text:
            fail(f"{rel}: localized external review badge/disclosure missing")
        if len(set(REF_ID_RE.findall(html))) < 19:
            fail(f"{rel}: expected at least 19 annotated reference anchors")
        if "isBasedOn" in html:
            fail(f"{rel}: forthcoming book must not be encoded as evidence via isBasedOn")
        if "mentions" not in html:
            fail(f"{rel}: thematic book relationship must use mentions")
        if "claims.json" not in html or "/evidence/" not in html:
            fail(f"{rel}: evidence surfaces missing")
        if language == "ar":
            safety_tokens = ("الطوارئ", "لا توقف دواء", "ليست تشخيصًا")
            review_tokens = ("لم تتم بعد مراجعة مستقلة", "ليس مقياسًا سريريًا مُعتمدًا", "لا يُقدَّم بوصفه أداة تشخيصية")
        else:
            safety_tokens = ("emergency", "Do not stop prescribed medication", "not a diagnosis or individual medical advice")
            review_tokens = ("No independent", "not a validated", "must not be represented")
        if not all(token.lower() in text.lower() for token in safety_tokens):
            fail(f"{rel}: medical safety boundary incomplete")
        if not all(token.lower() in text.lower() for token in review_tokens):
            fail(f"{rel}: synthesis/review limitations incomplete")

        scripts = SCRIPT_RE.findall(html)
        if not scripts:
            fail(f"{rel}: JSON-LD missing")
        parsed = [json.loads(block) for block in scripts]
        article_nodes = [node for data in parsed for node in walk_json(data) if isinstance(node, dict) and node.get("@type") == "Article"]
        if len(article_nodes) != 1:
            fail(f"{rel}: expected exactly one Article JSON-LD node")
        article = article_nodes[0]
        if article.get("version") != "1.0" or article.get("inLanguage") != language:
            fail(f"{rel}: Article version/language mismatch")
        mentions = article.get("mentions", {})
        if not isinstance(mentions, dict) or mentions.get("creativeWorkStatus") != "Forthcoming; not yet officially published":
            fail(f"{rel}: forthcoming thematic origin not truthfully declared")

    for path, language in ((AR_EVIDENCE, "ar"), (EN_EVIDENCE, "en")):
        html, text = html_text(path)
        rel = path.relative_to(ROOT)
        if f'<html lang="{language}"' not in html:
            fail(f"{rel}: evidence language mismatch")
        for cid in ("C01", "C06", "C12", "C14"):
            if cid not in text:
                fail(f"{rel}: claim table missing {cid}")
        if "claims.json" not in html or "references.bib" not in html or "references.ris" not in html:
            fail(f"{rel}: machine/reference exports missing")
        if "14" not in text or "19" not in text:
            fail(f"{rel}: claim/source inventory disclosure missing")


def validate_figures() -> None:
    names = (
        "fear-certainty-authority-cascade-ar.svg",
        "fear-certainty-authority-cascade-en.svg",
        "parallel-path-safeguard-ar.svg",
        "parallel-path-safeguard-en.svg",
    )
    for name in names:
        path = ROOT / "assets/figures" / name
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            fail(f"{path.relative_to(ROOT)}: invalid SVG: {exc}")
        if root.get("width") != "1200" or root.get("height") != "760" or root.get("viewBox") != "0 0 1200 760":
            fail(f"{path.relative_to(ROOT)}: SVG dimensions/viewBox mismatch")
        namespace = {"s": "http://www.w3.org/2000/svg"}
        if root.find("s:title", namespace) is None or root.find("s:desc", namespace) is None:
            fail(f"{path.relative_to(ROOT)}: accessible title/description missing")


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        fail(f"{path.relative_to(ROOT)}: invalid PNG signature")
    return struct.unpack(">II", data[16:24])


def validate_social_cards() -> None:
    for language in ("ar", "en"):
        path = ROOT / f"assets/social/diagnostic-uncertainty-family-fear-{language}.png"
        if png_dimensions(path) != (1200, 630):
            fail(f"{path.relative_to(ROOT)}: social card must be 1200×630")
        if path.stat().st_size < 10_000:
            fail(f"{path.relative_to(ROOT)}: social card suspiciously small")
        html = (AR_PAGE if language == "ar" else EN_PAGE).read_text(encoding="utf-8")
        if f"/{path.relative_to(ROOT).as_posix()}" not in html:
            fail(f"{path.relative_to(ROOT)}: card not linked from matching article metadata")


def validate_citations() -> None:
    refs_bib = (ROOT / f"articles/{SLUG}/evidence/references.bib").read_text(encoding="utf-8")
    refs_ris = (ROOT / f"articles/{SLUG}/evidence/references.ris").read_text(encoding="utf-8")
    if refs_bib.count("@") != 19:
        fail(f"references.bib: expected 19 entries, found {refs_bib.count('@')}")
    if refs_ris.count("TY  -") != 19 or refs_ris.count("ER  -") != 19:
        fail("references.ris: expected 19 complete records")
    for doi in (
        "10.2147/JMDH.S311900",
        "10.1111/eip.12214",
        "10.12669/pjms.305.5434",
        "10.1186/1752-4458-9-8",
        "10.3390/ijerph17155615",
    ):
        if doi not in refs_bib or doi not in refs_ris:
            fail(f"Reference export missing DOI {doi}")
    cff = (ROOT / f"articles/{SLUG}/CITATION.cff").read_text(encoding="utf-8")
    for token in ('cff-version: 1.2.0', 'version: "1.0"', "date-released: 2026-09-02", AR_URL):
        if token not in cff:
            fail(f"CITATION.cff missing {token}")


def validate_integration() -> None:
    index = load_json(ROOT / "articles/research-index.json")
    matches = [item for item in index.get("items", []) if item.get("slug") == SLUG]
    if len(matches) != 1:
        fail(f"research-index.json: expected one {SLUG} item")
    item = matches[0]
    if item.get("url") != AR_URL or item.get("english_url") != EN_URL:
        fail("research-index.json: bilingual URLs mismatch")
    if item.get("languages") != ["ar", "en"] or item.get("review") != REVIEW or item.get("book") != "umm-abbas":
        fail("research-index.json: language/review/book metadata mismatch")

    for path, url in (
        (ROOT / "articles/feed.json", AR_URL),
        (ROOT / "en/articles/feed.json", EN_URL),
    ):
        feed = load_json(path)
        found = [entry for entry in feed.get("items", []) if entry.get("url") == url]
        if len(found) != 1:
            fail(f"{path.relative_to(ROOT)}: dossier entry missing or duplicated")
        if REVIEW not in found[0].get("tags", []) or "umm-abbas" not in found[0].get("tags", []):
            fail(f"{path.relative_to(ROOT)}: review/book tags missing")

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    for url in (AR_URL, f"{AR_URL}evidence/", EN_URL, f"{EN_URL}evidence/"):
        if sitemap.count(f"<loc>{url}</loc>") != 1:
            fail(f"sitemap.xml: URL missing or duplicated: {url}")

    for path, article_url in (
        (ROOT / "articles/index.html", f"/articles/{SLUG}/"),
        (ROOT / "en/articles/index.html", f"/en/articles/{SLUG}/"),
        (ROOT / "index.html", f"/articles/{SLUG}/"),
        (ROOT / "en/index.html", f"/en/articles/{SLUG}/"),
        (ROOT / "books/umm-abbas/index.html", f"/articles/{SLUG}/"),
        (ROOT / "en/books/umm-abbas/index.html", f"/en/articles/{SLUG}/"),
        (ROOT / "de/books/umm-abbas/index.html", f"/en/articles/{SLUG}/"),
        (ROOT / "research-status/index.html", f"/articles/{SLUG}/"),
        (ROOT / "en/research-status/index.html", f"/en/articles/{SLUG}/"),
    ):
        html = path.read_text(encoding="utf-8")
        if article_url not in html:
            fail(f"{path.relative_to(ROOT)}: dossier discovery link missing")


def main() -> None:
    validate_files()
    validate_claims()
    validate_pages()
    validate_figures()
    validate_social_cards()
    validate_citations()
    validate_integration()
    print(
        "Dossier 11 integrity passed: two substantive editions, two evidence pages, "
        "14 reciprocal claims, 19 sources, four accessible figures, two 1200×630 cards, "
        "portable citations, explicit safety/review boundaries, and full discovery integration."
    )


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
