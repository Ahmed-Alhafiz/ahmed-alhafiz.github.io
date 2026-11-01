#!/usr/bin/env python3
"""Lock reviewed release text, preservation, indexing and language relationships."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'audit-reports/indonesian-reviewed-release-2026-11-01.json'
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
class Reader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.depth=0;self.capture=None;self.supplement=None;self.text=[];self.ids=[];self.links=[];self.alternates={};self.blocks=[];self.ld=False;self.buffer=[];self.h1=0;self.canonical=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag not in VOID:self.depth+=1
        if a.get('id'):self.ids.append(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='a':self.links.append(a)
        if 'reading-body' in a.get('class','').split():self.capture=self.depth
        if a.get('data-release-supplement') and self.capture:self.supplement=self.depth
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
def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def norm(s):return re.sub(r'\s+',' ',s).strip()
def main_hash(s):
    main=re.search(r'<main\b.*?</main>',s,re.S).group()
    return sha(re.sub(r'<a href="https://ahmedalhafiz\.com/id/[^"<>]+" hreflang="id">ID</a>','',main))
def check():
    audit=json.loads(AUDIT.read_text());assert audit['publication_authorized'] and audit['count']==27
    urls={r['url'] for r in audit['new_articles']};assert len(urls)==27
    for path,expected in audit['unchanged_original_mains'].items():assert main_hash((ROOT/path).read_text())==expected,path
    for path,expected in audit['unchanged_previous_id_pages'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
    for r in audit['new_articles']:
        text=(ROOT/r['path']).read_text();p=Reader();p.feed(text)
        assert p.h1==1 and len(p.ids)==len(set(p.ids)),r['path']
        assert sha(norm(' '.join(p.text)))==r['body_text_sha256'],r['key']+' body drift'
        assert p.canonical==[r['url']] and p.alternates==r['original_language_alternates'],r['key']
        assert 'noindex' not in text.lower() and '<html lang="id" dir="ltr">' in text
        assert '.pdf' not in ''.join(p.text) and 'Tautan dari unit sumber' not in text
        assert not re.search(r'belum disetujui|terjemahan Indonesia belum diterbitkan|terjemahan draf internal',text,re.I),r['key']+' obsolete draft metadata'
        for link in p.links:
            if link.get('href','').startswith('#'):assert link['href'][1:] in p.ids,(r['key'],link)
        article=next(n for b in p.blocks for n in b.get('@graph',[]) if n.get('@type')=='Article')
        assert article['headline']==r['title'] and article['datePublished']==audit['date']
        assert article['translationOfWork']=={'@id':r['source_url']+'#article'}
        for lang,url in p.alternates.items():
            if lang in ['id','x-default']:continue
            path=ROOT/(url.split('ahmedalhafiz.com/',1)[1].rstrip('/')+'/index.html')
            q=Reader();q.feed(path.read_text());assert q.alternates==p.alternates,(r['key'],lang)
    feed=json.loads((ROOT/'id/articles/feed.json').read_text());assert len(feed['items'])==36
    assert urls<={x['url'] for x in feed['items']}
    assert len(ET.parse(ROOT/'sitemap.xml').findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url'))==201
    print('Reviewed Indonesian release passed:27 complete reviewed texts,56 original mains,9 prior ID articles,36 feed entries,201 sitemap URLs and reciprocal languages.')
if __name__=='__main__':check()
