# SEO Operations Ledger — Ahmed Alhafiz

Purpose: shared execution memory for recurring SEO / AI discoverability tasks.

This file is operational only. It is not an independent public source for bibliographic or popularity claims.

## Required workflow for every recurring task
1. Read `.github/SEO_SOURCE_OF_TRUTH.md`.
2. Read this ledger.
3. Check whether the proposed action/opportunity was already executed, rejected, superseded, or is still awaiting measurement.
4. Execute only one new highest-impact action when justified.
5. Verify the result after execution.
6. Append a concise ledger entry containing date, task, book, target/query/opportunity, action, URL/file, verification, status, and next step.
7. Never overwrite prior history; append or explicitly mark an older entry as superseded.

## Status vocabulary
- `EXECUTED_VERIFIED` — implemented and checked.
- `EXECUTED_AWAITING_MEASUREMENT` — implemented, technically checked, awaiting search/traffic evidence.
- `READY_USER_ACTION` — complete packet prepared; one user action/permission required.
- `MONITOR` — no change yet; a specific condition is being watched.
- `REJECTED` — deliberately not pursued; include reason.
- `SUPERSEDED` — replaced by a later action.

---

## Entries

### 2026-08-29 — Shared operating baseline
- Task: orchestration / all SEO tasks
- Book: all; priority = أم عباس + سيروا في الأرض
- Action: verified current repository baseline before creating shared memory.
- Verified facts:
  - `/about/` exists.
  - separate `/books/` pages exist.
  - Arabic, English and German page sets are present in `sitemap.xml`.
  - `robots.txt` allows `OAI-SearchBot`, `GPTBot`, and generic crawlers.
  - Search Console verification file exists in repository.
- Status: `EXECUTED_VERIFIED`
- Next: all recurring tasks must use the shared source-of-truth and this ledger before selecting actions.

### 2026-08-29 — Priority strategy reset
- Task: orchestration / automations
- Book: أم عباس + قل سيروا في الأرض فانظروا كيف بدأ الخلق
- Action: recurring strategy was changed from author-first/general SEO to book-first recommendation/discoverability.
- Workstreams now separated into:
  1. recommendation-intent acquisition;
  2. ChatGPT/AI discoverability and technical SEO;
  3. bibliographic/book-entity strengthening;
  4. independent recommendation-source acquisition;
  5. Search Console measurement.
- Status: `EXECUTED_VERIFIED`
- Next: avoid recreating generic author-first work unless priority-book opportunities are exhausted.

### 2026-08-29 — Sirou recommendation-intent page strengthening
- Task: recommendation-intent engine
- Book: قل سيروا في الأرض فانظروا كيف بدأ الخلق
- Target: relevant non-branded recommendation/search intent around Arabic books on religion and science.
- Action: repository commit `c7ca1cd20a1d06a5181296609af6a9445ca2be89` strengthened the Arabic page title/description/semantic copy and added reader-fit/question sections.
- File: `books/sirou-fi-alard/index.html`
- Verification: commit changed only that file; current page contains sections including «لمن يناسب كتاب سيروا في الأرض؟» and «ما الأسئلة التي يدور حولها الكتاب؟».
- Status: `EXECUTED_AWAITING_MEASUREMENT`
- Next: do not immediately rewrite the same page again without either a clear technical defect, new independent evidence, or sufficient Search Console measurement.

### 2026-08-29 — Shared source of truth created
- Task: orchestration
- Book: all
- Action: created `.github/SEO_SOURCE_OF_TRUTH.md` with public-safe identity, current site baseline, priority order, book records, execution rules, measurement hierarchy and Search Console limitation.
- Verification: file creation commit recorded by GitHub.
- Status: `EXECUTED_VERIFIED`
- Next: update recurring task prompts so they explicitly read both shared files before acting and append verified actions to this ledger.

### 2026-08-29 — Shared-memory orchestration linked to all five SEO tasks
- Task: orchestration / all SEO tasks
- Book: all; operational priority = أم عباس + قل سيروا في الأرض فانظروا كيف بدأ الخلق
- Action: updated all five active SEO task prompts so each must read `.github/SEO_SOURCE_OF_TRUTH.md` and `.github/SEO_OPERATIONS_LEDGER.md` before selecting an action; avoid executed/rejected/awaiting-measurement work; refetch the newest ledger and SHA before appending; preserve history; retry one merge on write conflict; and keep private/unannounced publication data out of the public repository.
- Verification: post-update automation inspection confirmed the five intended SEO tasks are enabled and contain the shared-memory rule. A concurrent task run occurred during setup, but repository history showed no competing commit after creation of the ledger before this entry was written.
- Status: `EXECUTED_VERIFIED`
- Next: allow the coordinated tasks to operate; evaluate new ledger entries and real search/traffic measurements rather than repeatedly redesigning the orchestration without evidence.

### 2026-08-29 — Automated Search Console → Gmail measurement relay prepared
- Task: Search Console measurement infrastructure
- Book: all; measurement priority = أم عباس + سيروا في الأرض
- Action: created `tools/gsc-relay/Code.gs`, `tools/gsc-relay/appsscript.json`, and `tools/gsc-relay/README.md`. The relay uses the official Search Console API with read-only scope, detects the newest finalized date, compares the latest finalized 7 days with the prior 7 days, and emails a private machine-readable report with subject prefix `[GSC-AUTO]` to the effective Google account. Updated the recurring Search Console measurement task so Gmail relay reports are its preferred real-data source before requesting any manual export.
- Verification: Gmail connector is active and a targeted search for `[GSC-AUTO]` completed successfully; no report exists yet because the Apps Script has not been authorized/run. Automation prompt update succeeded. Search Console data itself is not stored in this public repository.
- Status: `READY_USER_ACTION`
- Next: create/authorize the Apps Script once using the prepared files and run `setupGscRelay`; after the first `[GSC-AUTO] Ahmed Alhafiz ...` email arrives, verify the full Gmail → automation data path and then mark this relay `EXECUTED_VERIFIED`.

