#!/usr/bin/env python3
"""Audit the public research discovery graph.

Checks: index/feed chronology and titles, Article JSON-LD headline and calendar
publication/modification dates, sitemap and hub presence, reciprocal book links,
and complete reciprocal hreflang plus visible language switching for every
declared language edition.

Feed timestamps are timezone-aware instants. Page JSON-LD dates are calendar
publication dates. Calendar-date equality is therefore compared from the source
ISO date component, while UTC conversion is used only for chronology/future checks;
this avoids false mismatches around local midnight.
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
    "quran-science-method-evidence",
    "human-embryo-quran-stages",
    "brain-consciousness-spirit-limits",
    "water-life-molecular-properties",
    "iron-fire-light-matter-energy",
    "civilization-knowledge-justice-collapse",
    "religious-ocd-scrupulosity",
    "how-certainty-becomes-violence",
    "juhayman-grand-mosque-1979",
    "fall-of-baghdad-1258-ibn-al-alqami",
    "ratq-fatq-big-bang", "teaching-names-ai-understanding",
    "spiritual-healing-exploitation-safeguarding", "functional-seizures-vs-epilepsy",
    "six-days-creation-cosmic-time", "sleep-paralysis-jathoom",
    "arabic-psychological-horror", "water-civilization-power",
    "diagnostic-uncertainty-family-fear-coercive-authority",
}
BOOKS = {
    "juhayman": ROOT / "books/juhayman/index.html",
    "kitab-al-kutub": ROOT / "books/kitab-al-kutub/index.html",
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


class HomeReading(HTMLParser):
    """Read actual homepage anchors; JSON-LD text is not a visible link."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_selection = False
        self.current = None
        self.text = []
        self.selected = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'ol' and 'selected-reading-list' in attrs.get('class', '').split():
            self.in_selection = True
        if tag == 'a':
            self.links.append(attrs.get('href'))
            if self.in_selection:
                self.current = attrs.get('href')
                self.text = []

    def handle_data(self, data):
        if self.current:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == 'a' and self.current:
            self.selected.append((self.current, norm(''.join(self.text))))
            self.current = None
        if tag == 'ol':
            self.in_selection = False


def die(msg): raise SystemExit(msg)
def norm(s): return re.sub(r"\s+", " ", str(s)).strip()
def same(a, b): return norm(a).casefold() == norm(b).casefold()
def iso_day(value):
    if not isinstance(value, str) or len(value) < 10:
        die(f"invalid ISO date value: {value!r}")
    return value[:10]
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
    if p.scheme and p.netloc != "ahmedalhafiz.com": die(f"off-site canonical research URL: {url}")
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
    if not same(n.get("headline", ""), headline): die(f"{rel}: Article headline drift; index={headline!r}, page={n.get('headline')!r}")
    if n.get("url") and n.get("url") != url: die(f"{rel}: Article URL drift")
    pub, mod = n.get("datePublished"), n.get("dateModified")
    if not isinstance(pub, str) or not pub: die(f"{rel}: datePublished missing")
    if not isinstance(mod, str) or not mod: die(f"{rel}: dateModified missing")
    return html, pub, mod

def citation_graph(url, expected):
    p = page_path(url); rel = str(p.relative_to(ROOT)); html = p.read_text(encoding="utf-8")
    values = article(html, rel).get("citation")
    # Three declared primary sources is the repository minimum. Bounded
    # historical explainers need not imitate the source count of long dossiers.
    if (not isinstance(values, list) or len(values) < 3 or
            not set(expected).issubset(set(values)) or len(values) != len(set(values))):
        die(f"{rel}: Article citation graph missing, duplicated, or drifted")

