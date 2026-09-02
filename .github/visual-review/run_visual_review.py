#!/usr/bin/env python3
"""Render and verify the multilingual site with a real browser.

The runner uses Selenium only for browser control; it does not alter the site.
It verifies computed portrait geometry, stacking, overlap, viewport overflow,
targeted footer/contact visibility, screenshot dimensions, and social-card
assets before producing the pull-request artifact.
"""
from __future__ import annotations

import json
import shutil
import struct
import time
from pathlib import Path
from typing import Any

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "http://127.0.0.1:4173"
ROOT = Path("visual-review")
WAIT_SECONDS = 15

VIEWPORTS = {
    "desktop": (1440, 1200),
    "mobile": (390, 844),
}

GEOMETRY_TESTS = (
    ("home-ar", "/", ".hero-portrait", ".home-hero-grid>div:first-child"),
    ("home-en", "/en/", ".hero-portrait", ".home-hero-grid>div:first-child"),
    ("home-de", "/de/", ".hero-portrait", ".home-hero-grid>div:first-child"),
    ("about-ar", "/about/", ".profile-portrait", ".profile-grid>div:first-child"),
    ("about-en", "/en/about/", ".profile-portrait", ".profile-grid>div:first-child"),
    ("about-de", "/de/about/", ".profile-portrait", ".profile-grid>div:first-child"),
)

TOP_PAGES = (
    ("home-ar", "/"),
    ("home-en", "/en/"),
    ("home-de", "/de/"),
    ("about-ar", "/about/"),
    ("about-en", "/en/about/"),
    ("about-de", "/de/about/"),
    ("research-ar", "/articles/"),
    ("research-en", "/en/articles/"),
    ("ratq-ar", "/articles/ratq-fatq-big-bang/"),
    ("ratq-en", "/en/articles/ratq-fatq-big-bang/"),
    ("water-ar", "/articles/water-civilization-power/"),
    ("water-en", "/en/articles/water-civilization-power/"),
    ("fear-ar", "/articles/diagnostic-uncertainty-family-fear-coercive-authority/"),
    ("fear-en", "/en/articles/diagnostic-uncertainty-family-fear-coercive-authority/"),
    ("fear-evidence-ar", "/articles/diagnostic-uncertainty-family-fear-coercive-authority/evidence/"),
    ("fear-evidence-en", "/en/articles/diagnostic-uncertainty-family-fear-coercive-authority/evidence/"),
    ("sirou-ar", "/books/sirou-fi-alard/"),
    ("sirou-en", "/en/books/sirou-fi-alard/"),
    ("sirou-de", "/de/books/sirou-fi-alard/"),
    ("umm-abbas-ar", "/books/umm-abbas/"),
    ("umm-abbas-en", "/en/books/umm-abbas/"),
    ("umm-abbas-de", "/de/books/umm-abbas/"),
    ("juhayman-ar", "/books/juhayman/"),
    ("juhayman-en", "/en/books/juhayman/"),
    ("juhayman-de", "/de/books/juhayman/"),
    ("kitab-al-kutub-ar", "/books/kitab-al-kutub/"),
    ("kitab-al-kutub-en", "/en/books/kitab-al-kutub/"),
    ("kitab-al-kutub-de", "/de/books/kitab-al-kutub/"),
)

TARGET_PAGES = (
    ("home-ar-footer", "/", "#site-footer", "end"),
    ("home-en-footer", "/en/", "#site-footer", "end"),
    ("home-de-footer", "/de/", "#site-footer", "end"),
    ("about-ar-contact", "/about/", "#contact", "start"),
    ("about-en-contact", "/en/about/", "#contact", "start"),
    ("about-de-contact", "/de/about/", "#contact", "start"),
    ("fear-cascade-ar", "/articles/diagnostic-uncertainty-family-fear-coercive-authority/", "#cascade-figure", "start"),
    ("fear-parallel-ar", "/articles/diagnostic-uncertainty-family-fear-coercive-authority/", "#parallel-figure", "start"),
    ("fear-cascade-en", "/en/articles/diagnostic-uncertainty-family-fear-coercive-authority/", "#cascade-figure", "start"),
    ("fear-parallel-en", "/en/articles/diagnostic-uncertainty-family-fear-coercive-authority/", "#parallel-figure", "start"),
)

