/* Local progressive search: no requests, storage, analytics or dependencies. */
(() => {
  const library = document.querySelector('.research-library');
  if (!library) return;
  const form = library.querySelector('.library-search');
  const input = form.querySelector('input');
  const status = form.querySelector('.library-results');
  const empty = library.querySelector('.library-empty');
  const groups = [...library.querySelectorAll('.library-group')];
  const normalize = text => text.normalize('NFKD').replace(/[\u0300-\u036f\u064b-\u065f\u0670\u0640]/g, '').replace(/[أإآٱ]/g, 'ا').replace(/ى/g, 'ي').toLocaleLowerCase().replace(/ß/g, 'ss');
  const entries = [...library.querySelectorAll('.library-entry')].map(element => ({
    element,
    text: normalize(element.querySelector('.library-entry-copy').textContent)
  }));
  function filter() {
    const terms = normalize(input.value.trim()).split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const entry of entries) {
      entry.element.hidden = !terms.every(term => entry.text.includes(term));
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
  form.addEventListener('submit', event => event.preventDefault());
  input.addEventListener('input', filter);
  form.addEventListener('reset', () => {
    input.value = '';
    filter();
    input.focus();
  });
})();
