const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '..', 'assets', 'analytics-ga4-28.js'), 'utf8');

function clickFrom(page, href, lang, dataset = {}) {
  const location = new URL(page);
  const link = { href: new URL(href, location).href, dataset };
  let clickHandler;
  const document = {
    documentElement: { lang },
    addEventListener(type, handler) {
      if (type === 'click') clickHandler = handler;
    },
    createElement() { return {}; },
    head: { appendChild() {} }
  };
  const window = { location };
  vm.runInNewContext(source, { window, document, URL, Date, encodeURIComponent });
  clickHandler({ target: { closest(selector) {
    assert.equal(selector, 'a[href]');
    return link;
  } } });
  return Array.from(window.dataLayer).filter((entry) => entry[0] === 'event').map((entry) => ({
    name: entry[1],
    article: entry[2].article_slug,
    book: entry[2].book_slug,
    lang: entry[2].lang
  }));
}

const origin = 'https://ahmedalhafiz.com';
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
console.log('GA4 article_to_book routing passed (AR/EN/DE, legacy tags, negative cases).');
