/* Local progressive search: no requests, storage, analytics or dependencies. */
(() => {
  const library = document.querySelector('.research-library');
  if (!library) return;
  const form = library.querySelector('.library-search');
  const input = form.querySelector('input');
  const status = form.querySelector('.library-results');
  const empty = library.querySelector('.library-empty');
  const groups = [...library.querySelectorAll('.library-group')];
  const modes = [...form.querySelectorAll('input[name="library-view"]')];
  const bookSelect = form.querySelector('#library-book');
  const bookFilter = form.querySelector('.library-book-filter');
  const bookContext = form.querySelector('.library-book-context');
  const topics = library.querySelector('.library-topics');
  const bookOption = slug => bookSelect && [...bookSelect.options].find(option => option.value === slug && slug);
  const selectedBook = () => modes.find(mode => mode.checked)?.value === 'book' ? bookSelect.value : '';
  const normalize = text => text.normalize('NFKD').replace(/[\u0300-\u036f\u064b-\u065f\u0670\u0640]/g, '').replace(/[أإآٱ]/g, 'ا').replace(/ى/g, 'ي').toLocaleLowerCase().replace(/ß/g, 'ss');
  const entries = [...library.querySelectorAll('.library-entry')].map(element => ({
    element,
    text: normalize(element.querySelector('.library-entry-copy').textContent),
    book: element.dataset.book
  }));
  function filter() {
    const terms = normalize(input.value.trim()).split(/\s+/).filter(Boolean);
    const book = bookSelect ? selectedBook() : '';
    const bookMode = modes.some(mode => mode.checked && mode.value === 'book');
    if (modes.length) library.dataset.view = bookMode ? 'book' : 'topic';
    if (bookFilter) bookFilter.hidden = !bookMode;
    if (topics && modes.length) topics.hidden = bookMode;
    if (bookContext) {
      const option = bookOption(book);
      bookContext.hidden = !option;
      if (option) {
        const anchor = bookContext.querySelector('a');
        anchor.setAttribute('href', option.dataset.route);
        anchor.querySelector('.library-book-title').textContent = option.textContent.replace(/ \(\d+\)$/, '');
      }
    }
    let visible = 0;
    for (const entry of entries) {
      entry.element.hidden = !!(book && entry.book !== book) || !terms.every(term => entry.text.includes(term));
      if (!entry.element.hidden) visible++;
    }
    for (const group of groups) {
      const count = [...group.querySelectorAll('.library-entry')].filter(entry => !entry.hidden).length;
      group.hidden = count === 0;
      group.querySelector('.library-group-count').textContent = String(count).padStart(2, '0');
      const link = library.querySelector(`.library-topics a[href="#${group.id}"]`);
      link.hidden = count === 0;
      link.querySelector('small').textContent = count;
    }
    status.textContent = `${visible} / ${entries.length} ${status.dataset.unit}`;
    empty.hidden = visible !== 0;
  }
  form.hidden = false;
  if (bookSelect) {
    const initial = new URL(location.href).searchParams.get('book');
    if (bookOption(initial)) {
      bookSelect.value = initial;
      modes.find(mode => mode.value === 'book').checked = true;
    }
    const updateRoute = () => {
      const url = new URL(location.href);
      const book = selectedBook();
      if (book) url.searchParams.set('book', book);
      else url.searchParams.delete('book');
      history.replaceState(null, '', url);
      filter();
    };
    bookSelect.addEventListener('change', updateRoute);
    modes.forEach(mode => mode.addEventListener('change', updateRoute));
  }
  form.addEventListener('submit', event => event.preventDefault());
  input.addEventListener('input', filter);
  form.addEventListener('reset', () => {
    input.value = '';
    if (bookSelect) {
      bookSelect.value = '';
      modes.forEach(mode => { mode.checked = mode.value === 'topic'; });
      const url = new URL(location.href);
      url.searchParams.delete('book');
      history.replaceState(null, '', url);
    }
    filter();
    input.focus();
  });
  if (bookSelect) filter();
})();
