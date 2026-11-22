"""Recover the text verified by the historical Indonesian release audits."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVISIONS = json.loads(
    (ROOT / "audit-reports/book-publication-editorial-revisions-2026-11-22.json").read_text()
)


def historical_text(path):
    text = path.read_text()
    for offset, published, previous in reversed(REVISIONS.get(path.relative_to(ROOT).as_posix(), [])):
        if text[offset:offset + len(published)] != published:
            raise ValueError(f"{path}: the approved publication wording was changed")
        text = text[:offset] + previous + text[offset + len(published):]
    return text
