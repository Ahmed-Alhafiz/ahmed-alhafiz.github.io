#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHOR_ID = "https://ahmed-alhafiz.github.io/#person"
AUTHOR_NAME = "أحمد الحافظ"
ALIASES = ["Ahmed Alhafiz", "Ahmad Alhafiz"]
AUTHOR_URL = "https://ahmed-alhafiz.github.io/about/"
EMAIL = "mailto:hhafz9924@gmail.com"
SAME_AS = [
    "https://medium.com/@AhmedAlhafiz",
    "https://www.instagram.com/ahmed_666_8",
]
IMAGE = {
    "@type": "ImageObject",
    "url": "https://ahmed-alhafiz.github.io/ahmed-alhafiz-author.png",
    "width": 1229,
    "height": 1536,
}
IDENTIFIER = {
    "@type": "PropertyValue",
    "propertyID": "canonical-author-id",
    "value": AUTHOR_ID,
}
PROFILE_URLS = [
    "https://ahmed-alhafiz.github.io/about/",
    "https://ahmed-alhafiz.github.io/en/about/",
    "https://ahmed-alhafiz.github.io/de/about/",
]
EXCLUDED_HTML = {"404.html", "google904951439b331720.html"}
SCRIPT_RE = re.compile(
    r"(<script\b[^>]*\btype=[\"']application/ld\+json[\"'][^>]*>)(.*?)(</script>)",
    re.IGNORECASE | re.DOTALL,
)

AR_IDENTITY = '''<section class="section identity-section" id="identity"><div class="wrap"><div class="kicker">تمييز الاسم والهوية</div><h2>مرجع الهوية الرسمي</h2><div class="rule"></div><p class="identity-intro">هذه الصفحة هي المرجع الرسمي لتمييز الكاتب أحمد الحافظ عن الأشخاص الآخرين الذين يحملون الاسم نفسه. تُستخدم صيغة لاتينية واحدة ثابتة في النشر، مع تهجئة بديلة محدودة لأغراض البحث فقط، من دون إنشاء صفحات مكررة لكل صيغة.</p><div class="identity-grid"><dl class="identity-record"><div><dt>الاسم العربي الرسمي</dt><dd>أحمد الحافظ</dd></div><div><dt>الاسم اللاتيني المعتمد</dt><dd dir="ltr">Ahmed Alhafiz</dd></div><div><dt>تهجئة بحث بديلة</dt><dd dir="ltr">Ahmad Alhafiz</dd></div><div><dt>المعرّف المرجعي</dt><dd><code dir="ltr">https://ahmed-alhafiz.github.io/#person</code></dd></div><div><dt>صفحة الكاتب المرجعية</dt><dd><a href="/about/" dir="ltr">https://ahmed-alhafiz.github.io/about/</a></dd></div></dl><aside class="identity-note"><strong>حدود الإسناد</strong><p>تشير هذه الهوية حصراً إلى مؤلف الأعمال والملفات البحثية المدرجة في هذا الموقع. لا يُنسب إلى أحمد الحافظ حساب أو كتاب أو تصريح لمجرد تشابه الاسم.</p><p>القنوات الخارجية المثبتة حاليًا هي Medium وInstagram فقط، إضافة إلى البريد المنشور في قسم التواصل.</p><div class="actions"><a class="btn primary" href="/author.json">ملف الهوية الآلي</a><a class="btn" href="/methodology/">مبادئ النشر</a></div></aside></div></div></section>'''

EN_IDENTITY = '''<section class="section identity-section" id="identity"><div class="wrap"><div class="kicker">Name and identity disambiguation</div><h2>Canonical author identity</h2><div class="rule"></div><p class="identity-intro">This page is the official reference for distinguishing this author from other people who share the Arabic name أحمد الحافظ. One preferred Latin spelling is used in publication, with one secondary transliteration retained only for search disambiguation—not as a duplicate author page.</p><div class="identity-grid"><dl class="identity-record"><div><dt>Official Arabic name</dt><dd lang="ar" dir="rtl">أحمد الحافظ</dd></div><div><dt>Preferred Latin name</dt><dd>Ahmed Alhafiz</dd></div><div><dt>Search transliteration</dt><dd>Ahmad Alhafiz</dd></div><div><dt>Canonical identifier</dt><dd><code>https://ahmed-alhafiz.github.io/#person</code></dd></div><div><dt>Canonical author page</dt><dd><a href="/about/">https://ahmed-alhafiz.github.io/about/</a></dd></div></dl><aside class="identity-note"><strong>Attribution boundary</strong><p>This identity refers only to the author of the works and research dossiers listed on this official site. A shared or similar name is not evidence that another account, book, or statement belongs to Ahmed Alhafiz.</p><p>The currently verified external profiles are Medium and Instagram, together with the public email in the contact section.</p><div class="actions"><a class="btn primary" href="/author.json">Machine-readable identity</a><a class="btn" href="/en/methodology/">Publishing principles</a></div></aside></div></div></section>'''

