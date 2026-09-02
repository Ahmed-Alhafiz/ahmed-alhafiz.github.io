#!/usr/bin/env python3
"""Integrate Teaching the Names and AI pillar 13 across the public site.

The release archive replaces the article/evidence/citation files. This script
updates all discovery, review, book, inventory, CI, and visual-regression
surfaces atomically. It is intentionally strict and aborts on drift rather than
silently producing a partial publication.
"""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SLUG = "teaching-names-ai-understanding"
AR_URL = f"https://ahmed-alhafiz.github.io/articles/{SLUG}/"
EN_URL = f"https://ahmed-alhafiz.github.io/en/articles/{SLUG}/"
AR_ROUTE = f"/articles/{SLUG}/"
EN_ROUTE = f"/en/articles/{SLUG}/"
VERSION = "2.1"
DATE = "2026-09-02"
STAMP = "2026-09-02T14:00:00+02:00"
REVIEW = "author_review_complete_ai_nlp_specialist_review_pending"
AR_TITLE = "تعليم الأسماء والذكاء الاصطناعي: ما الذي يثبت عن فهم الآلة؟"
EN_TITLE = "Teaching the Names and Artificial Intelligence: What Does the Evidence Establish About Machine Understanding?"
AR_SUMMARY = "ملف ثنائي اللغة يفصل ست طبقات كثيرًا ما تُضغط في كلمة الفهم: الرمز، والارتباط، والتركيب والنقل، والإحالة المتجذرة، والسببية والتدخل، ثم القصد والتجربة والمسؤولية؛ مع بروتوكول 6×4 و12 ادعاءً و25 مصدرًا."
EN_SUMMARY = "A bilingual evidence-led dossier separating six layers often compressed into machine understanding: symbol discrimination, distributional association, compositional transfer, grounded reference, causal intervention, and intention or responsibility; with a 6×4 protocol, 12 claims, and 25 sources."

SCRIPT_RE = re.compile(
    r"(<script\b[^>]*\btype=[\"']application/ld\+json[\"'][^>]*>)(.*?)(</script>)",
    re.IGNORECASE | re.DOTALL,
)

AR_HUB_SECTION = f'''
<section class="section" id="teaching-names-ai-pillar">
  <div class="wrap">
    <div class="kicker">ملف بحثي ثنائي اللغة · الدلالة والتأريض والسببية · الإصدار {VERSION}</div>
    <h2>ما الذي يثبت فعلًا عندما نقول إن الآلة «تفهم»؟</h2>
    <div class="rule"></div>
    <div class="featured-grid">
      <article class="featured-dossier">
        <div>
          <div class="kicker">الاسم · الرمز · التمثيل · العالم · القصد</div>
          <h3><a href="{AR_ROUTE}">{AR_TITLE}</a></h3>
          <p>يفصل الملف بين ست قدرات مختلفة بدل الحكم بكلمة واحدة، ويعرض الأدلة المؤيدة والمعارضة، ثم يقدّم مصفوفة تحليلية وبروتوكول 6×4 يحاول كسر ادعاء الفهم بإعادة الصياغة والمثال المضاد والنقل والتدخل.</p>
          <div class="evidence-row"><span>12 ادعاءً محدودًا</span><span>25 مصدرًا حتى 2025</span><span>نسخة إنجليزية كاملة</span><span>مراجعة اختصاصية معلّقة</span></div>
        </div>
        <div class="actions"><a class="btn light" href="{AR_ROUTE}">اقرأ الملف</a><a class="btn light" href="{EN_ROUTE}">Read in English</a><a class="btn light" href="{AR_ROUTE}evidence/">سجل الادعاءات والأدلة</a></div>
      </article>
      <figure class="figure-card"><img src="/assets/figures/ai-understanding-matrix-ar.svg" width="1200" height="760" alt="مصفوفة الفهم من ست طبقات" loading="lazy"><figcaption>النجاح في الرمز أو الارتباط أو التركيب لا يثبت تلقائيًا الإحالة السببية أو القصد أو الوعي.</figcaption></figure>
    </div>
  </div>
</section>
'''.strip()

