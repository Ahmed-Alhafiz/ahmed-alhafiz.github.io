#!/usr/bin/env python3
"""Validate permanent multilingual UX and public-identity invariants.

The structural and editorial audits protect content integrity. This gate protects
presentation decisions that materially affect trust and usability:

- one compact footer per public page;
- no duplicated language selector in the footer;
- no public GitHub profile presented as an author channel;
- exactly three official contact channels where contact details are shown;
- stable portrait markup on Arabic, English, and German home/profile pages;
- explicit one-column portrait-first stacking at tablet and mobile widths;
- one modern book layout across all three languages;
- correct page direction and accessible social links.
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {"404.html", "google904951439b331720.html"}
PUBLIC_GITHUB = "https://github.com/Ahmed-Alhafiz"

FOOTER_RE = re.compile(r"<footer\b[^>]*>.*?</footer>", re.IGNORECASE | re.DOTALL)
HTML_RE = re.compile(
    r"<html\b(?=[^>]*\blang=[\"']([^\"']+)[\"'])(?=[^>]*\bdir=[\"']([^\"']+)[\"'])[^>]*>",
    re.IGNORECASE,
)
SCRIPT_RE = re.compile(
    r"<script\b[^>]*\btype=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)
PORTRAIT_RE = re.compile(
    r'<div\b[^>]*class=["\'][^"\']*\b(?:hero-portrait|profile-portrait)\b[^"\']*["\'][^>]*>\s*'
    r'<img\b(?=[^>]*src=["\']/ahmed-alhafiz-author\.png["\'])(?=[^>]*width=["\']1229["\'])(?=[^>]*height=["\']1536["\'])[^>]*>',
    re.IGNORECASE | re.DOTALL,
)
CONTACT_CHANNEL_RE = re.compile(
    r'<a\b[^>]*class=["\'][^"\']*\bcontact-channel\b[^"\']*["\']',
    re.IGNORECASE,
)

HOME_PAGES = {
    "index.html": "ar",
    "en/index.html": "en",
    "de/index.html": "de",
}
PROFILE_PAGES = {
    "about/index.html": "ar",
    "en/about/index.html": "en",
    "de/about/index.html": "de",
}
BOOK_SLUGS = ("sirou-fi-alard", "umm-abbas", "juhayman", "kitab-al-kutub")
BOOK_PAGES = {
    f"{prefix}books/{slug}/index.html"
    for prefix in ("", "en/", "de/")
    for slug in BOOK_SLUGS
}
GLOBAL_LEGACY_TOKENS = (
    'class="identity-links"',
    "Languages and profiles",
    "اللغات والروابط",
)
BOOK_LEGACY_TOKENS = (
    'class="page-head"',
    'class="book-layout"',
    'href="/#links"',
    'href="/en/#links"',
    'href="/de/#links"',
    'href="/en/#books"',
)


class FooterParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_footer = False
        self.footer_depth = 0
        self.lang_blocks = 0
        self.social_links: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key: value or "" for key, value in attrs}
        classes = attributes.get("class", "").split()
        if tag.lower() == "footer" and not self.in_footer:
            self.in_footer = True
            self.footer_depth = 1
            return
        if not self.in_footer:
            return
        if tag.lower() == "footer":
            self.footer_depth += 1
        if "langs" in classes:
            self.lang_blocks += 1
        if tag.lower() == "a" and "social-icon" in classes:
            self.social_links.append(attributes)

    def handle_endtag(self, tag: str) -> None:
        if self.in_footer and tag.lower() == "footer":
            self.footer_depth -= 1
            if self.footer_depth == 0:
                self.in_footer = False


def public_pages() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.html")
        if ".git" not in path.parts and path.name not in EXCLUDED
    )


def inspect_json(value: object, errors: list[str], context: str) -> None:
    if isinstance(value, dict):
        same_as = value.get("sameAs")
        if isinstance(same_as, list):
            for url in same_as:
                if isinstance(url, str) and url.startswith(PUBLIC_GITHUB):
                    errors.append(f"{context}: GitHub remained in structured public identity")
        for child in value.values():
            inspect_json(child, errors, context)
    elif isinstance(value, list):
        for child in value:
            inspect_json(child, errors, context)


def validate_public_page(path: Path, errors: list[str]) -> None:
    rel = path.relative_to(ROOT).as_posix()
    html = path.read_text(encoding="utf-8")

    match = HTML_RE.search(html)
    if not match:
        errors.append(f"{rel}: html lang/dir declaration missing")
    else:
        language = match.group(1).lower().split("-")[0]
        direction = match.group(2).lower()
        expected = "rtl" if language == "ar" else "ltr"
        if direction != expected:
            errors.append(f"{rel}: dir={direction!r}, expected {expected!r} for {language}")

    footers = FOOTER_RE.findall(html)
    if len(footers) != 1:
        errors.append(f"{rel}: expected one footer, found {len(footers)}")
    if html.count('id="site-footer"') != 1:
        errors.append(f"{rel}: rebuilt footer ID missing or duplicated")

    parser = FooterParser()
    parser.feed(html)
    if parser.lang_blocks:
        errors.append(f"{rel}: footer contains a duplicate language selector")
    if len(parser.social_links) != 3:
        errors.append(f"{rel}: expected three compact footer social links, found {len(parser.social_links)}")
    else:
        hrefs = {item.get("href", "") for item in parser.social_links}
        required = {
            "https://medium.com/@AhmedAlhafiz",
            "https://www.instagram.com/ahmed_666_8",
            "mailto:hhafz9924@gmail.com",
        }
        if hrefs != required:
            errors.append(f"{rel}: footer contact channels drifted: {sorted(hrefs)}")
        for item in parser.social_links:
            if not item.get("aria-label"):
                errors.append(f"{rel}: a footer social link lacks an aria-label")

    if PUBLIC_GITHUB in html:
        errors.append(f"{rel}: public GitHub author link remained")
    for token in GLOBAL_LEGACY_TOKENS:
        if token in html:
            errors.append(f"{rel}: legacy or duplicated interface token remained: {token}")

    for index, block in enumerate(SCRIPT_RE.findall(html), start=1):
        try:
            data = json.loads(block)
        except json.JSONDecodeError as exc:
            errors.append(f"{rel}: JSON-LD block {index} is invalid: {exc}")
            continue
        inspect_json(data, errors, f"{rel} JSON-LD block {index}")


def validate_priority_pages(errors: list[str]) -> None:
    for rel, language in {**HOME_PAGES, **PROFILE_PAGES}.items():
        html = (ROOT / rel).read_text(encoding="utf-8")
        if not PORTRAIT_RE.search(html):
            errors.append(f"{rel}: stable 1229×1536 portrait markup missing")
        if language == "ar" and 'dir="rtl"' not in html:
            errors.append(f"{rel}: Arabic direction missing")
        if language != "ar" and 'dir="ltr"' not in html:
            errors.append(f"{rel}: LTR direction missing")

    for rel in PROFILE_PAGES:
        html = (ROOT / rel).read_text(encoding="utf-8")
        if html.count('id="contact"') != 1:
            errors.append(f"{rel}: compact contact section missing or duplicated")
        if len(CONTACT_CHANNEL_RE.findall(html)) != 3:
            errors.append(f"{rel}: expected exactly three visible contact channels")
        if "mailto:hhafz9924@gmail.com" not in html:
            errors.append(f"{rel}: official email contact missing")
        if '<small dir="ltr">' not in html:
            errors.append(f"{rel}: LTR-safe account handle markup missing")

    for rel in BOOK_PAGES:
        html = (ROOT / rel).read_text(encoding="utf-8")
        for token in (
            'class="site-header"',
            'class="site-footer"',
            'class="book-hero"',
            'class="book-hero-cover"',
            'class="publication-note"',
        ):
            if token not in html:
                errors.append(f"{rel}: modern multilingual book token missing: {token}")
        for token in BOOK_LEGACY_TOKENS:
            if token in html:
                errors.append(f"{rel}: legacy book-layout token remained: {token}")


def validate_css(errors: list[str]) -> None:
    css = (ROOT / "assets/site-v2.css").read_text(encoding="utf-8")
    required = (
        "Site UX Rebuild 10 — multilingual visual consistency",
        ".home-hero-grid,.profile-grid{grid-template-columns:",
        "aspect-ratio:4/5",
        "object-fit:cover",
        ".contact-channel",
        ".footer-shell",
        ".social-icon",
        "width:min(50vw,184px)",
        ".book-hero .pill",
        "UX10 final mobile footer alignment",
        "UX10 mobile stacking correction",
        "@media(max-width:960px){\n  .home-hero-grid,.profile-grid{\n    grid-template-columns:minmax(0,1fr);",
        "grid-column:1;\n    grid-row:auto;\n    order:-1;",
        "width:min(47vw,174px)",
    )
    for token in required:
        if token not in css:
            errors.append(f"assets/site-v2.css: required UX invariant missing: {token}")


def main() -> None:
    errors: list[str] = []
    pages = public_pages()
    for page in pages:
        validate_public_page(page, errors)
    validate_priority_pages(errors)
    validate_css(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"UX integrity failed with {len(errors)} error(s)")
        raise SystemExit(1)

    print(
        "UX integrity passed: "
        f"{len(pages)} public pages, one compact footer each, "
        "three official contact channels, no duplicate language footers, "
        "no public GitHub identity, stable tri-language portrait markup, "
        "mobile portrait-first single-column stacking, "
        "and one modern book layout across Arabic, English, and German."
    )


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
