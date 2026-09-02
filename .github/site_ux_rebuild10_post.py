#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

about = ROOT / "de/about/index.html"
text = about.read_text(encoding="utf-8")
old = '<div class="langs" aria-label="Sprachen"><a href="/" hreflang="ar">AR</a><a href="/en/" hreflang="en">EN</a><a href="/de/" hreflang="de" aria-current="page">DE</a></div>'
new = '<div class="langs" aria-label="Sprachen"><a href="/about/" hreflang="ar">AR</a><a href="/en/about/" hreflang="en">EN</a><a href="/de/about/" hreflang="de" aria-current="page">DE</a></div>'
if text.count(old) != 1:
    raise SystemExit(f"de/about language switch: expected one legacy block, found {text.count(old)}")
about.write_text(text.replace(old, new, 1), encoding="utf-8")

css = ROOT / "assets/site-v2.css"
styles = css.read_text(encoding="utf-8")
marker = "/* UX10 final mobile footer alignment */"
if marker in styles:
    raise SystemExit("UX10 post-CSS marker already exists")
styles = styles.rstrip() + f'''\n\n{marker}\n@media(max-width:620px){{.footer-meta{{flex-direction:column;align-items:flex-start;gap:2px;text-align:start}}}}\n'''
css.write_text(styles, encoding="utf-8")

updated = about.read_text(encoding="utf-8")
for token in ('href="/about/" hreflang="ar"', 'href="/en/about/" hreflang="en"', 'href="/de/about/" hreflang="de" aria-current="page"'):
    if token not in updated:
        raise SystemExit(f"de/about missing exact counterpart token: {token}")
print("Applied exact German profile counterparts and mobile footer alignment")