EN_HUB_SECTION = f'''
<section class="section" id="teaching-names-ai-pillar">
  <div class="wrap">
    <div class="kicker">Complete bilingual dossier · semantics, grounding, and causality · version {VERSION}</div>
    <h2>What does the evidence actually establish when we say a machine “understands”?</h2>
    <div class="rule"></div>
    <div class="featured-grid">
      <article class="featured-dossier">
        <div>
          <div class="kicker">Names · symbols · representations · world · intention</div>
          <h3><a href="{EN_ROUTE}">{EN_TITLE}</a></h3>
          <p>The dossier separates six capacities instead of issuing a binary verdict, confronts evidence on both sides, and introduces a Six-Layer Matrix plus a 6×4 protocol that stress-tests understanding through paraphrase, counterexample, transfer, and intervention.</p>
          <div class="evidence-row"><span>12 bounded claims</span><span>25 sources through 2025</span><span>Full Arabic edition</span><span>Specialist review pending</span></div>
        </div>
        <div class="actions"><a class="btn light" href="{EN_ROUTE}">Read the dossier</a><a class="btn light" href="{AR_ROUTE}">اقرأ بالعربية</a><a class="btn light" href="{EN_ROUTE}evidence/">Claim and evidence register</a></div>
      </article>
      <figure class="figure-card"><img src="/assets/figures/ai-understanding-matrix-en.svg" width="1200" height="760" alt="Six-Layer Understanding Matrix" loading="lazy"><figcaption>Success at symbol, association, or composition does not automatically establish grounded causality, intention, or consciousness.</figcaption></figure>
    </div>
  </div>
</section>
'''.strip()

AR_HOME_SECTION = f'''
<section class="section" id="teaching-names-ai">
  <div class="wrap">
    <div class="kicker">الركيزة الرابعة · ملف عربي وإنجليزي كامل</div>
    <h2>بين الاسم والمعنى: لا نمنح الآلة أكثر مما أثبتته، ولا ننكر ما تعلمته</h2>
    <div class="rule"></div>
    <div class="featured-grid">
      <article class="featured-dossier">
        <div><div class="kicker">الذكاء الاصطناعي · اللغة · التأريض · الوعي</div><h3><a href="{AR_ROUTE}">تعليم الأسماء والذكاء الاصطناعي</a></h3><p>مصفوفة من ست طبقات تفصل الرمز والارتباط والتركيب عن الإحالة والسببية والقصد، وبروتوكول 6×4 يمنع تحويل الطلاقة أو النجاح في اختبار واحد إلى حكم شامل.</p><div class="evidence-row"><span>12 ادعاءً</span><span>25 مصدرًا</span><span>مصادر مؤيدة ومعارضة</span><span>ملحق أدلة آلي</span></div></div>
        <div class="actions"><a class="btn light" href="{AR_ROUTE}">فتح الملف</a><a class="btn light" href="{EN_ROUTE}">English edition</a><a class="btn light" href="{AR_ROUTE}evidence/">فحص الأدلة</a></div>
      </article>
      <figure class="figure-card"><img src="/assets/figures/ai-understanding-6x4-ar.svg" width="1200" height="760" alt="بروتوكول 6×4 لفحص ادعاء الفهم" loading="lazy"><figcaption>لكل طبقة أربعة اختبارات: إعادة الصياغة، المثال المضاد، النقل، والتدخل. البروتوكول لا ينتج درجة وعي.</figcaption></figure>
    </div>
  </div>
</section>
'''.strip()

EN_HOME_SECTION = f'''
<section class="section" id="teaching-names-ai">
  <div class="wrap">
    <div class="kicker">Fourth pillar · complete Arabic and English dossier</div>
    <h2>Between name and meaning: neither overclaim what the machine proves nor deny what it learns</h2>
    <div class="rule"></div>
    <div class="featured-grid">
      <article class="featured-dossier">
        <div><div class="kicker">Artificial intelligence · language · grounding · consciousness</div><h3><a href="{EN_ROUTE}">Teaching the Names and Artificial Intelligence</a></h3><p>A six-layer matrix separates symbol, association, and composition from reference, causality, and intention. A 6×4 protocol prevents fluency or one successful benchmark from becoming a universal verdict.</p><div class="evidence-row"><span>12 claims</span><span>25 sources</span><span>Supporting and counter-evidence</span><span>Machine-readable appendix</span></div></div>
        <div class="actions"><a class="btn light" href="{EN_ROUTE}">Open the dossier</a><a class="btn light" href="{AR_ROUTE}">النسخة العربية</a><a class="btn light" href="{EN_ROUTE}evidence/">Inspect the evidence</a></div>
      </article>
      <figure class="figure-card"><img src="/assets/figures/ai-understanding-6x4-en.svg" width="1200" height="760" alt="6×4 Protocol for testing understanding claims" loading="lazy"><figcaption>Every layer faces paraphrase, counterexample, transfer, and intervention. The protocol produces no consciousness score.</figcaption></figure>
    </div>
  </div>
</section>
'''.strip()

