#!/usr/bin/env python3
"""Execute the visual runner with viewport-aware readiness and target scrolling.

Below-the-fold images are intentionally lazy-loaded, so the runner waits only
for images that can affect the current viewport. Targeted footer/contact
captures also override smooth scrolling and wait for the target to become
visibly positioned before taking a screenshot.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

MODULE_PATH = Path(__file__).with_name("run_visual_review.py")
SPEC = importlib.util.spec_from_file_location("site_visual_review", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise SystemExit(f"Unable to load {MODULE_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def wait_for_visible_page(driver) -> None:
    wait = WebDriverWait(driver, MODULE.WAIT_SECONDS)
    wait.until(lambda browser: browser.execute_script("return document.readyState") == "complete")
    try:
        wait.until(
            lambda browser: browser.execute_script(
                """
                const priority = new Set([
                  ...document.querySelectorAll('.hero-portrait img, .profile-portrait img, .book-hero-cover img, img[fetchpriority="high"]')
                ]);
                const limit = window.innerHeight * 1.5;
                const relevant = [...document.images].filter(image => {
                  const rect = image.getBoundingClientRect();
                  return priority.has(image) || (rect.bottom >= -40 && rect.top <= limit);
                });
                return relevant.every(image => image.complete && image.naturalWidth > 0);
                """
            )
        )
    except TimeoutException as exc:
        state = driver.execute_script(
            """
            return [...document.images].map(image => {
              const rect = image.getBoundingClientRect();
              return {
                src:image.currentSrc || image.src,
                loading:image.loading,
                complete:image.complete,
                naturalWidth:image.naturalWidth,
                top:Math.round(rect.top),
                bottom:Math.round(rect.bottom)
              };
            });
            """
        )
        raise SystemExit(
            f"Timed out waiting for viewport images on {driver.current_url}: {state}"
        ) from exc

    driver.set_script_timeout(MODULE.WAIT_SECONDS)
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
    except TimeoutException as exc:
        raise SystemExit(f"Timed out waiting for fonts on {driver.current_url}") from exc

    driver.execute_script(
        "document.documentElement.style.scrollBehavior='auto';"
        "document.body.style.scrollBehavior='auto';"
        "window.scrollTo(0,0);"
    )
    time.sleep(0.15)


def render_targets_instant(driver, mode: str, width: int, height: int):
    MODULE.configure_viewport(driver, width, height)
    reports = []
    for name, route, selector, alignment in MODULE.TARGET_PAGES:
        MODULE.open_page(driver, route, f"target-{mode}")
        element = driver.find_element(By.CSS_SELECTOR, selector)
        driver.execute_script(
            """
            document.documentElement.style.scrollBehavior = 'auto';
            document.body.style.scrollBehavior = 'auto';
            arguments[0].scrollIntoView({block:arguments[1], inline:'nearest', behavior:'auto'});
            """,
            element,
            alignment,
        )

        wait = WebDriverWait(driver, MODULE.WAIT_SECONDS)
        try:
            wait.until(
                lambda browser: browser.execute_script(
                    """
                    const r = arguments[0].getBoundingClientRect();
                    const visible = Math.max(0, Math.min(innerHeight, r.bottom) - Math.max(0, r.top));
                    return window.scrollY > 0 && visible >= Math.min(180, Math.max(80, r.height * .45));
                    """,
                    element,
                )
            )
        except TimeoutException as exc:
            state = driver.execute_script(
                """
                const r = arguments[0].getBoundingClientRect();
                return {
                  scrollY:window.scrollY,
                  innerHeight:innerHeight,
                  documentHeight:document.documentElement.scrollHeight,
                  target:{top:r.top,bottom:r.bottom,height:r.height}
                };
                """,
                element,
            )
            raise SystemExit(f"{mode} {name}: target did not enter viewport: {state}") from exc

        if alignment == "start":
            driver.execute_script("window.scrollBy({top:-20,left:0,behavior:'auto'})")
            time.sleep(0.1)

        rect = MODULE.rounded_rect(driver, element)
        scroll_y = float(driver.execute_script("return window.scrollY"))
        visible = max(0.0, min(float(height), rect["bottom"]) - max(0.0, rect["top"]))
        required = min(180.0, max(80.0, rect["height"] * 0.45))
        if scroll_y <= 0:
            raise SystemExit(f"{mode} {name}: targeted capture did not scroll")
        if visible < required:
            raise SystemExit(
                f"{mode} {name}: target visibility {visible} < {required}; rect={rect}"
            )

        reports.append(
            {
                "name": name,
                "route": route,
                "selector": selector,
                "alignment": alignment,
                "scrollY": round(scroll_y, 2),
                "viewport": {"width": width, "height": height},
                "target": rect,
                "visibleHeight": round(visible, 2),
            }
        )
        MODULE.screenshot(driver, MODULE.ROOT / mode / f"{name}.png", width, height)

    (MODULE.ROOT / "targets" / f"{mode}.json").write_text(
        json.dumps(reports, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return reports


MODULE.wait_for_page = wait_for_visible_page
MODULE.render_targets = render_targets_instant
MODULE.main()
