#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TODAY = '2026-09-06'

PAGES = {
    'articles/ratq-fatq-big-bang/evidence/index.html': 'https://ahmed-alhafiz.github.io/assets/figures/ratq-evidence-map-ar.svg',
    'en/articles/ratq-fatq-big-bang/evidence/index.html': 'https://ahmed-alhafiz.github.io/assets/figures/ratq-evidence-map-en.svg',
}

for rel, image_url in PAGES.items():
    path = ROOT / rel
    text = path.read_text(encoding='utf-8')
    old_date = '"dateModified":"2026-09-02"'
    if text.count(old_date) != 1:
        raise SystemExit(f'{rel}: expected exactly one old dateModified, found {text.count(old_date)}')
    text = text.replace(old_date, f'"dateModified":"{TODAY}"', 1)

    marker = '"creativeWorkStatus":"Author review complete; external specialist review not completed","isPartOf":'
    if text.count(marker) != 1:
        raise SystemExit(f'{rel}: expected exactly one Article insertion marker, found {text.count(marker)}')
    image = f'"creativeWorkStatus":"Author review complete; external specialist review not completed","image":{{"@type":"ImageObject","url":"{image_url}","width":1200,"height":760}},"isPartOf":'
    text = text.replace(marker, image, 1)
    path.write_text(text, encoding='utf-8')

sitemap = ROOT / 'sitemap.xml'
sm = sitemap.read_text(encoding='utf-8')
for url in [
    'https://ahmed-alhafiz.github.io/articles/ratq-fatq-big-bang/evidence/',
    'https://ahmed-alhafiz.github.io/en/articles/ratq-fatq-big-bang/evidence/',
]:
    old = f'<url><loc>{url}</loc><lastmod>2026-09-02</lastmod></url>'
    new = f'<url><loc>{url}</loc><lastmod>{TODAY}</lastmod></url>'
    if sm.count(old) != 1:
        raise SystemExit(f'sitemap: expected exactly one old row for {url}, found {sm.count(old)}')
    sm = sm.replace(old, new, 1)
sitemap.write_text(sm, encoding='utf-8')

audit = ROOT / 'tools/site_audit.py'
a = audit.read_text(encoding='utf-8')
old = """                value=node.get('mainContentOfPage')
                target_id=value.get('@id') if isinstance(value,dict) else value if isinstance(value,str) else ''
                if isinstance(target_id,str) and target_id.endswith('#article'):
                    errors.append(f'{rel}: mainContentOfPage points to an Article; use mainEntity instead')
"""
new = """                typ=node.get('@type')
                node_types=set(typ) if isinstance(typ,list) else {typ}
                if 'Article' in node_types and not node.get('image'):
                    errors.append(f'{rel}: Article structured data missing image')
                value=node.get('mainContentOfPage')
                target_id=value.get('@id') if isinstance(value,dict) else value if isinstance(value,str) else ''
                if isinstance(target_id,str) and target_id.endswith('#article'):
                    errors.append(f'{rel}: mainContentOfPage points to an Article; use mainEntity instead')
"""
if a.count(old) != 1:
    raise SystemExit(f'site_audit.py: expected one insertion block, found {a.count(old)}')
a = a.replace(old, new, 1)
audit.write_text(a, encoding='utf-8')

print('Applied exact Article image structured-data fix to 2 evidence pages, synced sitemap lastmod, and added regression gate.')
