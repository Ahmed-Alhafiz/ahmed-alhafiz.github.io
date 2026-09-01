#!/usr/bin/env python3
"""Repository-level integrity audit for ahmed-alhafiz.github.io.

Uses only Python's standard library so it can run in GitHub Actions without
installing dependencies. It validates discoverability, visible metadata,
JSON-LD syntax, internal navigation, sitemap/feed coverage, and a small set of
project-specific editorial safety rules for unpublished books.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

BASE_URL = "https://ahmed-alhafiz.github.io"
EXCLUDED_HTML = {"404.html"}
DRAFT_PUBLICATION_MARKERS = (
    "isbn",
    "ردمك",
    "دار غراب",
    "دار هاوس",
    "house 101",
    "house101",
    "9789948639251",
)


@dataclass
class PageData:
    path: Path
    title: str = ""
    description: str = ""
    robots: str = ""
    canonical: str = ""
    h1_count: int = 0
    html_lang: str = ""
    html_dir: str = ""
    hrefs: list[str] = field(default_factory=list)
    jsonld_raw: list[str] = field(default_factory=list)
    jsonld: list[object] = field(default_factory=list)
    img_without_alt: int = 0
    img_without_dimensions: int = 0
    blank_links_without_rel: int = 0
    text: str = ""


class AuditHTMLParser(HTMLParser):
    def __init__(self, path: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.page = PageData(path=path)
        self._in_title = False
        self._in_jsonld = False
        self._json_buffer: list[str] = []
        self._text_buffer: list[str] = []

    @staticmethod
    def _attrs(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {k.lower(): (v or "") for k, v in attrs}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        a = self._attrs(attrs)
        if tag == "html":
            self.page.html_lang = a.get("lang", "")
            self.page.html_dir = a.get("dir", "")
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            name = a.get("name", "").lower()
            if name == "description":
                self.page.description = a.get("content", "").strip()
            elif name == "robots":
                self.page.robots = a.get("content", "").strip().lower()
        elif tag == "link":
            rel = {part.lower() for part in a.get("rel", "").split()}
            if "canonical" in rel:
                self.page.canonical = a.get("href", "").strip()
        elif tag == "h1":
            self.page.h1_count += 1
        elif tag == "a":
            href = a.get("href", "").strip()
            if href:
                self.page.hrefs.append(href)
            if a.get("target", "").lower() == "_blank":
                rel = {part.lower() for part in a.get("rel", "").split()}
                if "noopener" not in rel:
                    self.page.blank_links_without_rel += 1
        elif tag == "img":
            if not a.get("alt", "").strip():
                self.page.img_without_alt += 1
            if not a.get("width", "").strip() or not a.get("height", "").strip():
                self.page.img_without_dimensions += 1
        elif tag == "script" and a.get("type", "").lower() == "application/ld+json":
            self._in_jsonld = True
            self._json_buffer = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._in_jsonld:
            self._in_jsonld = False
            raw = "".join(self._json_buffer).strip()
            if raw:
                self.page.jsonld_raw.append(raw)
            self._json_buffer = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.page.title += data
        if self._in_jsonld:
            self._json_buffer.append(data)
        else:
            stripped = data.strip()
            if stripped:
                self._text_buffer.append(stripped)

    def close(self) -> None:
        super().close()
        self.page.title = re.sub(r"\s+", " ", self.page.title).strip()
        self.page.text = " ".join(self._text_buffer)


def expected_url(root: Path, path: Path) -> str | None:
    rel = path.relative_to(root).as_posix()
    if rel in EXCLUDED_HTML or path.name.startswith("google"):
        return None
    if rel == "index.html":
        return BASE_URL + "/"
    if path.name == "index.html":
        return BASE_URL + "/" + path.parent.relative_to(root).as_posix().strip("/") + "/"
    return BASE_URL + "/" + rel


def target_for_href(root: Path, page_path: Path, href: str) -> Path | None:
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or href.startswith(("mailto:", "tel:", "javascript:", "data:")):
        return None
    raw_path = unquote(parsed.path)
    if not raw_path:
        return None
    if raw_path.startswith("/"):
        rel = raw_path.lstrip("/")
        target = root / rel
    else:
        target = page_path.parent / raw_path
    if raw_path.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target.resolve()


def iter_json_nodes(obj: object):
    if isinstance(obj, dict):
        yield obj
        graph = obj.get("@graph")
        if isinstance(graph, list):
            for item in graph:
                yield from iter_json_nodes(item)
    elif isinstance(obj, list):
        for item in obj:
            yield from iter_json_nodes(item)


def json_has_type(objects: list[object], wanted: str) -> bool:
    for obj in objects:
        for node in iter_json_nodes(obj):
            value = node.get("@type")
            if value == wanted or (isinstance(value, list) and wanted in value):
                return True
    return False


def article_nodes(objects: list[object]) -> list[dict]:
    result: list[dict] = []
    for obj in objects:
        for node in iter_json_nodes(obj):
            value = node.get("@type")
            if value == "Article" or (isinstance(value, list) and "Article" in value):
                result.append(node)
    return result


def parse_page(path: Path) -> PageData:
    parser = AuditHTMLParser(path)
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    for raw in parser.page.jsonld_raw:
        parser.page.jsonld.append(json.loads(raw))
    return parser.page


def local_path_from_site_url(root: Path, url: str) -> Path | None:
    parsed = urlsplit(url)
    if f"{parsed.scheme}://{parsed.netloc}" != BASE_URL:
        return None
    rel = unquote(parsed.path).lstrip("/")
    if not rel:
        return root / "index.html"
    target = root / rel
    if parsed.path.endswith("/"):
        target = target / "index.html"
    return target


def add_problem(problems: list[str], path: Path, message: str) -> None:
    problems.append(f"{path.as_posix()}: {message}")


def audit(root: Path, partial: bool = False) -> tuple[list[str], list[str], dict[str, int]]:
    errors: list[str] = []
    warnings: list[str] = []
    pages: dict[Path, PageData] = {}
    canonicals: dict[str, Path] = {}
    titles: dict[str, list[Path]] = {}

    html_paths = sorted(
        p for p in root.rglob("*.html")
        if ".git" not in p.parts and p.relative_to(root).as_posix() not in EXCLUDED_HTML and not p.name.startswith("google")
    )

    for path in html_paths:
        try:
            page = parse_page(path)
        except (UnicodeDecodeError, json.JSONDecodeError, Exception) as exc:
            add_problem(errors, path.relative_to(root), f"تعذر تحليل HTML/JSON-LD: {exc}")
            continue
        pages[path.resolve()] = page
        rel = path.relative_to(root)
        expected = expected_url(root, path)

        if not page.html_lang:
            add_problem(errors, rel, "وسم html يفتقد lang")
        if page.html_lang == "ar" and page.html_dir != "rtl":
            add_problem(errors, rel, "الصفحة العربية لا تحمل dir=rtl")
        if not page.title:
            add_problem(errors, rel, "عنوان <title> مفقود")
        elif not (20 <= len(page.title) <= 90):
            add_problem(warnings, rel, f"طول العنوان غير مثالي ({len(page.title)} حرفًا)")
        if not page.description:
            add_problem(errors, rel, "meta description مفقود")
        elif not (70 <= len(page.description) <= 180):
            add_problem(warnings, rel, f"طول الوصف غير مثالي ({len(page.description)} حرفًا)")
        if "index" not in page.robots:
            add_problem(errors, rel, "robots meta لا يسمح بالفهرسة صراحة")
        if page.h1_count != 1:
            add_problem(errors, rel, f"عدد H1 يجب أن يكون 1، الموجود {page.h1_count}")
        if not page.canonical:
            add_problem(errors, rel, "canonical مفقود")
        elif expected and page.canonical != expected:
            add_problem(errors, rel, f"canonical لا يطابق المسار المتوقع: {page.canonical} != {expected}")
        if page.canonical:
            previous = canonicals.get(page.canonical)
            if previous and previous != path:
                add_problem(errors, rel, f"canonical مكرر مع {previous.relative_to(root)}")
            canonicals[page.canonical] = path
        if not page.jsonld:
            add_problem(errors, rel, "JSON-LD مفقود")
        if page.img_without_alt:
            add_problem(errors, rel, f"صور بلا alt: {page.img_without_alt}")
        if page.img_without_dimensions:
            add_problem(warnings, rel, f"صور بلا width/height: {page.img_without_dimensions}")
        if page.blank_links_without_rel:
            add_problem(errors, rel, f"روابط target=_blank بلا noopener: {page.blank_links_without_rel}")

        lower_source = path.read_text(encoding="utf-8").lower()
        for marker in DRAFT_PUBLICATION_MARKERS:
            if marker in lower_source:
                add_problem(errors, rel, f"بيانات نشر غير معتمدة ظهرت في HTML العام: {marker}")

        if page.title:
            titles.setdefault(page.title, []).append(path)

        rel_posix = rel.as_posix()
        if rel_posix.startswith("articles/") and rel_posix != "articles/index.html":
            nodes = article_nodes(page.jsonld)
            if not nodes:
                add_problem(errors, rel, "صفحة المقال لا تحمل Article JSON-LD")
            else:
                article = nodes[0]
                for prop in ("headline", "datePublished", "dateModified", "author", "image"):
                    if not article.get(prop):
                        add_problem(errors, rel, f"Article JSON-LD يفتقد {prop}")
                author = article.get("author")
                if not isinstance(author, dict) or "أحمد الحافظ" not in str(author.get("name", "")):
                    add_problem(errors, rel, "بيانات مؤلف المقال غير مكتملة")
                citations = article.get("citation")
                if not isinstance(citations, list) or len(citations) < 5:
                    add_problem(errors, rel, "المقال المرجعي يحتاج خمسة مراجع آلية على الأقل")
            for required in ('href="/about/"', 'href="/methodology/"', 'class="references"', 'class="citation-box"', 'class="related-work"'):
                if required not in lower_source:
                    add_problem(errors, rel, f"صفحة المقال تفتقد عنصر الثقة: {required}")

    # Duplicate exact titles are suspicious, but language variants may legitimately differ.
    for title, paths in titles.items():
        if len(paths) > 1:
            joined = ", ".join(p.relative_to(root).as_posix() for p in paths)
            warnings.append(f"عنوان HTML مكرر: {title!r} في {joined}")

    # Internal link resolution.
    for page_path, page in pages.items():
        for href in page.hrefs:
            target = target_for_href(root, page_path, href)
            if target is None:
                continue
            if not target.exists():
                rel = page_path.relative_to(root)
                message = f"رابط داخلي مكسور: {href} -> {target}"
                add_problem(warnings if partial else errors, rel, message)

    sitemap_urls: set[str] = set()
    sitemap = root / "sitemap.xml"
    if sitemap.exists():
        try:
            tree = ET.parse(sitemap)
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            for loc in tree.findall("sm:url/sm:loc", ns):
                if loc.text:
                    sitemap_urls.add(loc.text.strip())
        except ET.ParseError as exc:
            errors.append(f"sitemap.xml: XML غير صالح: {exc}")
    elif not partial:
        errors.append("sitemap.xml مفقود")

    if sitemap_urls:
        for page_path, page in pages.items():
            if page.canonical and page.canonical not in sitemap_urls:
                add_problem(errors, page_path.relative_to(root), "canonical غير موجود في sitemap.xml")
        for url in sorted(sitemap_urls):
            target = local_path_from_site_url(root, url)
            if target is not None and not target.exists():
                bucket = warnings if partial else errors
                bucket.append(f"sitemap.xml: رابط بلا ملف محلي: {url} -> {target.relative_to(root)}")

    robots = root / "robots.txt"
    if robots.exists():
        robots_text = robots.read_text(encoding="utf-8")
        for token in ("OAI-SearchBot", "GPTBot", "Sitemap: https://ahmed-alhafiz.github.io/sitemap.xml"):
            if token not in robots_text:
                errors.append(f"robots.txt يفتقد: {token}")
    elif not partial:
        errors.append("robots.txt مفقود")

    feed = root / "articles" / "feed.xml"
    if feed.exists():
        try:
            tree = ET.parse(feed)
            ns = {"a": "http://www.w3.org/2005/Atom"}
            entries = tree.findall("a:entry", ns)
            if not entries:
                errors.append("articles/feed.xml: لا توجد entries")
            for entry in entries:
                link = entry.find("a:link", ns)
                href = link.attrib.get("href", "") if link is not None else ""
                if not href:
                    errors.append("articles/feed.xml: entry بلا رابط")
                elif sitemap_urls and href not in sitemap_urls:
                    errors.append(f"articles/feed.xml: رابط entry غير موجود في sitemap: {href}")
        except ET.ParseError as exc:
            errors.append(f"articles/feed.xml: XML غير صالح: {exc}")
    elif not partial:
        errors.append("articles/feed.xml مفقود")

    stats = {
        "html_pages": len(pages),
        "canonicals": len(canonicals),
        "sitemap_urls": len(sitemap_urls),
        "errors": len(errors),
        "warnings": len(warnings),
    }
    return errors, warnings, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the author website repository.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--partial", action="store_true", help="Allow unresolved links outside a partial build tree")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors, warnings, stats = audit(root, partial=args.partial)

    print("=== Site Integrity Audit ===")
    for key, value in stats.items():
        print(f"{key}: {value}")
    if warnings:
        print("\nWARNINGS")
        for item in warnings:
            print(f"- {item}")
    if errors:
        print("\nERRORS")
        for item in errors:
            print(f"- {item}")
        return 1
    print("\nPASS: no blocking integrity errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
