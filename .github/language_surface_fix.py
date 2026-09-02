#!/usr/bin/env python3
"""Correct visible language switchers on research surfaces.

The public switcher must point to the exact hreflang counterpart. A language
without an equivalent page is not shown merely to increase apparent coverage.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPLACEMENTS = {
    "methodology/index.html": (
        '<div class="langs" aria-label="اللغات"><a href="/" hreflang="ar" aria-current="page">AR</a><a href="/en/" hreflang="en">EN</a><a href="/de/" hreflang="de">DE</a></div>',
        '<div class="langs" aria-label="اللغات"><a href="/methodology/" hreflang="ar" aria-current="page">AR</a><a href="/en/methodology/" hreflang="en">EN</a></div>',
    ),
    "articles/index.html": (
        '<div class="langs" aria-label="اللغات"><a href="/" hreflang="ar" aria-current="page">AR</a><a href="/en/" hreflang="en">EN</a><a href="/de/" hreflang="de">DE</a></div>',
        '<div class="langs" aria-label="اللغات"><a href="/articles/" hreflang="ar" aria-current="page">AR</a><a href="/en/articles/" hreflang="en">EN</a></div>',
    ),
    "research-status/index.html": (
        '<div class="langs" aria-label="اللغات"><a href="/" hreflang="ar" aria-current="page">AR</a><a href="/en/" hreflang="en">EN</a><a href="/de/" hreflang="de">DE</a></div>',
        '<div class="langs" aria-label="اللغات"><a href="/research-status/" hreflang="ar" aria-current="page">AR</a><a href="/en/research-status/" hreflang="en">EN</a></div>',
    ),
    "en/methodology/index.html": (
        '<div class="langs" aria-label="Languages"><a href="/" hreflang="ar">AR</a><a href="/en/" hreflang="en" aria-current="page">EN</a><a href="/de/" hreflang="de">DE</a></div>',
        '<div class="langs" aria-label="Languages"><a href="/methodology/" hreflang="ar">AR</a><a href="/en/methodology/" hreflang="en" aria-current="page">EN</a></div>',
    ),
    "en/articles/index.html": (
        '<div class="langs" aria-label="Languages"><a href="/" hreflang="ar">AR</a><a href="/en/" hreflang="en" aria-current="page">EN</a><a href="/de/" hreflang="de">DE</a></div>',
        '<div class="langs" aria-label="Languages"><a href="/articles/" hreflang="ar">AR</a><a href="/en/articles/" hreflang="en" aria-current="page">EN</a></div>',
    ),
    "en/research-status/index.html": (
        '<div class="langs" aria-label="Languages"><a href="/" hreflang="ar">AR</a><a href="/en/" hreflang="en" aria-current="page">EN</a><a href="/de/" hreflang="de">DE</a></div>',
        '<div class="langs" aria-label="Languages"><a href="/research-status/" hreflang="ar">AR</a><a href="/en/research-status/" hreflang="en" aria-current="page">EN</a></div>',
    ),
    "articles/ratq-fatq-big-bang/evidence/index.html": (
        '<div class="langs"><a href="/articles/ratq-fatq-big-bang/evidence/" aria-current="page">AR</a><a href="/en/articles/ratq-fatq-big-bang/evidence/">EN</a></div>',
        '<div class="langs" aria-label="اللغات"><a href="/articles/ratq-fatq-big-bang/evidence/" hreflang="ar" aria-current="page">AR</a><a href="/en/articles/ratq-fatq-big-bang/evidence/" hreflang="en">EN</a></div>',
    ),
    "en/articles/ratq-fatq-big-bang/evidence/index.html": (
        '<div class="langs"><a href="/articles/ratq-fatq-big-bang/evidence/">AR</a><a href="/en/articles/ratq-fatq-big-bang/evidence/" aria-current="page">EN</a></div>',
        '<div class="langs" aria-label="Languages"><a href="/articles/ratq-fatq-big-bang/evidence/" hreflang="ar">AR</a><a href="/en/articles/ratq-fatq-big-bang/evidence/" hreflang="en" aria-current="page">EN</a></div>',
    ),
}


def main() -> None:
    for rel, (old, new) in REPLACEMENTS.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            raise RuntimeError(f"{rel}: expected one exact switcher block, found {count}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        print(f"corrected: {rel}")


if __name__ == "__main__":
    main()
