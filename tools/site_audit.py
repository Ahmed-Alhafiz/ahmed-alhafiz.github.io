#!/usr/bin/env python3
"""Repository-wide audit for Ahmed Alhafiz's static author and research site.

Standard-library only. The audit checks parseability, canonical/sitemap coverage,
internal links, accessibility basics, language alternates, structured data,
feed/manifest integrity, and publication-safety rules for forthcoming books.
"""
from __future__ import annotations
import argparse, json, re, sys, xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

BASE='https://ahmed-alhafiz.github.io'
EXCLUDED={'404.html'}

@dataclass
class Page:
    path:Path
    lang:str=''; direction:str=''; title:str=''; description:str=''; robots:str=''; canonical:str=''
    h1:int=0; hrefs:list[str]=field(default_factory=list); images:list[dict]=field(default_factory=list)
    jsonld_raw:list[str]=field(default_factory=list); alternates:dict[str,str]=field(default_factory=dict)
    blank_rel_errors:int=0; text:list[str]=field(default_factory=list)

class Parser(HTMLParser):
    def __init__(self,path:Path):
        super().__init__(convert_charrefs=True); self.p=Page(path); self.title_on=False; self.json_on=False; self.buf=[]; self.ignore=0
    def attrs(self,a): return {k.lower():(v or '') for k,v in a}
    def handle_starttag(self,tag,attrs):
        tag=tag.lower(); a=self.attrs(attrs)
        if tag=='html': self.p.lang=a.get('lang',''); self.p.direction=a.get('dir','')
        elif tag=='title': self.title_on=True
        elif tag=='meta':
            if a.get('name','').lower()=='description': self.p.description=a.get('content','').strip()
            if a.get('name','').lower()=='robots': self.p.robots=a.get('content','').lower()
        elif tag=='link':
            rel=set(a.get('rel','').lower().split())
            if 'canonical' in rel: self.p.canonical=a.get('href','').strip()
            if 'alternate' in rel and a.get('hreflang'): self.p.alternates[a['hreflang'].lower()]=a.get('href','').strip()
        elif tag=='h1': self.p.h1+=1
        elif tag=='a':
            if a.get('href'): self.p.hrefs.append(a['href'].strip())
            if a.get('target','').lower()=='_blank' and 'noopener' not in set(a.get('rel','').lower().split()): self.p.blank_rel_errors+=1
        elif tag=='img': self.p.images.append(a)
        elif tag=='script':
            if a.get('type','').lower()=='application/ld+json': self.json_on=True; self.buf=[]
            else: self.ignore+=1
        elif tag in {'style','noscript'}: self.ignore+=1
    def handle_endtag(self,tag):
        tag=tag.lower()
        if tag=='title': self.title_on=False
        elif tag=='script' and self.json_on:
            raw=''.join(self.buf).strip(); self.json_on=False; self.buf=[]
            if raw:self.p.jsonld_raw.append(raw)
        elif tag in {'script','style','noscript'} and self.ignore:self.ignore-=1
    def handle_data(self,data):
        if self.title_on:self.p.title+=data
        if self.json_on:self.buf.append(data)
        elif not self.ignore and data.strip():self.p.text.append(data.strip())

def parse(path:Path)->Page:
    q=Parser(path); q.feed(path.read_text(encoding='utf-8')); q.close(); q.p.title=re.sub(r'\s+',' ',q.p.title).strip()
    for raw in q.p.jsonld_raw: json.loads(raw)
    return q.p

def expected(root:Path,path:Path)->str|None:
    rel=path.relative_to(root).as_posix()
    if rel in EXCLUDED or path.name.startswith('google'): return None
    if rel=='index.html':return BASE+'/'
    if path.name=='index.html':return BASE+'/'+path.parent.relative_to(root).as_posix().strip('/')+'/'
    return BASE+'/'+rel

