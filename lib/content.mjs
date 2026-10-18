// Zajednička logika za sadržaj: koristi je i build.mjs (statički sajt u docs/) i Next.js (app/).
// src/pages/**.html (sa front matter-om) -> stranice sa HTML sadržajem
import { readdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
export const SRC = path.join(ROOT, 'src');

export const site = JSON.parse(await readFile(path.join(SRC, 'site.json'), 'utf8'));

export const esc = (s = '') =>
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
export const pages = [];
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

// Sadržaj unutar <main>: zaglavlje stranice, sadržaj, „prethodno / sledeće". Linkovi ostaju apsolutni.
export function renderContent(page) {
  const { body, headings } = processBody(page.body);
  const m = page.meta;
  const sectionKey = page.segs[0] || '';
  const sectionTitle = site.sections[sectionKey]?.title;

  if (m.bare === 'true') return body;

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

  return `<div class="wrap">
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

export const pageTitle = (page) =>
  page.url === '/' ? `${site.name} — ${site.tagline}` : `${page.meta.title} · ${site.name}`;

export const pageDescription = (page) => page.meta.summary || page.meta.description || site.description;
