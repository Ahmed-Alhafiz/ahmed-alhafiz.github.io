# Post-merge truth sync 15 — 2026-09-05

## Scope

Synchronize current operational source-of-truth records with the verified state already released through PR #20, without changing public layout or design.

## Verified starting point

- Base branch: `main`.
- Base commit: `30cbb9bc1f12e2944b125f52e40c81814855e232`.
- PR #20 merged successfully.
- GitHub Pages deployment `33958995913` completed successfully.
- Official Juhayman title: `جُهَيْمَان — خوارج بين الركن والمقام`.
- Teaching the Names is a complete Arabic/English pillar; final recorded reference-grade score: 88/100.

## Drift corrected by this branch

1. Current governing/SEO/checkpoint records still carried the retired Juhayman title.
2. `data/content-inventory.json` still classified Teaching the Names as an Arabic-only pillar candidate.
3. Entity integrity still enforced the historical 3-pillar/1-candidate strategy.
4. Visibility auditing did not compare inventory languages with the machine research index and did not enforce the baseline count of complete bilingual pillars.

## Intended invariant after this branch

- Four current bilingual pillars; zero pillar candidates.
- Inventory language declarations must match `articles/research-index.json` by slug.
- The baseline expectation of four complete bilingual pillars is measured by `tools/visibility_audit.py`.
- The canonical Juhayman title is enforced across the current public book surfaces and current operational control documents.
- The 20–30 minute work-round rule is encoded in the governing directive.
- No public design, CSS, layout, canonical URL, or book-page content is changed in this synchronization branch.

## Merge gate

Do not merge unless all required workflows are green on the same final head commit. After merge, verify the resulting `main` and GitHub Pages deployment before recording completion.
