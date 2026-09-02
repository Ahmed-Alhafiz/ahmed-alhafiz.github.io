# Global Editorial Rebuild 07 — Pre-merge Record

Date: 2026-09-02

## Scope

This release replaces the portfolio-style public presentation with a bilingual author-and-research platform. It includes a redesigned editorial system, Arabic and English research hubs, a bilingual flagship dossier, machine-readable evidence outputs, methodology and research-status pages, strengthened author/book linking, and persistent structural, editorial, safety and visual review workflows.

## Verified before this record

- The reviewed release archive was reconstructed and matched its expected base64 and decoded SHA-256 digests exactly.
- The branch-level structural audit reported 34 public HTML pages, 34 canonical URLs, 34 sitemap URLs, zero structural errors and zero structural warnings.
- Seven research pages passed the editorial, evidence, transparency, reciprocal-link and medical-safety gates.
- JSON-LD blocks, XML feeds and evidence JSON parsed successfully.
- Desktop and mobile screenshots of the priority pages were generated and manually inspected.
- Book-page mobile hierarchy was corrected after visual inspection.
- Visible language switchers now point to the exact Arabic or English counterpart declared by each page's `hreflang` metadata. German is not displayed on research surfaces that do not yet have a genuine German counterpart.
- Evidence appendices now expose explicit Arabic and English `hreflang` navigation.
- The two forthcoming books are linked thematically and are not presented as independent evidence.
- No claim is made that rankings or AI citations improved before real measurement.

## Previous stale check and correction

A pull-request integrity run attached to the trigger commit failed because it began before the one-time language-correction workflow finished. The correction workflow then completed successfully and committed the corrected surface state. This record intentionally creates a new pull-request head so that both permanent gates run against the corrected files rather than against the stale trigger snapshot.

## Final merge gate

The current pull-request head must receive fresh successful runs of:

1. `Site integrity`;
2. `Visual review`.

After both succeed, inspect the new visual artifact, merge pull request #10, wait for GitHub Pages deployment, and verify the public homepage, article hubs, flagship Arabic/English dossier, evidence appendix, methodology pages, research-status pages, author page, book pages, sitemap and feeds.
