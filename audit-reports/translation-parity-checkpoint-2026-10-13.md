# Translation parity checkpoint — 13 October 2026

GitHub is the source of truth. Base main for this snapshot: `240900aa414cfa614b905addf4b82c44a58b544c`.

PR #208 replaced the abridged, unpublished PR #207. The Arabic concepts body was preserved byte for byte. Its English edition has 42 paragraphs, 11 H2, 7 H3, 14 reference groups and no added table; 41 external link occurrences retain their exact sequence and block positions. Site, Governance, Citation, Content Research, Visual and a fresh PR Policy passed. Pages succeeded; the target AR/EN pages, English hub/home, both feeds, sitemap and robots returned HTTP 200. English feed = 49 and sitemap = 144 after that release.

The remaining AI-soul edition on this branch has 44 paragraphs, 9 H2, 2 H3, 6 reference groups and no table. Its 25 external link occurrences and per-block numbers match Arabic. The original religious/scientific distinctions, hypothetical healthcare example, research limits and uncompleted specialist-review status are retained. Its CI, manual screenshots and production deployment are still pending at the time this checkpoint was written; consult the PR and Actions for subsequent state.

The branch inventory is 50 Arabic article directories, 50 English, 5 German, 51 original research/guide records and 145 sitemap URLs. Directory equality is coverage, not proof that every older English article is a faithful translation.

## Historical review queue

The full automated pass covers 50 EN article directories. Four legacy layouts are unassessed. Among the 46 parsed pairs, 21 have different element counts. The stricter source/block/numeric comparison flags 38 pairs in total; 17 of those have matching element counts and may include notation differences. These are review flags, not 38 proven defective translations. Eight pass the mechanical checks; semantic fidelity for historical editions still requires a complete bilingual reading.

Prioritize large paragraph deficits and missing blockquotes/tables. Do not modify Arabic bodies. Read each flagged AR and EN edition fully, establish whether the difference is content loss, addition, changed caveat, reference grouping or harmless notation, then repair one article per PR. Keep original URLs, source order, numbers and publication dates. Preserve the existing design.

| Article | AR/EN paragraphs | AR/EN H2 | AR/EN reference/list items |
|---|---:|---:|---:|
| adam-all-languages-origin-language | 35/36 | 13/14 | 16/16 |
| age-of-universe-13-8-billion-years | 31/32 | 12/13 | 17/17 |
| civilization-knowledge-justice-collapse | 61/45 | 17/17 | 18/19 |
| difference-light-nur-quran-sun-moon | 41/25 | 13/14 | 8/19 |
| dna-code-genetic-information | 36/36 | 15/16 | 20/21 |
| human-embryo-quran-stages | 55/23 | 17/18 | 26/19 |
| injustice-fall-of-states-quran-history | 34/35 | 13/14 | 18/18 |
| jinn-demons-quran-bible-torah | 50/33 | 14/15 | 18/18 |
| madain-salih-thamud-nabataean-tombs | 39/35 | 15/15 | 9/12 |
| marib-dam-sayl-al-arim | 35/36 | 15/15 | 24/24 |
| mesopotamia-irrigation-soil-salinity-collapse | 55/27 | 11/11 | 10/13 |
| nile-ancient-egypt-flood-calendar-state | 39/30 | 14/14 | 16/16 |
| quran-day-thousand-fifty-thousand-years-relativity | 44/33 | 14/14 | 7/9 |
| quran-science-method-evidence | 63/30 | 16/16 | 40/29 |
| ratq-fatq-big-bang | 43/34 | 14/15 | 9/24 |
| river-civilizations-water-state | 35/36 | 12/13 | 10/10 |
| six-days-creation-cosmic-time | 38/35 | 11/11 | 9/13 |
| teaching-names-ai-understanding | 49/61 | 23/28 | 47/50 |
| universe-expansion-wa-inna-lamusiun | 36/36 | 13/14 | 23/23 |
| water-life-molecular-properties | 45/29 | 13/13 | 15/17 |
| writing-changed-human-history | 45/46 | 17/19 | 20/20 |

Legacy layouts: fall-of-baghdad-1258-ibn-al-alqami, how-certainty-becomes-violence, juhayman-grand-mosque-1979, water-civilization-power.

Use `python tools/translation_parity_audit.py --slug SLUG --base BASE_SHA` for each corrected article, then the repository's technical checks, Red Team, screenshots at 1440/390/360, Draft PR, six gates and fresh expected-head merge guard. The user explicitly authorized continued work and publication in the 13 October handoff. Do not merge obsolete PR #169: the universe-age page is already published. Do not claim Google indexing, traffic gains or specialist review from these checks.

## Search choices and boundaries

Only two Arabic article slugs lacked English at the actual main inspected; the old 17-English handoff was stale. Concept formation is distinct from the origin of all languages and AI understanding. The soul/obligation article is distinct from the Turing Test and neuroscience articles: its central question is religious obligation and accountable human decisions. Resolve the existing concepts PR first, then publish the last missing edition.

Concept title: “How Do Concepts Form? From Names to Scientific Models” (53 characters). Primary: “how do concepts form”; variants: concept formation, infant categorization, concept vs scientific model, does a concept need a word.

AI title: “Does AI Have a Soul? Consciousness and Responsibility” (53 characters). Primary: “does AI have a soul”; variants: AI soul Islam, soul vs consciousness, AI moral responsibility, religious obligation/taklif. The alternative “Does AI Have a Soul or Religious Obligation?” is faithful but less familiar as a search phrase; “Can AI Be Conscious?” would collide with the Turing article. These are qualitative choices, with no fabricated volume or difficulty metrics.

Current multi-query retrieval used primary research, Stanford, NASA, Royal Society of Chemistry, arXiv, NIST and the existing tafsir sources. Some PubMed fetches hit a verification wall; that is not evidence of a dead source. The Arabic article's discussion of Butlin 2023 explicitly limits the conclusion to examined systems, not every 2026 system. No new 2025/2026 paper was inserted into the translation. All source sequences remain those of Arabic.
