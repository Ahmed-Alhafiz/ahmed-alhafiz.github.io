#!/usr/bin/env python3
"""Integrate dossier 11 across feeds, hubs, books, review registers and gates."""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "diagnostic-uncertainty-family-fear-coercive-authority"
AR_URL = f"https://ahmed-alhafiz.github.io/articles/{SLUG}/"
EN_URL = f"https://ahmed-alhafiz.github.io/en/articles/{SLUG}/"
AR_ROUTE = f"/articles/{SLUG}/"
EN_ROUTE = f"/en/articles/{SLUG}/"
DATE = "2026-09-02"
STAMP = "2026-09-02T10:00:00+02:00"
REVIEW = "author_review_complete_specialist_review_pending"
AR_TITLE = "حين يحكم الخوف قبل التشخيص: كيف يتحول الغموض إلى سلطة وإكراه داخل الأسرة؟"
EN_TITLE = "When Fear Decides Before Diagnosis: How Uncertainty Becomes Authority and Coercion in Families"
AR_SUMMARY = "ملف بحثي موسع يشرح سلسلة انتقال العرض الملتبس من عدم اليقين وخوف الأسرة إلى اليقين المبكر ونقل السلطة وتآكل الموافقة، ويقترح مسار أمان موازيا يحفظ التقييم وصوت الشخص والدعم الديني الطوعي."
EN_SUMMARY = "An evidence-led dossier on how an ambiguous symptom can move through family fear, premature certainty, authority transfer and consent erosion—and how a parallel-path safeguard preserves assessment, voice and voluntary spiritual support."

SCRIPT_RE = re.compile(
    r"(<script\b[^>]*\btype=[\"']application/ld\+json[\"'][^>]*>)(.*?)(</script>)",
    re.IGNORECASE | re.DOTALL,
)

AR_HUB_BLOCK = f'''
<section class="section"><div class="wrap"><div class="kicker">ملف بحثي ثنائي اللغة · السلامة التشخيصية · الإصدار 1.0</div><h2>حين يحكم الخوف قبل التشخيص</h2><div class="rule"></div><div class="feature-index"><article class="primary-story"><div><div class="kicker">عدم اليقين · خوف الأسرة · الموافقة · الإكراه</div><h2><a href="{AR_ROUTE}">{AR_TITLE}</a></h2><p>إطار أصلي من سبع مراحل يشرح كيف يصبح الخوف نظام قرار، ثم يقابله بمسار أمان موازٍ يحفظ التقييم متعدد الفرضيات، وصوت الشخص، وحدود الجسد، والدعم الديني الطوعي غير الحصري.</p></div><div><div class="story-meta"><span>عربي وإنجليزي كاملان</span><span>14 ادعاءً مصنفًا</span><span>19 مصدرًا مشروحًا</span><span>مراجعة طب نفسي/سلامة تشخيصية: لم تتم بعد</span></div><div class="actions"><a class="btn light" href="{AR_ROUTE}">فتح الملف الكامل</a><a class="btn light" href="{AR_ROUTE}evidence/">سجل الادعاءات والأدلة</a><a class="btn light" href="{EN_ROUTE}">النسخة الإنجليزية</a></div></div></article><figure class="figure-card"><img src="/assets/figures/fear-certainty-authority-cascade-ar.svg" width="1200" height="760" alt="سلسلة الخوف واليقين والسلطة في سبع مراحل" loading="lazy"><figcaption>الواقعة الملتبسة لا تقود حتمًا إلى الضرر. يمكن قطع السلسلة بالتقييم، وشفافية عدم اليقين، والموافقة، والمتابعة.</figcaption></figure></div></div></section>
'''.strip()

