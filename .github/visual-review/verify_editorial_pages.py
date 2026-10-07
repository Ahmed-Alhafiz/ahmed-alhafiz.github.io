#!/usr/bin/env python3
"""Capture and verify editorial pages and multilingual library behavior.

These trust surfaces sit outside the top-page visual matrix. The check is
intentionally structural: it catches viewport escape,
clipped headings, missing target sections, and broken mobile scrolling while
also saving screenshots for human review.
"""
from __future__ import annotations

import shutil
import time
import json
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
    ("umm-abbas-book-ar", "/books/umm-abbas/", "#research"),
    ("umm-abbas-hexagram-ar", "/articles/hexagram-magic-seal-of-solomon-umm-abbas/", ".references"),
    ("umm-abbas-cyberbullying-ar", "/articles/cyberbullying-university-rumor-stigma/", ".references"),
    ("umm-abbas-fear-ar", "/articles/fear-physical-symptoms-umm-abbas/", ".references"),
    ("umm-abbas-sleepwalking-ar", "/articles/sleepwalking-why-no-memory/", ".references"),
    ("umm-abbas-intrusive-ar", "/articles/unwanted-intrusive-thoughts-meaning/", ".references"),
    ("umm-abbas-intrusive-en", "/en/articles/unwanted-intrusive-thoughts-meaning/", ".references"),
    ("umm-abbas-sleep-paralysis-en", "/en/articles/sleep-paralysis-jathoom/", ".references"),
    ("umm-abbas-religious-ocd-en", "/en/articles/religious-ocd-scrupulosity/", ".references"),
    ("umm-abbas-dpdr-ar", "/articles/depersonalization-derealization-feeling-unreal/", ".references"),
    ("umm-abbas-dpdr-en", "/en/articles/depersonalization-derealization-feeling-unreal/", ".references"),
    ("umm-abbas-scriptures-ar", "/articles/jinn-demons-quran-bible-torah/", ".table-scroll"),
    ("umm-abbas-memory-ar", "/articles/memory-gaps-unremembered-actions/", ".table-scroll"),
    ("umm-abbas-voices-ar", "/articles/hearing-voices-in-head/", ".table-scroll"),
    ("umm-abbas-jinn-ar", "/articles/jinn-existence-quran-sunnah/", ".references"),
    ("umm-abbas-family-ar", "/articles/umm-abbas-family-fear/", ".related-work"),
    ("umm-abbas-family-en", "/en/articles/umm-abbas-family-fear/", ".related-work"),
    ("umm-abbas-family-de", "/de/articles/umm-abbas-family-fear/", ".related-work"),
    ("research-status-ar", "/research-status/", ".evidence-table"),
    ("research-status-en", "/en/research-status/", ".evidence-table"),
    ("mesopotamia-salinity-ar", "/articles/mesopotamia-irrigation-soil-salinity-collapse/", ".source-list"),
    ("nile-egypt-ar", "/articles/nile-ancient-egypt-flood-calendar-state/", ".source-list"),
    ("ratq-fatq-ar", "/articles/ratq-fatq-big-bang/", ".table-scroll"),
    ("six-days-creation-ar", "/articles/six-days-creation-cosmic-time/", ".references"),
    ("universe-expansion-ar", "/articles/universe-expansion-wa-inna-lamusiun/", ".table-scroll"),
    ("water-life-ar", "/articles/water-life-molecular-properties/", ".references"),
    ("concepts-models-ar", "/articles/how-concepts-form-adam-names-scientific-models/", ".references"),
    ("light-nur-ar", "/articles/difference-light-nur-quran-sun-moon/", ".references"),
    ("ai-soul-taklif-ar", "/articles/ai-soul-consciousness-understanding-taklif/", ".references"),
    ("library-ar", "/articles/", "#topic-history"),
    ("library-en", "/en/articles/", "#topic-history"),
    ("library-de", "/de/articles/", "#topic-psychology"),
    ("madain-evidence-ar", "/articles/madain-salih-thamud-nabataean-tombs/", 'img[src$="madain-salih-evidence-map-ar.svg"]'),
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