AR_BOOK_CARD = f'''<article class="article-card"><div><div class="kicker">ملف ثنائي اللغة · الإصدار {VERSION}</div><h2><a href="{AR_ROUTE}">تعليم الأسماء والذكاء الاصطناعي: ما الذي يثبت عن فهم الآلة؟</a></h2><p>تحقيق في ست طبقات من الرمز إلى القصد، مع 12 ادعاءً و25 مصدرًا وبروتوكول 6×4 ونسخة إنجليزية كاملة.</p><div class="actions"><a class="btn" href="{AR_ROUTE}evidence/">الأدلة</a><a class="btn" href="{EN_ROUTE}">English</a></div></div><span class="tag">ملف مكتمل</span></article>'''
EN_BOOK_CARD = f'''<article class="article-card"><div><div class="kicker">Complete bilingual dossier · version {VERSION}</div><h2><a href="{EN_ROUTE}">Teaching the Names and Artificial Intelligence</a></h2><p>A six-layer investigation from symbol to intention, with 12 claims, 25 sources, a 6×4 protocol, and a complete Arabic counterpart.</p><div class="actions"><a class="btn" href="{EN_ROUTE}evidence/">Evidence</a><a class="btn" href="{AR_ROUTE}">العربية</a></div></div><span class="tag">Complete</span></article>'''
DE_BOOK_CARD = f'''<article class="article-card"><div><div class="kicker">Vollständiges englisches Dossier · Version {VERSION}</div><h2><a href="{EN_ROUTE}" hreflang="en">Teaching the Names and Artificial Intelligence</a></h2><p>Sechs getrennte Ebenen von Symbol und Assoziation bis zu Referenz, Kausalität, Absicht und Verantwortung; mit 12 Aussagen und 25 Quellen.</p><div class="actions"><a class="btn" href="{EN_ROUTE}evidence/" hreflang="en">Belege</a><a class="btn" href="{AR_ROUTE}" hreflang="ar">Arabisch</a></div></div><span class="tag">Öffnen</span></article>'''

AR_STATUS_ROW = f'''<tr><td><a href="{AR_ROUTE}">تعليم الأسماء والذكاء الاصطناعي: ما الذي يثبت عن فهم الآلة؟</a></td><td>ملف بحثي موسع ثنائي اللغة</td><td>{VERSION}</td><td>2 سبتمبر 2026</td><td><span class="confidence open">مراجعة NLP/فلسفة الذكاء الاصطناعي معلّقة</span></td><td><a href="/books/sirou-fi-alard/">سيروا في الأرض</a> — منشأ موضوعي لا دليل تقني</td></tr>'''
EN_STATUS_ROW = f'''<tr><td><a href="{EN_ROUTE}">Teaching the Names and Artificial Intelligence</a></td><td>Complete bilingual research dossier</td><td>{VERSION}</td><td>2 September 2026</td><td><span class="confidence open">NLP/philosophy-of-AI specialist review pending</span></td><td><a href="/en/books/sirou-fi-alard/">Sirou fi al-Ard</a> — thematic origin, not technical evidence</td></tr>'''

INDEX_ITEM = {
    "slug": SLUG,
    "title": AR_TITLE,
    "english_title": EN_TITLE,
    "summary": AR_SUMMARY,
    "english_summary": EN_SUMMARY,
    "type": "ملف بحثي موسع",
    "version": VERSION,
    "languages": ["ar", "en"],
    "review": REVIEW,
    "book": "sirou-fi-alard",
    "url": AR_URL,
    "english_url": EN_URL,
    "evidence_appendix": AR_URL + "evidence/",
    "english_evidence_appendix": EN_URL + "evidence/",
    "claims_json": AR_URL + "evidence/claims.json",
    "references_bib": AR_URL + "evidence/references.bib",
    "references_ris": AR_URL + "evidence/references.ris",
    "citation_bib": AR_URL + "citation.bib",
    "citation_ris": AR_URL + "citation.ris",
    "citation_cff": AR_URL + "CITATION.cff",
}


def write_text(path: Path, text: str) -> None:
    path.write_text("\n".join(line.rstrip() for line in text.rstrip().splitlines()) + "\n", encoding="utf-8")


def walk(value: object):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def rewrite_jsonld(path: Path, callback) -> int:
    text = path.read_text(encoding="utf-8")
    changed = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal changed
        data = json.loads(match.group(2))
        if callback(data):
            changed += 1
        return match.group(1) + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + match.group(3)

    revised = SCRIPT_RE.sub(replace, text)
    if changed:
        write_text(path, revised)
    return changed


def update_itemlist(path: Path, list_id: str, url: str, name: str, after_url: str | None) -> None:
    def callback(data: object) -> bool:
        changed = False
        target = None
        for node in walk(data):
            if isinstance(node, dict) and node.get("@type") == "ItemList" and node.get("@id") == list_id:
                target = node
                break
        if target is None:
            return False
        items = target.setdefault("itemListElement", [])
        existing = next((item for item in items if isinstance(item, dict) and item.get("url") in {AR_URL, EN_URL}), None)
        if existing:
            existing["url"] = url
            existing["name"] = name
        else:
            insertion = len(items)
            if after_url:
                for idx, item in enumerate(items):
                    if isinstance(item, dict) and item.get("url") == after_url:
                        insertion = idx + 1
                        break
            items.insert(insertion, {"@type": "ListItem", "position": 0, "url": url, "name": name})
        for position, item in enumerate(items, 1):
            if isinstance(item, dict):
                item["position"] = position
        target["numberOfItems"] = len(items)
        for node in walk(data):
            if isinstance(node, dict) and node.get("@type") in {"CollectionPage", "ProfilePage", "WebPage"}:
                if "dateModified" in node:
                    node["dateModified"] = DATE
        changed = True
        return changed

    if rewrite_jsonld(path, callback) != 1:
        raise RuntimeError(f"{path.relative_to(ROOT)}: expected one ItemList JSON-LD update")


