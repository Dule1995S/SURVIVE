"""HTML -> PDF преко Chromium-а (Playwright) и извештај о слободном простору.

    python3 render.py sveska.html            само извештај
    python3 render.py sveska.html izlaz.pdf  извештај и PDF

За сваку страну исписује слободан простор до футера у mm
(негативан број значи да садржај прелива). Пре штампе допуњује линије:
где на страни остане места, у поље означено са data-grow додаје линије
од 8,5 mm, колико стане. Проверава и да ниједан елемент не излази из
свог блока ни у зону од 10 mm од ивице листа.
"""

import os
import sys

from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter

# Chromium: ако постоји локална инсталација из CHROME, користи се она,
# иначе Playwright-ов (python3 -m playwright install chromium).
CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
A4 = (595.2756, 841.8898)   # 210 x 297 mm у тачкама


def fix_a4(path, title):
    """Chromium заокружује лист на цео пиксел (594,96 x 841,92 pt).
    Овде се свака страна скалира на тачну меру A4, разлика је 0,05 %."""
    rd = PdfReader(path)
    w = PdfWriter()
    for pg in rd.pages:
        pg.scale_to(*A4)
        w.add_page(pg)
    for pg in w.pages:
        pg.compress_content_streams()
    w.add_metadata({"/Title": title, "/Author": "IGRA LAB", "/Creator": "IGRA LAB build.py"})
    with open(path, "wb") as fh:
        w.write(fh)

JS_MEASURE = r"""
(fill) => {
  const MM = 96 / 25.4;
  const LH = 8.5 * MM;
  const out = [];
  const pages = [...document.querySelectorAll('.page')];
  function free(pg) {
    const body = pg.querySelector('.body');
    if (!body) return null;
    const ref = body.getBoundingClientRect().bottom;
    let bottom = body.getBoundingClientRect().top;
    for (const ch of body.children) bottom = Math.max(bottom, ch.getBoundingClientRect().bottom);
    return (ref - bottom) / MM;
  }
  pages.forEach((pg, i) => {
    let added = 0, slack = null;
    if (fill) {
      // 1) линије: где остане места, наизменично у поља data-grow на тој страни
      const gs = [...pg.querySelectorAll('[data-grow]')];
      let fr = free(pg);
      if (gs.length && fr !== null) {
        const n = Math.floor((fr * MM - 1.2) / LH);
        for (let k = 0; k < n; k++) {
          const d = document.createElement('div'); d.className = 'ln'; gs[k % gs.length].appendChild(d); added++;
        }
      }
      slack = free(pg);
      // 2) остатак мањи од линије (или страна без поља за линије) иде у једнаке размаке међу блоковима
      const body = pg.querySelector('.body');
      fr = free(pg);
      if (body && fr > 0 && body.children.length > 1 && !pg.classList.contains('cover')) {
        const g0 = parseFloat(getComputedStyle(body).rowGap) / MM;
        const ex = Math.min(fr / (body.children.length - 1), 6);
        body.style.rowGap = (g0 + ex - 0.05) + 'mm';
      }
    }
    const fr = free(pg);
    const P = pg.getBoundingClientRect();
    const zone = 10 * MM, tol = 0.3 * MM;
    const bad = [];
    pg.querySelectorAll('*').forEach(el => {
      if (el.closest('defs, clipPath, pattern')) return;
      const r = el.getBoundingClientRect();
      if (r.width === 0 && r.height === 0) return;
      if (r.left < P.left + zone - tol || r.right > P.right - zone + tol ||
          r.top < P.top + zone - tol || r.bottom > P.bottom - zone + tol)
        bad.push('зона: ' + (el.className.baseVal ?? el.className) + ' ' + el.tagName);
      const blk = el.parentElement && el.parentElement.closest('.task, .remember, .home, .opener, .qbox, .note, .solcard, .map, .steps');
      if (blk) {
        const B = blk.getBoundingClientRect();
        if (r.left < B.left - tol || r.right > B.right + tol || r.top < B.top - tol || r.bottom > B.bottom + tol)
          bad.push('блок ' + (blk.dataset.id || blk.className) + ': ' + el.tagName + '.' + (el.className.baseVal ?? el.className));
      }
    });
    // текст који не стаје у свој ред
    pg.querySelectorAll('.task *, .remember *, .home *').forEach(el => {
      if (el.scrollWidth > el.clientWidth + 1 && getComputedStyle(el).overflow !== 'visible' && el.tagName !== 'svg')
        bad.push('прелив текста: ' + el.className);
    });
    out.push({page: i + 1, free: fr, slack: slack, added: added, bad: [...new Set(bad)].slice(0, 6)});
  });
  return out;
}
"""


def render(html_path, pdf_path=None, fill=True, quiet=False, title="IGRA LAB"):
    url = "file://" + os.path.abspath(html_path)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME) if os.path.exists(CHROME) else p.chromium.launch()
        pg = b.new_page(viewport={"width": 794, "height": 1123})
        pg.goto(url)
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(200)
        rep = pg.evaluate(JS_MEASURE, fill)
        if pdf_path:
            pg.pdf(path=pdf_path, prefer_css_page_size=True, print_background=True,
                   margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        b.close()
    if pdf_path:
        fix_a4(pdf_path, title)
    if not quiet:
        print(f"{os.path.basename(html_path)}: {len(rep)} страна")
        for r in rep:
            fr = "  ---" if r["free"] is None else f"{r['free']:6.1f} mm"
            if r.get("slack") is not None and r["free"] is not None and r["slack"] - r["free"] > 0.3:
                fr += f"  (остатак {r['slack']:.1f} mm раздељен у размаке)"
            add = f"  +{r['added']} лин." if r["added"] else ""
            print(f"  стр. {r['page']:2d}: слободно {fr}{add}")
            for x in r["bad"]:
                print("        ! " + x)
    return rep


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
