"""IGRA LAB · ИСТРАЖИВАЧ 12+ · Физика 6 · Увод у физику и кретање

    python3 build.py c   свеска у боји
    python3 build.py b   свеска црно бело
    python3 build.py r   решења и смернице
    python3 build.py     све три

PDF иде у ../FINALNO/, а render.py исписује слободан простор по страни.
Пре сваког прављења сви рачуни из решења се поново израчунају
(proveri_racune); ако се иједан разликује, build стаје.
"""

import os
import re
import sys

import crtezi as C
from render import render

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "FINALNO")
NAME = "IGRALAB_FIZIKA-6_UVOD-I-KRETANJE_{}_v01"
NB = " "

CEL = [  # кључ, језичак, наслов, лекција, задаци
    ("fiz", "ФИЗИКА", "Физика и природа", "лекција 1.1", "1 до 9"),
    ("met", "МЕТОД", "Како физика проучава природу?", "лекција 1.2", "10 до 17"),
    ("vel", "ВЕЛИЧИНЕ", "Физичке величине, мерење и мерне јединице", "лекција 1.3", "18 до 26"),
    ("kre", "КРЕТАЊЕ", "Кретање у свакодневном животу, релативност кретања", "лекција 2.1", "27 до 33"),
    ("put", "ПУТАЊА", "Путања и пут", "лекција 2.2", "34 до 42"),
    ("brz", "БРЗИНА", "Време и приказивање кретања, брзина", "лекција 2.3", "43 до 50"),
    ("zav", "ЗАВРШНА", "Завршна", "", ""),
]
CNUM = {k: i + 1 for i, (k, *_) in enumerate(CEL)}

# ------------------------------------------------------------------ типографија физике
# *s* -> ознака величине курзивом; јединице остају усправне;
# 5 cm -> нераздвојив размак; m/s, km/h, cm/s -> прави разломак;
# 300 000 -> хиљаде одвојене нераздвојивим размаком.

UNITS = r"(?:mm|cm|dm|km|ms|min|kg|m²|m³|cm²|cm³|m|s|h|°C)"


def typo(html):
    parts = re.split(r"(<svg.*?</svg>)", html, flags=re.S)
    for i in range(0, len(parts), 2):
        t = parts[i]
        t = re.sub(r"\*([A-Za-zΔ]+)\*", r'<i class="qv">\1</i>', t)
        t = re.sub(r"(?<![A-Za-z])(km|cm|m)/(h|s|min)(?![A-Za-z])",
                   r'<span class="fr"><span>\1</span><span>\2</span></span>', t)
        t = re.sub(r"(\d) (\d{3})(?!\d)", r"\1" + NB + r"\2", t)
        t = re.sub(r"(\d) (?=" + UNITS + r"(?![A-Za-z²³]))", r"\1" + NB, t)
        t = re.sub(r"(\d) (?=<span class=\"fr\">)", r"\1" + NB, t)
        parts[i] = t
    return "".join(parts)


def fml(t):
    """Формула: једино место где сме да стоји знак минус."""
    return f'<span class="fml">{t}</span>'


def br(x, dec=None):
    """Број са децималним зарезом: 0.5 -> 0,5; 300000 -> 300 000."""
    if dec is not None:
        s = f"{x:.{dec}f}"
    elif float(x).is_integer():
        s = str(int(x))
    else:
        s = f"{x:.10g}"
    ip, _, dp = s.partition(".")
    neg = ip.startswith("-")
    ip = ip.lstrip("-")
    groups = []
    while len(ip) > 3:
        groups.insert(0, ip[-3:])
        ip = ip[:-3]
    groups.insert(0, ip)
    out = NB.join(groups) if len(groups) > 1 and len("".join(groups)) > 4 else "".join(groups)
    return ("−" if neg else "") + out + ("," + dp if dp else "")


# ------------------------------------------------------------------ помоћне функције


def blank(w=34):
    return f'<span class="blank" style="width:{w}mm"></span>'


def lines(n, grow=False, labels=None):
    g = ' data-grow="1"' if grow else ""
    labels = labels or []
    rows = "".join(f'<div class="ln">{l}</div>' for l in labels) + '<div class="ln"></div>' * (n - len(labels))
    return f'<div class="lines{" lab" if labels else ""}"{g}>{rows}</div>'


def task(n, kind, body):
    return (f'<div class="task" data-id="{n}"><div class="th"><div class="tn">{n}</div>'
            f'<div class="tk">{kind}</div></div>{body}</div>')


def p(t, cls="tt"):
    return f'<p class="{cls}">{t}</p>'


def hint(t):
    return f'<p class="hint">{t}</p>'


def chips(words, boxed=True):
    return f'<div class="chips{" boxed" if boxed else ""}">' + "".join(f"<span>{w}</span>" for w in words) + "</div>"


def opts(items, col=False, gap=None):
    st = f' style="gap:{gap}mm"' if gap else ""
    return (f'<div class="opts{" col" if col else ""}"{st}>'
            + "".join(f"<span><b>{a})</b>{t}</span>" for a, t in items) + "</div>")


def match(left, right, lw=52):
    l = "".join(f'<div><span>{x}</span><span class="box"></span></div>' for x in left)
    r = "".join(f"<div><b>{a})</b>{t}</div>" for a, t in right)
    return (f'<div class="match" style="grid-template-columns:{lw}mm 1fr"><div class="left">{l}</div>'
            f'<div class="right">{r}</div></div>')


def tf(rows, boxes=True, cols=1):
    box = '<span class="box"></span>' if boxes else ""
    return f'<div class="tf{" g2" if cols == 2 else ""}">' + "".join(f'<div class="row"><span>{r}</span>{box}</div>' for r in rows) + "</div>"


