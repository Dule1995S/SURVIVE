(() => {
  const root = document.documentElement.dataset.root || './';
  document.documentElement.classList.add('js');

  const toggle = document.querySelector('.nav-toggle');
  const nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
  }

  // Offline: ceo sajt se kešira posle prve posete.
  if ('serviceWorker' in navigator && location.protocol !== 'file:' && !document.documentElement.hasAttribute('data-no-sw')) {
    navigator.serviceWorker.register(root + 'sw.js').catch(() => {});
  }
})();
