# Opstanak — vodič za preživljavanje (Srbija)

Edukativni sajt na srpskom jeziku (latinica, ekavica): šta raditi u slučaju nuklearne opasnosti, pandemije,
prirodnih katastrofa, dugog nestanka struje i raspada sistema, koje su veštine najvažnije i kako napraviti
plan i zalihe za porodicu.

- 5 scenarija (sa procenom rizika, „pre krize" i „kada se desi")
- 9 veština po prioritetu (svaka sa ciljem lekcije i vežbom)
- Kalkulator zaliha i interaktivna lista za proveru (čuva se samo u pregledaču, može da se odštampa)
- Stranica „Srbija": hitni brojevi, institucije, lokalne specifičnosti
- Radi **offline** (service worker) i može da se instalira na telefon

## Pokretanje

Bez zavisnosti, potreban je samo Node 18+ (i Python za lokalni server):

```bash
npm run build     # src/ -> docs/
npm run serve     # build + http://localhost:8080
```

Izgrađeni sajt je u `docs/` (komitovan), pa može direktno na GitHub Pages (Settings → Pages → `main` / `docs`).
Za `sitemap.xml` i `canonical` linkove upiši adresu u `src/site.json` (`"url"`).

### Next.js

Isti sadržaj (`src/pages/`) može da se pokreće i kroz Next.js (App Router, `src/app/`). Potreban je Node 20.9+:

```bash
npm install
npm run dev          # Next.js dev server: http://localhost:3000
npm run next:build   # produkcijski build (sve stranice se prave unapred)
npm start            # pokreće produkcijski build
```

- `src/app/[[...slug]]/page.jsx` pravi po jednu stranicu za svaki fajl iz `src/pages/`.
- Logika za čitanje i obradu sadržaja je u `lib/content.mjs` i dele je Next.js i `build.mjs`.
- `src/assets/` se pre pokretanja kopira u `public/assets/` (`npm run assets`).
- Offline keš (service worker) i `docs/` za GitHub Pages i dalje pravi samo `npm run build`.
- **Tailwind CSS v4** (`src/app/globals.css`): boje sajta su dostupne kao klase (`bg-surface`, `text-muted`,
  `border-line`, `bg-accent`, `text-accent-ink`…) i prate svetlu/tamnu temu. Preflight reset je namerno isključen
  da ne pokvari HTML sadržaj; `style.css` je u sloju `components`, pa Tailwind klase uvek imaju prednost.
  Zaglavlje i podnožje su u `src/components/` i napisani su Tailwind klasama.

## Kako dodati sadržaj

Svaka stranica je jedan HTML fajl u `src/pages/` sa zaglavljem:

```html
---
title: Naziv u kartici i meniju
heading: (opciono) duži naslov H1
summary: Opis od 100–160 karaktera (koristi se kao meta opis i uvod)
icon: 🔥
order: 5
---
<h2>Prvi naslov</h2>
<p>Tekst…</p>
```

- `src/pages/scenariji/*.html` i `src/pages/vestine/*.html` se automatski pojavljuju na početnoj i u indeksima
  (po polju `order`), uz „prethodno / sledeće" navigaciju.
- Linkovi se pišu apsolutno (`/vestine/voda/`), generator ih pretvara u relativne.
- Gotovi blokovi: `callout` (`warn`, `tip`, `note`), `exercise` (vežba), tabele, `{{cards:scenariji}}`.
- `<h2>` naslovi automatski dobijaju sidra i „Sadržaj stranice".

## Napomena o sadržaju

Brojeve hitnih službi i nazive institucija povremeno proveri na zvaničnim sajtovima.
Sajt je edukativan i ne zamenjuje obuku, lekara ni uputstva nadležnih službi.