def sub(t):
    return f'<p class="sublab">{t}</p>'


def fig(s):
    return f'<div class="fig">{s}</div>'


def calc(racun=2, grow=True):
    """Поље за рачунски задатак у три реда: подаци, рачун, одговор."""
    return ('<div class="calc">'
            f'<div class="cl">ПОДАЦИ</div><div class="cv">{lines(1)}</div>'
            f'<div class="cl">РАЧУН</div><div class="cv">{lines(racun, grow=grow)}</div>'
            f'<div class="cl">ОДГОВОР</div><div class="cv">{lines(1)}</div></div>')


def order(n):
    cells = '<span class="lt">&lt;</span>'.join('<span class="box"></span>' for _ in range(n))
    return f'<div class="order">{cells}</div>'


def grid_table(head, rows, widths, nlines=1, rowh=None):
    th = "".join(f"<th>{h}</th>" for h in head)
    rh = f' style="height:{rowh}mm"' if rowh else ""
    out = f'<table class="grid"><tr>{th}</tr>'
    for r in rows:
        out += f"<tr{rh}>"
        for k, cell in enumerate(r):
            w = widths[k]
            if cell is None:
                out += f'<td class="w" style="width:{w}mm">' + '<div class="ln"></div>' * nlines + "</td>"
            elif k == 0:
                out += f'<td class="rh" style="width:{w}mm">{cell}</td>'
            else:
                out += f'<td class="c" style="width:{w}mm">{cell}</td>'
        out += "</tr>"
    return out + "</table>"


def remember(t):
    return f'<div class="remember"><h3>ЗАПАМТИ</h3><p>{t}</p></div>'


def opener(key):
    _, tab, title, lesson, rng = CEL[CNUM[key] - 1]
    return (f'<div class="opener"><div class="onum"><b>{CNUM[key]}</b><span>ЦЕЛИНА</span></div>'
            f'<div><h1>{title}</h1><p>{lesson} · задаци {rng}</p></div></div>')


# ------------------------------------------------------------------ задаци

T = {}

# ЦЕЛИНА 1 · ФИЗИКА
T[1] = task(1, "Допуни", p(
    f"Наука је скуп сазнања и могућих објашњења којима {blank(36)} уочене и {blank(36)} нове појаве.", "fill"))
T[2] = task(2, "Допуни", p(f"Реч физика долази од грчке речи „физис“, која значи {blank(40)}.", "fill"))
T[3] = task(3, "Заокружи", p("Заокружи природне науке:") + chips(["физика", "историја", "хемија", "српски језик", "биологија"]))
T[4] = task(4, "Допиши", p("Ластавица лети изнад реке. Која наука проучава њен лет, а која наука проучава како ради њено срце?")
            + sub("Лет ластавице") + lines(1, grow=True) + sub("Рад срца") + lines(1, grow=True))
T[5] = task(5, "Заокружи", p("Заокружи објективне описе.") + tf([
    "1. Муња је прелепа.", "2. Ивица коцке је дуга 5 cm.", "3. Коцка је ружно обојена.", "4. Маса коцке је 0,094 kg."], boxes=False))
T[6] = task(6, "Допуни", p(f"Материја се јавља у два облика: као {blank(40)} и као {blank(40)}.", "fill"))
T[7] = task(7, "Табела", p("Допуни табелу.") + grid_table(
    ["ФИЗИЧКО ТЕЛО", "СУПСТАНЦА", "ФИЗИЧКО ПОЉЕ"],
    [["завртањ и магнет", None, None], ["оловка и планета Земља", None, None], ["пластични штап и папирићи", None, None]],
    [52, 58, 50], nlines=4))
T[8] = task(8, "Тачно/нетачно", p("Напиши Т или Н, нетачну исправи.") + tf([
    "1. Магнет делује на завртањ само ако га додирује.",
    "2. Физичка тела имају свој облик и заузимају део простора."]) + sub("Исправка") + lines(2, grow=True))
T[9] = task(9, "Допиши", p("Наведи по један пример појаве из сваке групе: механичка, електрична, магнетна, светлосна.")
            + "".join(sub(g) + lines(1, grow=True) for g in ["Механичка", "Електрична", "Магнетна", "Светлосна"]))

# ЦЕЛИНА 2 · МЕТОД
T[10] = task(10, "Допуни", p(f"Најстарији начин на који се у физици проучавају природне појаве је {blank(48)}.", "fill"))
T[11] = task(11, "Допиши", p("Којим чулима опажаш олују са муњом? Зашто прво видиш муњу, а тек онда чујеш гром?")
             + sub("Чула") + lines(1, grow=True) + sub("Зашто прво видиш муњу") + lines(2, grow=True))
T[12] = task(12, "Заокружи", p("Згужвани лист папира и оловка пуштени су истовремено са исте висине. Шта ће се десити?") + opts([
    ("а", "Оловка пада раније јер има већу масу."), ("б", "Падају на тло готово истовремено."), ("в", "Папир пада раније.")], col=True))
T[13] = task(13, "Повежи", p("Повежи научника са доприносом.") + hint("Слово доприноса упиши у поље поред научника.") + match(
    ["Галилео Галилеј", "Никола Тесла"], [
        ("А", "Међу првима је употребио телескоп за посматрање неба и открио Јупитерове сателите."),
        ("Б", "Допринео је развоју електричних мотора, радиотехнике и даљинског управљања.")], lw=56))
T[14] = task(14, "Допиши", p("Зашто раван лист папира пада спорије од оловке, а згужван лист пада готово истовремено са њом?")
             + lines(3, grow=True))
