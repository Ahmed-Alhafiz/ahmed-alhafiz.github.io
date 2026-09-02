#!/usr/bin/env python3
"""Harden the one-time dossier 11 integration before execution.

The first draft correctly covered content, feeds, evidence and permanent gates,
but two release-surface operations required stronger handling:
- book cards must be inserted without splitting existing HTML;
- the current visual review stores its route inventory in the Selenium runner,
  not in the workflow YAML, and its inventory assertions must remain dynamic.
The English review register is also upgraded to the same six-column structure
used by the Arabic register.
"""
from __future__ import annotations

from pathlib import Path

PATH = Path(".github/dossier11_integrate.py")

BOOKS = r'''def patch_books() -> None:
    pages = (
        (
            ROOT / "books/umm-abbas/index.html",
            '<div class="article-list"><article class="article-card"><div><div class="kicker">ملف مستقل</div><h2><a href="/articles/spiritual-healing-exploitation-safeguarding/">',
            '<div class="article-list">' + AR_BOOK_CARD + '<article class="article-card"><div><div class="kicker">ملف مستقل</div><h2><a href="/articles/spiritual-healing-exploitation-safeguarding/">',
            AR_ROUTE,
        ),
        (
            ROOT / "en/books/umm-abbas/index.html",
            '<div class="article-list"><article class="article-card"><div><div class="kicker">Arabic independent dossier</div><h2><a href="/articles/spiritual-healing-exploitation-safeguarding/" hreflang="ar">',
            '<div class="article-list">' + EN_BOOK_CARD + '<article class="article-card"><div><div class="kicker">Arabic independent dossier</div><h2><a href="/articles/spiritual-healing-exploitation-safeguarding/" hreflang="ar">',
            EN_ROUTE,
        ),
        (
            ROOT / "de/books/umm-abbas/index.html",
            '<div class="article-list"><article class="article-card"><div><div class="kicker">Thematisch verbunden</div><h2><a href="/articles/spiritual-healing-exploitation-safeguarding/">',
            '<div class="article-list">' + DE_BOOK_CARD + '<article class="article-card"><div><div class="kicker">Thematisch verbunden</div><h2><a href="/articles/spiritual-healing-exploitation-safeguarding/">',
            EN_ROUTE,
        ),
    )
    for path, marker, replacement, route in pages:
        text = path.read_text(encoding="utf-8")
        if route in text:
            raise RuntimeError(f"{path.relative_to(ROOT)}: dossier card already exists before one-time integration")
        if text.count(marker) != 1:
            raise RuntimeError(f"{path.relative_to(ROOT)}: expected one book-card insertion marker, found {text.count(marker)}")
        write_text(path, text.replace(marker, replacement, 1))
'''

STATUS = r'''def patch_status() -> None:
    path = ROOT / "research-status/index.html"
    text = path.read_text(encoding="utf-8")
    marker = "<tbody><tr><td><a href=\"/articles/water-civilization-power/\">"
    if text.count(marker) != 1:
        raise RuntimeError(f"Arabic status tbody marker count: {text.count(marker)}")
    write_text(path, text.replace(marker, "<tbody>" + AR_STATUS_ROW + '<tr><td><a href="/articles/water-civilization-power/">', 1))

    path = ROOT / "en/research-status/index.html"
    text = path.read_text(encoding="utf-8")
    old_header = "<thead><tr><th>Work</th><th>Type</th><th>Version</th><th>Source review</th><th>External review</th></tr></thead>"
    new_header = "<thead><tr><th>Work</th><th>Type</th><th>Version</th><th>Source review</th><th>External review</th><th>Related work</th></tr></thead>"
    if text.count(old_header) != 1:
        raise RuntimeError(f"English status header marker count: {text.count(old_header)}")
    text = text.replace(old_header, new_header, 1)

    relationships = {
        "/en/articles/water-civilization-power/": '<a href="/en/books/sirou-fi-alard/">Sirou fi al-Ard</a> — thematic relationship, not evidence',
        "/en/articles/ratq-fatq-big-bang/": '<a href="/en/books/sirou-fi-alard/">Sirou fi al-Ard</a> — thematic relationship, not evidence',
        "/articles/teaching-names-ai-understanding/": '<a href="/en/books/sirou-fi-alard/">Sirou fi al-Ard</a> — thematic relationship',
        "/articles/spiritual-healing-exploitation-safeguarding/": '<a href="/en/books/umm-abbas/">Umm Abbas</a> — thematic relationship',
        "/articles/six-days-creation-cosmic-time/": '<a href="/en/books/sirou-fi-alard/">Sirou fi al-Ard</a> — thematic relationship',
        "/articles/sleep-paralysis-jathoom/": '<a href="/en/books/umm-abbas/">Umm Abbas</a> — thematic relationship',
        "/articles/functional-seizures-vs-epilepsy/": '<a href="/en/books/umm-abbas/">Umm Abbas</a> — thematic relationship',
    }
    for route, relationship in relationships.items():
        row_start = text.find(f'<tr><td><a href="{route}"')
        if row_start < 0:
            raise RuntimeError(f"English status row not found for {route}")
        row_end = text.find("</tr>", row_start)
        if row_end < 0:
            raise RuntimeError(f"English status row is not closed for {route}")
        row = text[row_start:row_end + len("</tr>")]
        if row.count("<td>") != 5:
            raise RuntimeError(f"English status row for {route} has {row.count('<td>')} cells before upgrade")
        upgraded = row[:-len("</tr>")] + f"<td>{relationship}</td></tr>"
        text = text[:row_start] + upgraded + text[row_end + len("</tr>"):]

    marker = "<tbody><tr><td><a href=\"/en/articles/water-civilization-power/\">"
    if text.count(marker) != 1:
        raise RuntimeError(f"English status tbody marker count after upgrade: {text.count(marker)}")
    write_text(path, text.replace(marker, "<tbody>" + EN_STATUS_ROW + '<tr><td><a href="/en/articles/water-civilization-power/">', 1))
'''

