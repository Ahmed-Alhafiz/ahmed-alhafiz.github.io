#!/usr/bin/env python3
from pathlib import Path

path = Path('.github/dossier11_integrate.py')
text = path.read_text(encoding='utf-8')
old = "insert_once(ROOT / \"index.html\", '<section class=\"section\"><div class=\"wrap\"><div class=\"kicker\">Research tracks</div>', AR_HOME_BLOCK)"
new = "insert_once(ROOT / \"index.html\", '<section class=\"section\">\\n  <div class=\"wrap\">\\n    <div class=\"kicker\">Research tracks</div>', AR_HOME_BLOCK)"
count = text.count(old)
if count != 1:
    raise SystemExit(f'Expected one Arabic home insertion call, found {count}')
text = text.replace(old, new, 1)
# The English homepage keeps its section in a compact single-line form, so its
# original marker is intentionally preserved.
path.write_text(text, encoding='utf-8')
print('Aligned the Arabic home marker and preserved the compact English marker')