T[15] = task(15, "Поређај", p("Поређај бројевима 1 до 4 пут од посматрања до практичне примене:") + hint("Број упиши у поље.") + tf([
    "практична примена", "експеримент", "непосредно посматрање", "физички закон или теорија"]))
T[16] = task(16, "Допуни", p(
    f"Предност експеримента у односу на непосредно посматрање је могућност {blank(40)}. Експерименти се изводе "
    f"под {blank(40)} условима, најчешће у {blank(40)}.", "fill"))
T[17] = task(17, "Повежи", p("Повежи уређај са применом у медицини.") + hint("Слово примене упиши у поље поред уређаја.") + match(
    ["Ултразвучни уређај", "Ласер", "Рендген апарат"], [
        ("А", "прецизне хируршке операције"), ("Б", "преглед повређеног зглоба"), ("В", "снимање костију")], lw=56))

# ЦЕЛИНА 3 · ВЕЛИЧИНЕ
T[18] = task(18, "Допуни", p(
    f"Мерење је упоређивање непознате вредности физичке величине са познатом {blank(46)} те исте физичке величине.", "fill"))
T[19] = task(19, "Табела", p("Допуни табелу. Неке ћелије су већ попуњене.") + grid_table(
    ["ВЕЛИЧИНА", "ОЗНАКА", "МЕРНА ЈЕДИНИЦА", "ОЗНАКА ЈЕДИНИЦЕ"],
    [["дужина", None, "метар", None], ["маса", "*m*", None, None], ["време", None, None, "s"],
     ["површина", "*S*", None, None], ["запремина", None, "метар кубни", None]],
    [36, 34, 54, 40], rowh=15))
T[20] = task(20, "Заокружи", p("Заокружи исправан запис дужине ивице коцке:") + opts([
    ("а", "a=5cm"), ("б", "*a* = 5 cm"), ("в", "*a* = 5 цм")], gap=14))
T[21] = task(21, "Израчунај", p("Ивица коцке је *a* = 4 cm. Израчунај површину једне стране, укупну површину и запремину коцке.")
             + calc(3))
T[22] = task(22, "Заокружи", p("Заокружи пар међусобно зависних физичких величина:") + opts([
    ("а", "дужина ивице коцке и запремина коцке"), ("б", "маса коцке и температура у учионици")], col=True))
T[23] = task(23, "Разврстај", p("Разврстај у основне и изведене физичке величине:")
             + chips(["дужина", "површина", "време", "запремина", "маса", "брзина"])
             + '<div class="sort"><div><h4>ОСНОВНЕ</h4>' + lines(3) + '</div><div><h4>ИЗВЕДЕНЕ</h4>' + lines(3) + "</div></div>")
T[24] = task(24, "Заокружи", p("Подвуци реченице које говоре о временском тренутку, а заокружи оне које говоре о временском интервалу.")
             + tf(["1. Час почиње у 8 h.", "2. Одмор траје 20 min.", "3. Воз полази у 7 h 45 min.", "4. Лет је трајао 2 h 54 min."], boxes=False, cols=2))
T[25] = task(25, "Израчунај", p(
    "Сатови показују почетак и крај одмора: *t*₁ = 10 h 50 min и *t*₂ = 11 h 05 min. Колико траје одмор? Запиши као "
    + fml("Δ*t* = *t*₂ − *t*₁") + ".") + fig(C.clocks()) + calc(2))
T[26] = task(26, "Допиши", p("Опиши своју свеску објективно: наведи три физичке величине са бројном вредношћу и мерном јединицом.")
             + grid_table(["", "ФИЗИЧКА ВЕЛИЧИНА", "БРОЈНА ВРЕДНОСТ И ЈЕДИНИЦА"],
                          [["1.", None, None], ["2.", None, None], ["3.", None, None]], [12, 74, 78]))

# ЦЕЛИНА 4 · КРЕТАЊЕ
T[27] = task(27, "Допуни", p(f"Механичко кретање је промена {blank(40)} неког тела у односу на {blank(40)} тела.", "fill"))
T[28] = task(28, "Допуни", p(
    f"Тело у односу на које одређујемо положај и посматрамо кретање других тела зове се {blank(36)} или {blank(36)} тело.", "fill"))
T[29] = task(29, "Заокружи", p("Ана седи у аутобусу који вози. У односу на шта Ана мирује?")
             + opts([("а", "пут"), ("б", "аутобус"), ("в", "дрво поред пута")]))
T[30] = task(30, "Тачно/нетачно", p("Напиши Т или Н, нетачну исправи.") + tf([
    "1. Табла мирује у односу на зид учионице.", "2. Табла мирује у односу на Сунце.", "3. Постоји апсолутно мировање."])
             + sub("Исправка") + lines(2, grow=True))
T[31] = task(31, "Допиши", '<div class="side"><div>' + p(
    "На лоптици је нацртан „чича Глиша“. Лоптица пада на под. Да ли се чича Глиша креће у односу на лоптицу? А у односу на под?")
             + sub("У односу на лоптицу") + lines(1, grow=True) + sub("У односу на под") + lines(1, grow=True)
             + f"</div><div>{C.ball_face()}</div></div>")
T[32] = task(32, "Допиши", p("Напиши референтно тело:") + lines(3, labels=[
    "чамац плови поред мола:", "птица лети ка дрвету:", "воз пролази кроз станицу:"]))
T[33] = task(33, "Допиши", p("Објасни релативност кретања на примеру путника у возу.") + lines(4, grow=True))

# ЦЕЛИНА 5 · ПУТАЊА
T[34] = task(34, "Допуни", p(
    f"Путања или трајекторија је стварна или {blank(40)} линија коју тело, или део тела, описује током кретања.", "fill"))