### 2026-08-29 — Umm Abbas recommendation-intent page strengthening
- Task: recommendation-intent engine
- Book: أم عباس لجلب الحبيب ورد المطلقة
- Target: non-branded recommendation/search intent around «روايات رعب نفسي عربية».
- Action: commit `2cec3d9ec8f79952045e88b293a5567ec07c59cb` updated the Arabic book page title/meta/Book schema and added reader-fit and horror-type sections without creating a competing article.
- URL/file: https://ahmed-alhafiz.github.io/books/umm-abbas/ — `books/umm-abbas/index.html`
- Verification: repository refetch confirmed canonical/hreflang remain intact and the page now includes «لمن تناسب رواية أم عباس؟» and «ما نوع الرعب في الرواية؟» with natural Arabic psychological-horror relevance.
- Status: `EXECUTED_AWAITING_MEASUREMENT`
- Next: do not rewrite this page again until Search Console/search evidence, a technical defect, or new independent evidence justifies another change.

### 2026-08-29 — ArabLit forthcoming-book coverage opportunity for Umm Abbas
- Task: independent recommendation-source acquisition
- Book: أم عباس لجلب الحبيب ورد المطلقة
- Target/opportunity: ArabLit / ArabLit Quarterly — legitimate editorial suggestion for forthcoming-book coverage, with later review potential after publication.
- Action: prepared a complete one-to-one outreach packet for `info@arablit.org`; no email sent automatically.
- URL: https://arablit.org/news/ ; related review surface: https://arablit.org/reviews/
- Verification: ArabLit states that it covers forthcoming publications and accepts suggestions for news coverage by email; its reviews page also accepts book suggestions by email. Existing site coverage demonstrates sustained attention to Arabic horror, djinn/supernatural literature, and Arabic-language authors. The book's public page currently identifies it as a forthcoming Arabic psychological-horror novel centered on fear, belief, doubt, interpretation, and family tension.
- Status: `READY_USER_ACTION`
- Next: user sends the prepared single email to `info@arablit.org`; if ArabLit responds, update this entry with the outcome and do not pitch the same opportunity again meanwhile.

### 2026-08-29 — Priority-book sitemap freshness correction
- Task: ChatGPT/AI discoverability and technical SEO
- Book: أم عباس لجلب الحبيب ورد المطلقة + قل سيروا في الأرض فانظروا كيف بدأ الخلق
- Target/problem: `sitemap.xml` still advertised `lastmod=2026-08-28` for both Arabic priority-book URLs after their substantive page updates on 2026-08-29.
- Action: updated only those two sitemap `lastmod` values to `2026-08-29`; no other URLs or language variants were changed.
- URL/file: `sitemap.xml` — https://ahmed-alhafiz.github.io/sitemap.xml
- Verification: repository refetch after commit `7d0d07f3133ef3fd30e0ad5b85f22c6044d781c7` confirmed both Arabic priority URLs now carry `2026-08-29` and the rest of the sitemap is preserved. `robots.txt` remains permissive for `OAI-SearchBot` and points to this sitemap.
- Status: `EXECUTED_VERIFIED`
- Next: do not touch these timestamps again unless the corresponding pages receive a real content change; monitor indexing/measurement instead.

### 2026-08-29 — Umm Abbas publisher-page bibliographic opportunity
- Task: bibliographic / book-entity strengthening
- Book: أم عباس لجلب الحبيب ورد المطلقة
- Target/gap: a public Facebook search surface associated with Dar Ghorab exposes the exact forthcoming title and credits أحمد الحافظ, while Dar Ghorab's official website has no dedicated book record for the title.
- Action: prepared a publisher-page request packet; do not treat the Facebook mentions surface as sufficient proof that Dar Ghorab is the confirmed publisher, and do not add publisher/ISBN data to the author site until the publisher confirms it publicly.
- URLs: https://www.facebook.com/darghorab/mentions/ ; https://www.ghorabpublishing.com/ ; official book page https://ahmed-alhafiz.github.io/books/umm-abbas/
- Verification: exact-title web search surfaced «قريبًا أم عباس لجلب الحبيب وردّ المطلّقة … تأليف: أحمد الحافظ» on the Dar Ghorab Facebook mentions surface; the official Dar Ghorab site was opened and inspected and currently lists other releases but no dedicated Umm Abbas page. Google Books, Goodreads, WorldCat and major-bookstore targeted searches returned no stable record for the title.
- Status: `READY_USER_ACTION`
- Next: user asks Dar Ghorab, through its official communication channel, to confirm whether the title is theirs and, if yes, publish a dedicated forthcoming-book page containing the exact title, author name, cover, forthcoming status and official author-book URL; ISBN/year/edition only after those fields are formally assigned and public.

