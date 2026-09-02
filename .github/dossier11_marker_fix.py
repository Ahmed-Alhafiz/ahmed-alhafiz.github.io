#!/usr/bin/env python3
from pathlib import Path

path = Path('.github/dossier11_integrate.py')
text = path.read_text(encoding='utf-8')
changes = {
    "insert_once(ROOT / \"index.html\", '<section class=\"section\"><div class=\"wrap\"><div class=\"kicker\">Research tracks</div>', AR_HOME_BLOCK)":
        "insert_once(ROOT / \"index.html\", '<section class=\"section\">\\n  <div class=\"wrap\">\\n    <div class=\"kicker\">Research tracks</div>', AR_HOME_BLOCK)",
    "insert_once(ROOT / \"en/index.html\", '<section class=\"section\"><div class=\"wrap\"><div class=\"kicker\">Research tracks</div>', EN_HOME_BLOCK)":
        "insert_once(ROOT / \"en/index.html\", '<section class=\"section\">\\n  <div class=\"wrap\">\\n    <div class=\"kicker\">Research tracks</div>', EN_HOME_BLOCK)",
}
for old, new in changes.items():
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'Expected one home insertion call, found {count}: {old}')
    text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
print('Aligned Arabic and English home insertion markers with the formatted page structure')