def verify_library(driver: webdriver.Chrome, route: str, name: str, width: int) -> None:
    """Exercise filtering, reset, RTL/LTR and the readable no-script fallback."""
    from urllib.parse import urlparse
    lang = driver.find_element(By.CSS_SELECTOR, "html").get_attribute("lang")
    prefix = "" if lang == "ar" else lang + "/"
    feed = json.loads(Path(prefix, "articles/feed.json").read_text())["items"]
    expected = {urlparse(item["url"]).path for item in feed}
    actual = {urlparse(link.get_attribute("href")).path for link in driver.find_elements(By.CSS_SELECTOR, ".library-entry h3 a")}
    assert expected == actual, f"{name}: visible library does not match published feed"
    ordered_links = driver.find_elements(By.CSS_SELECTOR, ".library-entry h3 a")
    schema = driver.execute_script("return Array.from(document.querySelectorAll('script[type=\"application/ld+json\"]')).flatMap(s=>JSON.parse(s.textContent)['@graph']||[]).filter(n=>n['@type']==='ItemList')")
    assert len(schema) == 1
    items = schema[0]["itemListElement"]
    assert schema[0]["numberOfItems"] == len(ordered_links) == len(items)
    assert {v["url"] for v in items} == {v["url"] for v in feed}, f"{name}: schema must use canonical published URLs"
    # Selenium serves the pages on localhost; compare routes for visible links.
    assert [(v["position"], urlparse(v["url"]).path, v["name"]) for v in items] == [(pos, urlparse(link.get_attribute("href")).path, link.text) for pos, link in enumerate(ordered_links, 1)], f"{name}: ItemList differs from visible order/title"
    assert driver.find_element(By.CSS_SELECTOR, "html").get_attribute("dir") == ("rtl" if lang == "ar" else "ltr")
    reject = driver.find_elements(By.CSS_SELECTOR, "#analytics-consent button[data-consent='denied']")
    if reject:
        reject[0].click()
        WebDriverWait(driver, 5).until(lambda _: not driver.find_elements(By.ID, "analytics-consent"))
    field = driver.find_element(By.ID, "article-search")
    assert field.is_displayed(), f"{name}: search enhancement did not initialize"
    query = {"ar": "الْوَعْي", "en": "Baghdad", "de": "Bagdad"}[lang]
    visible = lambda: len([entry for entry in driver.find_elements(By.CSS_SELECTOR, ".library-entry") if entry.is_displayed()])
    field.send_keys(query)
    WebDriverWait(driver, 5).until(lambda _: 0 < visible() < len(feed))
    assert_page_geometry(driver, width, f"{name}-search")
    field.clear()
    field.send_keys("zzzz-no-matching-article-92831")
    WebDriverWait(driver, 5).until(lambda _: visible() == 0)
    assert driver.find_element(By.CSS_SELECTOR, ".library-empty").is_displayed()
    driver.find_element(By.CSS_SELECTOR, ".library-clear").click()
    WebDriverWait(driver, 5).until(lambda _: visible() == len(feed))
    assert not driver.find_element(By.CSS_SELECTOR, ".library-empty").is_displayed()
    assert field.get_attribute("value") == ""
    try:
        driver.execute_cdp_cmd("Emulation.setScriptExecutionDisabled", {"value": True})
        driver.get(f"{BASE}{route}?library_no_script_gate=1")
        assert visible() == len(feed), f"{name}: articles disappear without JavaScript"
        assert not driver.find_element(By.CSS_SELECTOR, ".library-search").is_displayed()
    finally:
        driver.execute_cdp_cmd("Emulation.setScriptExecutionDisabled", {"value": False})
    driver.get(f"{BASE}{route}?editorial_visual_gate=1")
    wait_ready(driver)


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    driver = build_driver()
    captures = 0
    try:
        for mode, (width, height) in VIEWPORTS.items():
            configure(driver, width, height)
            for home in ("/", "/en/", "/de/", "/about/", "/en/about/", "/de/about/"):
                driver.get(f"{BASE}{home}?controls_visual_gate=1")
                wait_ready(driver)
                portrait = driver.find_element(By.CSS_SELECTOR, ".hero-portrait img, .profile-portrait img")
                assert "/assets/portraits/" in portrait.get_property("currentSrc"), f"{mode}/{home}: responsive image not selected"
                # naturalWidth on a srcset image is density-corrected CSS pixels.
                # Decode the selected asset independently to measure actual pixels.
                pixels = driver.execute_async_script("const done=arguments[arguments.length-1], img=new Image(); img.onload=()=>done(img.naturalWidth); img.onerror=()=>done(0); img.src=arguments[0];", portrait.get_property("currentSrc"))
                density = driver.execute_script("return devicePixelRatio")
                assert pixels >= rect(driver, portrait)["width"] * density - 1, f"{mode}/{home}: insufficient portrait resolution"
                imports = driver.execute_script("return Array.from(document.styleSheets).filter(s=>(s.href||'').endsWith('/assets/articles.css')).flatMap(s=>Array.from(s.cssRules)).filter(r=>r.type===3).length")
                assert imports == 0, f"{mode}/{home}: nested stylesheet waterfall returned"
                for button in driver.find_elements(By.CSS_SELECTOR, ".home-hero .actions a.btn, .profile-hero .actions a.btn"):
                    assert rect(driver, button)["height"] >= 44, f"{mode}/{home}: undersized reading control"
                    radius = driver.execute_script("return parseFloat(getComputedStyle(arguments[0]).borderTopLeftRadius)", button)
                    assert radius >= 6, f"{mode}/{home}: legacy flat-link styling overrides the button"
            for name, route, target_selector in PAGES:
                driver.get(f"{BASE}{route}?editorial_visual_gate=1")
                wait_ready(driver)
                assert_page_geometry(driver, width, f"{mode}/{name}")
                screenshot(driver, ROOT / mode / f"{name}-top.png", width, height)
                captures += 1

                if name.startswith("library-"):
                    verify_library(driver, route, f"{mode}/{name}", width)
                if name == "madain-evidence-ar":
                    image = driver.find_element(By.CSS_SELECTOR, target_selector)
                    WebDriverWait(driver, 10).until(lambda browser: browser.execute_script("return arguments[0].complete && arguments[0].naturalWidth > 0", image))
                    box = rect(driver, image)
                    assert abs(box["height"] / box["width"] - 760 / 1200) < .01, f"{mode}/{name}: figure aspect ratio distorted"

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
    print(f"Editorial-page visual gate passed: {captures} screenshots across editorial pages.")


if __name__ == "__main__":
    main()
