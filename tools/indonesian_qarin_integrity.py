#!/usr/bin/env python3
"""Protect all approved qarin-article units, references, dates and language editions."""
from pathlib import Path
import hashlib,json,re,xml.etree.ElementTree as ET
from indonesian_ratq_integrity import Content
from indonesian_pilot_integrity import Units
from indonesian_juhayman_integrity import Page
ROOT=Path(__file__).resolve().parents[1]
HOST='https://ahmedalhafiz.com';ROUTE='/id/articles/jin-qorin-islam-pikiran/';URL=HOST+ROUTE
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def mainpart(s):return re.search(r'<main\b.*?</main>',s,re.S).group()
def compact(s):return re.sub(r'\s+','',s)
def main():
    audit=json.loads((ROOT/'audit-reports/indonesian-qarin-publication-2026-10-30.json').read_text());assert audit['owner_approved']
    assert len(audit['unchanged_original_mains'])==2 and len(audit['unchanged_previous_id_pages'])==7
    for x in audit['unchanged_original_mains']:assert digest(mainpart((ROOT/x['path']).read_text()))==x['main_sha256'],x['path']
    for x in audit['unchanged_previous_id_pages']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256'],x['path']
    text=(ROOT/(ROUTE.lstrip('/')+'index.html')).read_text();p=Content();p.feed(mainpart(text))
    units={u['id']:u['translation_text_sha256'] for u in audit['units']};extras={x['id']:x['text_sha256'] for x in audit['supplements']}
    assert set(units)=={f'Q{i:03}' for i in range(1,76)} and set(extras)=={'S001','S002','S003'}
    assert set(p.units)==set(units)|set(extras)
    for uid,value in {**units,**extras}.items():assert digest(p.units[uid])==value,uid+': approved text changed'
    assert compact(''.join(p.all_text))==compact(''.join(p.units.values())),'Unmapped additions or missing content'
    for tag,count in {'p':37,'h1':1,'h2':9,'h3':1,'li':19,'img':1,'a':48,'sup':11,'strong':14,'time':1,'code':2}.items():assert p.counts[tag]==count,(tag,p.counts[tag],count)
    assert [x['href'] for x in p.links]==audit['main_link_targets']
    assert len(audit['protected_arabic_fragments'])==8
    for fragment in audit['protected_arabic_fragments']:assert fragment in ''.join(p.units.values())
    for excerpt in audit['quran_meaning_excerpts']:assert excerpt['id_excerpt'] in p.units[excerpt['unit']]
    assert 'indonesian_affairs, versi 1.0.1' in p.units['S002']
    assert 'tidaklah cermat mengatakan bahwa para ulama sepakat' in p.units['Q021']
    assert 'dalam keadaan tertentu' in p.units['Q031'] and 'tidak mendiagnosis' in p.units['Q031']
    assert 'Bab Pertama, hlm. 12' in p.units['Q056'] and '324 halaman' in p.units['Q056']
    assert '53(1):5-13' in p.units['Q054'] and 'DOI:10.1037/0022-3514.53.1.5' in p.units['Q054']
    assert '27 Oktober 2026' in p.units['Q006'] and 'belum dilakukan' in p.units['Q007']
    assert audit['publication_date_id'] in p.units['S001'] and audit['publication_date_id'] in p.units['S003'] and URL in p.units['S003']
    assert 'belum dilakukan' in p.units['Q075']
    refs=[p.units[f'Q{i:03}'] for i in range(48,57)];assert refs==audit['references'] and len(refs)==9
    page=Page();page.feed(text);assert page.canonical==[URL] and len(page.ids)==len(set(page.ids))
    for n in page.links:
        if n.get('href','').startswith('#'):assert n['href'][1:] in page.ids
    assert set(page.alternates)=={'ar','en','id','x-default'} and page.alternates['id']==URL
    for x in audit['unchanged_original_mains']:
        other=Page();other.feed((ROOT/x['path']).read_text());assert other.alternates==page.alternates
        assert any(n.get('hreflang')=='id' and n.get('href')==URL for n in other.links)
    class Attributes(Units):
        def __init__(self):super().__init__();self.labels=[];self.images=[]
        def handle_starttag(self,tag,attrs):
            a=dict(attrs)
            if tag=='a' and a.get('aria-label','').startswith('Sumber '):self.labels.append(a['aria-label'])
            if tag=='img':self.images.append(a)
            super().handle_starttag(tag,attrs)
    attrs=Attributes();attrs.feed(mainpart(text));expected=[x['id_text'] for x in audit['translated_attributes'] if x['attribute']=='aria-label' and x['ar'].startswith('المصدر ')];assert attrs.labels==expected and len(attrs.labels)==11
    assert len(attrs.images)==1 and attrs.images[0]['src']=='/umm-abbas-cover.webp' and attrs.images[0]['alt']=='Sampul novel أم عباس لجلب الحبيب وردّ المطلّقة'
    metadata=Units();metadata.feed(text);article=next(n for b in metadata.blocks for n in b.get('@graph',[]) if n.get('@type')=='Article')
    assert article['headline']==''.join(metadata.title)==audit['h1'] and article['name']==audit['seo_title']
    assert article['description']==audit['meta_description'] and article['citation']==refs and article['inLanguage']=='id'
    assert article['translationOfWork']=={'@id':audit['source_url']+'#article'} and article['datePublished']==article['dateModified']==audit['publication_date']
    assert article['author']=={'@id':HOST+'/#person'} and 'Ahmed Alhafiz' in article['name']
    assert '<html lang="id" dir="ltr">' in text and 'content="noindex' not in text
    assert text.count('/assets/analytics-indonesia-pilot.js')==1 and 'id-draft-notice' not in text
    assert not any(x in text for x in ['data:image','filecite','/workspace/','localhost','غير معتمد'])
    booklinks=[n for n in p.links if 'data-article-to-book' in n];assert len(booklinks)==4
    for n in booklinks:assert n['data-lang']=='id' and n['data-book-slug']=='umm-abbas' and n['data-article-slug']==ROUTE.rstrip('/').split('/')[-1] and n['href']==HOST+'/books/umm-abbas/' and n['hreflang']=='ar'
    catalogue=Units();catalogue.feed((ROOT/'id/articles/index.html').read_text());listing=next(n for b in catalogue.blocks for n in b.get('@graph',[]) if n.get('@type')=='ItemList')
    actual={HOST+'/'+str(p.parent.relative_to(ROOT)).replace('\\','/')+'/' for p in (ROOT/'id/articles').glob('*/index.html')};listed=[x['url'] for x in listing['itemListElement']]
    assert listing['numberOfItems']==len(listed)==len(actual)>=8 and set(listed)==actual
    assert [x['position'] for x in listing['itemListElement']]==list(range(1,len(listed)+1))
    feed=json.loads((ROOT/'id/articles/feed.json').read_text());assert {x['url'] for x in feed['items']}==actual and len(feed['items'])==len(listed)
    item=next(x for x in feed['items'] if x['url']==URL);assert item['title']==audit['h1'] and item['date_published'].startswith(audit['publication_date'])
    entries=ET.parse(ROOT/'id/articles/feed.xml').findall('{http://www.w3.org/2005/Atom}entry');assert len(entries)==len(listed)
    locations=[n.text for n in ET.parse(ROOT/'sitemap.xml').findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')];assert locations.count(URL)==1
    print('Indonesian qarin integrity passed: 75 approved units, 13 translated attributes, 9 references, reciprocal AR/EN/ID, original bodies and seven earlier ID files unchanged.')
if __name__=='__main__':main()
