#!/usr/bin/env python3
from pathlib import Path

path = Path('.github/entity_measurement_foundation12_apply.py')
text = path.read_text(encoding='utf-8')
old = "    if 'rel=\"author\"' in html or 'href=\"/author.json\"' in html:\n"
new = "    if '<link rel=\"author\"' in html or 'href=\"/author.json\"' in html:\n"
if text.count(old) != 1:
    raise SystemExit(f'Expected one overly broad author relation check, found {text.count(old)}')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
print('Integration now permits existing visible byline links while guarding the canonical head link.')