### 2026-08-29 — Sirou canonical-title normalization on author page
- Task: ChatGPT/AI discoverability and technical SEO
- Book: قل سيروا في الأرض فانظروا كيف بدأ الخلق
- Target/problem: `/about/` linked to the priority book using only the short form «سيروا في الأرض», while the canonical public title on the book page is «قل سيروا في الأرض فانظروا كيف بدأ الخلق».
- Action: changed only the Sirou book card on the Arabic author page so its visible H3 and cover alt use the full canonical title; preserved the destination URL and all other author-page metadata/links. Refreshed `/about/` `lastmod` in `sitemap.xml` to `2026-08-29` as part of the same content change.
- URL/file: https://ahmed-alhafiz.github.io/about/ — `about/index.html`; `sitemap.xml`
- Verification: repository refetch confirmed the full canonical title is present in both the H3 and image alt, canonical/hreflang/schema on `/about/` remain intact, and sitemap now reports `2026-08-29` for `/about/`. Site commit `20c784eead367ff32e1ff488795bd8f993a4a129`; sitemap commit `d2820d04fdbc4b4ce1c7a79bb497e34b21ba6c3d`.
- Status: `EXECUTED_VERIFIED`
- Next: do not repeat this author-page fix. In a later run, independently assess whether the homepage's short-form Sirou card creates enough remaining entity-name inconsistency to justify normalization.

### 2026-08-29 — Goodreads catalog-addition packet for Umm Abbas
- Task: recommendation-intent / independent book-entity acquisition
- Book: أم عباس لجلب الحبيب ورد المطلقة
- Target/opportunity: Goodreads catalog record for the forthcoming Arabic novel, enabling an independent book entity that can be discovered, shelved and later reviewed.
- Action: prepared a complete Goodreads Librarians request using only public verified fields: exact Arabic title, author أحمد الحافظ / Ahmed Alhafiz, Arabic language, forthcoming status, official description, official book URL and public cover URL. No ISBN, publisher, exact publication date, page count or format is supplied because those fields are not yet independently confirmed.
- URL: https://www.goodreads.com/group/show/220-goodreads-librarians-group ; official evidence page: https://ahmed-alhafiz.github.io/books/umm-abbas/ ; cover: https://ahmed-alhafiz.github.io/umm-abbas-cover.webp
- Verification: Goodreads states that its Librarians Group is the official channel for requesting new-book additions; its current librarian guidance allows confirmed forthcoming books with partial information, while rumored/unconfirmed works are excluded. Targeted Goodreads searches on 2026-08-29 found no stable record for the exact title.
- Status: `READY_USER_ACTION`
- Next: user joins the Goodreads Librarians Group and posts the prepared request once; do not create duplicate requests while it is pending.

### 2026-08-29 — New Books Network pitch opportunity for Sirou
- Task: independent recommendation-source acquisition
- Book: قل سيروا في الأرض فانظروا كيف بدأ الخلق
- Target/opportunity: New Books Network — official “Pitch a Book” intake with relevant Islamic Studies / Religion and Science channels; hosts independently choose which books they cover.
- Action: prepared a complete one-book pitch packet for the official form; no submission made automatically.
- URL: https://newbooksnetwork.com/authors ; official book page: https://ahmed-alhafiz.github.io/books/sirou-fi-alard/
- Verification: New Books Network’s live pitch page explicitly invites authors to pitch their books and states that hosts see submissions and independently select books for coverage. Its current topic taxonomy includes Islamic Studies, Religion, Science, Biology and Evolution, History of Science, and Physics and Chemistry, making the book’s public religion-and-science focus directly relevant. The public book record identifies the title as forthcoming and describes its focus as beginning of creation, religion and science, revelation and reason, and limits of interpretation and knowledge. No publisher, ISBN, exact publication date, sales, ranking, or endorsement is asserted.
- Status: `READY_USER_ACTION`
- Next: user submits the single official NBN pitch form once, choosing Islamic Studies as the primary channel if available and leaving ISBN/publisher blank unless the form requires verified values; do not invent those fields or submit duplicate pitches while pending.

### 2026-08-29 — Goodreads catalog-addition packet for Sirou
- Task: bibliographic / book-entity strengthening
- Book: قل سيروا في الأرض فانظروا كيف بدأ الخلق
- Target/opportunity: create the first stable Goodreads catalog entity for the forthcoming Arabic book.
- Action: prepared a Goodreads Librarians request packet using only publicly verified fields: exact Arabic title, author أحمد الحافظ / Ahmed Alhafiz, Arabic language, forthcoming status, official description, official book URL, and public cover URL. Publisher, ISBN, exact publication date, page count, edition, and format are intentionally omitted because they are not publicly verified.
- URL/file: https://www.goodreads.com/group/show/220-goodreads-librarians-group ; evidence: https://ahmed-alhafiz.github.io/books/sirou-fi-alard/ ; cover: https://ahmed-alhafiz.github.io/sirou-fi-alard-cover.webp
- Verification: targeted Goodreads/Google Books/WorldCat searches on 2026-08-29 found no stable record for the exact title. Current Goodreads librarian guidance states that confirmed forthcoming books with partial information may be valid catalog records when supported by a verifiable non-bookseller source; rumored/unconfirmed releases should not be added.
- Status: `READY_USER_ACTION`
- Next: user joins the Goodreads Librarians Group and posts one request using the prepared packet; do not submit duplicates while pending, and later add ISBN/publisher/date only after those fields are formally public and verifiable.

