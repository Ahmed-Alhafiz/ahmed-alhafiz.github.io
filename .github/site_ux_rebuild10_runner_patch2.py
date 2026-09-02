#!/usr/bin/env python3
from pathlib import Path

path = Path('.github/site_ux_rebuild10_runner.py')
text = path.read_text(encoding='utf-8')
old = '    parse_structured_outputs()\n'
new = '''    for trigger in (ROOT / ".github").glob("site-ux-rebuild-10*.trigger"):
        trigger.unlink(missing_ok=True)

    parse_structured_outputs()
'''
if text.count(old) != 1:
    raise SystemExit(f'Expected one structured-output call, found {text.count(old)}')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
print('Runner now removes every UX rebuild trigger before the permanent audit.')
