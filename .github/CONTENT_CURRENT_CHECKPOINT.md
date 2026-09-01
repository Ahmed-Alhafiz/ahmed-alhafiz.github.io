# Content Project Current Checkpoint — Ahmed Alhafiz

**Updated:** 2026-09-02

## Governing directive and mandatory memory

Before any website, article, SEO, AI-discoverability, or book-linked content work, read in order:

1. `.github/PROJECT_GOVERNING_DIRECTIVE.md`
2. `.github/SEO_SOURCE_OF_TRUTH.md`
3. `.github/SEO_OPERATIONS_LEDGER.md`
4. `.github/SEO_OPERATIONS_CORRECTION_2026-09-01.md`
5. `.github/CONTENT_CURRENT_CHECKPOINT.md`

The correction file supersedes only inaccurate earlier claims about the number of live studies, cleanup, and verification. It does not erase work that was actually present.

## Current source priority

1. «قل سيروا في الأرض فانظروا كيف بدأ الخلق» — active first article cluster.
2. «أم عباس لجلب الحبيب ورد المطلقة» — active second article cluster.
3. «كتاب الكتب» — deferred until explicit instruction.
4. «جهيمان — القيامة بين الركن والمقام» — deferred until explicit instruction.

## Accuracy correction

A prior report overstated completion of the first research release. Inspection of the actual `main` branch found that only two reference studies were live at that point and that failed one-time release artifacts remained. The missing work was rebuilt on a feature branch, subjected to pull-request checks, merged, deployed, and verified. The factual record is preserved in `.github/SEO_OPERATIONS_CORRECTION_2026-09-01.md`.

## Verified reference release 04

- Status: `EXECUTED_VERIFIED`.
- Pull request: `#7`.
- Merge commit: `73c7d57dd421e4a632a8f9b77eadf563a9af2516`.
- Pull-request integrity run: `33563747279` — success.
- Post-merge integrity run: `33563836430` — success.
- Public-page fetch confirmed the article hub, both new HTML studies, and both updated book pages were serving the merged content.
- Sitemap and Atom feed were validated from the merged repository and by the CI XML/content checks.

### Live reference studies

1. `/articles/ratq-fatq-big-bang/`
   - 2,079 visible words;
   - 8 visible sources.

2. `/articles/six-days-creation-cosmic-time/`
   - 2,598 visible words;
   - 11 visible sources;
   - separates Qur'anic text, classical interpretation, measured cosmic/terrestrial ages, and inference.

3. `/articles/sleep-paralysis-jathoom/`
   - 2,379 visible words;
   - 6 visible sources.

4. `/articles/functional-seizures-vs-epilepsy/`
   - 2,775 visible words;
   - 10 visible sources;
   - includes urgent-care guidance, educational-only language, medication safeguards, and diagnostic limits.

### Supporting public surfaces

- `/articles/`
- `/guides/arabic-psychological-horror/`
- `/methodology/`
- `/articles/feed.xml`
- `/books/sirou-fi-alard/`
- `/books/umm-abbas/`
- `/about/`

The corresponding book pages and articles contain reciprocal visible and structured links. Both books remain described as forthcoming / `قيد الإصدار`.

## Persistent quality controls

The repository now contains:

- `tools/site_audit.py`
- `tools/editorial_quality_gate.py`
- `.github/workflows/site-integrity.yml`

Every pull request and push to `main` checks:

- Python syntax;
- XML and all JSON-LD blocks;
- HTML, canonical, sitemap, feed, and internal-link integrity;
- publication safety for unpublished works;
- article depth and direct-answer blocks;
- visible and machine-readable source counts;
- source-domain diversity;
- reciprocal book links;
- explicit uncertainty;
- medical disclaimers, urgent-care language, treatment-specific medication warnings, and MedicalWebPage schema.

Verified structural result for release 04:

- HTML pages: 25;
- canonicals: 25;
- sitemap URLs: 25;
- errors: 0;
- warnings: 0.

All four reference studies passed the editorial, evidence, linking, uncertainty, and safety gates.

## Cleanup state

Removed:

- bridge tests;
- incomplete bundle parts;
- stale manifests;
- failed one-time apply/finalize workflows;
- the later inactive one-time recorder and its trigger manifest.

Only persistent operational files and the site-integrity workflow should remain. Do not recreate one-time release workflows unless an ordinary feature-branch / pull-request path is technically impossible.

## Baseline measurement

Latest verified Search Console period before the research expansion: 2026-08-23 to 2026-08-29.

- Homepage: 15 clicks, 54 impressions, 27.78% CTR, average position 3.98.
- `/about/`: 2 clicks, 15 impressions, 13.33% CTR, average position 4.73.

These are small early samples. Deployment does not prove ranking growth or AI citation. Compare finalized data at 14, 28, and 56 days after release 04.

## Next research batch

Proceed on a clean feature branch and publish only after the same structural/editorial gates pass.

### «قل سيروا في الأرض»

Provisional next study:

**«تعليم الأسماء والذكاء الاصطناعي: هل تفهم الآلة الكلمات أم تتنبأ بها؟»**

Required distinctions:

- Qur'anic text and classical interpretation;
- naming, concept formation, reference, and symbol grounding;
- what Transformer language models technically do;
- behavioral capability versus claims of human-like understanding;
- human agency, intention, responsibility, and the limits of theological analogy.

### «أم عباس»

Provisional next study:

**«حين يتحول العلاج الروحي إلى استغلال: كيف تحمي الأسرة المريض من الدجل والاعتداء؟»**

Required distinctions:

- legitimate voluntary religious support versus diagnosis/treatment claims;
- coercion, isolation, financial exploitation, sexual boundary violations, and victim blaming;
- preserving medical and psychiatric assessment;
- emergency and safeguarding procedures;
- culturally respectful language that neither validates unverified supernatural causation nor ridicules religious belief.

Both studies require fresh primary/official research, manuscript disclosure review, truthful reciprocal book linking, and the persistent quality gates.