T[35] = task(35, "Заокружи", p("Заокружи праволинијска кретања:") + chips([
    "ласерски зрак", "авион који на аеромитингу прави петље", "лифт од приземља до трећег спрата",
    "кошаркашка лопта бачена ка кошу", "камен пуштен да слободно пада"]))
T[36] = task(36, "Путање", p("Бицикл вози праволинијски. На траци нацртај путању осовине точка једном бојом, а путању вентила "
                             "на гуми другом бојом. По чему се разликују?") + fig(C.wheel_strip()) + lines(2, grow=True))
T[37] = task(37, "Путање", p("На плану нацртај најкраћу путању по улицама од куће А до школе Б. Страница поља је 50 m. "
                             "Колики пут прелазиш?") + fig(C.plan()) + calc(1))
T[38] = task(38, "Допуни", p(
    f"Пређени пут је {blank(32)} дела путање између две претходно одабране тачке. Означава се словом {blank(20)}, "
    f"а основна мерна јединица је {blank(32)}.", "fill"))
T[39] = task(39, "Поређај", p("Поређај мерне јединице за дужину од најмање до највеће: km, cm, m, mm, dm.") + order(5))


def pick(rows):
    return '<div class="pick">' + "".join(
        f'<div class="row"><span>{a}</span><span class="ch"><span>{x}</span><span>{y}</span></span></div>' for a, x, y in rows) + "</div>"


T[40] = task(40, "Заокружи", p("Заокружи погоднију јединицу.") + pick([
    ("Пут од Новог Сада до Београда:", "m", "km"), ("Дужина мрава:", "mm", "km"),
    ("Дужина учионице:", "m", "km"), ("Ширина свеске:", "cm", "km")]))
T[41] = task(41, "Заокружи", p("Заокружи случајеве у којима тело можемо посматрати као материјалну тачку:") + opts([
    ("а", "Земља док кружи око Сунца"), ("б", "аутомобил на путу од Београда до Ниша"),
    ("в", "аутомобил док се паркира у гаражу")], col=True))
T[42] = task(42, "Допиши", p("Зашто Земљу можемо посматрати као материјалну тачку када посматрамо њено кретање око Сунца?")
             + lines(3, grow=True))

# ЦЕЛИНА 6 · БРЗИНА
T[43] = task(43, "Израчунај", p("Аутобус креће у 6 h 50 min, а стиже у 8 h 05 min. Колико траје вожња?") + calc(2))
T[44] = task(44, "Поређај", p("Поређај јединице за време од најмање до највеће: s, ms, h, min, стотинка.") + order(5))
T[45] = task(45, "Дијаграм", p("На дијаграму кретања колица положаји су обележени сваке секунде. Колики пут колица пређу "
                               "за 4 s? Колика је њихова брзина?") + fig(C.motion_diagram()) + calc(2))
T[46] = task(46, "Дијаграм", p("Ученик хода стално брзином 1 m/s. На правој обележи његов положај у тренуцима 0 s, 2 s, "
                               "4 s, 6 s, 8 s и 10 s.") + hint("Положај обележи тачком, а изнад тачке упиши тренутак.")
             + fig(C.number_line()))
T[47] = task(47, "Заокружи", p("Плави бициклиста пређе 60 m за 10 s, а зелени 60 m за 12 s. Заокружи бржег и израчунај обе брзине.")
             + chips(["плави бициклиста", "зелени бициклиста"]) + calc(2))
T[48] = task(48, "Израчунај", p("Воз пређе 180 km за 2 h. Израчунај брзину у km/h, па је изрази у m/s.") + calc(2))
T[49] = task(49, "Израчунај", p("Пуж се креће брзином 1,3 cm/s. Колики пут пређе за 1 минут?") + calc(2))
T[50] = task(50, "Допиши", p("Мој пут до школе: уз помоћ одраслог сазнај колико је дуг твој пут до школе и колико траје. "
                             "Нацртај скицу путање и израчунај своју брзину.")
             + '<div class="sketch">скица путање</div>' + calc(2))

assert sorted(T) == list(range(1, 51))

# ------------------------------------------------------------------ оквири

ZAP = {
    "fiz": "Физика је природна наука која проучава материју и појаве у природи. Материја постоји као супстанца "
           "и као физичко поље. Објективан опис садржи податак који свако може да провери, на пример: маса коцке је *m* = 0,094 kg.",
    "met": "Физичари природу проучавају посматрањем и експериментом. Експеримент се изводи под контролисаним условима и "
           "може да се понови. Пример записа: згужван лист и оловка пуштени са висине од 1 m падну на под готово истовремено.",
    "vel": "Физичка величина је особина тела или појаве која може да се измери. Резултат мерења пишемо као ознаку, "
           "број и мерну јединицу: " + fml("*a* = 5 cm") + ", при чему је ознака искошена, јединица усправна, а између броја и јединице је размак.",
    "kre": "Тело се креће ако мења положај у односу на референтно тело. Кретање и мировање су релативни, зависе од "
           "избора референтног тела. Пример: путник мирује у односу на воз, а креће се у односу на станицу.",
    "put": "Путања је линија коју тело описује док се креће, а пређени пут је дужина дела путање. Пут означавамо словом "
           "*s*, а основна јединица је метар. Пример записа: *s* = 500 m.",
    "brz": "Брзина показује колики пут тело пређе за јединицу времена: " + fml("*v* = *s* : *t*") + ". Основна јединица "
           "је метар у секунди, а често се користи и километар на час. Пример записа: *s* = 8 m, *t* = 4 s, *v* = 2 m/s.",
}

