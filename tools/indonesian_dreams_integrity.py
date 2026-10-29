#!/usr/bin/env python3
"""Protect all approved dream-article units, references, dates and language editions."""
from pathlib import Path
import hashlib,json,re,xml.etree.ElementTree as ET
from indonesian_ratq_integrity import Content
from indonesian_pilot_integrity import Units
from indonesian_juhayman_integrity import Page
ROOT=Path(__file__).resolve().parents[1]
HOST='https://ahmedalhafiz.com';ROUTE='/id/articles/mimpi-melihat-jin-pertanda-sihir/';URL=HOST+ROUTE
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def mainpart(s):return re.search(r'<main\b.*?</main>',s,re.S).group()
def compact(s):return re.sub(r'\s+','',s)
def main():
    audit=json.loads((ROOT/'audit-reports/indonesian-dreams-publication-2026-10-29.json').read_text());assert audit['owner_approved']
    assert len(audit['unchanged_original_mains'])==2 and len(audit['unchanged_previous_id_pages'])==6
    for x in audit['unchanged_original_mains']:assert digest(mainpart((ROOT/x['path']).read_text()))==x['main_sha256'],x['path']
    for x in audit['unchanged_previous_id_pages']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256'],x['path']
    text=(ROOT/(ROUTE.lstrip('/')+'index.html')).read_text();p=Content();p.feed(mainpart(text))
    units={u['id']:u['translation_text_sha256'] for u in audit['units']};extras={x['id']:x['text_sha256'] for x in audit['supplements']}
    assert set(units)=={f'D{i:03}' for i in range(1,81)} and set(extras)=={'S001','S002','S003'}
    assert set(p.units)==set(units)|set(extras)
    for uid,value in {**units,**extras}.items():assert digest(p.units[uid])==value,uid+': approved text changed'
    assert compact(''.join(p.all_text))==compact(''.join(p.units.values())),'Unmapped additions or missing content'
    for tag,count in {'p':43,'h1':1,'h2':9,'h3':1,'li':18,'img':1,'a':42,'sup':12,'strong':14,'time':1,'code':2}.items():assert p.counts[tag]==count,(tag,p.counts[tag],count)
    assert [x['href'] for x in p.links]==audit['main_link_targets']
    assert all(fragment in p.units[uid] for uid,fragment in [('D013','وَالرُّؤْيَا ثَلَاثَةٌ'),('D016','وَلَا تَقْفُ مَا لَيْسَ لَكَ بِهِ عِلْمٌ')])
    assert audit['quran_meaning_excerpt'] in p.units['D016'] and 'indonesian_affairs, versi 1.0.1' in p.units['S002']
    assert 'tidak cukup untuk membuktikan' in p.units['D010'] and 'tidak harus' in p.units['D013']
    assert 'tidak membuktikan' in p.units['D014'] and 'tidak menetapkan' in p.units['D014']
    assert '125 perempuan sehat' in p.units['D021'] and 'mendukung kemungkinan' in p.units['D022']
    assert 'tidak meneliti mimpi tentang jin' in p.units['D023'] and 'tidak mewakili semua orang' in p.units['D023']
    assert 'bukanlah mimpinya' not in p.units['D025'] and 'Mungkin yang paling menyakitkan bagi seseorang adalah makna' in p.units['D025']
    assert 'أم عباس لجلب الحبيب وردّ المطلّقة' in p.units['D032'] and 'Memikat Kekasih' not in p.units['D032']
    assert 'tidak memutuskan' in p.units['D028'] and 'memerlukan bukti' in p.units['D016']
    assert 'tenaga profesional' in p.units['D045'] and 'tidak dengan sendirinya' in p.units['D048']
    assert 'tidak mensyaratkan' in p.units['D044'] and 'sebelum hatinya tenang' in p.units['D044']
    assert '26 Oktober 2026' in p.units['D006'] and 'belum dilakukan' in p.units['D007']
    assert '29 Oktober 2026' in p.units['S001'] and audit['publication_date_id'] in p.units['S003'] and URL in p.units['S003']
    assert p.units['D068']=='Dalam Artikel Ini' and p.units['D079']=='Jenis Tulisan' and 'belum dilakukan' in p.units['D080']
    refs=[p.units[f'D{i:03}'] for i in range(54,62)];assert refs==audit['references'] and len(refs)==8
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
    attrs=Attributes();attrs.feed(mainpart(text));expected=[x['id_text'] for x in audit['translated_attributes'] if x['attribute']=='aria-label' and x['ar'].startswith('المصدر ')];assert attrs.labels==expected and len(attrs.labels)==12
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
    assert listing['numberOfItems']==len(listed)==len(actual)>=7 and set(listed)==actual
    assert [x['position'] for x in listing['itemListElement']]==list(range(1,len(listed)+1))
    feed=json.loads((ROOT/'id/articles/feed.json').read_text());assert {x['url'] for x in feed['items']}==actual and len(feed['items'])==len(listed)
    item=next(x for x in feed['items'] if x['url']==URL);assert item['title']==audit['h1'] and item['date_published'].startswith(audit['publication_date'])
    entries=ET.parse(ROOT/'id/articles/feed.xml').findall('{http://www.w3.org/2005/Atom}entry');assert len(entries)==len(listed)
    locations=[n.text for n in ET.parse(ROOT/'sitemap.xml').findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')];assert locations.count(URL)==1
    print('Indonesian dreams integrity passed: 80 approved units, 14 translated attributes, 8 references, reciprocal AR/EN/ID, original bodies and six earlier ID files unchanged.')
if __name__=='__main__':main()
