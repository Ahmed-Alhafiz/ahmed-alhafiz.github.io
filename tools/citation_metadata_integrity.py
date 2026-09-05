#!/usr/bin/env python3
"""Protect Citation File Format metadata from invalid root semantics.

CFF 1.2 root works are software or datasets; article/book/report types belong
in references such as preferred-citation. This repository uses dossier-level
CFF files to describe portable evidence/citation packages (datasets) and then
points to the human-readable dossier as the preferred article citation.

This is a repository policy gate, not a replacement for a complete CFF schema
validator. It catches the failure modes relevant to these published files and
keeps the metadata honest and internally consistent.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TOP_FIELD = re.compile(r"^([A-Za-z0-9-]+):(?:\s*(.*))?$")
PREFERRED = re.compile(r"^preferred-citation:\s*$")
INDENTED_TYPE = re.compile(r"^\s{2}type:\s*([^#]+?)\s*$")


def scalar(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip().strip('"').strip("'")


def top_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith((" ", "\t")):
            continue
        match = TOP_FIELD.match(line)
        if match:
            fields[match.group(1)] = scalar(match.group(2))
    return fields


def preferred_type(text: str) -> str | None:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not PREFERRED.match(line):
            continue
        for child in lines[index + 1 :]:
            if child and not child.startswith((" ", "\t")):
                break
            match = INDENTED_TYPE.match(child)
            if match:
                return scalar(match.group(1))
    return None


def main() -> None:
    paths = sorted(ROOT.rglob("CITATION.cff"))
    if not paths:
        raise SystemExit("No CITATION.cff files found")

    errors: list[str] = []
    checked: list[str] = []
    for path in paths:
        if ".git" in path.parts:
            continue
        rel = str(path.relative_to(ROOT))
        text = path.read_text(encoding="utf-8")
        fields = top_fields(text)
        checked.append(rel)

        if fields.get("cff-version") != "1.2.0":
            errors.append(f"{rel}: cff-version must be 1.2.0")
        for required in ("message", "title", "type", "authors", "date-released", "url"):
            if required not in fields:
                errors.append(f"{rel}: missing required repository field {required}")

        root_type = fields.get("type")
        if root_type not in {"dataset", "software"}:
            errors.append(
                f"{rel}: CFF 1.2 root type must be dataset/software; found {root_type!r}"
            )

        license_value = fields.get("license")
        if license_value and license_value.casefold() in {
            "all rights reserved",
            "all-rights-reserved",
        }:
            errors.append(
                f"{rel}: 'All rights reserved' is not an SPDX license identifier; omit license instead"
            )

        # The collection-level root CFF describes the research collection.
        # Dossier-level evidence packages must give the article citation that a
        # reader should actually use.
        if rel != "CITATION.cff":
            ptype = preferred_type(text)
            if ptype != "article":
                errors.append(
                    f"{rel}: dossier evidence package requires preferred-citation type article"
                )
            if "preferred-citation:" not in text:
                errors.append(f"{rel}: preferred-citation missing")

    if errors:
        print("CITATION METADATA ERRORS:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print(
        "Citation metadata integrity passed for "
        f"{len(checked)} CFF files: root work types, required fields, licensing, "
        "and dossier preferred citations are internally consistent."
    )


if __name__ == "__main__":
    main()