### 2026-08-29 — The Markaz Review editorial-review opportunity for Umm Abbas
- Task: independent recommendation-source acquisition
- Book: أم عباس لجلب الحبيب ورد المطلقة
- Target/opportunity: The Markaz Review — independent literary review/feature consideration through its explicit book-publicist/author intake handled by Executive Editor Rana Asfour.
- Action: prepared a one-to-one outreach packet for review consideration; no email sent because TMR explicitly asks book publicists, authors and publishers to send a press release together with an electronic ARC, and no ARC attachment is available in the current execution context.
- URL: https://themarkaz.org/submissions/ ; official book page: https://ahmed-alhafiz.github.io/books/umm-abbas/
- Verification: TMR states that it publishes book reviews, profiles and interviews year-round; its submission FAQ explicitly directs book publicists, authors and publishers to Executive Editor Rana Asfour for review assignments with a press release and electronic ARC. TMR's mission and current editorial scope center SWANA literature, and it maintains an active book-review section and book club. The book's public record identifies it as a forthcoming Arabic psychological-horror novel focused on fear, belief, doubt, interpretation and family tension. No request for favorable coverage is made.
- Status: `READY_USER_ACTION`
- Next: send one email to Rana Asfour at `rana@themarkaz.org` with a short press note plus the electronic ARC; do not pitch the same book to TMR again while the request is pending.

### 2026-08-29 — Sirou canonical-title normalization on English book page
- Task: ChatGPT/AI discoverability and technical SEO
- Book: قل سيروا في الأرض فانظروا كيف بدأ الخلق
- Target/problem: the English hreflang page still identified the shared Book entity and visible Arabic H1 with the shortened Arabic title «سيروا في الأرض», creating entity-name inconsistency against the canonical Arabic page and author page.
- Action: normalized the English page’s `Book.name`, visible H1, cover alt, and first identifying sentence to the full Arabic canonical title while preserving the English subtitle, self-canonical, hreflang cluster, author link, and existing descriptive metadata. Refreshed only this English URL’s sitemap `lastmod` to `2026-08-29` as part of the same change.
- URL/file: https://ahmed-alhafiz.github.io/en/books/sirou-fi-alard/ — `en/books/sirou-fi-alard/index.html`; `sitemap.xml`
- Verification: repository refetch confirmed the full title «قل سيروا في الأرض فانظروا كيف بدأ الخلق» in the structured Book entity, H1, image alt and lead sentence; canonical and hreflang remain intact. Site commit `960b2df4e58d2c89b5453ceb51133ea540e5db3e`; sitemap commit `6d233c871eb1ad05423e68b336c4057175f75f32`.
- Status: `EXECUTED_VERIFIED`
- Next: do not repeat this English-page normalization. Independently inspect the German hreflang page and homepage only if a distinct remaining canonical-title inconsistency is still present.

### 2026-08-29 — StoryGraph catalog-addition opportunity for Umm Abbas
- Task: recommendation-intent / independent book-entity acquisition
- Book: أم عباس لجلب الحبيب ورد المطلقة
- Target/opportunity: The StoryGraph missing-book catalog record for the forthcoming Arabic psychological-horror novel.
- Action: prepared a complete manual-add packet using only public verified fields: exact Arabic title, author أحمد الحافظ / Ahmed Alhafiz, Arabic language, forthcoming status, official description, official book URL, and cover URL; ISBN, publisher, exact publication date, page count, and format remain omitted until publicly verified.
- URL/file: https://app.thestorygraph.com/books/new ; evidence: https://ahmed-alhafiz.github.io/books/umm-abbas/ ; cover: https://ahmed-alhafiz.github.io/umm-abbas-cover.webp
- Verification: StoryGraph's official support documentation states that users can manually add books missing from its database and may leave unavailable fields blank; targeted StoryGraph searches on 2026-08-29 returned no stable result for the exact title or author/title combination.
- Status: `READY_USER_ACTION`
- Next: user signs in to StoryGraph and submits the book once using the prepared packet; do not create a duplicate while pending or after the record appears.

### 2026-08-29 — Sirou canonical-title normalization on German book page
- Task: ChatGPT/AI discoverability and technical SEO
- Book: قل سيروا في الأرض فانظروا كيف بدأ الخلق
- Target/problem: the German hreflang page still identified the shared Book entity and visible Arabic H1 with the shortened title «سيروا في الأرض», after the Arabic and English pages had already been normalized to the canonical full title.
- Action: normalized the German page’s `Book.name`, visible H1, cover alt, and lead identifying sentence to «قل سيروا في الأرض فانظروا كيف بدأ الخلق», while preserving the German display subtitle, self-canonical, hreflang cluster, author link, and existing German metadata. Refreshed only the German Sirou URL’s sitemap `lastmod` to `2026-08-29` as part of the same fix.
- URL/file: https://ahmed-alhafiz.github.io/de/books/sirou-fi-alard/ — `de/books/sirou-fi-alard/index.html`; `sitemap.xml`
- Verification: repository refetch confirmed the full canonical Arabic title in `Book.name`, H1, image alt, and the first identifying sentence; canonical/hreflang remained intact. Site commit `934b1845969586084383af8079284f0c73579b0b`; sitemap commit `8df05e4796ec8fbe2fa4a878f353d680cb807cde`. `robots.txt` still explicitly allows `OAI-SearchBot` and points to the sitemap.
- Status: `EXECUTED_VERIFIED`
- Next: do not repeat this German-page normalization; inspect the homepage only if a distinct remaining canonical-title inconsistency is still present.