HOME = (f'<div class="home"><div><h3>ОГЛЕД КОД КУЋЕ</h3>'
        '<p>Узми два иста листа папира и оловку. Са исте висине пусти истовремено раван лист и оловку. Затим један лист '
        'згужвај у лоптицу и пусти га истовремено са оловком. Запиши шта видиш.</p>'
        + sub("Раван лист и оловка") + lines(1, grow=True) + sub("Згужван лист и оловка") + lines(1, grow=True)
        + f'</div><div class="ico">{C.drop_icon()}</div></div>')

# ------------------------------------------------------------------ стране


def tabs(active):
    active = active if isinstance(active, (list, tuple)) else [active]
    return '<div class="tabs">' + "".join(
        f'<div class="tab{" on" if k in active else ""}" style="--tc:var(--c-{k})">{tab}</div>' for k, tab, *_ in CEL) + "</div>"


def header(sol):
    st2 = "РЕШЕЊА И СМЕРНИЦЕ" if sol else "ЗА ШЕСТИ РАЗРЕД"
    return (f'<div class="head"><div class="brand">{C.stamp(13)}<div><div class="bt1">IGRA LAB</div>'
            f'<div class="bt2">ИСТРАЖИВАЧ</div></div></div>'
            f'<div class="subj"><div class="st1">ФИЗИКА 6</div><div class="st2">{st2}</div></div></div>')


def page(key, inner, num, sol=False, active=None):
    active = key if active is None else active
    return (f'<section class="page {key}">{header(sol)}{tabs(active)}<div class="body">{inner}</div>'
            f'<div class="foot"><span class="ft">УВОД У ФИЗИКУ И КРЕТАЊЕ</span>'
            f'<span class="pn">{num}</span></div></section>')


def cover():
    strip = "".join(f'<span style="--tc:var(--c-{k})">{tab}</span>' for k, tab, *_ in CEL[:6])
    return (f'<section class="page cover zav"><div class="ctop"><div class="brand">{C.stamp(17)}'
            f'<div><div class="bt1">IGRA LAB</div><div class="bt2">ИСТРАЖИВАЧ 12+</div></div></div>'
            f'<div class="subj"><div class="st1">ФИЗИКА 6</div><div class="st2">ЗА ШЕСТИ РАЗРЕД</div></div></div>'
            f'<div class="body" style="gap:0;padding-top:0">'
            f'<div><span class="mis">МИСИЈА 01 · УВОД И КРЕТАЊЕ</span>'
            f'<h1>ФИЗИКА 6</h1>'
            f'<h2>Увод у физику и кретање</h2>'
            f'<p class="csub">Истраживачка радна свеска · 50 задатака у шест целина</p></div>'
            f'<div class="cart">{C.cover_art()}</div>'
            f'<div><div class="cstrip">{strip}</div>'
            f'<div class="owner"><div>ОВА СВЕСКА ПРИПАДА</div><div>ОДЕЉЕЊЕ</div></div></div>'
            f'</div></section>')


def mission_map():
    return '<div class="map">' + "".join(
        f'<div class="mc" style="--tc:var(--c-{k})"><div class="mh">{tab}</div>'
        f'<div class="mb"><b>Целина {i + 1}</b>{lesson}<br>задаци {rng}</div></div>'
        for i, (k, tab, _, lesson, rng) in enumerate(CEL[:6])) + "</div>"


def intro(num):
    inner = (
        '<div class="intro"><h1>Пре него што кренеш</h1></div>'
        '<p class="lede">У овој мисији упознајеш физику: како посматра природу, како мери и како описује кретање. '
        'На крају ћеш умети да израчунаш колико брзо се нешто креће.</p>'
        '<div class="qbox"><div class="ql">ИСТРАЖИВАЧКО ПИТАЊЕ</div>'
        '<div class="q">Зашто прво видимо муњу, а тек онда чујемо гром?</div></div>'
        '<div class="task" data-id="pre"><p class="tt">Запиши шта сада мислиш. На крају свеске вратићеш се овом питању '
        'и упоредити одговоре.</p>' + lines(5, grow=True) + "</div>"
        + mission_map() +
        '<div class="steps">'
        '<div><b>Пиши ознаке тачно</b>Ознака величине је искошена, јединица усправна, а између броја и јединице је размак: ' + fml("*a* = 5 cm") + '.</div>'
        '<div><b>Рачунај у три корака</b>Код рачунских задатака попуни редом: подаци, рачун, одговор.</div>'
        '<div><b>Провери се</b>Решења су у посебној свесци. Отвори их тек када завршиш целину.</div>'
        '</div>')
    return page("zav", inner, num, active="")


def final(num):
    checks = [
        "Објашњавам шта проучава физика и шта је материја.",
        "Разликујем непосредно посматрање и експеримент.",
        "Пишем физичку величину са ознаком, бројем и мерном јединицом.",
        "Одређујем да ли се тело креће у односу на референтно тело.",
        "Разликујем путању и пређени пут.",
        "Рачунам брзину као " + fml("*v* = *s* : *t*") + " и пишем је у m/s и km/h.",
    ]
    ch = "".join(f'<div><span class="box"></span><span>{c}</span></div>' for c in checks)
    inner = (
        f'<div class="final-stamp">{C.mission_stamp(58)}</div>'
        '<div class="qbox"><div class="ql">ВРАТИ СЕ НА ИСТРАЖИВАЧКО ПИТАЊЕ</div>'
        '<div class="q">Зашто прво видимо муњу, а тек онда чујемо гром?</div></div>'
        '<div class="task" data-id="kraj"><p class="tt">Одговори поново, сада уз оно што знаш после ове мисије. '
        'Употреби речи <b>светлост</b>, <b>звук</b> и <b>брзина</b>.</p>' + lines(4, grow=True) + "</div>"
        '<div class="task" data-id="znam"><p class="sublab" style="margin-top:0">Шта сада знам</p>'
        '<p class="hint">Означи поље поред онога што умеш да објасниш другу или другарици.</p>'
        f'<div class="check">{ch}</div></div>')
    return page("zav", inner, num)


