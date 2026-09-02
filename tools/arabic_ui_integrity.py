#!/usr/bin/env python3
"""Protect Arabic interface language and research-register structure.

English titles, scientific abbreviations, source names, and book subtitles may
remain where they carry content. This gate targets avoidable English interface
labels that made Arabic pages look unfinished, and it verifies that the public
research register has one consistent column model.
"""
from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

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
        "English research desk",
        "Open the English desk",
        "English edition",
        "العربية / English",
    ),
    "articles/water-civilization-power/index.html": (
        ">English edition</a>",
    ),
}

REQUIRED_ARABIC_LABELS = {
    "articles/index.html": (
        "مركز أبحاث أحمد الحافظ",
        "الملف البحثي المحوري",
        "ملف بحثي ثنائي اللغة",
        "ملفات موسعة باللغة العربية",
        "المسارات البحثية",
        "سجل النشر",
        "سياسة الإصدار العالمي",
        "مركز الأبحاث بالإنجليزية",
        "النسخة الإنجليزية",
    ),
    "articles/water-civilization-power/index.html": (
        ">النسخة الإنجليزية</a>",
    ),
}


class DossierTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_table = False
        self.table_depth = 0
        self.in_row = False
        self.current_cells = 0
        self.rows: list[int] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key: value or "" for key, value in attrs}
        classes = attributes.get("class", "").split()
        tag = tag.lower()
        if tag == "table" and "dossier-table" in classes and not self.in_table:
            self.in_table = True
            self.table_depth = 1
            return
        if not self.in_table:
            return
        if tag == "table":
            self.table_depth += 1
        elif tag == "tr":
            self.in_row = True
            self.current_cells = 0
        elif self.in_row and tag in {"th", "td"}:
            self.current_cells += 1

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if not self.in_table:
            return
        if tag == "tr" and self.in_row:
            self.rows.append(self.current_cells)
            self.in_row = False
        elif tag == "table":
            self.table_depth -= 1
            if self.table_depth == 0:
                self.in_table = False


def main() -> None:
    errors: list[str] = []

    for rel, phrases in BANNED_VISIBLE_INTERFACE.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase in text:
                errors.append(f"{rel}: avoidable English interface label remained: {phrase}")

    for rel, phrases in REQUIRED_ARABIC_LABELS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{rel}: required Arabic interface label missing: {phrase}")

    hub_path = ROOT / "articles/index.html"
    parser = DossierTableParser()
    parser.feed(hub_path.read_text(encoding="utf-8"))
    if not parser.rows:
        errors.append("articles/index.html: publication register table not found")
    elif parser.rows[0] != 5:
        errors.append(
            f"articles/index.html: publication register must have five headers, found {parser.rows[0]}"
        )
    elif any(cells != parser.rows[0] for cells in parser.rows[1:]):
        errors.append(
            "articles/index.html: publication register row/header mismatch: "
            f"{parser.rows}"
        )

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)

    print(
        "Arabic UI integrity passed: research labels are localized, the English "
        "edition remains clearly reachable, and every publication-register row "
        "matches the five-column header."
    )


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
