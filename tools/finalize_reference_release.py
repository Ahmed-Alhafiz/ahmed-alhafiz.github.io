#!/usr/bin/env python3
"""Append the verified 2026-09-01 release entry to the immutable SEO ledger."""
from pathlib import Path

ledger = Path('.github/SEO_OPERATIONS_LEDGER.md')
text = ledger.read_text(encoding='utf-8')
key = '2026-09-01 — First reference-content release: Sirou + Umm Abbas'

entry = r'''

### 2026-09-01 — First reference-content release: Sirou + Umm Abbas
- Task: reference-content engine / author entity / AI discoverability / technical quality
- Books: «قل سيروا في الأرض فانظروا كيف بدأ الخلق» + «أم عباس لجلب الحبيب ورد المطلقة»
- Source handling: both manuscripts were read completely for private editorial mapping. Plot-sensitive and unpublished bibliographic material remained private; the public site continues to state that both works are forthcoming / `قيد الإصدار`.
- Strategic comparison: adapted the useful structural principles of leading evidence-led/reference publishers—topic hub, explicit methodology, stable citations, visible author identity, source hierarchy, and strong internal navigation—without copying their text or branding.
- Public actions:
  1. created `/articles/` as the article/research hub;
  2. published `/articles/ratq-fatq-big-bang/` as a sourced Sirou-linked reference study;
  3. published `/articles/sleep-paralysis-jathoom/` as a sourced Umm-Abbas-linked medical/cultural report;
  4. rebuilt `/guides/arabic-psychological-horror/` as a substantive analytical guide;
  5. published `/methodology/` and `/articles/feed.xml`;
  6. strengthened `/about/`, the two active book pages, homepage discovery, article-to-author links, article-to-book links, canonicals, Article/Person/Breadcrumb JSON-LD, and `sitemap.xml`;
  7. corrected homepage book-card access by adding a visible full-book-page action inside the modal;
  8. installed `tools/site_audit.py` and the persistent `site-integrity.yml` workflow;
  9. resolved all remaining metadata/image-dimension audit warnings and removed one-time release artifacts.
- Main release commit: `9eb154299a57bd5f11cabbf7dc33e3b9d8da8ebf`.
- Homepage discovery commit: `a1d28d2b588ec66ff4a679f232bc7f283f468fed`.
- Quality cleanup commit: `6571b2c`.
- Verification:
  - reviewed content-bundle workflow run `33547770288`: success;
  - homepage patch workflow run `33548607934`: success;
  - quality cleanup workflow run `33548970012`: success;
  - final repository audit after quality cleanup: 23 HTML pages, 23 canonicals, 23 sitemap URLs, 0 errors, 0 warnings;
  - GitHub Pages deployment run `33548624517` after homepage integration: success.
- Measurement baseline before release (finalized 2026-08-23 to 2026-08-29): homepage 15 clicks / 54 impressions / 27.78% CTR / average position 3.98; `/about/` 2 clicks / 15 impressions / 13.33% CTR / average position 4.73.
- Status: `EXECUTED_AWAITING_MEASUREMENT`
- Next: do not repeatedly rewrite the new pages. Continue the next deep reference articles while evaluating finalized 14, 28, and 56-day Search Console windows; expand clusters according to evidence and entity value.
'''

if key not in text:
    ledger.write_text((text.rstrip() + entry).rstrip() + '\n', encoding='utf-8')
    print('Release entry appended to SEO operations ledger.')
else:
    print('Release entry already present; no duplicate appended.')

Path('.github/finalize-release.marker').unlink(missing_ok=True)
Path(__file__).unlink(missing_ok=True)
