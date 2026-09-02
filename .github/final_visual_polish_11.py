#!/usr/bin/env python3
"""One-time final visual polish for UX rebuild 10.

The script fixes defects discovered by manual inspection of the successful
visual artifact:
- book-cover source files contain large black padding, so hero/card frames must
  crop rather than display the full padded canvas;
- the Arabic research hub still contained avoidable English interface labels;
- the water row in the publication register had six cells under five headers;
- one English meta description and one review-status phrase produced warnings.
"""
from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS_MARKER = "/* UX10 cover-frame and Arabic-interface polish */"
CSS = r'''

/* UX10 cover-frame and Arabic-interface polish */
.book-hero-cover{aspect-ratio:2/3}
.book-hero-cover img{width:100%;height:100%;aspect-ratio:auto;object-fit:cover;object-position:center}
.book-card-cover{display:block;width:100%;aspect-ratio:2/3;overflow:hidden;border-radius:10px;background:#171717}
.book-card .book-card-cover img{display:block;width:100%;height:100%;aspect-ratio:auto;object-fit:cover;object-position:center;border-radius:0}
'''

BOOK_CARD_RE = re.compile(
    r'(<article\b[^>]*class=["\'][^"\']*\bbook-card\b[^"\']*["\'][^>]*>\s*<a\b[^>]*>\s*)'
    r'(<img\b[^>]*>)',
    re.IGNORECASE,
)

ARABIC_UI_REPLACEMENTS = {
    "Author research desk · مكتب أبحاث الكاتب": "مركز أبحاث أحمد الحافظ",
    "Flagship dossier · الإصدار 2.0": "الملف البحثي المحوري · الإصدار 2.0",
    "Global bilingual dossier · الإصدار 1.0": "ملف بحثي ثنائي اللغة · الإصدار 1.0",
    "Extended dossiers in Arabic": "ملفات موسعة باللغة العربية",
    "02 / LANGUAGE &amp; AI": "02 / اللغة والذكاء الاصطناعي",
    "03 / SAFEGUARDING": "03 / الحماية والسلامة",
    "REVIEW / STATUS": "المراجعة / الحالة",
    "Research tracks": "المسارات البحثية",
    "01 / COSMOS": "01 / الكون",
    "02 / MIND": "02 / العقل والتجربة",
    "03 / NARRATIVE": "03 / السرد والسلطة",
    "Publication register": "سجل النشر",
    "Global edition policy": "سياسة الإصدار العالمي",
    "English research desk": "مركز الأبحاث بالإنجليزية",
    "Open the English desk": "فتح مركز الأبحاث بالإنجليزية",
    "English edition": "النسخة الإنجليزية",
    "العربية / English": "العربية والإنجليزية",
}

BANNED_ARABIC_UI = tuple(ARABIC_UI_REPLACEMENTS)

WATER_ROW_OLD = (
    '<tr><td><a href="/articles/water-civilization-power/">الماء والحضارة والسلطة</a></td>'
    '<td>ملف بحثي موسع ثنائي اللغة</td><td>1.0</td><td>عربي وإنجليزي</td><td>21</td>'
    '<td>مراجعة المؤلف مكتملة؛ مراجعة اختصاصية خارجية معلّقة</td></tr>'
)
WATER_ROW_NEW = (
    '<tr><td><a href="/articles/water-civilization-power/">الماء والحضارة والسلطة</a></td>'
    '<td>ملف بحثي موسع ثنائي اللغة</td><td>العربية والإنجليزية</td>'
    '<td><span class="confidence open">مراجعة اختصاصية خارجية معلّقة</span></td><td>1.0</td></tr>'
)

Juhayman_DESCRIPTION_OLD = (
    "The official page for Juhayman — The Resurrection Between the Rukn and the Maqam, "
    "a forthcoming historical religious novel by Ahmed Alhafiz about the 1979 Grand Mosque "
    "seizure and the paths of extremism."
)
Juhayman_DESCRIPTION_NEW = (
    "Official page for Juhayman, Ahmed Alhafiz’s forthcoming historical novel about the "
    "1979 Grand Mosque seizure and the paths of closed certainty."
)


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_table = False
        self.depth = 0
        self.in_row = False
        self.current = 0
        self.rows: list[int] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key: value or "" for key, value in attrs}
        classes = attributes.get("class", "").split()
        if tag.lower() == "table" and "dossier-table" in classes and not self.in_table:
            self.in_table = True
            self.depth = 1
            return
        if not self.in_table:
            return
        if tag.lower() == "table":
            self.depth += 1
        if tag.lower() == "tr":
            self.in_row = True
            self.current = 0
        elif self.in_row and tag.lower() in {"th", "td"}:
            self.current += 1

    def handle_endtag(self, tag: str) -> None:
        if not self.in_table:
            return
        if tag.lower() == "tr" and self.in_row:
            self.rows.append(self.current)
            self.in_row = False
        if tag.lower() == "table":
            self.depth -= 1
            if self.depth == 0:
                self.in_table = False