EN_HUB_BLOCK = f'''
<section class="section"><div class="wrap"><div class="kicker">Complete bilingual dossier · diagnostic safety · version 1.0</div><h2>When Fear Decides Before Diagnosis</h2><div class="rule"></div><div class="feature-index"><article class="primary-story"><div><div class="kicker">Uncertainty · family fear · consent · coercion</div><h2><a href="{EN_ROUTE}">{EN_TITLE}</a></h2><p>An original seven-stage cascade explains how fear can become a decision system. A parallel safeguard keeps multiple hypotheses, assessment, the person’s voice, bodily boundaries, and voluntary non-exclusive spiritual support in view at the same time.</p></div><div><div class="story-meta"><span>Complete Arabic and English editions</span><span>14 classified claims</span><span>19 annotated sources</span><span>Independent psychiatry/diagnostic-safety review: not completed</span></div><div class="actions"><a class="btn light" href="{EN_ROUTE}">Read the full dossier</a><a class="btn light" href="{EN_ROUTE}evidence/">Claim and evidence register</a><a class="btn light" href="{AR_ROUTE}">النسخة العربية</a></div></div></article><figure class="figure-card"><img src="/assets/figures/fear-certainty-authority-cascade-en.svg" width="1200" height="760" alt="The seven-stage Fear–Certainty–Authority Cascade" loading="lazy"><figcaption>An ambiguous event does not inevitably end in harm. Assessment, transparent uncertainty, consent, and review can interrupt the chain.</figcaption></figure></div></div></section>
'''.strip()

AR_HOME_BLOCK = f'''
<section class="section" id="fear-before-diagnosis"><div class="wrap"><div class="kicker">ملف جديد ثنائي اللغة · العقل والأسرة والسلطة</div><h2>الخوف ليس تشخيصًا، واليقين لا يمنح حق السيطرة</h2><div class="rule"></div><div class="featured-grid"><article class="featured-dossier"><div><div class="kicker">السلامة التشخيصية · الموافقة · حماية الأسرة</div><h3><a href="{AR_ROUTE}">حين يحكم الخوف قبل التشخيص</a></h3><p>يفصل الملف بين الواقعة والتفسير والقرار، ويكشف كيف ينتقل الخوف إلى يقين مبكر ثم إلى سلطة على الجسد والعلاج. يتضمن إطارين أصليين، وسجلًا من 14 ادعاءً و19 مصدرًا، ونسخة إنجليزية كاملة.</p><div class="evidence-row"><span>سلسلة تحليلية أصلية</span><span>مسار أمان موازٍ</span><span>ملحق JSON وBibTeX وRIS</span><span>مراجعة اختصاصية معلّقة</span></div></div><div class="actions"><a class="btn light" href="{AR_ROUTE}">اقرأ الملف</a><a class="btn light" href="{EN_ROUTE}">Read in English</a><a class="btn light" href="{AR_ROUTE}evidence/">ملحق الأدلة</a></div></article><figure class="figure-card"><img src="/assets/figures/parallel-path-safeguard-ar.svg" width="1200" height="760" alt="مسار الأمان الموازي الذي يضع الشخص في مركز السلامة والتقييم والموافقة" loading="lazy"><figcaption>الشخص في المركز؛ ويمكن أن يعمل التقييم والدعم العائلي والديني الطوعي بالتوازي من دون إلغاء السلامة أو الموافقة.</figcaption></figure></div></div></section>
'''.strip()

EN_HOME_BLOCK = f'''
<section class="section" id="fear-before-diagnosis"><div class="wrap"><div class="kicker">New complete bilingual dossier · mind, family and authority</div><h2>Fear is not a diagnosis, and certainty is not permission to control</h2><div class="rule"></div><div class="featured-grid"><article class="featured-dossier"><div><div class="kicker">Diagnostic safety · consent · family safeguarding</div><h3><a href="{EN_ROUTE}">When Fear Decides Before Diagnosis</a></h3><p>The dossier separates event, interpretation, and action, then maps how family fear can become premature certainty and power over the person’s body and care. It includes two original frameworks, 14 classified claims, 19 sources, and a full Arabic edition.</p><div class="evidence-row"><span>Original analytical cascade</span><span>Parallel-path safeguard</span><span>JSON, BibTeX, RIS, and CFF</span><span>Specialist review pending</span></div></div><div class="actions"><a class="btn light" href="{EN_ROUTE}">Read the dossier</a><a class="btn light" href="{AR_ROUTE}">اقرأ بالعربية</a><a class="btn light" href="{EN_ROUTE}evidence/">Evidence register</a></div></article><figure class="figure-card"><img src="/assets/figures/parallel-path-safeguard-en.svg" width="1200" height="760" alt="The person-centred Parallel-Path Safeguard" loading="lazy"><figcaption>The person remains central while assessment, family support, consent and voluntary spiritual support run without cancelling one another.</figcaption></figure></div></div></section>
'''.strip()

