// Automatski generisano (build.mjs)
const CACHE = 'opstanak-9c3e88c5d8';
const FILES = ["assets/icon.svg","assets/plan.js","assets/site.js","assets/style.css","./","manifest.webmanifest","o-projektu/","plan/","scenariji/dugorocno-prezivljavanje/","scenariji/","scenariji/nestanak-struje/","scenariji/nuklearna-katastrofa/","scenariji/pandemija/","scenariji/prirodne-katastrofe/","srbija/","vestine/higijena-i-sanitacija/","vestine/hrana/","vestine/","vestine/komunikacija-i-informisanje/","vestine/mentalna-otpornost/","vestine/navigacija/","vestine/prva-pomoc/","vestine/skloniste-i-toplota/","vestine/vatra/","vestine/voda/"];
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE)
      .then((c) => c.addAll(FILES.map((f) => new URL(f, self.registration.scope).href)))
      .then(() => self.skipWaiting())
  );
});
self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith('opstanak-') && k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});
self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  e.respondWith(caches.match(e.request, { ignoreSearch: true }).then((hit) => hit || fetch(e.request)));
});