### 2026-08-29 — Google Books Partner Center entity opportunity for Umm Abbas
- Task: recommendation-intent / bibliographic entity strengthening
- Book: أم عباس لجلب الحبيب ورد المطلقة
- Target/opportunity: create an official Google Books / Google Play Books catalog entity for the forthcoming Arabic psychological-horror novel, without inventing an ISBN.
- Action: prepared a one-book Partner Center packet using only public verified fields. Google officially permits adding a book without ISBN and assigns a Google-specific `GGKEY`; metadata should include exact title, Arabic language, author, description, and a relevant genre. No publisher, ISBN, exact release date, page count, price, or availability claim should be entered unless independently confirmed and rights permit submission.
- URL/file: https://play.google.com/books/publish/ ; official book page: https://ahmed-alhafiz.github.io/books/umm-abbas/ ; cover: https://ahmed-alhafiz.github.io/umm-abbas-cover.webp
- Verification: Google Play Books Partner Center documentation current on 2026-08-29 states that an ISBN is not required, that Google assigns a `GGKEY` to books without one, and that metadata completeness improves discoverability. Google also supports Google Books preview availability separately from sale/pre-order settings.
- Status: `READY_USER_ACTION`
- Next: user signs in to Google Play Books Partner Center, adds one book, chooses the no-ISBN / Google book ID option, and enters only verified public metadata; upload/preview or sale settings only if the user currently holds the necessary distribution/preview rights. Do not create duplicate entries if an ISBN-backed publisher record later appears; reconcile identifiers instead.

### 2026-08-29 — Science and Religion Forum review opportunity for Sirou
- Task: independent recommendation-source acquisition
- Book: قل سيروا في الأرض فانظروا كيف بدأ الخلق
- Target/opportunity: Science and Religion Forum — `Reviews in Science and Religion`, a specialist journal that explicitly invites appropriate books to be brought to the editor’s attention for review.
- Action: prepared a one-book editorial enquiry packet for the official contact form; no submission made automatically because the journal asks enquiries to use its contact form in the first instance.
- URL: https://www.srforum.org/reviews-in-science-and-religion ; contact: https://www.srforum.org/contact ; official book page: https://ahmed-alhafiz.github.io/books/sirou-fi-alard/
- Verification: the journal states that it publishes recent reviews of books in the science-and-religion field and that members, colleagues and students may bring appropriate books to the editor’s attention; editor listed as Maureen Simpson. SRF’s current scope is explicitly open to all religions, and its 2026 programming addresses boundaries between scientific understanding and religious interpretation and welcomes non-Christian perspectives. The book is publicly described as forthcoming, Arabic-language, and focused on beginning of creation, religion and science, revelation and reason, and limits of interpretation and knowledge. The journal does not state an Arabic-language review policy, so the enquiry discloses the book’s Arabic language and asks whether it is eligible rather than assuming acceptance.
- Status: `READY_USER_ACTION`
- Next: submit the prepared single enquiry through the SRF contact form, asking whether the forthcoming Arabic book can be considered for `Reviews in Science and Religion`; if they confirm eligibility, provide the review copy/ARC in the format they request and do not submit a duplicate enquiry while pending.

### 2026-08-29 — Qantara.de Arabic-literature editorial opportunity for Umm Abbas
- Task: independent recommendation-source acquisition
- Book: أم عباس لجلب الحبيب ورد المطلقة
- Target/opportunity: Qantara.de — editorial book tip to the Arabic culture/literature desk for possible independent review, interview, or cultural coverage.
- Action: prepared a one-to-one editorial pitch addressed to Mohammed Magdy, the Arabic editor listed on Qantara's current contact page; no email sent automatically.
- URL: https://qantara.de/en/page/about-us-contact ; Arabic literature surface: https://qantara.de/thema/arabische-literatur ; official book page: https://ahmed-alhafiz.github.io/books/umm-abbas/
- Verification: Qantara's current contact page lists Mohammed Magdy as Arabic editor and provides a direct editorial email. The site actively maintains an Arabic-literature topic surface and has published book reviews and author interviews, including 2025 coverage of Saïd Khatibi's novel and 2026 literary coverage. Qantara does not state that unsolicited books are automatically accepted, so the outreach is framed only as an editorial tip for independent consideration. The book's public page identifies it as a forthcoming Arabic psychological-horror novel centered on fear, belief, doubt, interpretation and family tension; no publisher, ISBN, sales, ranking, or endorsement claim is made.
- Status: `READY_USER_ACTION`
- Next: send one concise editorial-tip email to Mohammed Magdy at the address listed on Qantara's official contact page; do not request favorable coverage and do not re-pitch Qantara while the enquiry is pending.

### 2026-08-29 — Google Books Partner Center entity opportunity for Sirou
- Task: recommendation-intent / bibliographic entity strengthening
- Book: قل سيروا في الأرض فانظروا كيف بدأ الخلق
- Target/opportunity: create a distinct Google Books / Google Play Books entity so the book is separable from high-authority Quran verse and tafsir results that currently dominate exact-title searches.
- Action: prepared a one-book Partner Center packet using only public verified fields: exact Arabic title, author أحمد الحافظ — Ahmed Alhafiz, Arabic language, public description, official book URL and cover. ISBN, publisher, exact publication date, price, page count and availability remain omitted unless publicly verified. Google permits books without ISBN and assigns a `GGKEY`.
- URL/file: https://play.google.com/books/publish/ ; official book page: https://ahmed-alhafiz.github.io/books/sirou-fi-alard/ ; cover: https://ahmed-alhafiz.github.io/sirou-fi-alard-cover.webp
- Verification: targeted Google Books searches on 2026-08-29 found no stable record for the exact title/author combination. General exact-title search is dominated by Quran/tafsir pages for Al-Ankabut 29:20. Current Google Partner Center documentation states that a book can be added without ISBN via “Get a Google book ID (GGKEY)” and that richer metadata improves discoverability.
- Status: `READY_USER_ACTION`
- Next: user signs in to Google Play Books Partner Center and adds this single book once, using the exact title and only verified metadata; choose the no-ISBN / Google book ID option. Enable preview/sale settings only if the user holds the necessary rights, and do not create a duplicate if an ISBN-backed publisher record later appears.

