# Performance and research-index follow-up — 2026-10-01

Base: PR #128, main 4840936b265de89dc16b8032619c065edd457d65, deployed and live verified.

## Measured asset changes

Original portrait: 202060 bytes. Responsive WebP files: 348px / 10236 bytes; 560px / 20654 bytes; 840px / 40424 bytes; 1229px / 72290 bytes. Transfer savings range 64.2–94.9%, depending on the selected candidate. Original PNG remains the fallback and structured identity image. Six home/profile pages keep alt text, original width/height, CSS geometry and priority. Browsers choose candidates using srcset/sizes. This does not measure LCP, Core Web Vitals or a ranking gain.

Shared articles.css now contains its five imported styles in their original order, without rule rewriting. Five nested stylesheet requests are removed. The five editable sources and wrapper remain; tools/build_article_styles.py rebuilds the bundle and --check is required by site-integrity CI. Relative URLs, nested imports and charsets fail explicitly rather than change meaning silently.

## Honest structured discovery

The hub generator now synchronizes the one research ItemList with the visible grouped list, including order, title, URL and item count. Published editions remain 40 Arabic, 8 English, 4 German. No new doorway pages, keywords stuffing, artificial review/rating schema or content claims. Profile primary controls now receive the full shape/tap-target rules rather than the older flat-link override.

## Checks and red team

Local site audit: 88 pages/canonicals/sitemap URLs, zero errors/warnings. Discovery, UX, Arabic UI, entity, hygiene, editorial, dossier, citation, research architecture, visibility, governance, compilation and diff checks passed. The bundle was compared byte-for-byte with deterministic source expansion. Responsive CI adds currentSrc/resolution checks, absence of import rules, visible-versus-schema order/title checks and button-size/radius checks on all six home/profile pages. Full desktop/mobile/narrow-phone screenshots and human review remain required before merge.

## Limits and next measurement

No current Search Console ranking data, field performance score, indexing guarantee, specialist article review or new substantive translation claimed. Three English translation-sync comparison flags remain from the preceding audit. No charge or analytics/privacy change. Release head, CI, visual human review, merge, Pages and live verification are tracked in the follow-up PR. Laptop: compare Search Console queries/pages over equal date ranges, prioritize real impressions and relevance, and resolve translation flags before publishing semantic changes.

Primary guidance: https://web.dev/learn/images/responsive-images and https://developers.google.com/search/docs/appearance/page-experience and https://developers.google.com/search/docs/fundamentals/do-i-need-seo .
