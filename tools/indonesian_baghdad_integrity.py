#!/usr/bin/env python3
"""Protect all approved Baghdad units, the disclosed correction and language graph."""
from pathlib import Path
import hashlib, json, re
from indonesian_ratq_integrity import Content
from indonesian_pilot_integrity import Units
from indonesian_juhayman_integrity import Page

ROOT = Path(__file__).resolve().parents[1]
HOST = 'https://ahmedalhafiz.com'
ROUTE = '/id/articles/jatuhnya-baghdad-1258-ibnu-al-alqami/'
URL = HOST + ROUTE
def digest(s): return hashlib.sha256(s.encode()).hexdigest()
def mainpart(s): return re.search(r'<main\b.*?</main>', s, re.S).group()
def compact(s): return re.sub(r'\s+', '', s)

def main():
    audit = json.loads((ROOT / 'audit-reports/indonesian-baghdad-publication-2026-10-29.json').read_text())
    assert audit['owner_approved'] and audit['approved_reference_correction']['approved']
    for record in audit['unchanged_original_mains']:
        assert digest(mainpart((ROOT / record['path']).read_text())) == record['main_sha256'], record['path']
    for record in audit['authorized_original_changes']:
        assert digest(mainpart((ROOT / record['path']).read_text())) == record['after_main_sha256'], record['path']
    assert len(audit['unchanged_previous_id_pages']) == 3
    for record in audit['unchanged_previous_id_pages']:
        assert hashlib.sha256((ROOT / record['path']).read_bytes()).hexdigest() == record['sha256'], record['path']
    text = (ROOT / (ROUTE.lstrip('/') + 'index.html')).read_text()
    p = Content(); p.feed(mainpart(text))
    expected = {u['id']: u['translation_text_sha256'] for u in audit['units']}
    extras = {u['id']: u['text_sha256'] for u in audit['supplements']}
    assert set(expected) == {f'B{i:03}' for i in range(1, 106)}
    assert set(extras) == {'S001', 'S002'} and set(p.units) == set(expected) | set(extras)
    for uid, value in {**expected, **extras}.items(): assert digest(p.units[uid]) == value, uid
    assert compact(''.join(p.all_text)) == compact(''.join(p.units.values())), 'Unmapped author text or additions'
    for tag, count in {'h1': 1, 'h2': 16, 'h3': 7, 'p': 64, 'li': 18, 'table': 0, 'img': 0, 'blockquote': 0, 'strong': 11, 'em': 11}.items():
        assert p.counts[tag] == count, (tag, p.counts[tag], count)
    assert len(p.links) == 9 and [a['href'] for a in p.links] == audit['main_link_targets']
    refs = [p.units[f'B{i:03}'] for i in range(93, 101)]
    assert len(refs) == 8 and refs == audit['references']
    assert 'Reuven Amitai' in p.units['B099'] and 'Charles Melville' not in p.units['B099']
    assert '800 ribu' in p.units['B056'] and 'satu juta delapan ratus ribu' in p.units['B056']
    assert 'enam belas' in p.units['B056'] and 'empat riwayat asal' in p.units['B056']
    for uid in ('B073', 'B074', 'B076'): assert '«كتاب الكتب»' in p.units[uid]
    for uid in ('B024', 'B102'): assert 'الحوادث الجامعة' in p.units[uid]
    metadata = Units(); metadata.feed(text)
    article = next(n for b in metadata.blocks for n in b.get('@graph', []) if n.get('@type') == 'Article')
    assert article['citation'] == refs and article['headline'] == audit['h1']
    assert article['name'] == audit['seo_title'] and len(article['name']) == 59
    assert article['description'] == audit['meta_description'] and len(article['description']) == 145
    assert article['translationOfWork'] == {'@id': audit['source_url'] + '#article'}
    assert article['author'] == {'@id': HOST + '/#person'} and article['dateModified'] >= article['datePublished'] >= '2026-10-29'
    page = Page(); page.feed(text)
    assert page.canonical == [URL] and len(page.ids) == len(set(page.ids))
    for a in page.links:
        if a.get('href', '').startswith('#'): assert a['href'][1:] in page.ids
    assert set(page.alternates) == {'ar', 'en', 'de', 'id', 'x-default'}
    for lang in ('ar', 'en', 'de'):
        rel = page.alternates[lang].removeprefix(HOST).lstrip('/') + 'index.html'
        other = Page(); other.feed((ROOT / rel).read_text())
        assert other.alternates == page.alternates, lang + ': nonreciprocal language graph'
        assert any(a.get('hreflang') == 'id' and a.get('href') == URL for a in other.links)
    assert '<html lang="id" dir="ltr">' in text and 'content="noindex' not in text
    assert text.count('/assets/analytics-indonesia-pilot.js') == 1
    assert 'id-draft-notice' not in text and 'review-' not in text
    for a in p.links:
        if 'data-article-to-book' in a:
            assert a['data-lang'] == 'id' and a['data-article-slug'] == 'jatuhnya-baghdad-1258-ibnu-al-alqami'
            assert a['data-book-slug'] == 'kitab-al-kutub' and a['hreflang'] == 'ar'
    catalogue = Units(); catalogue.feed((ROOT / 'id/articles/index.html').read_text())
    listing = next(n for b in catalogue.blocks for n in b.get('@graph', []) if n.get('@type') == 'ItemList')
    assert listing['numberOfItems'] == len(listing['itemListElement']) == 4
    assert listing['itemListElement'][0]['url'] == URL
    feed = json.loads((ROOT / 'id/articles/feed.json').read_text())
    assert len(feed['items']) == 4 and feed['items'][0]['url'] == URL
    assert URL in (ROOT / 'sitemap.xml').read_text()
    bib = (ROOT / 'articles/fall-of-baghdad-1258-ibn-al-alqami/evidence/references.bib').read_text()
    ris = (ROOT / 'articles/fall-of-baghdad-1258-ibn-al-alqami/evidence/references.ris').read_text()
    assert 'author = {Melville, Charles}' not in bib and 'author = {Amitai, Reuven}' in bib
    assert 'AU  - Melville, Charles' not in ris and ris.count('AU  - Amitai, Reuven') == 2
    print('Indonesian Baghdad integrity passed: 105 approved units, 8 references, disclosed author correction, source argument preserved, three earlier translations unchanged, reciprocal AR/EN/DE/ID.')

if __name__ == '__main__': main()