def back():
    return (f'<section class="page cover back zav"><div class="body" style="padding-top:0;gap:7mm;justify-content:center">'
            f'<div style="display:flex;justify-content:center">{C.stamp(46)}</div>'
            f'<div style="text-align:center"><div class="bt1" style="font-size:22pt">IGRA LAB</div>'
            f'<div class="bt2" style="font-size:9pt">ИСТРАЖИВАЧ 12+</div></div>'
            f'<p class="lede" style="text-align:center;max-width:150mm;margin:0 auto">Свеске ИСТРАЖИВАЧ 12+ воде кроз градиво '
            f'као кроз мисију: прво истраживачко питање, па задаци, огледи и рачуни, па одговор на крају.</p>'
            + mission_map() +
            f'<div class="steps"><div><b>50 задатака</b>Допуни, заокружи, повежи, поређај, нацртај путању и израчунај.</div>'
            f'<div><b>Рачун у три корака</b>Подаци, рачун и одговор, са ознакама и мерним јединицама.</div>'
            f'<div><b>Решења</b>Решења и смернице за одрасле налазе се у посебној свесци.</div></div>'
            f'<p class="clab" style="text-align:center">ФИЗИКА 6 · УВОД У ФИЗИКУ И КРЕТАЊЕ</p>'
            f'</div></section>')


LAYOUT = [
    ("fiz", [opener("fiz"), T[1], T[2], T[3], T[4]]),
    ("fiz", [T[5], T[6], T[7]]),
    ("fiz", [T[8], T[9], remember(ZAP["fiz"])]),
    ("met", [opener("met"), T[10], T[11], T[12]]),
    ("met", [T[13], T[14], HOME]),
    ("met", [T[15], T[16], T[17], remember(ZAP["met"])]),
    ("vel", [opener("vel"), T[18], T[19], T[20]]),
    ("vel", [T[21], T[22], T[23], T[24]]),
    ("vel", [T[25], T[26], remember(ZAP["vel"])]),
    ("kre", [opener("kre"), T[27], T[28], T[29], T[30]]),
    ("kre", [T[31], T[32], T[33], remember(ZAP["kre"])]),
    ("put", [opener("put"), T[34], T[35], T[36]]),
    ("put", [T[37], T[38]]),
    ("put", [T[39], T[40], T[41], T[42], remember(ZAP["put"])]),
    ("brz", [opener("brz"), T[43], T[44], T[45]]),
    ("brz", [T[46], T[47], T[48]]),
    ("brz", [T[49], T[50], remember(ZAP["brz"])]),
]


def workbook():
    pages = [cover(), intro(2)]
    n = 3
    for key, blocks in LAYOUT:
        pages.append(page(key, "".join(blocks), n))
        n += 1
    pages.append(final(n))
    return pages


# ------------------------------------------------------------------ решења

S = {
    1: "описујемо; предвиђамо",
    2: "природа",
    3: "физика, хемија, биологија",
    4: "лет (кретање): физика; рад срца (појаве у живом телу): биологија",
    5: "2 и 4. Објективан опис садржи податке које је могуће проверити.",
    6: "супстанца; физичко поље",
    7: "1: гвожђе; магнетно поље. 2: дрво и графит, више различитих супстанци; гравитационо поље. "
       "3: пластика, папир; електрично поље.",
    8: "1 Н: магнет делује путем физичког (магнетног) поља и без додира. 2 Т.",
    9: "Примери: кретање мехура од сапунице; балон протрљан о косу привлачи власи; магнет привлачи завртње; "
       "дуга у капљицама воде.",
    10: "непосредно посматрање",
    11: "вид и слух (и мирис озона). Светлост путује много брже од звука (око 300 000 km/s према око 340 m/s).",
    12: "б",
    13: "Галилеј А, Тесла Б",
    14: "Брзина падања не зависи од масе. Равном листу ваздух се више супротставља; згужван лист има мању површину "
        "на коју ваздух делује.",
    15: "1 непосредно посматрање, 2 експеримент, 3 физички закон или теорија, 4 практична примена",
    16: "понављања; контролисаним; лабораторијама",
    17: "ултразвук Б, ласер А, рендген В",
    18: "мерном јединицом",
    20: "б (ознака величине искошена, јединица усправна, размак између броја и јединице)",
    21: "*S* = 4 cm · 4 cm = 16 cm²; укупно 6 · 16 cm² = 96 cm²; *V* = 4 cm · 4 cm · 4 cm = 64 cm³",
    22: "а",
    23: "основне: дужина, време, маса; изведене: површина, запремина, брзина",
    24: "тренутак: 1 и 3; интервал: 2 и 4",
    25: fml("Δ*t* = 11 h 05 min − 10 h 50 min = 15 min"),
    26: "Отворено. Пример: дужина 29,7 cm, ширина 21 cm, маса 0,2 kg.",
    27: "положаја; друга",
    28: "упоредно; референтно",
    29: "б",
    30: "1 Т. 2 Н: табла се заједно са Земљом креће око Сунца. 3 Н: не постоје ни апсолутно мировање ни апсолутно кретање.",
    31: "у односу на лоптицу мирује; у односу на под се креће",
    32: "мол; дрво; станица",
    33: "Путник мирује у односу на воз, а креће се у односу на шине и станицу. Кретање изгледа различито у зависности "
        "од избора референтног тела.",
    34: "замишљена",
    35: "ласерски зрак, лифт, камен који слободно пада",
    36: "осовина: права линија; вентил: низ лукова који додирују тло. Различити делови истог тела могу имати различите путање.",
    37: "Свака најкраћа путања иде 6 поља десно и 4 поља горе: 10 · 50 m = 500 m.",
    38: "дужина; *s*; метар (m)",
    39: "mm, cm, dm, m, km",
    40: "km; mm; m; cm",
    41: "а и б",
    42: "Њене димензије су много мање од пута који прелази око Сунца.",
    43: "1 h 15 min",
    44: "ms, стотинка, s, min, h",
    45: "*s* = 8 m, *t* = 4 s, *v* = 8 m : 4 s = 2 m/s",
    46: "на 0 m, 2 m, 4 m, 6 m, 8 m и 10 m",
    47: "плави: 60 m : 10 s = 6 m/s; зелени: 60 m : 12 s = 5 m/s; бржи је плави",
    48: "*v* = 180 km : 2 h = 90 km/h; 90 : 3,6 = 25 m/s",
    49: "1 min = 60 s; *s* = 1,3 cm/s · 60 s = 78 cm",
    50: "Отворено. Тражити податке *s* и *t* са јединицама и рачун *v* = *s* : *t*. "
        "Пример: 500 m за 10 min = 50 m/min, око 0,8 m/s.",
}
SN = {
    9: "Прихватити сваки тачан пример.",
    26: "Прихватити сваки исправан запис са јединицом.",
    32: "Прихватити и друго смислено тело.",
    37: "Прихватити сваку путању од 10 поља.",
    43: "Рачун: од 6 h 50 min до 7 h је 10 min, од 7 h до 8 h 05 min је 1 h 05 min; укупно 1 h 15 min.",
}
SOL19 = grid_table(["ВЕЛИЧИНА", "ОЗНАКА", "МЕРНА ЈЕДИНИЦА", "ОЗНАКА ЈЕДИНИЦЕ"],
                   [["дужина", "*a* (или *l*)", "метар", "m"], ["маса", "*m*", "килограм", "kg"], ["време", "*t*", "секунда", "s"],
                    ["површина", "*S*", "метар квадратни", "m²"], ["запремина", "*V*", "метар кубни", "m³"]],
                   [30, 30, 44, 34]).replace('class="grid"', 'class="grid sm"')
