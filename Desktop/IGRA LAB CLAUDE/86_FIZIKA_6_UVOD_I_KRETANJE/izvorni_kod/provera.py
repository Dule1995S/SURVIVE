"""Провере пре испоруке.  python3 provera.py

PDF: број и величина страна, уграђени фонтови, цртице, латиница само за
дозвољене ознаке, забрањене речи, мушки род. HTML: ознаке величина
курзивом, јединице усправно са нераздвојивим размаком, минус само у
формулама, децимални зарез, разломци за брзину, редослед задатака,
цртежи и поновни рачун свих решења.
"""

import os
import re
import subprocess
import sys

import build as B
import crtezi as C

FILES = {k: os.path.join(B.OUT, B.NAME.format(k) + ".pdf") for k in ("KOMPLET_COLOR", "KOMPLET_CRNO-BELO", "RESENJA")}
DASHES = "–—―"
MINUS = "−"
BANNED = ["савршен", "пажњ", "љубав", "трансформ", "безбедн", "без компромиса", "сигур"]
MASC = [r"\bси\s+\w+(?:ао|ио|ео|уо)\b", r"\w+(?:ао|ио)\s+си\b", r"/\s*-?\s*ла\b", r"\(\s*-?ла\s*\)",
        r"\bсам/сама\b", r"\bспреман\b", r"\bистраживач[аеу]\b"]
# дозвољене латиничне ознаке: величине (курзивом) и јединице (усправно)
QTY = {"s", "t", "v", "a", "S", "V", "m", "l"}
UNIT = {"m", "cm", "dm", "mm", "km", "s", "min", "h", "ms", "kg", "C"}
ALLOWED = QTY | UNIT | {"IGRA", "LAB"}
WRONG_EXAMPLE = "a=5cm"          # намерно погрешан запис у задатку 20
CYR = "а-яА-ЯђјљњћџЂЈЉЊЋЏ"
errors = []


def check(ok, msg):
    print(("  ок  " if ok else "  ГРЕШКА  ") + msg)
    if not ok:
        errors.append(msg)


def text_of(path):
    return subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True).stdout


def html_text(html):
    """Видљиви текст без ознака и без SVG атрибута."""
    import html as H
    t = re.sub(r"<style.*?</style>|<title>.*?</title>", "", html, flags=re.S)
    return H.unescape(re.sub(r"<[^>]+>", " ", t))


print("рачуни")
try:
    n = B.proveri_racune()
    check(True, f"{n} рачуна поново израчунато у коду, сви одговарају решењима")
except SystemExit:
    check(False, "рачун у решењима се не слаже са поновљеним рачуном")

