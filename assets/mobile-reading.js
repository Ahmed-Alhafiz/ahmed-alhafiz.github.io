/* Progressive reading controls. No network requests, storage or analytics. */
(() => {
  const root = document.documentElement;
  const header = document.querySelector('.site-header');
  const article = document.querySelector('.article-body, .article-prose');
  const narrow = matchMedia('(max-width: 1000px)');
  const contents = [];

  if (header) {
    const measure = () => root.style.setProperty('--masthead-height', `${header.getBoundingClientRect().height}px`);
    measure();
    if ('ResizeObserver' in window) new ResizeObserver(measure).observe(header);
    else window.addEventListener('resize', measure, {passive: true});
  }

  if (article) {
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
      const details = document.createElement('details');
      details.className = 'reading-contents';
      const summary = document.createElement('summary');
      title.before(details);
      summary.append(title);
      details.append(summary, list);
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
      for (const section of sections) {
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
