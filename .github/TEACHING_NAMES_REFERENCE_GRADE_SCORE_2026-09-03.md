# Teaching Names reference-grade score — 2026-09-03

**Scope:** Arabic and English public editions of `teaching-names-ai-understanding` on `content-depth-rebuild-14`.

**Status:** provisional score complete; release gate remains blocked until bilingual reciprocity is complete and final CI is green.

## Governing judgment

The dossier is now intellectually strong enough to score above the numerical 85/100 reference-pillar threshold, but it must **not** yet be labelled a completed reference pillar because the Arabic edition does not currently declare the English alternate in reciprocal `hreflang` or expose the matching EN switch. The reference-grade standard treats bilingual parity and inspectability as a veto gate, so a numerical pass cannot override that defect.

External specialist review is also still explicitly not completed. That does not by itself prevent author-led publication, but the review state must remain visible and must never be described as peer review.

## Evidence snapshot

Latest verified CI on commit `7ccade66c087e086b49cd167251d8728f4a957d5` is fully green:

- Site Integrity: success.
- Content Research Architecture: success.
- Visual Review: success.
- Arabic edition: 3,925 visible words; 28 external sources.
- English edition: 5,224 visible words; 30 external sources.
- Both editions pass the current depth/evidence/transparency/linking gate.
- Machine-readable claim and reference artefacts exist, including claims JSON, BibTeX, RIS and CFF.
- The forthcoming manuscript is treated as question origin/thematic relation rather than empirical or exegetical evidence.
- External specialist review: not completed.

The green CI confirms the current repository-level integrity gates, but it does **not** erase the manually verified asymmetry between the English and Arabic article headers. The generic multilingual validator only validates pages that already declare alternates; it does not prove that every logically paired bilingual page declares the full reciprocal set. That gap remains an explicit manual blocker rather than being hidden by a green build.

## 100-point rubric

| Axis | Score | Maximum | Reason |
|---|---:|---:|---|
| Specific question + direct answer | 11 | 12 | The central question is explicit and the direct answer is extractable. Minor room remains to tighten the search-intent formulations into a single canonical question sentence shared by both editions. |
| Qur’anic / exegetical rigor | 13 | 15 | 2:30–33 is treated as a unit; Tabari, Qurtubi, Razi, Ibn Ashur and Abu Hayyan are differentiated; the Tabari correction is preserved; modern synthesis is separated from tafsir. External specialist review remains absent. |
| Scientific / technical rigor | 15 | 18 | Training objective, decodability, causal use, generalization, grounding and agency are separated; primary papers and methodological counterweights are present. Some frontier evidence remains preprint-level and is correctly excluded from the central conclusion. |
| Original contribution | 13 | 15 | The Name–World–Responsibility Matrix and adversarial protocol are reusable, named contributions and are explicitly presented as an unvalidated analytical framework rather than a validated scale. |
| Objections + counterevidence | 8 | 10 | Strong objections are represented, including behavioural criteria, language-only learning, internal representations and multimodal grounding. Additional direct negative/failure evidence could still deepen the causal-grounding sections. |
| Limits + uncertainty | 8 | 8 | Limits are explicit; consciousness is separated from the six layers; no categorical unsupported consciousness claim is made; Qur’anic framing is not used as empirical machine evidence. |
| Evidence ledger + portable citation | 9 | 10 | Claims JSON, BibTeX, RIS and CFF are present and mirror checks exist. A human-readable evidence appendix dedicated to the final bilingual edition would improve inspectability further. |
| Editorial construction + clarity | 6 | 7 | Both editions are long-form, structured, objection-aware and source-rich. The English edition is substantially longer than the Arabic edition, so parity should be audited by claim coverage rather than word count alone. |
| Bilingual parity + discovery + linking | 3 | 5 | English-to-Arabic linkage is present and research index/feed/book links have been rebuilt. Arabic-to-English reciprocal `hreflang` and visible EN switch are still missing from the Arabic article and therefore block final release status. |
| **Total** | **86** | **100** | Numerical threshold met, but veto gate still blocks reference-pillar designation. |

## Veto-gate audit

### Religious rigor

**PASS, with review limitation disclosed.** No false consensus, no identification of Teaching the Names with machine learning, and no conversion of a modern synthesis into a classical exegetical claim.

### Scientific rigor

**PASS.** The dossier distinguishes objective, representation, causal use, generalization, grounding, intention and consciousness, and does not infer consciousness from fluent behaviour or internal representation.

### Evidence independence

**PASS.** The unpublished book is not used as scientific, philosophical or exegetical evidence.

### Inspectability / bilingual parity

**BLOCKED.** The English page declares Arabic, English and x-default alternates and exposes an AR/EN switch. The Arabic page currently declares only Arabic `hreflang` and has no matching visible language-switch block. Until that is corrected and tested reciprocally, the dossier is not release-complete under the governing standard.

## Required corrections before merge

1. Add reciprocal `hreflang="en"` and `x-default` to the Arabic article.
2. Add visible AR/EN switch links to the Arabic article matching the metadata alternates.
3. Add a dedicated reciprocity assertion so a logically bilingual dossier cannot pass merely because one side omits all alternate declarations.
4. Run the multilingual switcher validator and full Site Integrity workflow after the change.
5. Confirm Arabic and English feeds, research index, sitemap and related-book links all agree on canonical titles and URLs.
6. Re-run the evidence-mirror byte equality checks.
7. Confirm no production-process residue or internal markers leak into public files.
8. Update PR #20 description to reflect the actual rebuilt bilingual dossier before merge.

## Release decision

**Do not merge yet.** The dossier has a provisional **86/100** and all current CI workflows are green, but the manually verified bilingual reciprocity defect is a hard release blocker under the governing standard. The correct response is to fix the defect and strengthen the validator, not to treat the green build as evidence that the defect does not exist.
