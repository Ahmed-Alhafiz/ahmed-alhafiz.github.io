#!/usr/bin/env python3
"""Audit the public research discovery graph.

Checks: index/feed chronology and titles, Article JSON-LD headline/date, sitemap and
hub presence, reciprocal book links, and complete two-way hreflang + visible
language switching for every dossier declared bilingual.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
ATOM = {"a": "http://www.w3.org/2005/Atom"}
SM = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
FUTURE = timedelta(minutes=10)
SLUGS = {
    "ratq-fatq-big-bang", "teaching-names-ai-understanding",
    "spiritual-healing-exploitation-safeguarding", "functional-seizures-vs-epilepsy",
    "six-days-creation-cosmic-time", "sleep-paralysis-jathoom",
    "arabic-psychological-horror", "water-civilization-power",
    "diagnostic-uncertainty-family-fear-coercive-authority",
}
BOOKS = {
    "sirou-fi-alard": ROOT / "books/sirou-fi-alard/index.html",
    "umm-abbas": ROOT / "books/umm-abbas/index.html",
}
ALT_RE = re.compile(r'<link\b[^>]*rel=["\']alternate["\'][^>]*hreflang=["\']([^"\']+)["\'][^>]*href=["\']([^"\']+)["\'][^>]*>', re.I)
LANGS_RE = re.compile(r'<div\b[^>]*class=["\'][^"\']*\blangs\b[^"\']*["\'][^>]*>(.*?)</div>', re.I | re.S)
A_RE = re.compile(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*hreflang=["\']([^"\']+)["\'][^>]*>', re.I)


class LD(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.on = False; self.buf = []; self.blocks = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag.lower() == "script" and a.get("type", "").lower() == "application/ld+json":
            self.on = True; self.buf = []
    def handle_endtag(self, tag):
        if tag.lower() == "script" and self.on:
            self.blocks.append("".join(self.buf)); self.on = False
    def handle_data(self, data):
        if self.on: self.buf.append(data)


def die(msg): raise SystemExit(msg)

def norm(s): return re.sub(r"\s+", " ", str(s)).strip()

def same(a, b): return norm(a).casefold() == norm(b).casefold()

def jload(path):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e: die(f"{path.relative_to(ROOT)}: invalid JSON: {e}")

def when(value, ctx):
    try: d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception as e: die(f"{ctx}: invalid time {value!r}: {e}")
    if d.tzinfo is None: die(f"{ctx}: timezone missing")
    return d.astimezone(timezone.utc)

def route(url):
    p = urlparse(url)
    if p.scheme and p.netloc != "ahmed-alhafiz.github.io": die(f"off-site canonical research URL: {url}")
    r = p.path if p.scheme else url.split("#",1)[0].split("?",1)[0]
    if not r.startswith("/"): r = "/" + r
    if not r.endswith("/"): die(f"canonical research URL lacks trailing slash: {url}")
    return r

def page_path(url): return ROOT / route(url).lstrip("/") / "index.html"

def article(html, rel):
    p = LD(); p.feed(html)
    for raw in p.blocks:
        if not raw.strip(): continue
        data = json.loads(raw)
        nodes = [data] if isinstance(data, dict) else []
        if isinstance(data, dict) and isinstance(data.get("@graph"), list): nodes += data["@graph"]
        for n in nodes:
            if isinstance(n, dict) and n.get("@type") in {"Article", "ScholarlyArticle"}: return n
    die(f"{rel}: Article JSON-LD missing")

def page_meta(url, headline):
    p = page_path(url); rel = str(p.relative_to(ROOT)); html = p.read_text(encoding="utf-8")
    n = article(html, rel)
    if not same(n.get("headline", ""), headline):
        die(f"{rel}: Article headline drift; index={headline!r}, page={n.get('headline')!r}")
    if n.get("url") != url: die(f"{rel}: Article URL drift")
    pub, mod = n.get("datePublished"), n.get("dateModified")
    if not isinstance(pub, str) or not pub: die(f"{rel}: datePublished missing")
    if not isinstance(mod, str) or not mod: die(f"{rel}: dateModified missing")
    return html, pub, mod

def bilingual(item):
    if "en" not in item["languages"]: return
    ar, en = item["url"], item["english_url"]
    alt_expected = {"ar": ar, "en": en, "x-default": en}
    switch_expected = {"ar": route(ar), "en": route(en)}
    for url in (ar, en):
        p = page_path(url); rel = str(p.relative_to(ROOT)); html = p.read_text(encoding="utf-8")
        alts = {k.lower(): v for k, v in ALT_RE.findall(html)}
        for lang, target in alt_expected.items():
            if alts.get(lang) != target:
                die(f"{rel}: reciprocal hreflang {lang} expected {target!r}, found {alts.get(lang)!r}")
        m = LANGS_RE.search(html)
        if not m: die(f"{rel}: visible bilingual language switch missing")
        visible = {lang.lower(): route(href) for href, lang in A_RE.findall(m.group(1)) if lang.lower() in {"ar","en"}}
        for lang, target in switch_expected.items():
            if visible.get(lang) != target: die(f"{rel}: visible {lang} switch drift")

def index_data():
    data = jload(ROOT / "articles/research-index.json"); items = data.get("items")
    if not isinstance(items, list) or not items: die("research-index: empty items")
    urls = {}; slugs = {}
    for x in items:
        req = ("slug","title","summary","type","version","languages","review","book","url")
        miss = [k for k in req if not x.get(k)]
        if miss: die(f"{x.get('slug','?')}: missing {miss}")
        s, u = x["slug"], x["url"]
        if s in slugs or u in urls: die(f"research-index duplicate: {s}")
        if x["book"] not in BOOKS: die(f"{s}: unknown book")
        if "ar" not in x["languages"]: die(f"{s}: Arabic not declared")
        if not page_path(u).is_file(): die(f"{s}: Arabic page missing")
        page_meta(u, x["title"])
        if "en" in x["languages"]:
            if not x.get("english_title") or not x.get("english_url"): die(f"{s}: incomplete English metadata")
            if not page_path(x["english_url"]).is_file(): die(f"{s}: English page missing")
            page_meta(x["english_url"], x["english_title"]); bilingual(x)
        urls[u] = x; slugs[s] = x
    missing = SLUGS - set(slugs)
    if missing: die(f"research-index missing surfaces: {sorted(missing)}")
    return urls

def atom(path, expected):
    root = ET.parse(path).getroot(); fu = root.findtext("a:updated", namespaces=ATOM)
    if not fu: die(f"{path}: feed updated missing")
    feed_updated = when(fu, f"{path} updated"); latest = datetime.min.replace(tzinfo=timezone.utc); entries = {}
    for e in root.findall("a:entry", ATOM):
        link = e.find("a:link", ATOM); u = link.get("href") if link is not None else None
        t = e.findtext("a:title", namespaces=ATOM); p = e.findtext("a:published", namespaces=ATOM); m = e.findtext("a:updated", namespaces=ATOM)
        if not all((u,t,p,m)) or u in entries: die(f"{path}: malformed/duplicate entry")
        pd, md = when(p, f"{path} {u} published"), when(m, f"{path} {u} updated")
        if md < pd: die(f"{path}: update before publication {u}")
        latest = max(latest, pd, md); entries[u] = (t,p)
    if set(entries) != set(expected): die(f"{path}: URL drift")
    for u, x in expected.items():
        if not same(entries[u][0], x["title"]): die(f"{path}: title drift {u}")
        _, page_pub, _ = page_meta(u, x["title"])
        if when(entries[u][1], "feed pub").date().isoformat() != page_pub[:10]:
            die(f"{path}: publication-date drift {u}: feed={entries[u][1][:10]}, page={page_pub[:10]}")
    limit = datetime.now(timezone.utc) + FUTURE
    if latest > limit or feed_updated > limit: die(f"{path}: future timestamp")
    if feed_updated < latest: die(f"{path}: feed updated older than newest item")

def json_feed(path, expected):
    items = jload(path).get("items")
    if not isinstance(items, list): die(f"{path}: items not list")
    entries = {x.get("url"): x for x in items if isinstance(x, dict)}
    if None in entries or len(entries) != len(items) or set(entries) != set(expected): die(f"{path}: URL/duplicate drift")
    limit = datetime.now(timezone.utc) + FUTURE
    for u, x in expected.items():
        f = entries[u]
        if not same(f.get("title", ""), x["title"]): die(f"{path}: title drift {u}")
        tags = set(f.get("tags", []))
        if x["review"] not in tags or x["book"] not in tags: die(f"{path}: review/book tags missing {u}")
        pd, md = when(f.get("date_published", ""), f"{path} pub"), when(f.get("date_modified", ""), f"{path} mod")
        if md < pd or max(pd,md) > limit: die(f"{path}: chronology error {u}")
        _, page_pub, _ = page_meta(u, x["title"])
        if pd.date().isoformat() != page_pub[:10]: die(f"{path}: publication-date drift {u}")

def surfaces(indexed):
    ah = (ROOT/"articles/index.html").read_text(encoding="utf-8"); eh = (ROOT/"en/articles/index.html").read_text(encoding="utf-8")
    sm = ET.parse(ROOT/"sitemap.xml").getroot(); urls = {n.text for n in sm.findall("s:url/s:loc", SM) if n.text}
    for u, x in indexed.items():
        r = route(u)
        if r not in ah or u not in urls: die(f"{x['slug']}: absent from Arabic hub/sitemap")
        bp = BOOKS[x["book"]]; bh = bp.read_text(encoding="utf-8"); br = "/" + str(bp.relative_to(ROOT)).removesuffix("index.html")
        sh = page_path(u).read_text(encoding="utf-8")
        if r not in bh or br not in sh: die(f"{x['slug']}: reciprocal book link missing")
        if x.get("english_url"):
            eu = x["english_url"]; er = route(eu)
            if eu not in urls or er not in eh: die(f"{x['slug']}: English hub/sitemap omission")

def main():
    ar = index_data(); en = {x["english_url"]:{**x,"title":x["english_title"]} for x in ar.values() if x.get("english_url")}
    atom(ROOT/"articles/feed.xml", ar); json_feed(ROOT/"articles/feed.json", ar)
    atom(ROOT/"en/articles/feed.xml", en); json_feed(ROOT/"en/articles/feed.json", en)
    surfaces(ar)
    print(f"Discovery integrity passed: {len(ar)} Arabic surfaces, {len(en)} English editions; chronology, JSON-LD metadata, reciprocal hreflang/switches, hubs, sitemap and book links agree.")

if __name__ == "__main__":
    try: main()
    except BrokenPipeError: sys.exit(1)
