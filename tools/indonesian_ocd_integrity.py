#!/usr/bin/env python3
"""Protect complete medical-guide translation, source bodies and discovery links."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,re,xml.etree.ElementTree as ET
from indonesian_ratq_integrity import Content
from indonesian_juhayman_integrity import Page
from indonesian_pilot_integrity import Units

ROOT=Path(__file__).resolve().parents[1]
HOST='https://ahmedalhafiz.com'
ROUTE='/id/articles/waswas-ibadah-ocd/'
URL=HOST+ROUTE

def digest(text):return hashlib.sha256(text.encode()).hexdigest()
def mainpart(text):return re.search(r'<main\b.*?</main>',text,re.S).group()
def compact(text):return re.sub(r'\s+','',text)

def main():
    audit=json.loads((ROOT/'audit-reports/indonesian-ocd-publication-2026-11-01.json').read_text())
    assert audit['publication_authorized'] and not audit['owner_approved']
    assert len(audit['unchanged_original_mains'])==2 and len(audit['unchanged_previous_id_pages'])==8
    for original in audit['unchanged_original_mains']:
        assert digest(mainpart((ROOT/original['path']).read_text()))==original['main_sha256'],original['path']
    for previous in audit['unchanged_previous_id_pages']:
        assert hashlib.sha256((ROOT/previous['path']).read_bytes()).hexdigest()==previous['sha256'],previous['path']
    text=(ROOT/(ROUTE.lstrip('/')+'index.html')).read_text();content=Content();content.feed(mainpart(text))
    units={u['id']:u['translation_text_sha256'] for u in audit['units']}
    supplements={u['id']:u['text_sha256'] for u in audit['supplements']}
    assert set(units)=={f'O{i:03}' for i in range(1,85)} and set(supplements)=={'S001','S002'}
    assert set(content.units)==set(units)|set(supplements)
    for uid,expected in {**units,**supplements}.items():assert digest(content.units[uid])==expected,uid
    assert compact(''.join(content.all_text))==compact(''.join(content.units.values())),'Missing or unmapped text'
    assert [link['href'] for link in content.links]==audit['main_link_targets']
    assert content.counts['table']==1 and content.counts['th']==2 and content.counts['td']==10
    assert content.counts['time']==2 and content.counts['h1']==1 and content.counts['img']==0
    assert 'bukan untuk mendiagnosis individu tertentu' in content.units['O011']
    assert 'Jangan menghentikan obat atau mengubah dosis' in content.units['O011']
    assert 'tidak membuktikan diagnosis' in content.units['O044']
    assert 'bukan memaksa seseorang melanggar agamanya' in content.units['O054']
    assert 'Jangan memulai, menghentikan, atau mengubah dosis obat tanpa dokter' in content.units['O056']
    assert '100%' in content.units['O035']
    assert '26 September 2026' in content.units['O006'] and '27 Oktober 2026' in content.units['O009']
    assert audit['publication_date_id'] in content.units['S001'] and audit['publication_date_id'] in content.units['S002']
    refs=[content.units[f'O{i:03}'] for i in range(67,74)];assert refs==audit['references'] and len(refs)==7
    page=Page();page.feed(text);assert page.canonical==[URL] and len(page.ids)==len(set(page.ids))
    assert set(page.alternates)=={'ar','en','id','x-default'} and page.alternates['id']==URL
    for anchor in page.links:
        if anchor.get('href','').startswith('#'):assert anchor['href'][1:] in page.ids
    for original in audit['unchanged_original_mains']:
        other=Page();other.feed((ROOT/original['path']).read_text());assert other.alternates==page.alternates
        assert any(a.get('hreflang')=='id' and a.get('href')==URL for a in other.links)
    metadata=Units();metadata.feed(text)
    article=next(n for graph in metadata.blocks for n in graph.get('@graph',[]) if n.get('@type')=='Article')
    assert article['citation']==refs and article['datePublished']==audit['publication_date']
    assert article['translationOfWork']=={'@id':audit['source_url']+'#article'} and article['inLanguage']=='id'
    inventory=json.loads((ROOT/'data/content-inventory.json').read_text());item=next(x for x in inventory['items'] if x['slug']=='religious-ocd-scrupulosity');assert item['indonesian_url']==URL and 'id' in item['languages']
    feed=json.loads((ROOT/'id/articles/feed.json').read_text());actual={HOST+'/'+str(p.parent.relative_to(ROOT)).strip('/')+'/' for p in [* (ROOT/'id/articles').glob('*/index.html'),* (ROOT/'id/guides').glob('*/index.html')]}
    assert {i['url'] for i in feed['items']}==actual
    item=next(i for i in feed['items'] if i['url']==URL);assert item['title']==audit['h1'] and item['date_published'].startswith(audit['publication_date'])
    assert len(ET.parse(ROOT/'id/articles/feed.xml').findall('{http://www.w3.org/2005/Atom}entry'))==len(actual)
    locations=[n.text for n in ET.parse(ROOT/'sitemap.xml').findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')];assert locations.count(URL)==1
    assert 'noindex' not in text.lower() and 'lang="id"' in text and 'dir="ltr"' in text
    print('Indonesian OCD integrity passed: 84 complete units, 7 references, 5x2 table, medical qualifications, AR/EN bodies and eight prior ID editions preserved.')

if __name__=='__main__':main()
