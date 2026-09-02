#!/usr/bin/env python3
"""One-time post-release correction for editorial rebuild 07.

This patch:
- replaces future-dated feed timestamps with the verified public deployment time;
- aligns the Arabic Atom and JSON feeds with the seven-item research hub;
- records the verified global release in the operational memory;
- replaces the stale content checkpoint with the actual live state;
- adds a permanent CI gate for feed chronology and the article/book discovery graph.
"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPLOYED_AT = "2026-09-02T04:33:19+02:00"
ORIGINAL_AR_PUBLISHED = "2026-09-01T23:00:00+02:00"

AR_ITEMS = [
    {
        "url": "https://ahmed-alhafiz.github.io/articles/ratq-fatq-big-bang/",
        "title": "الرتق والفتق والانفجار العظيم: تحقيق في النص والتفسير وأدلة علم الكون",
        "summary": "ملف موسع يفصل النص القرآني وتاريخ التفسير عن الرصد والنموذج العلمي والاستنتاج الفلسفي، مع خريطة ادعاء ودليل ونسخة إنجليزية.",
        "category": "ملف بحثي موسع",
        "published": ORIGINAL_AR_PUBLISHED,
        "tags": ["ملف بحثي موسع", "author_review_complete_external_review_pending", "sirou-fi-alard"],
    },
    {
        "url": "https://ahmed-alhafiz.github.io/articles/teaching-names-ai-understanding/",
        "title": "تعليم الأسماء والذكاء الاصطناعي: هل تفهم الآلة الكلمات أم تتنبأ بها؟",
        "summary": "دراسة تفصل بين الرمز والعلاقة الإحصائية والتمثيل المفهومي والتأسيس في العالم والقصد والمسؤولية.",
        "category": "ملف بحثي موسع",
        "published": DEPLOYED_AT,
        "tags": ["ملف بحثي موسع", "author_review_complete_external_review_pending", "sirou-fi-alard"],
    },
    {
        "url": "https://ahmed-alhafiz.github.io/articles/spiritual-healing-exploitation-safeguarding/",
        "title": "حين يتحول العلاج الروحي إلى استغلال: كيف تحمي الأسرة المريض؟",
        "summary": "ملف حماية يميز الدعم الروحي الطوعي عن الإكراه والعزل والاستغلال واللمس بلا موافقة وتأخير الرعاية الطبية.",
        "category": "ملف حماية وصحة",
        "published": DEPLOYED_AT,
        "tags": ["ملف حماية وصحة", "author_review_complete_specialist_review_pending", "umm-abbas"],
    },
    {
        "url": "https://ahmed-alhafiz.github.io/articles/functional-seizures-vs-epilepsy/",
        "title": "النوبات الوظيفية والصرع: كيف يفرّق الأطباء بينهما؟",
        "summary": "موجز طبي تثقيفي عن آليتي الحالتين، وفيديو-EEG، وتعايشهما، وحدود التشخيص من الحركة أو الفيديو وحدهما.",
        "category": "موجز طبي تثقيفي",
        "published": ORIGINAL_AR_PUBLISHED,
        "tags": ["موجز طبي تثقيفي", "medical_specialist_review_pending", "umm-abbas"],
    },
    {
        "url": "https://ahmed-alhafiz.github.io/articles/six-days-creation-cosmic-time/",
        "title": "أيام الخلق الستة والزمن الكوني: هل اليوم القرآني 24 ساعة؟",
        "summary": "موجز أدلة يفصل ما يثبته النص وتنوع التفسير عن قياسات الزمن الكوني وما لا تسمح به المطابقة القسرية.",
        "category": "موجز أدلة",
        "published": ORIGINAL_AR_PUBLISHED,
        "tags": ["موجز أدلة", "external_review_pending", "sirou-fi-alard"],
    },
    {
        "url": "https://ahmed-alhafiz.github.io/articles/sleep-paralysis-jathoom/",
        "title": "شلل النوم والجاثوم: لماذا نشعر بوجود كائن في الغرفة؟",
        "summary": "موجز طبي ثقافي لشلل النوم وثقل الصدر والإحساس بالحضور، مع حدود التفسير ومتى يلزم التقييم الطبي.",
        "category": "موجز طبي ثقافي",
        "published": ORIGINAL_AR_PUBLISHED,
        "tags": ["موجز طبي ثقافي", "medical_specialist_review_pending", "umm-abbas"],
    },
    {
        "url": "https://ahmed-alhafiz.github.io/guides/arabic-psychological-horror/",
        "title": "الرعب النفسي العربي: كيف يعمل الخوف حين لا نعرف مصدره؟",
        "summary": "دليل تحليلي يميز مركز الخوف النفسي عن مجرد وجود حدث خارق أو صدمة، ويربط الغموض بالتفسير والسلطة داخل الحكاية.",
        "category": "دليل تحليلي",
        "published": ORIGINAL_AR_PUBLISHED,
        "tags": ["دليل تحليلي", "author_review_complete_external_review_pending", "umm-abbas"],
    },
]

EN_ITEM = {
    "url": "https://ahmed-alhafiz.github.io/en/articles/ratq-fatq-big-bang/",
    "title": "Ratq, fatq, and the Big Bang: text, exegesis, evidence, and limits",
    "summary": "A layered inquiry into Qur’an 21:30, classical exegesis, and hot Big Bang cosmology, separating text, observation, model, and metaphysical inference.",
    "category": "extended research dossier",
    "published": DEPLOYED_AT,
    "tags": ["extended research dossier", "Quranic exegesis", "cosmology", "external review pending"],
}

CHECKPOINT = """# Content Project Current Checkpoint — Ahmed Alhafiz

