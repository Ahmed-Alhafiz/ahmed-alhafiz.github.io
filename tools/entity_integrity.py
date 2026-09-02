#!/usr/bin/env python3
"""Validate the canonical Ahmed Alhafiz author entity across the site.

This gate prevents identity drift, duplicate spelling pages, inconsistent
Person nodes, unsupported external profiles, and machine-only identity claims
that are not visible on the author pages.
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
AUTHOR_ID = "https://ahmed-alhafiz.github.io/#person"
AUTHOR_URL = "https://ahmed-alhafiz.github.io/about/"
AUTHOR_NAME = "أحمد الحافظ"
ALIASES = ["Ahmed Alhafiz", "Ahmad Alhafiz"]
EMAIL = "mailto:hhafz9924@gmail.com"
SAME_AS = [
    "https://medium.com/@AhmedAlhafiz",
    "https://www.instagram.com/ahmed_666_8",
]
MANIFEST_URL = "https://ahmed-alhafiz.github.io/author.json"
IDENTIFIER = {
    "@type": "PropertyValue",
    "propertyID": "canonical-author-id",
    "value": AUTHOR_ID,
}
EXCLUDED_HTML = {"404.html", "google904951439b331720.html"}
SCRIPT_RE = re.compile(
    r"<script\b[^>]*\btype=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)
CANONICAL_RE = re.compile(
    r'<link\b[^>]*\brel=["\']canonical["\'][^>]*\bhref=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
AUTHOR_LINK_RE = re.compile(
    r'<link\b[^>]*\brel=["\']author["\'][^>]*\bhref=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
MANIFEST_LINK_RE = re.compile(
    r'<link\b(?=[^>]*\brel=["\']alternate["\'])(?=[^>]*\btype=["\']application/ld\+json["\'])(?=[^>]*\bhref=["\']/author\.json["\'])[^>]*>',
    re.IGNORECASE,
)


class VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.suppressed = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "svg"}:
            self.suppressed += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "svg"} and self.suppressed:
            self.suppressed -= 1

    def handle_data(self, data: str) -> None:
        if not self.suppressed:
            self.parts.append(data)

    @property
    def text(self) -> str:
        return " ".join(" ".join(self.parts).split())


def iter_nodes(value: object):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from iter_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_nodes(child)


def node_has_type(node: dict, expected: str) -> bool:
    node_type = node.get("@type")
    if isinstance(node_type, str):
        return node_type == expected
    return isinstance(node_type, list) and expected in node_type


def public_html() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.html")
        if ".git" not in path.parts and path.name not in EXCLUDED_HTML
    )


def expected_author_href(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("en/"):
        return "/en/about/"
    if rel.startswith("de/"):
        return "/de/about/"
    return "/about/"


def validate_person(node: dict, context: str, errors: list[str]) -> None:
    if node.get("@id") != AUTHOR_ID:
        errors.append(f"{context}: Person @id drifted: {node.get('@id')!r}")
    if node.get("name") != AUTHOR_NAME:
        errors.append(f"{context}: primary Arabic name drifted: {node.get('name')!r}")
    if node.get("alternateName") != ALIASES:
        errors.append(f"{context}: alternate names must be exactly {ALIASES!r}")
    if node.get("url") != AUTHOR_URL:
        errors.append(f"{context}: canonical author URL drifted: {node.get('url')!r}")
    if node.get("identifier") != IDENTIFIER:
        errors.append(f"{context}: canonical PropertyValue identifier missing or inconsistent")
    if node.get("email") != EMAIL:
        errors.append(f"{context}: official public email missing or inconsistent")
    if node.get("sameAs") != SAME_AS:
        errors.append(f"{context}: sameAs must contain only the two verified public profiles")
    image = node.get("image")
    if not isinstance(image, dict):
        errors.append(f"{context}: ImageObject missing")
    else:
        expected_image = "https://ahmed-alhafiz.github.io/ahmed-alhafiz-author.png"
        if image.get("@type") != "ImageObject" or image.get("url") != expected_image:
            errors.append(f"{context}: canonical author image drifted")
        if image.get("width") != 1229 or image.get("height") != 1536:
            errors.append(f"{context}: canonical image dimensions must remain 1229×1536")


def validate_manifest(errors: list[str]) -> None:
    path = ROOT / "author.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"author.json: invalid or missing: {exc}")
        return
    if data.get("@context") != "https://schema.org":
        errors.append("author.json: schema.org context missing")
    graph = data.get("@graph")
    if not isinstance(graph, list):
        errors.append("author.json: @graph missing")
        return
    persons = [node for node in graph if isinstance(node, dict) and node_has_type(node, "Person")]
    if len(persons) != 1:
        errors.append(f"author.json: expected one Person, found {len(persons)}")
    else:
        validate_person(persons[0], "author.json", errors)
        profiles = persons[0].get("mainEntityOfPage")
        expected_profiles = [
            "https://ahmed-alhafiz.github.io/about/",
            "https://ahmed-alhafiz.github.io/en/about/",
            "https://ahmed-alhafiz.github.io/de/about/",
        ]
        if profiles != expected_profiles:
            errors.append("author.json: three language-specific profile URLs missing")
        if persons[0].get("publishingPrinciples") != "https://ahmed-alhafiz.github.io/methodology/":
            errors.append("author.json: publishingPrinciples must point to the public method page")

    profiles = [node for node in graph if isinstance(node, dict) and node_has_type(node, "ProfilePage")]
    if len(profiles) != 3:
        errors.append(f"author.json: expected three ProfilePage nodes, found {len(profiles)}")
    else:
        languages = sorted(node.get("inLanguage") for node in profiles)
        if languages != ["ar", "de", "en"]:
            errors.append(f"author.json: profile languages drifted: {languages}")
        for node in profiles:
            if node.get("mainEntity") != {"@id": AUTHOR_ID}:
                errors.append(f"author.json: ProfilePage {node.get('@id')} does not reference canonical Person")

    books = [node for node in graph if isinstance(node, dict) and node_has_type(node, "Book")]
    if len(books) != 4:
        errors.append(f"author.json: expected four forthcoming books, found {len(books)}")
    for book in books:
        if book.get("creativeWorkStatus") != "Forthcoming; not yet officially published":
            errors.append(f"author.json: {book.get('name')} lost forthcoming status")
        if book.get("author") != {"@id": AUTHOR_ID}:
            errors.append(f"author.json: {book.get('name')} does not reference the canonical author")

    articles = [node for node in graph if isinstance(node, dict) and node_has_type(node, "Article")]
    if len(articles) < 4:
        errors.append(f"author.json: expected at least four reference dossiers, found {len(articles)}")
    for article in articles:
        if article.get("author") != {"@id": AUTHOR_ID}:
            errors.append(f"author.json: article {article.get('url')} does not reference canonical author")


def validate_html(errors: list[str]) -> None:
    person_count = 0
    page_count = 0
    for path in public_html():
        rel = path.relative_to(ROOT).as_posix()
        html = path.read_text(encoding="utf-8")
        page_count += 1

        author_links = AUTHOR_LINK_RE.findall(html)
        expected = expected_author_href(path)
        if author_links != [expected]:
            errors.append(f"{rel}: expected one rel=author link to {expected}, found {author_links}")
        if len(MANIFEST_LINK_RE.findall(html)) != 1:
            errors.append(f"{rel}: expected one linked /author.json manifest")

        canonical_match = CANONICAL_RE.search(html)
        if not canonical_match:
            errors.append(f"{rel}: canonical link missing")
        else:
            parsed = urlparse(canonical_match.group(1))
            if parsed.hostname != "ahmed-alhafiz.github.io":
                errors.append(f"{rel}: canonical host drifted: {canonical_match.group(1)}")

        for index, block in enumerate(SCRIPT_RE.findall(html), start=1):
            try:
                data = json.loads(block)
            except json.JSONDecodeError as exc:
                errors.append(f"{rel}: JSON-LD block {index} invalid: {exc}")
                continue
            for node in iter_nodes(data):
                if isinstance(node, dict) and node_has_type(node, "Person"):
                    person_count += 1
                    validate_person(node, f"{rel} JSON-LD block {index}", errors)

    if page_count < 40:
        errors.append(f"Public-page inventory unexpectedly small: {page_count}")
    if person_count < 20:
        errors.append(f"Too few canonical Person nodes were validated: {person_count}")


def validate_visible_profiles(errors: list[str]) -> None:
    expectations = {
        "about/index.html": [
            "مرجع الهوية الرسمي",
            "الاسم العربي الرسمي",
            "الاسم اللاتيني المعتمد",
            "تهجئة بحث بديلة",
            "https://ahmed-alhafiz.github.io/#person",
            "ملف الهوية الآلي",
        ],
        "en/about/index.html": [
            "Canonical author identity",
            "Official Arabic name",
            "Preferred Latin name",
            "Search transliteration",
            "https://ahmed-alhafiz.github.io/#person",
            "Machine-readable identity",
        ],
        "de/about/index.html": [
            "Kanonische Autorenidentität",
            "Offizieller arabischer Name",
            "Bevorzugter lateinischer Name",
            "Alternative Suchschreibweise",
            "https://ahmed-alhafiz.github.io/#person",
            "Maschinenlesbare Identität",
        ],
    }
    for rel, tokens in expectations.items():
        path = ROOT / rel
        html = path.read_text(encoding="utf-8")
        parser = VisibleText()
        parser.feed(html)
        text = parser.text
        if html.count('id="identity"') != 1:
            errors.append(f"{rel}: visible identity section missing or duplicated")
        for token in tokens:
            if token not in text and token not in html:
                errors.append(f"{rel}: visible identity token missing: {token}")
        if html.count('href="/author.json"') < 1:
            errors.append(f"{rel}: visible author-manifest link missing")


def validate_no_doorways(errors: list[str]) -> None:
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    aliases = ("/ahmed-alhafiz/", "/ahmad-alhafiz/", "/أحمد-الحافظ/")
    for alias in aliases:
        if alias in sitemap:
            errors.append(f"sitemap.xml: doorway-style author alias URL found: {alias}")
    for path in public_html():
        rel = "/" + path.relative_to(ROOT).as_posix().replace("index.html", "")
        lowered = rel.lower()
        if lowered.startswith(("/ahmed-alhafiz/", "/ahmad-alhafiz/")):
            errors.append(f"Doorway-style author alias page found: {rel}")


def validate_strategy_data(errors: list[str]) -> None:
    for rel in ("data/visibility-baseline.json", "data/content-inventory.json"):
        try:
            json.loads((ROOT / rel).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{rel}: invalid JSON: {exc}")
    inventory = json.loads((ROOT / "data/content-inventory.json").read_text(encoding="utf-8"))
    items = inventory.get("items", [])
    if len(items) != 9:
        errors.append(f"content inventory: expected nine indexed research/guide items, found {len(items)}")
    counts: dict[str, int] = {}
    for item in items:
        counts[item.get("class", "missing")] = counts.get(item.get("class", "missing"), 0) + 1
    if counts != inventory.get("current_counts"):
        errors.append(f"content inventory counts drifted: computed {counts}, declared {inventory.get('current_counts')}")
    if counts.get("pillar") != 3 or counts.get("pillar_candidate") != 1:
        errors.append(f"content strategy must retain exactly three current pillars and one candidate: {counts}")


def main() -> None:
    errors: list[str] = []
    validate_manifest(errors)
    validate_html(errors)
    validate_visible_profiles(errors)
    validate_no_doorways(errors)
    validate_strategy_data(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Entity integrity failed with {len(errors)} error(s)")
        raise SystemExit(1)
    print(
        "Entity integrity passed: canonical Arabic name, two Latin aliases, one author ID, "
        "two verified public profiles, one machine-readable manifest, three visible profile editions, "
        "four forthcoming books, four reference dossiers, and no alias doorway pages."
    )


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
