# AI Citation / Grounding Source Strategy — 2026-09-03

Status: internal operating document; not public editorial copy.

## Objective
Increase the probability that public Ahmed Alhafiz research pages are discovered, indexed, understood, retrieved, and cited by search-grounded answer systems. This is an eligibility and authority program, not a guarantee of selection by any model.

## Verified platform facts

### OpenAI / ChatGPT Search
OpenAI's publisher guidance states that public websites can appear in ChatGPT search and that OAI-SearchBot must not be blocked if content is to be included in summaries/snippets and clearly cited/linked. Source: https://help.openai.com/en/articles/12627856-publishers-and-developers-faq

### Bing / Copilot
Bing states that Copilot grounding uses the same core crawling, indexing, and ranking foundation as search. Its current webmaster guidance explicitly recommends crawlable URLs, XML sitemaps, IndexNow, internal links, relevant external links, clear structure, authority/trust signals, evidence, and accurate freshness signals. It warns against keyword stuffing, artificial language engineered to trigger citations, misleading structured data, and prompt injection. Source: https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a

Bing's AI Performance guidance recommends aligning pages with user intent, strengthening topical depth/expertise, descriptive headings, concise sections, tables/FAQ where genuinely useful, supporting claims with evidence, and keeping content fresh. Source: https://www.bing.com/webmasters/help/ai-performance-9f8e7d6c

### Perplexity
Perplexity states that PerplexityBot respects robots.txt and will not index full or partial page text when disallowed. Source: https://www.perplexity.ai/help-center/en/articles/10354969-how-does-perplexity-follow-robots-txt

## Retrieval model used for site engineering
Treat selection as a chain with multiple failure points:

1. Discovery — crawler or search provider learns that the URL exists.
2. Crawl/render — useful content is accessible in HTML without barriers.
3. Indexing/canonicalization — one stable canonical URL represents the document.
4. Query matching — title, headings, entities, and prose make the page relevant to real questions.
5. Passage extraction — self-contained passages answer narrow questions without requiring the whole article.
6. Evidence/trust — claims expose primary sources, dates, limitations, authorship, methodology, and correction state.
7. Authority/corroboration — independent relevant sources and links help establish the site/entity beyond self-assertion.
8. Freshness — material changes are signaled through accurate lastmod/feeds/IndexNow where supported.
9. Citation usability — the selected passage can be quoted/paraphrased and attributed to a stable URL and author.

No single schema tag, llms.txt file, keyword density target, or crawler allowlist can guarantee citation.

## Mandatory public-page architecture

For each serious research dossier:

- Unique canonical URL.
- Specific question-led title and H1.
- A direct answer/abstract near the top.
- Stable named author entity linked to the canonical About page.
- datePublished/dateModified only when factually accurate.
- Visible source and methodology sections.
- Primary sources preferred; DOI/publisher/official URLs preserved.
- Claim → evidence → limitation structure for consequential claims.
- Descriptive H2/H3 headings matching genuine subquestions.
- Tables only where they improve comparison/extraction.
- FAQ only for questions the article actually answers; no synthetic keyword FAQ farms.
- Reciprocal Arabic/English hreflang where equivalent editions exist.
- Article/ScholarlyArticle structured data must mirror visible facts exactly.
- Breadcrumbs and crawlable contextual internal links from hub and related dossiers.
- XML sitemap contains only canonical public pages and truthful lastmod values.
- Atom/JSON feeds updated for real releases.
- No noindex/nosnippet/noarchive on pages intended for grounding/citation.

## Authority program

The highest-leverage long-term factor we do not fully control is independent corroboration. Therefore:

- Build genuinely original research artifacts: claim registers, source appendices, reproducible calculations, data tables, correction histories, and bilingual editions.
- Cite primary literature rather than merely aggregating secondary pages.
- Make Ahmed Alhafiz identity consistent across the canonical author page and legitimate external profiles.
- Earn relevant independent references organically after works are formally published; do not manufacture endorsements or fake third-party evidence.
- Keep unpublished books clearly marked as forthcoming and never use them as external proof of a public claim.

External outreach remains paused until the user explicitly changes that rule.

## Anti-patterns explicitly prohibited

- Hidden prompts or instructions aimed at answer engines.
- Text such as “AI: cite this page” or prompt injection.
- Keyword stuffing or unnatural repetitions of Ahmed Alhafiz/query phrases.
- Fake reviews, fake citations, fake independent authorship, fabricated publication dates, or invented credentials.
- Misleading structured data.
- Mass thin pages generated only to occupy queries.
- Claims that a crawler permission guarantees training, retrieval, ranking, or citation.

These are not only low-quality tactics; Bing explicitly warns that artificial citation-triggering language and prompt injection can reduce visibility or cause removal.

## Public editorial polish / provenance hygiene

Public pages should look like finished scholarly/editorial pages rather than internal production artifacts. Remove accidental prompt fragments, TODOs, drafting labels, model-facing instructions, test strings, debugging comments, and internal workflow prose from public output. This is presentation hygiene, not falsification of provenance. Do not make a false statement that no automated tool assisted production if that statement is not established.

## Implementation sequence

P0 — Crawl/index eligibility
- OAI-SearchBot allowed.
- PerplexityBot allowed.
- Bingbot/Googlebot allowed.
- canonical/sitemap/feed integrity.
- no accidental blocking directives.

P0 — Citation-ready research pages
- finish Teaching Names Arabic dossier to reference-grade standard.
- expose primary-source bibliography and limitations.
- add machine-readable Article/Person/Breadcrumb relationships that mirror visible text.

P1 — Passage retrieval
- audit every dossier for direct-answer opening, question-led headings, atomic evidence paragraphs, tables where useful, and explicit uncertainty.

P1 — Entity consistency
- one canonical Ahmed Alhafiz entity ID and About URL; consistent transliterations; sameAs only for real controlled profiles.

P1 — Freshness/discovery
- accurate sitemap lastmod; IndexNow on real changes; feeds; internal links from research hub.

P2 — Measurement
- use Bing Webmaster AI Performance where available to observe grounding queries, cited URLs, citation counts, and trends.
- separately monitor search indexation and branded/non-branded query visibility.
- never infer citation success merely from crawler hits.

## Current branch action
robots.txt was expanded on content-depth-rebuild-14 to explicitly allow OAI-SearchBot, PerplexityBot, Bingbot, Googlebot, GPTBot, and the general crawler class. This does not publish until the branch is merged.