for tag, path in FILES.items():
    print(f"\n{os.path.basename(path)}")
    check(os.path.exists(path), "фајл постоји")
    info = subprocess.run(["pdfinfo", path], capture_output=True, text=True).stdout
    pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    w, h = map(float, re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", info).groups())
    if tag.startswith("KOMPLET"):
        check(19 <= pages <= 23, f"{pages} страна (тражи се 19 до 23)")
    else:
        check(pages >= 1, f"{pages} страна решења")
    check(abs(w - 595.3) < 0.1 and abs(h - 841.9) < 0.1, f"A4 {w} x {h} pt")
    fonts = subprocess.run(["pdffonts", path], capture_output=True, text=True).stdout.splitlines()[2:]
    names = sorted({l.split()[0].split("+")[-1] for l in fonts})
    check(fonts and all(" yes " in l for l in fonts), "сви фонтови уграђени: " + ", ".join(names))
    check(not any("Type 3" in l for l in fonts), "нема Type3 фонтова")
    check(all(n.startswith(("Lora-Bold", "FiraSans")) for n in names), "само Lora Bold и Fira Sans")

    t = text_of(path)
    low = t.lower()
    bad_d = [c for c in DASHES if c in t]
    check(not bad_d, "нема цртица – — ―" + (f" (нађено: {bad_d})" if bad_d else ""))
    check("-" not in t, "нема цртице ни у једној речи")
    toks = set(re.findall(r"[A-Za-z]+", t))
    check(toks <= ALLOWED | {"cm"}, "латиница само у дозвољеним ознакама: " + " ".join(sorted(toks))
          + ("" if toks <= ALLOWED else f" (вишак: {sorted(toks - ALLOWED)})"))
    mixed = re.findall(rf"[A-Za-z][{CYR}]|[{CYR}][A-Za-z]", t)
    check(not mixed, "нема мешања ћирилице и латинице у речи" + (f" (нађено: {mixed[:5]})" if mixed else ""))
    dots = [m.group(0) for m in re.finditer(r"(?<!лекција )\d+\.\d", t)]
    check(not dots, "децимални зарез, не тачка" + (f" (нађено: {dots[:5]})" if dots else ""))
    found = [w for w in BANNED if w in low]
    check(not found, "нема забрањених речи" + (f" (нађено: {found})" if found else ""))
    masc = [m.group(0) for p in MASC for m in re.finditer(p, low)]
    check(not masc, "нема обраћања у мушком роду" + (f" (нађено: {masc})" if masc else ""))

for label, pages in (("свеска", B.workbook()), ("решења", B.solutions())):
    html = B.doc(pages, "x")
    print(f"\nзапис у HTML ({label})")
    body = re.sub(r"<svg.*?</svg>", lambda m: re.sub(r"<(?!text|tspan|/text|/tspan)[^>]+>", "", m.group(0)), html, flags=re.S)
    # минус само у формулама (формула не садржи друге <span>, па се затвара првим </span>)
    total = html_text(html).count(MINUS)
    fml_spans = re.findall(r'<span class="fml">.*?</span>', html, flags=re.S)
    outside = re.sub(r'<span class="fml">.*?</span>', " ", html, flags=re.S)
    check(MINUS not in html_text(outside) and total > 0,
          f"минус само у формулама ({total} знака у {len(fml_spans)} формула)")
    # величине курзивом: t, v, a, S, V, l ван курзива нису дозвољене
    txt = re.sub(r'<i class="qv">[A-Za-zΔ]+</i>|<tspan style="font-style:italic">[A-Za-z]+</tspan>', " ", body)
    txt = html_text(txt)
    txt = txt.replace(WRONG_EXAMPLE, " ")
    stray = sorted(set(w for w in re.findall(r"[A-Za-z]+", txt) if w in {"t", "v", "a", "S", "V", "l"}))
    check(not stray, "ознаке величина курзивом" + (f" (усправно нађено: {stray})" if stray else ""))
    rest = sorted(set(re.findall(r"[A-Za-z]+", txt)) - UNIT - {"IGRA", "LAB", "m"})
    check(not rest, "остала латиница су само јединице" + (f" (вишак: {rest})" if rest else ""))
    glued = re.findall(r"\d(?:mm|cm|dm|km|ms|min|kg|m|s|h)\b", txt)
    check(not glued, "између броја и јединице има размака" + (f" (нађено: {glued[:5]})" if glued else ""))
    no_svg = re.sub(r"<svg.*?</svg>", " ", html, flags=re.S)       # у SVG су број и јединица посебни натписи
    plain_sp = re.findall(r"\d (?:mm|cm|dm|km|ms|min|kg|m|s|h)\b", html_text(no_svg))
    check(not plain_sp, "размак број–јединица је нераздвојив" + (f" (нађено: {plain_sp[:5]})" if plain_sp else ""))
    sl = re.findall(r"\b(?:km|cm|m)/(?:h|s|min)\b", html_text(html))
    check(not sl, "брзина у m/s и km/h сложена као прави разломак" + (f" (нађено: {sl[:5]})" if sl else ""))

print("\nсадржај свеске")
html = "".join(B.workbook())
ids = [int(x) for x in re.findall(r'class="task" data-id="(\d+)"', html)]
check(ids == list(range(1, 51)), f"задаци 1 до 50, редом ({len(ids)} задатака)")
calc_tasks = [n for n in range(1, 51) if 'class="calc"' in B.T[n]]
check(set(B.KIND[n] for n in (21, 25, 43, 48, 49)) == {"Израчунај"} and set((21, 25, 43, 48, 49)) <= set(calc_tasks),
      "сви задаци Израчунај имају поље Подаци, Рачун, Одговор: " + ", ".join(map(str, calc_tasks)))
check(html.count(">ЗАПАМТИ<") == 6, "шест оквира ЗАПАМТИ")
check(html.count(">ОГЛЕД КОД КУЋЕ<") == 1, "оквир ОГЛЕД КОД КУЋЕ без броја")
check(B.T[45].count('class="accf"') >= 5 and B.T[46].count('class="accf"') == 0, "дијаграм 45 има пет тачака, права 46 је празна")
check([2 * t for t in C.KOLICA_T] == [0, 2, 4, 6, 8], "тачке на 0, 2, 4, 6 и 8 m")
check((C.PLAN_DESNO, C.PLAN_GORE, C.PLAN_POLJE_M) == (6, 4, 50), "план 6 × 4 поља, страница 50 m")
check((C.ODMOR_T1, C.ODMOR_T2) == ((10, 50), (11, 5)), "сатови 10 h 50 min и 11 h 05 min")
sol = "".join(B.solutions())
check(all(f'<div class="tn">{n}</div>' in sol for n in range(1, 51)), "решења за свих 50 задатака")
check("690" in sol and "2 430" in sol.replace(B.NB, " ") and "44" in sol and "37,58" in sol, "напомена: сонда Паркер и Болт")
check("није званични уџбеник" in sol, "напомена за одрасле на последњој страни решења")

print("\n" + ("СВЕ ПРОВЕРЕ ПРОШЛЕ" if not errors else f"{len(errors)} ГРЕШКА(Е)"))
sys.exit(1 if errors else 0)
