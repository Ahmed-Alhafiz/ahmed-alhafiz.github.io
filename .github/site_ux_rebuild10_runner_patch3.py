#!/usr/bin/env python3
from pathlib import Path

path = Path('.github/site_ux_rebuild10_runner.py')
text = path.read_text(encoding='utf-8')
old = '''        custom_checks()
        run("git", "diff", "--check")
'''
new = '''        custom_checks()
        for candidate in list(ROOT.rglob("*.html")) + list(ROOT.rglob("*.css")):
            if ".git" in candidate.parts:
                continue
            original = candidate.read_text(encoding="utf-8")
            normalized = "\\n".join(line.rstrip() for line in original.splitlines()) + "\\n"
            if normalized != original:
                candidate.write_text(normalized, encoding="utf-8")
        run("git", "diff", "--check")
'''
if text.count(old) != 1:
    raise SystemExit(f'Expected one final verification block, found {text.count(old)}')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
print('Runner now normalizes generated HTML/CSS trailing whitespace before diff verification.')
