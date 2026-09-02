#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path("visual-review/geometry")


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


def load_report(mode: str) -> list[dict]:
    source = ROOT / f"{mode}.html"
    parser = ResultParser()
    parser.feed(source.read_text(encoding="utf-8"))
    raw = html.unescape("".join(parser.values)).strip()
    if not raw:
        raise SystemExit(f"{source}: no browser result was produced")
    report = json.loads(raw)
    if report.get("status") != "complete":
        raise SystemExit(f"{source}: layout audit did not complete: {report}")
    results = report.get("results")
    if not isinstance(results, list) or len(results) != 6:
        raise SystemExit(f"{source}: expected six measurements, found {results!r}")
    (ROOT / f"{mode}.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return results


def main() -> None:
    reports = {mode: load_report(mode) for mode in ("desktop", "mobile")}

    for mode, report in reports.items():
        by_name = {item["name"]: item for item in report}
        if len(by_name) != 6:
            raise SystemExit(f"{mode}: duplicate or missing test names")

        for group in (
            ("home-ar", "home-en", "home-de"),
            ("about-ar", "about-en", "about-de"),
        ):
            widths = [by_name[name]["portrait"]["width"] for name in group]
            heights = [by_name[name]["portrait"]["height"] for name in group]
            if max(widths) - min(widths) > 1.5:
                raise SystemExit(
                    f"{mode}: cross-language portrait width drift: {dict(zip(group, widths))}"
                )
            if max(heights) - min(heights) > 1.5:
                raise SystemExit(
                    f"{mode}: cross-language portrait height drift: {dict(zip(group, heights))}"
                )

        for name, item in by_name.items():
            portrait = item["portrait"]
            image = item["image"]
            copy = item["copy"]
            viewport = item["viewport"]
            document = item["document"]

            ratio = portrait["width"] / portrait["height"]
            if not 0.79 <= ratio <= 0.81:
                raise SystemExit(
                    f"{mode} {name}: portrait ratio is {ratio:.4f}, expected 4:5"
                )
            if (
                abs(portrait["width"] - image["width"]) > 1.5
                or abs(portrait["height"] - image["height"]) > 1.5
            ):
                raise SystemExit(f"{mode} {name}: image does not fill portrait frame")
            if item["objectFit"] != "cover":
                raise SystemExit(
                    f"{mode} {name}: object-fit is {item['objectFit']!r}, expected cover"
                )
            if item["overlapArea"] > 2:
                raise SystemExit(
                    f"{mode} {name}: portrait overlaps copy by {item['overlapArea']} px²"
                )
            if document["scrollWidth"] > document["clientWidth"] + 1:
                raise SystemExit(
                    f"{mode} {name}: horizontal overflow "
                    f"{document['scrollWidth']} > {document['clientWidth']}"
                )

            width = viewport["width"]
            for label, rect in (("portrait", portrait), ("copy", copy)):
                if rect["left"] < -1.5 or rect["right"] > width + 1.5:
                    raise SystemExit(
                        f"{mode} {name}: {label} escapes viewport: {rect}"
                    )

            if mode == "mobile":
                if portrait["bottom"] > copy["top"] - 8:
                    raise SystemExit(
                        f"{mode} {name}: portrait is not cleanly stacked before copy; "
                        f"gap={item['verticalGap']}"
                    )
                if not 140 <= portrait["width"] <= 200:
                    raise SystemExit(
                        f"{mode} {name}: portrait width {portrait['width']} outside target"
                    )

    print(
        "Portrait layout passed: equal Arabic/English/German dimensions, "
        "4:5 crop, no copy overlap, no horizontal overflow, and portrait-first mobile order."
    )


if __name__ == "__main__":
    main()
