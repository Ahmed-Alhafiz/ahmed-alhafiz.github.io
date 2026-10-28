#!/usr/bin/env python3
"""Protect full source parity and the published Indonesian ratq/fatq edition."""
from collections import Counter
from pathlib import Path
import hashlib,json,re
from indonesian_pilot_integrity import Units

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'audit-reports/indonesian-ratq-publication-2026-10-28.json'

def digest(text):return hashlib.sha256(text.encode()).hexdigest()
def compact(text):return re.sub(r'\s+','',text)

class Content(Units):
    def __init__(self):
        super().__init__();self.all_text=[];self.counts=Counter()
    def handle_starttag(self,tag,attrs):
        self.counts[tag]+=1
        a=dict(attrs)
        if a.get('data-supplement'):attrs=list(attrs)+[('data-unit',a['data-supplement'])]
        super().handle_starttag(tag,attrs)
    def handle_data(self,text):
        self.all_text.append(text);super().handle_data(text)

def main():
    audit=json.loads(AUDIT.read_text());assert audit['owner_approved']
    for record in audit['existing_main_pages']:
        text=(ROOT/record['path']).read_text();part=re.search(r'<main\b.*?</main>',text,re.S).group()
        assert digest(part)==record['main_sha256'],record['path']+': original content changed'
    route='/id/articles/big-bang-dalam-al-quran/'
    text=(ROOT/(route.lstrip('/')+'index.html')).read_text()
    main_html=re.search(r'<main\b.*?</main>',text,re.S).group();p=Content();p.feed(main_html)
    expected={u['id']:u['translation_text_sha256'] for u in audit['units']}
    supplements={u['id']:u['text_sha256'] for u in audit['supplements']}
    assert len(expected)==106 and len(supplements)==2
    assert set(p.units)==set(expected)|set(supplements),'incomplete, duplicate or unknown units'
    for uid,value in {**expected,**supplements}.items():assert digest(p.units[uid])==value,uid+': approved text drift'
    assert compact(''.join(p.all_text))==compact(''.join(p.units.values())),'unmapped text added outside approved content'
    assert re.findall('﴿.*?﴾',''.join(p.all_text))==audit['source_quran_quotes'],'Quran Arabic changed'
    for tag,count in {'h1':1,'h2':14,'h3':4,'li':20,'table':1,'tr':4,'th':3,'td':9,'img':0}.items():assert p.counts[tag]==count,(tag,p.counts[tag],count)
    assert 'terjemahan' in text.lower() and 'indonesian_affairs' in text and 'versi 1.0.1' in text
    assert 'quran-620' in text and '[620]' in p.units['R058']
    assert 'Sungguh, Allah Mahakuasa' not in p.units['R058'],'unquoted part of original verse added'
    meta=Units();meta.feed(text)
    article=next(n for b in meta.blocks for n in b.get('@graph',[]) if n.get('@type')=='Article')
    assert article['headline']==''.join(meta.title)==audit['h1']
    assert article['translationOfWork']=={'@id':audit['source_url']+'#article'}
    assert article['author']=={'@id':'https://ahmedalhafiz.com/#person'}
    assert article['citation']==audit['references'] and len(article['citation'])==11
    assert article['datePublished']>='2026-10-28' and article['dateModified']>=article['datePublished']
    assert '<html lang="id" dir="ltr">' in text and 'content="noindex' not in text
    assert text.count('/assets/analytics-indonesia-pilot.js')==1
    assert 'href="/author.json"' in text and 'href="https://ahmedalhafiz.com/id/articles/big-bang-dalam-al-quran/"' in text
    print('Indonesian ratq/fatq integrity passed: 106 complete approved units, ten Arabic Quran quotations, full table, nine reference entries and eleven source URLs; unchanged Arabic/English main content.')

if __name__=='__main__':main()
