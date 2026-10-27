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
    ("umm-abbas-eye-ar", "/articles/evil-eye-envy-signs/", ".references"),
    ("umm-abbas-eye-opening-ar", "/articles/evil-eye-envy-signs/", "#answer"),
    ("umm-abbas-photo-ar", "/articles/magic-with-personal-photo/", ".references"),
    ("umm-abbas-photo-opening-ar", "/articles/magic-with-personal-photo/", "#answer"),
    ("umm-abbas-qarin-ar", "/articles/qarin-islam-thoughts-control/", ".references"),
    ("umm-abbas-qarin-opening-ar", "/articles/qarin-islam-thoughts-control/", "#answer"),
    ("umm-abbas-sprinkled-ar", "/articles/sprinkled-magic-water-door-evidence/", ".references"),
    ("umm-abbas-sprinkled-opening-ar", "/articles/sprinkled-magic-water-door-evidence/", "#answer"),
    ("umm-abbas-love-ar", "/articles/love-magic-reconciliation-ruling/", ".references"),
    ("umm-abbas-love-opening-ar", "/articles/love-magic-reconciliation-ruling/", "#answer"),
    ("umm-abbas-dreams-ar", "/articles/jinn-dream-fear-meaning/", ".references"),
    ("umm-abbas-dreams-opening-ar", "/articles/jinn-dream-fear-meaning/", "#answer"),
    ("umm-abbas-shams-ar", "/articles/shams-al-maarif-truth-reading-ruling/", ".references"),
    ("umm-abbas-shams-opening-ar", "/articles/shams-al-maarif-truth-reading-ruling/", "#answer"),
    ("related-certainty-en", "/en/articles/how-certainty-becomes-violence/", ".related-panel"),
    ("related-light-en", "/en/articles/iron-fire-light-matter-energy/", "#related-reading"),
    ("related-concepts-en", "/en/articles/teaching-names-ai-understanding/", "#related-reading"),
    ("related-rivers-en", "/en/articles/river-civilizations-water-state/", "#related-reading"),
    ("related-justice-en", "/en/articles/water-civilization-power/", "#related-reading"),
    ("related-comparison-en", "/en/articles/anzalna-iron-meteorites/", ".notice-box:has(#related-reading)"),
    ("reader-answer-ai-ar", "/articles/ai-soul-consciousness-understanding-taklif/", "#answer"),
    ("reader-answer-ai-en", "/en/articles/ai-soul-consciousness-understanding-taklif/", "#answer"),
    ("reader-answer-concepts-ar", "/articles/how-concepts-form-adam-names-scientific-models/", "#answer"),
    ("reader-answer-concepts-en", "/en/articles/how-concepts-form-adam-names-scientific-models/", "#answer"),
    ("reader-method-ar", "/articles/quran-science-method-evidence/", "#answer"),
    ("reader-method-en", "/en/articles/quran-science-method-evidence/", "#answer"),
    ("reader-ratq-sources-en", "/en/articles/ratq-fatq-big-bang/evidence/", "#direct-sources + ul"),
    ("ratq-book-path-en", "/en/articles/ratq-fatq-big-bang/", ".related-work"),
    ("teaching-book-path-en", "/en/articles/teaching-names-ai-understanding/", ".related-work"),
    ("expansion-certainty-en", "/en/articles/universe-expansion-wa-inna-lamusiun/", "#certainty + .table-scroll"),
    ("ratq-table-en", "/en/articles/ratq-fatq-big-bang/", ".table-scroll"),
    ("teaching-claims-en", "/en/articles/teaching-names-ai-understanding/", "#claims + .table-scroll"),
    ("teaching-matrix-en", "/en/articles/teaching-names-ai-understanding/", "#matrix + p + .table-scroll"),
    ("teaching-glossary-en", "/en/articles/teaching-names-ai-understanding/", ".table-scroll"),
    ("teaching-names-ai-understanding-en", "/en/articles/teaching-names-ai-understanding/", ".references"),
    ("ratq-fatq-big-bang-en", "/en/articles/ratq-fatq-big-bang/", ".references"),
    ("human-embryo-quran-stages-en", "/en/articles/human-embryo-quran-stages/", ".references"),
    ("jinn-demons-quran-bible-torah-en", "/en/articles/jinn-demons-quran-bible-torah/", ".references"),
    ("universe-expansion-wa-inna-lamusiun-en", "/en/articles/universe-expansion-wa-inna-lamusiun/", ".references"),
    ("hegra-diagram-en", "/en/articles/madain-salih-thamud-nabataean-tombs/", "figure"),
    ("water-power-toc-en", "/en/articles/water-civilization-power/", ".article-layout > .toc"),
    ("water-civilization-power-en", "/en/articles/water-civilization-power/", ".references"),
    ("nile-ancient-egypt-flood-calendar-state-en", "/en/articles/nile-ancient-egypt-flood-calendar-state/", ".references"),
    ("madain-salih-thamud-nabataean-tombs-en", "/en/articles/madain-salih-thamud-nabataean-tombs/", ".references"),
    ("six-days-creation-cosmic-time-en", "/en/articles/six-days-creation-cosmic-time/", ".references"),
    ("quran-day-thousand-fifty-thousand-years-relativity-en", "/en/articles/quran-day-thousand-fifty-thousand-years-relativity/", ".references"),
    ("writing-changed-human-history-en", "/en/articles/writing-changed-human-history/", ".references"),

    ("injustice-fall-of-states-quran-history-en", "/en/articles/injustice-fall-of-states-quran-history/", ".references"),
    ("iron-fire-light-matter-energy-en", "/en/articles/iron-fire-light-matter-energy/", ".references"),
    ("marib-dam-sayl-al-arim-en", "/en/articles/marib-dam-sayl-al-arim/", ".references"),

    ("method-evidence-table-en", "/en/articles/quran-science-method-evidence/", ".table-scroll"),
    ("method-evidence-sources-en", "/en/articles/quran-science-method-evidence/", ".references"),
    ("dna-information-en", "/en/articles/dna-code-genetic-information/", ".references"),
    ("baghdad-sources-en", "/en/articles/fall-of-baghdad-1258-ibn-al-alqami/", "#core-sources-for-this-draft + ul"),
    ("certainty-violence-en", "/en/articles/how-certainty-becomes-violence/", "#references + ol"),
    ("civilization-collapse-en", "/en/articles/civilization-knowledge-justice-collapse/", ".references"),
    ("possession-or-disorder-en", "/en/articles/possession-or-neurological-psychological-disorder/", ".references"),
    ("diagnostic-uncertainty-en", "/en/articles/diagnostic-uncertainty-family-fear-coercive-authority/", ".references"),
    ("umm-abbas-book-ar", "/books/umm-abbas/", "#research"),
    ("umm-abbas-hexagram-ar", "/articles/hexagram-magic-seal-of-solomon-umm-abbas/", ".references"),
    ("umm-abbas-cyberbullying-ar", "/articles/cyberbullying-university-rumor-stigma/", ".references"),
    ("umm-abbas-cyberbullying-en", "/en/articles/cyberbullying-university-rumor-stigma/", ".references"),
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
    ("umm-abbas-voices-en", "/en/articles/hearing-voices-in-head/", ".references"),
    ("umm-abbas-functional-seizures-en", "/en/articles/functional-seizures-vs-epilepsy/", ".references"),
    ("umm-abbas-sleepwalking-en", "/en/articles/sleepwalking-why-no-memory/", ".references"),
    ("umm-abbas-hexagram-en", "/en/articles/hexagram-magic-seal-of-solomon-umm-abbas/", ".references"),
    ("juhayman-evidence-en", "/en/articles/juhayman-grand-mosque-1979/", "table"),
    ("umm-abbas-fear-symptoms-en", "/en/articles/fear-physical-symptoms-umm-abbas/", ".references"),
    ("umm-abbas-memory-gaps-en", "/en/articles/memory-gaps-unremembered-actions/", ".references"),
    ("umm-abbas-jinn-ar", "/articles/jinn-existence-quran-sunnah/", ".references"),
    ("umm-abbas-jinn-en", "/en/articles/jinn-existence-quran-sunnah/", ".references"),
    ("sirou-turing-ar", "/articles/turing-test-ai-consciousness/", ".references"),
    ("sirou-turing-en", "/en/articles/turing-test-ai-consciousness/", ".references"),
    ("umm-abbas-family-ar", "/articles/umm-abbas-family-fear/", ".related-work"),
    ("umm-abbas-family-en", "/en/articles/umm-abbas-family-fear/", ".related-work"),
    ("umm-abbas-family-de", "/de/articles/umm-abbas-family-fear/", ".related-work"),
    ("research-status-ar", "/research-status/", ".evidence-table"),
    ("research-status-en", "/en/research-status/", ".evidence-table"),
    ("mesopotamia-salinity-ar", "/articles/mesopotamia-irrigation-soil-salinity-collapse/", ".source-list"),
    ("iron-meteorites-en", "/en/articles/anzalna-iron-meteorites/", ".references"),
    ("mesopotamia-salinity-en", "/en/articles/mesopotamia-irrigation-soil-salinity-collapse/", ".source-list"),
    ("nile-egypt-ar", "/articles/nile-ancient-egypt-flood-calendar-state/", ".source-list"),
    ("ratq-fatq-ar", "/articles/ratq-fatq-big-bang/", ".table-scroll"),
    ("sirou-before-big-bang-en", "/en/articles/before-big-bang-science-limits/", ".references"),
    ("six-days-creation-ar", "/articles/six-days-creation-cosmic-time/", ".references"),
    ("universe-expansion-ar", "/articles/universe-expansion-wa-inna-lamusiun/", ".table-scroll"),
    ("water-life-ar", "/articles/water-life-molecular-properties/", ".references"),
    ("water-life-en", "/en/articles/water-life-molecular-properties/", ".references"),
    ("sirou-green-tree-ar", "/articles/green-tree-fire-photosynthesis/", ".references"),
    ("sirou-green-tree-en", "/en/articles/green-tree-fire-photosynthesis/", ".references"),
    ("concepts-models-ar", "/articles/how-concepts-form-adam-names-scientific-models/", ".references"),
    ("concepts-models-en", "/en/articles/how-concepts-form-adam-names-scientific-models/", ".references"),
    ("light-nur-ar", "/articles/difference-light-nur-quran-sun-moon/", ".references"),
    ("light-nur-en", "/en/articles/difference-light-nur-quran-sun-moon/", ".references"),
    ("ai-soul-taklif-ar", "/articles/ai-soul-consciousness-understanding-taklif/", ".references"),
    ("ai-soul-taklif-en", "/en/articles/ai-soul-consciousness-understanding-taklif/", ".references"),
    ("khufu-merer-ar", "/articles/how-khufu-pyramid-built-merer-diary/", ".references"),
    ("khufu-merer-en", "/en/articles/how-khufu-pyramid-built-merer-diary/", ".references"),
    ("spiritual-healing-safety-ar", "/articles/spiritual-healing-exploitation-safeguarding/", ".references"),
    ("spiritual-healing-safety-en", "/en/articles/spiritual-healing-exploitation-safeguarding/", ".references"),
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


