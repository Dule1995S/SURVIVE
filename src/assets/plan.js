(() => {
  const STORE_KEY = 'opstanak.checklist.v1';

  // ---------- kalkulator ----------
  const people = document.getElementById('calc-people');
  const days = document.getElementById('calc-days');
  const out = document.getElementById('calc-out');
  const nf = new Intl.NumberFormat('sr-Latn-RS', { maximumFractionDigits: 1 });

  function calc() {
    const p = Math.min(20, Math.max(1, parseInt(people.value, 10) || 1));
    const d = parseInt(days.value, 10);
    const water = p * d * 3;
    const kcal = p * d * 2200;
    const food = p * d * 0.65;
    const salt = p * d * 0.005;
    const cells = [
      [nf.format(water) + ' L', 'vode', `oko ${Math.ceil(water / 5)} flaša od 5 L`],
      [nf.format(food) + ' kg', 'suve hrane', 'pirinač, testenina, grah, brašno, ulje…'],
      [new Intl.NumberFormat('sr-Latn-RS').format(kcal) + ' kcal', 'ukupno kalorija', '2200 kcal po osobi dnevno'],
      [nf.format(salt) + ' kg', 'soli', 'plus šećer, začini, čaj'],
    ];
    out.innerHTML = cells.map(([v, l, s]) => `<div><b>${v}</b>${l}<br><small>${s}</small></div>`).join('');
  }
  if (people && days && out) {
    people.addEventListener('input', calc);
    days.addEventListener('change', calc);
    calc();
  }

  // ---------- lista ----------
  const GROUPS = [
    {
      id: 'torba',
      title: 'Torba za evakuaciju (72 sata)',
      note: 'Spakovana, na vidljivom mestu pored vrata. Obnavljaj jednom u šest meseci.',
      items: [
        ['Voda 1,5–2 L po osobi', 'plus tablete ili filter za prečišćavanje'],
        ['Hrana koja se ne kvari', 'energetske pločice, orasi, suvo voće, konzerve sa otvaranjem na prsten'],
        ['Baterijska lampa (čeona) i rezervne baterije'],
        ['Radio na baterije ili dinamo'],
        ['Powerbank (napunjen) i kablovi'],
        ['Komplet prve pomoći', 'zavoji, gaze, antiseptik, podvez, rukavice'],
        ['Lekovi za hroničnu terapiju', 'najmanje 7 dana'],
        ['Topla odeća u slojevima, kabanica, kapa, rukavice, rezervne čarape'],
        ['Termo folija ili vreća za spavanje'],
        ['Upaljač, šibice u vodootpornoj kesi, kresivo'],
        ['Nož ili multi-alat'],
        ['FFP2/N95 maske i rukavice'],
        ['Higijena', 'sapun, vlažne maramice, toalet papir, higijenski ulošci'],
        ['Gotovina u sitnim apoenima'],
        ['Kopije dokumenata u vodootpornoj kesi', 'lična karta, pasoš, zdravstvena knjižica, polise, USB'],
        ['Papirna mapa kraja i kompas'],
        ['Zvižduk'],
        ['Spisak kontakata na papiru'],
        ['Za bebe i decu: pelene, formula, igračka. Za ljubimce: hrana i povodac'],
      ],
    },
    {
      id: 'kuca',
      title: 'Kućne zalihe (2 nedelje)',
      note: 'Dopuni redom: voda, hrana, toplota, svetlo, higijena.',
      items: [
        ['Voda: 3 L po osobi dnevno', 'vidi kalkulator iznad'],
        ['Hrana za 14 dana', 'pirinač, testenina, grah, konzerve, ulje, so, šećer'],
        ['Rešo na gas i rezervne kartuše ili boca'],
        ['Drva ili drugi ogrev za zimu, očišćen dimnjak'],
        ['Detektor ugljen-monoksida'],
        ['Aparat za gašenje požara i detektor dima'],
        ['Hlor (varikina bez mirisa) ili tablete za vodu'],
        ['Kante, vreće za smeće, piljevina ili pepeo (toalet bez vode)'],
        ['Rezervne lampe, sveće u staklu, baterije'],
        ['Alat: čekić, klešta, odvijač, lopata, sečivo'],
        ['Pokrivači i vreće za spavanje za sve ukućane'],
        ['Lekovi za 30 dana, termometar, oksimetar, rastvor za rehidrataciju'],
        ['Rezervne naočare ili sočiva'],
      ],
    },
    {
      id: 'plan',
      title: 'Porodični plan i znanje',
      note: 'Najjeftinija i najvažnija grupa. Za nju ti ne treba novac, samo vreme.',
      items: [
        ['Dogovoreno mesto okupljanja blizu kuće i van naselja'],
        ['Kontakt van mesta u kome živimo, kojem se svi javljamo'],
        ['Znam gde su ventili za gas i vodu i osigurač za struju'],
        ['Izabrano mesto za zaklon u kući (zemljotres, nuklearna opasnost)'],
        ['Probna evakuacija izvedena sa porodicom'],
        ['Završen kurs prve pomoći (barem jedan član porodice)'],
        ['Znam kako se prečišćava voda i uradio sam probu'],
        ['Znam da zapalim vatru i skuvam obrok bez struje'],
        ['Znam brojeve hitnih službi i imam ih na papiru'],
        ['Dogovoreno šta radimo sa starijim, bolesnim i ljubimcima'],
      ],
    },
    {
      id: 'dokumenta',
      title: 'Dokumenta, novac i zajednica',
      note: 'Kada nema sistema, vrede gotovina i ljudi koje poznaješ.',
      items: [
        ['Originali i kopije važnih dokumenata na jednom mestu'],
        ['Gotovina za najmanje nedelju dana'],
        ['Fotografije članova porodice (za slučaj razdvajanja)'],
        ['Znam komšije i ko im je od pomoći (lekar, mehaničar, majstor)'],
        ['Dogovor sa rođacima na selu ili vikendicom'],
        ['Rezervni ključevi kod poverljive osobe'],
      ],
    },
  ];

  const root = document.getElementById('checklists');
  if (!root) return;

  let state = {};
  try { state = JSON.parse(localStorage.getItem(STORE_KEY) || '{}'); } catch (e) { state = {}; }
  const save = () => { try { localStorage.setItem(STORE_KEY, JSON.stringify(state)); } catch (e) {} };

  const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  root.innerHTML = GROUPS.map((g) => `
    <section class="list-group" data-group="${g.id}">
      <h3>${esc(g.title)} <span class="badge" data-count="${g.id}"></span></h3>
      <p class="small-note">${esc(g.note)}</p>
      <div class="progress" aria-hidden="true"><i data-bar="${g.id}"></i></div>
      <ul class="checklist">
        ${g.items.map((it, i) => {
          const id = `${g.id}-${i}`;
          return `<li><label><input type="checkbox" id="${id}" ${state[id] ? 'checked' : ''}><span>${esc(it[0])}${it[1] ? `<small>${esc(it[1])}</small>` : ''}</span></label></li>`;
        }).join('')}
      </ul>
    </section>`).join('');

  function update() {
    let done = 0, total = 0;
    for (const g of GROUPS) {
      const n = g.items.length;
      const c = g.items.filter((_, i) => state[`${g.id}-${i}`]).length;
      done += c; total += n;
      root.querySelector(`[data-count="${g.id}"]`).textContent = `${c}/${n}`;
      root.querySelector(`[data-bar="${g.id}"]`).style.width = `${(c / n) * 100}%`;
    }
    document.getElementById('overall-bar').style.width = `${(done / total) * 100}%`;
    document.getElementById('overall-text').textContent = `Ukupno završeno: ${done} od ${total} stavki (${Math.round((done / total) * 100)}%).`;
  }

  root.addEventListener('change', (e) => {
    if (e.target.matches('input[type=checkbox]')) {
      state[e.target.id] = e.target.checked;
      save();
      update();
    }
  });
  document.getElementById('print-btn').addEventListener('click', () => window.print());
  document.getElementById('reset-btn').addEventListener('click', () => {
    if (!confirm('Poništiti sve štikle?')) return;
    state = {};
    save();
    root.querySelectorAll('input[type=checkbox]').forEach((c) => (c.checked = false));
    update();
  });
  update();
})();