**Updated:** 2026-09-02

## Mandatory reading order

Before any website, research, SEO, AI-discoverability, or book-linked content action, read:

1. `.github/PROJECT_GOVERNING_DIRECTIVE.md`
2. `.github/SEO_SOURCE_OF_TRUTH.md`
3. `.github/SEO_OPERATIONS_LEDGER.md`
4. `.github/SEO_OPERATIONS_CORRECTION_2026-09-01.md`
5. `.github/CONTENT_CURRENT_CHECKPOINT.md`
6. `.github/GLOBAL_REBUILD_07_PREMERGE_RECORD.md`
7. `.github/POST_RELEASE_INTEGRITY_08.md`

## Current source priority

1. «قل سيروا في الأرض فانظروا كيف بدأ الخلق» — active research cluster.
2. «أم عباس لجلب الحبيب ورد المطلقة» — active research cluster.
3. «كتاب الكتب» — deferred until explicit instruction.
4. «جهيمان — القيامة بين الركن والمقام» — deferred until explicit instruction.

## Current live platform

The portfolio-style site was replaced by a bilingual author-and-research platform.

Verified public architecture:

- Arabic and English homepages.
- Arabic and English research hubs.
- Arabic and English methodology pages.
- Arabic and English research-status registries.
- Arabic and English Atom and JSON feeds.
- A bilingual flagship dossier and bilingual evidence appendix.
- Machine-readable claim ledger, BibTeX, RIS and `CITATION.cff` files.
- Honest thematic links from research to forthcoming books; unpublished manuscripts are not treated as scientific or medical evidence.
- Responsive paper-and-ink editorial design with reproducible mobile and desktop visual review.

## Verified global editorial rebuild 07

- Pull request: `#10`.
- Squash merge: `da1b67a6f9f622b650128dfe58fc0da0d383d212`.
- Main-branch integrity run: `33583601409` — success.
- GitHub Pages deployment run: `33583600618` — success; completed at `2026-09-02T02:33:19Z` (`04:33:19+02:00`).
- Final pre-merge visual artifact: 26 desktop/mobile screenshots, manually inspected.
- Verified structure at release: 34 public HTML pages, 34 canonicals, 34 sitemap URLs, zero structural errors and zero structural warnings.
- Seven Arabic research pages passed the depth, evidence, transparency, reciprocal-link and medical-safety gates.
- The complete English flagship dossier and evidence appendix are live.

### Current research inventory

1. `/articles/ratq-fatq-big-bang/`
2. `/articles/teaching-names-ai-understanding/`
3. `/articles/spiritual-healing-exploitation-safeguarding/`
4. `/articles/six-days-creation-cosmic-time/`
5. `/articles/sleep-paralysis-jathoom/`
6. `/articles/functional-seizures-vs-epilepsy/`
7. `/guides/arabic-psychological-horror/`
8. `/en/articles/ratq-fatq-big-bang/` — complete English edition.

