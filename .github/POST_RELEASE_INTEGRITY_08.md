# Post-release Integrity 08

**Prepared:** 2026-09-02  
**Status:** `EXECUTED_VERIFIED`

## Defect found

The Arabic and English feeds contained timestamps later than the real public deployment and later than the then-current local time. The Arabic feed also omitted the psychological-horror guide, and the machine research index contained six items although the research hub declared seven Arabic research surfaces.

## Correction

- Verified original rebuild deployment completion used as release/update time: `2026-09-02T04:33:19+02:00`.
- Arabic Atom and JSON feeds aligned to all seven Arabic research surfaces.
- English Atom and JSON feeds aligned to the complete English flagship dossier.
- Earlier Arabic publication dates preserved; global-rebuild modifications use the verified deployment time.
- The psychological-horror guide added to `articles/research-index.json`.
- `tools/discovery_integrity.py` added as a permanent gate against:
  - future-dated feed entries;
  - feed/index/hub drift;
  - missing public pages or sitemap URLs;
  - duplicate research URLs or slugs;
  - one-way links between research and its related forthcoming book;
  - missing machine review and related-book identifiers.
- Completed one-time correction machinery removed before merge.

## Verification record

- One-time branch correction workflow: `33584638355` — success.
- Pull request: `#11`.
- Final pull-request head: `35b9ff05392027c1aa4b7ef20f49cfc544ec2bc3`.
- Pull-request `Site integrity`: `33585129924` — success; permanent discovery gate reported seven Arabic research surfaces, one complete English edition, valid chronology, feeds, hub, sitemap and reciprocal book links.
- Pull-request `Visual review`: `33585129947` — success; 26 desktop/mobile screenshots generated and manually inspected.
- Squash merge: `06e106494936e47aa93b1b74c3c7450e943e82d7`.
- Main-branch `Site integrity`: `33585344480` — success.
- GitHub Pages deployment: `33585343848` — success; completed at `2026-09-02T03:01:03Z` (`05:01:03+02:00`).

## Live verification

After deployment, the public Arabic JSON Feed exposed seven entries with non-future publication/update times, the English JSON Feed exposed the complete English flagship dossier with machine review/book identifiers, and `articles/research-index.json` exposed all seven Arabic research records. The public Arabic research hub and both related book pages were fetched successfully after deployment.

The Atom files were parsed in pull-request and main-branch CI and deployed in the same successful Pages build. A third-party content extractor declined to render the live XML media type; this is recorded as a crawler limitation, not treated as an independent live-content parse.

## Measurement boundary

This correction proves structural and deployment integrity only. It does not prove improved Google ranking, traffic, links, recommendations or AI citations. Those outcomes remain subject to real Search Console and referral evidence at the established 14-, 28- and 56-day windows.