SOCIAL_CARDS = (
    Path("assets/social/water-civilization-power-ar.png"),
    Path("assets/social/water-civilization-power-en.png"),
    Path("assets/social/diagnostic-uncertainty-family-fear-ar.png"),
    Path("assets/social/diagnostic-uncertainty-family-fear-en.png"),
)


def rounded_rect(driver: webdriver.Chrome, element: Any) -> dict[str, float]:
    return driver.execute_script(
        """
        const r = arguments[0].getBoundingClientRect();
        const q = value => Math.round(value * 100) / 100;
        return {top:q(r.top), right:q(r.right), bottom:q(r.bottom), left:q(r.left), width:q(r.width), height:q(r.height)};
        """,
        element,
    )


def configure_viewport(driver: webdriver.Chrome, width: int, height: int) -> None:
    driver.set_window_rect(x=0, y=0, width=width, height=height)
    driver.execute_cdp_cmd(
        "Emulation.setDeviceMetricsOverride",
        {
            "width": width,
            "height": height,
            "deviceScaleFactor": 1,
            "mobile": False,
            "screenWidth": width,
            "screenHeight": height,
            "positionX": 0,
            "positionY": 0,
            "dontSetVisibleSize": False,
        },
    )


def wait_for_page(driver: webdriver.Chrome) -> None:
    wait = WebDriverWait(driver, WAIT_SECONDS)
    wait.until(lambda browser: browser.execute_script("return document.readyState") == "complete")
    wait.until(
        lambda browser: browser.execute_script(
            "return Array.from(document.images).every(image => image.complete)"
        )
    )
    driver.set_script_timeout(WAIT_SECONDS)
    try:
        driver.execute_async_script(
            """
            const done = arguments[0];
            if (document.fonts && document.fonts.ready) {
              document.fonts.ready.then(() => done(true), () => done(false));
            } else {
              done(true);
            }
            """
        )
    except TimeoutException:
        raise SystemExit(f"Timed out waiting for fonts on {driver.current_url}")
    driver.execute_script("window.scrollTo(0, 0)")
    time.sleep(0.15)


def open_page(driver: webdriver.Chrome, route: str, marker: str) -> None:
    separator = "&" if "?" in route else "?"
    driver.get(f"{BASE_URL}{route}{separator}visual_review={marker}")
    wait_for_page(driver)


def overlap_area(first: dict[str, float], second: dict[str, float]) -> float:
    width = max(0.0, min(first["right"], second["right"]) - max(first["left"], second["left"]))
    height = max(0.0, min(first["bottom"], second["bottom"]) - max(first["top"], second["top"]))
    return round(width * height, 2)