def verify_reading_controls(driver: webdriver.Chrome, width: int, height: int, mode: str) -> None:
    """Check the two article layouts, native disclosure, anchors and progress."""
    from selenium.webdriver.common.keys import Keys
    routes = (
        ("ar", "/articles/difference-light-nur-quran-sun-moon/"),
        ("en", "/en/articles/water-civilization-power/"),
        ("de", "/de/articles/possession-or-neurological-psychological-disorder/"),
    )
    for lang, route in routes:
        driver.get(f"{BASE}{route}?reading_controls_gate=1")
        wait_ready(driver)
        for reject in driver.find_elements(By.CSS_SELECTOR, "#analytics-consent button[data-consent='denied']"):
            reject.click()
        details = driver.find_element(By.CSS_SELECTOR, ".reading-contents")
        summary = details.find_element(By.TAG_NAME, "summary")
        assert bool(details.get_property("open")) == (width > 1000), f"{mode}/{lang}: wrong initial TOC state"
        if width <= 1000:
            assert rect(driver, summary)["height"] >= 44
            summary.send_keys(Keys.SPACE)
            WebDriverWait(driver, 5).until(lambda _: details.get_property("open"))
        links = details.find_elements(By.CSS_SELECTOR, "a[href^='#']")
        assert len(links) >= 3, f"{mode}/{lang}: contents lost"
        # A long mobile contents list has its own scroll area. Verify every
        # entry after scrolling it into view, rather than demanding that all
        # entries fit in the same viewport at once.
        for item in links:
            assert item.get_attribute("textContent").strip(), f"{mode}/{lang}: empty contents link"
            visible = driver.execute_script(
                "arguments[0].scrollIntoView({block:'nearest',inline:'nearest',behavior:'auto'});"
                "const r=arguments[0].getBoundingClientRect();"
                "const list=arguments[0].closest('ol,ul,.reading-contents-links').getBoundingClientRect();"
                "return r.width>0 && r.height>0 && r.bottom>Math.max(0,list.top) && r.top<Math.min(innerHeight,list.bottom);", item)
            assert visible, f"{mode}/{lang}: contents link cannot be reached: {item.get_attribute('href')}"
        driver.execute_script("arguments[0].scrollIntoView({block:'nearest',behavior:'auto'});", links[0])
        screenshot(driver, ROOT / mode / f"reading-{lang}-contents.png", width, height)
        link = links[2]
        target_id = link.get_attribute("href").split("#", 1)[1]
        driver.execute_script("arguments[0].scrollIntoView({block:'center',behavior:'auto'});", link)
        link.click()
        WebDriverWait(driver, 5).until(lambda _: driver.current_url.endswith("#" + target_id))
        if width <= 1000:
            assert not details.get_property("open"), f"{mode}/{lang}: TOC did not close after selection"
        target = driver.find_element(By.ID, target_id)
        WebDriverWait(driver, 5).until(lambda browser: browser.execute_script(
            "const r=arguments[0].getBoundingClientRect();const h=document.querySelector('.site-header').getBoundingClientRect().height;return r.top>=h-2 && r.top<innerHeight;", target))
        WebDriverWait(driver, 5).until(lambda _: link.get_attribute("aria-current") == "location")
        WebDriverWait(driver, 5).until(lambda browser: browser.execute_script(
            "return parseFloat(getComputedStyle(document.querySelector('.reading-progress span')).transform.slice(7)) > 0"))
        assert_page_geometry(driver, width, f"{mode}/reading-{lang}")
        screenshot(driver, ROOT / mode / f"reading-{lang}-section.png", width, height)


