#!/usr/bin/env python3
"""Verify the approved full translation, source version, and ID release graph."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,re

ROOT=Path(__file__).resolve().parents[1]
audit=json.loads((ROOT/'audit-reports/indonesian-pilot-publication-2026-10-28.json').read_text())
class Units(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.depth=0;self.active=[];self.units={};self.ld=False;self.buf=[];self.blocks=[];self.h1=False;self.title=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a':self.links.append(a)
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:self.depth+=1
        if a.get('data-unit'):self.active.append([a['data-unit'],self.depth,[]])
        if tag=='script' and a.get('type')=='application/ld+json':self.ld=True;self.buf=[]
        if tag=='h1':self.h1=True
    def handle_endtag(self,tag):
        for unit in list(self.active):
            if unit[1]==self.depth:
                assert unit[0] not in self.units,'duplicate translation unit'
                self.units[unit[0]]=''.join(unit[2]);self.active.remove(unit)
        if tag=='script' and self.ld:self.blocks.append(json.loads(''.join(self.buf)));self.ld=False
        if tag=='h1':self.h1=False
        self.depth-=1
    def handle_data(self,data):
        for unit in self.active:unit[2].append(data)
        if self.ld:self.buf.append(data)
        if self.h1:self.title.append(data)

def digest(text):return hashlib.sha256(text.encode()).hexdigest()
def main():
    source=(ROOT/'articles/sleep-paralysis-jathoom/index.html').read_text()
    source_main=re.search(r'<main\b.*?</main>',source,re.S).group()
    assert digest(source_main)==audit['source_main_sha256'],'Arabic source changed: re-review the linked translation'
    route='/id/articles/ketindihan-melihat-sosok/'
    translated=(ROOT/(route.lstrip('/')+'index.html')).read_text();p=Units();p.feed(translated)
    expected={u['id']:u['translation_text_sha256'] for u in audit['units']}
    assert len(expected)==141 and set(p.units)==set(expected),'incomplete approved translation'
    for uid,value in p.units.items():assert digest(value)==expected[uid],f'{uid}: approved Indonesian text drift'
    article=next(n for b in p.blocks for n in b.get('@graph',[]) if n.get('@type')=='Article')
    assert article['headline']==''.join(p.title)==audit['h1'],'visible/indexed title mismatch'
    assert article['citation']==audit['references'] and len(article['citation'])==6,'reference loss'
    assert article['translationOfWork']=={'@id':audit['source_url']+'#article'},'source relation drift'
    assert article['author']=={'@id':'https://ahmedalhafiz.com/#person'},'author identity drift'
    assert article['datePublished']>='2026-10-28','Arabic date copied as translation publication'
    assert 'masih berupa draf dan belum diterbitkan' not in translated
    assert 'id-draft-notice' not in translated
    catalogue=Units();catalogue.feed((ROOT/'id/articles/index.html').read_text())
    assert any(a.get('href')=='https://ahmedalhafiz.com/articles/' and a.get('hreflang')=='ar' for a in catalogue.links),'untranslated catalogue must lead to its actual Arabic destination'
    for path in (ROOT/'id').rglob('index.html'):
        text=path.read_text()
        assert '<html lang="id" dir="ltr">' in text,str(path)
        assert 'content="noindex' not in text,str(path)
        assert 'hreflang="id"' in text,str(path)
        assert text.count('/assets/analytics-indonesia-pilot.js')==1,str(path)
        assert 'href="/author.json"' in text,str(path)
    print('Indonesian release integrity passed: all 141 approved units, unchanged Arabic source, six references and all current complete locale pages.')
if __name__=='__main__':main()
