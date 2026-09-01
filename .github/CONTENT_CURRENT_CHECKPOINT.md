# Content Project Current Checkpoint — Ahmed Alhafiz

**Updated:** 2026-09-01

## Governing directive

Before any website, article, SEO, AI-discoverability, or book-linked content work, read in order:

1. `.github/PROJECT_GOVERNING_DIRECTIVE.md`
2. `.github/SEO_SOURCE_OF_TRUTH.md`
3. `.github/SEO_OPERATIONS_LEDGER.md`
4. `.github/CONTENT_CURRENT_CHECKPOINT.md`

## Current source priority

1. «قل سيروا في الأرض فانظروا كيف بدأ الخلق» — active first article cluster.
2. «أم عباس لجلب الحبيب ورد المطلقة» — active second article cluster.
3. «كتاب الكتب» — deferred until explicit instruction.
4. «جهيمان — القيامة بين الركن والمقام» — deferred until explicit instruction.

## Accuracy correction

A prior checkpoint/report overstated the completion of the first research release. Inspection of the actual `main` tree on 2026-09-01 established the following:

- Live on `main`: the article hub, the ratq/fatq study, the sleep-paralysis report, the psychological-horror guide, methodology, feed, author/book links, and the structural site audit.
- Not present on `main` before release candidate 04: the six-creation-days study, the functional-seizures report, and the editorial quality-gate script.
- Several failed one-time release workflows, manifests, bridge tests, and two incomplete bundle parts remained in the repository despite the earlier statement that all temporary artifacts had been removed.
- Therefore no claim that four reference studies were live was valid before release candidate 04 is merged and publicly verified.

This correction does not erase historical records. It supersedes only the inaccurate completion and verification claims about the missing files and cleanup state.

## Verified live baseline before release candidate 04

- `/articles/`
- `/articles/ratq-fatq-big-bang/`
- `/articles/sleep-paralysis-jathoom/`
- `/guides/arabic-psychological-horror/`
- `/methodology/`
- `/articles/feed.xml`
- linked Arabic pages for the author, «سيروا في الأرض», and «أم عباس»
- `tools/site_audit.py`
- `.github/workflows/site-integrity.yml`

## Release candidate 04 — branch `editorial-release-04`

Prepared and committed on the feature branch:

1. `/articles/six-days-creation-cosmic-time/`
   - Reference study separating Qur'anic text, classical interpretation, measured cosmic/terrestrial ages, and philosophical inference.
   - Direct answer, explicit uncertainty, eleven machine-readable and visible sources, Article/WebPage/Breadcrumb schema, and a truthful forthcoming-book relation.

2. `/articles/functional-seizures-vs-epilepsy/`
   - Medical reference report separating functional seizures from epileptic seizures.
   - Covers history, witnesses, smartphone video, video-EEG, coexisting epilepsy, treatment evidence, medication limits, first aid, family response, and AI diagnostic limits.
   - Contains emergency guidance, educational-only wording, medication-change warning, ten machine-readable and visible sources, MedicalWebPage/Article/Breadcrumb schema, and a truthful forthcoming-novel relation.

3. Article hub, Atom feed, sitemap, and both active Arabic book pages updated with reciprocal links to the new studies.

4. Added `tools/editorial_quality_gate.py` to enforce:
   - substantial visible analysis;
   - direct-answer blocks;
   - Article abstracts and book relations;
   - source count and domain diversity;
   - hub/feed/sitemap coverage;
   - reciprocal book links;
   - uncertainty language;
   - medical disclaimers, urgent-care language, treatment-specific medication warnings, and MedicalWebPage schema.

5. Expanded `.github/workflows/site-integrity.yml` so pull requests and pushes compile both audit tools, parse all JSON-LD/XML, run the structural audit, run the editorial quality gate, and check patch whitespace.

6. Removed obsolete release artifacts from the feature branch:
   - bridge test files;
   - incomplete release bundle parts;
   - stale manifests;
   - failed one-time apply/finalize workflows.

## Release status

- Current state: `RELEASE_CANDIDATE_AWAITING_CI`.
- The new pages must not be described as live until the pull-request checks pass, the branch is merged into `main`, GitHub Pages deploys, and the public URLs are fetched successfully.
- Search ranking and AI citation improvement remain measurement questions, not deployment facts.

## Baseline measurement

Latest verified Search Console period before the research expansion: 2026-08-23 to 2026-08-29.

- Homepage: 15 clicks, 54 impressions, 27.78% CTR, average position 3.98.
- `/about/`: 2 clicks, 15 impressions, 13.33% CTR, average position 4.73.

These are small early samples. Do not claim ranking improvement until later finalized windows exist.

## Immediate next actions

1. Open a pull request from `editorial-release-04` to `main`.
2. Require the full structural and editorial quality workflow to pass; inspect logs and repair every blocking failure.
3. Merge only after green checks.
4. Verify the GitHub Pages deployment and each public route, plus sitemap and Atom feed.
5. Record the exact release commit and live-verification result.
6. After release, avoid immediate rewrites. Measure finalized Search Console and referral data at 14, 28, and 56 days.
7. Continue the next article only when it adds a distinct information need rather than repeating the current studies. The next provisional Sirou topic is «تعليم الأسماء والذكاء الاصطناعي: من المفهوم إلى الآلة»; the next provisional Umm-Abbas topic is exploitation of frightened families by fraudulent spiritual healers. Both require fresh source research and the same quality gates.
