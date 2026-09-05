#!/usr/bin/env python3
"""Protect Arabic interface quality and the public research-hub structure.

The Arabic research hub may contain English titles only when they are part of a
proper name or explicit source metadata. Navigation and edition controls on the
Arabic surface must remain Arabic. This gate also cross-checks the machine-readable
research register instead of requiring one specific visual table layout.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / "articles/index.html"
REGISTER = ROOT / "articles/research-index.json"

BANNED_VISIBLE_INTERFACE = {
    "articles/index.html": (
        "Author research desk",
        "Flagship dossier",
        "Global bilingual dossier",
        "Extended dossiers in Arabic",
        "LANGUAGE & AI",
        "SAFEGUARDING",
        "REVIEW / STATUS",
        "Research tracks",
        "COSMOS",
        "MIND",
        "NARRATIVE",
        "Publication register",
        "Global edition policy",
        "العربية / English",
        "English edition",
        "English research desk",
    ),
    "research-status/index.html": (
        "Transparency register",
        "English edition",
    ),
    "articles/water-civilization-power/index.html": (
        ">English edition</a>",
    ),
}

# These phrases describe the current Arabic editorial surface. They are
# intentionally semantic rather than layout-specific so visual redesigns do
# not force the integrity gate to preserve an obsolete table or section order.
REQUIRED_ARABIC_HUB_TEXT = (
    "مركز أبحاث أحمد الحافظ",
    "تعليم الأسماء والذكاء الاصطناعي",
    "الرتق والفتق والانفجار العظيم",
    "الماء والحضارة والسلطة",
    "حين يحكم الخوف قبل التشخيص",
    "مراجعة اختصاصية خارجية: لم تتم بعد",
)

REQUIRED_REGISTER_FIELDS = {
    "slug",
    "title",
    "summary",
    "type",
    "version",
    "languages",
    "review",
    "book",
    "url",
}


def load_register() -> dict:
    try:
        return json.loads(REGISTER.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: articles/research-index.json is invalid: {exc}")


def main() -> None:
    errors: list[str] = []

    for rel, phrases in BANNED_VISIBLE_INTERFACE.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase in text:
                errors.append(f"{rel}: avoidable English interface label remained: {phrase}")

    hub_text = HUB.read_text(encoding="utf-8")
    for phrase in REQUIRED_ARABIC_HUB_TEXT:
        if phrase not in hub_text:
            errors.append(f"articles/index.html: required Arabic hub text missing: {phrase}")

    if 'href="/en/articles/"' not in hub_text or 'hreflang="en"' not in hub_text:
        errors.append("articles/index.html: English research hub is not clearly reachable with hreflang=en")

    data = load_register()
    items = data.get("items")
    if not isinstance(items, list) or not items:
        errors.append("articles/research-index.json: items must be a non-empty list")
        items = []

    seen_slugs: set[str] = set()
    seen_urls: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            errors.append("articles/research-index.json: every item must be an object")
            continue
        missing = sorted(field for field in REQUIRED_REGISTER_FIELDS if not item.get(field))
        slug = item.get("slug", "<unknown>")
        if missing:
            errors.append(f"articles/research-index.json: {slug} missing {', '.join(missing)}")
            continue

        if slug in seen_slugs:
            errors.append(f"articles/research-index.json: duplicate slug {slug}")
        seen_slugs.add(slug)

        url = item["url"]
        if url in seen_urls:
            errors.append(f"articles/research-index.json: duplicate URL {url}")
        seen_urls.add(url)

        languages = item["languages"]
        if not isinstance(languages, list) or "ar" not in languages:
            errors.append(f"articles/research-index.json: {slug} must declare Arabic")
        if "en" in languages and (not item.get("english_url") or not item.get("english_title")):
            errors.append(f"articles/research-index.json: {slug} declares English without english_url/english_title")

        local_path = "/" + url.removeprefix("https://ahmed-alhafiz.github.io/")
        if local_path not in hub_text:
            errors.append(f"articles/index.html: research surface not linked from hub: {local_path}")

    # The current public program intentionally contains nine Arabic research
    # surfaces. A count change must be an explicit editorial change rather than
    # accidental register drift.
    if len(items) != 9:
        errors.append(f"articles/research-index.json: expected 9 current research surfaces, found {len(items)}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)

    print(
        "Arabic UI integrity passed: current Arabic hub language is localized, "
        "the English edition remains reachable, and nine research surfaces are "
        "consistent with the machine-readable publication register."
    )


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
