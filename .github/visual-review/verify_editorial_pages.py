#!/usr/bin/env python3
"""Capture and verify methodology and review-status pages.

These pages are trust surfaces and were previously outside the top-page visual
matrix. The check is intentionally structural: it catches viewport escape,
clipped headings, missing target sections, and broken mobile scrolling while
also saving screenshots for human review.
"""
from __future__ import annotations

import shutil
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

BASE = "http://127.0.0.1:4173"
ROOT = Path("visual-review") / "editorial-pages"
VIEWPORTS = {
    "desktop": (1440, 1200),
    "mobile": (390, 844),
    "narrow-mobile": (360, 800),
}
PAGES = (
    ("methodology-ar", "/methodology/", ".method-list"),
    ("methodology-en", "/en/methodology/", ".method-list"),
    ("research-status-ar", "/research-status/", ".evidence-table"),
    ("research-status-en", "/en/research-status/", ".evidence-table"),
)


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


def wait_ready(driver: webdriver.Chrome) -> None:
    wait = WebDriverWait(driver, 15)
    wait.until(lambda browser: browser.execute_script("return document.readyState") == "complete")
    wait.until(
        lambda browser: browser.execute_script(
            "return Array.from(document.images).filter(i => i.getBoundingClientRect().top < innerHeight * 1.5).every(i => i.complete && i.naturalWidth > 0)"
        )
    )
    driver.set_script_timeout(15)
    driver.execute_async_script(
        """
        const done=arguments[0];
        if(document.fonts && document.fonts.ready){document.fonts.ready.then(()=>done(true),()=>done(false));}
        else{done(true);}
        """
    )
    driver.execute_script(
        "document.documentElement.style.scrollBehavior='auto';"
        "document.body.style.scrollBehavior='auto';"
        "window.scrollTo(0,0);"
    )
    time.sleep(0.12)


def rect(driver: webdriver.Chrome, element):
    return driver.execute_script(
        """
        const r=arguments[0].getBoundingClientRect();
        return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height};
        """,
        element,
    )


def assert_page_geometry(driver: webdriver.Chrome, width: int, name: str) -> None:
    metrics = driver.execute_script(
        "return {scrollWidth:document.documentElement.scrollWidth, innerWidth:innerWidth, bodyWidth:document.body.scrollWidth};"
    )
    if metrics["scrollWidth"] > width + 2 or metrics["bodyWidth"] > width + 2:
        raise SystemExit(f"{name}: horizontal page overflow at {width}px: {metrics}")
    heading = driver.find_element(By.CSS_SELECTOR, "h1")
    box = rect(driver, heading)
    if box["left"] < -1.5 or box["right"] > width + 1.5 or box["height"] <= 20:
        raise SystemExit(f"{name}: h1 escapes viewport at {width}px: {box}")


def screenshot(driver: webdriver.Chrome, path: Path, width: int, height: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not driver.save_screenshot(str(path)):
        raise SystemExit(f"Failed to save {path}")
    if path.stat().st_size < 8_000:
        raise SystemExit(f"Suspiciously small screenshot: {path}")


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    driver = build_driver()
    captures = 0
    try:
        for mode, (width, height) in VIEWPORTS.items():
            configure(driver, width, height)
            for name, route, target_selector in PAGES:
                driver.get(f"{BASE}{route}?editorial_visual_gate=1")
                wait_ready(driver)
                assert_page_geometry(driver, width, f"{mode}/{name}")
                screenshot(driver, ROOT / mode / f"{name}-top.png", width, height)
                captures += 1

                target = driver.find_element(By.CSS_SELECTOR, target_selector)
                driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center',inline:'nearest',behavior:'auto'});",
                    target,
                )
                time.sleep(0.12)
                box = rect(driver, target)
                visible = max(0.0, min(float(height), box["bottom"]) - max(0.0, box["top"]))
                if float(driver.execute_script("return window.scrollY")) <= 0 or visible < 100:
                    raise SystemExit(f"{mode}/{name}: target not visibly captured: {box}")
                assert_page_geometry(driver, width, f"{mode}/{name}-target")
                screenshot(driver, ROOT / mode / f"{name}-target.png", width, height)
                captures += 1
    finally:
        driver.quit()

    expected = len(VIEWPORTS) * len(PAGES) * 2
    if captures != expected:
        raise SystemExit(f"Expected {expected} captures, produced {captures}")
    print(f"Editorial-page visual gate passed: {captures} screenshots across methodology and research-status pages.")


if __name__ == "__main__":
    main()
