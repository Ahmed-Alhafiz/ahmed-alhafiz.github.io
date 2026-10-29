#!/usr/bin/env python3
"""Protect the approved fifth text, quotations, references and existing editions."""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import urljoin
import hashlib,json,re,xml.etree.ElementTree as ET
from indonesian_ratq_integrity import Content
from indonesian_pilot_integrity import Units
from indonesian_juhayman_integrity import Page

ROOT=Path(__file__).resolve().parents[1]
HOST='https://ahmedalhafiz.com'
ROUTE='/id/articles/kitab-syamsul-maarif-hukum-membaca/'
URL=HOST+ROUTE
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def mainpart(s):return re.search(r'<main\b.*?</main>',s,re.S).group()
def compact(s):return re.sub(r'\s+','',s)
class Attributes(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.nodes=[]
    def handle_starttag(self,tag,attrs):self.nodes.append((tag,dict(attrs)))

def main():
    audit=json.loads((ROOT/'audit-reports/indonesian-shams-publication-2026-10-29.json').read_text());assert audit['owner_approved']
    assert len(audit['unchanged_original_mains'])==2 and len(audit['unchanged_previous_id_pages'])==4
    for x in audit['unchanged_original_mains']:assert digest(mainpart((ROOT/x['path']).read_text()))==x['main_sha256'],x['path']
    for x in audit['unchanged_previous_id_pages']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256'],x['path']
    text=(ROOT/(ROUTE.lstrip('/')+'index.html')).read_text();body=mainpart(text);p=Content();p.feed(body)
    units={u['id']:u['translation_text_sha256'] for u in audit['units']};extras={s['id']:s['text_sha256'] for s in audit['supplements']}
    assert set(units)=={f'M{i:03}' for i in range(1,92)} and set(extras)=={'S001','S002','S003'}
    assert set(p.units)==set(units)|set(extras)
    for uid,value in {**units,**extras}.items():assert digest(p.units[uid])==value,uid+': approved text changed'
    assert compact(''.join(p.all_text))==compact(''.join(p.units.values())),'unmapped additions or missing text'
    for tag,count in {'h1':1,'h2':9,'h3':1,'p':53,'li':19,'ol':2,'img':1,'blockquote':5,'table':0,'strong':6,'em':4,'code':2}.items():assert p.counts[tag]==count,(tag,p.counts[tag])
    assert len(p.links)==43 and [n['href'] for n in p.links]==audit['main_link_targets']
    att=Attributes();att.feed(body);attrs=[a for tag,a in att.nodes]
    labels=Counter(a['aria-label'] for a in attrs if re.fullmatch(r'Sumber \d+',a.get('aria-label','')))
    expected_labels=Counter(x['id_text'] for x in audit['attributes'] if x['attribute']=='aria-label' and x['id_text'].startswith('Sumber '))
    assert labels==expected_labels and sum(labels.values())==13
    assert [a['alt'] for tag,a in att.nodes if tag=='img']==[next(x['id_text'] for x in audit['attributes'] if x['attribute']=='alt')]
    assert any(tag=='nav' and a.get('aria-label')=='Daftar isi artikel' for tag,a in att.nodes)
    assert [re.search(r'﴿.*?﴾',p.units[x['unit']]).group() for x in audit['quran_quotes']]==[re.search(r'﴿.*?﴾',x['ar']).group() for x in audit['quran_quotes']]
    assert audit['hadith_quote'] in p.units['M030'] and '2200' in p.units['M030']
    for x in audit['quran_meanings']['excerpts']:assert x['id_excerpt'] in p.units[x['unit']]
    assert '147' in p.units['M043'] and '137' in p.units['M045'] and 'tidak menemukan efek utama' in p.units['M045']
    assert 'Tidak satu pun dari keduanya menguji Syamsul Ma’arif' in p.units['M046'] and 'dalam fatwa ini' in p.units['M023']
    assert 'Sepuluh video' in p.units['M051'] and 'sepuluh kesaksian' in p.units['M051']
    assert '«أم عباس لجلب الحبيب وردّ المطلّقة»' in p.units['M018'] and 'كتاب شمس المعارف: حقيقته وحكم قراءته' in p.units['M077']
    assert '26 Oktober 2026' in p.units['M006'] and audit['source_url'] in p.units['M077']
    assert audit['publication_date_id'] in p.units['S001'] and audit['publication_date_id'] in p.units['S003'] and URL in p.units['S003']
    assert 'indonesian_affairs, versi 1.0.1' in p.units['S002']
    refs=[p.units[f'M{i:03}'] for i in range(64,73)];assert len(refs)==9 and refs==audit['references']
    page=Page();page.feed(text);assert page.canonical==[URL] and len(page.ids)==len(set(page.ids))
    for n in page.links:
        if n.get('href','').startswith('#'):assert n['href'][1:] in page.ids
    assert set(page.alternates)=={'ar','en','id','x-default'} and page.alternates['id']==URL
    for x in audit['unchanged_original_mains']:
        other=Page();other.feed((ROOT/x['path']).read_text());assert other.alternates==page.alternates
        assert any(n.get('hreflang')=='id' and n.get('href')==URL for n in other.links)
    metadata=Units();metadata.feed(text);article=next(n for b in metadata.blocks for n in b.get('@graph',[]) if n.get('@type')=='Article')
    assert article['headline']==audit['h1'] and article['name']==audit['seo_title'] and len(article['name'])==54
    assert article['description']==audit['meta_description'] and len(article['description'])==146
    assert article['citation']==refs and article['author']=={'@id':HOST+'/#person'}
    assert article['translationOfWork']=={'@id':audit['source_url']+'#article'}
    assert article['datePublished']==article['dateModified']==audit['publication_date']
    assert '<html lang="id" dir="ltr">' in text and 'content="noindex' not in text
    assert text.count('/assets/analytics-indonesia-pilot.js')==1 and 'id-draft-notice' not in text
    assert 'data:image' not in text and 'filecite' not in text and '/workspace/' not in text
    booklinks=[n for n in p.links if 'data-article-to-book' in n];assert len(booklinks)==3
    for n in booklinks:
        assert n['data-lang']=='id' and n['data-article-slug']=='kitab-syamsul-maarif-hukum-membaca' and n['data-book-slug']=='umm-abbas'
        assert n['href']==HOST+'/books/umm-abbas/' and n['hreflang']=='ar'
    assert hashlib.sha256((ROOT/'umm-abbas-cover.webp').read_bytes()).hexdigest()==audit['cover_sha256']
    catalogue=Units();catalogue.feed((ROOT/'id/articles/index.html').read_text());listing=next(n for b in catalogue.blocks for n in b.get('@graph',[]) if n.get('@type')=='ItemList')
    expected_urls={HOST+'/'+str(p.parent.relative_to(ROOT)).replace('\\','/')+'/' for p in (ROOT/'id/articles').glob('*/index.html')}
    listed=[x['url'] for x in listing['itemListElement']]
    assert listing['numberOfItems']==len(listed)==len(expected_urls)>=5 and set(listed)==expected_urls
    assert [x['position'] for x in listing['itemListElement']]==list(range(1,len(listed)+1))
    feed=json.loads((ROOT/'id/articles/feed.json').read_text());assert len(feed['items'])==len(listed)
    assert {x['url'] for x in feed['items']}==expected_urls
    item=next(x for x in feed['items'] if x['url']==URL);assert item['title']==audit['h1'] and item['date_published'].startswith(audit['publication_date'])
    atom=ET.parse(ROOT/'id/articles/feed.xml');entries=atom.findall('{http://www.w3.org/2005/Atom}entry');assert len(entries)==len(listed)
    assert sum(e.find('{http://www.w3.org/2005/Atom}id').text==URL for e in entries)==1
    sitemap=ET.parse(ROOT/'sitemap.xml');locations=[n.text for n in sitemap.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')];assert locations.count(URL)==1
    print('Indonesian Shams integrity passed: 91 approved units, 15 translated attributes, 4 Quran fragments and 1 hadith, 9 references, reciprocal AR/EN/ID, original bodies and four earlier ID files unchanged.')

if __name__=='__main__':main()
