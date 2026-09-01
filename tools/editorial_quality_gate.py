#!/usr/bin/env python3
"""Editorial quality gate for published reference articles.

The repository integrity audit checks structural correctness. This companion
gate checks the minimum editorial traits that make a reference page useful:
a direct answer, substantial visible analysis, traceable sources, explicit
uncertainty, reciprocal book links, and additional safeguards on medical and
safeguarding pages.

It uses only the Python standard library so GitHub Actions can run it without
network access or third-party packages.
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://ahmed-alhafiz.github.io"

REFERENCE_ARTICLES = {
    "articles/ratq-fatq-big-bang/index.html": {
        "book": "books/sirou-fi-alard/index.html",
        "minimum_words": 1800,
        "medical": False,
        "medication_warning": False,
        "safeguarding": False,
        "medical_context_markers": (),
        "required_phrases": ("الانفجار العظيم", "الرتق والفتق"),
    },
    "articles/six-days-creation-cosmic-time/index.html": {
        "book": "books/sirou-fi-alard/index.html",
        "minimum_words": 2200,
        "medical": False,
        "medication_warning": False,
        "safeguarding": False,
        "medical_context_markers": (),
        "required_phrases": ("أيام الخلق الستة", "الزمن الكوني"),
    },
    "articles/teaching-names-ai-understanding/index.html": {
        "book": "books/sirou-fi-alard/index.html",
        "minimum_words": 2500,
        "medical": False,
        "medication_warning": False,
        "safeguarding": False,
        "medical_context_markers": (),
        "required_phrases": (
            "سُلّم الاسم",
            "تعليم آدم الأسماء",
            "Transformer",
            "لا يثبت وحده",
        ),
    },
    "articles/sleep-paralysis-jathoom/index.html": {
        "book": "books/umm-abbas/index.html",
        "minimum_words": 1800,
        "medical": True,
        "medication_warning": False,
        "safeguarding": False,
        "medical_context_markers": ("rem", "طب النوم", "شلل النوم"),
        "required_phrases": ("شلل النوم", "الجاثوم"),
    },
    "articles/functional-seizures-vs-epilepsy/index.html": {
        "book": "books/umm-abbas/index.html",
        "minimum_words": 2400,
        "medical": True,
        "medication_warning": True,
        "safeguarding": False,
        "medical_context_markers": (
            "فيديو-eeg",
            "video-eeg",
            "تخطيط كهربائية الدماغ",
        ),
        "required_phrases": ("النوبات الوظيفية", "الصرع"),
    },
    "articles/spiritual-healing-exploitation-safeguarding/index.html": {
        "book": "books/umm-abbas/index.html",
        "minimum_words": 2600,
        "medical": True,
        "medication_warning": True,
        "safeguarding": True,
        "medical_context_markers": (
            "الموافقة",
            "الرعاية الطبية",
            "الاحتيال الصحي",
        ),
        "required_phrases": (
            "اختبار الحدود الخمس",
            "حرية الانسحاب",
            "صون الجسد",
            "قابلية المساءلة",
        ),
    },
}

FORBIDDEN_CERTAINTY = (
    "يثبت نهائيًا",
    "يثبت قطعيًا علميًا",
    "يعالج حتمًا",
    "يضمن الشفاء",
    "تشخيص مؤكد من الفيديو",
    "لا يمكن أن يخطئ",
)

MEDICAL_SAFETY_GROUPS = (
    ("هذه مادة تثقيفية", "مادة تثقيفية عامة"),
    ("ليست تشخيصًا", "ليس تشخيصًا"),
    ("الطوارئ", "اطلب الإسعاف", "اتصل بالإسعاف", "تقييم عاجل"),
)

MEDICATION_WARNING = ("لا توقف", "لا تغيّر جرعة", "لا تغير جرعة")

SAFEGUARDING_GROUPS = (
    ("الموافقة", "قبول حر"),
    ("الاعتداء", "العنف الجنسي"),
    ("مكان آمن", "تعزيز الأمان"),
    ("خدمة حماية", "شرطة", "جهة قادرة على الحماية"),
    ("استشارة قانونية", "القانون المحلي"),
)

TRUSTED_HOST_SUFFIXES = (
    "aan.com",
    "neurology.org",
    "pubmed.ncbi.nlm.nih.gov",
    "pmc.ncbi.nlm.nih.gov",
    "ilae.org",
    "cdc.gov",
    "nhs.uk",
    "who.int",
    "ohchr.org",
    "fda.gov",
    "gov.uk",
    "nasa.gov",
    "esa.int",
    "usgs.gov",
    "arxiv.org",
    "aclanthology.org",
    "academic.oup.com",
    "eprints.soton.ac.uk",
    "science.org",
    "tafsir.app",
    "quran.com",
    "sunnah.com",
)


@dataclass
class ArticleData:
    text_parts: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    ids: set[str] = field(default_factory=set)
    classes: set[str] = field(default_factory=set)
    jsonld_buffers: list[str] = field(default_factory=list)
    _in_ignored: int = 0
    _in_jsonld: bool = False
    _json_buffer: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self.text_parts)).strip()


class Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.data = ArticleData()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag in {"style", "noscript"}:
            self.data._in_ignored += 1
        if tag == "script":
            if a.get("type", "").lower() == "application/ld+json":
                self.data._in_jsonld = True
                self.data._json_buffer = []
            else:
                self.data._in_ignored += 1
        if tag == "a" and a.get("href"):
            self.data.links.append(a["href"].strip())
        if a.get("id"):
            self.data.ids.add(a["id"].strip())
        for cls in a.get("class", "").split():
            self.data.classes.add(cls)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "script" and self.data._in_jsonld:
            raw = "".join(self.data._json_buffer).strip()
            if raw:
                self.data.jsonld_buffers.append(raw)
            self.data._in_jsonld = False
            self.data._json_buffer = []
        elif tag in {"script", "style", "noscript"} and self.data._in_ignored:
            self.data._in_ignored -= 1

    def handle_data(self, value: str) -> None:
        if self.data._in_jsonld:
            self.data._json_buffer.append(value)
        elif not self.data._in_ignored and value.strip():
            self.data.text_parts.append(value.strip())


def parse(path: Path) -> ArticleData:
    parser = Parser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    for raw in parser.data.jsonld_buffers:
        json.loads(raw)
    return parser.data


def word_count(text: str) -> int:
    return len(re.findall(r"[\u0600-\u06FF\w]+", text, flags=re.UNICODE))


def article_node(data: ArticleData) -> dict | None:
    def walk(value):
        if isinstance(value, dict):
            yield value
            graph = value.get("@graph")
            if isinstance(graph, list):
                for item in graph:
                    yield from walk(item)
        elif isinstance(value, list):
            for item in value:
                yield from walk(item)

    for raw in data.jsonld_buffers:
        obj = json.loads(raw)
        for node in walk(obj):
            types = node.get("@type")
            if types == "Article" or (isinstance(types, list) and "Article" in types):
                return node
    return None


def canonical_for_path(rel: str) -> str:
    parent = Path(rel).parent.as_posix().strip("/")
    return f"{BASE}/{parent}/"


def load_sitemap() -> set[str]:
    tree = ET.parse(ROOT / "sitemap.xml")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return {
        node.text.strip()
        for node in tree.findall("s:url/s:loc", ns)
        if node.text
    }


def load_feed_links() -> set[str]:
    tree = ET.parse(ROOT / "articles" / "feed.xml")
    ns = {"a": "http://www.w3.org/2005/Atom"}
    result: set[str] = set()
    for entry in tree.findall("a:entry", ns):
        for link in entry.findall("a:link", ns):
            href = link.attrib.get("href", "").strip()
            if href:
                result.add(href)
    return result


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    hub = (ROOT / "articles" / "index.html").read_text(encoding="utf-8")
    sitemap = load_sitemap()
    feed = load_feed_links()

    for rel, rules in REFERENCE_ARTICLES.items():
        path = ROOT / rel
        if not path.exists():
            errors.append(f"{rel}: missing reference article")
            continue

        data = parse(path)
        text = data.text
        lower = text.lower()
        count = word_count(text)
        url = canonical_for_path(rel)

        if count < rules["minimum_words"]:
            errors.append(
                f"{rel}: visible analysis is too short ({count} < {rules['minimum_words']} words)"
            )
        if "answer" not in data.ids or "summary-box" not in data.classes:
            errors.append(f"{rel}: missing direct-answer summary")
        for required_class in ("references", "citation-box", "related-work"):
            if required_class not in data.classes:
                errors.append(f"{rel}: missing .{required_class}")
        for phrase in rules["required_phrases"]:
            if phrase not in text:
                errors.append(f"{rel}: required analytical phrase missing: {phrase}")

        node = article_node(data)
        if node is None:
            errors.append(f"{rel}: missing Article JSON-LD")
            citations: list[str] = []
        else:
            raw_citations = node.get("citation", [])
            citations = raw_citations if isinstance(raw_citations, list) else []
            if len(citations) < 5:
                errors.append(f"{rel}: fewer than five machine-readable citations")
            if node.get("url") != url:
                errors.append(f"{rel}: Article URL does not match canonical route")
            if not node.get("abstract"):
                errors.append(f"{rel}: Article JSON-LD has no abstract")
            if node.get("isBasedOn") is None:
                errors.append(f"{rel}: Article JSON-LD has no isBasedOn book relation")

        external = [
            href for href in data.links
            if urlsplit(href).scheme in {"http", "https"}
            and urlsplit(href).netloc not in {"ahmed-alhafiz.github.io"}
        ]
        if len(set(external)) < 5:
            errors.append(f"{rel}: fewer than five unique visible external references")

        trusted = {
            urlsplit(href).netloc.lower()
            for href in external
            if any(urlsplit(href).netloc.lower().endswith(suffix) for suffix in TRUSTED_HOST_SUFFIXES)
        }
        if len(trusted) < 2:
            errors.append(f"{rel}: external evidence lacks domain diversity ({sorted(trusted)})")

        if url not in sitemap:
            errors.append(f"{rel}: missing from sitemap")
        if url not in feed:
            errors.append(f"{rel}: missing from Atom feed")
        route = "/" + Path(rel).parent.as_posix().strip("/") + "/"
        if route not in hub:
            errors.append(f"{rel}: missing from article hub")

        book_path = ROOT / rules["book"]
        if not book_path.exists():
            errors.append(f"{rel}: related book page is missing: {rules['book']}")
        else:
            book_html = book_path.read_text(encoding="utf-8")
            if route not in book_html:
                errors.append(f"{rel}: no reciprocal link from {rules['book']}")

        for phrase in FORBIDDEN_CERTAINTY:
            if phrase in text:
                errors.append(f"{rel}: unsupported certainty phrase: {phrase}")

        uncertainty_markers = ("قد ", "لا يعني", "لا يكفي", "حدود", "لا يصح")
        if sum(marker in text for marker in uncertainty_markers) < 2:
            warnings.append(f"{rel}: uncertainty language is unusually sparse")

        if rules["medical"]:
            for alternatives in MEDICAL_SAFETY_GROUPS:
                if not any(value in text for value in alternatives):
                    errors.append(
                        f"{rel}: medical safety language missing one of {alternatives}"
                    )
            if rules["medication_warning"] and not any(
                value in text for value in MEDICATION_WARNING
            ):
                errors.append(f"{rel}: medication-change warning is missing")
            context_markers = tuple(value.lower() for value in rules["medical_context_markers"])
            if context_markers and not any(value in lower for value in context_markers):
                errors.append(
                    f"{rel}: article-specific medical mechanism/context language is missing"
                )
            if "MedicalWebPage" not in "".join(data.jsonld_buffers):
                errors.append(f"{rel}: medical article lacks MedicalWebPage schema")

        if rules["safeguarding"]:
            for alternatives in SAFEGUARDING_GROUPS:
                if not any(value in text for value in alternatives):
                    errors.append(
                        f"{rel}: safeguarding language missing one of {alternatives}"
                    )

        print(f"{rel}: {count} visible words, {len(set(external))} visible sources")

    if warnings:
        print("\nWARNINGS")
        for item in warnings:
            print(f"- {item}")

    if errors:
        print("\nERRORS")
        for item in errors:
            print(f"- {item}")
        return 1

    print(
        f"\nPASS: {len(REFERENCE_ARTICLES)} reference articles satisfy "
        "the editorial, evidence, linking and safety gates"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