DE_IDENTITY = '''<section class="section identity-section" id="identity"><div class="wrap"><div class="kicker">Namens- und Identitätsklärung</div><h2>Kanonische Autorenidentität</h2><div class="rule"></div><p class="identity-intro">Diese Seite ist die offizielle Referenz zur Unterscheidung dieses Autors von anderen Personen mit dem arabischen Namen أحمد الحافظ. Für Veröffentlichungen gilt eine bevorzugte lateinische Schreibweise; eine zweite Transkription dient ausschließlich der Suchzuordnung und erhält keine eigene Duplikatseite.</p><div class="identity-grid"><dl class="identity-record"><div><dt>Offizieller arabischer Name</dt><dd lang="ar" dir="rtl">أحمد الحافظ</dd></div><div><dt>Bevorzugter lateinischer Name</dt><dd>Ahmed Alhafiz</dd></div><div><dt>Alternative Suchschreibweise</dt><dd>Ahmad Alhafiz</dd></div><div><dt>Kanonische Kennung</dt><dd><code>https://ahmed-alhafiz.github.io/#person</code></dd></div><div><dt>Kanonische Autorenseite</dt><dd><a href="/about/">https://ahmed-alhafiz.github.io/about/</a></dd></div></dl><aside class="identity-note"><strong>Zuordnungsgrenze</strong><p>Diese Identität bezeichnet ausschließlich den Autor der auf dieser offiziellen Website aufgeführten Werke und Forschungsdossiers. Eine Namensähnlichkeit belegt keine Zuordnung fremder Konten, Bücher oder Aussagen.</p><p>Als externe Profile sind derzeit nur Medium und Instagram verifiziert; hinzu kommt die öffentlich angegebene E-Mail-Adresse.</p><div class="actions"><a class="btn primary" href="/author.json">Maschinenlesbare Identität</a><a class="btn" href="/en/methodology/" hreflang="en">Publikationsprinzipien</a></div></aside></div></div></section>'''

CSS = r'''

/* Entity and measurement foundation 12 */
.identity-section{background:linear-gradient(135deg,var(--paper),var(--paper-2));position:relative;overflow:hidden}
.identity-section::after{content:"";position:absolute;width:430px;height:430px;border:1px solid rgba(43,96,118,.12);border-radius:50%;inset:auto -180px -220px auto;box-shadow:0 0 0 70px rgba(43,96,118,.025),0 0 0 140px rgba(43,96,118,.018);pointer-events:none}
.identity-section .wrap{position:relative;z-index:1}
.identity-intro{max-width:900px;color:var(--ink-2);font-size:19px;line-height:1.95;margin:0 0 34px}
.identity-grid{display:grid;grid-template-columns:minmax(0,1.22fr) minmax(300px,.78fr);gap:24px;align-items:stretch}
.identity-record{margin:0;background:var(--surface);border:1px solid var(--line);border-radius:20px;box-shadow:var(--shadow-soft);overflow:hidden}
.identity-record>div{display:grid;grid-template-columns:minmax(155px,.42fr) minmax(0,1fr);gap:22px;padding:17px 22px;border-bottom:1px solid var(--line);align-items:center}
.identity-record>div:last-child{border-bottom:0}
.identity-record dt{font:700 12px/1.45 Arial,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:var(--copper)}
.identity-record dd{margin:0;color:var(--ink);font-weight:700;overflow-wrap:anywhere}
.identity-record code{font:13px/1.6 ui-monospace,SFMono-Regular,Consolas,monospace;color:var(--blue);direction:ltr;unicode-bidi:embed}
.identity-record a{color:var(--blue);text-decoration:underline;text-underline-offset:4px}
.identity-note{background:var(--navy);color:#dce5eb;border-radius:20px;padding:27px 28px;box-shadow:var(--shadow)}
.identity-note>strong{display:block;color:#fff;font-size:21px;margin-bottom:9px}
.identity-note p{margin:0 0 13px;color:#c5d1d9;line-height:1.8}
.identity-note .btn{border-color:rgba(255,255,255,.34);color:#fff}
.identity-note .btn.primary{background:#fff;color:var(--navy);border-color:#fff}
.identity-note .btn:hover,.identity-note .btn:focus-visible{border-color:#f0ad85}
@media(max-width:860px){.identity-grid{grid-template-columns:1fr}.identity-record>div{grid-template-columns:1fr;gap:6px}.identity-note{padding:24px}}
@media(max-width:620px){.identity-intro{font-size:17px}.identity-record>div{padding:15px 17px}.identity-record code{font-size:11px}.identity-note .actions{display:grid}.identity-note .btn{width:100%}}
'''