KIND = {n: h.split('<div class="tk">')[1].split("<")[0] for n, h in T.items()}


def sol_item(n, body=None):
    body = body or f'<span class="sa">{S[n]}</span>'
    note = f'<div class="sn">{SN[n]}</div>' if n in SN else ""
    return (f'<div class="sol"><div class="tn">{n}</div><div><span class="sq">{KIND[n]}</span>'
            f'{body}{note}</div></div>')


def sol_section(key, nums, cont=False):
    _, tab, title, lesson, rng = CEL[CNUM[key] - 1]
    head = "" if cont else (f'<div class="opener" style="padding:2mm 4mm"><div class="onum" style="width:11mm;height:11mm">'
                            f'<b style="font-size:13pt">{CNUM[key]}</b></div><div><h1 style="font-size:13pt">{title}</h1>'
                            f'<p>{lesson} · задаци {rng}</p></div></div>')
    items = "".join(sol_item(n, f'<div class="sa">{SOL19}</div>' if n == 19 else None) for n in nums)
    return (f'<div class="{key}" style="display:flex;flex-direction:column;gap:2.4mm">{head}'
            f'<div class="solcard">{items}</div></div>')


SOL_INTRO = ('<div class="note"><h3>КАКО КОРИСТИТИ РЕШЕЊА</h3>'
             '<p>Решења су поређана по целинама, истим редом као задаци у свесци. Код рачунских задатака дат је цео рачун; '
             'прихватите и другачији ред корака ако су подаци, рачун и одговор тачни и записани са мерним јединицама.</p>'
             '<p>Пазите на запис: ознака величине искошено (*s*, *t*, *v*), јединица усправно (m, s, km/h), између броја '
             'и јединице размак, децимални зарез.</p></div>')

SOL_GUIDE = ('<div class="note zav"><h3>ИСТРАЖИВАЧКО ПИТАЊЕ И ОГЛЕД</h3>'
             '<p><b>Зашто прво видимо муњу, а тек онда чујемо гром?</b> Муња и гром настају у истом тренутку, али светлост '
             'путује око 300 000 km/s, а звук кроз ваздух око 340 m/s. Светлост до нас стигне готово одмах, а звуку '
             'треба око 3 s за сваки километар. Прихватите сваки одговор који пореди брзину светлости и звука.</p>'
             '<p><b>Оглед код куће.</b> Раван лист пада спорије од оловке јер му се ваздух више супротставља. '
             'Згужван лист и оловка падну на под готово истовремено. Брзина падања не зависи од масе.</p></div>')

SOL_NOTE = ('<div class="note"><h3>НАПОМЕНА ЗА ОДРАСЛЕ</h3>'
            '<p>Овај материјал није званични уџбеник. То је додатна радна свеска за вежбање градива физике за шести '
            'разред, лекције „Увод у физику“ и „Кретање“.</p>'
            '<p>Податак о брзини сонде Паркер у уџбенику (око 2 430 km/h) је вероватно штампарска грешка. Њена стварна '
            'највећа брзина је око 690 000 km/h.</p>'
            '<p>Податак 37,58 km/h за Јусејна Болта је просечна брзина на трци од 100 m (100 m за 9,58 s). '
            'Његова највећа тренутна брзина током трке била је око 44 km/h.</p></div>')


