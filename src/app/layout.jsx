import Script from 'next/script';
import { site } from '../../lib/content.mjs';

export const metadata = {
  title: `${site.name} — ${site.tagline}`,
  description: site.description,
  icons: { icon: { url: '/assets/icon.svg', type: 'image/svg+xml' } },
  openGraph: { type: 'website', locale: 'sr_RS' },
};

export const viewport = { themeColor: '#0f1210' };

export default function RootLayout({ children }) {
  return (
    // data-no-sw: offline keš (sw.js) pravi samo build.mjs za docs/
    <html lang="sr" data-no-sw="">
      <head>
        <link rel="stylesheet" href="/assets/style.css" />
      </head>
      <body>
        {children}
        <Script src="/assets/site.js" strategy="afterInteractive" />
      </body>
    </html>
  );
}