### 2026-08-29 — The Arab Daily News book-review request opportunity for Umm Abbas
- Task: independent recommendation-source acquisition
- Book: أم عباس لجلب الحبيب ورد المطلقة
- Target/opportunity: The Arab Daily News — explicit book-review / book-release intake handled by Ray Hanania, with an active Book Review category and 2026 book coverage.
- Action: prepared a one-to-one plain-text book-review request / release packet; no email sent automatically.
- URL: https://thearabdailynews.com/book-reviews/ ; review surface: https://thearabdailynews.com/category/book-review/ ; official book page: https://ahmed-alhafiz.github.io/books/umm-abbas/
- Verification: the publication’s book-review page explicitly invites book review requests and book releases concerning Arab and Middle East-related books, directs submissions to Ray Hanania, requires press-release text in the email body, and says the ideal release is under 800 words. Its Book Review category remained active in 2026, including a June 2, 2026 forthcoming-book item. The proposed pitch identifies Umm Abbas only by its verified public facts: a forthcoming Arabic psychological-horror novel by Ahmed Alhafiz, focused on fear, belief, doubt, interpretation and family tension; it does not assert publisher, ISBN, sales, ranking, or endorsement.
- Status: `READY_USER_ACTION`
- Next: send one concise plain-text email to Ray Hanania using the address displayed on The Arab Daily News book-review page, asking for independent review/editorial consideration and linking to the official book page; do not request favorable coverage or send a duplicate while pending.

### 2026-08-29 — Umm Abbas English-page citation clarity
- Task: ChatGPT/AI discoverability and technical SEO
- Book: أم عباس لجلب الحبيب ورد المطلقة
- Target/problem: the English hreflang page’s lead sentence named the work and genre but did not identify the author or forthcoming status until later in the page, weakening single-sentence extraction for answer engines.
- Action: changed only the first visible identifying sentence to state that the work is a forthcoming psychological horror novel by Ahmed Alhafiz; preserved title/meta, self-canonical, hreflang cluster, Book schema, author links, and the rest of the copy. Refreshed only the English Umm Abbas URL’s sitemap `lastmod` to `2026-08-29` as part of the same content change.
- URL/file: https://ahmed-alhafiz.github.io/en/books/umm-abbas/ — `en/books/umm-abbas/index.html`; `sitemap.xml`
- Verification: repository refetch confirmed the revised lead sentence, unchanged canonical/hreflang/schema, and `sitemap.xml` now reports `2026-08-29` for the English Umm Abbas URL. Page commit `9b5aaffcb027b03c347fae8c4d9572a5fc27565c`; sitemap commit `0cbfc21d6af996114004346efb32d9e5bd57554d`. `robots.txt` continues to explicitly allow `OAI-SearchBot`.
- Status: `EXECUTED_VERIFIED`
- Next: do not repeat this English lead-sentence fix; independently inspect the German Umm Abbas hreflang page or homepage only if a distinct technical/entity defect remains.

### 2026-08-29 — Sirou canonical-title normalization on Arabic homepage
- Task: recommendation-intent / ChatGPT-AI discoverability
- Book: قل سيروا في الأرض فانظروا كيف بدأ الخلق
- Target/problem: the Arabic homepage still exposed the priority book under the short form «سيروا في الأرض» in the book-card label/title/cover alt and overlay title, while the Arabic, English and German book pages and `/about/` had already been normalized to the full canonical title.
- Action: normalized the homepage Sirou card and overlay to the full canonical title «قل سيروا في الأرض فانظروا كيف بدأ الخلق» without changing the destination URL, descriptive blurb, page metadata, or other book cards.
- URL/file: https://ahmed-alhafiz.github.io/ — `index.html`
- Verification: repository refetch confirmed the full canonical title in the Sirou card `aria-label`, cover alt, visible card title and overlay title. Commit `eee35f7d1d2c7f13719f48f1600dfe3e5518b050`.
- Status: `EXECUTED_VERIFIED`
- Next: do not repeat homepage title normalization; prioritize independent catalog/editorial evidence or real Search Console measurement before further copy changes.

### 2026-08-29 — Al-Abhath review inquiry for Sirou
- Task: independent recommendation-source acquisition
- Book: قل سيروا في الأرض فانظروا كيف بدأ الخلق
- Target/opportunity: Al-Abhath (American University of Beirut / Brill) — independent book-review consideration in a refereed Arab and Middle Eastern studies journal with Arabic-language review capability.
- Action: sent one individual editorial inquiry to `alabhath@aub.edu.lb` asking whether the forthcoming Arabic book is eligible for review consideration and whether an author-supplied electronic or print review copy is acceptable; the message explicitly did not request favorable coverage and did not claim a publisher, ISBN, or fixed publication date.
- URL: https://www.aub.edu.lb/alabhath/Pages/instructions.aspx ; journal: https://www.aub.edu.lb/alabhath/Pages/default.aspx ; current volume: https://www.aub.edu.lb/alabhath/Pages/volume-73.aspx ; official book page: https://ahmed-alhafiz.github.io/books/sirou-fi-alard/
- Verification: AUB identifies Al-Abhath as a refereed annual journal publishing reviews in Arab and Middle Eastern studies and accepting Arabic-language work; its current editorial board lists dedicated Book Review Editors. Its instructions explicitly provide a books-for-review route, while stating that publishers normally send review copies, so the outreach correctly asks about author eligibility before sending a copy. Volume 73 (2025) contains active book reviews in Arabic/Islamic studies. Gmail confirmed the one-to-one inquiry was sent successfully.
- Status: `EXECUTED_VERIFIED`
- Next: wait for Al-Abhath's response; if they confirm eligibility, provide the requested review copy in their preferred format. Do not re-pitch Al-Abhath while this inquiry is pending.