def replace_card(path: Path, route_fragment: str, replacement: str, classes=("track-card", "article-card"), required=True) -> None:
    text = path.read_text(encoding="utf-8")
    matches = []
    for cls in classes:
        pattern = re.compile(rf'<article\b[^>]*class=["\'][^"\']*\b{re.escape(cls)}\b[^"\']*["\'][^>]*>.*?{re.escape(route_fragment)}.*?</article>', re.I | re.S)
        for match in pattern.finditer(text):
            matches.append((match.start(), match.end()))
    # Deduplicate overlapping matches and replace the smallest one containing the route.
    unique = sorted(set(matches), key=lambda pair: (pair[1] - pair[0], pair[0]))
    if not unique:
        if required:
            raise RuntimeError(f"{path.relative_to(ROOT)}: card containing {route_fragment} not found")
        return
    start, end = unique[0]
    revised = text[:start] + replacement + text[end:]
    write_text(path, revised)


def insert_before(path: Path, marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    if block in text:
        return
    if text.count(marker) != 1:
        raise RuntimeError(f"{path.relative_to(ROOT)}: marker count {text.count(marker)} for {marker[:80]!r}")
    write_text(path, text.replace(marker, block + "\n" + marker, 1))


def update_research_index() -> None:
    path = ROOT / "articles/research-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items", [])
    matches = [index for index, item in enumerate(items) if item.get("slug") == SLUG]
    if len(matches) != 1:
        raise RuntimeError(f"research-index: expected one teaching item, found {len(matches)}")
    items[matches[0]] = INDEX_ITEM
    data["generated"] = DATE
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_inventory() -> None:
    path = ROOT / "data/content-inventory.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    matches = [item for item in data.get("items", []) if item.get("slug") == SLUG]
    if len(matches) != 1:
        raise RuntimeError(f"content inventory: expected one teaching item, found {len(matches)}")
    item = matches[0]
    item.update({
        "class": "pillar",
        "languages": ["ar", "en"],
        "next_action": "hold_scope_measure_and_seek_independent_ai_nlp_review_only_after_explicit_user_permission",
        "reason": "Complete bilingual version 2.1 with two original but explicitly unvalidated frameworks, 12 reciprocal claims, 25 sources through 2025, portable citations, and a machine-readable evidence appendix.",
    })
    counts = {name: 0 for name in data.get("classes", {})}
    for current in data.get("items", []):
        cls = current.get("class")
        if cls in counts:
            counts[cls] += 1
    data["current_counts"] = counts
    data["generated"] = DATE
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_json_feed(path: Path, language: str) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    url = AR_URL if language == "ar" else EN_URL
    title = AR_TITLE if language == "ar" else EN_TITLE
    summary = AR_SUMMARY if language == "ar" else EN_SUMMARY
    item = {
        "id": url,
        "url": url,
        "title": title,
        "summary": summary,
        "date_published": STAMP,
        "date_modified": STAMP,
        "tags": [
            "ملف بحثي موسع ثنائي اللغة" if language == "ar" else "complete bilingual research dossier",
            REVIEW,
            "sirou-fi-alard",
            "machine understanding" if language == "en" else "فهم الآلة",
            "symbol grounding" if language == "en" else "تأسيس الرموز",
        ],
        "language": language,
    }
    items = data.setdefault("items", [])
    matches = [idx for idx, existing in enumerate(items) if existing.get("url") in {AR_URL, EN_URL}]
    if language == "ar":
        if len(matches) != 1:
            raise RuntimeError(f"{path.relative_to(ROOT)}: expected one existing Arabic teaching entry")
        items[matches[0]] = item
    else:
        if len(matches) > 1:
            raise RuntimeError(f"{path.relative_to(ROOT)}: duplicate teaching entries")
        if matches:
            items[matches[0]] = item
        else:
            insertion = next((idx + 1 for idx, existing in enumerate(items) if "diagnostic-uncertainty" in existing.get("url", "")), len(items))
            items.insert(insertion, item)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def atom_tag(name: str) -> str:
    return f"{{http://www.w3.org/2005/Atom}}{name}"


