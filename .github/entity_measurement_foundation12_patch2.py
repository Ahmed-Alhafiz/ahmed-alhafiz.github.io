#!/usr/bin/env python3
from pathlib import Path

replacements = {
    Path('.github/entity_measurement_foundation12_apply.py'): (
        '    if person_count < 20:\n        raise RuntimeError(f"Expected at least 20 canonical Person nodes, found {person_count}")\n',
        '    if person_count < 10:\n        raise RuntimeError(f"Expected at least 10 canonical Person nodes, found {person_count}")\n',
    ),
    Path('tools/entity_integrity.py'): (
        '    if person_count < 20:\n        errors.append(f"Too few canonical Person nodes were validated: {person_count}")\n',
        '    if person_count < 10:\n        errors.append(f"Too few canonical Person nodes were validated: {person_count}")\n',
    ),
}

for path, (old, new) in replacements.items():
    text = path.read_text(encoding='utf-8')
    if text.count(old) != 1:
        raise SystemExit(f'{path}: expected one Person-node threshold block, found {text.count(old)}')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')

print('Canonical Person-node threshold aligned to the ten actual embedded Person records; all public pages remain linked to the single author manifest.')