CHECKPOINT = '''# Content Project Current Checkpoint — Ahmed Alhafiz

**Updated:** 2026-09-02

## Mandatory reading order

Before any website, research, SEO, AI-discoverability, entity, measurement, domain, or book-linked content action, read:

1. `.github/PROJECT_GOVERNING_DIRECTIVE.md`
2. `.github/SEO_SOURCE_OF_TRUTH.md`
3. `.github/SEO_OPERATIONS_LEDGER.md`
4. `.github/SEO_OPERATIONS_CORRECTION_2026-09-01.md`
5. `.github/CONTENT_CURRENT_CHECKPOINT.md`
6. `.github/GLOBAL_REBUILD_07_PREMERGE_RECORD.md`
7. `.github/POST_RELEASE_INTEGRITY_08.md`
8. `.github/WATER_CIVILIZATION_POWER_09_PREMERGE.md`
9. `.github/SITE_UX_REBUILD_10_VERIFICATION.md`
10. `.github/UMM_ABBAS_FEAR_CERTAINTY_AUTHORITY_11_PREMERGE.md`
11. `.github/MEASUREMENT_PROTOCOL.md`
12. `.github/CUSTOM_DOMAIN_MIGRATION_PLAN.md`

## Governing strategy

The site is not managed as a volume blog. It is an author-entity and reference-dossier system.

- One official author identity: `https://ahmed-alhafiz.github.io/#person`.
- One canonical Arabic name: `أحمد الحافظ`.
- One preferred Latin spelling: `Ahmed Alhafiz`.
- One secondary transliteration for search disambiguation only: `Ahmad Alhafiz`.
- No doorway pages for spelling variants.
- No new indexed URL merely to increase page count.
- Forthcoming manuscripts may generate questions; they are not evidence for scientific, medical, legal, historical, or policy claims.
- Search ranking and AI citation are external outcomes and remain unclaimed until directly measured.

## Current source priority

1. «قل سيروا في الأرض فانظروا كيف بدأ الخلق» — active research cluster.
2. «أم عباس لجلب الحبيب ورد المطلقة» — active research cluster.
3. «كتاب الكتب» — deferred until explicit instruction.
4. «جهيمان — القيامة بين الركن والمقام» — deferred until explicit instruction.

## Current verified platform

- Arabic, English, and German author/profile surfaces.
- Arabic and English homepages, research hubs, methodology pages, and review registers.
- Arabic and English Atom and JSON feeds.
- Three complete bilingual reference dossiers:
  1. ratq/fatq, exegesis, and Big Bang evidence;
  2. water, civilisation, power, and justice;
  3. diagnostic uncertainty, family fear, and coercive authority.
- Evidence appendices, machine-readable claim ledgers, BibTeX, RIS, and `CITATION.cff` outputs.
- Responsive editorial design with browser-based desktop/mobile visual review.
- Explicit crawler access for `OAI-SearchBot`, `GPTBot`, and generic crawlers.

## Verified release 11 — Umm Abbas fear/certainty/authority dossier

- Pull request: `#16`.
- Squash merge: `b317e17c04235c14eb1ad4e8fc115d0ee4d715f1`.
- Main `Site integrity`: `33622072299` — success.
- GitHub Pages deployment: `33622071723` — success.
- Two substantive language editions and two evidence pages.
- Four accessible diagrams and two 1200×630 share cards.
- Fourteen reciprocal claims and nineteen annotated sources.
- Two original frameworks explicitly labelled non-validated:
  - Fear–Certainty–Authority Cascade.
  - Parallel-Path Safeguard.
- The forthcoming novel is encoded as thematic origin only, never medical evidence.

## Strategic content inventory

Controlled by `data/content-inventory.json`:

- 3 current pillars.
- 1 pillar candidate: names and AI understanding.
- 3 supporting briefs.
- 1 literary guide.
- 1 URL held for overlap review.

No consolidation or deletion occurs before overlap, link, and 30-day measurement review.

## Measurement baseline

Controlled by:

- `.github/MEASUREMENT_PROTOCOL.md`
- `data/visibility-baseline.json`
- `tools/visibility_audit.py`
- `.github/workflows/visibility-monitor.yml`

Current external outcomes:

- Google indexed-page count: not measured in the repository.
- Branded-query positions: not measured in the repository.
- ChatGPT referral sessions: not measured; analytics source not connected.
- Verified AI citations: none observed and preserved as evidence.
- Independent external citations: none observed and preserved as evidence.

Technical readiness is not reported as ranking success.

## Entity and domain foundation 12

Current controlled batch:

- standardise every canonical `Person` node;
- publish one machine-readable `author.json` identity manifest;
- add a visible identity/disambiguation section to Arabic, English, and German author pages;
- retain only Medium and Instagram as verified external identity links;
- add a technical visibility monitor;
- activate constrained IndexNow changed-URL notification with explicit transport-only interpretation;
- prepare, but do not activate, the custom-domain migration until the user purchases and selects the domain.

## Custom-domain dependency

No domain is purchased or configured yet. Preferred naming order, subject to live availability:

1. `ahmedalhafiz.com`
2. `ahmed-alhafiz.com`
3. `ahmadalhafiz.com`

The user must choose and purchase the domain. DNS, GitHub verification, HTTPS, canonical migration, redirects, sitemap transition, and rollback are governed by `.github/CUSTOM_DOMAIN_MIGRATION_PLAN.md`.

## Persistent controls

Permanent checks must continue to validate:

- Python syntax;
- all JSON-LD, JSON, XML, Atom, SVG, BibTeX, RIS, and CFF surfaces;
- canonical, sitemap, internal-link, hreflang, and visible language-switch integrity;
- truthful forthcoming-book status;
- evidence depth, source diversity, uncertainty, and review disclosure;
- reciprocal research/book/evidence links;
- medical emergency and medication boundaries;
- canonical author name, aliases, identifier, image, email, and verified profiles;
- absence of alias doorway pages;
- content-inventory counts and anti-thin-content policy;
- public crawler access and machine identity manifest;
- reproducible desktop/mobile visual review;
- absence of temporary release machinery.

## Next controlled work after foundation 12

1. Observe the Day-7 and Day-30 measurement windows without noisy title changes.
2. Rebuild `teaching-names-ai-understanding` into the fourth complete bilingual pillar instead of creating derivative posts.
3. Purchase and verify the selected custom domain before any canonical-host migration.
4. Connect a trustworthy Search Console export/API and privacy-compliant referral analytics when account authorization is available.
5. Keep «كتاب الكتب» and «جهيمان» deferred.
'''


