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
  let resetConsent;

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
    querySelectorAll(selector) {
      assert.equal(selector, '[data-analytics-consent-reset]');
      return [{ addEventListener(type, handler) {
        assert.equal(type, 'click');
        resetConsent = handler;
      } }];
    },
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

  return { window, document, appended, clickHandler, resetConsent };
}

function clickLink(env, href, dataset = {}, inOrdering = false) {
  const target = new URL(href, env.window.location);
  const link = {
    href: target.href,
    protocol: target.protocol,
    dataset,
    closest(selector) {
      assert.equal(selector, '#ordering');
      return inOrdering ? {} : null;
    }
  };
  assert.equal(typeof env.clickHandler, 'function');
  env.clickHandler({ target: { closest(selector) {
    assert.equal(selector, 'a[href]');
    return link;
  } } });
}

function events(env) {
  return Array.from(env.window.dataLayer || []).filter((entry) => entry[0] === 'event');
}

function clickFrom(page, href, lang, dataset = {}, consent = 'granted') {
  const env = harness(page, lang, consent);
  clickLink(env, href, dataset);
  return events(env).map((entry) => ({
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

for (const [lang, prefix] of [['ar', ''], ['en', 'en/'], ['de', 'de/']]) {
  for (const book of ['umm-abbas', 'sirou-fi-alard']) {
    const route = `${prefix}books/${book}/`;
    const html = fs.readFileSync(path.join(__dirname, '..', route, 'index.html'), 'utf8');
    const ordering = html.match(/<aside[^>]*id="ordering"[^>]*>[\s\S]*?<\/aside>/)[0];
    for (const [protocol, method] of [['mailto:', 'email'], ['tel:', 'phone']]) {
      const href = new RegExp(`href="(${protocol}[^"]+)"`).exec(ordering)[1];
      const env = harness(`${origin}/${route}`, lang);
      clickLink(env, href, {}, true);
      assert.deepEqual(events(env).map((entry) => [entry[1], { ...entry[2] }]), [
        ['publisher_contact_click', { book_slug: book, lang, contact_method: method }]
      ]);
    }
  }
}

const bookPage = `${origin}/books/umm-abbas/`;
const publisher = 'mailto:publisher@example.test?subject=Book';
for (const consent of [null, 'denied']) {
  const env = harness(bookPage, 'ar', consent);
  clickLink(env, publisher, {}, true);
  clickLink(env, 'tel:+431234567', {}, true);
  assert.deepEqual(events(env), []);
}
const contactEnv = harness(bookPage, 'ar');
clickLink(contactEnv, publisher); // Outside the publisher contact section.
clickLink(contactEnv, '#ordering'); // Merely opening the section is not a contact click.
clickLink(contactEnv, 'https://example.test', {}, true);
assert.deepEqual(events(contactEnv), []);
contactEnv.resetConsent();
clickLink(contactEnv, publisher, {}, true);
assert.deepEqual(events(contactEnv), []);

const articleEnv = harness(`${origin}/articles/sleep-paralysis-jathoom/`, 'ar');
clickLink(articleEnv, '/books/umm-abbas/#ordering');
assert.deepEqual(events(articleEnv).map((entry) => entry[1]), ['article_to_book']);
clickLink(articleEnv, publisher, {}, true);
assert.equal(events(articleEnv).length, 1);

console.log('GA4 consent, article routing, and publisher email/phone clicks passed for Arabic, English, and German.');