def multilingual(item):
    fields = {
        "ar": ("url", "title"),
        "en": ("english_url", "english_title"),
        "de": ("german_url", "german_title"),
        "id": ("indonesian_url", "indonesian_title"),
    }
    declared = item["languages"]
    if len(declared) < 2:
        return
    editions = {lang: item[fields[lang][0]] for lang in declared}
    switch_expected = {lang: route(url) for lang, url in editions.items()}
    seen_xdefault = []
    for url in editions.values():
        p = page_path(url); rel = str(p.relative_to(ROOT)); html = p.read_text(encoding="utf-8")
        alts = {k.lower(): v for k, v in ALT_RE.findall(html)}
        for lang, target in editions.items():
            if alts.get(lang) != target: die(f"{rel}: reciprocal hreflang {lang} missing/drifted")
        xd = alts.get("x-default")
        if xd not in set(editions.values()): die(f"{rel}: x-default must target one canonical language edition")
        seen_xdefault.append(xd)
        m = LANGS_RE.search(html)
        if not m: die(f"{rel}: visible multilingual language switch missing")
        visible = {lang.lower(): route(href) for href, lang in A_RE.findall(m.group(1)) if lang.lower() in editions}
        for lang, target in switch_expected.items():
            if visible.get(lang) != target: die(f"{rel}: visible {lang} switch drift")
    if len(set(seen_xdefault)) != 1: die(f"{item['slug']}: language editions disagree on x-default")

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
            page_meta(x["english_url"], x["english_title"])
        if "de" in x["languages"]:
            if not x.get("german_title") or not x.get("german_url"): die(f"{s}: incomplete German metadata")
            if not page_path(x["german_url"]).is_file(): die(f"{s}: German page missing")
            page_meta(x["german_url"], x["german_title"])
        if "id" in x["languages"]:
            if not x.get("indonesian_title") or not x.get("indonesian_url"): die(f"{s}: incomplete Indonesian metadata")
            if not page_path(x["indonesian_url"]).is_file(): die(f"{s}: Indonesian page missing")
            page_meta(x["indonesian_url"], x["indonesian_title"])
        unsupported = set(x["languages"]) - {"ar", "en", "de", "id"}
        if unsupported: die(f"{s}: unsupported declared languages: {sorted(unsupported)}")
        multilingual(x)
        if "de" in x["languages"]:
            # An author's reading of an unpublished novel is not a sourced
            # research guide. Require a declared source work and manuscript
            # reading notes, not three invented independent sources.
            if x["type"] == "قراءة أدبية في عمل المؤلف":
                if x.get("source_work") != "https://ahmedalhafiz.com/books/umm-abbas/":
                    die(f"{s}: literary reading lacks the declared source work")
                for lang_url in (x["url"], x["english_url"], x["german_url"]):
                    html = page_path(lang_url).read_text(encoding="utf-8")
                    if 'id="reading-notes"' not in html:
                        die(f"{s}: literary reading lacks manuscript notes: {lang_url}")
            else:
                expected_citations = x.get("primary_sources", [])
                if len(expected_citations) < 3: die(f"{s}: multilingual guide lacks primary-source inventory")
                for lang_url in (x["url"], x["english_url"], x["german_url"]):
                    citation_graph(lang_url, expected_citations)
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
        latest = max(latest, pd, md); entries[u] = (t,p,m)
    if set(entries) != set(expected): die(f"{path}: URL drift")
    for u, x in expected.items():
        if not same(entries[u][0], x["title"]): die(f"{path}: title drift {u}")
        _, page_pub, page_mod = page_meta(u, x["title"])
        if iso_day(entries[u][1]) != iso_day(page_pub): die(f"{path}: publication-date drift {u}: feed={iso_day(entries[u][1])}, page={iso_day(page_pub)}")
        if iso_day(entries[u][2]) != iso_day(page_mod): die(f"{path}: modified-date drift {u}: feed={iso_day(entries[u][2])}, page={iso_day(page_mod)}")
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
        pub_raw, mod_raw = f.get("date_published", ""), f.get("date_modified", "")
        pd, md = when(pub_raw, f"{path} pub"), when(mod_raw, f"{path} mod")
        if md < pd or max(pd,md) > limit: die(f"{path}: chronology error {u}")
        _, page_pub, page_mod = page_meta(u, x["title"])
        if iso_day(pub_raw) != iso_day(page_pub): die(f"{path}: publication-date drift {u}")
        if iso_day(mod_raw) != iso_day(page_mod): die(f"{path}: modified-date drift {u}")

