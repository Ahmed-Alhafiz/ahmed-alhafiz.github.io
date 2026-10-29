#!/usr/bin/env python3
"""Protect the sixth edition, evidence table, uncertainties and prior languages."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,re,xml.etree.ElementTree as ET
from indonesian_ratq_integrity import Content
from indonesian_pilot_integrity import Units
from indonesian_juhayman_integrity import Page
ROOT=Path(__file__).resolve().parents[1]
HOST='https://ahmedalhafiz.com';ROUTE='/id/articles/piramida-khufu-dibangun-catatan-merer/';URL=HOST+ROUTE
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def mainpart(s):return re.search(r'<main\b.*?</main>',s,re.S).group()
def compact(s):return re.sub(r'\s+','',s)
def main():
    audit=json.loads((ROOT/'audit-reports/indonesian-khufu-publication-2026-10-29.json').read_text());assert audit['owner_approved']
    assert len(audit['unchanged_original_mains'])==2 and len(audit['unchanged_previous_id_pages'])==5
    for x in audit['unchanged_original_mains']:assert digest(mainpart((ROOT/x['path']).read_text()))==x['main_sha256'],x['path']
    for x in audit['unchanged_previous_id_pages']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256'],x['path']
    text=(ROOT/(ROUTE.lstrip('/')+'index.html')).read_text();body=mainpart(text);p=Content();p.feed(body)
    units={u['id']:u['translation_text_sha256'] for u in audit['units']};extras={x['id']:x['text_sha256'] for x in audit['supplements']}
    assert set(units)=={f'K{i:03}' for i in range(1,99)} and set(extras)=={'S001','S002','S003'}
    assert set(p.units)==set(units)|set(extras)
    for uid,value in {**units,**extras}.items():assert digest(p.units[uid])==value,uid+': approved text changed'
    assert compact(''.join(p.all_text))==compact(''.join(p.units.values())),'Unmapped additions or missing content'
    expected={'p':34,'h1':1,'h2':14,'h3':4,'h4':1,'li':23,'th':3,'td':15,'table':1,'blockquote':1,'img':0,'a':22,'em':1,'code':1}
    for tag,count in expected.items():assert p.counts[tag]==count,(tag,p.counts[tag],count)
    assert [x['href'] for x in p.links]==audit['main_link_targets']
    assert 'sekitar empat puluh' in p.units['K021'] and 'dua atau tiga' in p.units['K021'] and 'sepuluh hari' in p.units['K021']
    assert 'tahun kedua puluh enam' in p.units['K022'] and 'mungkin' in p.units['K022'] and 'Banyak batu' in p.units['K022']
    assert 'tidak mencatat kontrak hukum setiap orang' in p.units['K054'] and 'tidak dengan sendirinya memastikan status hukum' in p.units['K081']
    assert 'besarnya armada' in p.units['K067'] and 'jalur kerja manusia' in p.units['K070']
    assert audit['quran_title_fragment'] in p.units['K098'] and audit['quran_title_meaning'] in p.units['K098']
    assert 'قل سيروا في الأرض فانظروا كيف بدأ الخلق' in p.units['K096'] and '83–84' in p.units['K096']
    assert '27 September 2026' in p.units['K006'] and 'belum' in p.units['K008']
    assert 'Tidak dapat dipastikan' in p.units['K043'] and 'Tidak disebutkan' in p.units['K042']
    refs=[p.units[f'K{i:03}'] for i in range(89,97)];assert refs==audit['references'] and len(refs)==8
    page=Page();page.feed(text);assert page.canonical==[URL] and len(page.ids)==len(set(page.ids))
    for n in page.links:
        if n.get('href','').startswith('#'):assert n['href'][1:] in page.ids
    assert set(page.alternates)=={'ar','en','id','x-default'} and page.alternates['id']==URL
    for x in audit['unchanged_original_mains']:
        other=Page();other.feed((ROOT/x['path']).read_text());assert other.alternates==page.alternates
        assert any(n.get('hreflang')=='id' and n.get('href')==URL for n in other.links)
    metadata=Units();metadata.feed(text);article=next(n for b in metadata.blocks for n in b.get('@graph',[]) if n.get('@type')=='Article')
    assert article['headline']==audit['h1'] and article['name']==audit['seo_title'] and len(article['name'])==51
    assert article['description']==audit['meta_description'] and len(article['description'])==147
    assert article['citation']==refs and article['translationOfWork']=={'@id':audit['source_url']+'#article'}
    assert article['datePublished']==article['dateModified']==audit['publication_date']
    assert audit['publication_date_id'] in p.units['S001'] and audit['publication_date_id'] in p.units['S003'] and URL in p.units['S003']
    assert '<html lang="id" dir="ltr">' in text and 'content="noindex' not in text
    assert text.count('/assets/analytics-indonesia-pilot.js')==1 and 'id-draft-notice' not in text
    assert 'data:image' not in text and 'filecite' not in text and '/workspace/' not in text
    booklinks=[n for n in p.links if 'data-article-to-book' in n];assert len(booklinks)==2
    for n in booklinks:assert n['data-lang']=='id' and n['data-book-slug']=='sirou-fi-alard' and n['data-article-slug']=='piramida-khufu-dibangun-catatan-merer' and n['href']==HOST+'/books/sirou-fi-alard/' and n['hreflang']=='ar'
    catalogue=Units();catalogue.feed((ROOT/'id/articles/index.html').read_text());listing=next(n for b in catalogue.blocks for n in b.get('@graph',[]) if n.get('@type')=='ItemList')
    actual={HOST+'/'+str(p.parent.relative_to(ROOT)).replace('\\','/')+'/' for p in (ROOT/'id/articles').glob('*/index.html')};listed=[x['url'] for x in listing['itemListElement']]
    assert listing['numberOfItems']==len(listed)==len(actual)>=6 and set(listed)==actual
    assert [x['position'] for x in listing['itemListElement']]==list(range(1,len(listed)+1))
    feed=json.loads((ROOT/'id/articles/feed.json').read_text());assert {x['url'] for x in feed['items']}==actual and len(feed['items'])==len(listed)
    item=next(x for x in feed['items'] if x['url']==URL);assert item['title']==audit['h1'] and item['date_published'].startswith(audit['publication_date'])
    entries=ET.parse(ROOT/'id/articles/feed.xml').findall('{http://www.w3.org/2005/Atom}entry');assert len(entries)==len(listed)
    assert sum(e.find('{http://www.w3.org/2005/Atom}id').text==URL for e in entries)==1
    locations=[n.text for n in ET.parse(ROOT/'sitemap.xml').findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')];assert locations.count(URL)==1
    print('Indonesian Khufu integrity passed: 98 approved units, complete 3-column/5-row evidence table, 8 references, reciprocal AR/EN/ID, original bodies and five earlier ID files unchanged.')
if __name__=='__main__':main()
