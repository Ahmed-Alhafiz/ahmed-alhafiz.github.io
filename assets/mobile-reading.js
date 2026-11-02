/* Progressive reading controls. No network requests, storage or analytics. */
(() => {
  const root = document.documentElement;
  const header = document.querySelector('.site-header');
  const article = document.querySelector('main .reading-body') ||
    document.querySelector('main .article-body, main .article-prose, main.article-page .prose');
  const narrow = matchMedia('(max-width: 1000px)');
  const contents = [];
  const language = (root.lang || 'ar').split('-')[0];
  const copy = {
    ar: {contact: 'تواصل', contents: 'محتويات المقال'},
    en: {contact: 'Contact', contents: 'Article contents'},
    de: {contact: 'Kontakt', contents: 'Inhalt des Artikels'},
    id: {contact: 'Kontak', contents: 'Daftar isi artikel'}
  }[language] || {contact: 'Contact', contents: 'Article contents'};

  // Keep the same contact action on every language and every page. It remains
  // a real local anchor; no home-page detour or untranslated placeholder.
  const footer = document.querySelector('footer.site-footer');
  const nav = header?.querySelector('nav');
  if (footer && nav) {
    const target = footer.querySelector('.footer-contact') || footer;
    target.id = 'site-contact';
    let contact = [...nav.querySelectorAll('a')].find(link =>
      new URL(link.href).hash === '#contact' || link.getAttribute('href') === '#site-contact');
    if (!contact) {
      contact = document.createElement('a');
      nav.append(contact);
    }
    contact.href = '#site-contact';
    contact.textContent = copy.contact;
    const prefix = language === 'ar' ? '/' : `/${language}/`;
    for (const link of nav.querySelectorAll('a')) {
      if (new URL(link.href).hash) continue;
      const path = new URL(link.href).pathname;
      if (path === location.pathname || (path !== prefix && location.pathname.startsWith(path))) {
        link.setAttribute('aria-current', 'page');
      }
    }
  }

  if (header) {
    const measure = () => root.style.setProperty('--masthead-height', `${header.getBoundingClientRect().height}px`);
    measure();
    if ('ResizeObserver' in window) new ResizeObserver(measure).observe(header);
    else window.addEventListener('resize', measure, {passive: true});
  }

  if (article) {
    // Fixed positioning avoids shifting the article when progressively adding
    // the same contents control to older and newer translation templates.
    const headings = [...article.querySelectorAll('h2')].filter(heading =>
      heading.textContent.trim() && !heading.closest('.toc, nav, aside'));
    if (headings.length >= 3) {
      const tools = document.createElement('details');
      tools.className = 'reading-tools';
      const summary = document.createElement('summary');
      summary.textContent = copy.contents;
      const menu = document.createElement('nav');
      menu.setAttribute('aria-label', copy.contents);
      headings.forEach((heading, index) => {
        if (!heading.id) {
          let id = `reading-section-${index + 1}`;
          while (document.getElementById(id)) id += '-section';
          heading.id = id;
        }
        const link = document.createElement('a');
        link.href = `#${encodeURIComponent(heading.id)}`;
        link.textContent = heading.textContent.trim();
        menu.append(link);
      });
      tools.append(summary, menu);
      document.body.append(tools);
      menu.addEventListener('click', event => {
        if (event.target.closest('a')) tools.open = false;
      });
      document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && tools.open) {
          tools.open = false;
          summary.focus();
        }
      });
      document.addEventListener('click', event => {
        if (tools.open && !tools.contains(event.target)) tools.open = false;
      });
      const consent = document.getElementById('analytics-consent');
      if (consent) {
        // Consent is injected before this deferred script. Keep the reading
        // control out of its way until the visitor makes a choice.
        tools.hidden = true;
        const observer = new MutationObserver(() => {
          if (!consent.isConnected) { tools.hidden = false; observer.disconnect(); }
        });
        observer.observe(document.body, {childList: true});
      }
    }
    document.querySelectorAll('.toc').forEach(toc => {
      const title = toc.querySelector('strong, h2, h3');
      let list = toc.querySelector('ol, ul');
      if (!list) {
        const links = [...toc.querySelectorAll(':scope > a')];
        if (links.length) {
          list = document.createElement('div');
          list.className = 'reading-contents-links';
          list.append(...links);
        }
      }
      if (!title || !list) return;
      // A native disclosure can be delivered with the page so a slow script
      // never collapses an already-painted contents list above the article.
      let details = toc.querySelector(':scope > details.reading-contents');
      if (!details) {
        details = document.createElement('details');
        details.className = 'reading-contents';
        const summary = document.createElement('summary');
        title.before(details);
        summary.append(title);
        details.append(summary, list);
      }
      contents.push(details);
      list.addEventListener('click', event => {
        if (narrow.matches && event.target.closest('a[href^="#"]')) details.open = false;
      });
    });
    const syncContents = () => contents.forEach(details => { details.open = !narrow.matches; });
    syncContents();
    narrow.addEventListener('change', syncContents);

    const meter = document.createElement('div');
    meter.className = 'reading-progress';
    meter.setAttribute('aria-hidden', 'true');
    const fill = document.createElement('span');
    meter.append(fill);
    document.body.append(meter);
    const links = [...document.querySelectorAll('.toc a[href^="#"]')];
    const sections = links.map(link => ({
      link, target: document.getElementById(decodeURIComponent(link.hash.slice(1)))
    })).filter(section => section.target);
    let queued = false;
    let active;
    const update = () => {
      queued = false;
      const masthead = header ? header.getBoundingClientRect().height : 0;
      const box = article.getBoundingClientRect();
      const start = box.top + window.scrollY;
      const distance = Math.max(1, box.height - (window.innerHeight - masthead));
      const progress = Math.max(0, Math.min(1, (window.scrollY + masthead - start) / distance));
      fill.style.transform = `scaleX(${progress})`;
      let current;
      if (sections.length) for (const section of sections) {
        if (section.target.getBoundingClientRect().top <= masthead + 90) current = section.link;
      }
      if (current !== active) {
        if (active) active.removeAttribute('aria-current');
        if (current) current.setAttribute('aria-current', 'location');
        active = current;
      }
    };
    const schedule = () => {
      if (!queued) { queued = true; requestAnimationFrame(update); }
    };
    window.addEventListener('scroll', schedule, {passive: true});
    window.addEventListener('resize', schedule, {passive: true});
    document.fonts?.ready.then(schedule);
    if ('ResizeObserver' in window) new ResizeObserver(schedule).observe(article);
    update();
    let printState;
    window.addEventListener('beforeprint', () => {
      printState = contents.map(details => details.open);
      contents.forEach(details => { details.open = true; });
    });
    window.addEventListener('afterprint', () => {
      contents.forEach((details, i) => { details.open = printState?.[i] ?? !narrow.matches; });
    });
  }

  const topicLinks = [...document.querySelectorAll('.library-topics a[href^="#"]')];
  const groups = topicLinks.map(link => ({link, target: document.getElementById(link.hash.slice(1))}));
  if (groups.length) {
    let queued = false;
    const update = () => {
      queued = false;
      const offset = (header?.getBoundingClientRect().height || 0) + 100;
      let current;
      for (const group of groups) {
        if (group.target && !group.target.hidden && group.target.getBoundingClientRect().top <= offset) current = group.link;
      }
      topicLinks.forEach(link => {
        if (link === current) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    };
    const schedule = () => {
      if (!queued) { queued = true; requestAnimationFrame(update); }
    };
    window.addEventListener('scroll', schedule, {passive: true});
    document.querySelector('.library-search')?.addEventListener('input', schedule);
    document.querySelector('.library-search')?.addEventListener('reset', schedule);
    update();
  }
})();
