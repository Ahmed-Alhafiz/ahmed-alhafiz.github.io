#!/usr/bin/env python3
"""Verify that Arabic navigation remains fully contained on narrow mobile widths.

This complements the visual screenshots by checking every important Arabic
surface instead of only the homepage/profile pair.
"""
from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

BASE_URL = "http://127.0.0.1:4173"
OUTPUT = Path("visual-review/sitewide-arabic-nav.json")
VIEWPORTS = ((390, 844), (360, 800))
ROUTES = (
    "/",
    "/about/",
    "/articles/",
    "/methodology/",
    "/research-status/",
    "/guides/arabic-psychological-horror/",
    "/books/sirou-fi-alard/",
    "/books/umm-abbas/",
    "/books/juhayman/",
    "/books/kitab-al-kutub/",
    "/articles/teaching-names-ai-understanding/",
    "/articles/ratq-fatq-big-bang/",
    "/articles/water-civilization-power/",
    "/articles/diagnostic-uncertainty-family-fear-coercive-authority/",
    "/articles/spiritual-healing-exploitation-safeguarding/",
    "/articles/six-days-creation-cosmic-time/",
    "/articles/sleep-paralysis-jathoom/",
    "/articles/functional-seizures-vs-epilepsy/",
)


def build_driver() -> webdriver.Chrome:
    binary = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    if not binary:
        raise SystemExit("No Chromium-compatible browser found")
    options = Options()
    options.binary_location = binary
    for arg in (
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--hide-scrollbars",
        "--disable-extensions",
        "--disable-background-networking",
        "--force-device-scale-factor=1",
    ):
        options.add_argument(arg)
    return webdriver.Chrome(options=options)


def rect(driver: webdriver.Chrome, element) -> dict[str, float]:
    return driver.execute_script(
        """
        const r=arguments[0].getBoundingClientRect();
        return {left:r.left,right:r.right,width:r.width,top:r.top,bottom:r.bottom};
        """,
        element,
    )


def main() -> None:
    driver = build_driver()
    report: list[dict] = []
    try:
        for width, height in VIEWPORTS:
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
            for route in ROUTES:
                driver.get(f"{BASE_URL}{route}?sitewide_nav_review={width}")
                for _ in range(40):
                    if driver.execute_script("return document.readyState") == "complete":
                        break
                    time.sleep(0.05)
                language = driver.execute_script("return document.documentElement.lang.toLowerCase()")
                if language.split("-")[0] != "ar":
                    raise SystemExit(f"{route}: expected Arabic document, found {language!r}")

                nav = driver.find_element(By.CSS_SELECTOR, ".site-header .nav")
                links = nav.find_elements(By.TAG_NAME, "a")
                nav_rect = rect(driver, nav)
                metrics = driver.execute_script(
                    """
                    return {
                      navScroll:arguments[0].scrollWidth,
                      navClient:arguments[0].clientWidth,
                      pageScroll:document.documentElement.scrollWidth,
                      pageClient:document.documentElement.clientWidth,
                      overflowX:getComputedStyle(arguments[0]).overflowX,
                      display:getComputedStyle(arguments[0]).display
                    };
                    """,
                    nav,
                )
                if len(links) != 5:
                    raise SystemExit(f"{route}: expected five primary links, found {len(links)}")
                if metrics["pageScroll"] > metrics["pageClient"] + 1:
                    raise SystemExit(f"{width}px {route}: page overflow {metrics}")
                if metrics["navScroll"] > metrics["navClient"] + 1:
                    raise SystemExit(f"{width}px {route}: navigation scrolls horizontally {metrics}")
                if metrics["display"] != "grid":
                    raise SystemExit(f"{width}px {route}: Arabic navigation is not the hardened grid")
                if nav_rect["left"] < -1.5 or nav_rect["right"] > width + 1.5:
                    raise SystemExit(f"{width}px {route}: navigation escapes viewport {nav_rect}")

                link_rects = [rect(driver, link) for link in links]
                for item in link_rects:
                    if item["left"] < nav_rect["left"] - 1 or item["right"] > nav_rect["right"] + 1:
                        raise SystemExit(f"{width}px {route}: navigation item clipped {item}")

                report.append(
                    {
                        "route": route,
                        "viewport": [width, height],
                        "nav": nav_rect,
                        "metrics": metrics,
                        "links": link_rects,
                    }
                )
    finally:
        driver.quit()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Site-wide Arabic mobile navigation passed: {len(ROUTES)} routes × {len(VIEWPORTS)} viewports")


if __name__ == "__main__":
    main()
