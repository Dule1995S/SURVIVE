"""Провере пре испоруке.  python3 provera.py

Проверава три PDF-а у ../FINALNO и HTML из build.py:
број и величину страна, уграђене фонтове, цртице, латиницу,
забрањене речи, обраћање у мушком роду, редослед задатака
и да сваки број на цртежу има своје поље за одговор.
"""

import os
import re
import subprocess
import sys

import build as B

OUT = B.OUT
FILES = {k: os.path.join(OUT, B.NAME.format(k) + ".pdf") for k in ("KOMPLET_COLOR", "KOMPLET_CRNO-BELO", "RESENJA")}
DASHES = "−–—―"
BANNED = ["савршен", "пажњ", "љубав", "трансформ", "безбедн", "без компромиса", "сигур"]
MASC = [r"\bси\s+\w+(?:ао|ио|ео|уо)\b", r"\w+(?:ао|ио)\s+си\b", r"/\s*-?\s*ла\b", r"\(\s*-?ла\s*\)",
        r"\bсам/сама\b", r"\bспреман\b", r"\bистраживач[аеу]\b"]
errors = []


def check(ok, msg):
    print(("  ок  " if ok else "  ГРЕШКА  ") + msg)
    if not ok:
        errors.append(msg)


def text_of(path):
    return subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True).stdout


for tag, path in FILES.items():
    print(f"\n{os.path.basename(path)}")
    check(os.path.exists(path), "фајл постоји")
    info = subprocess.run(["pdfinfo", path], capture_output=True, text=True).stdout
    pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    size = re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", info)
    w, h = float(size.group(1)), float(size.group(2))
    if tag.startswith("KOMPLET"):
        check(19 <= pages <= 23, f"{pages} страна (тражи се 19 до 23)")
    else:
        check(pages >= 1, f"{pages} страна решења")
    check(abs(w - 595.3) < 0.1 and abs(h - 841.9) < 0.1, f"A4 {w} x {h} pt")
    fonts = subprocess.run(["pdffonts", path], capture_output=True, text=True).stdout.splitlines()[2:]
    names = sorted({l.split()[0].split("+")[-1] for l in fonts})
    check(all(" yes " in l for l in fonts) and fonts, "сви фонтови уграђени: " + ", ".join(names))
    check(not any("Type 3" in l for l in fonts), "нема Type3 фонтова")
    check(all(n.startswith(("Lora-Bold", "FiraSans")) for n in names), "само Lora Bold и Fira Sans")

    t = text_of(path)
    low = t.lower()
    bad_d = [c for c in DASHES if c in t]
    check(not bad_d, "нема цртица " + " ".join(DASHES) + (f" (нађено: {bad_d})" if bad_d else ""))
    hy = [m.group(0) for m in re.finditer(r"\S*-\S*", t) if m.group(0).strip("„“.,;:()") != "угљен-диоксид"]
    check(not hy, "цртица само у „угљен-диоксид“" + (f" (нађено: {hy[:5]})" if hy else ""))
    # латиница сме да чини само IGRA LAB; кружни текст печата pdftotext
    # чита испремештаним редом, па се пореди састав слова, а не редослед
    from collections import Counter
    seq = "".join(re.findall(r"[A-Za-z]", t)).replace("IGRALAB", "")
    cnt, unit = Counter(seq), Counter("IGRALAB")
    k = cnt["B"]
    ok = all(cnt[ch] == unit[ch] * k for ch in set(cnt) | set(unit))
    check(ok, "само ћирилица осим IGRA LAB" + ("" if ok else f" (вишак латинице: {seq[:30]})"))
    found = [w for w in BANNED if w in low]
    check(not found, "нема забрањених речи" + (f" (нађено: {found})" if found else ""))
    masc = [m.group(0) for p in MASC for m in re.finditer(p, low)]
    check(not masc, "нема обраћања у мушком роду" + (f" (нађено: {masc})" if masc else ""))

print("\nсадржај свеске")
html = "".join(B.workbook())
ids = [int(x) for x in re.findall(r'class="task" data-id="(\d+)"', html)]
check(ids == list(range(1, 51)), f"задаци 1 до 50, редом ({len(ids)} задатака)")


def block(n):
    s = html.index(f'data-id="{n}"')
    e = html.find('class="task" data-id=', s + 10)
    return html[s:e if e > 0 else None]


for n in (14, 32, 46):
    b = block(n)
    nums = len(re.findall(r'class="ncirc"', b))
    fields = len(re.findall(r'class="lr"', b))
    check(nums == fields == 4, f"задатак {n}: бројева на цртежу {nums}, поља {fields}")
b = block(34)
check(len(re.findall(r'class="ltext"', b)) == 4 and b.count('rx="1.2" style="fill:#fff') == 4, "задатак 34: слова А до Г и 4 поља")
b = block(40)
check(b.count('rx="1.2" style="fill:#fff') == 4 and b.count("<b>") == 4, "задатак 40: 4 облика, 4 поља, 4 назива")
b = block(3)
check(b.count('rx="1.6" style="fill:#fff') == 5, "задатак 3: 5 поља на степеницама")
b = block(47)
check(b.count('class="ink" style="stroke-width:.35" d="M') == 2, "задатак 47: две празне линије за натпис")
check(html.count(">ЗАПАМТИ<") == 5, "пет оквира ЗАПАМТИ")
check(html.count(">КОД КУЋЕ<") == 2, "оквири КОД КУЋЕ без броја")

sol = "".join(B.solutions())
check(all(f'<div class="tn">{n}</div>' in sol for n in range(1, 51)), "решења за свих 50 задатака")
check("вибрили" in sol and "вибриони" in sol, "у решењима оба назива: вибриони и вибрили")
check("није званични уџбеник" in sol, "напомена за одрасле на последњој страни решења")

print("\n" + ("СВЕ ПРОВЕРЕ ПРОШЛЕ" if not errors else f"{len(errors)} ГРЕШКА(Е)"))
sys.exit(1 if errors else 0)