### 2026-08-29 — ESSSAT / ISSR review inquiry for Sirou
- Task: independent recommendation-source acquisition
- Book: قل سيروا في الأرض فانظروا كيف بدأ الخلق
- Target/opportunity: `Reviews in Science, Religion and Theology`, the quarterly joint publication of ESSSAT and ISSR, for independent book-review consideration.
- Action: sent one individual email to editor Dr Edward DeLaquil at `esdelaquil@gmail.com`, explicitly identifying the book as forthcoming and Arabic-language and asking whether it is eligible for review consideration before offering a review copy. No favorable review, endorsement, publisher, ISBN, fixed publication date, ranking, or sales claim was requested or asserted.
- URL: https://www.esssat.net/esssat-news-reviews ; contact evidence: https://esssatconference.org/contact-us/ ; official book page: https://ahmed-alhafiz.github.io/books/sirou-fi-alard/
- Verification: ESSSAT states that the quarterly publication includes book reviews and welcomes notification of books suitable for review; current instructions cover science-and-theology, philosophical/epistemological, cosmological, evolutionary/biological and related fields. ESSSAT's contact page identifies Edward DeLaquil as editor for the journal, and current journal material lists the same editor/contact. Gmail confirmed the one-to-one inquiry was sent successfully.
- Status: `EXECUTED_VERIFIED`
- Next: wait for the editor's response; if Arabic-language/forthcoming books are eligible, provide the requested review copy or metadata in the format requested. Do not re-pitch ESSSAT/ISSR while pending.

### 2026-08-29 — Qantara.de editorial tip sent for Umm Abbas
- Task: independent recommendation-source acquisition
- Book: أم عباس لجلب الحبيب ورد المطلقة
- Target/opportunity: Qantara.de Arabic editorial desk — independent review/interview/cultural-coverage consideration.
- Action: sent one concise Arabic editorial-tip email to Mohammed Magdy at `kassem@qantara.de`, using only public verified facts and linking to the official book page; no favorable coverage, publisher, ISBN, sales, ranking, or endorsement was requested or claimed.
- URL/file: https://qantara.de/en/page/about-us-contact ; https://ahmed-alhafiz.github.io/books/umm-abbas/
- Verification: Qantara's current contact page lists Mohammed Magdy as Arabic editor and `kassem@qantara.de`; Gmail search confirmed the message in Sent with message ID `1a04c603f6c20a59` and no attachment.
- Status: `EXECUTED_VERIFIED`
- Next: wait for Qantara's response; do not re-pitch the same book while this enquiry is pending.

### 2026-08-29 — AJIS review inquiry for Sirou
- Task: independent recommendation-source acquisition
- Book: قل سيروا في الأرض فانظروا كيف بدأ الخلق
- Target/opportunity: American Journal of Islam and Society (AJIS) — independent book-review consideration in an active interdisciplinary journal covering Islam, philosophy/metaphysics, and related intellectual fields.
- Action: sent one individual editorial inquiry to `ajis@iiit.org`, explicitly identifying the book as forthcoming and Arabic-language and asking whether it is eligible for AJIS book-review consideration and whether an author-supplied review copy is acceptable. No favorable review, endorsement, publisher, ISBN, fixed publication date, ranking, or sales claim was requested or asserted.
- URL: https://www.ajis.org/index.php/ajiss/about/submissions ; editorial team: https://www.ajis.org/index.php/ajiss/about/editorialTeam ; official book page: https://ahmed-alhafiz.github.io/books/sirou-fi-alard/
- Verification: AJIS's current submission guidance states that it publishes book reviews and review essays; its scope includes scholarly research on Islam, philosophy and metaphysics, and its current editorial team lists Dr Younus Mirza as Book Review Editor. A current 2026 issue confirms the journal remains active. Gmail confirmed the one-to-one inquiry was sent successfully with message ID `1a04c89920946665`.
- Status: `EXECUTED_VERIFIED`
- Next: wait for AJIS's response; if the forthcoming Arabic book is eligible, provide the requested review copy or metadata in the format requested. Do not re-pitch AJIS while pending.

### 2026-08-29 — Homepage sitemap freshness correction
- Task: ChatGPT/AI discoverability and technical SEO
- Book: قل سيروا في الأرض فانظروا كيف بدأ الخلق (homepage entity path)
- Target/problem: the Arabic homepage had been materially updated on 2026-08-29 to normalize the book’s canonical title, but `sitemap.xml` still reported the homepage as `lastmod=2026-08-28`.
- Action: changed only the homepage `lastmod` in `sitemap.xml` to `2026-08-29`; no other URL timestamp or content was changed.
- URL/file: https://ahmed-alhafiz.github.io/ — `sitemap.xml`
- Verification: repository refetch after commit `f87f44f84a3132dde51e01393091b4901556f0ab` confirmed the homepage now carries `lastmod=2026-08-29`; priority-book URLs remain unchanged at `2026-08-29`, and `robots.txt` still explicitly allows `OAI-SearchBot` and references the sitemap.
- Status: `EXECUTED_VERIFIED`
- Next: do not change homepage `lastmod` again unless the homepage receives another real content change; prioritize a distinct technical defect or new evidence in later runs.

