#!/usr/bin/env python3
"""Validate the public research discovery graph.

This gate prevents four high-impact failures:
1. future-dated Atom or JSON Feed entries;
2. drift between the machine research index and public feeds;
3. research pages disappearing from the public hub or sitemap;
4. one-way linking between a study and its related forthcoming book.
"""
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://ahmed-alhafiz.github.io"
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
}
BOOKS = {
    "sirou-fi-alard": ROOT / "books/sirou-fi-alard/index.html",
    "umm-abbas": ROOT / "books/umm-abbas/index.html",
}


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
        fail(f"{context}: timestamp lacks a timezone: {value!r}")
    return moment.astimezone(timezone.utc)


def local_path(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme and parsed.netloc != "ahmed-alhafiz.github.io":
        fail(f"Research URL is outside the canonical site: {url}")
    path = parsed.path
    if not path.startswith("/") or not path.endswith("/"):
        fail(f"Canonical research URL must use a leading and trailing slash: {url}")
    return path


def html_path(url: str) -> Path:
    return ROOT / local_path(url).lstrip("/") / "index.html"


def validate_index() -> tuple[dict[str, dict], dict[str, dict]]:
    path = ROOT / "articles/research-index.json"
    data = load_json(path)
    items = data.get("items")
    if not isinstance(items, list) or not items:
        fail("articles/research-index.json: items must be a non-empty list")

    by_url: dict[str, dict] = {}
    by_slug: dict[str, dict] = {}
    for item in items:
        if not isinstance(item, dict):
            fail("articles/research-index.json: every item must be an object")
        missing = [key for key in ("slug", "title", "summary", "type", "version", "languages", "review", "book", "url") if not item.get(key)]
        if missing:
            fail(f"research item {item.get('slug', '<unknown>')}: missing {', '.join(missing)}")
        slug = item["slug"]
        url = item["url"]
        if slug in by_slug:
            fail(f"articles/research-index.json: duplicate slug {slug}")
        if url in by_url:
            fail(f"articles/research-index.json: duplicate URL {url}")
        if item["book"] not in BOOKS:
            fail(f"{slug}: unknown related book {item['book']}")
        if "ar" not in item["languages"]:
            fail(f"{slug}: Arabic research index item must declare ar")
        page = html_path(url)
        if not page.is_file():
            fail(f"{slug}: public page does not exist at {page.relative_to(ROOT)}")
        if "en" in item["languages"]:
            if not item.get("english_title"):
                fail(f"{slug}: English title missing from research index")
            english = item.get("english_url")
            if not english:
                fail(f"{slug}: English declared but english_url is missing")
            if not html_path(english).is_file():
                fail(f"{slug}: English page does not exist at {html_path(english).relative_to(ROOT)}")
        by_slug[slug] = item
        by_url[url] = item

    missing_slugs = REQUIRED_ARABIC_SLUGS - set(by_slug)
    if missing_slugs:
        fail(f"articles/research-index.json: required research surfaces missing: {sorted(missing_slugs)}")

    generated = data.get("generated")
    if generated:
        try:
            generated_date = datetime.fromisoformat(generated).date()
        except ValueError as exc:
            fail(f"articles/research-index.json: invalid generated date: {exc}")
        if generated_date > datetime.now(timezone.utc).date() + timedelta(days=1):
            fail(f"articles/research-index.json: future generated date {generated}")

    return by_url, by_slug


def validate_atom(path: Path, expected: dict[str, dict]) -> None:
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as exc:
        fail(f"{path.relative_to(ROOT)}: invalid Atom XML: {exc}")

    feed_updated_text = root.findtext("a:updated", namespaces=ATOM_NS)
    if not feed_updated_text:
        fail(f"{path.relative_to(ROOT)}: missing feed updated timestamp")
    feed_updated = parse_time(feed_updated_text, f"{path.relative_to(ROOT)} feed updated")

    entries: dict[str, dict[str, str]] = {}
    latest_entry = datetime.min.replace(tzinfo=timezone.utc)
    for entry in root.findall("a:entry", ATOM_NS):
        link = entry.find("a:link", ATOM_NS)
        url = link.get("href") if link is not None else None
        title = entry.findtext("a:title", namespaces=ATOM_NS)
        published_text = entry.findtext("a:published", namespaces=ATOM_NS)
        updated_text = entry.findtext("a:updated", namespaces=ATOM_NS)
        if not all((url, title, published_text, updated_text)):
            fail(f"{path.relative_to(ROOT)}: an entry lacks URL, title, published or updated")
        if url in entries:
            fail(f"{path.relative_to(ROOT)}: duplicate entry {url}")
        published = parse_time(published_text, f"{path.relative_to(ROOT)} {url} published")
        updated = parse_time(updated_text, f"{path.relative_to(ROOT)} {url} updated")
        if updated < published:
            fail(f"{path.relative_to(ROOT)}: {url} updated precedes publication")
        latest_entry = max(latest_entry, published, updated)
        entries[url] = {"title": title}

    if set(entries) != set(expected):
        fail(
            f"{path.relative_to(ROOT)}: URL drift; "
            f"missing={sorted(set(expected) - set(entries))}, extra={sorted(set(entries) - set(expected))}"
        )
    for url, item in expected.items():
        if entries[url]["title"] != item["title"]:
            fail(f"{path.relative_to(ROOT)}: title drift for {url}")

    now_limit = datetime.now(timezone.utc) + FUTURE_TOLERANCE
    if latest_entry > now_limit or feed_updated > now_limit:
        fail(f"{path.relative_to(ROOT)}: future timestamp detected")
    if feed_updated < latest_entry:
        fail(f"{path.relative_to(ROOT)}: feed updated precedes its newest entry")


def validate_json_feed(path: Path, expected: dict[str, dict]) -> None:
    data = load_json(path)
    items = data.get("items")
    if not isinstance(items, list):
        fail(f"{path.relative_to(ROOT)}: items must be a list")
    entries: dict[str, dict] = {}
    now_limit = datetime.now(timezone.utc) + FUTURE_TOLERANCE
    for item in items:
        url = item.get("url")
        if not url:
            fail(f"{path.relative_to(ROOT)}: feed item lacks URL")
        if url in entries:
            fail(f"{path.relative_to(ROOT)}: duplicate item {url}")
        published = parse_time(item.get("date_published", ""), f"{path.relative_to(ROOT)} {url} date_published")
        modified = parse_time(item.get("date_modified", ""), f"{path.relative_to(ROOT)} {url} date_modified")
        if modified < published:
            fail(f"{path.relative_to(ROOT)}: {url} modified precedes publication")
        if max(published, modified) > now_limit:
            fail(f"{path.relative_to(ROOT)}: future timestamp for {url}")
        entries[url] = item

    if set(entries) != set(expected):
        fail(
            f"{path.relative_to(ROOT)}: URL drift; "
            f"missing={sorted(set(expected) - set(entries))}, extra={sorted(set(entries) - set(expected))}"
        )
    for url, indexed in expected.items():
        feed_item = entries[url]
        if feed_item.get("title") != indexed["title"]:
            fail(f"{path.relative_to(ROOT)}: title drift for {url}")
        tags = set(feed_item.get("tags", []))
        if indexed["review"] not in tags or indexed["book"] not in tags:
            fail(f"{path.relative_to(ROOT)}: {url} lacks review/book discovery tags")


def validate_hub_sitemap_and_books(indexed: dict[str, dict]) -> None:
    hub = (ROOT / "articles/index.html").read_text(encoding="utf-8")
    sitemap_root = ET.parse(ROOT / "sitemap.xml").getroot()
    sitemap_urls = {node.text for node in sitemap_root.findall("s:url/s:loc", SITEMAP_NS) if node.text}

    for url, item in indexed.items():
        path = local_path(url)
        if path not in hub:
            fail(f"articles/index.html: missing research surface {path}")
        if url not in sitemap_urls:
            fail(f"sitemap.xml: missing research URL {url}")

        book_path = BOOKS[item["book"]]
        book_html = book_path.read_text(encoding="utf-8")
        book_url = "/" + str(book_path.relative_to(ROOT)).removesuffix("index.html")
        study_html = html_path(url).read_text(encoding="utf-8")
        if path not in book_html:
            fail(f"{book_path.relative_to(ROOT)}: missing link to {path}")
        if book_url not in study_html:
            fail(f"{html_path(url).relative_to(ROOT)}: missing return link to {book_url}")

        english_url = item.get("english_url")
        if english_url and english_url not in sitemap_urls:
            fail(f"sitemap.xml: missing English research URL {english_url}")


def main() -> None:
    indexed_ar, _ = validate_index()
    indexed_en = {
        item["english_url"]: {
            **item,
            "title": item["english_title"],
        }
        for item in indexed_ar.values()
        if item.get("english_url")
    }
    validate_atom(ROOT / "articles/feed.xml", indexed_ar)
    validate_json_feed(ROOT / "articles/feed.json", indexed_ar)
    validate_atom(ROOT / "en/articles/feed.xml", indexed_en)
    validate_json_feed(ROOT / "en/articles/feed.json", indexed_en)
    validate_hub_sitemap_and_books(indexed_ar)
    print(
        "Discovery integrity passed: "
        f"{len(indexed_ar)} Arabic research surfaces, "
        f"{len(indexed_en)} complete English editions, "
        "chronology, feeds, hub, sitemap and reciprocal book links."
    )


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