def surfaces(indexed):
    ah = (ROOT/"articles/index.html").read_text(encoding="utf-8"); eh = (ROOT/"en/articles/index.html").read_text(encoding="utf-8")
    sm = ET.parse(ROOT/"sitemap.xml").getroot(); urls = {n.text for n in sm.findall("s:url/s:loc", SM) if n.text}
    for u, x in indexed.items():
        r = route(u)
        if r not in ah or u not in urls: die(f"{x['slug']}: absent from Arabic hub/sitemap")
        bp = BOOKS[x["book"]]; bh = bp.read_text(encoding="utf-8"); br = "/" + bp.relative_to(ROOT).as_posix().removesuffix("index.html")
        sh = page_path(u).read_text(encoding="utf-8")
        if r not in bh or br not in sh: die(f"{x['slug']}: reciprocal book link missing")
        if x.get("english_url"):
            eu = x["english_url"]; er = route(eu)
            if eu not in urls or er not in eh: die(f"{x['slug']}: English hub/sitemap omission")
        if x.get("german_url"):
            gu = x["german_url"]; gr = route(gu)
            gh = (ROOT/"de/index.html").read_text(encoding="utf-8")
            gdh = (ROOT/"de/articles/index.html").read_text(encoding="utf-8")
            if gu not in urls or gr not in gh or gr not in gdh:
                die(f"{x['slug']}: German homepage/hub/sitemap omission")
        if x.get("indonesian_url"):
            iu=x["indonesian_url"]; ir=route(iu)
            ih=(ROOT/"id/articles/index.html").read_text(encoding="utf-8")
            if iu not in urls or ir not in ih: die(f"{x['slug']}: Indonesian hub/sitemap omission")
            if br not in page_path(iu).read_text(encoding="utf-8"): die(f"{x['slug']}: Indonesian article lost its original Arabic book destination")

def english_homepage(expected):
    path = ROOT / "en/index.html"
    html = path.read_text(encoding="utf-8")
    parser = HomeReading(); parser.feed(html)
    if '/en/articles/' not in parser.links:
        die('en/index.html: visible route to complete English catalogue missing')
    if any('https://ahmedalhafiz.com' + href not in expected for href, _ in parser.selected):
        die('en/index.html: selected article is not a published English edition')

def hub_structured_inventory(indexed):
    """Keep each language hub's visible inventory and ItemList in lockstep."""
    configs = (
        ("articles/index.html", "ar", "url", "https://ahmedalhafiz.com/articles/#list"),
        ("en/articles/index.html", "en", "english_url", "https://ahmedalhafiz.com/en/articles/#list"),
        ("de/articles/index.html", "de", "german_url", "https://ahmedalhafiz.com/de/articles/#list"),
        ("id/articles/index.html", "id", "indonesian_url", "https://ahmedalhafiz.com/id/articles/#list"),
    )
    for rel, language, url_key, list_id in configs:
        html = (ROOT / rel).read_text(encoding="utf-8")
        parser = LD(); parser.feed(html)
        target = None
        for raw in parser.blocks:
            data = json.loads(raw)
            nodes = data.get("@graph", []) if isinstance(data, dict) else []
            target = next(
                (node for node in nodes if isinstance(node, dict) and node.get("@id") == list_id),
                target,
            )
        if target is None:
            die(f"{rel}: research ItemList missing")
        expected = {
            item[url_key]
            for item in indexed.values()
            if language in item.get("languages", []) and item.get(url_key)
        }
        listed = {
            item.get("url")
            for item in target.get("itemListElement", [])
            if isinstance(item, dict) and item.get("url")
        }
        if target.get("numberOfItems") != len(expected) or listed != expected:
            die(
                f"{rel}: structured research inventory drift; "
                f"expected {len(expected)} unique URLs, found {target.get('numberOfItems')}"
            )