### 2026-08-29 — Open Library catalog-addition opportunity for Umm Abbas
- Task: bibliographic / book-entity strengthening
- Book: أم عباس لجلب الحبيب ورد المطلقة
- Target/opportunity: create a discoverable Open Library work/edition record as an additional independent bibliographic surface; targeted Open Library searches found no matching title/author record.
- Action: prepared a minimal public-data packet only. Use the exact Arabic title, primary author name «أحمد الحافظ», alternate searchable author name `Ahmed Alhafiz`, Arabic language, official description, official book URL, and verified cover. Leave publisher, ISBN, publication date, edition, pages and format blank until publicly verified.
- URL/file: https://openlibrary.org/books/add ; evidence: https://ahmed-alhafiz.github.io/books/umm-abbas/ ; cover: https://ahmed-alhafiz.github.io/umm-abbas-cover.webp
- Verification: Open Library’s current editing FAQ states that a book can be added with little or extensive information, recommends the native-script author name as primary with transliterations/alternate spellings added as searchable alternate names, and allows records without ISBN. The catalog also contains future-dated book records, confirming that a forthcoming work is not inherently excluded. No publisher/ISBN/date claim is inferred.
- Status: `READY_USER_ACTION`
- Next: user signs in to Open Library and creates the book once with only the verified fields above; after the author record exists, ensure `Ahmed Alhafiz` is added as an alternate name. Do not create a duplicate when later publisher/ISBN metadata becomes public; update the same work/edition instead.

### 2026-08-29 — Umm Abbas German-page citation clarity
- Task: ChatGPT/AI discoverability and technical SEO
- Book: أم عباس لجلب الحبيب ورد المطلقة
- Target/problem: the German hreflang page’s first identifying sentence described the work and genre but did not bind the canonical Arabic title, author, and forthcoming status into one extractable sentence.
- Action: revised only the first visible paragraph so it states the canonical Arabic title, German display title, that the work is an in-preparation psychological horror novel, and that it is by Ahmed Alhafiz; preserved title/meta, self-canonical, hreflang cluster, Book schema, author links, and the rest of the page. Refreshed only the German Umm Abbas URL’s sitemap `lastmod` to `2026-08-29` as part of the same content change.
- URL/file: https://ahmed-alhafiz.github.io/de/books/umm-abbas/ — `de/books/umm-abbas/index.html`; `sitemap.xml`
- Verification: repository refetch confirmed the revised lead sentence, unchanged canonical/hreflang/schema, and `sitemap.xml` now reports `2026-08-29` for the German Umm Abbas URL. Page commit `52dd836f7491e641681955327c9bbcb8e6066a88`; sitemap commit `f366265a7c3f0edf8fd93319a2d5a8c04f97bbd9`. `robots.txt` continues to explicitly allow `OAI-SearchBot`.
- Status: `EXECUTED_VERIFIED`
- Next: do not repeat this German lead-sentence fix; prioritize a distinct technical defect, independent evidence, or measurement in later runs.

### 2026-08-29 — The New Arab Book Club editorial inquiry for Umm Abbas
- Task: independent recommendation-source acquisition
- Book: أم عباس لجلب الحبيب ورد المطلقة
- Target/opportunity: The New Arab — active Book Club / features coverage for Arab-authored books, including reviews, interviews, annual/new-books lists and literary features.
- Action: sent one individual editorial inquiry to `editorial-english@newarab.com`, identifying the book only by its verified public facts as a forthcoming Arabic psychological-horror novel and asking whether it is eligible for independent Book Club review/interview/forthcoming-books coverage. No favorable review, publisher, ISBN, fixed publication date, ranking, sales, or endorsement was requested or asserted.
- URL: https://www.newarab.com/features ; contact: https://www.newarab.com/contact ; editorial team: https://www.newarab.com/editorialteam ; official book page: https://ahmed-alhafiz.github.io/books/umm-abbas/
- Verification: The New Arab's live Features page shows an active Book Club in August 2026; current editorial pages identify Sheeffah Shiraz as Features Editor and provide `editorial-english@newarab.com`. The publication has a recurring Book Club surface with reviews and curated reading lists, including a February 18, 2026 Ramadan list and a December 17, 2025 '26 must-read new books for 2026' list. Gmail confirmed the one-to-one inquiry was sent successfully with message ID `1a04cce359e1b517`.
- Status: `EXECUTED_VERIFIED`
- Next: wait for The New Arab's response; if Arabic-language forthcoming titles are eligible, provide the requested reading copy or metadata in the format requested. Do not re-pitch The New Arab while this inquiry is pending.

### 2026-08-29 — Al-Shajarah review inquiry for Sirou
- Task: independent recommendation-source acquisition
- Book: قل سيروا في الأرض فانظروا كيف بدأ الخلق
- Target/opportunity: Al-Shajarah (ISTAC-IIUM) — independent book-review consideration in a refereed journal whose stated scope includes Islamic thought, Islamic civilization, and Islamic science.
- Action: sent one individual editorial inquiry to `alshajarah@iium.edu.my`, explicitly identifying the book as forthcoming and Arabic-language and asking whether it is eligible for independent review consideration and whether an author-supplied review copy is acceptable. No favorable review, endorsement, publisher, ISBN, fixed publication date, ranking, or sales claim was requested or asserted.
- URL: https://journals.iium.edu.my/shajarah/ ; official book page: https://ahmed-alhafiz.github.io/books/sirou-fi-alard/
- Verification: current Al-Shajarah material identifies the journal as a refereed publication covering Islamic thought, Islamic civilization, and Islamic science, lists a Book Review Editor, and provides `alshajarah@iium.edu.my` for publication enquiries; recent 2026 material confirms the journal remains active. Gmail confirmed the one-to-one inquiry was sent successfully with message ID `1a04cfc1eb192202`.
- Status: `EXECUTED_VERIFIED`
- Next: wait for Al-Shajarah's response; if Arabic-language forthcoming books are eligible, provide the requested review copy or metadata in the format requested. Do not re-pitch Al-Shajarah while pending.