def solutions():
    P = [
        ("fiz", [SOL_INTRO, sol_section("fiz", range(1, 10))]),
        ("met", [sol_section("met", range(10, 18)), sol_section("vel", range(18, 21))]),
        ("vel", [sol_section("vel", range(21, 27), cont=True), sol_section("kre", range(27, 34))]),
        ("put", [sol_section("put", range(34, 43)), sol_section("brz", range(43, 47))]),
        ("brz", [sol_section("brz", range(47, 51), cont=True), SOL_GUIDE, SOL_NOTE]),
    ]
    out = []
    for i, (key, blocks) in enumerate(P):
        html = "".join(blocks)
        act = [k for k, *_ in CEL if f'<div class="{k}" style="display:flex' in html] or [key]
        out.append(page(key, html, i + 1, sol=True, active=act))
    return out


# ------------------------------------------------------------------ провера рачуна

def plain(html):
    t = re.sub(r'<span class="fr"><span>(.*?)</span><span>(.*?)</span></span>', r"\1/\2", typo(html))
    return re.sub(r"<[^>]+>", "", t).replace(NB, " ")


def hm(h, m):
    return 60 * h + m


def hm_str(mins):
    h, m = divmod(mins, 60)
    return f"{h} h {m:02d} min" if h and m < 10 else (f"{h} h {m} min" if h else f"{m} min")


def proveri_racune():
    """Сваки рачун из решења рачуна се поново; build стаје ако се разликује."""
    chk = []

    def need(n, text):
        chk.append((n, text, text in plain(S[n] if isinstance(n, int) else n)))

    a = 4
    need(21, f"= {a * a} cm²")
    need(21, f"6 · {a * a} cm² = {6 * a * a} cm²")
    need(21, f"= {a ** 3} cm³")
    d25 = hm(*C.ODMOR_T2) - hm(*C.ODMOR_T1)
    need(25, f"= {d25} min")
    need(25, f"{hm_str(hm(*C.ODMOR_T2))} − {hm_str(hm(*C.ODMOR_T1))}")
    polja = C.PLAN_DESNO + C.PLAN_GORE
    need(37, f"{C.PLAN_DESNO} поља десно и {C.PLAN_GORE} поља горе")
    need(37, f"{polja} · {C.PLAN_POLJE_M} m = {polja * C.PLAN_POLJE_M} m")
    need(43, hm_str(hm(8, 5) - hm(6, 50)))
    s45, t45 = C.KOLICA_V * max(C.KOLICA_T), max(C.KOLICA_T)
    need(45, f"*s* = {s45} m, *t* = {t45} s".replace("*", ""))
    need(45, f"{s45} m : {t45} s = {s45 // t45} m/s")
    need(46, ", ".join(f"{1 * t} m" for t in (0, 2, 4, 6, 8)) + " и 10 m")
    need(47, f"60 m : 10 s = {60 // 10} m/s")
    need(47, f"60 m : 12 s = {60 // 12} m/s")
    v48 = 180 / 2
    need(48, f"= {br(v48)} km/h")
    need(48, f"{br(v48)} : 3,6 = {br(v48 / 3.6)} m/s")
    need(49, f"= {br(round(1.3 * 60, 6))} cm")
    need(50, f"= {br(500 / 10)} m/min, око {br(500 / 10 / 60, 1)} m/s")
    need(SOL_GUIDE, f"око {round(1000 / 340)} s за сваки километар")
    need(SOL_NOTE, f"{br(round(100 / 9.58 * 3.6, 2))} km/h")
    need(SOL_NOTE, f"(100 m за 9,58 s)")
    bad = [(n, t) for n, t, ok in chk if not ok]
    for n, t in bad:
        print(f"РАЧУН НЕ ОДГОВАРА РЕШЕЊУ (задатак {n if isinstance(n, int) else 'напомена'}): очекује се „{t}“")
    if bad:
        raise SystemExit(1)
    return len(chk)


# ------------------------------------------------------------------ састављање

BW = ("<style>:root{--c-fiz:#222;--c-met:#222;--c-vel:#222;--c-kre:#222;--c-put:#222;--c-brz:#222;--c-zav:#222;"
      "--lisko:#8f8f8f}</style>")


def doc(pages, title, bw=False):
    return typo('<!doctype html><html lang="sr-Cyrl"><head><meta charset="utf-8">'
                f'<title>{title}</title><link rel="stylesheet" href="style.css">{BW if bw else ""}</head>'
                f'<body>{"".join(pages)}</body></html>')


def build(mode):
    os.makedirs(OUT, exist_ok=True)
    if mode == "r":
        title, tag = "IGRA LAB Физика 6 Увод у физику и кретање Решења и смернице", "RESENJA"
        html = doc(solutions(), title)
    else:
        bw = mode == "b"
        title = "IGRA LAB Физика 6 Увод у физику и кретање" + (" црно бело" if bw else "")
        html = doc(workbook(), title, bw)
        tag = "KOMPLET_CRNO-BELO" if bw else "KOMPLET_COLOR"
    hp = os.path.join(HERE, f"_{mode}.html")
    with open(hp, "w", encoding="utf-8") as fh:
        fh.write(html)
    pdf = os.path.join(OUT, NAME.format(tag) + ".pdf")
    rep = render(hp, pdf, title=title)
    os.remove(hp)
    print("  ->", os.path.relpath(pdf, HERE))
    return rep


if __name__ == "__main__":
    print(f"рачуни: {proveri_racune()} провера, сви одговарају решењима")
    modes = sys.argv[1:] or ["c", "b", "r"]
    for m in modes:
        build(m)