def measure_layout(driver: webdriver.Chrome, mode: str, width: int, height: int) -> list[dict[str, Any]]:
    configure_viewport(driver, width, height)
    results: list[dict[str, Any]] = []
    for name, route, portrait_selector, copy_selector in GEOMETRY_TESTS:
        open_page(driver, route, f"geometry-{mode}")
        portrait = driver.find_element(By.CSS_SELECTOR, portrait_selector)
        image = portrait.find_element(By.TAG_NAME, "img")
        copy = driver.find_element(By.CSS_SELECTOR, copy_selector)
        portrait_rect = rounded_rect(driver, portrait)
        image_rect = rounded_rect(driver, image)
        copy_rect = rounded_rect(driver, copy)
        computed = driver.execute_script(
            """
            const style = getComputedStyle(arguments[0]);
            return {objectFit:style.objectFit, objectPosition:style.objectPosition};
            """,
            image,
        )
        document_metrics = driver.execute_script(
            """
            return {
              scrollWidth: document.documentElement.scrollWidth,
              clientWidth: document.documentElement.clientWidth,
              scrollHeight: document.documentElement.scrollHeight,
              clientHeight: document.documentElement.clientHeight
            };
            """
        )
        results.append(
            {
                "name": name,
                "viewport": {"width": width, "height": height},
                "document": document_metrics,
                "portrait": portrait_rect,
                "image": image_rect,
                "copy": copy_rect,
                "overlapArea": overlap_area(portrait_rect, copy_rect),
                "verticalGap": round(copy_rect["top"] - portrait_rect["bottom"], 2),
                **computed,
            }
        )

    (ROOT / "geometry" / f"{mode}.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return results


def verify_layout(reports: dict[str, list[dict[str, Any]]]) -> None:
    for mode, report in reports.items():
        by_name = {item["name"]: item for item in report}
        if len(by_name) != 6:
            raise SystemExit(f"{mode}: duplicate or missing portrait tests")

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
            document = item["document"]
            ratio = portrait["width"] / portrait["height"]
            if not 0.79 <= ratio <= 0.81:
                raise SystemExit(f"{mode} {name}: portrait ratio {ratio:.4f} is not 4:5")
            if abs(portrait["width"] - image["width"]) > 1.5 or abs(portrait["height"] - image["height"]) > 1.5:
                raise SystemExit(f"{mode} {name}: portrait image does not fill its frame")
            if item["objectFit"] != "cover":
                raise SystemExit(f"{mode} {name}: object-fit is {item['objectFit']!r}")
            if item["overlapArea"] > 2:
                raise SystemExit(f"{mode} {name}: portrait overlaps copy by {item['overlapArea']} px²")
            if document["scrollWidth"] > document["clientWidth"] + 1:
                raise SystemExit(
                    f"{mode} {name}: horizontal overflow "
                    f"{document['scrollWidth']} > {document['clientWidth']}"
                )
            viewport_width = item["viewport"]["width"]
            for label, rect in (("portrait", portrait), ("copy", copy)):
                if rect["left"] < -1.5 or rect["right"] > viewport_width + 1.5:
                    raise SystemExit(f"{mode} {name}: {label} escapes viewport: {rect}")
            if mode == "mobile":
                if portrait["bottom"] > copy["top"] - 8:
                    raise SystemExit(
                        f"mobile {name}: portrait is not cleanly above copy; "
                        f"gap={item['verticalGap']}"
                    )
                if not 140 <= portrait["width"] <= 200:
                    raise SystemExit(
                        f"mobile {name}: portrait width {portrait['width']} outside 140–200 px"
                    )


def screenshot(driver: webdriver.Chrome, output: Path, width: int, height: int) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if not driver.save_screenshot(str(output)):
        raise SystemExit(f"Failed to save screenshot {output}")
    actual = png_dimensions(output)
    if actual != (width, height):
        raise SystemExit(f"{output}: expected {(width, height)}, found {actual}")
    if output.stat().st_size < 5_000:
        raise SystemExit(f"{output}: suspiciously small screenshot ({output.stat().st_size} bytes)")


def render_top_pages(driver: webdriver.Chrome, mode: str, width: int, height: int) -> None:
    configure_viewport(driver, width, height)
    for name, route in TOP_PAGES:
        open_page(driver, route, f"top-{mode}")
        metrics = driver.execute_script(
            "return {scrollWidth:document.documentElement.scrollWidth,clientWidth:document.documentElement.clientWidth};"
        )
        if metrics["scrollWidth"] > metrics["clientWidth"] + 1:
            raise SystemExit(f"{mode} {route}: horizontal overflow {metrics}")
        screenshot(driver, ROOT / mode / f"{name}.png", width, height)


def render_targets(driver: webdriver.Chrome, mode: str, width: int, height: int) -> list[dict[str, Any]]:
    configure_viewport(driver, width, height)
    reports: list[dict[str, Any]] = []
    for name, route, selector, alignment in TARGET_PAGES:
        open_page(driver, route, f"target-{mode}")
        element = driver.find_element(By.CSS_SELECTOR, selector)
        driver.execute_script(
            "arguments[0].scrollIntoView({block:arguments[1], inline:'nearest'});",
            element,
            alignment,
        )
        if alignment == "start":
            driver.execute_script("window.scrollBy(0, -20)")
        time.sleep(0.15)
        rect = rounded_rect(driver, element)
        scroll_y = float(driver.execute_script("return window.scrollY"))
        visible = max(0.0, min(float(height), rect["bottom"]) - max(0.0, rect["top"]))
        required = min(180.0, max(80.0, rect["height"] * 0.45))
        if scroll_y <= 0:
            raise SystemExit(f"{mode} {name}: targeted capture did not scroll")
        if visible < required:
            raise SystemExit(
                f"{mode} {name}: target visibility {visible} < {required}; rect={rect}"
            )
        report = {
            "name": name,
            "route": route,
            "selector": selector,
            "alignment": alignment,
            "scrollY": round(scroll_y, 2),
            "viewport": {"width": width, "height": height},
            "target": rect,
            "visibleHeight": round(visible, 2),
        }
        reports.append(report)
        screenshot(driver, ROOT / mode / f"{name}.png", width, height)

    (ROOT / "targets" / f"{mode}.json").write_text(
        json.dumps(reports, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return reports


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise SystemExit(f"{path}: not a valid PNG")
    return struct.unpack(">II", data[16:24])


def copy_and_verify_social_cards() -> None:
    output = ROOT / "social"
    output.mkdir(parents=True, exist_ok=True)
    for source in SOCIAL_CARDS:
        target = output / source.name
        shutil.copy2(source, target)
        if png_dimensions(target) != (1200, 630):
            raise SystemExit(f"{target}: expected 1200×630, found {png_dimensions(target)}")
        if target.stat().st_size < 10_000:
            raise SystemExit(f"{target}: suspiciously small social card")


def verify_inventory() -> None:
    expected_screenshots = len(TOP_PAGES) + len(TARGET_PAGES)
    for mode, dimensions in VIEWPORTS.items():
        images = sorted((ROOT / mode).glob("*.png"))
        if len(images) != expected_screenshots:
            raise SystemExit(
                f"{mode}: expected {expected_screenshots} screenshots, found {len(images)}"
            )
        for image in images:
            if png_dimensions(image) != dimensions:
                raise SystemExit(f"{image}: wrong screenshot dimensions")
    if len(list((ROOT / "geometry").glob("*.json"))) != len(VIEWPORTS):
        raise SystemExit(f"Expected {len(VIEWPORTS)} geometry reports")
    if len(list((ROOT / "targets").glob("*.json"))) != len(VIEWPORTS):
        raise SystemExit(f"Expected {len(VIEWPORTS)} target reports")
    if len(list((ROOT / "social").glob("*.png"))) != len(SOCIAL_CARDS):
        raise SystemExit(f"Expected {len(SOCIAL_CARDS)} social cards")


def build_driver() -> webdriver.Chrome:
    binary = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    if not binary:
        raise SystemExit("No Chromium-compatible browser found")
    options = Options()
    options.binary_location = binary
    for argument in (
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--hide-scrollbars",
        "--disable-extensions",
        "--disable-background-networking",
        "--force-device-scale-factor=1",
        "--window-size=1440,1200",
    ):
        options.add_argument(argument)
    options.page_load_strategy = "normal"
    return webdriver.Chrome(options=options)


def main() -> None:
    for directory in ("desktop", "mobile", "geometry", "targets", "social"):
        (ROOT / directory).mkdir(parents=True, exist_ok=True)

    driver = build_driver()
    try:
        reports = {
            mode: measure_layout(driver, mode, width, height)
            for mode, (width, height) in VIEWPORTS.items()
        }
        verify_layout(reports)
        print("Computed portrait geometry passed across Arabic, English, and German")

        for mode, (width, height) in VIEWPORTS.items():
            render_top_pages(driver, mode, width, height)
            render_targets(driver, mode, width, height)
    finally:
        driver.quit()

    copy_and_verify_social_cards()
    verify_inventory()
    total_screenshots = (len(TOP_PAGES) + len(TARGET_PAGES)) * len(VIEWPORTS)
    print(
        f"Visual review passed: {total_screenshots} exact-size screenshots, "
        f"{len(GEOMETRY_TESTS)} portrait tests at {len(VIEWPORTS)} viewports, "
        f"{len(TARGET_PAGES) * len(VIEWPORTS)} verified targeted captures, "
        f"and {len(SOCIAL_CARDS)} social cards."
    )


if __name__ == "__main__":
    main()