AR_BOOK_CARD = f'''<article class="article-card"><div><div class="kicker">ملف ثنائي اللغة · عدم اليقين والسلطة</div><h2><a href="{AR_ROUTE}">حين يحكم الخوف قبل التشخيص</a></h2><p>تحليل لمسار يتحول فيه العرض الملتبس إلى خوف عائلي ويقين مبكر ونقل للسلطة وتآكل للموافقة، مع بديل يحفظ التقييم وصوت الشخص.</p></div><span class="tag">افتح الملف</span></article>'''
EN_BOOK_CARD = f'''<article class="article-card"><div><div class="kicker">Complete bilingual dossier · uncertainty and authority</div><h2><a href="{EN_ROUTE}">When Fear Decides Before Diagnosis</a></h2><p>How an ambiguous event can become family fear, premature certainty, authority transfer and consent erosion—and how to interrupt the chain.</p></div><span class="tag">Open</span></article>'''
DE_BOOK_CARD = f'''<article class="article-card"><div><div class="kicker">Vollständiges englisches Dossier</div><h2><a href="{EN_ROUTE}" hreflang="en">When Fear Decides Before Diagnosis</a></h2><p>Wie Unsicherheit durch Familienangst zu vorschneller Gewissheit, Machtübertragung und beschädigter Zustimmung werden kann.</p></div><span class="tag">Öffnen</span></article>'''

AR_STATUS_ROW = f'''<tr><td><a href="{AR_ROUTE}">الخوف قبل التشخيص: عدم اليقين والأسرة والسلطة</a></td><td>ملف بحثي موسع ثنائي اللغة</td><td>1.0</td><td>2 سبتمبر 2026</td><td><span class="confidence open">مراجعة طب نفسي/سلامة تشخيصية معلّقة</span></td><td><a href="/books/umm-abbas/">أم عباس</a> — منشأ موضوعي لا دليل طبي</td></tr>'''
EN_STATUS_ROW = f'''<tr><td><a href="{EN_ROUTE}">When Fear Decides Before Diagnosis</a></td><td>Complete bilingual research dossier</td><td>1.0</td><td>2 September 2026</td><td><span class="confidence open">Psychiatry/diagnostic-safety review pending</span></td><td><a href="/en/books/umm-abbas/">Umm Abbas</a> — thematic origin, not medical evidence</td></tr>'''

COMPANION_BLOCK = f'''<div class="key-takeaway"><strong>الملف المكمل: ماذا يحدث قبل دخول صاحب السلطة؟</strong><p><a href="{AR_ROUTE}">حين يحكم الخوف قبل التشخيص</a> يحلل السلسلة السابقة للاستغلال: العرض الملتبس، وخوف الأسرة، واليقين المبكر، ونقل القرار، وتآكل الموافقة. هذا الرابط يكمل ملف الحدود ولا يكرره.</p></div>'''

AR_INDEX_ITEM = {
    "slug": SLUG,
    "title": AR_TITLE,
    "english_title": EN_TITLE,
    "summary": AR_SUMMARY,
    "english_summary": EN_SUMMARY,
    "type": "ملف بحثي موسع",
    "version": "1.0",
    "languages": ["ar", "en"],
    "review": REVIEW,
    "book": "umm-abbas",
    "url": AR_URL,
    "english_url": EN_URL,
    "evidence_appendix": AR_URL + "evidence/",
    "english_evidence_appendix": EN_URL + "evidence/",
    "claims_json": AR_URL + "evidence/claims.json",
    "citation_bib": AR_URL + "citation.bib",
    "citation_ris": AR_URL + "citation.ris",
    "citation_cff": AR_URL + "CITATION.cff"
}


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def insert_once(path: Path, marker: str, block: str, *, before: bool = True) -> None:
    text = path.read_text(encoding="utf-8")
    if AR_ROUTE in text and block in text:
        return
    count = text.count(marker)
    if count != 1:
        raise RuntimeError(f"{path.relative_to(ROOT)}: expected one insertion marker, found {count}: {marker[:90]!r}")
    replacement = block + "\n" + marker if before else marker + "\n" + block
    write_text(path, text.replace(marker, replacement, 1))


