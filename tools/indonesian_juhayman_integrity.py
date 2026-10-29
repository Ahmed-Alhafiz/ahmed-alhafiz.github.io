#!/usr/bin/env python3
"""Protect the approved complete Juhayman translation and its four-language graph."""
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin
from html.parser import HTMLParser
import hashlib, json, re
from indonesian_ratq_integrity import Content
from indonesian_pilot_integrity import Units

ROOT = Path(__file__).resolve().parents[1]
HOST = 'https://ahmedalhafiz.com'
ROUTE = '/id/articles/juhaiman-masjidil-haram-1979/'
URL = HOST + ROUTE

def digest(text): return hashlib.sha256(text.encode()).hexdigest()
def mainpart(text): return re.search(r'<main\b.*?</main>', text, re.S).group()
def compact(text): return re.sub(r'\s+', '', text)

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.alternates = {}; self.canonical = []; self.ids = []; self.links = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'): self.ids.append(a['id'])
        if tag == 'link' and a.get('hreflang'): self.alternates[a['hreflang']] = a['href']
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical.append(a['href'])
        if tag == 'a': self.links.append(a)

def main():
    audit = json.loads((ROOT / 'audit-reports/indonesian-juhayman-publication-2026-10-28.json').read_text())
    assert audit['owner_approved'] and not audit['specialist_review_completed']
    for record in audit['existing_main_pages']:
        assert digest(mainpart((ROOT / record['path']).read_text())) == record['main_sha256'], record['path'] + ': original body changed'
    text = (ROOT / (ROUTE.lstrip('/') + 'index.html')).read_text()
    body = mainpart(text); p = Content(); p.feed(body)
    expected = {u['id']: u['translation_text_sha256'] for u in audit['units']}
    supplements = {u['id']: u['text_sha256'] for u in audit['supplements']}
    assert len(expected) == 106 and set(expected) == {f'J{i:03}' for i in range(1, 107)}
    assert len(supplements) == 1 and set(p.units) == set(expected) | set(supplements)
    for uid, value in {**expected, **supplements}.items(): assert digest(p.units[uid]) == value, uid + ': approved text drift'
    assert compact(''.join(p.all_text)) == compact(''.join(p.units.values())), 'Unmapped body text'
    for tag, count in {'h1': 1, 'h2': 13, 'h3': 7, 'li': 19, 'table': 1, 'tr': 10, 'th': 3, 'td': 27, 'img': 0, 'blockquote': 1, 'strong': 2, 'em': 2, 'sup': 15}.items():
        assert p.counts[tag] == count, (tag, p.counts[tag], count)
    assert audit['source_hadith_excerpt'] in p.units['J050']
    assert '«جهيمان — خوارج بين الركن والمقام»' in p.units['J080']
    assert 'hari pertama abad Hijriah yang baru' in p.units['J051'], 'Do not silently change the author’s calendar wording'
    visible_refs = [re.search(r'https://\S+', p.units[f'J{i:03}']).group() for i in range(99, 103)]
    assert visible_refs == audit['references'] and len(visible_refs) == 4
    translated_links = [a['href'] if a['href'].startswith('#') else urljoin(audit['source_url'], a['href']) for a in p.links]
    assert translated_links == audit['main_link_targets'] and len(translated_links) == 23
    metadata = Units(); metadata.feed(text)
    article = next(n for block in metadata.blocks for n in block.get('@graph', []) if n.get('@type') == 'Article')
    assert article['headline'] == ''.join(metadata.title) == audit['h1']
    assert article['name'] == audit['seo_title'] and len(article['name']) == 60
    assert article['description'] == audit['meta_description']
    assert article['citation'] == visible_refs and article['translationOfWork'] == {'@id': audit['source_url'] + '#article'}
    assert article['author'] == {'@id': HOST + '/#person'}
    assert article['datePublished'] >= '2026-10-28' and article['dateModified'] >= article['datePublished']
    page = Page(); page.feed(text)
    assert page.canonical == [URL] and len(page.ids) == len(set(page.ids))
    for a in page.links:
        if a.get('href', '').startswith('#'): assert a['href'][1:] in page.ids
    for lang in ('ar', 'en', 'de', 'id', 'x-default'): assert lang in page.alternates
    for lang in ('ar', 'en', 'de'):
        rel = page.alternates[lang].removeprefix(HOST).lstrip('/') + 'index.html'
        counterpart = Page(); counterpart.feed((ROOT / rel).read_text())
        assert counterpart.alternates == page.alternates, lang + ': nonreciprocal language graph'
        assert any(a.get('hreflang') == 'id' and a.get('href') == URL for a in counterpart.links)
    assert '<html lang="id" dir="ltr">' in text and 'content="noindex' not in text
    assert 'id-draft-notice' not in text and text.count('/assets/analytics-indonesia-pilot.js') == 1
    for a in p.links:
        if 'data-article-to-book' in a:
            assert a['data-lang'] == 'id' and a['data-article-slug'] == 'juhaiman-masjidil-haram-1979'
            assert a['data-book-slug'] == 'juhayman' and a['hreflang'] == 'ar'
    catalogue = Units(); catalogue.feed((ROOT / 'id/articles/index.html').read_text())
    listing = next(n for b in catalogue.blocks for n in b.get('@graph', []) if n.get('@type') == 'ItemList')
    assert listing['numberOfItems'] == len(listing['itemListElement']) == 3
    assert listing['itemListElement'][0]['url'] == URL
    feed = json.loads((ROOT / 'id/articles/feed.json').read_text())
    assert len(feed['items']) == 3 and feed['items'][0]['url'] == URL
    assert URL in (ROOT / 'sitemap.xml').read_text()
    print('Indonesian Juhayman integrity passed: all 106 approved units, 9-row data table, 4 visible/schema references, 23 source links, Arabic hadith excerpt, reciprocal AR/EN/DE/ID and unchanged existing bodies.')

if __name__ == '__main__': main()
