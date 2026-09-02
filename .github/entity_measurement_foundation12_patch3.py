#!/usr/bin/env python3
from pathlib import Path

path = Path('tools/visibility_audit.py')
text = path.read_text(encoding='utf-8')
old = '        author_links += html.count(\'rel="author"\')\n'
new = '        author_links += len(re.findall(r\'<link\\b[^>]*\\brel=["\\\']author["\\\'][^>]*>\', html, re.IGNORECASE))\n'
if text.count(old) != 1:
    raise SystemExit(f'Expected one broad author-link counter, found {text.count(old)}')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
print('Visibility audit now counts canonical head author links without double-counting visible byline links.')
