#!/usr/bin/env python3
"""Verify that book covers render as true 2:3 artwork, not padded canvases.

The covers do not share one luminance profile: Juhayman is intentionally much
darker than the other jackets. Padding is therefore detected from uniform
edge bands and low whole-image variation, not from one brightness quota.

Element screenshots supplied by WebDriver can be clipped to the visible mobile
viewport. This audit therefore uses Chrome DevTools Protocol with
``captureBeyondViewport`` so every measured 2:3 frame is inspected in full.
"""
from __future__ import annotations

import base64
import json
import shutil
import struct
import time
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

BASE = "http://127.0.0.1:4173"
ROOT = Path("visual-review")
VIEWPORTS = {"desktop": (1440, 1200), "mobile": (390, 844)}
BOOKS = (
    ("sirou", "sirou-fi-alard"),
    ("umm-abbas", "umm-abbas"),
    ("juhayman", "juhayman"),
    ("kitab-al-kutub", "kitab-al-kutub"),
)
LANGS = (("ar", ""), ("en", "en/"), ("de", "de/"))
HOME_ROUTES = (("ar", "/"), ("en", "/en/"), ("de", "/de/"))

# Juhayman is a deliberately black, low-key cover. A per-title floor prevents
# the audit from confusing visual darkness with an empty/padded canvas.
MIN_VISIBLE_CONTENT = {
    "sirou-fi-alard": 0.18,
    "umm-abbas": 0.18,
    "juhayman": 0.12,
    "kitab-al-kutub": 0.18,
}


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
    return webdriver.Chrome(options=options)


def configure(driver: webdriver.Chrome, width: int, height: int) -> None:
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


def open_page(driver: webdriver.Chrome, route: str) -> None:
    driver.get(f"{BASE}{route}?cover_audit=ux10")
    wait = WebDriverWait(driver, 15)
    wait.until(lambda browser: browser.execute_script("return document.readyState") == "complete")
    wait.until(
        lambda browser: browser.execute_script(
            """
            const image = document.querySelector('.book-hero-cover img') || document.querySelector('#works img');
            return !image || (image.complete && image.naturalWidth > 0);
            """
        )
    )
    driver.execute_script(
        "document.documentElement.style.scrollBehavior='auto';"
        "document.body.style.scrollBehavior='auto';"
        "window.scrollTo(0,0);"
    )
    time.sleep(0.12)


def rect(driver: webdriver.Chrome, element: Any) -> dict[str, float]:
    return driver.execute_script(
        """
        const r = arguments[0].getBoundingClientRect();
        const q = value => Math.round(value * 100) / 100;
        return {top:q(r.top),right:q(r.right),bottom:q(r.bottom),left:q(r.left),width:q(r.width),height:q(r.height)};
        """,
        element,
    )


def capture_element_beyond_viewport(
    driver: webdriver.Chrome,
    element: Any,
    output: Path,
) -> None:
    """Capture the complete element in document coordinates through CDP."""
    driver.execute_script(
        """
        document.documentElement.style.scrollBehavior = 'auto';
        document.body.style.scrollBehavior = 'auto';
        arguments[0].scrollIntoView({block:'center', inline:'nearest', behavior:'auto'});
        """,
        element,
    )
    time.sleep(0.12)
    clip = driver.execute_script(
        """
        const r = arguments[0].getBoundingClientRect();
        return {
          x: r.left + window.scrollX,
          y: r.top + window.scrollY,
          width: r.width,
          height: r.height
        };
        """,
        element,
    )
    if clip["width"] <= 0 or clip["height"] <= 0:
        raise SystemExit(f"Cannot capture an empty element frame: {clip}")
    result = driver.execute_cdp_cmd(
        "Page.captureScreenshot",
        {
            "format": "png",
            "fromSurface": True,
            "captureBeyondViewport": True,
            "clip": {
                "x": float(clip["x"]),
                "y": float(clip["y"]),
                "width": float(clip["width"]),
                "height": float(clip["height"]),
                "scale": 1,
            },
        },
    )
    encoded = result.get("data")
    if not encoded:
        raise SystemExit(f"Chrome returned no screenshot data for {output}")
    payload = base64.b64decode(encoded, validate=True)
    if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
        raise SystemExit(f"Chrome returned a non-PNG element capture for {output}")
    output.write_bytes(payload)


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise SystemExit(f"{path}: not a valid PNG")
    return struct.unpack(">II", data[16:24])


