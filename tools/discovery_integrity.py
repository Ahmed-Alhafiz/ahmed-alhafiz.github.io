#!/usr/bin/env python3
"""Validate the public research discovery graph.

The gate checks chronology, research-index/feed agreement, sitemap and hub
presence, reciprocal book links, bilingual hreflang/switch reciprocity, and
Article JSON-LD title/date consistency. SEO <title> text may intentionally be
shorter than the research headline, so the canonical headline is taken from
Article JSON-LD rather than requiring an exact document-title match.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
ATOM_NS = {"a": "http://www.w3.org/2005/Atom"}
SITEMAP_NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
FUTURE_TOLERANCE = timedelta(minutes=10)

REQUIRED_ARABIC_SLUGS = {
    "ratq-fatq-big-bang",
    "teaching-names-ai-understanding",
    "spiritual-healing-exploitation-safeguarding",
    "functional-seizures-vs-epilepsy",
    "six-days-creation-cosmic-time",
    "sleep-paralysis-jathoom",
    "arabic-psychological-horror",
    "water-civilization-power",
    "diagnostic-uncertainty-family-fear-coercive-authority",
}
BOOKS = {
    "sirou-fi-alard": ROOT / "books/sirou-fi-alard/index.html",
    "umm-abbas": ROOT / "books/umm-abbas/index.html",
}

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
HREFLANG_RE = re.compile(
    r'<link\b[^>]*\brel=["\']alternate["\'][^>]*\bhreflang=["\']([^"\']+)["\'][^>]*\bhref=["\']([^"\']+)["\'][^>]*>',
    re.I,
)
LANGS_RE = re.compile(
    r'<div\b[^>]*\bclass=["\'][^"\']*\blangs\b[^"\']*["\'][^>]*>(.*?)</div>',
    re.I | re.S,
)
ANCHOR_RE = re.compile(
    r'<a\b[^>]*\bhref=["\']([^"\']+)["\'][^>]*\bhreflang=["\']([^"\']+)["\'][^>]*>',
    re.I,
)


class JsonLdParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.active = False
        self.buffer: list[str] = []
        self.blocks: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs = dict(attrs)
        if tag.lower() == "script" and attrs.get("type", "").lower() == "application/ld+json":
            self.active = True
            self.buffer = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self.active:
            self.blocks.append("".join(self.buffer))
            self.active = False

    def handle_data(self, data: str) -> None:
        if self.active:
            self.buffer.append(data)


def fail(message: str) -> None:
    raise SystemExit(message)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")


def parse_time(value: str, context: str) -> datetime:
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        fail(f"{context}: invalid ISO-8601 timestamp {value!r}: {exc}")
    if moment.tzinfo is None:
        fail(f"{context}: timestamp lacks timezone: {value!r}")
    return moment.astimezone(timezone.utc)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def local_path(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme and parsed.netloc != "ahmed-alhafiz.github.io":
        fail(f"Research URL is outside canonical site: {url}")
    path = parsed.path if parsed.scheme else url.split("#", 1)[0].split("?", 1)[0]
    if not path.startswith("/"):
        path = "/" + path
    if not path.endswith("/"):
        fail(f"Canonical research URL must end with slash: {url}")
    return path


def html_path(url: str) -> Path:
    return ROOT / local_path(url).lstrip("/") / "index.html"


def article_node(html: str, rel: str) -> dict:
    parser = JsonLdParser()
    parser.feed(html)
    for raw in parser.blocks:
        if not raw.strip():
            continue
        data = json.loads(raw)
        candidates = [data] if isinstance(data, dict) else []
        if isinstance(data, dict) and isinstance(data.get("@graph"), list):
            candidates += data["@graph"]
        for node in candidates:
            if isinstance(node, dict) and node.get("@type") in {"Article", "ScholarlyArticle"}:
                return node
    fail(f"{rel}: Article JSON-LD node not found")


def page_metadata(url: str, expected_headline: str) -> dict:
    path = html_path(url)
    rel = str(path.relative_to(ROOT))
    html = path.read_text(encoding="utf-8")
    if not TITLE_RE.search(html):
        fail(f"{rel}: missing document title")
    node = article_node(html, rel)
    headline = normalize(str(node.get("headline", "")))
    if headline != normalize(expected_headline):
        fail(f"{rel}: Article headline drift; index={expected_headline!r}, page={headline!r}")
    if node.get("url") != url:
        fail(f"{rel}: Article URL drift; expected {url}, found {node.get('url')!r}")
    published = node.get("datePublished")
    modified = node.get("dateModified")
    if not isinstance(published, str) or not published:
        fail(f"{rel}: Article datePublished missing")
    if not isinstance(modified, str) or not modified:
        fail(f"{rel}: Article dateModified missing")
    return {"html": html, "published": published, "modified": modified}


def validate_bilingual_pair(item: dict) -> None:
    if "en" not in item["languages"]:
        return
    ar_url = item["url"]
    en_url = item["english_url"]
    expected_alt = {"ar": ar_url, "en": en_url, "x-default": en_url}
    expected_switch = {"ar": local_path(ar_url), "en": local_path(en_url)}

    for url in (ar_url, en_url):
        path = html_path(url)
        rel = str(path.relative_to(ROOT))
        html = path.read_text(encoding="utf-8")
        alternates = {lang.lower(): href for lang, href in HREFLANG_RE.findall(html)}
        for lang, target in expected_alt.items():
            if alternates.get(lang) != target:
                fail(
                    f"{rel}: reciprocal hreflang failure for {lang}; "
                    f"expected {target!r}, found {alternates.get(lang)!r}"
                )
        switch = LANGS_RE.search(html)
        if not switch:
            fail(f"{rel}: bilingual page lacks visible language switch")
        visible = {
            lang.lower(): local_path(href)
            for href, lang in ANCHOR_RE.findall(switch.group(1))
            if lang.lower() in {"ar", "en"}
        }
        for lang, target in expected_switch.items():
            if visible.get(lang) != target:
                fail(
                    f"{rel}: visible {lang} switch drift; "
                    f"expected {target!r}, found {visible.get(lang)!r}"
                )


def validate_index() -> tuple[dict[str, dict], dict[str, dict]]:
    data = load_json(ROOT / "articles/research-index.json")
    items = data.get("items")
    if not isinstance(items, list) or not items:
        fail("articles/research-index.json: items must be non-empty list")
    by_url: dict[str, dict] = {}
    by_slug: dict[str, dict] = {}
    for item in items:
        if not isinstance(item, dict):
            fail("articles/research-index.json: every item must be object")
        required = ("slug", "title", "summary", "type", "version", "languages", "review", "book", "url")
        missing = [key for key in required if not item.get(key)]
        if missing:
            fail(f"research item {item.get('slug','<unknown>')}: missing {', '.join(missing)}")
        slug, url = item["slug"], item["url"]
        if slug in by_slug or url in by_url:
            fail(f"articles/research-index.json: duplicate slug/url for {slug}")
        if item["book"] not in BOOKS:
            fail(f"{slug}: unknown related book {item['book']}")
        if "ar" not in item["languages"]:
            fail(f"{slug}: Arabic must be declared")
        if not html_path(url).is_file():
            fail(f"{slug}: Arabic page missing")
        page_metadata(url, item["title"])
        if "en" in item["languages"]:
            if not item.get("english_title") or not item.get("english_url"):
                fail(f"{slug}: English declared without title/url")
            if not html_path(item["english_url"]).is_file():
                fail(f"{slug}: English page missing")
            page_metadata(item["english_url"], item["english_title"])
            validate_bilingual_pair(item)
        by_slug[slug] = item
        by_url[url] = item

    missing = REQUIRED_ARABIC_SLUGS - set(by_slug)
    if missing:
        fail(f"articles/research-index.json: missing required surfaces {sorted(missing)}")
    return by_url, by_slug


def validate_atom(path: Path, expected: dict[str, dict]) -> None:
    root = ET.parse(path).getroot()
    feed_updated_text = root.findtext("a:updated", namespaces=ATOM_NS)
    if not feed_updated_text:
        fail(f"{path.relative_to(ROOT)}: missing feed updated")
    feed_updated = parse_time(feed_updated_text, f"{path.relative_to(ROOT)} updated")
    entries: dict[str, dict] = {}
    latest = datetime.min.replace(tzinfo=timezone.utc)
    for entry in root.findall("a:entry", ATOM_NS):
        link = entry.find("a:link", ATOM_NS)
        url = link.get("href") if link is not None else None
        title = entry.findtext("a:title", namespaces=ATOM_NS)
        pub = entry.findtext("a:published", namespaces=ATOM_NS)
        upd = entry.findtext("a:updated", namespaces=ATOM_NS)
        if not all((url, title, pub, upd)):
            fail(f"{path.relative_to(ROOT)}: incomplete entry")
        if url in entries:
            fail(f"{path.relative_to(ROOT)}: duplicate {url}")
        pub_dt = parse_time(pub, f"{path.relative_to(ROOT)} {url} published")
        upd_dt = parse_time(upd, f"{path.relative_to(ROOT)} {url} updated")
        if upd_dt < pub_dt:
            fail(f"{path.relative_to(ROOT)}: updated precedes publication for {url}")
        latest = max(latest, pub_dt, upd_dt)
        entries[url] = {"title": title, "published": pub}

    if set(entries) != set(expected):
        fail(f"{path.relative_to(ROOT)}: URL drift")
    for url, item in expected.items():
        if entries[url]["title"] != item["title"]:
            fail(f"{path.relative_to(ROOT)}: title drift for {url}")
        page = page_metadata(url, item["title"])
        feed_date = parse_time(entries[url]["published"], "feed date").date().isoformat()
        if feed_date != page["published"][:10]:
            fail(
                f"{path.relative_to(ROOT)}: publication-date drift for {url}; "
                f"feed={feed_date}, page={page['published'][:10]}"
            )

    now_limit = datetime.now(timezone.utc) + FUTURE_TOLERANCE
    if latest > now_limit or feed_updated > now_limit:
        fail(f"{path.relative_to(ROOT)}: future timestamp detected")
    if feed_updated < latest:
        fail(f"{path.relative_to(ROOT)}: feed updated precedes newest entry")


def validate_json_feed(path: Path, expected: dict[str, dict]) -> None:
    items = load_json(path).get("items")
    if not isinstance(items, list):
        fail(f"{path.relative_to(ROOT)}: items must be list")
    entries = {item.get("url"): item for item in items if isinstance(item, dict)}
    if None in entries or len(entries) != len(items):
        fail(f"{path.relative_to(ROOT)}: missing/duplicate URL")
    if set(entries) != set(expected):
        fail(f"{path.relative_to(ROOT)}: URL drift")
    now_limit = datetime.now(timezone.utc) + FUTURE_TOLERANCE
    for url, indexed in expected.items():
        item = entries[url]
        if item.get("title") != indexed["title"]:
            fail(f"{path.relative_to(ROOT)}: title drift for {url}")
        tags = set(item.get("tags", []))
        if indexed["review"] not in tags or indexed["book"] not in tags:
            fail(f"{path.relative_to(ROOT)}: review/book tags missing for {url}")
        pub = parse_time(item.get("date_published", ""), f"{path.relative_to(ROOT)} {url} published")
        mod = parse_time(item.get("date_modified", ""), f"{path.relative_to(ROOT)} {url} modified")
        if mod < pub or max(pub, mod) > now_limit:
            fail(f"{path.relative_to(ROOT)}: invalid chronology for {url}")
        page = page_metadata(url, indexed["title"])
        if pub.date().isoformat() != page["published"][:10]:
            fail(
                f"{path.relative_to(ROOT)}: publication-date drift for {url}; "
                f"feed={pub.date().isoformat()}, page={page['published'][:10]}"
            )


def validate_surfaces(indexed: dict[str, dict]) -> None:
    hub = (ROOT / "articles/index.html").read_text(encoding="utf-8")
    en_hub = (ROOT / "en/articles/index.html").read_text(encoding="utf-8")
    sitemap = ET.parse(ROOT / "sitemap.xml").getroot()
    urls = {node.text for node in sitemap.findall("s:url/s:loc", SITEMAP_NS) if node.text}
    for url, item in indexed.items():
        route = local_path(url)
        if route not in hub or url not in urls:
            fail(f"{item['slug']}: missing from Arabic hub or sitemap")
        book_path = BOOKS[item["book"]]
        book_html = book_path.read_text(encoding="utf-8")
        book_route = "/" + str(book_path.relative_to(ROOT)).removesuffix("index.html")
        study_html = html_path(url).read_text(encoding="utf-8")
        if route not in book_html or book_route not in study_html:
            fail(f"{item['slug']}: reciprocal book/study link missing")
        if item.get("english_url"):
            en_url = item["english_url"]
            en_route = local_path(en_url)
            if en_url not in urls or en_route not in en_hub:
                fail(f"{item['slug']}: English page missing from hub or sitemap")
            if item["english_title"] not in en_hub:
                fail(f"{item['slug']}: English hub title drift")


def main() -> None:
    indexed_ar, _ = validate_index()
    indexed_en = {
        item["english_url"]: {**item, "title": item["english_title"]}
        for item in indexed_ar.values()
        if item.get("english_url")
    }
    validate_atom(ROOT / "articles/feed.xml", indexed_ar)
    validate_json_feed(ROOT / "articles/feed.json", indexed_ar)
    validate_atom(ROOT / "en/articles/feed.xml", indexed_en)
    validate_json_feed(ROOT / "en/articles/feed.json", indexed_en)
    validate_surfaces(indexed_ar)
    print(
        "Discovery integrity passed: "
        f"{len(indexed_ar)} Arabic surfaces, {len(indexed_en)} English editions; "
        "feed chronology, JSON-LD headlines/dates, reciprocal hreflang/switches, "
        "hubs, sitemap and book links are consistent."
    )


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
