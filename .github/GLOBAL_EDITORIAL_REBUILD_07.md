# Global Editorial Rebuild 07 — Design and Evidence Standard

Date: 2026-09-02  
Branch: `global-editorial-rebuild-07`

## Why this rebuild exists

The previous site was technically crawlable but visually resembled an author portfolio, while the article pages mostly relied on length, source lists and generic “reference” labels. Those traits are insufficient for global trust or citation. This release changes the unit of publication from a promotional article to an inspectable research dossier.

## Public criteria used

This is not a claim to know any proprietary ranking or citation algorithm. The implementation is based on observable criteria published or demonstrated by strong public references:

1. **Google Search guidance** — original analysis, substantial value, clear sourcing, authorship, purpose, and people-first usefulness; no special markup guarantees AI-feature inclusion.
   - https://developers.google.com/search/docs/fundamentals/creating-helpful-content
   - https://developers.google.com/search/docs/appearance/ai-features
2. **OpenAI publisher guidance** — permit `OAI-SearchBot`, keep accessible pages, and measure referrals carrying `utm_source=chatgpt.com`; permission enables discovery but does not guarantee citation.
   - https://help.openai.com/en/articles/12627856-publishers-and-developers-faq
3. **Our World in Data** — combine long-form explanation with topic architecture, definitions, visible data provenance, and reusable factual units.
   - https://ourworldindata.org/
4. **Stanford Encyclopedia of Philosophy** — qualified authorship, stable entries, explicit bibliography, revision discipline, and editorially selected external resources.
   - https://plato.stanford.edu/info.html
5. **Scientific mission and collaboration pages** — original papers, mission data, methods, uncertainty, and update history rather than detached summaries.

## Gaps closed in this release

| Previous weakness | Rebuild response |
|---|---|
| Dark portfolio aesthetic with little editorial hierarchy | Paper-and-ink editorial system, navy/copper identity, responsive research layouts, stronger typography and white space |
| Every long article described as “reference” | Explicit public types: extended dossier, evidence brief, medical-cultural brief, critical essay |
| Source lists without a claim map | C01–C08 public claim ledger, confidence labels, caveats, and machine-readable JSON |
| No substantive English research | Complete English edition of the flagship dossier and its evidence appendix |
| No visible external-review boundary | Review-status registry on every research surface; no peer-review implication |
| Books risked appearing as self-corroborating sources | `mentions` and thematic disclosure instead of `isBasedOn`; manuscripts carry no evidentiary role |
| Little original visual explanation | Bilingual five-layer evidence maps and bilingual discovery-to-citation pipeline diagrams |
| Only human-facing pages | Atom feeds, JSON feeds, research manifest, BibTeX, RIS, CFF, and claims JSON |
| Generic editorial policy | Public source hierarchy, entailment test, independence test, counter-source search, version and correction rules |
| No global release discipline | One complete English dossier first; no mass machine translation for page count |

## Citation-readiness model

A page becomes a plausible source candidate only after passing all of these gates:

1. Discoverable and indexable.
2. Relevant to the exact question.
3. Directly supports the claim at the stated specificity.
4. Has clear provenance, dates and authorship.
5. Presents extractable answer units: definitions, numbers, comparisons and procedures.
6. Exposes uncertainty, objections and revision status.
7. Is more useful than the sources it merely repeats through synthesis, framing, or original analysis.

Passing the gates does not guarantee ranking or citation. Citation selection is query- and system-dependent.

## Flagship dossier standard

The rebuilt ratq/fatq dossier must retain:

- direct answer before exposition;
- five-layer separation: text, exegesis, observation, model, inference;
- C01–C08 claim/evidence ledger;
- classical exegesis plurality;
- independent observational pillars of hot Big Bang cosmology;
- annotated references and source roles;
- objections and conditions that would change the conclusion;
- Arabic and English complete editions;
- public external-review status;
- machine-readable claims and citation files;
- thematic, non-evidentiary link to the forthcoming book.

## Safety and integrity

- No unpublished ISBN, publisher, sales, review or release-date claim.
- No manuscript chapter or plot disclosure beyond approved public themes.
- Medical pages remain educational, preserve emergency guidance, and prohibit treatment changes based on non-clinical advice.
- AI assistance is disclosed; AI output is not a factual source.
- No fake review, synthetic traffic, hidden content, link scheme or mass low-value translation.

## Release gate

The branch may merge only after:

1. repository-wide HTML, JSON-LD, XML and JSON parsing;
2. canonical/sitemap/internal-link validation;
3. bilingual hreflang validation;
4. forthcoming-book publication-safety scan;
5. article depth, source diversity and reciprocal-link checks;
6. medical safety checks;
7. desktop and mobile visual review;
8. GitHub Actions success;
9. post-deployment public URL verification.