def update_atom(path: Path, language: str) -> None:
    ET.register_namespace("", "http://www.w3.org/2005/Atom")
    tree = ET.parse(path)
    root = tree.getroot()
    updated = root.find(atom_tag("updated"))
    if updated is None:
        raise RuntimeError(f"{path.relative_to(ROOT)}: feed updated missing")
    updated.text = STAMP
    url = AR_URL if language == "ar" else EN_URL
    title = AR_TITLE if language == "ar" else EN_TITLE
    summary = AR_SUMMARY if language == "ar" else EN_SUMMARY
    category = "ملف بحثي موسع ثنائي اللغة" if language == "ar" else "complete bilingual research dossier"
    entries = root.findall(atom_tag("entry"))
    existing = []
    for entry in entries:
        link = entry.find(atom_tag("link"))
        if link is not None and link.get("href") in {AR_URL, EN_URL}:
            existing.append(entry)
    if len(existing) > 1:
        raise RuntimeError(f"{path.relative_to(ROOT)}: duplicate teaching Atom entries")
    if existing:
        entry = existing[0]
        for child in list(entry):
            entry.remove(child)
    else:
        entry = ET.Element(atom_tag("entry"))
        insertion = len(root)
        for current in entries:
            link = current.find(atom_tag("link"))
            if link is not None and "diagnostic-uncertainty" in link.get("href", ""):
                insertion = list(root).index(current) + 1
                break
        root.insert(insertion, entry)
    ET.SubElement(entry, atom_tag("title")).text = title
    ET.SubElement(entry, atom_tag("link"), {"href": url})
    ET.SubElement(entry, atom_tag("id")).text = url
    ET.SubElement(entry, atom_tag("published")).text = STAMP
    ET.SubElement(entry, atom_tag("updated")).text = STAMP
    ET.SubElement(entry, atom_tag("category"), {"term": category})
    ET.SubElement(entry, atom_tag("summary")).text = summary
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def update_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    tree = ET.parse(path)
    root = tree.getroot()
    url_tag = f"{{{namespace}}}url"
    loc_tag = f"{{{namespace}}}loc"
    lastmod_tag = f"{{{namespace}}}lastmod"
    nodes = {}
    for node in root.findall(url_tag):
        loc = node.find(loc_tag)
        if loc is not None and loc.text:
            nodes[loc.text] = node
    for url in (AR_URL, AR_URL + "evidence/", EN_URL, EN_URL + "evidence/"):
        if url in nodes:
            node = nodes[url]
        else:
            node = ET.SubElement(root, url_tag)
            ET.SubElement(node, loc_tag).text = url
        lastmod = node.find(lastmod_tag)
        if lastmod is None:
            lastmod = ET.SubElement(node, lastmod_tag)
        lastmod.text = DATE
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def update_visible_surfaces() -> None:
    ar_hub = ROOT / "articles/index.html"
    update_itemlist(ar_hub, "https://ahmed-alhafiz.github.io/articles/#list", AR_URL, AR_TITLE, "https://ahmed-alhafiz.github.io/articles/diagnostic-uncertainty-family-fear-coercive-authority/")
    replace_card(ar_hub, AR_ROUTE, "", classes=("track-card",), required=True)
    insert_before(ar_hub, '<section class="section alt"><div class="wrap"><div class="kicker">ملفات موسعة باللغة العربية</div>', AR_HUB_SECTION)
    text = ar_hub.read_text(encoding="utf-8")
    row_re = re.compile(r'<tr><td><a href="/articles/teaching-names-ai-understanding/".*?</tr>', re.S)
    if len(row_re.findall(text)) != 1:
        raise RuntimeError("Arabic research publication row not found exactly once")
    new_row = f'<tr><td><a href="{AR_ROUTE}">{AR_TITLE}</a></td><td>ملف بحثي موسع ثنائي اللغة</td><td>{VERSION}</td><td>2 سبتمبر 2026</td><td>مراجعة NLP/فلسفة الذكاء الاصطناعي معلّقة</td></tr>'
    write_text(ar_hub, row_re.sub(new_row, text, count=1))

    en_hub = ROOT / "en/articles/index.html"
    update_itemlist(en_hub, "https://ahmed-alhafiz.github.io/en/articles/#list", EN_URL, EN_TITLE, "https://ahmed-alhafiz.github.io/en/articles/diagnostic-uncertainty-family-fear-coercive-authority/")
    replace_card(en_hub, AR_ROUTE, "", classes=("track-card",), required=True)
    marker = '<section class="section alt"><div class="wrap"><div class="kicker">Publication model</div>'
    insert_before(en_hub, marker, EN_HUB_SECTION)

    ar_home = ROOT / "index.html"
    update_itemlist(ar_home, "https://ahmed-alhafiz.github.io/#featured-research", AR_URL, "تعليم الأسماء والذكاء الاصطناعي: طبقات فهم الآلة", "https://ahmed-alhafiz.github.io/articles/diagnostic-uncertainty-family-fear-coercive-authority/")
    replace_card(ar_home, AR_ROUTE, "", classes=("track-card",), required=True)
    marker_re = re.compile(r'<section class="section">\s*<div class="wrap">\s*<div class="kicker">Research tracks</div>', re.S)
    text = ar_home.read_text(encoding="utf-8")
    matches = list(marker_re.finditer(text))
    if len(matches) != 1:
        raise RuntimeError(f"Arabic home research-tracks marker count: {len(matches)}")
    idx = matches[0].start()
    write_text(ar_home, text[:idx] + AR_HOME_SECTION + "\n" + text[idx:])

    en_home = ROOT / "en/index.html"
    update_itemlist(en_home, "https://ahmed-alhafiz.github.io/en/#featured-research", EN_URL, "Teaching the Names and Artificial Intelligence", "https://ahmed-alhafiz.github.io/en/articles/diagnostic-uncertainty-family-fear-coercive-authority/")
    replace_card(en_home, AR_ROUTE, "", classes=("track-card",), required=False)
    text = en_home.read_text(encoding="utf-8")
    marker_re = re.compile(r'<section class="section">\s*<div class="wrap">\s*<div class="kicker">Research tracks</div>', re.S)
    matches = list(marker_re.finditer(text))
    if len(matches) != 1:
        # Fallback: insert before the books section without altering URL structure.
        fallback = '<section class="section alt" id="works">'
        if text.count(fallback) != 1:
            raise RuntimeError("English home insertion markers unavailable")
        write_text(en_home, text.replace(fallback, EN_HOME_SECTION + "\n" + fallback, 1))
    else:
        idx = matches[0].start()
        write_text(en_home, text[:idx] + EN_HOME_SECTION + "\n" + text[idx:])


