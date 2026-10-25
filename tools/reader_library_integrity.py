#!/usr/bin/env python3
"""Verify the book reading routes and both complete research libraries."""
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from reading_paths import BOOK_LABELS, book_assignments
from refresh_research_library import TOPICS

ROOT = Path(__file__).resolve().parents[1]


def validate(root=ROOT):
    associations = book_assignments(root)
    topic_for = {slug: topic for topic, slugs in TOPICS.items() for slug in slugs}
    for lang, prefix in (("ar", ""), ("en", "en/")):
        source = (root / prefix / "articles/index.html").read_text()
        feed = json.loads((root / prefix / "articles/feed.json").read_text())["items"]
        expected = {urlparse(item["url"]).path for item in feed}
        counts = Counter()
        found = set()
        for group in re.findall(r'<section class="library-group".*?</section>', source, re.S):
            topic = re.search(r'id="topic-([^"]+)"', group)[1]
            for card in re.findall(r'<article\b[^>]*data-article="[^"]+"[^>]*>.*?</article>', group, re.S):
                slug = re.search(r'data-article="([^"]+)"', card)[1]
                book = re.search(r'data-book="([^"]+)"', card)[1]
                assert book == associations[slug], f"{lang}/{slug}: unsupported book relationship"
                assert topic == topic_for[slug], f"{lang}/{slug}: incorrect topic"
                route = re.search(r'<h3><a href="([^"]+)"', card)[1]
                assert route not in found, f"{lang}: duplicate article {route}"
                found.add(route)
                counts[book] += 1
        assert found == expected, f"{lang}: research library and published editions differ"
        assert source.count('id="library-controls"') == source.count('id="library-book"') == 1
        assert len(re.findall(r'name="library-view"', source)) == 2
        assert 'id="library-controls" class="library-search" role="search" hidden' in source
        for book in BOOK_LABELS:
            assert f'<option value="{book}"' in source and f'({counts[book]})</option>' in source
        for path in [root / prefix / "index.html", root / prefix / "books/index.html"]:
            html = path.read_text()
            routes = re.findall(r'<a class="book-reading-link" href="([^"]+)"', html)
            actual = {parse_qs(urlparse(route).query)["book"][0] for route in routes}
            assert len(routes) == 4 and actual == set(BOOK_LABELS), f"{path}: incomplete book reading routes"
            assert all(urlparse(route).fragment == "library-controls" for route in routes)
        home = (root / prefix / "index.html").read_text()
        assert 'class="hero-portrait"' not in home, f"{lang}: removed portrait returned"
        assert f'class="author-about" href="/{prefix}about/"' in home
        for book in BOOK_LABELS:
            page = (root / prefix / "books" / book / "index.html").read_text()
            assert 'book-reading-hub' in page and 'class="book-route-nav"' in page
            assert 'book-section-nav' not in page, f'{lang}/{book}: duplicate reading navigation'
            assert f'href="/{prefix}articles/?book={book}#library-controls"' in page
            assert 'id="about-book"' in page
        print(f"{lang}: {len(found)} complete entries; declared book routes {dict(counts)}")


if __name__ == "__main__":
    validate()
