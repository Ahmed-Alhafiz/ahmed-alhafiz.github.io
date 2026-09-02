#!/usr/bin/env python3
"""Integrate dedicated social cards into the water dossier and its evidence pages."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://ahmed-alhafiz.github.io"
GENERIC = f"{BASE}/ahmed-alhafiz-social-card.png"
SCRIPT_RE = re.compile(
    r"(<script\b[^>]*\btype=[\"']application/ld\+json[\"'][^>]*>)(.*?)(</script>)",
    re.IGNORECASE | re.DOTALL,
)
OG_IMAGE_RE = re.compile(r'<meta property="og:image" content="[^"]+">')

PAGES = {
    "articles/water-civilization-power/index.html": {
        "image": f"{BASE}/assets/social/water-civilization-power-ar.png",
        "lang": "ar",
        "alt": "الماء والحضارة والسلطة — سلسلة الماء والسلطة والعدل — أحمد الحافظ",
        "x_default": f"{BASE}/articles/water-civilization-power/",
    },
    "articles/water-civilization-power/evidence/index.html": {
        "image": f"{BASE}/assets/social/water-civilization-power-ar.png",
        "lang": "ar",
        "alt": "ملحق ادعاءات وأدلة الماء والحضارة والسلطة — أحمد الحافظ",
        "x_default": f"{BASE}/articles/water-civilization-power/evidence/",
    },
    "en/articles/water-civilization-power/index.html": {
        "image": f"{BASE}/assets/social/water-civilization-power-en.png",
        "lang": "en",
        "alt": "Water, Civilization and Power — Water–Power–Justice Chain — Ahmed Alhafiz",
        "x_default": f"{BASE}/articles/water-civilization-power/",
    },
    "en/articles/water-civilization-power/evidence/index.html": {
        "image": f"{BASE}/assets/social/water-civilization-power-en.png",
        "lang": "en",
        "alt": "Claim and Evidence Appendix — Water, Civilization and Power — Ahmed Alhafiz",
        "x_default": f"{BASE}/articles/water-civilization-power/evidence/",
    },
}

AUDIT_BLOCK = r'''
    # Dedicated social cards for the bilingual water dossier.
    social_surfaces={
      'articles/water-civilization-power/index.html':('assets/social/water-civilization-power-ar.png',BASE+'/assets/social/water-civilization-power-ar.png'),
      'articles/water-civilization-power/evidence/index.html':('assets/social/water-civilization-power-ar.png',BASE+'/assets/social/water-civilization-power-ar.png'),
      'en/articles/water-civilization-power/index.html':('assets/social/water-civilization-power-en.png',BASE+'/assets/social/water-civilization-power-en.png'),
      'en/articles/water-civilization-power/evidence/index.html':('assets/social/water-civilization-power-en.png',BASE+'/assets/social/water-civilization-power-en.png'),
    }
    checked_cards=set()
    for page_rel,(card_rel,card_url) in social_surfaces.items():
        page_file=root/page_rel; source=page_file.read_text(encoding='utf-8') if page_file.exists() else ''
        if not source:errors.append(f'{page_rel}: missing social-card surface');continue
        image_id=(expected(root,page_file) or '')+'#image'
        required=(
          f'<meta property="og:image" content="{card_url}">',
          f'<meta property="og:image:secure_url" content="{card_url}">',
          '<meta property="og:image:type" content="image/png">',
          f'<meta name="twitter:image" content="{card_url}">',
          image_id,
        )
        for marker in required:
            if marker not in source:errors.append(f'{page_rel}: dedicated social marker missing: {marker}')
        if 'ahmed-alhafiz-social-card.png' in source:errors.append(f'{page_rel}: generic social card still used')
        if card_rel in checked_cards:continue
        checked_cards.add(card_rel); card=root/card_rel
        if not card.exists():errors.append(f'{card_rel}: dedicated social card missing');continue
        data=card.read_bytes()
        if len(data)<10_000:errors.append(f'{card_rel}: suspiciously small PNG ({len(data)} bytes)')
        if len(data)<24 or data[:8]!=b'\x89PNG\r\n\x1a\n' or data[12:16]!=b'IHDR':
            errors.append(f'{card_rel}: invalid PNG signature/IHDR');continue
        width,height=struct.unpack('>II',data[16:24])
        if (width,height)!=(1200,630):errors.append(f'{card_rel}: expected 1200x630, found {width}x{height}')
'''.strip("\n")


def transform_jsonld(raw: str, *, image_url: str, image_id: str, alt: str, lang: str) -> str:
    data = json.loads(raw)
    graph = data.get("@graph") if isinstance(data, dict) else None
    if not isinstance(graph, list):
        return json.dumps(data, ensure_ascii=False, indent=2)

    graph[:] = [node for node in graph if not (isinstance(node, dict) and node.get("@id") == image_id)]
    graph.append(
        {
            "@type": "ImageObject",
            "@id": image_id,
            "url": image_url,
            "contentUrl": image_url,
            "width": 1200,
            "height": 630,
            "caption": alt,
            "inLanguage": lang,
        }
    )
    for node in graph:
        if not isinstance(node, dict):
            continue
        node_type = node.get("@type")
        if node_type == "Article":
            node["image"] = {"@id": image_id}
        elif node_type == "WebPage":
            node["primaryImageOfPage"] = {"@id": image_id}
        elif node_type == "Dataset":
            node["thumbnailUrl"] = image_url
    return json.dumps(data, ensure_ascii=False, indent=2)


def update_page(path: Path, config: dict[str, str]) -> None:
    html = path.read_text(encoding="utf-8")
    image_url = config["image"]
    alt = config["alt"]
    lang = config["lang"]
    canonical_match = re.search(r'<link rel="canonical" href="([^"]+)">', html)
    if not canonical_match:
        raise RuntimeError(f"{path.relative_to(ROOT)}: canonical not found")
    image_id = canonical_match.group(1) + "#image"

    replacement = (
        f'<meta property="og:image" content="{image_url}">'
        f'<meta property="og:image:secure_url" content="{image_url}">'
        f'<meta property="og:image:type" content="image/png">'
        f'<meta property="og:image:alt" content="{alt}">'
    )
    html, count = OG_IMAGE_RE.subn(replacement, html, count=1)
    if count != 1:
        raise RuntimeError(f"{path.relative_to(ROOT)}: expected one og:image")

    card_marker = '<meta name="twitter:card" content="summary_large_image">'
    twitter = (
        card_marker
        + f'<meta name="twitter:image" content="{image_url}">'
        + f'<meta name="twitter:image:alt" content="{alt}">'
    )
    if '<meta name="twitter:image"' in html:
        html = re.sub(r'<meta name="twitter:image" content="[^"]+">', f'<meta name="twitter:image" content="{image_url}">', html, count=1)
        html = re.sub(r'<meta name="twitter:image:alt" content="[^"]+">', f'<meta name="twitter:image:alt" content="{alt}">', html, count=1)
    elif card_marker in html:
        html = html.replace(card_marker, twitter, 1)
    else:
        raise RuntimeError(f"{path.relative_to(ROOT)}: twitter card marker not found")

    html = re.sub(
        r'<link rel="alternate" hreflang="x-default" href="[^"]+">',
        f'<link rel="alternate" hreflang="x-default" href="{config["x_default"]}">',
        html,
        count=1,
    )

    def rewrite(match: re.Match[str]) -> str:
        rendered = transform_jsonld(
            match.group(2),
            image_url=image_url,
            image_id=image_id,
            alt=alt,
            lang=lang,
        )
        return f"{match.group(1)}\n{rendered}\n{match.group(3)}"

    html, script_count = SCRIPT_RE.subn(rewrite, html)
    if script_count < 1:
        raise RuntimeError(f"{path.relative_to(ROOT)}: no JSON-LD block found")

    if GENERIC in html:
        raise RuntimeError(f"{path.relative_to(ROOT)}: generic social card remained")
    for marker in (image_url, image_id, f'<meta name="twitter:image" content="{image_url}">'):
        if marker not in html:
            raise RuntimeError(f"{path.relative_to(ROOT)}: integration marker missing: {marker}")

    path.write_text(html, encoding="utf-8")
    print(f"social metadata integrated: {path.relative_to(ROOT)}")


def patch_audit() -> None:
    path = ROOT / "tools/site_audit.py"
    source = path.read_text(encoding="utf-8")
    if "Dedicated social cards for the bilingual water dossier" in source:
        return
    source = source.replace(
        "import argparse, json, re, sys, xml.etree.ElementTree as ET",
        "import argparse, json, re, struct, sys, xml.etree.ElementTree as ET",
        1,
    )
    marker = "    robots=(root/'robots.txt').read_text(encoding='utf-8') if (root/'robots.txt').exists() else ''"
    if source.count(marker) != 1:
        raise RuntimeError("site_audit.py insertion marker not found exactly once")
    source = source.replace(marker, AUDIT_BLOCK + "\n\n" + marker, 1)
    path.write_text(source, encoding="utf-8")
    print("permanent social-card audit added: tools/site_audit.py")


def patch_premerge_record() -> None:
    path = ROOT / ".github/WATER_CIVILIZATION_POWER_09_PREMERGE.md"
    text = path.read_text(encoding="utf-8").rstrip()
    marker = "## Dedicated social-card integrity"
    if marker not in text:
        text += f"""

{marker}

- Arabic and English 1200×630 PNG cards are generated from retained source code in `tools/generate_water_social_cards.py`.
- Both dossier pages and both evidence appendices use the language-appropriate card in Open Graph, Twitter, and JSON-LD image metadata.
- The Arabic evidence appendix now uses the Arabic page as `x-default`, matching the dossier pair.
- The permanent repository audit validates the PNG signature, IHDR dimensions, minimum file size, language-specific metadata references, and removal of the generic site card from these four surfaces.
"""
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    for rel, config in PAGES.items():
        update_page(ROOT / rel, config)
    patch_audit()
    patch_premerge_record()


if __name__ == "__main__":
    main()
