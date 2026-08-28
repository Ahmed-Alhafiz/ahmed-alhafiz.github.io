# Google Search Console → Gmail relay

Purpose: provide the recurring SEO measurement task with real, finalized Search Console data without storing private performance data in this public repository.

## What it does
- Queries the official Search Console API using read-only scope.
- Detects the newest finalized Search Console date instead of guessing the normal reporting lag.
- Compares the latest 7 finalized days with the previous 7 finalized days.
- Collects query+page rows, priority-book rows, and page totals.
- Sends the result privately to the executing Google account with subject prefix `[GSC-AUTO]`.
- No Search Console performance data, OAuth token, password, or credential is committed to GitHub.

## One-time setup
1. Open `https://script.new` while signed in to the same Google account that owns or can read the Search Console property `https://ahmed-alhafiz.github.io/`.
2. Replace the default `Code.gs` with the contents of `Code.gs` in this folder.
3. In Apps Script **Project Settings**, enable showing the `appsscript.json` manifest file in the editor, then replace its contents with this folder's `appsscript.json`.
4. Save the project.
5. Run `setupGscRelay` once from the Apps Script editor.
6. Approve the requested Google permissions. The Search Console permission is read-only (`webmasters.readonly`).
7. The setup function immediately attempts one report and installs a daily trigger around 06:00 Europe/Vienna.
8. Confirm that Gmail receives a message whose subject begins with `[GSC-AUTO] Ahmed Alhafiz`.

## If Google returns API-not-enabled / access-not-configured
Enable **Google Search Console API** for the Google Cloud project associated with the Apps Script project, then run `setupGscRelay` again.

## Security / privacy
- Never paste OAuth tokens or Google credentials into this repository.
- The report is emailed to the effective Google account running the script.
- Search Console metrics remain in Gmail and are not written into this public repository.
- The script requests only read access to Search Console plus the minimum Apps Script scopes needed to call the API and send the private report.

## Report format
Email body contains a machine-readable JSON object between:

`GSC_AUTO_JSON_START`

and

`GSC_AUTO_JSON_END`

The recurring measurement task can read the newest matching Gmail message and analyze it without requiring a manual CSV upload each day.
