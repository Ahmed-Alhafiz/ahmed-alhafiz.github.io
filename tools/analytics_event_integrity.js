const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '..', 'assets', 'analytics-ga4-28.js'), 'utf8');
const CONSENT_KEY = 'ahmedalhafiz.analyticsConsent.v1';

function harness(page, lang, consent = 'granted') {
  const location = new URL(page);
  const storage = new Map();
  if (consent) storage.set(CONSENT_KEY, consent);
  const appended = [];
  let clickHandler;

  function element(tag) {
    return {
      tagName: String(tag || '').toUpperCase(),
      dataset: {},
      style: {},
      setAttribute() {},
      addEventListener() {},
      remove() {},
      closest() { return null; },
      innerHTML: '',
      textContent: '',
      href: ''
    };
  }

  const document = {
    readyState: 'complete',
    documentElement: { lang },
    cookie: '',
    addEventListener(type, handler) {
      if (type === 'click') clickHandler = handler;
    },
    getElementById() { return null; },
    querySelector() { return null; },
    querySelectorAll() { return []; },
    createElement: element,
    head: { appendChild(node) { appended.push(node); } },
    body: { appendChild(node) { appended.push(node); } }
  };

  const localStorage = {
    getItem(key) { return storage.has(key) ? storage.get(key) : null; },
    setItem(key, value) { storage.set(key, String(value)); },
    removeItem(key) { storage.delete(key); }
  };

  const window = { location, localStorage };
  vm.runInNewContext(source, { window, document, URL, Date, encodeURIComponent });

  return { window, document, appended, get clickHandler() { return clickHandler; } };
}

function clickFrom(page, href, lang, dataset = {}, consent = 'granted') {
  const env = harness(page, lang, consent);
  const link = { href: new URL(href, env.window.location).href, dataset };
  assert.equal(typeof env.clickHandler, 'function');
  env.clickHandler({ target: { closest(selector) {
    assert.equal(selector, 'a[href]');
    return link;
  } } });
  return Array.from(env.window.dataLayer || []).filter((entry) => entry[0] === 'event').map((entry) => ({
    name: entry[1],
    article: entry[2].article_slug,
    book: entry[2].book_slug,
    lang: entry[2].lang
  }));
}

const origin = 'https://ahmedalhafiz.com';

// Consent gate: no Google script before opt-in.
for (const consent of [null, 'denied']) {
  const env = harness(`${origin}/articles/sleep-paralysis-jathoom/`, 'ar', consent);
  assert.equal(env.appended.some(node => String(node.src || '').includes('googletagmanager.com')), false);
  assert.deepEqual(clickFrom(`${origin}/articles/sleep-paralysis-jathoom/`, '/books/umm-abbas/', 'ar', {}, consent), []);
}
const granted = harness(`${origin}/articles/sleep-paralysis-jathoom/`, 'ar', 'granted');
assert.equal(granted.appended.some(node => String(node.src || '').includes('googletagmanager.com')), true);

// Existing article-to-book analytics route remains correct after consent.
assert.deepEqual(clickFrom(`${origin}/articles/sleep-paralysis-jathoom/`, '/books/umm-abbas/', 'ar'), [
  { name: 'article_to_book', article: 'sleep-paralysis-jathoom', book: 'umm-abbas', lang: 'ar' }
]);
assert.deepEqual(clickFrom(`${origin}/en/articles/fall-of-baghdad-1258-ibn-al-alqami/`, '/en/books/kitab-al-kutub/', 'en', {
  articleSlug: 'fall-of-baghdad-1258-ibn-al-alqami', bookSlug: 'kitab-al-kutub', lang: 'en'
}), [
  { name: 'article_to_book', article: 'fall-of-baghdad-1258-ibn-al-alqami', book: 'kitab-al-kutub', lang: 'en' }
]);
assert.deepEqual(clickFrom(`${origin}/de/articles/fall-von-bagdad-1258-ibn-al-alqami/`, '/de/books/kitab-al-kutub/', 'de'), [
  { name: 'article_to_book', article: 'fall-von-bagdad-1258-ibn-al-alqami', book: 'kitab-al-kutub', lang: 'de' }
]);
assert.deepEqual(clickFrom(`${origin}/guides/arabic-psychological-horror/`, '/books/umm-abbas/', 'ar'), [
  { name: 'article_to_book', article: 'arabic-psychological-horror', book: 'umm-abbas', lang: 'ar' }
]);
for (const [page, target] of [
  [`${origin}/`, '/books/umm-abbas/'],
  [`${origin}/articles/sleep-paralysis-jathoom/`, '/books/'],
  [`${origin}/articles/sleep-paralysis-jathoom/`, '/articles/'],
  [`${origin}/articles/sleep-paralysis-jathoom/`, 'https://example.com/books/umm-abbas/']
]) {
  assert.deepEqual(clickFrom(page, target, 'ar'), []);
}
console.log('GA4 consent gate and article_to_book routing passed (AR/EN/DE, negative cases).');
