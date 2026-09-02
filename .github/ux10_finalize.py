#!/usr/bin/env python3
"""Final non-destructive cleanup for site UX rebuild 10."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WATER = ROOT / "en/articles/water-civilization-power/index.html"
OLD = "External specialist review: not yet completed"
NEW = "External review by an independent specialist: not yet completed"
OBSOLETE = (
    ROOT / ".github/visual-review/layout-audit.template",
    ROOT / ".github/visual-review/capture.template",
    ROOT / ".github/visual-review/verify_layout.py",
    ROOT / ".github/visual-review/verify_artifact.py",
)


def main() -> None:
    html = WATER.read_text(encoding="utf-8")
    count = html.count(OLD)
    if count != 1:
        raise SystemExit(f"Expected one old review-status phrase, found {count}")
    html = html.replace(OLD, NEW, 1)
    WATER.write_text(html, encoding="utf-8")

    removed = []
    for path in OBSOLETE:
        if path.exists():
            path.unlink()
            removed.append(path.relative_to(ROOT).as_posix())

    revised = WATER.read_text(encoding="utf-8")
    if OLD in revised or NEW not in revised:
        raise SystemExit("Review-status wording correction did not persist")
    if any(path.exists() for path in OBSOLETE):
        raise SystemExit("An obsolete visual-review helper remained")

    print("Corrected explicit external-review wording")
    print(f"Removed {len(removed)} obsolete visual-review helper files")
    for rel in removed:
        print(f"- {rel}")


if __name__ == "__main__":
    main()
