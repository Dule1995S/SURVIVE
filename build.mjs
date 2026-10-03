#!/usr/bin/env node
// Mali generator statičkog sajta, bez zavisnosti.
// src/pages/**.html (sa front matter-om) + src/layout.html  ->  docs/
import { readdir, readFile, writeFile, mkdir, rm, cp } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const SRC = path.join(ROOT, 'src');
const OUT = path.join(ROOT, 'docs');

const site = JSON.parse(await readFile(path.join(SRC, 'site.json'), 'utf8'));
const layout = await readFile(path.join(SRC, 'layout.html'), 'utf8');

const esc = (s = '') =>
  String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const DIACRITICS = { č: 'c', ć: 'c', š: 's', ž: 'z', đ: 'dj' };
const slugify = (s) =>
  s
    .toLowerCase()
    .replace(/[čćšžđ]/g, (c) => DIACRITICS[c])
    .replace(/<[^>]+>/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');

function parse(raw) {
  raw = raw.replace(/\r\n/g, '\n');
  const m = raw.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  if (!m) return { meta: {}, body: raw };
  const meta = {};
  for (const line of m[1].split('\n')) {
    const i = line.indexOf(':');
    if (i > 0) meta[line.slice(0, i).trim()] = line.slice(i + 1).trim();
  }
  return { meta, body: m[2] };
}

async function walk(dir, base = '') {
  const out = [];
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const rel = path.posix.join(base, e.name);
    if (e.isDirectory()) out.push(...(await walk(path.join(dir, e.name), rel)));
    else if (e.name.endsWith('.html')) out.push(rel);
  }
  return out;
}

// ---------- učitavanje stranica ----------
const pages = [];
for (const rel of await walk(path.join(SRC, 'pages'))) {
  const { meta, body } = parse(await readFile(path.join(SRC, 'pages', rel), 'utf8'));
  const segs = rel.replace(/\.html$/, '').split('/');
  const isIndex = segs[segs.length - 1] === 'index';
  if (isIndex) segs.pop();
  pages.push({
    rel,
    meta,
    body,
    isIndex,
    inSection: segs.length > 1,
    segs,
    url: '/' + segs.join('/') + (segs.length ? '/' : ''),
    outFile: path.join(OUT, ...segs, 'index.html'),
    depth: segs.length,
  });
}

const byOrder = (a, b) => Number(a.meta.order ?? 99) - Number(b.meta.order ?? 99);
const sectionPages = (section) =>
  pages.filter((p) => p.inSection && p.segs[0] === section && !p.isIndex).sort(byOrder);

function cards(section) {
  const ranked = site.sections[section]?.ranked;
  return (
    '<div class="cards">' +
    sectionPages(section)
      .map(
        (p) => `<a class="card" href="${p.url}">
  <span class="card-top"><span class="card-icon" aria-hidden="true">${p.meta.icon || '•'}</span>${
    ranked ? `<span class="badge">Prioritet ${p.meta.order}</span>` : ''
  }</span>
  <h3>${esc(p.meta.title)}</h3>
  <p>${esc(p.meta.summary || '')}</p>
</a>`
      )
      .join('\n') +
    '</div>'
  );
}

// ---------- obrada sadržaja ----------
function processBody(body) {
  body = body.replace(/\{\{cards:([a-z-]+)\}\}/g, (_, s) => cards(s));
  const headings = [];
  body = body.replace(/<h2>([\s\S]*?)<\/h2>/g, (_, inner) => {
    const id = slugify(inner);
    headings.push({ id, text: inner.replace(/<[^>]+>/g, '') });
    return `<h2 id="${id}">${inner}</h2>`;
  });
  return { body, headings };
}

const readingMinutes = (html) =>
  Math.max(1, Math.round(html.replace(/<[^>]+>/g, ' ').split(/\s+/).filter(Boolean).length / 190));

function render(page) {
  const root = page.depth === 0 ? './' : '../'.repeat(page.depth);
  const { body, headings } = processBody(page.body);
  const m = page.meta;
  const sectionKey = page.segs[0] || '';
  const sectionTitle = site.sections[sectionKey]?.title;

  let content = '';
  if (m.bare === 'true') {
    content = body;
  } else {
    const crumbs = [`<a href="/">Početna</a>`];
    if (page.inSection && sectionTitle) crumbs.push(`<a href="/${sectionKey}/">${esc(sectionTitle)}</a>`);
    crumbs.push(`<span aria-current="page">${esc(m.title)}</span>`);
    const minutes = page.isIndex ? '' : `<span>⏱ ${readingMinutes(body)} min čitanja</span>`;
    const toc =
      headings.length >= 3 && m.toc !== 'false'
        ? `<details class="toc"><summary>Sadržaj stranice</summary><ol>${headings
            .map((h) => `<li><a href="#${h.id}">${esc(h.text)}</a></li>`)
            .join('')}</ol></details>`
        : '';

    let pager = '';
    if (page.inSection && !page.isIndex) {
      const list = sectionPages(sectionKey);
      const i = list.indexOf(page);
      const prev = list[i - 1];
      const next = list[i + 1];
      pager = `<nav class="pager" aria-label="Sledeća i prethodna stranica">
  ${prev ? `<a class="prev" href="${prev.url}"><small>← Prethodno</small>${esc(prev.meta.title)}</a>` : '<span></span>'}
  ${next ? `<a class="next" href="${next.url}"><small>Sledeće →</small>${esc(next.meta.title)}</a>` : '<span></span>'}
</nav>`;
    }

    content = `<div class="wrap">
  <header class="page-head">
    <nav class="crumbs" aria-label="Putanja">${crumbs.join('<span aria-hidden="true">›</span>')}</nav>
    <p class="eyebrow">${esc(m.eyebrow || sectionTitle || '')}</p>
    <h1>${esc(m.heading || m.title)}</h1>
    ${m.summary ? `<p class="lead">${esc(m.summary)}</p>` : ''}
    <p class="meta">${minutes}</p>
  </header>
  <article class="page">
    ${toc}
    ${body}
    ${pager}
  </article>
</div>`;
  }

  const nav = site.nav
    .map(
      (n) =>
        `<li><a href="${n.href}"${n.section === sectionKey && sectionKey ? ' aria-current="true"' : ''}>${esc(n.title)}</a></li>`
    )
    .join('');

  const title = page.url === '/' ? `${site.name} — ${site.tagline}` : `${m.title} · ${site.name}`;
  const description = m.summary || m.description || site.description;
  const script = m.script ? `<script src="/assets/${m.script}" defer></script>` : '';

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
  await mkdir(path.dirname(p.outFile), { recursive: true });
  await writeFile(p.outFile, render(p));
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