def rewrite_jsonld(path: Path, callback) -> None:
    text = path.read_text(encoding="utf-8")
    changed = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal changed
        data = json.loads(match.group(2))
        if callback(data):
            changed += 1
        return match.group(1) + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + match.group(3)

    revised = SCRIPT_RE.sub(repl, text)
    if changed == 0:
        raise RuntimeError(f"{path.relative_to(ROOT)}: JSON-LD target was not updated")
    write_text(path, revised)


def walk(value):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def update_itemlist(path: Path, list_id: str, url: str, name: str, *, after_url: str | None = None) -> None:
    def callback(data: object) -> bool:
        changed = False
        for node in walk(data):
            if not isinstance(node, dict) or node.get("@type") != "ItemList" or node.get("@id") != list_id:
                continue
            items = node.setdefault("itemListElement", [])
            if any(item.get("url") == url for item in items if isinstance(item, dict)):
                return False
            entry = {"@type": "ListItem", "position": 0, "url": url, "name": name}
            index = len(items)
            if after_url:
                for position, item in enumerate(items):
                    if isinstance(item, dict) and item.get("url") == after_url:
                        index = position + 1
                        break
            items.insert(index, entry)
            for position, item in enumerate(items, 1):
                item["position"] = position
            node["numberOfItems"] = len(items)
            changed = True
        for node in walk(data):
            if isinstance(node, dict) and node.get("@type") in {"CollectionPage", "ProfilePage"}:
                node["dateModified"] = DATE
        return changed

    rewrite_jsonld(path, callback)


def add_medical_webpage(path: Path) -> None:
    def callback(data: object) -> bool:
        changed = False
        for node in walk(data):
            if not isinstance(node, dict):
                continue
            node_type = node.get("@type")
            node_id = str(node.get("@id", ""))
            if node_type == "WebPage" and node_id.endswith("/#page"):
                node["@type"] = ["WebPage", "MedicalWebPage"]
                node["audience"] = {"@type": "PeopleAudience", "audienceType": "Families, patients, carers, and general readers"}
                changed = True
        return changed

    rewrite_jsonld(path, callback)


def patch_article_safety() -> None:
    path = ROOT / f"articles/{SLUG}/index.html"
    text = path.read_text(encoding="utf-8")
    old = "هذا الملف للتثقيف والتحليل، وليس لتشخيص شخص بعينه."
    new = "هذه مادة تثقيفية عامة للتحليل، وليست تشخيصًا لشخص بعينه."
    if text.count(old) != 1:
        raise RuntimeError(f"Arabic safety phrase count: {text.count(old)}")
    write_text(path, text.replace(old, new, 1))

    path = ROOT / f"en/articles/{SLUG}/index.html"
    text = path.read_text(encoding="utf-8")
    old = "This is educational analysis, not individual medical advice."
    new = "This is educational analysis, not a diagnosis or individual medical advice."
    if text.count(old) != 1:
        raise RuntimeError(f"English safety phrase count: {text.count(old)}")
    write_text(path, text.replace(old, new, 1))


