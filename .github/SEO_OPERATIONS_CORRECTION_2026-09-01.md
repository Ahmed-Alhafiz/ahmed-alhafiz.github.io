# Accuracy Correction and Verified Reference Release 04

**Date:** 2026-09-01  
**Status:** `EXECUTED_VERIFIED`  
**Supersedes:** only the inaccurate completion/verification portions of the earlier first-reference-release report and checkpoint. It does not erase work that was actually present.

## Why this correction exists

A direct inspection of the `main` branch found that an earlier report overstated the deployment state. At that time, the following were genuinely live:

- the article hub;
- the ratq/fatq reference study;
- the sleep-paralysis/jathoom report;
- the psychological-horror guide;
- the methodology page;
- the Atom feed and initial structural audit.

However, the earlier report incorrectly stated that two additional studies, an editorial quality gate, complete cleanup of temporary release artifacts, and a final four-article verification were already live. The two pages were absent from `main`, and several failed one-time workflows, stale manifests, bridge tests, and incomplete bundle parts remained.

## Corrective release

Pull request #7 was created from `editorial-release-04`, passed its complete pull-request integrity workflow, and was squash-merged into `main` as:

`73c7d57dd421e4a632a8f9b77eadf563a9af2516`

The post-merge integrity workflow also completed successfully.

## New public studies

1. `/articles/six-days-creation-cosmic-time/`
   - 2,598 visible words at CI verification;
   - 11 visible external references;
   - separates Qur'anic text, classical interpretation, measured cosmic/terrestrial ages, and philosophical inference;
   - includes a direct answer, explicit uncertainty, Article/WebPage/Breadcrumb structured data, and a truthful relation to the forthcoming «قل سيروا في الأرض» page.

2. `/articles/functional-seizures-vs-epilepsy/`
   - 2,775 visible words at CI verification;
   - 10 visible external references;
   - distinguishes functional seizures from epileptic seizures and covers history, witnesses, smartphone video, video-EEG, possible coexistence, treatment evidence, first aid, family response, medication limits, and AI diagnostic limits;
   - includes emergency guidance, educational-only language, a medication-change warning, MedicalWebPage/Article/Breadcrumb structured data, and a truthful relation to the forthcoming «أم عباس» page.

## Discovery and reciprocal linking

The release updated:

- `/articles/`;
- `/articles/feed.xml`;
- `sitemap.xml`;
- `/books/sirou-fi-alard/`;
- `/books/umm-abbas/`.

Both new studies are linked visibly and in structured data from their corresponding book pages, and each study links back to the relevant forthcoming work and to the author page.

## Persistent quality controls

Added `tools/editorial_quality_gate.py` and expanded `.github/workflows/site-integrity.yml` so every pull request and push to `main` checks:

- Python syntax for both audit tools;
- XML parsing;
- every JSON-LD block;
- HTML/canonical/sitemap integrity;
- internal and reciprocal links;
- publication-safety rules for unpublished works;
- minimum reference-article depth;
- direct-answer sections;
- visible and machine-readable source counts;
- source-domain diversity;
- explicit uncertainty language;
- medical disclaimers, urgent-care language, treatment-specific medication warnings, and MedicalWebPage schema.

## Verified results

Pull-request workflow run: `33563747279` — success.  
Post-merge workflow run: `33563836430` — success.

Structural audit result:

- HTML pages: 25;
- canonicals: 25;
- sitemap URLs: 25;
- errors: 0;
- warnings: 0.

Editorial gate result:

- ratq/fatq: 2,079 visible words / 8 visible sources;
- six days/cosmic time: 2,598 / 11;
- sleep paralysis/jathoom: 2,379 / 6;
- functional seizures/epilepsy: 2,775 / 10;
- all four passed the evidence, linking, uncertainty, and safety gates.

A direct public-page fetch confirmed that the article hub, both new HTML studies, and both corresponding book pages were serving the merged content. The sitemap and Atom feed were separately validated from the merged repository and by the CI XML/content checks.

## Cleanup

The corrective release removed:

- bridge-test files;
- incomplete release bundle parts;
- stale release manifests;
- failed one-time apply/finalize workflows.

A later recorder workflow failed to register its intended trigger. It and its trigger manifest were then removed manually. No claim of its successful execution is made.

## Publication safety

Both works remain described as forthcoming / `قيد الإصدار`. The corrective release added no unconfirmed publisher, ISBN, fixed publication date, sales claim, review, long excerpt, or plot-sensitive disclosure.

## Measurement rule

Deployment proves only that the pages and controls are present and technically valid. It does not prove ranking growth or citation by an AI system. Compare finalized Search Console and referral data at 14, 28, and 56 days after the corrective release, and expand only articles that serve a distinct information need.
