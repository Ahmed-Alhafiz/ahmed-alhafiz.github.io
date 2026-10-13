#!/usr/bin/env python3
"""Audit translation structure; matching counts are not proof of semantic fidelity.

Use --slug for a required gate on one article. Without it, print a queue of
structural discrepancies across article-body pages; legacy layouts are listed
as unassessed, never silently counted as passes.
"""
from pathlib import Path
import argparse,json,re,subprocess,hashlib
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[1]
TAGS=('h2','h3','p','table','td','th','ol','ul','li','blockquote','figure')

class Body(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.counts=dict.fromkeys(TAGS,0);self.urls=[];self.blocks=[]
        self.open_blocks=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag in self.counts:self.counts[tag]+=1
        if tag in ('h2','h3','p','li'):
            block={'tag':tag,'text':'','urls':[]};self.blocks.append(block);self.open_blocks.append(block)
        if tag=='a':
            url=attrs.get('href','')
            if url.startswith(('http://','https://')) and 'ahmedalhafiz.com' not in url:
                self.urls.append(url)
                for b in self.open_blocks:b['urls'].append(url)
    def handle_data(self,data):
        for b in self.open_blocks:b['text']+=data
    def handle_endtag(self,tag):
        if self.open_blocks and self.open_blocks[-1]['tag']==tag:self.open_blocks.pop()

def extract(source):
    m=re.search(r'<article\b[^>]*class=["\'][^"\']*\barticle-body\b[^"\']*["\'][^>]*>.*?</article>',source,re.S)
    return m.group() if m else None

def audit(slug,base=None):
    ap=ROOT/'articles'/slug/'index.html';ep=ROOT/'en/articles'/slug/'index.html'
    if not ap.exists() or not ep.exists():return {'slug':slug,'status':'missing_edition'}
    ar=extract(ap.read_text());en=extract(ep.read_text())
    if ar is None or en is None:return {'slug':slug,'status':'unassessed_legacy_layout'}
    a=Body();a.feed(ar);e=Body();e.feed(en);issues=[]
    counts={t:[a.counts[t],e.counts[t]] for t in TAGS}
    if a.counts!=e.counts:issues.append('element_counts')
    if a.urls!=e.urls:issues.append('external_source_url_sequence')
    if len(a.blocks)!=len(e.blocks):issues.append('block_count')
    else:
        for i,(x,y) in enumerate(zip(a.blocks,e.blocks)):
            if x['tag']!=y['tag']:issues.append(f'block_{i}_tag')
            if x['urls']!=y['urls']:issues.append(f'block_{i}_sources')
            nums=lambda text:re.findall(r'\d+(?:\.\d+)?',text.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩','0123456789')))
            if nums(x['text'])!=nums(y['text']):issues.append(f'block_{i}_numbers')
    unchanged=None
    if base:
        old=subprocess.check_output(['git','show',f'{base}:articles/{slug}/index.html'],cwd=ROOT,text=True)
        unchanged=extract(old)==ar
        if not unchanged:issues.append('arabic_body_changed')
    return {'slug':slug,'status':'structural_match' if not issues else 'needs_review','counts_ar_en':counts,'external_url_count_ar_en':[len(a.urls),len(e.urls)],'issues':issues,'ar_body_unchanged':unchanged,'ar_body_sha256':hashlib.sha256(ar.encode()).hexdigest(),'semantic_fidelity':'requires_full_bilingual_reading'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--slug');p.add_argument('--base');args=p.parse_args()
    slugs=[args.slug] if args.slug else sorted(x.parent.name for x in (ROOT/'en/articles').glob('*/index.html'))
    result=[audit(slug,args.base) for slug in slugs];print(json.dumps(result,ensure_ascii=False,indent=2))
    if args.slug and result[0]['status']!='structural_match':raise SystemExit(1)

if __name__=='__main__':main()
