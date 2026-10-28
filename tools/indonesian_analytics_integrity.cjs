// A simulated browser checks behavior without sending any real Analytics traffic.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const repo = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(repo, 'assets/analytics-indonesia-pilot.js'), 'utf8');
const key = 'ahmedalhafiz.analyticsConsent.v1';
const origin = 'https://ahmedalhafiz.com';
let assertions = 0;
function equal(a, b) { assert.deepEqual(a, b); assertions++; }
function harness(page, lang = 'id', consent = null, blockedStorage = false) {
  const nodes = [], handlers = {}, storage = new Map();
  if (consent) storage.set(key, consent);
  function element(tag) {
    return { tagName: tag, dataset: {}, style: {}, attrs: {}, handlers: {},
      setAttribute(k,v) { this.attrs[k] = v; },
      addEventListener(k,f) { this.handlers[k] = f; },
      querySelector() { return null; },
      remove() { this.removed = true; }, innerHTML: '', textContent: '', href: '' };
  }
  const footer = element('nav'); footer.appendChild = x => nodes.push(x);
  const reset = element('button');
  const document = {
    readyState: 'complete', documentElement: { lang }, cookie: '',
    addEventListener(k,f) { handlers[k] = f; },
    getElementById(id) { return nodes.find(x => x.id === id && !x.removed) || null; },
    querySelector(s) { return s === '.footer-nav' ? footer : null; },
    querySelectorAll(s) { return s === '[data-analytics-consent-reset]' ? [reset] : []; },
    createElement: element,
    head: { appendChild(x) { nodes.push(x); } }, body: { appendChild(x) { nodes.push(x); } }
  };
  const localStorage = {
    getItem(k) { if (blockedStorage) throw Error('Storage blocked'); return storage.get(k) || null; },
    setItem(k,v) { if (blockedStorage) throw Error('Storage blocked'); storage.set(k,v); },
    removeItem(k) { if (blockedStorage) throw Error('Storage blocked'); storage.delete(k); }
  };
  const window = { location: new URL(page), localStorage };
  vm.runInNewContext(source, { window, document, URL, Date, encodeURIComponent });
  const events = () => Array.from(window.dataLayer || []).filter(e => e[0] === 'event').map(e => JSON.parse(JSON.stringify({name:e[1], ...e[2]})));
  const click = href => handlers.click({target:{closest() { return {href:new URL(href, page).href, dataset:{}}; }}});
  const googleLoads = () => nodes.filter(x => String(x.src || '').includes('googletagmanager.com')).length;
  return {window,document,nodes,reset,storage,events,click,googleLoads};
}
const article = `${origin}/id/articles/ketindihan-melihat-sosok/`;
for (const consent of [null, 'denied', 'invalid']) {
  const env = harness(article, 'id', consent);
  equal(env.googleLoads(), 0);
  env.click('/books/umm-abbas/'); env.click('/id/about/'); equal(env.events(), []);
}
for (const lang of ['id', 'id-ID']) {
  const env = harness(article, lang);
  const banner = env.document.getElementById('analytics-consent');
  equal(banner.attrs['aria-label'], 'Pengaturan privasi'); equal(banner.dir, 'ltr');
  equal(banner.innerHTML.includes('/id/privacy/'), true);
  equal(banner.innerHTML.includes('Izinkan analitik'), true);
  banner.handlers.click({target:{closest() {return {dataset:{consent:'granted'}};}}});
  equal(env.googleLoads(), 1); equal(env.storage.get(key), 'granted');
  equal(env.document.getElementById('analytics-consent'), null);
  env.click('/books/umm-abbas/');
  equal(env.events(), [{name:'article_to_book',article_slug:'ketindihan-melihat-sosok',book_slug:'umm-abbas',lang}]);
  env.click('/id/about/');
  equal(env.events()[1], {name:'article_to_author',article_slug:'ketindihan-melihat-sosok',author_id:`${origin}/#person`,lang});
  env.reset.handlers.click(); equal(env.googleLoads(), 1); equal(env.storage.has(key), false);
  env.click('/books/umm-abbas/'); equal(env.events().length, 2);
  const again = env.document.getElementById('analytics-consent');
  again.handlers.click({target:{closest() {return {dataset:{consent:'denied'}};}}});
  equal(env.storage.get(key), 'denied'); equal(env.document.getElementById('analytics-consent'), null);
}
for (const target of ['/books/', '/id/articles/', 'https://example.com/books/umm-abbas/', 'https://example.com/id/about/']) {
  const env = harness(article, 'id', 'granted'); env.click(target); equal(env.events(), []);
}
for (const page of [`${origin}/id/`, `${origin}/id/about/`]) {
  const env = harness(page, 'id', 'granted'); env.click('/books/umm-abbas/'); equal(env.events(), []);
}
const future = harness(`${origin}/id/guides/contoh/`, 'id', 'granted');
future.click('/id/books/umm-abbas/'); equal(future.events()[0].book_slug,'umm-abbas');
for (const host of ['http://terminal.local:4173', 'http://localhost:4173']) {
  const env = harness(`${host}/id/articles/ketindihan-melihat-sosok/`, 'id', 'granted');
  env.click('/books/umm-abbas/'); equal(env.googleLoads(), 0); equal(env.events(), []);
}
const blocked = harness(article, 'id', null, true); equal(blocked.googleLoads(), 0);
equal(Boolean(blocked.document.getElementById('analytics-consent')), true);
const result = {tested_at:new Date().toISOString(),status:'pass',assertions,real_network_requests:0,
  cases:['consent gate','ID and id-ID labels','one book event per click','author event','withdrawal and rejection','negative routes','preview isolation','blocked storage'],
  limitation:'Simulated DOM; consent UI and responsive rendering are checked separately in the browser.'};
console.log(JSON.stringify(result));