def verify_native_reading_stability(driver, width, height, mode):
    """A late reading-control script must not move already-painted prose."""
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled": True})
    driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": ["*assets/mobile-reading.js*"]})
    try:
        driver.get(f"{BASE}/articles/sleep-paralysis-jathoom/?native_contents_gate=1")
        wait_ready(driver)
        assert not driver.find_elements(By.CSS_SELECTOR, ".reading-progress"), f"{mode}: enhancement was not isolated"
        details = driver.find_element(By.CSS_SELECTOR, ".toc > details.reading-contents")
        summary = details.find_element(By.TAG_NAME, "summary")
        assert not details.get_property("open"), f"{mode}: native disclosure should start closed"
        # Native controls remain usable even if enhancement never arrives.
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", summary)
        summary.click()
        assert details.get_property("open"), f"{mode}: contents needs JavaScript to open"
        summary.click()
        article = driver.find_element(By.CSS_SELECTOR, ".article-body")
        before = driver.execute_script("return arguments[0].getBoundingClientRect().top + scrollY", article)
        driver.execute_script(Path("assets/mobile-reading.js").read_text())
        driver.execute_async_script("const done=arguments[0];requestAnimationFrame(()=>requestAnimationFrame(done));")
        after = driver.execute_script("return arguments[0].getBoundingClientRect().top + scrollY", article)
        assert abs(after - before) <= 1, f"{mode}: late enhancement moved prose by {after-before}px"
        assert len(driver.find_elements(By.CSS_SELECTOR, ".toc .reading-contents")) == 1
        assert len(driver.find_elements(By.CSS_SELECTOR, ".reading-progress")) == 1
        assert bool(details.get_property("open")) == (width > 1000)
        for link in driver.find_elements(By.CSS_SELECTOR, ".breadcrumbs a"):
            line = driver.execute_script("return getComputedStyle(arguments[0]).textDecorationLine", link)
            assert "underline" in line, f"{mode}: breadcrumb still relies only on color"
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", summary)
        screenshot(driver, ROOT / mode / "native-reading-stability-ar.png", width, height)
    finally:
        driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": []})
        driver.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled": False})


