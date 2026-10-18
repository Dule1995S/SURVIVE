'use client';

import { useState } from 'react';

export default function SiteHeader({ name, nav, sectionKey }) {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-line bg-bg/92 backdrop-blur-md before:block before:h-[5px] before:bg-[repeating-linear-gradient(-45deg,var(--accent)_0_12px,#111_12px_24px)] before:content-[''] print:hidden">
      <div className="wrap relative flex min-h-14 items-center justify-between gap-4">
        <a href="/" className="inline-flex items-center gap-2.5 font-extrabold tracking-[.08em] text-fg uppercase no-underline">
          <img src="/assets/icon.svg" alt="" width="28" height="28" />
          <span>{name}</span>
        </a>
        <button
          type="button"
          className="cursor-pointer rounded-lg border border-line bg-surface-2 px-3.5 py-1.5 font-semibold text-fg md:hidden"
          aria-expanded={open}
          aria-controls="site-nav"
          onClick={() => setOpen(!open)}
        >
          Meni
        </button>
        <nav
          id="site-nav"
          aria-label="Glavna navigacija"
          className={`${open ? 'block' : 'hidden'} absolute inset-x-0 top-full border-b border-line bg-bg px-4 pt-2 pb-4 md:static md:block md:border-0 md:bg-transparent md:p-0`}
        >
          <ul className="m-0 flex list-none flex-col gap-1 p-0 md:flex-row md:flex-wrap">
            {nav.map((n) => (
              <li key={n.href}>
                <a
                  href={n.href}
                  aria-current={sectionKey && n.section === sectionKey ? 'true' : undefined}
                  className="block rounded-lg px-3 py-2 text-[.95rem] font-semibold text-fg no-underline hover:bg-surface-2 aria-[current]:bg-accent aria-[current]:text-accent-ink"
                >
                  {n.title}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </header>
  );
}
