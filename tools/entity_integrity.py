#!/usr/bin/env python3
"""Validate the canonical Ahmed Alhafiz author entity across the site.

This gate prevents identity drift, duplicate spelling pages, inconsistent
Person nodes, unsupported external profiles, machine-only identity claims,
and stale current-control records that contradict the published author/book state.
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
AUTHOR_ID = "https://ahmedalhafiz.com/#person"
AUTHOR_URL = "https://ahmedalhafiz.com/about/"
AUTHOR_NAME = "أحمد الحافظ — Ahmed Alhafiz"
ALIASES = ["أحمد الحافظ", "Ahmed Alhafiz", "Ahmad Alhafiz"]
EMAIL = "mailto:hhafz9924@gmail.com"
SAME_AS = [
    "https://medium.com/@AhmedAlhafiz",
    "https://www.instagram.com/ahmed_666_8",
]
MANIFEST_URL = "https://ahmedalhafiz.com/author.json"
IDENTIFIER = {
    "@type": "PropertyValue",
    "propertyID": "canonical-author-id",
    "value": AUTHOR_ID,
}
JUHAYMAN_ID = "https://ahmedalhafiz.com/books/juhayman/#book"
JUHAYMAN_TITLE = "جُهَيْمَان — خوارج بين الركن والمقام"
STALE_JUHAYMAN_TITLE = "جهيمان — القيامة بين الركن والمقام"
UMM_ABBAS_ID = "https://ahmedalhafiz.com/books/umm-abbas/#book"
UMM_ABBAS_GUIDE_IDS = {
    "ar": "https://ahmedalhafiz.com/articles/possession-or-neurological-psychological-disorder/#article",
    "en": "https://ahmedalhafiz.com/en/articles/possession-or-neurological-psychological-disorder/#article",
    "de": "https://ahmedalhafiz.com/de/articles/possession-or-neurological-psychological-disorder/#article",
}
NEW_COMPANIONS = {
    "fall-of-baghdad-1258-ibn-al-alqami": {
        "book": "https://ahmedalhafiz.com/books/kitab-al-kutub/#book",
        "ar": "https://ahmedalhafiz.com/articles/fall-of-baghdad-1258-ibn-al-alqami/#article",
        "en": "https://ahmedalhafiz.com/en/articles/fall-of-baghdad-1258-ibn-al-alqami/#article",
        "de": "https://ahmedalhafiz.com/de/articles/fall-von-bagdad-1258-ibn-al-alqami/#article",
    },
    "juhayman-grand-mosque-1979": {
        "book": JUHAYMAN_ID,
        "ar": "https://ahmedalhafiz.com/articles/juhayman-grand-mosque-1979/#article",
        "en": "https://ahmedalhafiz.com/en/articles/juhayman-grand-mosque-1979/#article",
        "de": "https://ahmedalhafiz.com/de/articles/dschuhaiman-grosse-moschee-1979/#article",
    },
    "how-certainty-becomes-violence": {
        "book": JUHAYMAN_ID,
        "ar": "https://ahmedalhafiz.com/articles/how-certainty-becomes-violence/#article",
        "en": "https://ahmedalhafiz.com/en/articles/how-certainty-becomes-violence/#article",
        "de": "https://ahmedalhafiz.com/de/articles/wie-gewissheit-zu-gewalt-wird/#article",
    },
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
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
DESCRIPTION_RE = re.compile(
    r'<meta\b[^>]*\bname=["\']description["\'][^>]*\bcontent=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")

HOME_REQUIREMENTS = {
    "index.html": {
        "title": "أحمد الحافظ — Ahmed Alhafiz | الموقع الرسمي",
        "description": "الموقع الرسمي للكاتب أحمد الحافظ — Ahmed Alhafiz: مؤلفاته قيد الإصدار، وأبحاثه ذات المصادر المعلنة في التاريخ والدين والعلم والنفس والمجتمع.",
        "links": ["/about/", "/books/", "/articles/"],
    },
    "en/index.html": {
        "title": "أحمد الحافظ — Ahmed Alhafiz | Official Author Website",
        "description": "The official website of writer Ahmed Alhafiz — أحمد الحافظ: forthcoming books and source-backed research in history, religion, science, psychology, and society.",
        "links": ["/en/about/", "/en/books/", "/en/articles/"],
    },
    "de/index.html": {
        "title": "أحمد الحافظ — Ahmed Alhafiz | Offizielle Autorenwebsite",
        "description": "Offizielle Website von Ahmed Alhafiz — أحمد الحافظ: kommende Bücher und Forschung mit Quellen zu Geschichte, Religion, Wissenschaft, Psyche und Gesellschaft.",
        "links": ["/de/about/", "/de/books/", "/de/articles/"],
    },
}


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
        expected_image = "https://ahmedalhafiz.com/ahmed-alhafiz-author.png"
        if image.get("@type") != "ImageObject" or image.get("url") != expected_image:
            errors.append(f"{context}: canonical author image drifted")
        if image.get("width") != 1229 or image.get("height") != 1536:
            errors.append(f"{context}: canonical image dimensions must remain 1229×1536")


def validate_website(node: dict, context: str, errors: list[str]) -> None:
    if node.get("@id") != "https://ahmedalhafiz.com/#website":
        errors.append(f"{context}: WebSite @id drifted: {node.get('@id')!r}")
    if node.get("name") != AUTHOR_NAME:
        errors.append(f"{context}: canonical bilingual WebSite name drifted: {node.get('name')!r}")
    if node.get("alternateName") != ALIASES:
        errors.append(f"{context}: WebSite alternate names must be exactly {ALIASES!r}")
    if node.get("publisher") != {"@id": AUTHOR_ID}:
        errors.append(f"{context}: WebSite publisher must reference the canonical Person")


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
    websites = [node for node in graph if isinstance(node, dict) and node_has_type(node, "WebSite")]
    if len(websites) != 1:
        errors.append(f"author.json: expected one WebSite, found {len(websites)}")
    else:
        validate_website(websites[0], "author.json", errors)
    persons = [node for node in graph if isinstance(node, dict) and node_has_type(node, "Person")]
    if len(persons) != 1:
        errors.append(f"author.json: expected one Person, found {len(persons)}")
    else:
        validate_person(persons[0], "author.json", errors)
        profiles = persons[0].get("mainEntityOfPage")
        expected_profiles = [
            "https://ahmedalhafiz.com/about/",
            "https://ahmedalhafiz.com/en/about/",
            "https://ahmedalhafiz.com/de/about/",
        ]
        if profiles != expected_profiles:
            errors.append("author.json: three language-specific profile URLs missing")
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
    juhayman = [book for book in books if book.get("@id") == JUHAYMAN_ID]
    if len(juhayman) != 1:
        errors.append(f"author.json: expected exactly one Juhayman Book node, found {len(juhayman)}")
    elif juhayman[0].get("name") != JUHAYMAN_TITLE:
        errors.append(f"author.json: canonical Juhayman title drifted: {juhayman[0].get('name')!r}")

    articles = [node for node in graph if isinstance(node, dict) and node_has_type(node, "Article")]
    if len(articles) < 4:
        errors.append(f"author.json: expected at least four reference dossiers, found {len(articles)}")
    for article in articles:
        if article.get("author") != {"@id": AUTHOR_ID}:
            errors.append(f"author.json: article {article.get('url')} does not reference canonical author")

    article_by_id = {article.get("@id"): article for article in articles}
    guide_by_language: dict[str, dict] = {}
    for language, article_id in UMM_ABBAS_GUIDE_IDS.items():
        article = article_by_id.get(article_id)
        if article is None:
            errors.append(f"author.json: missing {language} Umm Abbas companion guide node")
            continue
        guide_by_language[language] = article
        if article.get("inLanguage") != language:
            errors.append(f"author.json: {language} Umm Abbas guide language drifted")

    arabic_guide = guide_by_language.get("ar")
    if arabic_guide:
        if arabic_guide.get("about") != {"@id": UMM_ABBAS_ID}:
            errors.append("author.json: Arabic Umm Abbas guide must reference the book with about")
        expected_translations = [
            {"@id": UMM_ABBAS_GUIDE_IDS["en"]},
            {"@id": UMM_ABBAS_GUIDE_IDS["de"]},
        ]
        if arabic_guide.get("workTranslation") != expected_translations:
            errors.append("author.json: Arabic Umm Abbas guide must link the English and German translations")
    for language in ("en", "de"):
        article = guide_by_language.get(language)
        if article and article.get("translationOfWork") != {"@id": UMM_ABBAS_GUIDE_IDS["ar"]}:
            errors.append(f"author.json: {language} Umm Abbas guide must link back to the Arabic original")

    umm_abbas = [book for book in books if book.get("@id") == UMM_ABBAS_ID]
    if len(umm_abbas) != 1:
        errors.append(f"author.json: expected exactly one Umm Abbas Book node, found {len(umm_abbas)}")
    elif umm_abbas[0].get("subjectOf") != {"@id": UMM_ABBAS_GUIDE_IDS["ar"]}:
        errors.append("author.json: Umm Abbas book must link to its Arabic companion guide")

    for slug, expected in NEW_COMPANIONS.items():
        ar_article = article_by_id.get(expected["ar"])
        if ar_article is None:
            errors.append(f"author.json: missing Arabic companion article {slug}")
            continue
        if ar_article.get("about") != {"@id": expected["book"]}:
            errors.append(f"author.json: {slug} must reference its related book with about")
        translations = [{"@id": expected["en"]}, {"@id": expected["de"]}]
        if ar_article.get("workTranslation") != translations:
            errors.append(f"author.json: {slug} translation graph drifted")
        for language in ("en", "de"):
            translated = article_by_id.get(expected[language])
            if translated is None:
                errors.append(f"author.json: missing {language} companion article {slug}")
            elif translated.get("translationOfWork") != {"@id": expected["ar"]}:
                errors.append(f"author.json: {language} {slug} must link to the Arabic original")

    book_by_id = {book.get("@id"): book for book in books}
    expected_juhayman_subjects = [
        {"@id": NEW_COMPANIONS["juhayman-grand-mosque-1979"]["ar"]},
        {"@id": NEW_COMPANIONS["how-certainty-becomes-violence"]["ar"]},
    ]
    if book_by_id.get(JUHAYMAN_ID, {}).get("subjectOf") != expected_juhayman_subjects:
        errors.append("author.json: Juhayman book-to-research graph drifted")
    kitab_id = NEW_COMPANIONS["fall-of-baghdad-1258-ibn-al-alqami"]["book"]
    if book_by_id.get(kitab_id, {}).get("subjectOf") != {"@id": NEW_COMPANIONS["fall-of-baghdad-1258-ibn-al-alqami"]["ar"]}:
        errors.append("author.json: Kitab al-Kutub book-to-research graph drifted")


def validate_html(errors: list[str]) -> None:
    person_count = 0
    page_count = 0
    for path in public_html():
        rel = path.relative_to(ROOT).as_posix()
        html = path.read_text(encoding="utf-8")
        page_count += 1
        page_person_count = 0

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
            if parsed.hostname != "ahmedalhafiz.com":
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
                    page_person_count += 1
                    validate_person(node, f"{rel} JSON-LD block {index}", errors)
                if isinstance(node, dict) and node_has_type(node, "WebSite"):
                    validate_website(node, f"{rel} JSON-LD block {index}", errors)
                if isinstance(node, dict) and node_has_type(node, "Book"):
                    if rel.endswith("books/juhayman/index.html"):
                        expected_subjects = [
                            {"@id": NEW_COMPANIONS["juhayman-grand-mosque-1979"]["ar"]},
                            {"@id": NEW_COMPANIONS["how-certainty-becomes-violence"]["ar"]},
                        ]
                        if node.get("subjectOf") != expected_subjects:
                            errors.append(f"{rel}: Juhayman Book schema lost its companion research links")
                    if rel.endswith("books/kitab-al-kutub/index.html"):
                        expected_subject = {"@id": NEW_COMPANIONS["fall-of-baghdad-1258-ibn-al-alqami"]["ar"]}
                        if node.get("subjectOf") != expected_subject:
                            errors.append(f"{rel}: Kitab al-Kutub Book schema lost its companion research link")
        if page_person_count > 1:
            errors.append(f"{rel}: duplicate canonical Person nodes found: {page_person_count}")

    if page_count < 40:
        errors.append(f"Public-page inventory unexpectedly small: {page_count}")
    if person_count < 10:
        errors.append(f"Too few canonical Person nodes were validated: {person_count}")


def validate_homepages(errors: list[str]) -> None:
    for rel, expected in HOME_REQUIREMENTS.items():
        html = (ROOT / rel).read_text(encoding="utf-8")
        title_match = TITLE_RE.search(html)
        title = title_match.group(1).strip() if title_match else None
        if title != expected["title"]:
            errors.append(f"{rel}: homepage title drifted: {title!r}")
        description_match = DESCRIPTION_RE.search(html)
        description = description_match.group(1).strip() if description_match else None
        if description != expected["description"]:
            errors.append(f"{rel}: homepage description drifted: {description!r}")
        h1_match = H1_RE.search(html)
        h1 = " ".join(TAG_RE.sub("", h1_match.group(1)).split()) if h1_match else None
        if h1 != AUTHOR_NAME:
            errors.append(f"{rel}: H1 must be the canonical bilingual author name, found {h1!r}")
        for href in expected["links"]:
            if f'href="{href}"' not in html:
                errors.append(f"{rel}: required homepage journey link missing: {href}")


def validate_visible_profiles(errors: list[str]) -> None:
    expectations = {
        "about/index.html": [
            "الكاتب أحمد الحافظ",
            "بيانات الكاتب المعتمدة",
            "الاسم العربي الرسمي",
            "الاسم اللاتيني المعتمد",
            "تهجئة بحث بديلة",
            "https://ahmedalhafiz.com/#person",
            "بيانات الهوية المنظمة",
        ],
        "en/about/index.html": [
            "Official author identity",
            "Official Arabic name",
            "Preferred Latin name",
            "Search transliteration",
            "https://ahmedalhafiz.com/#person",
            "Author record",
        ],
        "de/about/index.html": [
            "Offizielle Autorenidentität",
            "Offizieller arabischer Name",
            "Bevorzugter lateinischer Name",
            "Alternative Suchschreibweise",
            "https://ahmedalhafiz.com/#person",
            "Autorendaten",
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


def validate_juhayman_title(errors: list[str]) -> None:
    public_surfaces = (
        "books/juhayman/index.html",
        "index.html",
        "about/index.html",
        "en/index.html",
        "en/about/index.html",
        "de/index.html",
        "de/about/index.html",
    )
    for rel in public_surfaces:
        text = (ROOT / rel).read_text(encoding="utf-8")
        # A focused Arabic homepage may link to the complete catalogue instead.
        requires_title = rel != "index.html" or "/books/juhayman/" in text
        if requires_title and JUHAYMAN_TITLE not in text:
            errors.append(f"{rel}: canonical Juhayman title missing")
        if STALE_JUHAYMAN_TITLE in text:
            errors.append(f"{rel}: stale Juhayman title returned")

    control_docs = (
        ".github/PROJECT_GOVERNING_DIRECTIVE.md",
        ".github/SEO_SOURCE_OF_TRUTH.md",
        ".github/CONTENT_CURRENT_CHECKPOINT.md",
    )
    for rel in control_docs:
        text = (ROOT / rel).read_text(encoding="utf-8")
        if JUHAYMAN_TITLE not in text:
            errors.append(f"{rel}: canonical Juhayman title missing from current control record")
        if STALE_JUHAYMAN_TITLE in text:
            errors.append(f"{rel}: stale Juhayman title contradicts current control state")


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
    if len(items) != 20:
        errors.append(f"content inventory: expected twenty indexed research/guide items, found {len(items)}")
    counts: dict[str, int] = {key: 0 for key in inventory.get("classes", {})}
    for item in items:
        item_class = item.get("class", "missing")
        counts[item_class] = counts.get(item_class, 0) + 1
    if counts != inventory.get("current_counts"):
        errors.append(f"content inventory counts drifted: computed {counts}, declared {inventory.get('current_counts')}")
    if counts.get("pillar") != 4 or counts.get("pillar_candidate") != 0:
        errors.append(f"content strategy must retain exactly four current pillars and zero candidates: {counts}")

    teaching = [item for item in items if item.get("slug") == "teaching-names-ai-understanding"]
    if len(teaching) != 1:
        errors.append(f"content inventory: expected one Teaching the Names record, found {len(teaching)}")
    else:
        item = teaching[0]
        if item.get("class") != "pillar" or sorted(item.get("languages", [])) != ["ar", "en"]:
            errors.append("content inventory: Teaching the Names must remain a complete Arabic/English pillar")


def validate_llms_manifest(errors: list[str]) -> None:
    path = ROOT / "llms.txt"
    text = path.read_text(encoding="utf-8")
    for token in ("أحمد الحافظ", "Ahmed Alhafiz", "Ahmad Alhafiz", AUTHOR_ID, MANIFEST_URL):
        if token not in text:
            errors.append(f"llms.txt: canonical identity token missing: {token}")
    if "Ahmed Al-Hafiz" in text:
        errors.append("llms.txt: unsupported Latin-name spelling returned")
    for book_path in ("sirou-fi-alard", "umm-abbas", "juhayman", "kitab-al-kutub"):
        if f"https://ahmedalhafiz.com/books/{book_path}/" not in text:
            errors.append(f"llms.txt: official book missing: {book_path}")
    for url in re.findall(r"https://ahmedalhafiz\.com/[^\s)]+", text):
        parsed = urlparse(url)
        local = parsed.path.lstrip("/")
        candidate = ROOT / local
        if not local:
            candidate = ROOT / "index.html"
        elif parsed.path.endswith("/"):
            candidate = candidate / "index.html"
        if not candidate.exists():
            errors.append(f"llms.txt: broken official URL: {url}")


def main() -> None:
    errors: list[str] = []
    validate_manifest(errors)
    validate_html(errors)
    validate_homepages(errors)
    validate_visible_profiles(errors)
    validate_juhayman_title(errors)
    validate_no_doorways(errors)
    validate_strategy_data(errors)
    validate_llms_manifest(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Entity integrity failed with {len(errors)} error(s)")
        raise SystemExit(1)
    print(
        "Entity integrity passed: canonical bilingual name, Arabic and Latin aliases, one author ID, "
        "two verified public profiles, one machine-readable manifest, three visible profile editions, "
        "four forthcoming books, four current reference pillars, four multilingual book-to-research graphs, "
        "canonical Juhayman title, and no alias doorway pages."
    )


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
