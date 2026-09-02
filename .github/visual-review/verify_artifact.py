#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import struct
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path("visual-review")


class ResultParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_result = False
        self.values: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "pre" and dict(attrs).get("id") == "result":
            self.in_result = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "pre" and self.in_result:
            self.in_result = False

    def handle_data(self, data: str) -> None:
        if self.in_result:
            self.values.append(data)


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise SystemExit(f"{path}: not a valid PNG")
    return struct.unpack(">II", data[16:24])


def validate_targets() -> None:
    reports = []
    for path in sorted((ROOT / "targets").glob("*.html")):
        parser = ResultParser()
        parser.feed(path.read_text(encoding="utf-8"))
        raw = html.unescape("".join(parser.values)).strip()
        if not raw:
            raise SystemExit(f"{path}: no target-capture result was produced")
        report = json.loads(raw)
        if report.get("status") != "complete":
            raise SystemExit(f"{path}: target capture did not complete: {report}")
        viewport_height = report["viewport"]["height"]
        target = report["target"]
        visible = max(
            0,
            min(viewport_height, target["bottom"]) - max(0, target["top"]),
        )
        required = min(180, max(80, target["height"] * 0.45))
        if visible < required:
            raise SystemExit(
                f"{path}: target is not sufficiently visible; "
                f"visible={visible}, required={required}, report={report}"
            )
        if report["selector"] == "#site-footer" and report["scrollY"] <= 0:
            raise SystemExit(f"{path}: footer capture did not scroll away from page top")
        if report["selector"] == "#contact" and report["scrollY"] <= 0:
            raise SystemExit(f"{path}: contact capture did not scroll away from page top")
        reports.append(report)
    if len(reports) != 12:
        raise SystemExit(f"Expected 12 target-capture reports, found {len(reports)}")


def validate_page_screenshots() -> None:
    expected = {"desktop": (1440, 1200), "mobile": (390, 844)}
    total = 0
    for mode, dimensions in expected.items():
        paths = sorted((ROOT / mode).glob("*.png"))
        if len(paths) != 30:
            raise SystemExit(f"{mode}: expected 30 screenshots, found {len(paths)}")
        for path in paths:
            if png_dimensions(path) != dimensions:
                raise SystemExit(
                    f"{path}: expected {dimensions}, found {png_dimensions(path)}"
                )
            size = path.stat().st_size
            if size < 5_000:
                raise SystemExit(f"{path}: suspiciously small render ({size} bytes)")
            total += 1
    print(f"Verified {total} desktop/mobile page screenshots")


def validate_geometry_reports() -> None:
    for mode in ("desktop", "mobile"):
        path = ROOT / "geometry" / f"{mode}.json"
        report = json.loads(path.read_text(encoding="utf-8"))
        if len(report) != 6:
            raise SystemExit(f"{path}: expected six measurements")


def validate_social_cards() -> None:
    paths = sorted((ROOT / "social").glob("*.png"))
    expected_names = {
        "water-civilization-power-ar.png",
        "water-civilization-power-en.png",
    }
    if {path.name for path in paths} != expected_names:
        raise SystemExit(
            f"social cards: expected {sorted(expected_names)}, "
            f"found {[path.name for path in paths]}"
        )
    for path in paths:
        dimensions = png_dimensions(path)
        if dimensions != (1200, 630):
            raise SystemExit(f"{path}: expected 1200×630, found {dimensions}")
        if path.stat().st_size < 10_000:
            raise SystemExit(
                f"{path}: suspiciously small social card ({path.stat().st_size} bytes)"
            )


def main() -> None:
    validate_targets()
    validate_page_screenshots()
    validate_geometry_reports()
    validate_social_cards()
    print(
        "Visual artifact passed: target scrolling verified, 60 page renders, "
        "two geometry reports, and two 1200×630 social cards."
    )


if __name__ == "__main__":
    main()
