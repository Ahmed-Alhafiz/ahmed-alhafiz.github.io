#!/usr/bin/env python3
"""Protect Arabic interface quality and public research-status consistency.

This gate keeps avoidable English interface labels out of Arabic surfaces,
validates the machine-readable research register, and synchronizes the public
Arabic/English review-status pages with the current content inventory and
research index. It deliberately checks semantic facts rather than one visual
layout so responsive redesigns do not weaken the truth constraints.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / "articles/index.html"
REGISTER = ROOT / "articles/research-index.json"
INVENTORY = ROOT / "data/content-inventory.json"
STATUS_AR = ROOT / "research-status/index.html"
STATUS_EN = ROOT / "en/research-status/index.html"
BASE_URL = "https://ahmed-alhafiz.github.io/"
ROW_RE = re.compile(r"<tr\b[^>]*>.*?</tr>", re.IGNORECASE | re.DOTALL)

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

AR_MONTHS = {
    1: "يناير",
    2: "فبراير",
    3: "مارس",
    4: "أبريل",
    5: "مايو",
    6: "يونيو",
    7: "يوليو",
    8: "أغسطس",
    9: "سبتمبر",
    10: "أكتوبر",
    11: "نوفمبر",
    12: "ديسمبر",
}
EN_MONTHS = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


def load_json(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: {label} is invalid: {exc}")
    if not isinstance(value, dict):
        raise SystemExit(f"ERROR: {label} must be a JSON object")
    return value


def local_path(url: str) -> str:
    if not url.startswith(BASE_URL):
        return url
    return "/" + url.removeprefix(BASE_URL)


def row_for_href(html: str, href: str) -> str | None:
    double = f'href="{href}"'
    single = f"href='{href}'"
    for row in ROW_RE.findall(html):
        if double in row or single in row:
            return row
    return None


def validate_status_register(
    register: dict,
    inventory: dict,
    errors: list[str],
) -> None:
    status_ar = STATUS_AR.read_text(encoding="utf-8")
    status_en = STATUS_EN.read_text(encoding="utf-8")

    generated = inventory.get("generated")
    try:
        state_date = date.fromisoformat(generated)
    except (TypeError, ValueError):
        errors.append("data/content-inventory.json: generated must be an ISO date")
        return

    expected_ar_heading = f"الوضع العام في {state_date.day} {AR_MONTHS[state_date.month]} {state_date.year}"
    expected_en_heading = f"Current state on {state_date.day} {EN_MONTHS[state_date.month]} {state_date.year}"
    if expected_ar_heading not in status_ar:
        errors.append(f"research-status/index.html: stale visible state date; expected {expected_ar_heading!r}")
    if expected_en_heading not in status_en:
        errors.append(f"en/research-status/index.html: stale visible state date; expected {expected_en_heading!r}")

    date_pattern = re.compile(r'"dateModified"\s*:\s*"' + re.escape(generated) + r'"')
    if not date_pattern.search(status_ar):
        errors.append(f"research-status/index.html: JSON-LD dateModified must match inventory date {generated}")
    if not date_pattern.search(status_en):
        errors.append(f"en/research-status/index.html: JSON-LD dateModified must match inventory date {generated}")

    register_items = register.get("items")
    inventory_items = inventory.get("items")
    if not isinstance(register_items, list) or not isinstance(inventory_items, list):
        errors.append("research register and content inventory must both contain item lists")
        return

    register_by_slug = {
        item.get("slug"): item
        for item in register_items
        if isinstance(item, dict) and item.get("slug")
    }
    pillars = [
        item
        for item in inventory_items
        if isinstance(item, dict) and item.get("class") == "pillar"
    ]
    if len(pillars) != 4:
        errors.append(f"data/content-inventory.json: expected 4 current pillars, found {len(pillars)}")

    for pillar in pillars:
        slug = pillar.get("slug")
        languages = pillar.get("languages")
        if languages != ["ar", "en"]:
            errors.append(f"data/content-inventory.json: pillar {slug} must be exactly Arabic+English")
            continue

        item = register_by_slug.get(slug)
        if not item:
            errors.append(f"articles/research-index.json: pillar {slug} missing from research register")
            continue
        if item.get("languages") != ["ar", "en"]:
            errors.append(f"articles/research-index.json: pillar {slug} language state disagrees with inventory")

        english_url = item.get("english_url")
        english_title = item.get("english_title")
        version = str(item.get("version", ""))
        if not english_url or not english_title:
            errors.append(f"articles/research-index.json: bilingual pillar {slug} lacks English URL/title")
            continue
        if not version:
            errors.append(f"articles/research-index.json: pillar {slug} lacks version")
            continue

        ar_href = local_path(str(item.get("url", "")))
        en_href = local_path(str(english_url))
        ar_row = row_for_href(status_ar, ar_href)
        en_row = row_for_href(status_en, en_href)

        if ar_row is None:
            errors.append(f"research-status/index.html: pillar {slug} missing from Arabic status table")
        else:
            if "ثنائي اللغة" not in ar_row:
                errors.append(f"research-status/index.html: pillar {slug} is not marked bilingual")
            if f">{version}<" not in ar_row:
                errors.append(f"research-status/index.html: pillar {slug} version does not match {version}")

        if en_row is None:
            errors.append(f"en/research-status/index.html: English pillar link missing for {slug}: {en_href}")
        else:
            if "bilingual" not in en_row.lower():
                errors.append(f"en/research-status/index.html: pillar {slug} is not marked bilingual")
            if f">{version}<" not in en_row:
                errors.append(f"en/research-status/index.html: pillar {slug} version does not match {version}")


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

    data = load_json(REGISTER, "articles/research-index.json")
    inventory = load_json(INVENTORY, "data/content-inventory.json")
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

        local = local_path(url)
        if local not in hub_text:
            errors.append(f"articles/index.html: research surface not linked from hub: {local}")

    if len(items) != 9:
        errors.append(f"articles/research-index.json: expected 9 current research surfaces, found {len(items)}")

    validate_status_register(data, inventory, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)

    print(
        "Arabic UI integrity passed: the Arabic hub is localized, nine research "
        "surfaces match the machine register, and all four bilingual pillars have "
        "current Arabic/English status rows with synchronized versions and dates."
    )


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