def update_book_pages() -> None:
    replace_card(ROOT / "books/sirou-fi-alard/index.html", AR_ROUTE, AR_BOOK_CARD, classes=("article-card",), required=True)
    replace_card(ROOT / "en/books/sirou-fi-alard/index.html", AR_ROUTE, EN_BOOK_CARD, classes=("article-card",), required=True)
    # German currently has no teaching card; insert after water dossier card.
    path = ROOT / "de/books/sirou-fi-alard/index.html"
    text = path.read_text(encoding="utf-8")
    if EN_ROUTE not in text:
        pattern = re.compile(r'(<article\b[^>]*class=["\'][^"\']*\barticle-card\b[^"\']*["\'][^>]*>.*?/en/articles/water-civilization-power/.*?</article>)', re.I | re.S)
        matches = list(pattern.finditer(text))
        if len(matches) != 1:
            raise RuntimeError(f"German Sirou water card marker count: {len(matches)}")
        match = matches[0]
        write_text(path, text[:match.end()] + DE_BOOK_CARD + text[match.end():])


def update_status_pages() -> None:
    for path, route, row in (
        (ROOT / "research-status/index.html", AR_ROUTE, AR_STATUS_ROW),
        (ROOT / "en/research-status/index.html", None, EN_STATUS_ROW),
    ):
        text = path.read_text(encoding="utf-8")
        pattern = re.compile(r'<tr><td><a href="(?:/articles/teaching-names-ai-understanding/|/en/articles/teaching-names-ai-understanding/)"[^>]*>.*?</tr>', re.S)
        matches = list(pattern.finditer(text))
        if len(matches) != 1:
            raise RuntimeError(f"{path.relative_to(ROOT)}: teaching status row count {len(matches)}")
        write_text(path, pattern.sub(row, text, count=1))


def update_quality_gate() -> None:
    path = ROOT / "tools/editorial_quality_gate.py"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"\s*'articles/teaching-names-ai-understanding/index\.html':dict\([^\n]+\),")
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise RuntimeError(f"editorial quality teaching rule count: {len(matches)}")
    replacement = (
        "\n 'articles/teaching-names-ai-understanding/index.html':dict(words=4300,sources=20,book='books/sirou-fi-alard/index.html',route='/articles/teaching-names-ai-understanding/',medical=False,extended=True),"
        "\n 'en/articles/teaching-names-ai-understanding/index.html':dict(words=4700,sources=20,book='en/books/sirou-fi-alard/index.html',route='/en/articles/teaching-names-ai-understanding/',medical=False,extended=True),"
    )
    text = text[:matches[0].start()] + "".join(replacement) + text[matches[0].end():]
    primary_match = re.search(r"PRIMARY=\((.*?)\)\n", text, re.S)
    if not primary_match:
        raise RuntimeError("editorial quality PRIMARY tuple not found")
    current = primary_match.group(1)
    additions = [
        "'aclanthology.org'", "'proceedings.mlr.press'", "'proceedings.neurips.cc'",
        "'academic.oup.com'", "'eprints.soton.ac.uk'", "'pubmed.ncbi.nlm.nih.gov'",
        "'arxiv.org'", "'quran.com'", "'tafsir.app'"
    ]
    for domain in additions:
        if domain not in current:
            current += "," + domain
    text = text[:primary_match.start(1)] + current + text[primary_match.end(1):]
    route_old = "for route in ['/en/articles/ratq-fatq-big-bang/','/en/articles/water-civilization-power/','/en/articles/diagnostic-uncertainty-family-fear-coercive-authority/']:"
    if route_old in text:
        route_new = route_old[:-2] + ",'/en/articles/teaching-names-ai-understanding/']:"
        text = text.replace(route_old, route_new, 1)
    write_text(path, text)


