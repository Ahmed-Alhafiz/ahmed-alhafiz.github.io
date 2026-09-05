# Ahrefs Remediation 24 — Reciprocal hreflang

Date: 2026-09-05
Base main: `9f34d13e923826c22fc6ba100804eb59e427f473`

## Proven Ahrefs finding

Ahrefs reported 5 URLs with `Missing reciprocal hreflang (no return-tag)`.

Repository and live diagnostics found no broken language target and no missing ordinary AR/EN/DE return tag. A group-consistency audit found exactly two multilingual groups with inconsistent `x-default` mappings:

1. About group: 3 URLs (`/about/`, `/en/about/`, `/de/about/`).
   - `/en/about/` used itself as `x-default`; the Arabic and German members used `/about/`.
2. Research-hub group: 2 URLs (`/articles/`, `/en/articles/`).
   - `/en/articles/` used itself as `x-default`; the Arabic member used `/articles/`.

Total affected group members: 5, matching the Ahrefs count exactly.

## Repair

- `/en/about/` now uses `/about/` as `x-default`.
- `/en/articles/` now uses `/articles/` as `x-default`.
- `tools/site_audit.py` now validates multilingual groups generically: self hreflang, canonical targets, identical member sets, and identical mappings including `x-default`.

## Schema finding

Ahrefs also reported 8 URLs with Schema.org validation errors. Multiple repository, live, Schema.org vocabulary, duplicate-property, domain, and strict-range diagnostics did not identify a proven current defect matching that exact 8-page count. No Schema markup was changed in this remediation to avoid speculative damage. Exact Ahrefs row-level issue details are required before any Schema change.

## Boundary

No CSS, layout, images, article prose, research claims, canonical URLs, or book metadata changed.