def update_research_index() -> None:
    path = ROOT / "articles/research-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data["items"]
    if any(item.get("slug") == SLUG for item in items):
        raise RuntimeError("research index already contains dossier 11")
    position = next((i + 1 for i, item in enumerate(items) if item.get("slug") == "water-civilization-power"), 0)
    items.insert(position, AR_INDEX_ITEM)
    data["generated"] = DATE
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_json_feed(path: Path, *, english: bool) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    url = EN_URL if english else AR_URL
    if any(item.get("url") == url for item in data["items"]):
        raise RuntimeError(f"{path}: dossier entry already exists")
    entry = {
        "id": url,
        "url": url,
        "title": EN_TITLE if english else AR_TITLE,
        "summary": EN_SUMMARY if english else AR_SUMMARY,
        "date_published": STAMP,
        "date_modified": STAMP,
        "tags": [
            "extended research dossier" if english else "ملف بحثي موسع",
            REVIEW,
            "umm-abbas",
            "diagnostic safety" if english else "السلامة التشخيصية",
            "consent" if english else "الموافقة"
        ],
        "language": "en" if english else "ar"
    }
    position = next((i + 1 for i, item in enumerate(data["items"]) if "water-civilization-power" in item.get("url", "")), 0)
    data["items"].insert(position, entry)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def q(tag: str) -> str:
    return f"{{http://www.w3.org/2005/Atom}}{tag}"


def update_atom(path: Path, *, english: bool) -> None:
    ET.register_namespace("", "http://www.w3.org/2005/Atom")
    tree = ET.parse(path)
    root = tree.getroot()
    url = EN_URL if english else AR_URL
    if any(entry.find(q("link")).get("href") == url for entry in root.findall(q("entry")) if entry.find(q("link")) is not None):
        raise RuntimeError(f"{path}: dossier Atom entry already exists")
    updated = root.find(q("updated"))
    if updated is None:
        raise RuntimeError(f"{path}: feed updated node missing")
    updated.text = STAMP
    entry = ET.Element(q("entry"))
    ET.SubElement(entry, q("title")).text = EN_TITLE if english else AR_TITLE
    ET.SubElement(entry, q("link"), {"href": url})
    ET.SubElement(entry, q("id")).text = url
    ET.SubElement(entry, q("published")).text = STAMP
    ET.SubElement(entry, q("updated")).text = STAMP
    ET.SubElement(entry, q("category"), {"term": "extended research dossier" if english else "ملف بحثي موسع"})
    ET.SubElement(entry, q("summary")).text = EN_SUMMARY if english else AR_SUMMARY
    entries = root.findall(q("entry"))
    index = len(root)
    for existing in entries:
        link = existing.find(q("link"))
        if link is not None and "water-civilization-power" in link.get("href", ""):
            index = list(root).index(existing) + 1
            break
    root.insert(index, entry)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def update_sitemap() -> None:
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    tree = ET.parse(ROOT / "sitemap.xml")
    root = tree.getroot()
    loc_tag = f"{{{namespace}}}loc"
    urls = {node.text for node in root.findall(f"{{{namespace}}}url/{loc_tag}")}
    additions = (AR_URL, AR_URL + "evidence/", EN_URL, EN_URL + "evidence/")
    if any(url in urls for url in additions):
        raise RuntimeError("sitemap already contains one or more dossier 11 URLs")
    for url in additions:
        node = ET.SubElement(root, f"{{{namespace}}}url")
        ET.SubElement(node, loc_tag).text = url
        ET.SubElement(node, f"{{{namespace}}}lastmod").text = DATE
    ET.indent(tree, space="  ")
    tree.write(ROOT / "sitemap.xml", encoding="utf-8", xml_declaration=True)


def patch_hubs_and_home() -> None:
    update_itemlist(ROOT / "articles/index.html", "https://ahmed-alhafiz.github.io/articles/#list", AR_URL, AR_TITLE, after_url="https://ahmed-alhafiz.github.io/articles/water-civilization-power/")
    insert_once(ROOT / "articles/index.html", '<section class="section alt"><div class="wrap"><div class="kicker">ملفات موسعة باللغة العربية</div>', AR_HUB_BLOCK)

    update_itemlist(ROOT / "en/articles/index.html", "https://ahmed-alhafiz.github.io/en/articles/#list", EN_URL, EN_TITLE, after_url="https://ahmed-alhafiz.github.io/en/articles/water-civilization-power/")
    insert_once(ROOT / "en/articles/index.html", '<section class="section alt"><div class="wrap"><div class="kicker">Publication model</div>', EN_HUB_BLOCK)

    update_itemlist(ROOT / "index.html", "https://ahmed-alhafiz.github.io/#featured-research", AR_URL, "الخوف قبل التشخيص: عدم اليقين والأسرة والسلطة", after_url="https://ahmed-alhafiz.github.io/articles/water-civilization-power/")
    insert_once(ROOT / "index.html", '<section class="section"><div class="wrap"><div class="kicker">Research tracks</div>', AR_HOME_BLOCK)

    update_itemlist(ROOT / "en/index.html", "https://ahmed-alhafiz.github.io/en/#featured-research", EN_URL, "When Fear Decides Before Diagnosis", after_url="https://ahmed-alhafiz.github.io/en/articles/water-civilization-power/")
    insert_once(ROOT / "en/index.html", '<section class="section"><div class="wrap"><div class="kicker">Research tracks</div>', EN_HOME_BLOCK)


