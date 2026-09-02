#!/usr/bin/env python3
from pathlib import Path

path = Path('.github/site_ux_rebuild10_runner.py')
text = path.read_text(encoding='utf-8')
for line in (
    '        "en/articles/ratq-fatq-big-bang/evidence/claims.json",\n',
    '        "en/articles/water-civilization-power/evidence/claims.json",\n',
):
    if text.count(line) != 1:
        raise SystemExit(f'Expected one obsolete English claims path: {line.strip()}')
    text = text.replace(line, '', 1)
path.write_text(text, encoding='utf-8')
print('Corrected evidence-manifest inventory: machine claims files are canonical Arabic-path assets.')
