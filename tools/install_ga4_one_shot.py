#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEASUREMENT_ID = "G-TYFF6MTK0Y"
ASSET_REL = "assets/analytics-ga4-28.js"
SCRIPT_TAG = '<script defer src="/assets/analytics-ga4-28.js"></script>'
EXCLUDED = {"404.html"}

ASSET = r'''(() => {
  'use strict';

  const measurementId = 'G-TYFF6MTK0Y';
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };

  // Analytics only: no Google Signals and no ad-personalization signals.
  window.gtag('js', new Date());
  window.gtag('config', measurementId, {
    send_page_view: true,
    allow_google_signals: false,
    allow_ad_personalization_signals: false
  });

  const loader = document.createElement('script');
  loader.async = true;
  loader.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(measurementId);
  document.head.appendChild(loader);
})();
'''


def public_html() -> list[Path]:
    return sorted(
        p for p in ROOT.rglob("*.html")
        if ".git" not in p.parts
        and p.relative_to(ROOT).as_posix() not in EXCLUDED
        and not p.name.startswith("google")
    )


def install_page_tags() -> int:
    pages = public_html()
    changed = 0
    for path in pages:
        source = path.read_text(encoding="utf-8")
        count = source.count(SCRIPT_TAG)
        if count == 1:
            continue
        if count > 1:
            raise SystemExit(f"{path.relative_to(ROOT)}: duplicate GA4 loader tag")
        if source.count("</head>") != 1:
            raise SystemExit(f"{path.relative_to(ROOT)}: expected exactly one </head>")
        source = source.replace("</head>", f"{SCRIPT_TAG}\n</head>", 1)
        path.write_text(source, encoding="utf-8")
        changed += 1
    if not pages:
        raise SystemExit("No public HTML pages found")
    return changed


def install_asset() -> None:
    path = ROOT / ASSET_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(ASSET, encoding="utf-8")


def patch_site_audit() -> bool:
    path = ROOT / "tools/site_audit.py"
    source = path.read_text(encoding="utf-8")
    if "GA4 measurement integrity" in source:
        return False
    anchor = "    robots=(root/'robots.txt').read_text(encoding='utf-8') if (root/'robots.txt').exists() else ''\n"
    if anchor not in source:
        raise SystemExit("site_audit.py: GA4 insertion anchor not found")
    block = f'''    # GA4 measurement integrity: one centralized loader on every public page.\n    ga4_id={MEASUREMENT_ID!r}\n    ga4_asset='assets/analytics-ga4-28.js'\n    ga4_tag={SCRIPT_TAG!r}\n    ga4_path=root/ga4_asset\n    if not ga4_path.exists():\n        errors.append(f'{{ga4_asset}}: missing centralized GA4 loader')\n    else:\n        ga4_source=ga4_path.read_text(encoding='utf-8')\n        if ga4_source.count(ga4_id)!=1:errors.append(f'{{ga4_asset}}: expected exactly one measurement ID {{ga4_id}}')\n        for marker in ('allow_google_signals: false','allow_ad_personalization_signals: false','send_page_view: true'):\n            if marker not in ga4_source:errors.append(f'{{ga4_asset}}: privacy/measurement marker missing: {{marker}}')\n    for p in htmls:\n        page_source=p.read_text(encoding='utf-8')\n        count=page_source.count(ga4_tag)\n        if count!=1:errors.append(f'{{p.relative_to(root)}}: expected one centralized GA4 loader tag, found {{count}}')\n        if ga4_id in page_source:errors.append(f'{{p.relative_to(root)}}: GA4 measurement ID must stay centralized in {{ga4_asset}}')\n\n'''
    source = source.replace(anchor, block + anchor, 1)
    path.write_text(source, encoding="utf-8")
    return True


def verify() -> None:
    pages = public_html()
    asset = (ROOT / ASSET_REL).read_text(encoding="utf-8")
    if asset.count(MEASUREMENT_ID) != 1:
        raise SystemExit("GA4 asset measurement ID count is not exactly one")
    bad = []
    for path in pages:
        source = path.read_text(encoding="utf-8")
        if source.count(SCRIPT_TAG) != 1 or MEASUREMENT_ID in source:
            bad.append(path.relative_to(ROOT).as_posix())
    if bad:
        raise SystemExit("GA4 verification failed: " + ", ".join(bad))
    print(f"GA4 verification passed: {len(pages)} public pages")


def main() -> None:
    install_asset()
    changed = install_page_tags()
    audit_changed = patch_site_audit()
    verify()
    print(f"pages_changed={changed}; audit_changed={audit_changed}; measurement_id={MEASUREMENT_ID}")


if __name__ == "__main__":
    main()