def patch_books() -> None:
    insert_once(
        ROOT / "books/umm-abbas/index.html",
        '<div class="article-list"><article class="article-card"><div><div class="kicker">ملف مستقل</div><h2><a href="/articles/spiritual-healing-exploitation-safeguarding/">',
        AR_BOOK_CARD,
        before=False,
    )
    # The previous helper inserts after the marker, which would split the first card.
    path = ROOT / "books/umm-abbas/index.html"
    text = path.read_text(encoding="utf-8")
    broken = '<div class="article-list"><article class="article-card"><div><div class="kicker">ملف مستقل</div><h2><a href="/articles/spiritual-healing-exploitation-safeguarding/">\n' + AR_BOOK_CARD
    if broken in text:
        text = text.replace(broken, '<div class="article-list">' + AR_BOOK_CARD + '<article class="article-card"><div><div class="kicker">ملف مستقل</div><h2><a href="/articles/spiritual-healing-exploitation-safeguarding/">', 1)
        write_text(path, text)
    elif AR_BOOK_CARD not in text:
        raise RuntimeError("Arabic Umm Abbas card insertion failed")

    path = ROOT / "en/books/umm-abbas/index.html"
    marker = '<div class="article-list"><article class="article-card"><div><div class="kicker">Arabic independent dossier</div><h2><a href="/articles/spiritual-healing-exploitation-safeguarding/" hreflang="ar">'
    text = path.read_text(encoding="utf-8")
    if text.count(marker) != 1:
        raise RuntimeError(f"English Umm Abbas marker count: {text.count(marker)}")
    write_text(path, text.replace(marker, '<div class="article-list">' + EN_BOOK_CARD + '<article class="article-card"><div><div class="kicker">Arabic independent dossier</div><h2><a href="/articles/spiritual-healing-exploitation-safeguarding/" hreflang="ar">', 1))

    path = ROOT / "de/books/umm-abbas/index.html"
    marker = '<div class="article-list"><article class="article-card"><div><div class="kicker">Thematisch verbunden</div><h2><a href="/articles/spiritual-healing-exploitation-safeguarding/">'
    text = path.read_text(encoding="utf-8")
    if text.count(marker) != 1:
        raise RuntimeError(f"German Umm Abbas marker count: {text.count(marker)}")
    write_text(path, text.replace(marker, '<div class="article-list">' + DE_BOOK_CARD + '<article class="article-card"><div><div class="kicker">Thematisch verbunden</div><h2><a href="/articles/spiritual-healing-exploitation-safeguarding/">', 1))


def patch_status() -> None:
    path = ROOT / "research-status/index.html"
    text = path.read_text(encoding="utf-8")
    marker = "<tbody><tr><td><a href=\"/articles/water-civilization-power/\">"
    if text.count(marker) != 1:
        raise RuntimeError(f"Arabic status tbody marker count: {text.count(marker)}")
    write_text(path, text.replace(marker, "<tbody>" + AR_STATUS_ROW + '<tr><td><a href="/articles/water-civilization-power/">', 1))

    path = ROOT / "en/research-status/index.html"
    text = path.read_text(encoding="utf-8")
    marker = "<tbody><tr><td><a href=\"/en/articles/water-civilization-power/\">"
    if text.count(marker) != 1:
        raise RuntimeError(f"English status tbody marker count: {text.count(marker)}")
    write_text(path, text.replace(marker, "<tbody>" + EN_STATUS_ROW + '<tr><td><a href="/en/articles/water-civilization-power/">', 1))


