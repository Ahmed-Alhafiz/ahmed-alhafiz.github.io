(() => {
  'use strict';

  const measurementId = 'G-TYFF6MTK0Y';
  const consentKey = 'ahmedalhafiz.analyticsConsent.v1';
  let analyticsEnabled = false;
  let loaderStarted = false;

  const copy = {
    ar: {
      label: 'إعدادات الخصوصية',
      text: 'نستخدم Google Analytics فقط إذا وافقت. لن نحمّل خدمة الإحصاءات أو نضع ملفاتها قبل موافقتك.',
      accept: 'السماح بالإحصاءات',
      reject: 'رفض',
      privacy: 'سياسة الخصوصية'
    },
    en: {
      label: 'Privacy settings',
      text: 'We use Google Analytics only if you consent. Analytics is not loaded and its cookies are not set before you agree.',
      accept: 'Allow analytics',
      reject: 'Reject',
      privacy: 'Privacy policy'
    },
    de: {
      label: 'Datenschutzeinstellungen',
      text: 'Google Analytics wird nur mit Ihrer Einwilligung verwendet. Vor Ihrer Zustimmung wird der Dienst nicht geladen und setzt keine Analytics-Cookies.',
      accept: 'Analytics erlauben',
      reject: 'Ablehnen',
      privacy: 'Datenschutz'
    }
  };

  function language() {
    const lang = (document.documentElement.lang || 'ar').toLowerCase();
    return lang.startsWith('de') ? 'de' : lang.startsWith('en') ? 'en' : 'ar';
  }

  function privacyPath() {
    const lang = language();
    return lang === 'de' ? '/de/privacy/' : lang === 'en' ? '/en/privacy/' : '/privacy/';
  }

  function readConsent() {
    try {
      const value = window.localStorage.getItem(consentKey);
      return value === 'granted' || value === 'denied' ? value : null;
    } catch (_) {
      return null;
    }
  }

  function writeConsent(value) {
    try {
      window.localStorage.setItem(consentKey, value);
    } catch (_) {
      // If storage is unavailable, honor the choice for this page without persistence.
    }
  }

  function clearAnalyticsCookies() {
    const names = document.cookie.split(';').map(item => item.split('=')[0].trim()).filter(name => /^_ga(?:_|$)/.test(name));
    const hosts = [window.location.hostname, '.' + window.location.hostname];
    const parts = window.location.hostname.split('.');
    if (parts.length > 2) hosts.push('.' + parts.slice(-2).join('.'));
    for (const name of names) {
      document.cookie = name + '=; Max-Age=0; path=/; SameSite=Lax';
      for (const domain of hosts) {
        document.cookie = name + '=; Max-Age=0; path=/; domain=' + domain + '; SameSite=Lax';
      }
    }
  }

  function enableAnalytics() {
    if (loaderStarted) return;
    loaderStarted = true;
    analyticsEnabled = true;

    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', {
      analytics_storage: 'granted',
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied'
    });
    window.gtag('js', new Date());
    window.gtag('config', measurementId, {
      send_page_view: true,
      allow_google_signals: false,
      allow_ad_personalization_signals: false
    });

    const loader = document.createElement('script');
    loader.async = true;
    loader.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(measurementId);
    document.head.appendChild(loader);
  }

  function disableAnalytics() {
    analyticsEnabled = false;
    if (typeof window.gtag === 'function') {
      window.gtag('consent', 'update', {
        analytics_storage: 'denied',
        ad_storage: 'denied',
        ad_user_data: 'denied',
        ad_personalization: 'denied'
      });
    }
    clearAnalyticsCookies();
  }

  function setConsent(value) {
    writeConsent(value);
    if (value === 'granted') enableAnalytics();
    else disableAnalytics();
    document.getElementById('analytics-consent')?.remove();
  }

  function addPrivacyLink() {
    const footer = document.querySelector('.footer-nav');
    if (!footer || footer.querySelector('[data-privacy-link]')) return;
    const link = document.createElement('a');
    link.href = privacyPath();
    link.dataset.privacyLink = 'true';
    link.textContent = copy[language()].privacy;
    footer.appendChild(link);
  }

  function showBanner() {
    if (document.getElementById('analytics-consent')) return;
    const lang = language();
    const t = copy[lang];
    const banner = document.createElement('section');
    banner.id = 'analytics-consent';
    banner.className = 'analytics-consent';
    banner.setAttribute('role', 'region');
    banner.setAttribute('aria-label', t.label);
    banner.dir = lang === 'ar' ? 'rtl' : 'ltr';
    banner.innerHTML = '<div class="analytics-consent__copy"><strong>' + t.label + '</strong><p>' + t.text + '</p></div>' +
      '<div class="analytics-consent__actions"><button type="button" data-consent="granted">' + t.accept + '</button>' +
      '<button type="button" class="secondary" data-consent="denied">' + t.reject + '</button>' +
      '<a href="' + privacyPath() + '">' + t.privacy + '</a></div>';
    banner.addEventListener('click', event => {
      const button = event.target.closest('button[data-consent]');
      if (button) setConsent(button.dataset.consent);
    });
    document.body.appendChild(banner);
  }

  function installStyles() {
    if (document.getElementById('analytics-consent-style')) return;
    const style = document.createElement('style');
    style.id = 'analytics-consent-style';
    style.textContent = '.analytics-consent{position:fixed;z-index:1200;inset:auto 16px 16px 16px;display:flex;align-items:center;justify-content:space-between;gap:22px;max-width:980px;margin-inline:auto;padding:17px 18px;border:1px solid rgba(255,255,255,.18);border-radius:16px;background:#0b1724;color:#eef3f6;box-shadow:0 20px 60px rgba(0,0,0,.32);font:14px/1.6 Arial,sans-serif}.analytics-consent__copy{max-width:620px}.analytics-consent__copy strong{display:block;color:#fff;font-size:15px}.analytics-consent__copy p{margin:4px 0 0;color:#cbd6de}.analytics-consent__actions{display:flex;align-items:center;flex-wrap:wrap;gap:8px}.analytics-consent button,.analytics-consent a{min-height:40px;padding:8px 13px;border:1px solid #df9368;border-radius:999px;background:#df9368;color:#0b1724;font:700 12px/1 Arial,sans-serif;cursor:pointer}.analytics-consent button.secondary,.analytics-consent a{background:transparent;color:#fff;border-color:rgba(255,255,255,.45)}.analytics-consent a{display:inline-flex;align-items:center;text-decoration:none}@media(max-width:700px){.analytics-consent{inset:auto 10px 10px;display:block;padding:15px}.analytics-consent__actions{margin-top:12px}.analytics-consent button,.analytics-consent a{flex:1 1 auto;justify-content:center;text-align:center}}';
    document.head.appendChild(style);
  }

  document.addEventListener('click', event => {
    const link = event.target.closest('a[href]');
    if (!link || !analyticsEnabled || typeof window.gtag !== 'function') return;

    const article = window.location.pathname.match(/^\/(?:en\/|de\/)?(?:articles|guides)\/([^/]+)\//);
    if (!article) return;

    const destination = new URL(link.href, window.location.href);
    const book = destination.pathname.match(/^\/(?:en\/|de\/)?books\/([^/]+)\/?$/);
    if (destination.origin !== window.location.origin || !book) return;

    window.gtag('event', 'article_to_book', {
      article_slug: link.dataset.articleSlug || article[1],
      book_slug: link.dataset.bookSlug || book[1],
      lang: link.dataset.lang || document.documentElement.lang || ''
    });
  });

  function boot() {
    installStyles();
    addPrivacyLink();

    document.querySelectorAll('[data-analytics-consent-reset]').forEach(button => {
      button.addEventListener('click', () => {
        try { window.localStorage.removeItem(consentKey); } catch (_) {}
        disableAnalytics();
        showBanner();
      });
    });

    const consent = readConsent();
    if (consent === 'granted') enableAnalytics();
    else if (consent === 'denied') disableAnalytics();
    else showBanner();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, { once: true });
  else boot();
})();