def verify_author_home(driver, width, height, mode, route):
    """Verify the actual mobile journey, rather than requiring the old layout."""
    language = 'ar' if route == '/' else 'en'
    reject = driver.find_elements(By.CSS_SELECTOR, '#analytics-consent [data-consent="denied"]')
    if reject:
        reject[0].click()
    assert_page_geometry(driver, width, f'{mode}/author-home-{language}')
    assert len(driver.find_elements(By.CSS_SELECTOR, '.author-book')) == 4
    links = driver.find_elements(By.CSS_SELECTOR, '.selected-reading-list h3 a')
    assert len(links) == 3
    for link in links:
        assert rect(driver, link)['height'] >= 44, f'{mode}/{language}: small reading target'
    actions = driver.find_element(By.CSS_SELECTOR, '.home-hero .actions')
    assert rect(driver, actions)['bottom'] < height, f'{mode}/{language}: introduction pushes main actions below fold'
    secondary = driver.find_element(By.CSS_SELECTOR, '.home-hero .btn:not(.primary)')
    color = driver.execute_script('return getComputedStyle(arguments[0]).color', secondary)
    assert color == 'rgb(20, 26, 34)', f'{mode}/{language}: unreadable secondary action: {color}'
    screenshot(driver, ROOT / mode / f'author-home-{language}-top.png', width, height)
    secondary.click()
    WebDriverWait(driver, 5).until(lambda _: driver.current_url.endswith('#works'))
    target = driver.find_element(By.ID, 'works')
    header = driver.find_element(By.CSS_SELECTOR, '.site-header')
    WebDriverWait(driver, 5).until(lambda _: rect(driver, target)['top'] >= rect(driver, header)['bottom'] - 2)
    screenshot(driver, ROOT / mode / f'author-home-{language}-books.png', width, height)
    reading = driver.find_element(By.ID, 'selected-reading')
    driver.execute_script("arguments[0].scrollIntoView({block:'start',behavior:'auto'});", reading)
    assert_page_geometry(driver, width, f'{mode}/author-home-{language}-reading')
    screenshot(driver, ROOT / mode / f'author-home-{language}-reading.png', width, height)
    footer = driver.find_element(By.ID, 'site-footer')
    driver.execute_script("arguments[0].scrollIntoView({block:'end',behavior:'auto'});", footer)
    screenshot(driver, ROOT / mode / f'author-home-{language}-footer.png', width, height)