def patch_companion() -> None:
    path = ROOT / "articles/spiritual-healing-exploitation-safeguarding/index.html"
    text = path.read_text(encoding="utf-8")
    if AR_ROUTE in text:
        return
    marker = '<div class="related-work">'
    if text.count(marker) != 1:
        raise RuntimeError(f"Companion related-work marker count: {text.count(marker)}")
    write_text(path, text.replace(marker, COMPANION_BLOCK + marker, 1))


def patch_quality_gate() -> None:
    path = ROOT / "tools/editorial_quality_gate.py"
    text = path.read_text(encoding="utf-8")
    marker = " 'en/articles/water-civilization-power/index.html':dict(words=4000,sources=18,book='en/books/sirou-fi-alard/index.html',route='/en/articles/water-civilization-power/',medical=False,extended=True),\n"
    addition = (
        " 'articles/diagnostic-uncertainty-family-fear-coercive-authority/index.html':dict(words=3500,sources=15,book='books/umm-abbas/index.html',route='/articles/diagnostic-uncertainty-family-fear-coercive-authority/',medical=True,extended=True),\n"
        " 'en/articles/diagnostic-uncertainty-family-fear-coercive-authority/index.html':dict(words=3600,sources=15,book='en/books/umm-abbas/index.html',route='/en/articles/diagnostic-uncertainty-family-fear-coercive-authority/',medical=True,extended=True),\n"
    )
    if text.count(marker) != 1:
        raise RuntimeError(f"Quality RULES marker count: {text.count(marker)}")
    text = text.replace(marker, marker + addition, 1)
    text = text.replace("'ascelibrary.org')", "'ascelibrary.org','ahrq.gov','nice.org.uk','gmc-uk.org','nationalacademies.org','nap.nationalacademies.org')", 1)
    old = "if (rel.startswith(('articles/ratq','en/articles/ratq')) or 'water-civilization-power' in rel) and not n.get('mentions')"
    new = "if (rel.startswith(('articles/ratq','en/articles/ratq')) or 'water-civilization-power' in rel or 'diagnostic-uncertainty-family-fear-coercive-authority' in rel) and not n.get('mentions')"
    if text.count(old) != 1:
        raise RuntimeError("Quality mentions condition not found")
    text = text.replace(old, new, 1)
    required_marker = "'articles/water-civilization-power/CITATION.cff',"
    required_add = "'articles/diagnostic-uncertainty-family-fear-coercive-authority/evidence/index.html','en/articles/diagnostic-uncertainty-family-fear-coercive-authority/evidence/index.html','articles/diagnostic-uncertainty-family-fear-coercive-authority/evidence/claims.json','articles/diagnostic-uncertainty-family-fear-coercive-authority/evidence/references.bib','articles/diagnostic-uncertainty-family-fear-coercive-authority/evidence/references.ris','articles/diagnostic-uncertainty-family-fear-coercive-authority/citation.bib','articles/diagnostic-uncertainty-family-fear-coercive-authority/citation.ris','articles/diagnostic-uncertainty-family-fear-coercive-authority/CITATION.cff','assets/figures/fear-certainty-authority-cascade-ar.svg','assets/figures/fear-certainty-authority-cascade-en.svg','assets/figures/parallel-path-safeguard-ar.svg','assets/figures/parallel-path-safeguard-en.svg',"
    if text.count(required_marker) != 1:
        raise RuntimeError("Quality required infrastructure marker not found")
    text = text.replace(required_marker, required_marker + required_add, 1)
    route_marker = "for route in ['/en/articles/ratq-fatq-big-bang/','/en/articles/water-civilization-power/']:"
    route_new = "for route in ['/en/articles/ratq-fatq-big-bang/','/en/articles/water-civilization-power/','/en/articles/diagnostic-uncertainty-family-fear-coercive-authority/']:"
    if text.count(route_marker) != 1:
        raise RuntimeError("Quality English route marker not found")
    text = text.replace(route_marker, route_new, 1)
    write_text(path, text)


