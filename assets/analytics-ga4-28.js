(() => {
  'use strict';

  const measurementId = 'G-TYFF6MTK0Y';
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };

  // Analytics only: no Google Signals and no ad-personalization signals.
  window.gtag('js', new Date());
  window.gtag('config', measurementId, {
    send_page_view: true,
    allow_google_signals: false,
    allow_ad_personalization_signals: false
  });

  document.addEventListener('click', (event) => {
    const link = event.target.closest('a[href]');
    if (!link) return;

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

  const loader = document.createElement('script');
  loader.async = true;
  loader.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(measurementId);
  document.head.appendChild(loader);
})();
