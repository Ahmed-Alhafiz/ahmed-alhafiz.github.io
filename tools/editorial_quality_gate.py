#!/usr/bin/env python3
"""Evidence, transparency, safety, and bilingual-depth gate for public research."""
from __future__ import annotations
import json,re,sys,xml.etree.ElementTree as ET
from dataclasses import dataclass,field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
BASE='https://ahmed-alhafiz.github.io'

RULES={
 'articles/ratq-fatq-big-bang/index.html':dict(words=2800,sources=12,book='books/sirou-fi-alard/index.html',route='/articles/ratq-fatq-big-bang/',medical=False,extended=True),
 'en/articles/ratq-fatq-big-bang/index.html':dict(words=2500,sources=12,book='en/books/sirou-fi-alard/index.html',route='/en/articles/ratq-fatq-big-bang/',medical=False,extended=True),
 'articles/water-civilization-power/index.html':dict(words=3600,sources=18,book='books/sirou-fi-alard/index.html',route='/articles/water-civilization-power/',medical=False,extended=True),
 'en/articles/water-civilization-power/index.html':dict(words=4000,sources=18,book='en/books/sirou-fi-alard/index.html',route='/en/articles/water-civilization-power/',medical=False,extended=True),
 'articles/diagnostic-uncertainty-family-fear-coercive-authority/index.html':dict(words=3200,sources=15,book='books/umm-abbas/index.html',route='/articles/diagnostic-uncertainty-family-fear-coercive-authority/',medical=True,extended=True),
 'en/articles/diagnostic-uncertainty-family-fear-coercive-authority/index.html':dict(words=3600,sources=15,book='en/books/umm-abbas/index.html',route='/en/articles/diagnostic-uncertainty-family-fear-coercive-authority/',medical=True,extended=True),
 'articles/teaching-names-ai-understanding/index.html':dict(words=3500,sources=20,book='books/sirou-fi-alard/index.html',route='/articles/teaching-names-ai-understanding/',medical=False,extended=True),
 'en/articles/teaching-names-ai-understanding/index.html':dict(words=3000,sources=20,book='en/books/sirou-fi-alard/index.html',route='/en/articles/teaching-names-ai-understanding/',medical=False,extended=True),
 'articles/spiritual-healing-exploitation-safeguarding/index.html':dict(words=2350,sources=10,book='books/umm-abbas/index.html',route='/articles/spiritual-healing-exploitation-safeguarding/',medical=True,extended=False),
 'articles/six-days-creation-cosmic-time/index.html':dict(words=2100,sources=8,book='books/sirou-fi-alard/index.html',route='/articles/six-days-creation-cosmic-time/',medical=False,extended=False),
 'articles/sleep-paralysis-jathoom/index.html':dict(words=1800,sources=5,book='books/umm-abbas/index.html',route='/articles/sleep-paralysis-jathoom/',medical=True,extended=False),
 'articles/functional-seizures-vs-epilepsy/index.html':dict(words=2300,sources=8,book='books/umm-abbas/index.html',route='/articles/functional-seizures-vs-epilepsy/',medical=True,extended=False),
}
TRUSTED=('nasa.gov','esa.int','lbl.gov','doi.org','aanda.org','pdg.lbl.gov','pubmed.ncbi.nlm.nih.gov','pmc.ncbi.nlm.nih.gov','who.int','nhs.uk','fda.gov','gov.uk','aan.com','neurology.org','ilae.org','quran.com','quran.ksu.edu.sa','tafsir.app','sunnah.com','aclanthology.org','arxiv.org','academic.oup.com','oecd.org','fao.org','unesco.org','ipcc.ch','unece.org','un.org','cambridge.org','tandfonline.com','sciencedirect.com','science.org','wiley.com','onlinelibrary.wiley.com','dainst.org','ascelibrary.org','ahrq.gov','nice.org.uk','gmc-uk.org','nationalacademies.org','nap.nationalacademies.org','papers.nips.cc','proceedings.neurips.cc','proceedings.iclr.cc','jmlr.org','proceedings.mlr.press','pnas.org')