The Arabic research hub lists all seven Arabic surfaces. The Sirou page links to the ratq/fatq, six-days, and names/AI studies. The Umm Abbas page links to the safeguarding, sleep-paralysis, functional-seizures, and psychological-horror studies. Every linked study returns visibly to its relevant forthcoming book.

## Post-release integrity correction 08

A live verification found that the feeds contained publication times later than the actual current time. The correction:

- normalizes all release timestamps to the verified Pages deployment time;
- preserves original publication time for earlier Arabic studies and uses the deployment time only as their update time;
- aligns the Arabic Atom and JSON feeds with all seven Arabic research surfaces;
- adds a permanent CI gate for future timestamps, feed/hub drift, and reciprocal article/book links.

See `.github/POST_RELEASE_INTEGRITY_08.md` for the merge and live-verification status of this correction.

## Persistent controls

The permanent workflows and tools now validate:

- Python syntax;
- every JSON-LD block;
- XML, Atom and JSON feeds;
- machine-readable evidence outputs;
- canonical, sitemap, internal-link and hreflang integrity;
- exact visible language counterparts;
- truthful forthcoming-book status;
- research depth, source diversity, uncertainty and review disclosure;
- reciprocal links among research hub, articles and books;
- feed chronology and prevention of future-dated entries;
- medical emergency boundaries and medication safeguards;
- absence of temporary release machinery;
- reproducible desktop and mobile screenshots on pull requests.

## Measurement baseline and freeze

Latest verified pre-rebuild Search Console period: 2026-08-23 to 2026-08-29.

- Homepage: 15 clicks, 54 impressions, 27.78% CTR, average position 3.98.
- `/about/`: 2 clicks, 15 impressions, 13.33% CTR, average position 4.73.

These are small samples. The rebuild and feed correction do not prove ranking growth or AI citation.

Measurement windows from the global public release:

- 14 days: 2026-09-16.
- 28 days: 2026-09-30.
- 56 days: 2026-10-28.

Do not rewrite titles, canonical URLs, core conclusions, or article structure before evidence exists, except to correct a verified factual, safety, accessibility or technical defect. Drafting may continue on private feature branches.

## Next controlled work

1. Monitor Search Console indexing, branded queries, non-branded research queries, click-through rate and page coverage.
2. Monitor real referrals carrying `utm_source=chatgpt.com` or other answer-engine evidence; do not infer citation without a real referral or observed source link.
3. Prepare — but do not mass-publish — the next two dossiers:
   - water, civilization and political control from the Sirou cluster;
   - diagnostic uncertainty, family fear and coercive authority from the Umm Abbas cluster.
4. Custom domain, ORCID and DOI/Zenodo identity work require the user’s account, identity confirmation, or payment where applicable; do not claim completion before those actions occur.
5. Keep «كتاب الكتب» and «جهيمان» deferred.
"""

LEDGER_MARKER = "### 2026-09-02 — Global bilingual editorial and research platform release 07"
LEDGER_ENTRY = f"""{LEDGER_MARKER}
- Task: owned-surface rebuild / author entity / evidence-led research publishing
- Books: «قل سيروا في الأرض فانظروا كيف بدأ الخلق» + «أم عباس لجلب الحبيب ورد المطلقة»
- Action: replaced the portfolio-style site with a bilingual author-and-research platform; published a complete Arabic/English flagship dossier and evidence appendix; added research hubs, methodology and review-status pages, Atom/JSON feeds, claim ledgers and citation files; strengthened honest book/research linking, medical safeguards, structural CI and reproducible visual review.
- Pull request: `#10`
- Merge commit: `da1b67a6f9f622b650128dfe58fc0da0d383d212`
- Verification: fresh pull-request `Site integrity` and `Visual review` runs succeeded on the final head; the 26-image artifact was manually inspected; main `Site integrity` run `33583601409` and Pages deployment run `33583600618` succeeded; public priority URLs were fetched after deployment.
- Structural result: 34 public HTML pages, 34 canonicals, 34 sitemap URLs, zero structural errors, zero warnings. Seven Arabic research pages passed evidence, transparency, reciprocal-link and medical-safety gates.
- Publication safety: the two books remain forthcoming; manuscripts are thematic origins, not scientific or medical evidence. No publisher, ISBN, sales, ranking, review or AI-citation claim was fabricated.
- Status: `EXECUTED_VERIFIED`
- Next: freeze unforced public rewrites and evaluate finalized evidence at 14, 28 and 56 days.
"""

RECORD = f"""# Post-release Integrity 08