def band_stats(image: Image.Image, top: bool) -> dict[str, float]:
    gray = image.convert("L")
    height = max(4, round(gray.height * 0.12))
    box = (0, 0, gray.width, height) if top else (0, gray.height - height, gray.width, gray.height)
    band = gray.crop(box)
    stat = ImageStat.Stat(band)
    histogram = band.histogram()
    pixels = band.width * band.height
    near_black = sum(histogram[:24]) / pixels
    return {
        "mean": round(stat.mean[0], 2),
        "stddev": round(stat.stddev[0], 2),
        "nearBlackFraction": round(near_black, 4),
    }


def whole_image_stats(image: Image.Image) -> dict[str, float]:
    gray = image.convert("L")
    stat = ImageStat.Stat(gray)
    histogram = gray.histogram()
    pixels = gray.width * gray.height
    visible = sum(histogram[30:]) / pixels
    return {
        "mean": round(stat.mean[0], 2),
        "stddev": round(stat.stddev[0], 2),
        "visibleContentFraction": round(visible, 4),
    }


def audit_book_covers(driver: webdriver.Chrome, mode: str, width: int, height: int) -> list[dict[str, Any]]:
    output = ROOT / "covers"
    output.mkdir(parents=True, exist_ok=True)
    reports = []
    configure(driver, width, height)

    for language, prefix in LANGS:
        for short, slug in BOOKS:
            route = f"/{prefix}books/{slug}/"
            open_page(driver, route)
            frame = driver.find_element(By.CSS_SELECTOR, ".book-hero-cover")
            image = frame.find_element(By.TAG_NAME, "img")
            frame_rect = rect(driver, frame)
            image_rect = rect(driver, image)
            style = driver.execute_script(
                "const s=getComputedStyle(arguments[0]);return {objectFit:s.objectFit,objectPosition:s.objectPosition};",
                image,
            )

            ratio = frame_rect["width"] / frame_rect["height"]
            if not 0.662 <= ratio <= 0.671:
                raise SystemExit(f"{mode} {language}/{slug}: cover frame ratio {ratio:.4f} is not 2:3")
            if abs(frame_rect["width"] - image_rect["width"]) > 1.5 or abs(frame_rect["height"] - image_rect["height"]) > 1.5:
                raise SystemExit(f"{mode} {language}/{slug}: image does not fill cover frame")
            if style["objectFit"] != "cover":
                raise SystemExit(f"{mode} {language}/{slug}: object-fit is {style['objectFit']!r}")
            if frame_rect["left"] < -1.5 or frame_rect["right"] > width + 1.5:
                raise SystemExit(f"{mode} {language}/{slug}: cover escapes viewport")

            shot = output / f"{mode}-{language}-{short}.png"
            capture_element_beyond_viewport(driver, frame, shot)
            if shot.stat().st_size < 4_000:
                raise SystemExit(f"{shot}: suspiciously small cover render")
            rendered = Image.open(shot).convert("RGB")
            rendered_ratio = rendered.width / rendered.height
            if not 0.662 <= rendered_ratio <= 0.671:
                raise SystemExit(f"{shot}: rendered ratio {rendered_ratio:.4f} is not 2:3")

            top = band_stats(rendered, True)
            bottom = band_stats(rendered, False)
            whole = whole_image_stats(rendered)
            padded_top = top["nearBlackFraction"] > 0.96 and top["stddev"] < 8
            padded_bottom = bottom["nearBlackFraction"] > 0.96 and bottom["stddev"] < 8
            if padded_top and padded_bottom:
                raise SystemExit(
                    f"{shot}: uniform black padding remains at both edges; top={top}, bottom={bottom}"
                )
            if whole["stddev"] < 12:
                raise SystemExit(f"{shot}: rendered cover is visually near-uniform: {whole}")
            minimum = MIN_VISIBLE_CONTENT[slug]
            if whole["visibleContentFraction"] < minimum:
                raise SystemExit(
                    f"{shot}: too little visible artwork for {slug} "
                    f"({whole['visibleContentFraction']} < {minimum}); stats={whole}"
                )

            reports.append(
                {
                    "mode": mode,
                    "language": language,
                    "book": slug,
                    "route": route,
                    "frame": frame_rect,
                    "image": image_rect,
                    "objectFit": style["objectFit"],
                    "objectPosition": style["objectPosition"],
                    "rendered": {"width": rendered.width, "height": rendered.height},
                    "topBand": top,
                    "bottomBand": bottom,
                    "wholeImage": whole,
                    "minimumVisibleContent": minimum,
                }
            )

    (ROOT / "covers" / f"{mode}-report.json").write_text(
        json.dumps(reports, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return reports


def capture_works(driver: webdriver.Chrome, mode: str, width: int, height: int) -> None:
    output = ROOT / "works"
    output.mkdir(parents=True, exist_ok=True)
    configure(driver, width, height)
    for language, route in HOME_ROUTES:
        open_page(driver, route)
        target = driver.find_element(By.CSS_SELECTOR, "#works")
        driver.execute_script(
            "arguments[0].scrollIntoView({block:'start',inline:'nearest',behavior:'auto'});window.scrollBy({top:-20,left:0,behavior:'auto'});",
            target,
        )
        time.sleep(0.15)
        target_rect = rect(driver, target)
        visible = max(0.0, min(float(height), target_rect["bottom"]) - max(0.0, target_rect["top"]))
        if float(driver.execute_script("return window.scrollY")) <= 0 or visible < 180:
            raise SystemExit(f"{mode} {language}: works section was not captured visibly: {target_rect}")
        cards = driver.find_elements(By.CSS_SELECTOR, "#works .book-card-cover")
        if len(cards) != 4:
            raise SystemExit(f"{mode} {language}: expected four cropped book cards, found {len(cards)}")
        for card in cards:
            box = rect(driver, card)
            ratio = box["width"] / box["height"]
            if not 0.662 <= ratio <= 0.671:
                raise SystemExit(f"{mode} {language}: book card ratio {ratio:.4f} is not 2:3")
            image = card.find_element(By.TAG_NAME, "img")
            style = driver.execute_script("return getComputedStyle(arguments[0]).objectFit", image)
            if style != "cover":
                raise SystemExit(f"{mode} {language}: book card object-fit is {style!r}")
        shot = output / f"{mode}-{language}.png"
        if not driver.save_screenshot(str(shot)):
            raise SystemExit(f"Failed to save {shot}")
        if png_dimensions(shot) != (width, height):
            raise SystemExit(f"{shot}: wrong screenshot dimensions")


def main() -> None:
    driver = build_driver()
    all_reports = []
    try:
        for mode, (width, height) in VIEWPORTS.items():
            all_reports.extend(audit_book_covers(driver, mode, width, height))
            capture_works(driver, mode, width, height)
    finally:
        driver.quit()

    if len(all_reports) != 24:
        raise SystemExit(f"Expected 24 book-cover measurements, found {len(all_reports)}")
    if len(list((ROOT / "covers").glob("*.png"))) != 24:
        raise SystemExit("Expected 24 element-level cover screenshots")
    if len(list((ROOT / "works").glob("*.png"))) != 6:
        raise SystemExit("Expected six multilingual works-section screenshots")
    print(
        "Book-cover audit passed: 12 multilingual hero covers at two viewports, "
        "forced 2:3 crop, no dual black padding bands, calibrated dark-cover "
        "variation checks, and six works-section captures."
    )


if __name__ == "__main__":
    main()
