#!/usr/bin/env python3
"""Exercise multilingual navigation and real controls, beyond opening screenshots."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

BASE = 'http://127.0.0.1:4173'
OUT = Path('visual-review/interface'); OUT.mkdir(parents=True, exist_ok=True)
opts = Options()
for arg in ['--headless=new', '--no-sandbox', '--disable-dev-shm-usage', '--hide-scrollbars']:
    opts.add_argument(arg)
opts.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 15)
records = []

def open_page(route):
    driver.get(BASE + route)
    wait.until(lambda b: b.execute_script('return document.readyState') == 'complete')
    driver.execute_script("document.documentElement.style.setProperty('scroll-behavior','auto','important')")
    reject = driver.find_elements(By.CSS_SELECTOR, '#analytics-consent button[data-consent=denied]')
    if reject:
        reject[0].click()
        wait.until(lambda b: not b.find_elements(By.ID, 'analytics-consent'))

def viewport(width, height):
    driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
        'width': width, 'height': height, 'deviceScaleFactor': 1, 'mobile': False})

try:
    # Inspect every public page at the narrow mobile width. Use source URLs for
    # coverage, not a hand-picked list that could omit a translation template.
    routes = [e.text.split('ahmedalhafiz.com', 1)[1] for e in
              ET.parse('sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    viewport(360, 800)
    for route in routes:
        open_page(route)
        info = driver.execute_script('''
          const header=document.querySelector('.site-header'),nav=header.querySelector('nav');
          const links=[...header.querySelectorAll('nav a,.langs a')];
          const bounds=links.map(a=>{const r=a.getBoundingClientRect();return {text:a.innerText,left:r.left,right:r.right,height:r.height}});
          const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);
          return {route:location.pathname,width:innerWidth,scroll:document.documentElement.scrollWidth,
            header:getComputedStyle(header).backgroundColor,bounds,
            navColumns:getComputedStyle(nav).gridTemplateColumns.split(' ').length,
            duplicateIds:ids.filter((id,i)=>ids.indexOf(id)!==i),
            contact:!!document.getElementById('site-contact'),
            brokenAnchors:[...document.querySelectorAll('.reading-tools a,.toc a[href^="#"]')].filter(a=>!document.getElementById(decodeURIComponent(a.hash.slice(1)))).map(a=>a.hash)};
        ''')
        assert info['scroll'] <= 361, (route, 'horizontal overflow', info)
        assert info['header'] == 'rgba(8, 19, 30, 0.976)', (route, info['header'])
        assert info['navColumns'] == 5, (route, 'legacy navigation columns', info)
        assert info['contact'] and not info['duplicateIds'] and not info['brokenAnchors'], info
        for item in info['bounds']:
            assert item['left'] >= -1 and item['right'] <= 361 and item['height'] >= 43, (route, item)
        errors = [e for e in driver.get_log('browser') if e['level'] == 'SEVERE' and e.get('source') == 'javascript']
        assert not errors, (route, errors)
        records.append(info)
    print(f'Interface: all {len(routes)} public pages passed at 360px', flush=True)

    # Same header and language controls at three widths, including 320px zoom-like layout.
    for width, height in [(320, 800), (390, 844), (1440, 1000)]:
        viewport(width, height)
        for prefix, lang in [('', 'ar'), ('/en', 'en'), ('/de', 'de'), ('/id', 'id')]:
            open_page(prefix + '/')
            nav = driver.find_element(By.CSS_SELECTOR, 'header nav')
            assert len(nav.find_elements(By.TAG_NAME, 'a')) == 5
            assert len(driver.find_elements(By.CSS_SELECTOR, 'header .langs a')) == 4
            assert driver.execute_script('return document.documentElement.scrollWidth<=innerWidth+1')
            primary = driver.find_element(By.CSS_SELECTOR, '.home-hero .btn.primary')
            assert primary.value_of_css_property('background-color') == 'rgba(16, 38, 58, 1)'
            # A real click must reach a visible contact target on this same page.
            nav.find_element(By.CSS_SELECTOR, 'a[href="#site-contact"]').click()
            wait.until(lambda b: b.execute_script('const r=document.getElementById("site-contact").getBoundingClientRect();return r.top<innerHeight&&r.bottom>0'))
            driver.save_screenshot(str(OUT / f'{lang}-{width}-contact.png'))
            # Test an actual language link rather than only comparing hreflang.
            switch = driver.find_element(By.CSS_SELECTOR, 'header .langs a[hreflang=en]')
            # Production uses a mix of absolute and relative canonical links;
            # map only the origin in the fixture so the click tests this build.
            driver.execute_script('arguments[0].href=new URL(arguments[0].href).pathname', switch)
            switch.click()
            wait.until(lambda b: b.find_element(By.TAG_NAME, 'html').get_attribute('lang') == 'en')

    viewport(390, 844)
    for route in ['/articles/difference-light-nur-quran-sun-moon/',
                  '/en/articles/difference-light-nur-quran-sun-moon/',
                  '/de/articles/wie-gewissheit-zu-gewalt-wird/',
                  '/id/articles/matahari-dhiya-bulan-nur/',
                  '/id/articles/usia-alam-semesta-13-8-miliar-tahun/',
                  '/id/articles/juhaiman-masjidil-haram-1979/']:
        open_page(route)
        summary = driver.find_element(By.CSS_SELECTOR, '.reading-tools summary')
        summary.send_keys(Keys.ENTER)
        assert driver.find_element(By.CSS_SELECTOR, '.reading-tools').get_attribute('open') is not None
        driver.save_screenshot(str(OUT / (route.strip('/').replace('/', '-') + '-contents.png')))
        driver.find_elements(By.CSS_SELECTOR, '.reading-tools nav a')[-1].click()
        assert driver.execute_script('return !document.querySelector(".reading-tools").open&&!!document.getElementById(decodeURIComponent(location.hash.slice(1)))')
        summary.send_keys(Keys.ENTER)
        summary.send_keys(Keys.ESCAPE)
        assert driver.execute_script('return !document.querySelector(".reading-tools").open&&document.activeElement===document.querySelector(".reading-tools summary")')

    # Local search must filter, clear, restore the full catalogue and announce zero results.
    for route, field, clear, results, count in [
        ('/articles/', '.library-search input', '.library-clear', '.library-results', '59'),
        ('/id/articles/', '#id-article-search', '.id-catalogue-search button', '.id-catalogue-results', '59')]:
        open_page(route)
        box = driver.find_element(By.CSS_SELECTOR, field)
        box.send_keys('zzzxxyy-no-match')
        wait.until(lambda b: b.find_element(By.CSS_SELECTOR, results).text.startswith('0 /'))
        driver.find_element(By.CSS_SELECTOR, clear).click()
        wait.until(lambda b: b.find_element(By.CSS_SELECTOR, results).text.startswith(count + ' /'))
        assert driver.switch_to.active_element == box
        driver.save_screenshot(str(OUT / ('id-search.png' if route.startswith('/id') else 'ar-search.png')))

    # The two complete catalogues share topic membership and reading order.
    # Verify real anchor jumps, all source entries/schema, and no-script access.
    catalogue_orders = {}
    for width, height in [(320, 800), (390, 844), (1440, 1000)]:
        viewport(width, height)
        for route, language in [('/articles/', 'ar'), ('/id/articles/', 'id')]:
            open_page(route)
            expected = json.loads(Path(route.strip('/'), 'feed.json').read_text())['items']
            info = driver.execute_script('''
              const entries=[...document.querySelectorAll('.library-entry')];
              return {title:document.querySelector('h1').textContent,
                groups:[...document.querySelectorAll('.library-group')].map(g=>({id:g.id,
                  slugs:[...g.querySelectorAll('.library-entry')].map(e=>e.dataset.article),
                  count:Number(g.querySelector('.library-group-count').textContent)})),
                articles:entries.map(e=>({slug:e.dataset.article,title:e.querySelector('h3 a').textContent,
                  route:e.querySelector('h3 a').getAttribute('href'),summary:e.querySelector('.library-entry-copy p').textContent,
                  book:e.querySelector('.catalogue-book').textContent})),
                schema:[...document.querySelectorAll('script[type="application/ld+json"]')].flatMap(s=>JSON.parse(s.textContent)['@graph']||[]).find(n=>n['@type']==='ItemList'),
                overflow:document.documentElement.scrollWidth>innerWidth+1};
            ''')
            assert info['title'] == ('المقالات' if language == 'ar' else 'Artikel')
            assert not info['overflow'] and len(info['groups']) == 5
            assert [g['count'] for g in info['groups']] == [11, 9, 13, 24, 2]
            assert all(g['count'] == len(g['slugs']) for g in info['groups'])
            assert len(info['articles']) == len(expected) == info['schema']['numberOfItems']
            by_route = {e['url'].split('ahmedalhafiz.com', 1)[1]: e for e in expected}
            for article, schema_item in zip(info['articles'], info['schema']['itemListElement']):
                original = by_route[article['route']]
                assert article['title'] == original['title'] == schema_item['name']
                assert article['summary'] == original['summary'] and article['book'].strip()
                assert schema_item['url'] == original['url']
            catalogue_orders[language] = [(g['id'], g['slugs']) for g in info['groups']]
            for group in info['groups']:
                driver.find_element(By.CSS_SELECTOR, f'.catalogue-topics a[href="#{group["id"]}"]').click()
                wait.until(lambda b: b.current_url.endswith('#' + group['id']))
                assert driver.execute_script('''const h=document.querySelector('header').getBoundingClientRect(),g=document.getElementById(arguments[0]).getBoundingClientRect();return g.top>=h.bottom-1&&g.top<innerHeight''', group['id'])
            driver.save_screenshot(str(OUT / f'catalogue-{language}-{width}.png'))
            driver.execute_cdp_cmd('Emulation.setScriptExecutionDisabled', {'value': True})
            try:
                driver.get(BASE + route + '?no_script_catalogue=1')
                assert len([e for e in driver.find_elements(By.CSS_SELECTOR, '.library-entry') if e.is_displayed()]) == len(expected)
                assert not driver.find_element(By.CSS_SELECTOR, '.library-search').is_displayed()
            finally:
                driver.execute_cdp_cmd('Emulation.setScriptExecutionDisabled', {'value': False})
        assert catalogue_orders['ar'] == catalogue_orders['id']

    viewport(360, 800)
    # A wrapped inline headline can have an unclickable centre between its
    # line boxes. Exercise the whole visible title, not just its first text line.
    open_page('/id/articles/')
    driver.find_element(By.ID, 'id-article-search').send_keys('Berapa Umur Alam Semesta')
    wait.until(lambda b: b.find_element(By.CSS_SELECTOR, '.id-catalogue-results').text.startswith('1 /'))
    title = driver.find_element(By.CSS_SELECTOR, '.id-catalogue-entry:not([hidden]) h3 a')
    driver.execute_script('arguments[0].scrollIntoView({block:"center",behavior:"instant"})', title)
    assert driver.execute_script('const e=arguments[0],r=e.getBoundingClientRect();return document.elementFromPoint(r.left+r.width/2,r.top+r.height/2).closest("a")===e', title), 'Headline has an unclickable gap between lines'
    title.click()
    wait.until(lambda b: '/id/articles/usia-alam-semesta-13-8-miliar-tahun/' in b.current_url)
    assert driver.find_element(By.CSS_SELECTOR, '.reading-tools summary').is_displayed()

    # Privacy withdrawal is an actual button too: it must reopen the choice UI.
    open_page('/id/privacy/')
    driver.find_element(By.CSS_SELECTOR, '[data-analytics-consent-reset]').click()
    wait.until(lambda b: b.find_elements(By.ID, 'analytics-consent'))
    assert not driver.find_elements(By.CSS_SELECTOR, 'script[src*="googletagmanager"]')
    driver.find_element(By.CSS_SELECTOR, 'button[data-consent=denied]').click()
    wait.until(lambda b: not b.find_elements(By.ID, 'analytics-consent'))
finally:
    driver.quit()

(OUT / 'report.json').write_text(json.dumps({'pass': True, 'public_pages': len(records), 'checks': records}, ensure_ascii=False, indent=2))
print('Multilingual interface controls passed: every public mobile page; four languages at three widths; contact, language switches, keyboard contents, search/reset and privacy withdrawal.')
