from __future__ import annotations
import json
import re
from html.parser import HTMLParser
from pathlib import Path

TARGETS = [
    "en/articles/ratq-fatq-big-bang/index.html",
    "articles/ratq-fatq-big-bang/index.html",
    "articles/sleep-paralysis-jathoom/index.html",
    "articles/spiritual-healing-exploitation-safeguarding/index.html",
    "en/articles/teaching-names-ai-understanding/index.html",
    "articles/six-days-creation-cosmic-time/index.html",
    "articles/teaching-names-ai-understanding/index.html",
    "articles/functional-seizures-vs-epilepsy/index.html",
]

STALE = re.compile(r'"mainContentOfPage"\s*:\s*\{\s*"@id"\s*:\s*"([^"]+#article)"\s*\}')
FIXED = re.compile(r'"mainEntity"\s*:\s*\{\s*"@id"\s*:\s*"([^"]+#article)"\s*\}')

class JSONLDParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.on=False; self.buf=[]; self.blocks=[]
    def handle_starttag(self, tag, attrs):
        if tag.lower() == "script" and dict(attrs).get("type", "").lower() == "application/ld+json":
            self.on=True; self.buf=[]
    def handle_endtag(self, tag):
        if tag.lower() == "script" and self.on:
            self.blocks.append("".join(self.buf)); self.on=False; self.buf=[]
    def handle_data(self, data):
        if self.on: self.buf.append(data)

def graph_nodes(data):
    if isinstance(data, dict) and isinstance(data.get("@graph"), list):
        return [x for x in data["@graph"] if isinstance(x, dict)]
    if isinstance(data, dict): return [data]
    if isinstance(data, list): return [x for x in data if isinstance(x, dict)]
    return []

for name in TARGETS:
    path = Path(name)
    text = path.read_text(encoding="utf-8")
    stale = STALE.findall(text)
    fixed = FIXED.findall(text)
    if len(stale) == 1 and len(fixed) == 0:
        article_id = stale[0]
        text = STALE.sub(lambda m: f'"mainEntity":{{"@id":"{m.group(1)}"}}', text, count=1)
        path.write_text(text, encoding="utf-8")
    elif len(stale) == 0 and len(fixed) == 1:
        article_id = fixed[0]
    else:
        raise SystemExit(f"{name}: expected one stale or one corrected page→article relation; stale={len(stale)} corrected={len(fixed)}")

    parser = JSONLDParser(); parser.feed(path.read_text(encoding="utf-8"))
    parsed = [json.loads(raw) for raw in parser.blocks if raw.strip()]
    nodes = [node for block in parsed for node in graph_nodes(block)]
    by_id = {node.get("@id"): node for node in nodes if isinstance(node.get("@id"), str)}
    article = by_id.get(article_id)
    if not article or article.get("@type") != "Article":
        raise SystemExit(f"{name}: corrected target is not the Article node: {article_id}")
    page_id = article_id[:-len("#article")] + "#page"
    page = by_id.get(page_id)
    if not page:
        raise SystemExit(f"{name}: missing page node {page_id}")
    if page.get("mainEntity") != {"@id": article_id}:
        raise SystemExit(f"{name}: page mainEntity does not point to Article")
    if article.get("mainEntityOfPage") != {"@id": page_id}:
        raise SystemExit(f"{name}: Article mainEntityOfPage does not return to page")

AUDIT = Path("tools/site_audit.py")
code = AUDIT.read_text(encoding="utf-8")
marker = "mainContentOfPage points to an Article"
if marker not in code:
    anchor = """        if not q.jsonld_raw:errors.append(f'{rel}: missing JSON-LD')
        if q.blank_rel_errors:errors.append(f'{rel}: {q.blank_rel_errors} target=_blank links lack noopener')
"""
    replacement = """        if not q.jsonld_raw:errors.append(f'{rel}: missing JSON-LD')
        # Schema.org mainContentOfPage expects a WebPageElement, not an Article.
        # Article↔page relationships belong on mainEntity / mainEntityOfPage.
        for raw in q.jsonld_raw:
            data=json.loads(raw)
            for node in iter_jsonld_nodes(data):
                if not isinstance(node,dict):continue
                value=node.get('mainContentOfPage')
                target_id=value.get('@id') if isinstance(value,dict) else value if isinstance(value,str) else ''
                if isinstance(target_id,str) and target_id.endswith('#article'):
                    errors.append(f'{rel}: mainContentOfPage points to an Article; use mainEntity instead')
        if q.blank_rel_errors:errors.append(f'{rel}: {q.blank_rel_errors} target=_blank links lack noopener')
"""
    if code.count(anchor) != 1:
        raise SystemExit("tools/site_audit.py: schema gate insertion anchor drift")
    AUDIT.write_text(code.replace(anchor, replacement), encoding="utf-8")

print("Ahrefs Schema.org remediation applied/verified for 8 reported URLs.")
