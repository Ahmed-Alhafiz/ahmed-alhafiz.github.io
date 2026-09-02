# Post-release Integrity 08

**Prepared:** 2026-09-02  
**Status:** `BRANCH_VERIFIED_AWAITING_PR_AND_LIVE_DEPLOYMENT`

## Defect found

The Arabic and English feeds contained timestamps later than the real public deployment and later than the current local time. The Arabic feed also omitted the psychological-horror guide although the research hub and structured `ItemList` correctly declared seven Arabic research surfaces.

## Correction

- Verified deployment completion used as release/update time: `2026-09-02T04:33:19+02:00`.
- Arabic Atom and JSON feeds aligned to seven research surfaces.
- English flagship feed timestamp aligned to the verified deployment.
- Earlier Arabic publication dates preserved; global-rebuild modifications use the verified deployment time.
- Permanent CI expanded to reject future feed timestamps, feed/hub divergence, missing book-to-study links and missing study-to-book return links.

## Verification required before final status

1. The branch workflow must complete and self-remove its temporary files.
2. `Site integrity` and `Visual review` must succeed on the final pull-request head.
3. The pull request must merge to `main`.
4. GitHub Pages deployment must succeed.
5. Live Atom/JSON feeds, the Arabic research hub and both relevant book pages must be fetched and checked.

After those steps, replace this status with `EXECUTED_VERIFIED` and record the merge and deployment identifiers.
