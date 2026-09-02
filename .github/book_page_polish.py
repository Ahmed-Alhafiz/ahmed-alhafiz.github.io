#!/usr/bin/env python3
"""One-time polish for multilingual book pages and mobile book heroes."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS = {
    "books/sirou-fi-alard/index.html": [
        (
            '<div class="langs" aria-label="اللغات"><a href="/about/" hreflang="ar">AR</a><a href="/en/about/" hreflang="en">EN</a><a href="/de/about/" hreflang="de">DE</a></div>',
            '<div class="langs" aria-label="اللغات"><a href="/books/sirou-fi-alard/" hreflang="ar" aria-current="page">AR</a><a href="/en/books/sirou-fi-alard/" hreflang="en">EN</a><a href="/de/books/sirou-fi-alard/" hreflang="de">DE</a></div>',
        ),
        ('<meta property="og:type" content="profile">', '<meta property="og:type" content="website">'),
    ],
    "books/umm-abbas/index.html": [
        (
            '<div class="langs" aria-label="اللغات"><a href="/about/" hreflang="ar">AR</a><a href="/en/about/" hreflang="en">EN</a><a href="/de/about/" hreflang="de">DE</a></div>',
            '<div class="langs" aria-label="اللغات"><a href="/books/umm-abbas/" hreflang="ar" aria-current="page">AR</a><a href="/en/books/umm-abbas/" hreflang="en">EN</a><a href="/de/books/umm-abbas/" hreflang="de">DE</a></div>',
        ),
        ('<meta property="og:type" content="profile">', '<meta property="og:type" content="website">'),
    ],
    "en/books/sirou-fi-alard/index.html": [
        (
            '<div class="langs" aria-label="Languages"><a href="/about/" hreflang="ar">AR</a><a href="/en/about/" hreflang="en">EN</a><a href="/de/about/" hreflang="de">DE</a></div>',
            '<div class="langs" aria-label="Languages"><a href="/books/sirou-fi-alard/" hreflang="ar">AR</a><a href="/en/books/sirou-fi-alard/" hreflang="en" aria-current="page">EN</a><a href="/de/books/sirou-fi-alard/" hreflang="de">DE</a></div>',
        ),
        ('<meta property="og:type" content="profile">', '<meta property="og:type" content="website">'),
    ],
    "en/books/umm-abbas/index.html": [
        (
            '<div class="langs" aria-label="Languages"><a href="/about/" hreflang="ar">AR</a><a href="/en/about/" hreflang="en">EN</a><a href="/de/about/" hreflang="de">DE</a></div>',
            '<div class="langs" aria-label="Languages"><a href="/books/umm-abbas/" hreflang="ar">AR</a><a href="/en/books/umm-abbas/" hreflang="en" aria-current="page">EN</a><a href="/de/books/umm-abbas/" hreflang="de">DE</a></div>',
        ),
        ('<meta property="og:type" content="profile">', '<meta property="og:type" content="website">'),
    ],
}


def replace_exact(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path.relative_to(ROOT)}: expected one match, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    for rel, replacements in REPLACEMENTS.items():
        path = ROOT / rel
        if not path.exists():
            raise FileNotFoundError(rel)
        for old, new in replacements:
            replace_exact(path, old, new)
        print(f"polished: {rel}")

    css = ROOT / "assets/site-v2.css"
    replace_exact(
        css,
        ".book-hero-cover{order:-1;width:min(54vw,270px)}",
        ".book-hero-cover{order:2;width:min(54vw,270px);margin-top:4px}",
    )
    print("polished: assets/site-v2.css mobile book hierarchy")


if __name__ == "__main__":
    main()