def update_discovery_gate() -> None:
    path = ROOT / "tools/discovery_integrity.py"
    text = path.read_text(encoding="utf-8")
    if f'"{SLUG}",' not in text:
        marker = '    "diagnostic-uncertainty-family-fear-coercive-authority",\n'
        if text.count(marker) != 1:
            raise RuntimeError("discovery required slug marker not found")
        text = text.replace(marker, marker + f'    "{SLUG}",\n', 1)
    write_text(path, text)


def update_site_integrity() -> None:
    path = ROOT / ".github/workflows/site-integrity.yml"
    text = path.read_text(encoding="utf-8")
    compile_marker = "          tools/dossier11_integrity.py\n"
    if "tools/teaching_names_ai_integrity.py" not in text:
        if text.count(compile_marker) != 1:
            raise RuntimeError("site-integrity compile insertion marker not found")
        text = text.replace(compile_marker, compile_marker + "          tools/teaching_names_ai_integrity.py\n", 1)
    step_marker = "      - name: Validate canonical author identity aliases manifest and attribution boundaries\n"
    step = "      - name: Validate Teaching the Names and AI bilingual evidence pillar\n        run: python tools/teaching_names_ai_integrity.py\n\n"
    if step not in text:
        if text.count(step_marker) != 1:
            raise RuntimeError("site-integrity step insertion marker not found")
        text = text.replace(step_marker, step + step_marker, 1)
    write_text(path, text)


def update_visual_runner() -> None:
    path = ROOT / ".github/visual-review/run_visual_review.py"
    text = path.read_text(encoding="utf-8")
    tuple_marker = '    ("fear-evidence-en", "/en/articles/diagnostic-uncertainty-family-fear-coercive-authority/evidence/"),\n'
    tuples = (
        '    ("names-ai-ar", "/articles/teaching-names-ai-understanding/"),\n'
        '    ("names-ai-en", "/en/articles/teaching-names-ai-understanding/"),\n'
        '    ("names-ai-evidence-ar", "/articles/teaching-names-ai-understanding/evidence/"),\n'
        '    ("names-ai-evidence-en", "/en/articles/teaching-names-ai-understanding/evidence/"),\n'
    )
    if 'names-ai-ar' not in text:
        if text.count(tuple_marker) != 1:
            raise RuntimeError("visual runner TOP_PAGES marker not found")
        text = text.replace(tuple_marker, tuple_marker + tuples, 1)
    target_marker = '    ("fear-parallel-en", "/en/articles/diagnostic-uncertainty-family-fear-coercive-authority/", "#parallel-figure", "start"),\n'
    targets = (
        '    ("names-ai-matrix-ar", "/articles/teaching-names-ai-understanding/", "#ai-matrix-figure", "start"),\n'
        '    ("names-ai-protocol-ar", "/articles/teaching-names-ai-understanding/", "#ai-protocol-figure", "start"),\n'
        '    ("names-ai-matrix-en", "/en/articles/teaching-names-ai-understanding/", "#ai-matrix-figure", "start"),\n'
        '    ("names-ai-protocol-en", "/en/articles/teaching-names-ai-understanding/", "#ai-protocol-figure", "start"),\n'
    )
    if 'names-ai-matrix-ar' not in text:
        if text.count(target_marker) != 1:
            raise RuntimeError("visual runner TARGET_PAGES marker not found")
        text = text.replace(target_marker, target_marker + targets, 1)
    social_marker = '    Path("assets/social/diagnostic-uncertainty-family-fear-en.png"),\n'
    socials = (
        '    Path("assets/social/teaching-names-ai-understanding-ar.png"),\n'
        '    Path("assets/social/teaching-names-ai-understanding-en.png"),\n'
    )
    if 'assets/social/teaching-names-ai-understanding-ar.png' not in text:
        if text.count(social_marker) != 1:
            raise RuntimeError("visual runner SOCIAL_CARDS marker not found")
        text = text.replace(social_marker, social_marker + socials, 1)
    write_text(path, text)


