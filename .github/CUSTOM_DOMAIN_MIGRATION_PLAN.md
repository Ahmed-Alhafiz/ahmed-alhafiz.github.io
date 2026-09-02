# Custom Domain Migration Plan

**Status:** prepared; not activated  
**Prepared:** 2026-09-02  
**Current canonical origin:** `https://ahmed-alhafiz.github.io`  
**Blocking dependency:** the user must choose and purchase a domain before DNS or canonical migration can be executed.

## 1. Recommended naming order

Availability must be verified at the moment of purchase; this document does not claim that any candidate is currently available.

1. `ahmedalhafiz.com` — strongest match to the preferred Latin author name.
2. `ahmed-alhafiz.com` — clear fallback that preserves the exact spelling with a separator.
3. `ahmadalhafiz.com` — secondary transliteration only if the preferred spelling cannot be acquired.

Do not acquire multiple domains merely to create duplicate sites. At most, secondary domains should redirect to one canonical origin.

## 2. Canonical form

Preferred public form after purchase:

- `https://www.DOMAIN/` as the configured GitHub Pages custom domain;
- `https://DOMAIN/` configured at DNS and redirected automatically to the `www` form;
- one HTTPS origin only;
- no parallel duplicate indexable copy.

GitHub documents `www` as the most stable custom-domain form because it uses a CNAME and is not tied directly to GitHub Pages server IP changes. GitHub also recommends configuring the apex variant and verifying the domain before attaching it.

## 3. Required order of operations

The order is security-critical.

1. Purchase the selected domain through the user’s registrar account.
2. Add and verify the domain in the user’s GitHub account before publishing DNS records.
3. In repository **Settings → Pages**, add `www.DOMAIN` as the custom domain.
4. At the DNS provider, add:
   - `CNAME` — host `www` — value `Ahmed-Alhafiz.github.io`.
   - Apex `A` records — host `@`:
     - `185.199.108.153`
     - `185.199.109.153`
     - `185.199.110.153`
     - `185.199.111.153`
   - Optional but recommended apex `AAAA` records:
     - `2606:50c0:8000::153`
     - `2606:50c0:8001::153`
     - `2606:50c0:8002::153`
     - `2606:50c0:8003::153`
5. Do not create wildcard DNS records such as `*.DOMAIN`.
6. Verify DNS with `dig` or the registrar’s DNS inspection tool.
7. Wait for GitHub Pages to issue the certificate, then enable **Enforce HTTPS**.
8. Confirm redirects:
   - apex → `www`;
   - HTTP → HTTPS;
   - old `github.io` URLs → the corresponding custom-domain paths.
9. Only after live HTTPS and redirects are verified, run the repository-wide canonical migration.
10. Submit the new sitemap in a new Search Console domain property and monitor both old and new properties during the transition.

## 4. Repository migration batch

The canonical migration must be one controlled release, not a series of manual edits. The release will update:

- every `<link rel="canonical">`;
- all `hreflang` and `x-default` URLs;
- Open Graph and Twitter image/URL metadata;
- every JSON-LD `@id`, `url`, `contentUrl`, and internal entity reference;
- `author.json` and the canonical author identifier;
- `sitemap.xml`;
- Atom and JSON feeds;
- `robots.txt` sitemap declaration;
- citation files and machine-readable evidence records;
- IndexNow host and key location;
- repository documentation and integrity tests.

The path structure must remain unchanged. Only the origin changes.

## 5. Pre-migration acceptance checks

Do not switch canonical URLs until all conditions are true:

- selected domain is owned by the user;
- GitHub domain verification is complete;
- DNS resolves correctly from multiple resolvers;
- both apex and `www` are controlled;
- no wildcard record exists;
- GitHub Pages recognises the domain;
- HTTPS certificate is active;
- a complete repository backup or rollback tag exists;
- the migration script produces no path changes;
- all structural, editorial, discovery, entity, UX, and visual tests pass on the candidate branch.

## 6. Post-migration acceptance checks

Verify at least:

- home, author, research hub, all pillar dossiers, evidence appendices, and book pages return `200` on the new origin;
- the old GitHub Pages URLs redirect to matching new paths rather than only to the homepage;
- no mixed-content request remains;
- one canonical URL exists per public page;
- every canonical uses the new HTTPS origin;
- all `hreflang` counterparts are reciprocal;
- the new sitemap contains only the new origin;
- feeds and `author.json` use the new origin;
- OAI-SearchBot, GPTBot, and generic crawlers remain allowed according to the selected policy;
- IndexNow key validation succeeds for the new host;
- Search Console sees the sitemap and no unexpected duplicate-canonical spike appears.

## 7. Rollback plan

If the new domain produces certificate, DNS, redirect, or widespread canonical failure:

1. Revert the canonical-migration pull request.
2. Restore the previous Pages custom-domain setting or remove it.
3. Restore `ahmed-alhafiz.github.io` as the canonical origin in all machine outputs.
4. Keep DNS records only if the domain remains securely verified; otherwise remove GitHub Pages records immediately to reduce takeover risk.
5. Confirm the old origin returns `200` for all critical routes.
6. Resubmit the restored sitemap and preserve the incident record.

Rollback must preserve paths and content. It must not delete indexed pages.

## 8. Search and ranking boundary

A custom domain provides a cleaner permanent author identity and reduces dependence on a platform hostname. It does not guarantee first position, a knowledge panel, or AI citation. The effect must be measured at 7, 30, and 90 days under `.github/MEASUREMENT_PROTOCOL.md`.

## 9. Sources used for this plan

- GitHub Docs — About custom domains and GitHub Pages: `https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages`
- GitHub Docs — Managing a custom domain: `https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site`
- GitHub Docs — Verifying a custom domain: `https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages`
