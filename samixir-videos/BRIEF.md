---
workflow: general-video
flow: automation
storyboard: no
message: "Samixir aparati za napitke: jedan proizvod, tri ključne prednosti, poruči na samixir.rs"
destination: reels-tiktok
aspect: 1080x1920
language: sr-Cyrl
audience: HoReCa (kafići, restorani, hoteli, ketering)
length: 20s
angle: product-benefits
---

## Intent

Četiri vertikalna promo videa od po 20s za Samixir opremu za napitke (SLUSH Triple, KAM22,
HOT SC06, PANORAMIC M10) za Instagram Reels i TikTok. Jedan šablon (`index.html`) za sve,
a promenljiva `product` bira proizvod. Stil: čist slideshow sa motion grafikom, premium
B2B ketering osećaj, „Apple product reveal“ prilagođen profesionalnoj opremi. Statične fotke
proizvoda sa elegantnim pokretima kamere, bez AI animacije proizvoda.

Svaki video ima 5 scena: Hook 0–4s, Prednost 1 4–9s, Prednost 2 9–14s, Prednost 3 14–18s,
CTA 18–20s. Tekst je preuzet iz korisnikovog paketa promptova.

## Assets

- assets/src/slush-triple.jpg — SLUSH Triple (3×12L granita), originalna fotka
- assets/src/kam22.jpg — KAM22 (22L ajran sa penom), originalna fotka
- assets/src/hot-sc06.jpg — HOT SC06 (6L topli napici), originalna fotka
- assets/src/panoramic-m10.jpg — PANORAMIC M10 (10L hladni napici), originalna fotka
- assets/src/samixir-logo.png — Samixir logo sa sloganom; za video se koristi samo wordmark (assets/brand/samixir-wordmark.png)
- assets/products/*.png — proizvodi isečeni sa bele pozadine (tools/cutout.py)

## Customizations

- Brand paleta: #F5F7FA pozadina, #0A2540 navy, #FFC72C žuta, #1A1A1A tekst, pastelni krugovi #DCE9F5 / #E8F2EC
- Font: Inter (variable, ćirilica), lokalno ugrađen
- Muzika: sintetizovana podloga, 120 BPM, bez vokala (tools/synth.py), sa prelazima na smenama scena
- Efekti po proizvodu: brojevi posuda, noćni disk, iskrice (SLUSH); prsten na slavini, hlađenje, orbita mešanja (KAM22);
  para, orbita mešanja, prsten na LED indikatoru (HOT); orbita mešanja, hlađenje, prsten na slavini (M10)

## Notes

- Bez crtica (em-dash) u tekstu po brand pravilu. Crtice iz originalnog teksta su zamenjene tačkom ili zarezom.
- „Беин-мари“ ispravljeno u „Бен-мари“ (srpska transkripcija za bain-marie).
- Drugi red naslova je navy tekst na žutoj traci. Žut tekst na svetloj pozadini bi bio nečitljiv (ne prolazi WCAG kontrast).
- Logo je ~20% širine ekrana umesto 5% iz brifa. Sa 5% (54px) bio bi nečitljiv na telefonu.
- Sve tvrdnje (50% manje struje, magnetna lopatica itd.) su iz korisnikovog teksta, nisu proveravane.