def add_premerge_record() -> None:
    path = ROOT / ".github/TEACHING_NAMES_AI_PILLAR_13_PREMERGE.md"
    text = f'''# Teaching the Names and AI Pillar 13 — Pre-merge Record

**Date:** {DATE}  
**Branch:** `teaching-names-ai-pillar-13`  
**Status:** `BRANCH_B+ILD_AWAITING_VERIFIED_GATES`

## Contribution

The existing Arabic-only explainer is replaced at the same canonical URL by a complete Arabic/English evidence dossier. It introduces two explicitly unvalidated author syntheses—the Six-Layer Understanding Matrix and the 6×4 Protocol—and tests them against supporting and counter-evidence rather than using them as conclusions.

## Evidence package

- 12 bounded claims with Arabic and English wording, claim type, confidence, sources, and caveats.
- 25 sources through 2025, including classical exegesis, foundational papers, model/architecture papers, grounding and representation studies, causal-generalisation failures, multimodal and embodied systems, explanation-faithfulness work, and consciousness-science indicators.
- Four original accessible diagrams.
- Two complete evidence appendices.
- JSON, BibTeX, RIS, and CFF exports.
- Two reproducible 1200×630 social cards.

## Boundaries

- The forthcoming Sirou manuscript is thematic origin, never technical evidence.
- Decodable representation is not automatically causal use.
- Multimodal/robotic performance is not subjective experience.
- Model self-report is not an independent consciousness measurement.
- The 2025 spatial causal-intervention paper is labelled an emerging preprint, not peer-reviewed settlement.
- No NLP or philosophy-of-AI specialist has yet independently reviewed this edition.

## Required release gate

Do not merge until fresh pull-request runs of `Site integrity` and `Visual review` pass on the final head and the Arabic/English article, appendices, diagrams, and share cards have been visually inspected.
'''
    write_text(path, text)


def update_workplan() -> None:
    path = ROOT / ".github/TEACHING_NAMES_AI_PILLAR_13_WORKPLAN.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    text = text.replace("**الحالة:** `IN_PROGRESS — EVIDENCE_ARCHITECTURE`", "**الحالة:** `BRANCH_B+ILD — AWAITING_VERIFIED_GATES`")
    checks = {
        "- [ ] تثبيت سجل المصادر والادعاءات النهائي.": "- [x] تثبيت سجل المصادر والادعاءات النهائي (12 ادعاءً، 25 مصدرًا).",
        "- [ ] كتابة النسخة العربية الجديدة.": "- [x] كتابة النسخة العربية الجديدة.",
        "- [ ] تحرير النسخة الإنجليزية.": "- [x] تحرير النسخة الإنجليزية تحريرًا مستقلًا.",
        "- [ ] بناء ملاحق الأدلة والرسوم والاستشهادات.": "- [x] بناء ملاحق الأدلة والرسوم والاستشهادات وبطاقات المشاركة.",
        "- [ ] تكامل الاكتشاف والفحوص.": "- [x] تكامل الاكتشاف وإضافة بوابة دائمة؛ بانتظار تشغيل الفرع وPull Request.",
    }
    for old, new in checks.items():
        text = text.replace(old, new)
    write_text(path, text)


def main() -> None:
    # Confirm the release archive has already overlaid the canonical content.
    for path in (
        ROOT / "articles/teaching-names-ai-understanding/index.html",
        ROOT / "en/articles/teaching-names-ai-understanding/index.html",
        ROOT / "tools/teaching_names_ai_integrity.py",
    ):
        if not path.exists():
            raise FileNotFoundError(path)

    update_research_index()
    update_inventory()
    update_json_feed(ROOT / "articles/feed.json", "ar")
    update_json_feed(ROOT / "en/articles/feed.json", "en")
    update_atom(ROOT / "articles/feed.xml", "ar")
    update_atom(ROOT / "en/articles/feed.xml", "en")
    update_sitemap()
    update_visible_surfaces()
    update_book_pages()
    update_status_pages()
    update_quality_gate()
    update_discovery_gate()
    update_site_integrity()
    update_visual_runner()
    add_premerge_record()
    update_workplan()

    # Validate JSON/XML immediately after integration.
    for path in (
        ROOT / "articles/research-index.json",
        ROOT / "data/content-inventory.json",
        ROOT / "articles/feed.json",
        ROOT / "en/articles/feed.json",
        ROOT / "articles/teaching-names-ai-understanding/evidence/claims.json",
    ):
        json.loads(path.read_text(encoding="utf-8"))
    for path in (
        ROOT / "sitemap.xml",
        ROOT / "articles/feed.xml",
        ROOT / "en/articles/feed.xml",
        ROOT / "assets/figures/ai-understanding-matrix-ar.svg",
        ROOT / "assets/figures/ai-understanding-matrix-en.svg",
        ROOT / "assets/figures/ai-understanding-6x4-ar.svg",
        ROOT / "assets/figures/ai-understanding-6x4-en.svg",
    ):
        ET.parse(path)
    print("AI pillar 13 integrated across content, discovery, books, status, CI, and visual review")


if __name__ == "__main__":
    main()
