import Script from 'next/script';
import SiteHeader from '../../components/SiteHeader';
import SiteFooter from '../../components/SiteFooter';
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

  return (
    <>
      <a
        href="#main"
        className="absolute top-0 -left-[999px] z-[100] bg-accent px-4 py-2 text-accent-ink focus:left-0 print:hidden"
      >
        Pređi na sadržaj
      </a>
      <SiteHeader name={site.name} nav={site.nav} sectionKey={page.segs[0] || ''} />
      <main id="main" dangerouslySetInnerHTML={{ __html: renderContent(page) }} />
      <SiteFooter name={site.name} tagline={site.tagline} />
      {page.meta.script && <Script src={`/assets/${page.meta.script}`} strategy="afterInteractive" />}
    </>
  );
}
