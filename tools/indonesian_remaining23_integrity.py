#!/usr/bin/env python3
"""Preserve the reviewed text and prior releases while validating publication."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
def sha(b):return hashlib.sha256(b).hexdigest()
def norm(s):return re.sub(r'\s+',' ',s).strip()
def main_hash(s):
    main=re.search(r'<main\b.*?</main>',s,re.S).group()
    return sha(re.sub(r'<a href="https://ahmedalhafiz\.com/id/[^"<>]+" hreflang="id">ID</a>','',main).encode())
class Reader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.depth=0;self.capture=None;self.supplement=None;self.text=[];self.ids=[];self.links=[];self.alternates={};self.blocks=[];self.ld=False;self.buffer=[];self.h1=0;self.canonical=[];self.cells=0;self.tables=0;self.lang=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag not in VOID:self.depth+=1
        if a.get('id'):self.ids.append(a['id'])
        if tag=='html':self.lang=(a.get('lang'),a.get('dir'))
        if tag=='h1':self.h1+=1
        if tag=='a':self.links.append(a)
        if 'reading-body' in a.get('class','').split():self.capture=self.depth
        if a.get('data-release-supplement') and self.capture:self.supplement=self.depth
        if self.capture and tag in ('td','th'):self.cells+=1
        if self.capture and tag=='table':self.tables+=1
        if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a['href'])
        if tag=='link' and a.get('hreflang'):self.alternates[a['hreflang']]=a['href']
        if tag=='script' and a.get('type')=='application/ld+json':self.ld=True;self.buffer=[]
    def handle_endtag(self,tag):
        if tag=='script' and self.ld:self.blocks.append(json.loads(''.join(self.buffer)));self.ld=False
        if self.depth==self.supplement:self.supplement=None
        if self.depth==self.capture:self.capture=None
        if tag not in VOID:self.depth-=1
    def handle_data(self,s):
        if self.capture and not self.supplement:self.text.append(s)
        if self.ld:self.buffer.append(s)
def check():
    a=json.loads((ROOT/'audit-reports/indonesian-remaining23-release-2026-11-02.json').read_text())
    assert a['publication_authorized'] and a['count']==23
    assert len(a['new_articles'])==23 and len({r['url'] for r in a['new_articles']})==23
    assert len(a['unchanged_previous_id_pages'])==36
    for path,expected in a['unchanged_original_mains'].items():assert main_hash((ROOT/path).read_text())==expected,path
    for path,expected in a['unchanged_previous_id_pages'].items():assert sha((ROOT/path).read_bytes())==expected,path
    for r in a['new_articles']:
        text=(ROOT/r['path']).read_text();p=Reader();p.feed(text)
        assert p.h1==1 and len(p.ids)==len(set(p.ids)),r['key']
        assert sha(norm(''.join(p.text)).encode())==r['body_text_sha256'],r['key']+' incomplete text'
        assert (p.tables,p.cells)==(r['tables'],r['table_cells']),r['key']+' table drift'
        assert p.canonical==[r['url']] and p.alternates==r['original_language_alternates'],r['key']
        assert p.lang==('id','ltr') and 'noindex' not in text.lower(),r['key']
        assert not re.search(r'naskah persiapan|belum diterbitkan|private-status|register\.json|\bTODO\b',text,re.I),r['key']+' preparation residue'
        article=next(n for b in p.blocks for n in b.get('@graph',[]) if n.get('@type')=='Article')
        assert article['headline']==r['title'] and article['datePublished']==a['date']
        assert article['translationOfWork']=={'@id':r['source_url']+'#article'}
        for lang,url in p.alternates.items():
            if lang in ('id','x-default'):continue
            q=Reader();q.feed((ROOT/(url.split('ahmedalhafiz.com/',1)[1].rstrip('/')+'/index.html')).read_text())
            assert q.alternates==p.alternates,(r['key'],lang)
        for link in p.links:
            if link.get('href','').startswith('#'):assert link['href'][1:] in p.ids,(r['key'],link)
    feed=json.loads((ROOT/'id/articles/feed.json').read_text());urls=[i['url'] for i in feed['items']]
    assert len(urls)==len(set(urls))==a['expected_id_feed_items']==59
    assert {r['url'] for r in a['new_articles']}<=set(urls)
    ns={'a':'http://www.w3.org/2005/Atom','s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    assert {e.text for e in ET.parse(ROOT/'id/articles/feed.xml').findall('a:entry/a:id',ns)}==set(urls)
    sitemap={e.text for e in ET.parse(ROOT/'sitemap.xml').findall('s:url/s:loc',ns)}
    assert len(sitemap)==a['expected_sitemap_urls']==224 and set(urls)<=sitemap
    print(f'Remaining23 gate passed:23 reviewed texts and table-cell inventories;{len(a["unchanged_original_mains"])} original mains and36 prior ID pages preserved;59 feed items and224 sitemap URLs.')
if __name__=='__main__':check()
