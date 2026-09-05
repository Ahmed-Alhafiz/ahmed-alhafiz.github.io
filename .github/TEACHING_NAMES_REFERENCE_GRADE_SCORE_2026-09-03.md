# Teaching Names reference-grade score — final release record

**Scope:** Arabic and English public editions of `teaching-names-ai-understanding` on `content-depth-rebuild-14`.

**Finalized:** 2026-09-05.

**Status:** repository release gate passed; external specialist review remains pending and is not represented as peer review.

## Governing judgment

The dossier clears the numerical 85/100 reference-pillar threshold and the former bilingual-parity veto gate is now closed. The Arabic and English editions declare reciprocal `hreflang="ar"` / `hreflang="en"`, share one valid `x-default`, and expose visible AR/EN switching. `tools/discovery_integrity.py` explicitly enforces this two-way contract for every dossier declared bilingual, so the earlier omission can no longer pass silently.

The remaining external-review limitation is editorial, not a repository release blocker. It must remain visible and must not be described as peer review.

## Evidence snapshot

Verified release-hardening head before this record refresh: `e4ed40f04bd34d3a9c108171eb3a5e6887a2d334`.

All four current workflows completed successfully on that same head:

- Site Integrity: success.
- Content Research Architecture: success.
- Citation Metadata Integrity: success.
- Visual Review: success.

Additional verified state:

- Arabic and English Teaching the Names editions both satisfy the current depth/evidence/transparency/linking gates.
- Reciprocal bilingual discovery is validated mechanically, including visible switching and `x-default` agreement.
- Arabic/English feeds, research index, sitemap and related-book links are covered by discovery integrity.
- Machine-readable claim and reference artefacts exist, including claims JSON, BibTeX, RIS and CFF.
- The forthcoming manuscript is treated as question origin/thematic relation rather than empirical or exegetical evidence.
- Public-presentation hygiene remains part of the release gates.
- External specialist review: not completed.

## 100-point rubric

| Axis | Score | Maximum | Reason |
|---|---:|---:|---|
| Specific question + direct answer | 11 | 12 | The central question is explicit and the direct answer is extractable. Minor room remains to tighten search-intent wording into one canonical question sentence shared by both editions. |
| Qur’anic / exegetical rigor | 13 | 15 | 2:30–33 is treated as a unit; Tabari, Qurtubi, Razi, Ibn Ashur and Abu Hayyan are differentiated; the Tabari correction is preserved; modern synthesis is separated from tafsir. External specialist review remains absent. |
| Scientific / technical rigor | 15 | 18 | Training objective, decodability, causal use, generalization, grounding and agency are separated; primary papers and methodological counterweights are present. Some frontier evidence remains preprint-level and is kept out of the central conclusion. |
| Original contribution | 13 | 15 | The Name–World–Responsibility Matrix and adversarial protocol are reusable named contributions and are explicitly presented as an unvalidated analytical framework rather than a validated scale. |
| Objections + counterevidence | 8 | 10 | Strong objections are represented, including behavioural criteria, language-only learning, internal representations and multimodal grounding. More direct negative/failure evidence could still deepen causal-grounding sections. |
| Limits + uncertainty | 8 | 8 | Limits are explicit; consciousness is separated from the six layers; no unsupported categorical consciousness claim is made; Qur’anic framing is not used as empirical machine evidence. |
| Evidence ledger + portable citation | 9 | 10 | Claims JSON, BibTeX, RIS and CFF are present and mirror/integrity checks exist. A dedicated human-readable bilingual evidence appendix could still improve inspectability. |
| Editorial construction + clarity | 6 | 7 | Both editions are long-form, structured, objection-aware and source-rich. Parity is judged by claim coverage rather than raw word count. |
| Bilingual parity + discovery + linking | 5 | 5 | Reciprocal AR/EN hreflang, shared x-default, visible switching, feeds, hubs, sitemap and related-book links are now validated. |
| **Total** | **88** | **100** | Numerical threshold passed and no repository veto gate remains open. |

## Veto-gate audit

### Religious rigor

**PASS, with review limitation disclosed.** No false consensus, no identification of Teaching the Names with machine learning, and no conversion of modern synthesis into a classical exegetical claim.

### Scientific rigor

**PASS.** The dossier distinguishes objective, representation, causal use, generalization, grounding, intention and consciousness, and does not infer consciousness from fluent behaviour or internal representation.

### Evidence independence

**PASS.** The unpublished book is not used as scientific, philosophical or exegetical evidence.

### Inspectability / bilingual parity

**PASS.** Both language editions now expose reciprocal metadata and visible language switching, and the dedicated discovery validator enforces the pair mechanically.

## Release decision

**Repository release gate: PASS.** This record supersedes the earlier provisional 86/100 blocked state. The final score is **88/100** after closing the bilingual parity/discovery veto gate. Merge is permitted only after this record-refresh commit itself completes all required CI workflows successfully on one identical head SHA.
