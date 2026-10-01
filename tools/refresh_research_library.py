#!/usr/bin/env python3
"""Build the three research hubs from existing published feed entries.

The hub's main element and matching ItemList are rebuilt. Article copy, URLs, language groups,
feeds, author identity and book publication states remain their own sources.
An unclassified new article fails visibly rather than silently disappearing.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from html import escape
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
TOPICS = {
    "cosmos": "quran-science-method-evidence ratq-fatq-big-bang six-days-creation-cosmic-time before-big-bang-science-limits age-of-universe-13-8-billion-years universe-expansion-wa-inna-lamusiun quran-day-thousand-fifty-thousand-years-relativity anzalna-iron-meteorites green-tree-fire-photosynthesis difference-light-nur-quran-sun-moon iron-fire-light-matter-energy".split(),
    "mind": "adam-all-languages-origin-language how-concepts-form-adam-names-scientific-models teaching-names-ai-understanding turing-test-ai-consciousness ai-soul-consciousness-understanding-taklif brain-consciousness-spirit-limits human-embryo-quran-stages dna-code-genetic-information water-life-molecular-properties".split(),
    "history": "civilization-knowledge-justice-collapse water-civilization-power river-civilizations-water-state marib-dam-sayl-al-arim how-khufu-pyramid-built-merer-diary madain-salih-thamud-nabataean-tombs mesopotamia-irrigation-soil-salinity-collapse nile-ancient-egypt-flood-calendar-state injustice-fall-of-states-quran-history writing-changed-human-history fall-of-baghdad-1258-ibn-al-alqami juhayman-grand-mosque-1979".split(),
    "psychology": "memory-gaps-unremembered-actions hearing-voices-in-head jinn-existence-quran-sunnah possession-or-neurological-psychological-disorder functional-seizures-vs-epilepsy sleep-paralysis-jathoom religious-ocd-scrupulosity spiritual-healing-exploitation-safeguarding diagnostic-uncertainty-family-fear-coercive-authority how-certainty-becomes-violence".split(),
    "literature": ["arabic-psychological-horror", "umm-abbas-family-fear"],
}
COPY = {
    "ar": {
        "kicker": "مركز أبحاث أحمد الحافظ", "title": "ملفات بحثية بمصادر قابلة للتتبع",
        "intro": "اختر موضوعًا، أو ابحث عن السؤال الذي يشغلك. مقالات وتحقيقات مرتبطة بعوالم المؤلفات، مع مصادر معلنة وحدود واضحة للأدلة.",
        "unit": "مادة", "edition": "في النسخة العربية", "topics_label": "تصفح حسب الموضوع", "search": "ابحث داخل المقالات", "placeholder": "مثل: الوعي، عمر الكون، الجاثوم…", "clear": "مسح البحث", "empty": "لا توجد نتيجة مطابقة. جرّب كلمة أخرى أو امسح البحث.",
        "read": "اقرأ المقال", "guide": "اقرأ الدليل", "updated": "تحديث", "article": "مقال وبحث", "guide_type": "دليل أدبي", "review": "مراجعة اختصاصية خارجية: لم تتم بعد", "status": "حالة الأبحاث والمراجعة", "note": "الكتاب يفتح السؤال؛ والمصادر المستقلة تسند البحث. اطّلع على حالة المراجعة وحدود كل مادة داخل صفحتها.",
        "availability": "النسخ المتاحة", "edition_note": "المقالات غير المترجمة تظهر في نسختها العربية فقط.", "hub_links": [("en", "الأبحاث بالإنجليزية"), ("de", "الأبحاث بالألمانية")],
        "topics": {"cosmos": ("الكون والقرآن", "الرتق والفتق والانفجار العظيم، وأيام الخلق، والمادة والطاقة."), "mind": ("الإنسان والذكاء والحياة", "الأسماء والمفاهيم والوعي، من تعلم الإنسان إلى سؤال الآلة."), "history": ("الحضارة والتاريخ", "الماء والمؤسسات والآثار: قراءة ما تقوله الوثائق وما يبقى مختلفًا عليه."), "psychology": ("النفس والمجتمع", "الأعراض والتفسير والخوف واليقين، مع احترام حدود التشخيص والسلامة."), "literature": ("القراءة والأدب", "مسار إلى العوالم الروائية وأسئلة القراءة.")},
        "languages": {"ar": "العربية", "en": "الإنجليزية", "de": "الألمانية"},
    },
    "en": {
        "kicker": "Research by Ahmed Alhafiz", "title": "Questions, evidence, and the limits of knowledge",
        "intro": "Find a question, choose a topic, and follow the sources. Research connected to the books, with evidence and review boundaries stated in each article.",
        "unit": "publications", "edition": "in English", "topics_label": "Browse by topic", "search": "Search the articles", "placeholder": "For example: consciousness, Baghdad, symptoms…", "clear": "Clear search", "empty": "No matching articles. Try another word or clear the search.",
        "read": "Read the article", "guide": "Read the guide", "updated": "Updated", "article": "Article and research", "guide_type": "Literary guide", "review": "Independent specialist review: not completed. These articles are not peer-reviewed.", "status": "Research and review status", "note": "The books open the questions; independent sources support the research. Each article states its review status and the limits of its claims.",
        "availability": "Available editions", "edition_note": "This page lists the published English editions. Further articles are available in Arabic; an Arabic link does not imply an English translation.", "hub_links": [("ar", "Browse all research in Arabic"), ("de", "Research in German")],
        "topics": {"cosmos": ("Cosmos and the Qur’an", "Cosmic origins, interpretation, and the boundaries of scientific comparison."), "mind": ("Mind, intelligence, and life", "Language, understanding, and the questions raised by human and machine intelligence."), "history": ("Civilization and history", "Water, institutions, and historical events through their sources."), "psychology": ("Psychology and society", "Symptoms, interpretation, fear, and group certainty; diagnosis and safeguarding remain distinct."), "literature": ("Reading and literature", "Paths into the books and the questions they raise.")},
        "languages": {"ar": "Arabic", "en": "English", "de": "German"},
    },
    "de": {
        "kicker": "Forschung von Ahmed Alhafiz", "title": "Fragen, Belege und die Grenzen des Wissens",
        "intro": "Wählen Sie ein Thema oder suchen Sie nach einer Frage. Texte aus dem Umfeld der Bücher, mit nachvollziehbaren Quellen und offen benannten Grenzen.",
        "unit": "Beiträge", "edition": "auf Deutsch", "topics_label": "Nach Thema lesen", "search": "Beiträge durchsuchen", "placeholder": "Zum Beispiel: Bagdad, Symptome, Gewissheit…", "clear": "Suche zurücksetzen", "empty": "Keine passenden Beiträge. Versuchen Sie ein anderes Wort oder setzen Sie die Suche zurück.",
        "read": "Beitrag lesen", "guide": "Leitfaden lesen", "updated": "Aktualisiert", "article": "Beitrag und Forschung", "guide_type": "Literarischer Leitfaden", "review": "Unabhängige fachliche Prüfung: noch nicht abgeschlossen", "status": "Forschungs- und Prüfstatus", "note": "Die Bücher werfen Fragen auf; unabhängige Quellen stützen die Forschung. Jeder Beitrag nennt seinen Prüfstatus und die Grenzen seiner Aussagen.",
        "availability": "Verfügbare Sprachfassungen", "edition_note": "Hier finden Sie die veröffentlichten deutschen Fassungen. Weitere Beiträge sind auf Arabisch oder Englisch verfügbar; sie werden nicht als deutsche Übersetzungen ausgegeben.", "hub_links": [("ar", "Alle Beiträge auf Arabisch"), ("en", "Forschung auf Englisch")],
        "topics": {"cosmos": ("Kosmos und Koran", "Kosmische Ursprünge, Auslegung und Grenzen wissenschaftlicher Vergleiche."), "mind": ("Mensch, Intelligenz und Leben", "Sprache, Verständnis und die Fragen menschlicher und künstlicher Intelligenz."), "history": ("Zivilisation und Geschichte", "Wasser, Institutionen und historische Ereignisse im Licht der Quellen."), "psychology": ("Psychologie und Gesellschaft", "Symptome, Deutung, Angst und Gruppengewissheit; Diagnose und Schutz bleiben getrennt."), "literature": ("Lesen und Literatur", "Wege in die Bücher und ihre Fragen.")},
        "languages": {"ar": "Arabisch", "en": "Englisch", "de": "Deutsch"},
    },
}

def tag_text(value: str) -> str:
    return escape(value, quote=True)

def build(lang: str, register: list[dict]) -> None:
    c = COPY[lang]
    prefix = "" if lang == "ar" else lang + "/"
    path = ROOT / prefix / "articles/index.html"
    feed = json.loads((ROOT / prefix / "articles/feed.json").read_text())["items"]
    by_url = {entry["url"]: entry for entry in feed}
    url_key = {"ar": "url", "en": "english_url", "de": "german_url"}[lang]
    published = [(item, by_url[item[url_key]]) for item in register if item.get(url_key)]
    assert len(published) == len(feed), f"{lang}: feed and research register disagree"
    slugs = {item["slug"] for item, _ in published}
    assert slugs <= {slug for values in TOPICS.values() for slug in values}, "Classify new research in TOPICS first"
    groups = [(topic, [(item, entry) for item, entry in published if item["slug"] in slugs_in_topic]) for topic, slugs_in_topic in TOPICS.items()]
    groups = [(topic, entries) for topic, entries in groups if entries]
    status = "/research-status/" if lang == "ar" else "/en/research-status/" if lang == "en" else "/de/articles/#review-note"
    parts = [f'<main id="main" class="research-library" data-library-lang="{lang}">',
             '<section class="research-hero"><div class="wrap">',
             f'<div class="kicker">{c["kicker"]}</div><h1>{c["title"]}</h1><p>{c["intro"]}</p>',
             f'<div class="library-edition"><strong>{len(feed)} {c["unit"]}</strong><span>{c["edition"]}</span></div>',
             '</div></section><section class="library-section"><div class="wrap library-layout">',
             f'<aside class="library-sidebar"><nav class="library-topics" aria-label="{c["topics_label"]}"><strong>{c["topics_label"]}</strong>']
    for topic, entries in groups:
        parts.append(f'<a href="#topic-{topic}"><span>{c["topics"][topic][0]}</span><small>{len(entries)}</small></a>')
    parts += ['</nav>', f'<div class="library-review" id="review-note"><p>{c["note"]}</p><p>{c["review"]}</p>']
    if lang != "de":
        parts.append(f'<a href="{status}">{c["status"]}</a>')
    parts += ['</div></aside><div class="library-content">',
              f'<form class="library-search" role="search" hidden><label for="article-search">{c["search"]}</label><div class="library-search-field"><input id="article-search" type="search" autocomplete="off" aria-describedby="library-search-example" aria-controls="library-groups"><button type="reset" class="library-clear">{c["clear"]}</button></div><p class="library-example" id="library-search-example">{c["placeholder"]}</p><p class="library-results" role="status" aria-live="polite" aria-atomic="true" data-total="{len(feed)}" data-unit="{c["unit"]}">{len(feed)} {c["unit"]}</p></form>',
              f'<p class="library-empty" hidden>{c["empty"]}</p><div id="library-groups">']
    ordered_entries = []
    for topic, entries in groups:
        entries.sort(key=lambda value: datetime.fromisoformat(value[1]["date_published"]), reverse=True)
        ordered_entries.extend(entry for _, entry in entries)
        label, description = c["topics"][topic]
        parts += [f'<section class="library-group" id="topic-{topic}" aria-labelledby="heading-{topic}"><div class="library-group-head"><div><h2 id="heading-{topic}">{label}</h2><p>{description}</p></div><span class="library-group-count">{len(entries):02d}</span></div><div class="library-entries">']
        for item, entry in entries:
            route = urlparse(entry["url"]).path
            is_guide = route.startswith("/guides/")
            modified_date = entry["date_modified"][:10]
            langs = " · ".join(c["languages"][v] for v in item["languages"])
            title, summary = tag_text(entry["title"]), tag_text(entry["summary"])
            parts += [f'<article class="library-entry" data-article="{item["slug"]}">',
                      f'<div class="library-entry-meta"><span>{c["guide_type"] if is_guide else c["article"]}</span><time datetime="{modified_date}">{c["updated"]} {modified_date}</time><small>{langs}</small></div>',
                      f'<div class="library-entry-copy"><h3><a href="{route}">{title}</a></h3><p>{summary}</p></div>',
                      f'<a class="library-read" href="{route}" aria-label="{c["guide"] if is_guide else c["read"]}: {title}"><span>{c["guide"] if is_guide else c["read"]}</span><span class="reading-arrow" aria-hidden="true">{"←" if lang == "ar" else "→"}</span></a>',
                      '</article>']
        parts += ['</div></section>']
    parts += ['</div>', f'<section class="library-language-note"><h2>{c["availability"]}</h2><p>{c["edition_note"]}</p><div class="actions">']
    for other, label in c["hub_links"]:
        route = "/articles/" if other == "ar" else f"/{other}/articles/"
        parts.append(f'<a class="btn" href="{route}" hreflang="{other}">{label}</a>')
    parts += ['</div></section></div></div></section></main>']
    source = path.read_text()
    source, count = re.subn(r'<main\b[^>]*>.*?</main>', "\n".join(parts), source, flags=re.S)
    assert count == 1, path
    schema_count = 0
    def sync_schema(match: re.Match) -> str:
        nonlocal schema_count
        data = json.loads(match[1])
        for node in data.get("@graph", []):
            if node.get("@type") == "ItemList":
                schema_count += 1
                node["numberOfItems"] = len(ordered_entries)
                node["itemListElement"] = [
                    {"@type": "ListItem", "position": pos, "url": entry["url"], "name": entry["title"]}
                    for pos, entry in enumerate(ordered_entries, 1)
                ]
        return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + '</script>'
    source = re.sub(r'<script type="application/ld\+json">(.*?)</script>', sync_schema, source, flags=re.S)
    assert schema_count == 1, f"{lang}: expected exactly one research ItemList"
    if '/assets/research-library.js' not in source:
        source = source.replace('</head>', '<script src="/assets/research-library.js" defer></script>\n</head>')
    path.write_text(source)
    print(f"{lang}: {len(feed)} published entries across {len(groups)} topics")

if __name__ == "__main__":
    register = json.loads((ROOT / "articles/research-index.json").read_text())["items"]
    for language in COPY:
        build(language, register)