@dataclass
class D:
 text:list[str]=field(default_factory=list);links:list[str]=field(default_factory=list);classes:set[str]=field(default_factory=set);ids:set[str]=field(default_factory=set);jsons:list[str]=field(default_factory=list);ignore:int=0;json_on:bool=False;buf:list[str]=field(default_factory=list)
class P(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.d=D()
 def handle_starttag(self,t,a):
  t=t.lower();a={k.lower():(v or '') for k,v in a}
  if t in {'style','noscript'}:self.d.ignore+=1
  if t=='script':
   if a.get('type','').lower()=='application/ld+json':self.d.json_on=True;self.d.buf=[]
   else:self.d.ignore+=1
  if t=='a' and a.get('href'):self.d.links.append(a['href'].strip())
  if a.get('id'):self.d.ids.add(a['id'])
  self.d.classes.update(a.get('class','').split())
 def handle_endtag(self,t):
  t=t.lower()
  if t=='script' and self.d.json_on:
   raw=''.join(self.d.buf).strip();self.d.json_on=False;self.d.buf=[]
   if raw:self.d.jsons.append(raw)
  elif t in {'script','style','noscript'} and self.d.ignore:self.d.ignore-=1
 def handle_data(self,x):
  if self.d.json_on:self.d.buf.append(x)
  elif not self.d.ignore and x.strip():self.d.text.append(x.strip())
def parse(p):
 x=P();x.feed(p.read_text(encoding='utf-8'));x.close();[json.loads(j) for j in x.d.jsons];return x.d
def wc(text):return len(re.findall(r'[\u0600-\u06ffA-Za-z0-9]+',text))
def article_node(d):
 def walk(o):
  if isinstance(o,dict):
   yield o
   for x in o.get('@graph',[]) if isinstance(o.get('@graph'),list) else []:yield from walk(x)
  elif isinstance(o,list):
   for x in o:yield from walk(x)
 for raw in d.jsons:
  for n in walk(json.loads(raw)):
   typ=n.get('@type'); types=typ if isinstance(typ,list) else [typ]
   if 'Article' in types:return n
 return None

def main():
 errors=[];warnings=[]
 hubs={p:(ROOT/p).read_text(encoding='utf-8') for p in ['articles/index.html','en/articles/index.html','research-status/index.html','en/research-status/index.html']}
 sitemap=(ROOT/'sitemap.xml').read_text(encoding='utf-8'); feeds=(ROOT/'articles/feed.xml').read_text(encoding='utf-8'); enfeeds=(ROOT/'en/articles/feed.xml').read_text(encoding='utf-8')
 for rel,r in RULES.items():
  p=ROOT/rel
  if not p.exists():errors.append(f'{rel}: missing');continue
  d=parse(p);text=re.sub(r'\s+',' ',' '.join(d.text));count=wc(text);ext=sorted(set(h for h in d.links if urlsplit(h).scheme in {'http','https'} and urlsplit(h).netloc!='ahmed-alhafiz.github.io'))
  print(f'{rel}: {count} visible words, {len(ext)} external sources')
  if count<r['words']:errors.append(f'{rel}: depth {count} < {r["words"]}')
  if len(ext)<r['sources']:errors.append(f'{rel}: visible external sources {len(ext)} < {r["sources"]}')
  if 'answer' not in d.ids or 'summary-box' not in d.classes:errors.append(f'{rel}: no direct-answer unit')
  for c in ['references','citation-box','related-work']:
   if c not in d.classes:errors.append(f'{rel}: missing .{c}')
  n=article_node(d)
  if not n:errors.append(f'{rel}: no Article JSON-LD')
  else:
   typ=n.get('@type');
   if (typ=='ScholarlyArticle') or (isinstance(typ,list) and 'ScholarlyArticle' in typ):errors.append(f'{rel}: falsely implies ScholarlyArticle')
   for key in ['headline','abstract','datePublished','dateModified','author','citation']:
    if not n.get(key):errors.append(f'{rel}: Article schema missing {key}')
   if n.get('isBasedOn'):errors.append(f'{rel}: forthcoming book must not be declared evidentiary isBasedOn')
   if (rel.startswith(('articles/ratq','en/articles/ratq')) or 'water-civilization-power' in rel or 'diagnostic-uncertainty-family-fear-coercive-authority' in rel or 'teaching-names-ai-understanding' in rel) and not n.get('mentions'):errors.append(f'{rel}: thematic book relationship should be disclosed with mentions')
  domains={urlsplit(h).netloc.lower() for h in ext if any(urlsplit(h).netloc.lower().endswith(t) for t in TRUSTED)}
  if len(domains)<3:errors.append(f'{rel}: trusted-source diversity too low: {sorted(domains)}')
  book=(ROOT/r['book']).read_text(encoding='utf-8') if (ROOT/r['book']).exists() else ''
  if r['route'] not in book:errors.append(f'{rel}: no reciprocal link from {r["book"]}')
  hub=hubs['en/articles/index.html'] if rel.startswith('en/') else hubs['articles/index.html']
  if r['route'] not in hub:errors.append(f'{rel}: absent from relevant hub')
  if BASE+r['route'] not in sitemap:errors.append(f'{rel}: absent from sitemap')
  if rel.startswith('en/'):
   if BASE+r['route'] not in enfeeds:errors.append(f'{rel}: absent from English Atom feed')
  elif BASE+r['route'] not in feeds:errors.append(f'{rel}: absent from Arabic Atom feed')
  lower=text.lower()
  if not any(x in lower for x in ['external review','مراجعة خارجية','مراجعة اختصاص','لم تتم بعد']):warnings.append(f'{rel}: external-review wording is weak')
  if r['medical']:
   groups=[('هذه مادة تثقيفية','مادة تثقيفية عامة','educational'),('ليست تشخيص','ليس تشخيص','not a diagnosis'),('الطوارئ','الإسعاف','emergency'),('لا توقف','لا تغيّر','لا تغير','do not stop')]
   for g in groups:
    if not any(x.lower() in lower for x in g):errors.append(f'{rel}: missing medical safeguard {g}')
   if 'MedicalWebPage' not in ''.join(d.jsons):errors.append(f'{rel}: missing MedicalWebPage schema')

 required=[
  'articles/ratq-fatq-big-bang/evidence/index.html','en/articles/ratq-fatq-big-bang/evidence/index.html','articles/water-civilization-power/evidence/index.html','en/articles/water-civilization-power/evidence/index.html','articles/water-civilization-power/evidence/claims.json','articles/water-civilization-power/evidence/references.bib','articles/water-civilization-power/evidence/references.ris','articles/water-civilization-power/citation.bib','articles/water-civilization-power/citation.ris','articles/water-civilization-power/CITATION.cff','articles/diagnostic-uncertainty-family-fear-coercive-authority/evidence/index.html','en/articles/diagnostic-uncertainty-family-fear-coercive-authority/evidence/index.html','articles/diagnostic-uncertainty-family-fear-coercive-authority/evidence/claims.json','articles/diagnostic-uncertainty-family-fear-coercive-authority/evidence/references.bib','articles/diagnostic-uncertainty-family-fear-coercive-authority/evidence/references.ris','articles/diagnostic-uncertainty-family-fear-coercive-authority/citation.bib','articles/diagnostic-uncertainty-family-fear-coercive-authority/citation.ris','articles/diagnostic-uncertainty-family-fear-coercive-authority/CITATION.cff','assets/figures/fear-certainty-authority-cascade-ar.svg','assets/figures/fear-certainty-authority-cascade-en.svg','assets/figures/parallel-path-safeguard-ar.svg','assets/figures/parallel-path-safeguard-en.svg','assets/figures/water-power-justice-chain-ar.svg','assets/figures/water-power-justice-chain-en.svg','articles/ratq-fatq-big-bang/evidence/claims.json','articles/ratq-fatq-big-bang/citation.bib','articles/ratq-fatq-big-bang/citation.ris','assets/figures/ratq-evidence-map-ar.svg','assets/figures/ratq-evidence-map-en.svg','assets/figures/source-trust-pipeline-ar.svg','assets/figures/source-trust-pipeline-en.svg','articles/teaching-names-ai-understanding/claims.json','articles/teaching-names-ai-understanding/references.bib','articles/teaching-names-ai-understanding/references.ris','articles/teaching-names-ai-understanding/CITATION.cff','articles/teaching-names-ai-understanding/evidence/claims.json','articles/teaching-names-ai-understanding/evidence/references.bib','articles/teaching-names-ai-understanding/evidence/references.ris','articles/research-index.json','CITATION.cff']
 for f in required:
  if not (ROOT/f).exists() or (ROOT/f).stat().st_size<80:errors.append(f'{f}: missing or empty')
 try:
  tclaims=json.loads((ROOT/'articles/teaching-names-ai-understanding/claims.json').read_text(encoding='utf-8'))
  if len(tclaims.get('claims',[]))!=14:errors.append('Teaching Names claims.json must contain exactly 14 audited claims')
  if tclaims.get('external_review')!='not_completed':errors.append('Teaching Names claims.json: external review state is not explicit')
  if (ROOT/'articles/teaching-names-ai-understanding/claims.json').read_bytes() != (ROOT/'articles/teaching-names-ai-understanding/evidence/claims.json').read_bytes():errors.append('Teaching Names claim-register mirror drift')
  if (ROOT/'articles/teaching-names-ai-understanding/references.bib').read_bytes() != (ROOT/'articles/teaching-names-ai-understanding/evidence/references.bib').read_bytes():errors.append('Teaching Names BibTeX mirror drift')
  if (ROOT/'articles/teaching-names-ai-understanding/references.ris').read_bytes() != (ROOT/'articles/teaching-names-ai-understanding/evidence/references.ris').read_bytes():errors.append('Teaching Names RIS mirror drift')
 except Exception as e:errors.append(f'Teaching Names evidence package invalid: {e}')
 for f in ['methodology/index.html','en/methodology/index.html','research-status/index.html','en/research-status/index.html','about/index.html','en/about/index.html']:
  if not (ROOT/f).exists():errors.append(f'{f}: missing trust surface')

 for f in ['books/sirou-fi-alard/index.html','books/umm-abbas/index.html','en/books/sirou-fi-alard/index.html','en/books/umm-abbas/index.html']:
  t=(ROOT/f).read_text(encoding='utf-8') if (ROOT/f).exists() else ''
  if not any(x in t for x in ['قيد الإصدار','forthcoming']):errors.append(f'{f}: forthcoming state missing')
  if not any(x in t for x in ['لا تعتمد','does not treat','لا تُستخدم','not evidence']):errors.append(f'{f}: evidence independence not explicit')

 for route in ['/en/articles/ratq-fatq-big-bang/','/en/articles/water-civilization-power/','/en/articles/diagnostic-uncertainty-family-fear-coercive-authority/','/en/articles/teaching-names-ai-understanding/']:
  if route not in hubs['en/articles/index.html']:errors.append(f'English hub missing complete dossier {route}')
 en_hub_lower=hubs['en/articles/index.html'].lower()
 if not any(x in en_hub_lower for x in ['not a peer-reviewed journal','no suggestion of peer review where none occurred','not peer-reviewed']):errors.append('English hub missing review disclosure')

 if warnings:
  print('\nWARNINGS');[print('-',x) for x in warnings]
 if errors:
  print('\nERRORS');[print('-',x) for x in errors];return 1
 print(f'\nPASS: {len(RULES)} research pages satisfy depth, evidence, transparency, linking, bilingual and medical-safety gates');return 0
if __name__=='__main__':sys.exit(main())
