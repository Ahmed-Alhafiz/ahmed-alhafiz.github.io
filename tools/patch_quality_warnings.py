#!/usr/bin/env python3
"""One-time cleanup for image dimensions and overlong localized descriptions."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path('.')
IMG_RE = re.compile(r'<img\b[^>]*>', re.IGNORECASE)
SRC_RE = re.compile(r'\bsrc=["\']([^"\']+)["\']', re.IGNORECASE)

DIMENSIONS = {
    'ahmed-alhafiz-author.png': (1229, 1536),
    'ahmed-alhafiz-social-card.png': (1200, 630),
    'juhayman-cover.webp': (800, 1200),
    'kitab-al-kutub-cover.webp': (800, 1200),
    'sirou-fi-alard-cover.webp': (800, 1200),
    'umm-abbas-cover.webp': (800, 1200),
}

changed_pages = []
unknown_images = []
for path in sorted(ROOT.rglob('*.html')):
    if '.git' in path.parts:
        continue
    text = path.read_text(encoding='utf-8')
    original = text

    def add_dimensions(match: re.Match[str]) -> str:
        tag = match.group(0)
        if re.search(r'\bwidth=["\']', tag, re.IGNORECASE) and re.search(r'\bheight=["\']', tag, re.IGNORECASE):
            return tag
        src_match = SRC_RE.search(tag)
        if not src_match:
            unknown_images.append(f'{path}: img without src/dimensions')
            return tag
        filename = src_match.group(1).split('?')[0].split('#')[0].rstrip('/').split('/')[-1]
        dims = DIMENSIONS.get(filename)
        if not dims:
            unknown_images.append(f'{path}: unknown dimensions for {filename}')
            return tag
        width, height = dims
        insert = ''
        if not re.search(r'\bwidth=["\']', tag, re.IGNORECASE):
            insert += f' width="{width}"'
        if not re.search(r'\bheight=["\']', tag, re.IGNORECASE):
            insert += f' height="{height}"'
        return tag[:-1] + insert + '>'

    text = IMG_RE.sub(add_dimensions, text)
    if text != original:
        path.write_text(text, encoding='utf-8')
        changed_pages.append(path.as_posix())

if unknown_images:
    raise SystemExit('Unresolved image dimensions:\n' + '\n'.join(unknown_images))

localized_descriptions = {
    Path('en/about/index.html'): 'Official profile of Ahmed Alhafiz, an Arab writer and author working across fiction, thought, history, religion and science.',
    Path('de/about/index.html'): 'Offizielles Autorenprofil von Ahmed Alhafiz: arabischer Schriftsteller zu Literatur, Geschichte, Religion, Wissenschaft und Gesellschaft.',
}

for path, description in localized_descriptions.items():
    text = path.read_text(encoding='utf-8')
    pattern = re.compile(r'(<meta\s+name=["\']description["\']\s+content=["\'])(.*?)(["\']\s*/?>)', re.IGNORECASE)
    text2, count = pattern.subn(lambda m: m.group(1) + description + m.group(3), text, count=1)
    if count != 1:
        raise SystemExit(f'Could not patch exactly one description in {path}')
    if text2 != text:
        path.write_text(text2, encoding='utf-8')
        changed_pages.append(path.as_posix())

print(f'Quality warning patch changed {len(set(changed_pages))} pages.')