def verify_shared_palette(driver, width, height, mode):
    """Keep the home masthead/paper/footer aligned with the internal pages."""
    routes = (
        ('library-ar', '/articles/'), ('home-ar', '/'), ('home-en', '/en/'),
        ('home-de', '/de/'), ('library-en', '/en/articles/'),
        ('books-ar', '/books/'), ('books-en', '/en/books/'),
        ('book-ar', '/books/umm-abbas/'), ('book-en', '/en/books/umm-abbas/'),
        ('about-ar', '/about/'), ('research-ar', '/research-status/'),
        ('report-ar', '/articles/sleep-paralysis-jathoom/'),
        ('report-en', '/en/articles/juhayman-grand-mosque-1979/'),
        ('literary-ar', '/articles/hexagram-magic-seal-of-solomon-umm-abbas/'),
    )
    reference = None
    for name, route in routes:
        driver.get(f'{BASE}{route}?shared_palette_gate=1')
        wait_ready(driver)
        for reject in driver.find_elements(By.CSS_SELECTOR, '#analytics-consent [data-consent="denied"]'):
            reject.click()
        colors = driver.execute_script("""
            const style = selector => getComputedStyle(document.querySelector(selector));
            return {header:style('.site-header').backgroundColor,
                    footer:style('.site-footer').backgroundColor,
                    paper:style('body').backgroundColor,ink:style('body').color};
        """)
        if reference is None:
            reference = colors
        assert colors['header'] == reference['header'], f'{mode}/{name}: masthead palette drift: {colors}'
        assert colors['footer'] == reference['footer'], f'{mode}/{name}: footer palette drift: {colors}'
        if name.startswith('home-'):
            assert colors['paper'] == reference['paper'] and colors['ink'] == reference['ink'], f'{mode}/{name}: home paper/ink differ from the library: {colors}'
        assert_page_geometry(driver, width, f'{mode}/palette-{name}')
        nav = driver.find_element(By.CSS_SELECTOR, '.nav')
        if width <= 640:
            brand = driver.find_element(By.CSS_SELECTOR, '.brand')
            assert rect(driver, nav)['top'] >= rect(driver, brand)['bottom'] - 2, f'{mode}/{name}: navigation overlaps identity row'
            for link in nav.find_elements(By.TAG_NAME, 'a'):
                box = rect(driver, link)
                assert box['height'] >= 44 and box['left'] >= -1 and box['right'] <= width + 1, f'{mode}/{name}: navigation target clipped or too small: {box}'
        screenshot(driver, ROOT / mode / f'author-home-{name}-palette.png', width, height)


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    driver = build_driver()
    captures = 0
    try:
        for mode, (width, height) in VIEWPORTS.items():
            configure(driver, width, height)
            verify_reading_controls(driver, width, height, mode)
            verify_native_reading_stability(driver, width, height, mode)
            verify_shared_palette(driver, width, height, mode)
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
                if home in {'/', '/en/'}:
                    verify_author_home(driver, width, height, mode, home)
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
                # Targeted TOC screenshots exercise the new mobile disclosure.
                for details in target.find_elements(By.CSS_SELECTOR, ".reading-contents"):
                    if not details.get_property("open"):
                        details.find_element(By.TAG_NAME, "summary").click()
                driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center',inline:'nearest',behavior:'auto'});",
                    target,
                )
                time.sleep(0.12)
                box = rect(driver, target)
                visible = max(0.0, min(float(height), box["bottom"]) - max(0.0, box["top"]))
                if name.startswith("related-"):
                    # A valid one-link reading block can be shorter than 100px.
                    # Require its full visible area and every new link on screen.
                    if float(driver.execute_script("return window.scrollY")) <= 0 or visible < min(100, box["height"]) - .5:
                        raise SystemExit(f"{mode}/{name}: reading block clipped: {box}")
                    new_links = driver.find_elements(By.CSS_SELECTOR, "#related-reading a")
                    assert new_links, f"{mode}/{name}: added reading links missing"
                    header_height = driver.execute_script("return document.querySelector('.site-header').getBoundingClientRect().height")
                    for link in new_links:
                        link_box = rect(driver, link)
                        assert link_box["left"] >= -1 and link_box["right"] <= width + 1, f"{mode}/{name}: clipped reading link"
                        assert link_box["top"] >= header_height - 1 and link_box["bottom"] <= height + 1, f"{mode}/{name}: reading link outside capture"
                        assert "/en/articles/" in link.get_attribute("href") and link.text.strip(), f"{mode}/{name}: wrong reading destination"
                elif float(driver.execute_script("return window.scrollY")) <= 0 or visible < 100:
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