def patch_discovery_gate() -> None:
    path = ROOT / "tools/discovery_integrity.py"
    text = path.read_text(encoding="utf-8")
    marker = '    "water-civilization-power",\n'
    if text.count(marker) != 1:
        raise RuntimeError(f"Discovery slug marker count: {text.count(marker)}")
    write_text(path, text.replace(marker, marker + f'    "{SLUG}",\n', 1))


def patch_site_integrity() -> None:
    path = ROOT / ".github/workflows/site-integrity.yml"
    text = path.read_text(encoding="utf-8")
    old = "tools/discovery_integrity.py tools/ux_integrity.py tools/arabic_ui_integrity.py"
    new = old + " tools/dossier11_integrity.py"
    if text.count(old) != 1:
        raise RuntimeError("Site integrity compile marker not found")
    text = text.replace(old, new, 1)
    marker = "      - name: Validate multilingual UX portrait footer contact covers and public identity integrity\n"
    step = "      - name: Validate fear-before-diagnosis bilingual dossier evidence and safety package\n        run: python tools/dossier11_integrity.py\n\n"
    if text.count(marker) != 1:
        raise RuntimeError("Site integrity step marker not found")
    text = text.replace(marker, step + marker, 1)
    write_text(path, text)


def patch_visual_review() -> None:
    path = ROOT / ".github/workflows/visual-review.yml"
    text = path.read_text(encoding="utf-8")
    marker = "            'water-en|/en/articles/water-civilization-power/'\n"
    addition = (
        f"            'fear-ar|{AR_ROUTE}'\n"
        f"            'fear-en|{EN_ROUTE}'\n"
        f"            'fear-evidence-ar|{AR_ROUTE}evidence/'\n"
        f"            'fear-evidence-en|{EN_ROUTE}evidence/'\n"
    )
    if text.count(marker) != 1:
        raise RuntimeError("Visual page inventory marker not found")
    text = text.replace(marker, marker + addition, 1)
    marker = "            'assets/social/water-civilization-power-en.png',\n"
    addition = (
        "            'assets/social/diagnostic-uncertainty-family-fear-ar.png',\n"
        "            'assets/social/diagnostic-uncertainty-family-fear-en.png',\n"
    )
    if text.count(marker) != 1:
        raise RuntimeError("Visual social-card marker not found")
    text = text.replace(marker, marker + addition, 1)
    # The runner computes expected counts from its tuples, so no numeric adjustment is needed.
    write_text(path, text)


def patch_cff() -> None:
    path = ROOT / f"articles/{SLUG}/CITATION.cff"
    text = path.read_text(encoding="utf-8")
    text = text.replace("license: CC-BY-NC-ND-4.0\n", "")
    write_text(path, text)


def normalize() -> None:
    for path in list(ROOT.rglob("*.html")) + list(ROOT.rglob("*.json")) + list(ROOT.rglob("*.xml")) + list(ROOT.rglob("*.svg")) + list(ROOT.rglob("*.bib")) + list(ROOT.rglob("*.ris")) + list(ROOT.rglob("*.cff")) + list(ROOT.rglob("*.py")) + list(ROOT.rglob("*.yml")):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        path.write_text("\n".join(line.rstrip() for line in text.rstrip().splitlines()) + "\n", encoding="utf-8")


def main() -> None:
    patch_article_safety()
    add_medical_webpage(ROOT / f"articles/{SLUG}/index.html")
    add_medical_webpage(ROOT / f"en/articles/{SLUG}/index.html")
    patch_cff()
    update_research_index()
    update_json_feed(ROOT / "articles/feed.json", english=False)
    update_json_feed(ROOT / "en/articles/feed.json", english=True)
    update_atom(ROOT / "articles/feed.xml", english=False)
    update_atom(ROOT / "en/articles/feed.xml", english=True)
    update_sitemap()
    patch_hubs_and_home()
    patch_books()
    patch_status()
    patch_companion()
    patch_quality_gate()
    patch_discovery_gate()
    patch_site_integrity()
    patch_visual_review()
    normalize()
    print("Integrated dossier 11 across bilingual discovery, books, review registers, feeds, sitemap and permanent gates")


if __name__ == "__main__":
    main()
