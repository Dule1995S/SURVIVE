import './globals.css';
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
    <html lang="sr">
      <body>{children}</body>
    </html>
  );
}
