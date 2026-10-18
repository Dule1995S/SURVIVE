export default function SiteFooter({ name, tagline }) {
  return (
    <footer className="border-t border-line bg-surface py-8 text-[.92rem] text-muted print:hidden">
      <div className="wrap">
        <p className="my-1.5 max-w-[80ch]">
          <strong>{name}</strong> — {tagline}. Sadržaj je edukativan i ne zamenjuje obuku, lekara ni zvanična uputstva
          nadležnih službi. U stvarnoj opasnosti prvo slušaj uputstva Sektora za vanredne situacije i zovi{' '}
          <strong>112</strong>.
        </p>
        <p className="my-1.5 text-[.85rem]">
          <a href="/o-projektu/">O projektu</a> · <a href="/srbija/">Korisni brojevi</a>
        </p>
      </div>
    </footer>
  );
}
