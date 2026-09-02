#!/usr/bin/env python3
"""Execute the visual runner with viewport-aware image readiness.

Below-the-fold images are intentionally lazy-loaded. Waiting for every image on
a long research page never terminates until the page is scrolled. This wrapper
keeps the strict browser checks while waiting only for images that affect the
current viewport, plus the explicit hero/profile/book-cover images.
"""
from __future__ import annotations

import importlib.util
import sys
import time
from pathlib import Path

from selenium.common.exceptions import TimeoutException
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

    driver.execute_script("window.scrollTo(0, 0)")
    time.sleep(0.15)


MODULE.wait_for_page = wait_for_visible_page
MODULE.main()