VISUAL = r'''def patch_visual_review() -> None:
    path = ROOT / ".github/visual-review/run_visual_review.py"
    text = path.read_text(encoding="utf-8")

    page_marker = '    ("water-en", "/en/articles/water-civilization-power/"),\n'
    page_addition = (
        f'    ("fear-ar", "{AR_ROUTE}"),\n'
        f'    ("fear-en", "{EN_ROUTE}"),\n'
        f'    ("fear-evidence-ar", "{AR_ROUTE}evidence/"),\n'
        f'    ("fear-evidence-en", "{EN_ROUTE}evidence/"),\n'
    )
    if text.count(page_marker) != 1:
        raise RuntimeError(f"Visual TOP_PAGES marker count: {text.count(page_marker)}")
    text = text.replace(page_marker, page_marker + page_addition, 1)

    social_marker = '    Path("assets/social/water-civilization-power-en.png"),\n'
    social_addition = (
        '    Path("assets/social/diagnostic-uncertainty-family-fear-ar.png"),\n'
        '    Path("assets/social/diagnostic-uncertainty-family-fear-en.png"),\n'
    )
    if text.count(social_marker) != 1:
        raise RuntimeError(f"Visual SOCIAL_CARDS marker count: {text.count(social_marker)}")
    text = text.replace(social_marker, social_marker + social_addition, 1)

    old_inventory = '''def verify_inventory() -> None:
    for mode, dimensions in VIEWPORTS.items():
        images = sorted((ROOT / mode).glob("*.png"))
        if len(images) != 30:
            raise SystemExit(f"{mode}: expected 30 screenshots, found {len(images)}")
        for image in images:
            if png_dimensions(image) != dimensions:
                raise SystemExit(f"{image}: wrong screenshot dimensions")
    if len(list((ROOT / "geometry").glob("*.json"))) != 2:
        raise SystemExit("Expected two geometry reports")
    if len(list((ROOT / "targets").glob("*.json"))) != 2:
        raise SystemExit("Expected two target reports")
    if len(list((ROOT / "social").glob("*.png"))) != 2:
        raise SystemExit("Expected two social cards")
'''
    new_inventory = '''def verify_inventory() -> None:
    expected_screenshots = len(TOP_PAGES) + len(TARGET_PAGES)
    for mode, dimensions in VIEWPORTS.items():
        images = sorted((ROOT / mode).glob("*.png"))
        if len(images) != expected_screenshots:
            raise SystemExit(
                f"{mode}: expected {expected_screenshots} screenshots, found {len(images)}"
            )
        for image in images:
            if png_dimensions(image) != dimensions:
                raise SystemExit(f"{image}: wrong screenshot dimensions")
    if len(list((ROOT / "geometry").glob("*.json"))) != len(VIEWPORTS):
        raise SystemExit(f"Expected {len(VIEWPORTS)} geometry reports")
    if len(list((ROOT / "targets").glob("*.json"))) != len(VIEWPORTS):
        raise SystemExit(f"Expected {len(VIEWPORTS)} target reports")
    if len(list((ROOT / "social").glob("*.png"))) != len(SOCIAL_CARDS):
        raise SystemExit(f"Expected {len(SOCIAL_CARDS)} social cards")
'''
    if text.count(old_inventory) != 1:
        raise RuntimeError(f"Visual inventory block count: {text.count(old_inventory)}")
    text = text.replace(old_inventory, new_inventory, 1)

    old_summary = '''    print(
        "Visual review passed: 60 exact-size screenshots, six portrait tests at "
        "two viewports, 12 verified targeted captures, and two social cards."
    )
'''
    new_summary = '''    total_screenshots = (len(TOP_PAGES) + len(TARGET_PAGES)) * len(VIEWPORTS)
    print(
        f"Visual review passed: {total_screenshots} exact-size screenshots, "
        f"{len(GEOMETRY_TESTS)} portrait tests at {len(VIEWPORTS)} viewports, "
        f"{len(TARGET_PAGES) * len(VIEWPORTS)} verified targeted captures, "
        f"and {len(SOCIAL_CARDS)} social cards."
    )
'''
    if text.count(old_summary) != 1:
        raise RuntimeError(f"Visual final-summary block count: {text.count(old_summary)}")
    write_text(path, text.replace(old_summary, new_summary, 1))
'''


def replace_function(text: str, name: str, next_name: str, replacement: str) -> str:
    start_marker = f"def {name}() -> None:\n"
    end_marker = f"\ndef {next_name}() -> None:\n"
    start = text.find(start_marker)
    end = text.find(end_marker, start)
    if start < 0 or end < 0:
        raise SystemExit(f"Could not locate function span {name} -> {next_name}")
    return text[:start] + replacement.rstrip() + "\n\n" + text[end + 1:]


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    text = replace_function(text, "patch_books", "patch_status", BOOKS)
    text = replace_function(text, "patch_status", "patch_companion", STATUS)
    text = replace_function(text, "patch_visual_review", "patch_cff", VISUAL)
    PATH.write_text("\n".join(line.rstrip() for line in text.rstrip().splitlines()) + "\n", encoding="utf-8")
    print("Hardened dossier 11 integration for books, review tables, and Selenium visual inventory")


if __name__ == "__main__":
    main()