def is_type(node: dict, expected: str) -> bool:
    value = node.get("@type")
    return value == expected or isinstance(value, list) and expected in value


def patch_nodes(value: object) -> int:
    changed = 0
    if isinstance(value, dict):
        if is_type(value, "Person") and value.get("@id") == AUTHOR_ID:
            value["name"] = AUTHOR_NAME
            value["alternateName"] = ALIASES
            value["identifier"] = IDENTIFIER
            value["url"] = AUTHOR_URL
            value["mainEntityOfPage"] = PROFILE_URLS
            value["image"] = IMAGE
            value["email"] = EMAIL
            value["sameAs"] = SAME_AS
            value["publishingPrinciples"] = "https://ahmed-alhafiz.github.io/methodology/"
            value.setdefault("jobTitle", "كاتب ومؤلف — Writer and author")
            value.setdefault(
                "disambiguatingDescription",
                "أحمد الحافظ — Ahmed Alhafiz، الكاتب المرتبط حصراً بالمؤلفات والملفات البحثية المدرجة في هذا الموقع الرسمي.",
            )
            changed += 1
        for child in value.values():
            changed += patch_nodes(child)
    elif isinstance(value, list):
        for child in value:
            changed += patch_nodes(child)
    return changed


def author_href(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("en/"):
        return "/en/about/"
    if rel.startswith("de/"):
        return "/de/about/"
    return "/about/"


def patch_html(path: Path) -> tuple[int, int]:
    html = path.read_text(encoding="utf-8")
    if 'rel="author"' in html or 'href="/author.json"' in html:
        raise RuntimeError(f"{path.relative_to(ROOT)} already contains foundation links")
    links = (
        f'<link rel="author" href="{author_href(path)}">'
        '<link rel="alternate" type="application/ld+json" href="/author.json" title="Ahmed Alhafiz canonical author identity">'
    )
    marker = '<link rel="icon"'
    if marker in html:
        html = html.replace(marker, links + marker, 1)
    elif "</head>" in html:
        html = html.replace("</head>", links + "</head>", 1)
    else:
        raise RuntimeError(f"{path.relative_to(ROOT)}: no head insertion point")

    person_nodes = 0

    def replacement(match: re.Match[str]) -> str:
        nonlocal person_nodes
        data = json.loads(match.group(2))
        person_nodes += patch_nodes(data)
        return match.group(1) + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + match.group(3)

    html = SCRIPT_RE.sub(replacement, html)
    path.write_text(html.rstrip() + "\n", encoding="utf-8")
    return 1, person_nodes


def insert_identity(path: Path, block: str, action_marker: str, action: str) -> None:
    html = path.read_text(encoding="utf-8")
    contact = '<section class="section contact-section" id="contact">'
    if html.count(contact) != 1:
        raise RuntimeError(f"{path.relative_to(ROOT)}: contact marker count {html.count(contact)}")
    if html.count(action_marker) != 1:
        raise RuntimeError(f"{path.relative_to(ROOT)}: action marker count {html.count(action_marker)}")
    html = html.replace(action_marker, action_marker + action, 1)
    html = html.replace(contact, block + "\n" + contact, 1)
    path.write_text(html.rstrip() + "\n", encoding="utf-8")


def patch_css() -> None:
    path = ROOT / "assets/site-v2.css"
    css = path.read_text(encoding="utf-8")
    if "Entity and measurement foundation 12" in css:
        raise RuntimeError("Entity foundation CSS already present")
    path.write_text(css.rstrip() + CSS + "\n", encoding="utf-8")


def patch_integrity_workflow() -> None:
    path = ROOT / ".github/workflows/site-integrity.yml"
    text = path.read_text(encoding="utf-8")
    compile_old = "tools/arabic_ui_integrity.py tools/dossier11_integrity.py"
    compile_new = compile_old + " tools/entity_integrity.py tools/visibility_audit.py tools/indexnow_submit.py"
    if text.count(compile_old) != 1:
        raise RuntimeError("Site-integrity compile marker missing")
    text = text.replace(compile_old, compile_new, 1)

    json_marker = '              Path("articles/research-index.json"),\n'
    json_add = (
        '              Path("author.json"),\n'
        '              Path("data/content-inventory.json"),\n'
        '              Path("data/visibility-baseline.json"),\n'
        '              Path("data/indexnow-config.json"),\n'
    )
    if text.count(json_marker) != 1:
        raise RuntimeError("Site-integrity JSON list marker missing")
    text = text.replace(json_marker, json_marker + json_add, 1)

    step_marker = "      - name: Validate multilingual UX portrait footer contact covers and public identity integrity\n"
    new_steps = (
        "      - name: Validate canonical author identity manifest aliases and visible attribution boundaries\n"
        "        run: python tools/entity_integrity.py\n\n"
        "      - name: Validate technical visibility baseline without inventing external outcomes\n"
        "        run: python tools/visibility_audit.py --output visibility-audit-local.json\n\n"
        "      - name: Validate IndexNow configuration and build a dry-run URL inventory\n"
        "        run: python tools/indexnow_submit.py --all --report indexnow-dry-run.json\n\n"
    )
    if text.count(step_marker) != 1:
        raise RuntimeError("Site-integrity execution marker missing")
    text = text.replace(step_marker, new_steps + step_marker, 1)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def patch_visual_review() -> None:
    path = ROOT / ".github/visual-review/run_visual_review.py"
    text = path.read_text(encoding="utf-8")
    marker = '    ("about-de-contact", "/de/about/", "#contact", "start"),\n'
    addition = (
        '    ("about-ar-identity", "/about/", "#identity", "start"),\n'
        '    ("about-en-identity", "/en/about/", "#identity", "start"),\n'
        '    ("about-de-identity", "/de/about/", "#identity", "start"),\n'
    )
    if text.count(marker) != 1:
        raise RuntimeError("Visual target marker missing")
    path.write_text(text.replace(marker, marker + addition, 1).rstrip() + "\n", encoding="utf-8")


def update_checkpoint_and_ledger() -> None:
    (ROOT / ".github/CONTENT_CURRENT_CHECKPOINT.md").write_text(CHECKPOINT.rstrip() + "\n", encoding="utf-8")
    ledger_path = ROOT / ".github/SEO_OPERATIONS_LEDGER.md"
    ledger = ledger_path.read_text(encoding="utf-8").rstrip()
    entry = '''

### 2026-09-02 — Canonical author entity, measurement, domain, and IndexNow foundation 12
- Task: author-entity disambiguation, honest outcome measurement, crawler transport, and custom-domain migration readiness.
- Action: prepared a single canonical Person identity across public JSON-LD; one public `author.json` graph; visible Arabic, English, and German identity records; an anti-thin-content inventory; a non-fabricated Day-0 visibility baseline; local/live readiness auditing; constrained IndexNow changed-URL notification; and a verified custom-domain migration/rollback plan.
- Identity: primary Arabic name `أحمد الحافظ`; preferred Latin name `Ahmed Alhafiz`; secondary search transliteration `Ahmad Alhafiz`; canonical author ID `https://ahmed-alhafiz.github.io/#person`.
- External identity links: Medium and Instagram only. Email remains a contact field, not a `sameAs` identity profile.
- Measurement boundary: technical deployment, crawler access, structured data, and IndexNow receipt are not reported as Google ranking, indexing, knowledge-panel creation, traffic, or AI citation.
- Content policy: three current pillars, one pillar candidate, supporting briefs retained only for distinct reader intent, and no deletion or consolidation before baseline/overlap review and redirect planning.
- Domain status: migration plan prepared; no domain purchased, DNS changed, CNAME activated, or canonical host changed.
- Status: `PREMERGE_VERIFICATION_REQUIRED`.
'''
    if "Canonical author entity, measurement, domain, and IndexNow foundation 12" in ledger:
        raise RuntimeError("Ledger foundation entry already present")
    ledger_path.write_text(ledger + entry, encoding="utf-8")


def normalize() -> None:
    suffixes = {".html", ".css", ".json", ".md", ".py", ".yml", ".xml", ".txt"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in suffixes:
            continue
        text = path.read_text(encoding="utf-8")
        path.write_text("\n".join(line.rstrip() for line in text.rstrip().splitlines()) + "\n", encoding="utf-8")


def main() -> None:
    pages = sorted(
        path
        for path in ROOT.rglob("*.html")
        if ".git" not in path.parts and path.name not in EXCLUDED_HTML
    )
    link_count = person_count = 0
    for page in pages:
        links, persons = patch_html(page)
        link_count += links
        person_count += persons

    insert_identity(
        ROOT / "about/index.html",
        AR_IDENTITY,
        '<a class="btn" href="#works">المؤلفات</a>',
        '<a class="btn" href="#identity">تمييز الهوية</a>',
    )
    insert_identity(
        ROOT / "en/about/index.html",
        EN_IDENTITY,
        '<a class="btn" href="/en/#works">Forthcoming books</a>',
        '<a class="btn" href="#identity">Identity record</a>',
    )
    insert_identity(
        ROOT / "de/about/index.html",
        DE_IDENTITY,
        '<a class="btn" href="/de/#research">Forschung</a>',
        '<a class="btn" href="#identity">Identitätsnachweis</a>',
    )
    patch_css()
    patch_integrity_workflow()
    patch_visual_review()
    update_checkpoint_and_ledger()
    normalize()

    if link_count != len(pages):
        raise RuntimeError(f"Expected one link patch per page, found {link_count}/{len(pages)}")
    if person_count < 20:
        raise RuntimeError(f"Expected at least 20 canonical Person nodes, found {person_count}")
    print(f"Patched {len(pages)} public pages and standardized {person_count} canonical Person nodes")


if __name__ == "__main__":
    main()
