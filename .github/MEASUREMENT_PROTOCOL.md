# Search, Entity, and AI-Citation Measurement Protocol

**Project:** Ahmed Alhafiz official author and research site  
**Protocol version:** 1.0  
**Established:** 2026-09-02  
**Governing rule:** unknown values remain unknown; technical readiness is never reported as an external outcome.

## 1. Why this protocol exists

The project has previously completed substantial design, structured-data, evidence, feed, sitemap, and crawler-access work. Those actions make discovery possible. They do not prove that Google ranks the site first, that a rich result appears, or that an AI system cites the site.

Every future report must separate four layers:

1. **Published:** the file exists in the permanent branch.
2. **Deployed:** the public URL returns the intended current content.
3. **Discovered/indexed:** a search engine or external retrieval system has recorded or surfaced the URL.
4. **Ranked/cited:** the page appears for a defined query or is explicitly used as a linked source.

No layer is inferred from the previous one.

## 2. Canonical identity queries

The identity measurement set is intentionally small. It must not be expanded into doorway pages or mass-generated spelling variants.

| ID | Query | Purpose |
|---|---|---|
| Q-ID-AR-01 | `أحمد الحافظ` | Primary Arabic identity query |
| Q-ID-EN-01 | `Ahmed Alhafiz` | Preferred Latin spelling |
| Q-ID-EN-02 | `Ahmad Alhafiz` | Secondary transliteration used only for disambiguation |
| Q-ID-AR-02 | `أحمد الحافظ كاتب` | Arabic author-intent query |
| Q-ID-EN-03 | `Ahmed Alhafiz author` | English author-intent query |

The success target is the official site and profile page receiving the strongest relevant position for these identity queries. No position is recorded without a dated observation or Search Console evidence.

## 3. Pillar-question query sets

Each reference dossier receives its own query cluster. Query sets are created from the actual question answered by the page, not from unrelated high-volume keywords.

Current pillars:

- `ratq-fatq-big-bang`
- `water-civilization-power`
- `diagnostic-uncertainty-family-fear-coercive-authority`

Current pillar candidate:

- `teaching-names-ai-understanding`

The complete inventory and next action for each indexed page live in `data/content-inventory.json`.

## 4. Accepted evidence sources

### 4.1 Google indexing and search performance

Authoritative sources, in descending order:

1. Google Search Console URL Inspection / indexing data.
2. Google Search Console Performance report or API, filtered by query, page, country, device, and date.
3. A controlled signed-out manual observation recorded with timestamp, country, device, interface language, and screenshot.

A `site:` query is useful for diagnosis but is not treated as an authoritative page count or ranking measure.

### 4.2 Bing and IndexNow

- A successful IndexNow response proves only that the endpoint received the URL set or accepted it pending key validation.
- It does not prove crawl, indexing, ranking, or inclusion in any specific engine.
- Bing Webmaster Tools data, when connected, is reported separately from IndexNow transport status.

### 4.3 ChatGPT and other AI answer systems

A verified AI citation requires all of the following:

- an externally generated answer;
- a visible citation or link to the exact site page;
- the question, product/interface, date, language, and region recorded;
- a screenshot or export preserved;
- no prompting that falsely presupposes the site as an authority.

Crawler permission is a technical prerequisite only. It is not an AI citation.

### 4.4 Referral traffic

ChatGPT referral traffic may be isolated by `utm_source=chatgpt.com` when an analytics or log source is available. Until such a source is connected, the value remains `null`, not zero.

## 5. Baseline windows

### Day 0

Record:

- permanent commit;
- successful site-integrity and deployment runs;
- live HTTP status;
- canonical, hreflang, sitemap, feed, crawler, and identity-manifest state;
- current external metrics as `not_measured` where no source exists.

### Day 7

Check only fast-moving technical effects:

- public availability;
- sitemap/feed consistency;
- Search Console discovery and indexing state if available;
- errors or excluded pages;
- IndexNow transport results.

Do not rewrite titles because rankings have not moved in seven days.

### Day 30

First useful content-level review:

- identity-query impressions and positions;
- pillar-query impressions and positions;
- pages with zero impressions;
- overlapping pages competing for the same query;
- external links and AI referrals if observed;
- whether a supporting brief should remain, merge, redirect, or deepen.

### Day 90

Strategic review:

- trend rather than one-day position;
- whether the custom domain migration improved or damaged discovery;
- which pillar deserves another language or data asset;
- which low-value URLs should be consolidated with redirects;
- whether independent authority signals have appeared after official book publication.

## 6. Required observation record

Every manual search observation uses this structure:

```json
{
  "captured_at": "ISO-8601 timestamp",
  "engine_or_product": "Google Search | Bing | ChatGPT Search | other",
  "query": "exact query",
  "country": "country",
  "device": "mobile | desktop",
  "interface_language": "language",
  "signed_in": false,
  "result_url": "exact URL or null",
  "position_or_citation": "integer, linked citation, or not observed",
  "evidence_file": "screenshot/export path",
  "notes": "personalization, ambiguity, or limitation"
}
```

No undated memory-based ranking report is accepted.

## 7. Change-control rules during measurement

- Correct factual, legal, medical, security, accessibility, and broken-link defects immediately.
- Do not change canonical URLs or merge indexed pages without a redirect plan.
- Do not alter a pillar title repeatedly in response to day-to-day ranking noise.
- Do not publish multiple near-duplicate pages for spelling variants of the author name.
- Do not manufacture reviews, backlinks, citations, engagement, or independent-looking sites.
- Do not count Medium, Instagram, GitHub, or the official site linking to itself as independent authority.
- Keep unpublished works explicitly marked as forthcoming until public publication data is verified.

## 8. Automation boundary

The repository can automatically verify:

- public HTTP availability;
- robots rules;
- sitemap and feed structure;
- canonical author identity consistency;
- machine-readable manifests;
- internal discovery links;
- IndexNow request transport and response.

The repository cannot honestly infer without connected external data:

- Google position;
- total indexed pages;
- knowledge-panel creation;
- AI citation frequency;
- referral sessions;
- independent editorial authority.

Those fields remain `not_measured` until a valid source is connected.

## 9. Current baseline

The structured Day-0 baseline is stored at:

- `data/visibility-baseline.json`

Automated technical observations are produced by:

- `tools/visibility_audit.py`
- `.github/workflows/visibility-monitor.yml`

Content role and consolidation decisions are controlled by:

- `data/content-inventory.json`
