#!/usr/bin/env node
// Mali generator statičkog sajta (bez Next.js-a), za GitHub Pages.
// src/pages/**.html (sa front matter-om, vidi lib/content.mjs) + src/layout.html  ->  docs/
import { readdir, readFile, writeFile, mkdir, rm, cp } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { ROOT, SRC, site, esc, pages, renderContent, pageTitle, pageDescription } from './lib/content.mjs';

const OUT = path.join(ROOT, 'docs');
const layout = await readFile(path.join(SRC, 'layout.html'), 'utf8');
const outFile = (p) => path.join(OUT, ...p.segs, 'index.html');

function render(page) {
  const root = page.depth === 0 ? './' : '../'.repeat(page.depth);
  const sectionKey = page.segs[0] || '';
  const content = renderContent(page);

  const nav = site.nav
    .map(
      (n) =>
        `<li><a href="${n.href}"${n.section === sectionKey && sectionKey ? ' aria-current="true"' : ''}>${esc(n.title)}</a></li>`
    )
    .join('');

  const title = pageTitle(page);
  const description = pageDescription(page);
  const script = page.meta.script ? `<script src="/assets/${page.meta.script}" defer></script>` : '';

  const vars = {
    title: esc(title),
    description: esc(description),
    siteName: esc(site.name),
    tagline: esc(site.tagline),
    nav,
    content,
    script,
    root,
    canonical: site.url ? `<link rel="canonical" href="${site.url.replace(/\/$/, '')}${page.url}">` : '',
  };
  let html = layout.replace(/\{\{(\w+)\}\}/g, (_, k) => vars[k] ?? '');
  // /putanja -> relativna putanja (sajt radi u podfolderu i sa file://)
  html = html.replace(/(href|src)="\/(?!\/)/g, `$1="${root}`);
  return html;
}

// ---------- izgradnja ----------
await rm(OUT, { recursive: true, force: true });
await mkdir(OUT, { recursive: true });

for (const p of pages) {
  await mkdir(path.dirname(outFile(p)), { recursive: true });
  await writeFile(outFile(p), render(p));
}
await cp(path.join(SRC, 'assets'), path.join(OUT, 'assets'), { recursive: true });

// manifest
await writeFile(
  path.join(OUT, 'manifest.webmanifest'),
  JSON.stringify(
    {
      name: `${site.name} — ${site.tagline}`,
      short_name: site.name,
      description: site.description,
      lang: 'sr',
      start_url: './',
      scope: './',
      display: 'standalone',
      background_color: '#0f1210',
      theme_color: '#0f1210',
      icons: [{ src: 'assets/icon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any' }],
    },
    null,
    2
  )
);

// sitemap + robots (samo ako je podešen site.url)
if (site.url) {
  const base = site.url.replace(/\/$/, '');
  await writeFile(
    path.join(OUT, 'sitemap.xml'),
    `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${pages
      .map((p) => `  <url><loc>${base}${p.url}</loc></url>`)
      .join('\n')}\n</urlset>\n`
  );
  await writeFile(path.join(OUT, 'robots.txt'), `User-agent: *\nAllow: /\nSitemap: ${base}/sitemap.xml\n`);
}

// service worker — ceo sajt se kešira za rad bez interneta
async function listFiles(dir, base = '') {
  const out = [];
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const rel = path.posix.join(base, e.name);
    if (e.isDirectory()) out.push(...(await listFiles(path.join(dir, e.name), rel)));
    else out.push(rel);
  }
  return out;
}
const files = (await listFiles(OUT)).filter((f) => f !== 'sw.js');
const hash = createHash('sha1');
for (const f of files.sort()) hash.update(f).update(await readFile(path.join(OUT, f)));
const precache = files.flatMap((f) => (f.endsWith('index.html') ? [f.replace(/index\.html$/, '') || './'] : [f]));
await writeFile(
  path.join(OUT, 'sw.js'),
  `// Automatski generisano (build.mjs)
const CACHE = 'opstanak-${hash.digest('hex').slice(0, 10)}';
const FILES = ${JSON.stringify(precache)};
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
`
);

console.log(`Izgrađeno ${pages.length} stranica -> docs/ (${files.length} fajlova u kešu za offline)`);