def homepage_structured_inventory(indexed):
    configs = (
        ("index.html", "ar", "url", "https://ahmedalhafiz.com/#featured-research"),
        ("en/index.html", "en", "english_url", "https://ahmedalhafiz.com/en/#featured-research"),
        ("de/index.html", "de", "german_url", "https://ahmedalhafiz.com/de/#featured-research"),
    )
    for rel, language, url_key, list_id in configs:
        html = (ROOT / rel).read_text(encoding="utf-8")
        parser = LD(); parser.feed(html)
        target = None
        for raw in parser.blocks:
            data = json.loads(raw)
            nodes = data.get("@graph", []) if isinstance(data, dict) else []
            target = next(
                (node for node in nodes if isinstance(node, dict) and node.get("@id") == list_id),
                target,
            )
        if target is None:
            die(f"{rel}: homepage research ItemList missing")
        expected = {
            item[url_key]
            for item in indexed.values()
            if language in item.get("languages", []) and item.get(url_key)
        }
        if language in {'ar', 'en'}:
            # Homepages show a small selection; hub_structured_inventory still
            # checks every published edition in the complete article catalogue.
            visible = HomeReading(); visible.feed(html)
            hub = '/articles/' if language == 'ar' else '/en/articles/'
            if hub not in visible.links:
                die(f'{rel}: visible route to complete article catalogue missing')
            items = target.get('itemListElement', [])
            urls = ['https://ahmedalhafiz.com' + href for href, _ in visible.selected]
            if len(urls) != 3 or len(set(urls)) != 3 or not set(urls) <= expected:
                die(f'{rel}: expected three distinct published article links')
            actual = [(item.get('url'), norm(item.get('name', ''))) for item in items]
            wanted = list(zip(urls, [title for _, title in visible.selected]))
            if target.get('numberOfItems') != 3 or actual != wanted:
                die(f'{rel}: homepage schema differs from visible selection/order/titles')
            if [item.get('position') for item in items] != [1, 2, 3]:
                die(f'{rel}: selected-article positions drift')
            continue
        listed = {
            item.get("url")
            for item in target.get("itemListElement", [])
            if isinstance(item, dict) and item.get("url")
        }
        if target.get("numberOfItems") != len(expected) or listed != expected:
            die(f"{rel}: homepage structured research inventory drift")
        for url in expected:
            if route(url) not in html:
                die(f"{rel}: research URL is structured but not visibly linked: {url}")

def indonesian_homepage(indexed, translated):
    """The faithful homepage has three excerpts; Arabic destinations stay labeled."""
    text=(ROOT/"id/index.html").read_text(encoding="utf-8")
    visible=HomeReading();visible.feed(text)
    if '/id/articles/' not in visible.links:die('id/index.html: Indonesian catalogue route missing')
    known=set(indexed)|set(translated)
    selection=[(url if url.startswith('https://') else 'https://ahmedalhafiz.com'+url,title) for url,title in visible.selected]
    if len(selection)!=3 or len({u for u,_ in selection})!=3 or any(u not in known for u,_ in selection):die('id/index.html: selected article missing from published inventory')
    if not any(u in translated for u,_ in selection):die('id/index.html: complete Indonesian edition missing from selection')
    for url,_ in selection:
        if url in indexed and not re.search(r'href=["\']'+re.escape(url)+r'["\'][^>]*hreflang=["\']ar["\']',text):die('id/index.html: Arabic destination must retain its language label')
    ld=LD();ld.feed(text)
    lists=[n for raw in ld.blocks for n in json.loads(raw).get('@graph',[]) if n.get('@id')=='https://ahmedalhafiz.com/id/#featured-research']
    if len(lists)!=1 or lists[0].get('numberOfItems')!=3:die('id/index.html: featured ItemList missing')
    if [(i.get('url'),norm(i.get('name',''))) for i in lists[0].get('itemListElement',[])]!=selection:die('id/index.html: featured ItemList differs from visible excerpts')

def main():
    ar = index_data(); en = {x["english_url"]:{**x,"title":x["english_title"]} for x in ar.values() if x.get("english_url")}
    de = {x["german_url"]:{**x,"title":x["german_title"]} for x in ar.values() if x.get("german_url")}
    indonesian = {x["indonesian_url"]:{**x,"title":x["indonesian_title"]} for x in ar.values() if x.get("indonesian_url")}
    atom(ROOT/"articles/feed.xml", ar); json_feed(ROOT/"articles/feed.json", ar)
    atom(ROOT/"en/articles/feed.xml", en); json_feed(ROOT/"en/articles/feed.json", en)
    atom(ROOT/"de/articles/feed.xml", de)
    atom(ROOT/"id/articles/feed.xml", indonesian); json_feed(ROOT/"id/articles/feed.json", indonesian)
    surfaces(ar); english_homepage(en); hub_structured_inventory(ar); homepage_structured_inventory(ar)
    indonesian_homepage(ar, indonesian)
    print(f"Discovery integrity passed: {len(ar)} Arabic surfaces, {len(en)} English editions, {len(de)} German editions, {len(indonesian)} Indonesian editions; chronology, JSON-LD metadata, reciprocal hreflang/switches, feeds, hubs, sitemap, book links and homepage inventories agree.")

if __name__ == "__main__":
    try: main()
    except BrokenPipeError: sys.exit(1)