**Prepared:** 2026-09-02  
**Status:** `BRANCH_VERIFIED_AWAITING_PR_AND_LIVE_DEPLOYMENT`

## Defect found

The Arabic and English feeds contained timestamps later than the real public deployment and later than the current local time. The Arabic feed also omitted the psychological-horror guide although the research hub and structured `ItemList` correctly declared seven Arabic research surfaces.

## Correction

- Verified deployment completion used as release/update time: `{DEPLOYED_AT}`.
- Arabic Atom and JSON feeds aligned to seven research surfaces.
- English flagship feed timestamp aligned to the verified deployment.
- Earlier Arabic publication dates preserved; global-rebuild modifications use the verified deployment time.
- Permanent CI expanded to reject future feed timestamps, feed/hub divergence, missing book-to-study links and missing study-to-book return links.

## Verification required before final status

1. The branch workflow must complete and self-remove its temporary files.
2. `Site integrity` and `Visual review` must succeed on the final pull-request head.
3. The pull request must merge to `main`.
4. GitHub Pages deployment must succeed.
5. Live Atom/JSON feeds, the Arabic research hub and both relevant book pages must be fetched and checked.

After those steps, replace this status with `EXECUTED_VERIFIED` and record the merge and deployment identifiers.
"""

CI_STEP = r'''
      - name: Validate feed chronology and research discovery graph
        shell: bash
        run: |
          set -euo pipefail
          python - <<'PY'
          from datetime import datetime, timedelta, timezone
          from html.parser import HTMLParser
          from pathlib import Path
          import json
          import xml.etree.ElementTree as ET

          ATOM = {'a': 'http://www.w3.org/2005/Atom'}
          tolerance = datetime.now(timezone.utc) + timedelta(minutes=10)

          expected_ar = {
              'https://ahmed-alhafiz.github.io/articles/ratq-fatq-big-bang/',
              'https://ahmed-alhafiz.github.io/articles/teaching-names-ai-understanding/',
              'https://ahmed-alhafiz.github.io/articles/spiritual-healing-exploitation-safeguarding/',
              'https://ahmed-alhafiz.github.io/articles/six-days-creation-cosmic-time/',
              'https://ahmed-alhafiz.github.io/articles/sleep-paralysis-jathoom/',
              'https://ahmed-alhafiz.github.io/articles/functional-seizures-vs-epilepsy/',
              'https://ahmed-alhafiz.github.io/guides/arabic-psychological-horror/',
          }
          expected_en = {
              'https://ahmed-alhafiz.github.io/en/articles/ratq-fatq-big-bang/',
          }

          def parsed(value: str) -> datetime:
              moment = datetime.fromisoformat(value.replace('Z', '+00:00'))
              if moment.tzinfo is None:
                  raise SystemExit(f'Timestamp lacks timezone: {value}')
              return moment.astimezone(timezone.utc)

          def validate_atom(path: str, expected: set[str]) -> None:
              root = ET.parse(path).getroot()
              updated = root.findtext('a:updated', namespaces=ATOM)
              if not updated:
                  raise SystemExit(f'{path}: missing feed updated timestamp')
              moments = [parsed(updated)]
              urls = set()
              for entry in root.findall('a:entry', ATOM):
                  link = entry.find('a:link', ATOM)
                  if link is None or not link.get('href'):
                      raise SystemExit(f'{path}: entry lacks link')
                  urls.add(link.get('href'))
                  for tag in ('published', 'updated'):
                      value = entry.findtext(f'a:{tag}', namespaces=ATOM)
                      if not value:
                          raise SystemExit(f'{path}: {link.get("href")} lacks {tag}')
                      moments.append(parsed(value))
              if urls != expected:
                  raise SystemExit(f'{path}: URL set drift. expected={sorted(expected)} actual={sorted(urls)}')
              if max(moments) > tolerance:
                  raise SystemExit(f'{path}: future timestamp detected: {max(moments).isoformat()}')
              if parsed(updated) < max(moments[1:]):
                  raise SystemExit(f'{path}: feed updated precedes an entry timestamp')

          def validate_json(path: str, expected: set[str]) -> None:
              data = json.loads(Path(path).read_text(encoding='utf-8'))
              urls = {item['url'] for item in data.get('items', [])}
              if urls != expected:
                  raise SystemExit(f'{path}: URL set drift. expected={sorted(expected)} actual={sorted(urls)}')
              for item in data['items']:
                  for key in ('date_published', 'date_modified'):
                      moment = parsed(item[key])
                      if moment > tolerance:
                          raise SystemExit(f'{path}: future {key} for {item["url"]}: {item[key]}')

          validate_atom('articles/feed.xml', expected_ar)
          validate_atom('en/articles/feed.xml', expected_en)
          validate_json('articles/feed.json', expected_ar)
          validate_json('en/articles/feed.json', expected_en)

          hub = Path('articles/index.html').read_text(encoding='utf-8')
          for url in expected_ar:
              local = url.removeprefix('https://ahmed-alhafiz.github.io')
              if local not in hub:
                  raise SystemExit(f'articles/index.html: missing research surface {local}')

          graph = {
              'books/sirou-fi-alard/index.html': {
                  'articles/ratq-fatq-big-bang/index.html',
                  'articles/six-days-creation-cosmic-time/index.html',
                  'articles/teaching-names-ai-understanding/index.html',
              },
              'books/umm-abbas/index.html': {
                  'articles/spiritual-healing-exploitation-safeguarding/index.html',
                  'articles/sleep-paralysis-jathoom/index.html',
                  'articles/functional-seizures-vs-epilepsy/index.html',
                  'guides/arabic-psychological-horror/index.html',
              },
          }
          for book, studies in graph.items():
              book_html = Path(book).read_text(encoding='utf-8')
              book_url = '/' + book.removesuffix('index.html')
              for study in studies:
                  study_url = '/' + study.removesuffix('index.html')
                  if study_url not in book_html:
                      raise SystemExit(f'{book}: missing link to {study_url}')
                  study_html = Path(study).read_text(encoding='utf-8')
                  if book_url not in study_html:
                      raise SystemExit(f'{study}: missing return link to {book_url}')

          print('Feed chronology, seven-item Arabic discovery coverage, and reciprocal book graph passed')
          PY
'''.strip('\n')


def build_atom(path: Path, language: str) -> None:
    if language == "ar":
        title = "مركز أبحاث أحمد الحافظ"
        subtitle = "ملفات بحثية وموجزات أدلة مع مصادر وحالة مراجعة معلنة."
        feed_url = "https://ahmed-alhafiz.github.io/articles/feed.xml"
        json_url = "https://ahmed-alhafiz.github.io/articles/feed.json"
        home = "https://ahmed-alhafiz.github.io/articles/"
        author = "أحمد الحافظ"
        author_uri = "https://ahmed-alhafiz.github.io/about/"
        items = AR_ITEMS
    else:
        title = "Ahmed Alhafiz Research Desk"
        subtitle = "Full English research editions with traceable evidence and disclosed review status."
        feed_url = "https://ahmed-alhafiz.github.io/en/articles/feed.xml"
        json_url = "https://ahmed-alhafiz.github.io/en/articles/feed.json"
        home = "https://ahmed-alhafiz.github.io/en/articles/"
        author = "Ahmed Alhafiz"
        author_uri = "https://ahmed-alhafiz.github.io/en/about/"
        items = [EN_ITEM]

    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        f'<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="{language}">',
        f'  <title>{title}</title>',
        f'  <subtitle>{subtitle}</subtitle>',
        f'  <link href="{feed_url}" rel="self" type="application/atom+xml"/>',
        f'  <link href="{json_url}" rel="alternate" type="application/feed+json"/>',
        f'  <link href="{home}" rel="alternate" type="text/html"/>',
        f'  <id>{home}</id>',
        f'  <updated>{DEPLOYED_AT}</updated>',
        f'  <author><name>{author}</name><uri>{author_uri}</uri></author>',
    ]
    for item in items:
        lines.extend([
            '  <entry>',
            f'    <title>{item["title"]}</title>',
            f'    <link href="{item["url"]}"/>',
            f'    <id>{item["url"]}</id>',
            f'    <published>{item["published"]}</published>',
            f'    <updated>{DEPLOYED_AT}</updated>',
            f'    <category term="{item["category"]}"/>',
            f'    <summary>{item["summary"]}</summary>',
            '  </entry>',
        ])
    lines.append('</feed>')
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    ET.parse(path)


def build_json_feed(path: Path, language: str) -> None:
    if language == "ar":
        items = AR_ITEMS
        data = {
            "version": "https://jsonfeed.org/version/1.1",
            "title": "مركز أبحاث أحمد الحافظ",
            "home_page_url": "https://ahmed-alhafiz.github.io/articles/",
            "feed_url": "https://ahmed-alhafiz.github.io/articles/feed.json",
            "language": "ar",
            "authors": [{"name": "أحمد الحافظ — Ahmed Alhafiz", "url": "https://ahmed-alhafiz.github.io/about/"}],
        }
    else:
        items = [EN_ITEM]
        data = {
            "version": "https://jsonfeed.org/version/1.1",
            "title": "Ahmed Alhafiz Research Desk",
            "home_page_url": "https://ahmed-alhafiz.github.io/en/articles/",
            "feed_url": "https://ahmed-alhafiz.github.io/en/articles/feed.json",
            "language": "en",
            "authors": [{"name": "Ahmed Alhafiz", "url": "https://ahmed-alhafiz.github.io/en/about/"}],
        }
    data["items"] = [
        {
            "id": item["url"],
            "url": item["url"],
            "title": item["title"],
            "summary": item["summary"],
            "date_published": item["published"],
            "date_modified": DEPLOYED_AT,
            "tags": item["tags"],
            "language": language,
        }
        for item in items
    ]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    json.loads(path.read_text(encoding='utf-8'))


def patch_ci() -> None:
    path = ROOT / '.github/workflows/site-integrity.yml'
    text = path.read_text(encoding='utf-8')
    if 'Validate feed chronology and research discovery graph' in text:
        return
    marker = '      - name: Validate HTML links sitemap feeds hreflang and publication safety\n'
    if text.count(marker) != 1:
        raise RuntimeError('site-integrity insertion marker not found exactly once')
    path.write_text(text.replace(marker, CI_STEP + '\n\n' + marker, 1), encoding='utf-8')


def append_ledger() -> None:
    path = ROOT / '.github/SEO_OPERATIONS_LEDGER.md'
    text = path.read_text(encoding='utf-8').rstrip()
    if LEDGER_MARKER not in text:
        path.write_text(text + '\n\n' + LEDGER_ENTRY.strip() + '\n', encoding='utf-8')


def assert_graph() -> None:
    hub = (ROOT / 'articles/index.html').read_text(encoding='utf-8')
    for item in AR_ITEMS:
        local = item['url'].removeprefix('https://ahmed-alhafiz.github.io')
        if local not in hub:
            raise RuntimeError(f'Arabic research hub lacks {local}')
    pairs = {
        'books/sirou-fi-alard/index.html': [
            'articles/ratq-fatq-big-bang/index.html',
            'articles/six-days-creation-cosmic-time/index.html',
            'articles/teaching-names-ai-understanding/index.html',
        ],
        'books/umm-abbas/index.html': [
            'articles/spiritual-healing-exploitation-safeguarding/index.html',
            'articles/sleep-paralysis-jathoom/index.html',
            'articles/functional-seizures-vs-epilepsy/index.html',
            'guides/arabic-psychological-horror/index.html',
        ],
    }
    for book, studies in pairs.items():
        book_text = (ROOT / book).read_text(encoding='utf-8')
        book_url = '/' + book.removesuffix('index.html')
        for study in studies:
            study_url = '/' + study.removesuffix('index.html')
            if study_url not in book_text:
                raise RuntimeError(f'{book} lacks {study_url}')
            if book_url not in (ROOT / study).read_text(encoding='utf-8'):
                raise RuntimeError(f'{study} lacks return link to {book_url}')


def main() -> None:
    # Sanity-check the trusted deployment timestamp before writing it.
    datetime.fromisoformat(DEPLOYED_AT)
    build_atom(ROOT / 'articles/feed.xml', 'ar')
    build_atom(ROOT / 'en/articles/feed.xml', 'en')
    build_json_feed(ROOT / 'articles/feed.json', 'ar')
    build_json_feed(ROOT / 'en/articles/feed.json', 'en')
    (ROOT / '.github/CONTENT_CURRENT_CHECKPOINT.md').write_text(CHECKPOINT, encoding='utf-8')
    (ROOT / '.github/POST_RELEASE_INTEGRITY_08.md').write_text(RECORD, encoding='utf-8')
    append_ledger()
    patch_ci()
    assert_graph()
    print('Post-release chronology, discovery graph, checkpoint and operational record corrected.')


if __name__ == '__main__':
    main()