def target(root:Path,page:Path,href:str)->Path|None:
    u=urlsplit(href)
    if u.scheme or u.netloc or href.startswith(('mailto:','tel:','javascript:','data:','#')):return None
    raw=unquote(u.path)
    if not raw:return None
    p=(root/raw.lstrip('/')) if raw.startswith('/') else (page.parent/raw)
    if raw.endswith('/') or p.is_dir():p=p/'index.html'
    return p.resolve()

def site_path(root:Path,url:str)->Path|None:
    u=urlsplit(url)
    if f'{u.scheme}://{u.netloc}'!=BASE:return None
    rel=unquote(u.path).lstrip('/')
    if not rel:return root/'index.html'
    p=root/rel
    if u.path.endswith('/'):p=p/'index.html'
    return p

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default=str(Path(__file__).resolve().parents[1])); ap.add_argument('--partial',action='store_true'); args=ap.parse_args()
    root=Path(args.root).resolve(); errors=[]; warnings=[]; pages={}; canonical_map={}
    htmls=sorted(p for p in root.rglob('*.html') if '.git' not in p.parts and p.relative_to(root).as_posix() not in EXCLUDED and not p.name.startswith('google'))
    for p in htmls:
        rel=p.relative_to(root)
        try:q=parse(p)
        except Exception as e:errors.append(f'{rel}: parse failure: {e}');continue
        pages[p.resolve()]=q; exp=expected(root,p)
        if not q.lang:errors.append(f'{rel}: missing html lang')
        if q.lang=='ar' and q.direction!='rtl':errors.append(f'{rel}: Arabic page missing dir=rtl')
        if q.lang=='en' and q.direction not in {'ltr',''}:errors.append(f'{rel}: English page has invalid direction')
        if not q.title:errors.append(f'{rel}: missing title')
        elif not 20<=len(q.title)<=95:warnings.append(f'{rel}: title length {len(q.title)}')
        if not q.description:errors.append(f'{rel}: missing description')
        elif not 65<=len(q.description)<=190:warnings.append(f'{rel}: description length {len(q.description)}')
        if q.h1!=1:errors.append(f'{rel}: expected one H1, found {q.h1}')
        if 'index' not in q.robots:errors.append(f'{rel}: robots does not explicitly allow indexing')
        if not q.canonical:errors.append(f'{rel}: missing canonical')
        elif exp and q.canonical!=exp:errors.append(f'{rel}: canonical mismatch {q.canonical} != {exp}')
        if q.canonical in canonical_map and canonical_map[q.canonical]!=p:errors.append(f'{rel}: duplicate canonical with {canonical_map[q.canonical].relative_to(root)}')
        canonical_map[q.canonical]=p
        if not q.jsonld_raw:errors.append(f'{rel}: missing JSON-LD')
        if q.blank_rel_errors:errors.append(f'{rel}: {q.blank_rel_errors} target=_blank links lack noopener')
        for i,img in enumerate(q.images,1):
            if not img.get('alt','').strip():errors.append(f'{rel}: image {i} missing alt')
            if not img.get('width') or not img.get('height'):warnings.append(f'{rel}: image {i} missing width/height')
        # Forthcoming-book pages must not publish unstable bibliographic claims.
        if rel.as_posix().startswith(('books/','en/books/','de/books/')):
            source=p.read_text(encoding='utf-8').lower()
            forbidden=('9789948639251','دار غراب','دار هاوس','house 101','house101','available now','اشتر الآن','شراء الآن')
            for token in forbidden:
                if token in source:errors.append(f'{rel}: unstable publication marker exposed: {token}')
            if re.search(r'\b97[89][0-9\- ]{10,17}\b',source):errors.append(f'{rel}: ISBN-like number exposed on forthcoming page')
        # Paired research architecture.
        paired={
          'articles/index.html':('en','https://ahmed-alhafiz.github.io/en/articles/'),
          'methodology/index.html':('en','https://ahmed-alhafiz.github.io/en/methodology/'),
          'research-status/index.html':('en','https://ahmed-alhafiz.github.io/en/research-status/'),
          'articles/ratq-fatq-big-bang/index.html':('en','https://ahmed-alhafiz.github.io/en/articles/ratq-fatq-big-bang/'),
          'articles/ratq-fatq-big-bang/evidence/index.html':('en','https://ahmed-alhafiz.github.io/en/articles/ratq-fatq-big-bang/evidence/'),
          'en/articles/index.html':('ar','https://ahmed-alhafiz.github.io/articles/'),
          'en/methodology/index.html':('ar','https://ahmed-alhafiz.github.io/methodology/'),
          'en/research-status/index.html':('ar','https://ahmed-alhafiz.github.io/research-status/'),
          'en/articles/ratq-fatq-big-bang/index.html':('ar','https://ahmed-alhafiz.github.io/articles/ratq-fatq-big-bang/'),
          'en/articles/ratq-fatq-big-bang/evidence/index.html':('ar','https://ahmed-alhafiz.github.io/articles/ratq-fatq-big-bang/evidence/'),
        }
        if rel.as_posix() in paired:
            code,url=paired[rel.as_posix()]
            if q.alternates.get(code)!=url:errors.append(f'{rel}: missing/incorrect hreflang {code}')

    for p,q in pages.items():
        for h in q.hrefs:
            t=target(root,p,h)
            if t is not None and not t.exists():
                (warnings if args.partial else errors).append(f'{p.relative_to(root)}: broken local link {h} -> {t.relative_to(root) if t.is_relative_to(root) else t}')

    # Sitemap coverage and validity.
    sm=root/'sitemap.xml'; urls=set()
    if sm.exists():
        try:
            tree=ET.parse(sm); ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
            urls={n.text.strip() for n in tree.findall('s:url/s:loc',ns) if n.text}
        except Exception as e:errors.append(f'sitemap.xml: {e}')
    elif not args.partial:errors.append('sitemap.xml missing')
    for p,q in pages.items():
        if q.canonical and q.canonical not in urls:errors.append(f'{p.relative_to(root)}: canonical absent from sitemap')
    for u in urls:
        p=site_path(root,u)
        if p is not None and not p.exists():(warnings if args.partial else errors).append(f'sitemap.xml: no local page for {u}')

    # XML/JSON feeds and manifest.
    for f in ['articles/feed.xml','en/articles/feed.xml']:
        p=root/f
        if not p.exists():errors.append(f'{f}: missing')
        else:
            try:ET.parse(p)
            except Exception as e:errors.append(f'{f}: invalid XML: {e}')
    for f in ['articles/feed.json','en/articles/feed.json','articles/research-index.json','articles/ratq-fatq-big-bang/evidence/claims.json']:
        p=root/f
        if not p.exists():errors.append(f'{f}: missing')
        else:
            try:json.loads(p.read_text(encoding='utf-8'))
            except Exception as e:errors.append(f'{f}: invalid JSON: {e}')
    if not (root/'CITATION.cff').exists():errors.append('CITATION.cff missing')

    robots=(root/'robots.txt').read_text(encoding='utf-8') if (root/'robots.txt').exists() else ''
    for token in ['OAI-SearchBot','GPTBot','Sitemap: https://ahmed-alhafiz.github.io/sitemap.xml']:
        if token not in robots:errors.append(f'robots.txt missing {token}')

    # No temporary release machinery may remain in a public branch.
    for pattern in ['.github/*trigger*','.github/*manifest*','.github/workflows/finalize-*.yml','.github/workflows/apply-*.yml']:
        for p in root.glob(pattern):errors.append(f'{p.relative_to(root)}: temporary release machinery must be removed')

    print('=== Site Integrity Audit ===')
    print(f'html_pages: {len(pages)}\ncanonicals: {len(canonical_map)}\nsitemap_urls: {len(urls)}\nerrors: {len(errors)}\nwarnings: {len(warnings)}')
    if warnings:
        print('\nWARNINGS'); [print('-',x) for x in warnings]
    if errors:
        print('\nERRORS'); [print('-',x) for x in errors]; return 1
    print('\nPASS: no blocking integrity errors'); return 0
if __name__=='__main__':sys.exit(main())
