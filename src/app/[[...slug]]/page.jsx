import Script from 'next/script';
import { site, pages, renderContent, pageTitle, pageDescription } from '../../../lib/content.mjs';

// Sve stranice dolaze iz src/pages/ i prave se unapred; nepoznate putanje daju 404.
export const dynamicParams = false;

export function generateStaticParams() {
  return pages.map((p) => ({ slug: p.segs }));
}

const findPage = async (params) => {
  const { slug = [] } = await params;
  return pages.find((p) => p.segs.join('/') === slug.map(decodeURIComponent).join('/'));
};

export async function generateMetadata({ params }) {
  const page = await findPage(params);
  const title = pageTitle(page);
  const description = pageDescription(page);
  return { title, description, openGraph: { title, description } };
}

export default async function Page({ params }) {
  const page = await findPage(params);
  const sectionKey = page.segs[0] || '';

  return (
    <>
      <a className="skip" href="#main">Pređi na sadržaj</a>
      <header className="site-header">
        <div className="wrap bar">
          <a className="brand" href="/">
            <img src="/assets/icon.svg" alt="" width="28" height="28" />
            <span>{site.name}</span>
          </a>
          <button className="nav-toggle" aria-expanded="false" aria-controls="site-nav">Meni</button>
          <nav id="site-nav" className="site-nav" aria-label="Glavna navigacija">
            <ul>
              {site.nav.map((n) => (
                <li key={n.href}>
                  <a href={n.href} aria-current={sectionKey && n.section === sectionKey ? 'true' : undefined}>
                    {n.title}
                  </a>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      </header>
      <main id="main" dangerouslySetInnerHTML={{ __html: renderContent(page) }} />
      <footer className="site-footer">
        <div className="wrap">
          <p>
            <strong>{site.name}</strong> — {site.tagline}. Sadržaj je edukativan i ne zamenjuje obuku, lekara ni
            zvanična uputstva nadležnih službi. U stvarnoj opasnosti prvo slušaj uputstva Sektora za vanredne situacije
            i zovi <strong>112</strong>.
          </p>
          <p className="small">
            <a href="/o-projektu/">O projektu</a> · <a href="/srbija/">Korisni brojevi</a>
          </p>
        </div>
      </footer>
      {page.meta.script && <Script src={`/assets/${page.meta.script}`} strategy="afterInteractive" />}
    </>
  );
}