def replace_exact(path: Path, old: str, new: str, *, expected: int = 1) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != expected:
        raise RuntimeError(
            f"{path.relative_to(ROOT)}: expected {expected} occurrence(s) of {old!r}, found {count}"
        )
    path.write_text(text.replace(old, new), encoding="utf-8")


def patch_css() -> None:
    path = ROOT / "assets/site-v2.css"
    text = path.read_text(encoding="utf-8")
    if CSS_MARKER in text:
        raise RuntimeError("cover-frame polish marker already exists")
    path.write_text(text.rstrip() + CSS.rstrip() + "\n", encoding="utf-8")


def wrap_book_cards() -> int:
    total = 0
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        revised, count = BOOK_CARD_RE.subn(r'\1<span class="book-card-cover">\2</span>', text)
        if count:
            path.write_text(revised, encoding="utf-8")
            total += count
    if total < 12:
        raise RuntimeError(f"expected at least 12 book-card images, wrapped only {total}")
    return total


def polish_arabic_interface() -> None:
    path = ROOT / "articles/index.html"
    text = path.read_text(encoding="utf-8")
    for old, new in ARABIC_UI_REPLACEMENTS.items():
        text = text.replace(old, new)
    if text.count(WATER_ROW_OLD) != 1:
        raise RuntimeError("Arabic research hub: malformed water publication row not found exactly once")
    text = text.replace(WATER_ROW_OLD, WATER_ROW_NEW, 1)
    path.write_text(text, encoding="utf-8")

    water = ROOT / "articles/water-civilization-power/index.html"
    replace_exact(
        water,
        '>English edition</a>',
        '>النسخة الإنجليزية</a>',
    )


def remove_warnings() -> None:
    juhayman = ROOT / "en/books/juhayman/index.html"
    replace_exact(juhayman, Juhayman_DESCRIPTION_OLD, Juhayman_DESCRIPTION_NEW)

    water = ROOT / "en/articles/water-civilization-power/index.html"
    replace_exact(
        water,
        "Independent specialist review: not yet completed",
        "External specialist review: not yet completed",
    )


def normalize_text_files() -> None:
    for path in [*ROOT.rglob("*.html"), ROOT / "assets/site-v2.css"]:
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        normalized = "\n".join(line.rstrip() for line in text.rstrip().splitlines()) + "\n"
        if normalized != text:
            path.write_text(normalized, encoding="utf-8")


def validate() -> None:
    errors: list[str] = []
    css = (ROOT / "assets/site-v2.css").read_text(encoding="utf-8")
    for token in (
        CSS_MARKER,
        ".book-hero-cover{aspect-ratio:2/3}",
        ".book-hero-cover img{width:100%;height:100%;aspect-ratio:auto;object-fit:cover;object-position:center}",
        ".book-card-cover{display:block;width:100%;aspect-ratio:2/3;overflow:hidden",
        ".book-card .book-card-cover img{display:block;width:100%;height:100%;aspect-ratio:auto;object-fit:cover",
    ):
        if token not in css:
            errors.append(f"assets/site-v2.css: missing {token}")

    wrapped = 0
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        wrapped += text.count('class="book-card-cover"')
        if BOOK_CARD_RE.search(text):
            errors.append(f"{path.relative_to(ROOT)}: an unwrapped book-card image remained")
    if wrapped < 12:
        errors.append(f"expected at least 12 wrapped book-card images, found {wrapped}")

    hub = (ROOT / "articles/index.html").read_text(encoding="utf-8")
    for phrase in BANNED_ARABIC_UI:
        if phrase in hub:
            errors.append(f"articles/index.html: avoidable English UI remained: {phrase}")
    parser = TableParser()
    parser.feed(hub)
    if not parser.rows:
        errors.append("articles/index.html: publication table not found")
    elif len(set(parser.rows)) != 1 or parser.rows[0] != 5:
        errors.append(f"articles/index.html: inconsistent publication table cells {parser.rows}")

    water_ar = (ROOT / "articles/water-civilization-power/index.html").read_text(encoding="utf-8")
    if ">English edition</a>" in water_ar or ">النسخة الإنجليزية</a>" not in water_ar:
        errors.append("Arabic water dossier: English edition button was not localized")

    water_en = (ROOT / "en/articles/water-civilization-power/index.html").read_text(encoding="utf-8")
    if "External specialist review: not yet completed" not in water_en:
        errors.append("English water dossier: explicit external-review wording missing")

    juhayman = (ROOT / "en/books/juhayman/index.html").read_text(encoding="utf-8")
    if Juhayman_DESCRIPTION_OLD in juhayman or Juhayman_DESCRIPTION_NEW not in juhayman:
        errors.append("English Juhayman meta description was not shortened")

    if errors:
        raise SystemExit("\n".join(errors))


def main() -> None:
    patch_css()
    wrapped = wrap_book_cards()
    polish_arabic_interface()
    remove_warnings()
    normalize_text_files()
    validate()
    print(f"Final visual polish applied; wrapped {wrapped} book-card cover images")


if __name__ == "__main__":
    main()
