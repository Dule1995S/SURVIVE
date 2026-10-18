# Линијски цртежи за свеску, сви као SVG у коду.
# Јединица у viewBox је милиметар, па је дебљина линије у mm.
# Боја долази из CSS класа (acc, t1, t2...), па исти цртеж ради и у боји и црно бело.

import math


def svg(w, h, body, extra="", s=1.0):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w * s:.1f}mm" height="{h * s:.1f}mm" {extra}>{body}</svg>')


def f(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")


def smooth(pts, closed=True):
    """Catmull Rom кроз тачке, претворено у кубне Безијеове криве."""
    n = len(pts)
    if closed:
        d = f"M{f(pts[0][0])},{f(pts[0][1])}"
        for i in range(n):
            p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
            d += f" C{f(c1[0])},{f(c1[1])} {f(c2[0])},{f(c2[1])} {f(p2[0])},{f(p2[1])}"
        return d + "Z"
    d = f"M{f(pts[0][0])},{f(pts[0][1])}"
    for i in range(n - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < n else pts[i + 1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{f(c1[0])},{f(c1[1])} {f(c2[0])},{f(c2[1])} {f(p2[0])},{f(p2[1])}"
    return d


def blob(cx, cy, rx, ry, waves=(), lobes=(), n=40, rot=0):
    """Затворен облик: елипса + таласи (k, ам, фаза) + испупчења (угао, ширина, дужина)."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        r = 1.0
        for k, a, ph in waves:
            r += a * math.sin(k * t + ph)
        for ang, wid, ln in lobes:
            dt = math.atan2(math.sin(t - ang), math.cos(t - ang))
            r += ln * math.exp(-(dt / wid) ** 2)
        x, y = rx * r * math.cos(t), ry * r * math.sin(t)
        xr = x * math.cos(rot) - y * math.sin(rot)
        yr = x * math.sin(rot) + y * math.cos(rot)
        pts.append((cx + xr, cy + yr))
    return smooth(pts)


def num(x, y, n, r=2.6):
    return (f'<circle class="ncirc" cx="{f(x)}" cy="{f(y)}" r="{r}"/>'
            f'<text class="ntext" x="{f(x)}" y="{f(y + 1.2)}" text-anchor="middle">{n}</text>')


def lead(x1, y1, x2, y2, n, r=2.6):
    """Линија показивача од тачке на делу (x1, y1) до броја у кругу (x2, y2)."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ex, ey = x2 - dx / L * r, y2 - dy / L * r
    return (f'<circle class="ldot" cx="{f(x1)}" cy="{f(y1)}" r=".55"/>'
            f'<path class="lead" d="M{f(x1)},{f(y1)} L{f(ex)},{f(ey)}"/>' + num(x2, y2, n, r))


def letter(x, y, ch, r=3.0):
    return (f'<circle class="accf" cx="{f(x)}" cy="{f(y)}" r="{r}"/>'
            f'<text class="ltext" x="{f(x)}" y="{f(y + 1.35)}" text-anchor="middle" '
            f'style="fill:#fff;font-size:3.9px">{ch}</text>')


def mito(cx, cy, rx=4.6, ry=2.2, rot=0, cls="wf"):
    """Митохондрија: овал са таласастом унутрашњом мембраном."""
    pts = []
    k = 6
    for i in range(k * 4 + 1):
        u = -0.78 + 1.56 * i / (k * 4)
        x = u * rx
        y = (ry * 0.62) * math.sin(i * math.pi / 2) * (1 - (u / 0.82) ** 2) ** 0.5
        pts.append((x, y))
    d = "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts)
    return (f'<g transform="translate({f(cx)},{f(cy)}) rotate({f(rot)})">'
            f'<ellipse class="{cls}" cx="0" cy="0" rx="{rx}" ry="{ry}"/>'
            f'<ellipse class="ink" cx="0" cy="0" rx="{rx}" ry="{ry}" style="stroke-width:.4"/>'
            f'<path class="ink" d="{d}" style="stroke-width:.3"/></g>')


def chloro(cx, cy, rx=4.4, ry=2.3, rot=0):
    """Хлоропласт: овал у боји са наслаганим кесицама."""
    g = (f'<g transform="translate({f(cx)},{f(cy)}) rotate({f(rot)})">'
         f'<ellipse class="t3" cx="0" cy="0" rx="{rx}" ry="{ry}"/>'
         f'<ellipse class="ink" cx="0" cy="0" rx="{rx}" ry="{ry}" style="stroke-width:.4"/>')
    for xx in (-rx * .45, 0, rx * .45):
        for yy in (-.55, 0, .55):
            g += f'<rect class="accf" x="{f(xx - .8)}" y="{f(yy - .18)}" width="1.6" height=".36" rx=".18"/>'
    return g + "</g>"


def dots(pts, r=.32, cls="inkf", op=.45):
    return "".join(f'<circle class="{cls}" cx="{f(x)}" cy="{f(y)}" r="{r}" style="opacity:{op}"/>' for x, y in pts)


def arrow(x1, y1, x2, y2, cls="acc", w=.6, head=1.6):
    a = math.atan2(y2 - y1, x2 - x1)
    hx1, hy1 = x2 - head * math.cos(a - .45), y2 - head * math.sin(a - .45)
    hx2, hy2 = x2 - head * math.cos(a + .45), y2 - head * math.sin(a + .45)
    return (f'<path class="{cls}" d="M{f(x1)},{f(y1)} L{f(x2)},{f(y2)}" style="stroke-width:{w}"/>'
            f'<path class="{cls}" d="M{f(hx1)},{f(hy1)} L{f(x2)},{f(y2)} L{f(hx2)},{f(hy2)}" style="stroke-width:{w}"/>')


def tube(d, w=3.2, tint="t2"):
    """Цев са обрисом: широка линија мастила, па ужа у тону."""
    cmap = {"t1": "var(--tint)", "t2": "var(--tint2)", "t3": "var(--tint3)"}
    return (f'<path d="{d}" style="fill:none;stroke:var(--ink);stroke-width:{w};stroke-linecap:round;stroke-linejoin:round"/>'
            f'<path d="{d}" style="fill:none;stroke:{cmap[tint]};stroke-width:{w - .8};stroke-linecap:round;stroke-linejoin:round"/>')


# ---------------------------------------------------------------- Лиско

def lisko(cx=0, cy=0, s=1.0):
    """Лиско, глава лисице, нацртана у оквиру 20 x 20 око центра."""
    g = f'<g transform="translate({f(cx)},{f(cy)}) scale({s})">'
    g += '<path class="lisko" d="M-7.6,-8.6 L-3.2,-4.6 L3.2,-4.6 L7.6,-8.6 L8.2,-1.6 Q8.4,3.4 0,8.6 Q-8.4,3.4 -8.2,-1.6 Z"/>'
    g += '<path class="ink" style="stroke-width:.55" d="M-7.6,-8.6 L-3.2,-4.6 L3.2,-4.6 L7.6,-8.6 L8.2,-1.6 Q8.4,3.4 0,8.6 Q-8.4,3.4 -8.2,-1.6 Z"/>'
    g += '<path class="ink" style="stroke-width:.45" d="M-6.6,-6.8 L-4.6,-4.9 M6.6,-6.8 L4.6,-4.9"/>'
    g += '<path class="wf" d="M-8.1,-0.6 Q-4.2,0.4 -2.2,3.4 Q-1.2,5.6 0,8.6 Q-6.6,4.6 -8.1,-0.6 Z"/>'
    g += '<path class="wf" d="M8.1,-0.6 Q4.2,0.4 2.2,3.4 Q1.2,5.6 0,8.6 Q6.6,4.6 8.1,-0.6 Z"/>'
    g += '<path class="ink" style="stroke-width:.4" d="M-8.1,-0.6 Q-4.2,0.4 -2.2,3.4 Q-1.2,5.6 0,8.6 M8.1,-0.6 Q4.2,0.4 2.2,3.4 Q1.2,5.6 0,8.6"/>'
    g += '<ellipse class="inkf" cx="-3.4" cy="-1.2" rx=".95" ry="1.2"/><ellipse class="inkf" cx="3.4" cy="-1.2" rx=".95" ry="1.2"/>'
    g += '<circle class="wf" cx="-3.1" cy="-1.6" r=".32"/><circle class="wf" cx="3.7" cy="-1.6" r=".32"/>'
    g += '<path class="inkf" d="M-1.3,6.6 Q0,5.8 1.3,6.6 Q0,8.4 -1.3,6.6 Z"/>'
    return g + "</g>"


def stamp(size_mm=13, ring_text=None, big=False):
    r = 10
    body = f'<circle class="wf" cx="0" cy="0" r="{r}"/>'
    body += f'<circle cx="0" cy="0" r="{r - .4}" style="fill:none;stroke:var(--c-zav);stroke-width:.8"/>'
    body += f'<circle cx="0" cy="0" r="{r - 1.6}" style="fill:none;stroke:var(--c-zav);stroke-width:.3"/>'
    body += lisko(0, .4, .74)
    return (f'<svg class="stamp" xmlns="http://www.w3.org/2000/svg" viewBox="-10.5 -10.5 21 21" '
            f'width="{size_mm}mm" height="{size_mm}mm">{body}</svg>')


def mission_stamp(size_mm=72, top="МИСИЈА 01 · ЗАВРШЕНА", bottom="IGRA LAB · ИСТРАЖИВАЧ"):
    R = 30
    rt, rb = R - 7.4, R - 3.4      # полупречник основне линије текста горе и доле
    st = "fill:var(--acc);font-family:Lora,serif;font-weight:700;font-size:4.3px;letter-spacing:.35px"
    b = '<g transform="rotate(-8)">'
    b += f'<circle cx="0" cy="0" r="{R}" style="fill:#fff;stroke:var(--acc);stroke-width:1.4"/>'
    b += f'<circle cx="0" cy="0" r="{R - 2}" style="fill:none;stroke:var(--acc);stroke-width:.4"/>'
    b += f'<circle cx="0" cy="0" r="{R - 10.5}" style="fill:var(--tint);stroke:var(--acc);stroke-width:.6"/>'
    b += f'<path id="arcT" d="M{-rt},0 A{rt},{rt} 0 0 1 {rt},0" style="fill:none"/>'
    b += f'<path id="arcB" d="M{-rb},0 A{rb},{rb} 0 0 0 {rb},0" style="fill:none"/>'
    b += f'<text style="{st}" text-anchor="middle"><textPath href="#arcT" startOffset="50%">{top}</textPath></text>'
    b += f'<text style="{st};font-size:3.7px" text-anchor="middle"><textPath href="#arcB" startOffset="50%">{bottom}</textPath></text>'
    for sx in (-1, 1):
        b += f'<circle class="accf" cx="{sx * (R - 5.6)}" cy="0" r=".9"/>'
    b += lisko(0, -1, 1.25)
    b += '</g>'
    return svg(64, 64, f'<g transform="translate(32,32)">{b}</g>', f'style="width:{size_mm}mm;height:{size_mm}mm"')


# ---------------------------------------------------------------- 1. степенице (задатак 3)

def stairs():
    W, H = 172, 70
    bw, bh, rise, step = 30.0, 14.0, 9.4, 34.8
    b = ""
    base = H - 6
    for i in range(5):
        x = 2 + i * step
        top = base - bh - i * rise - 2.6
        # степеник
        sw = min(step - .6, W - (x - 1))
        b += f'<rect class="t1" x="{f(x - 1)}" y="{f(top + bh + .8)}" width="{f(sw)}" height="{f(base - top - bh - .8 + 2)}"/>'
        b += f'<path class="acc" style="stroke-width:.5" d="M{f(x - 1)},{f(top + bh + .8)} h{f(sw)}"/>'
        # поље за упис
        b += f'<rect x="{f(x)}" y="{f(top)}" width="{bw}" height="{bh}" rx="1.6" style="fill:#fff;stroke:var(--ink);stroke-width:.4"/>'
        if i < 4:
            x1, y1 = x + bw * .62, top - .6
            x2, y2 = x + step + bw * .36, top - rise - .9
            b += (f'<path class="acc" style="stroke-width:.55" d="M{f(x1)},{f(y1)} Q{f((x1 + x2) / 2)},{f(y2 - 5)} {f(x2)},{f(y2)}"/>')
            a = math.atan2(y2 - (y2 - 5), x2 - (x1 + x2) / 2)
            b += (f'<path class="acc" style="stroke-width:.55" d="M{f(x2 - 1.5 * math.cos(a - .5))},{f(y2 - 1.5 * math.sin(a - .5))} '
                  f'L{f(x2)},{f(y2)} L{f(x2 - 1.5 * math.cos(a + .5))},{f(y2 - 1.5 * math.sin(a + .5))}"/>')
    b += f'<path class="ink" style="stroke-width:.4" d="M0,{base + 2} H{W}"/>'
    b += f'<text class="mtext" x="2" y="{base + 5.6}">најједноставнији ниво</text>'
    t5 = base - bh - 4 * rise - 2.6
    b += f'<text class="mtext" x="{f(2 + 4 * step + bw / 2)}" y="{f(t5 + bh + 6)}" text-anchor="middle">најсложенији ниво</text>'
    return svg(W, H + 1, b)


# ---------------------------------------------------------------- 2. животињска ћелија (задатак 14)

def animal_cell(numbers=True, cx=52, cy=34, s=1.0):
    b = f'<g transform="translate({cx},{cy}) scale({s})">'
    d = blob(0, 0, 30, 24, waves=((3, .035, .4), (5, .025, 1.3), (2, .03, 2.1)))
    b += f'<path class="t1" d="{d}"/>'
    b += f'<path class="acc" style="stroke-width:1.0" d="{d}"/>'
    b += dots([(-20, -6), (-14, 10), (-6, -16), (10, 15), (18, 8), (-22, 4), (4, 18), (-10, 16), (15, -13), (22, -4),
               (-17, -12), (-2, 13), (8, -18), (-25, -2), (24, 3), (0, -12), (-13, 3)])
    # везикуле
    for (x, y, r) in ((-18, 12, 1.4), (21, -2, 1.2), (-6, 18, 1.0), (13, 18, 1.1)):
        b += f'<circle class="wf" cx="{x}" cy="{y}" r="{r}"/><circle class="ink" cx="{x}" cy="{y}" r="{r}" style="stroke-width:.3"/>'
    # једро
    b += '<circle class="t2" cx="4" cy="-1" r="9.6"/><circle class="ink" cx="4" cy="-1" r="9.6" style="stroke-width:.55"/>'
    b += '<circle class="ink" cx="4" cy="-1" r="8.7" style="stroke-width:.25;stroke-dasharray:.8 .7"/>'
    b += '<circle class="t3" cx="6.4" cy="0.6" r="2.8"/>'
    b += dots([(0, -4), (2, -6), (8, -5), (-1, 2), (1, 4), (9, 3), (5, -8), (-2, -1)], r=.28, op=.55)
    # митохондрије
    b += mito(-16, -3, rot=70)
    b += mito(-6, 11, rot=-15)
    b += mito(16, 10, rot=35)
    b += mito(-7, -14, rot=-25, rx=3.8, ry=1.9)
    b += '</g>'
    if numbers:
        # тачке на деловима у координатама целог цртежа
        b += lead(cx - 29.6 * s, cy + 6 * s, 6, cy + 18, 1)      # мембрана
        b += lead(cx - 19 * s, cy + 6 * s, 6, cy + 30, 2)       # цитоплазма
        b += lead(cx + 12 * s, cy - 6 * s, 98, cy - 20, 3)      # једро
        b += lead(cx + 16 * s, cy + 10 * s, 98, cy + 22, 4)     # митохондрија
        return svg(104, 70, b)
    return b


# ---------------------------------------------------------------- 3. биљна и животињска ћелија (задатак 21)

def plant_cell(cx, cy):
    w, h = 62, 44
    x0, y0 = cx - w / 2, cy - h / 2
    b = f'<rect class="t2" x="{x0}" y="{y0}" width="{w}" height="{h}" rx="3"/>'
    b += f'<rect class="ink" x="{x0}" y="{y0}" width="{w}" height="{h}" rx="3" style="stroke-width:.6"/>'
    b += f'<rect class="t1" x="{x0 + 1.8}" y="{y0 + 1.8}" width="{w - 3.6}" height="{h - 3.6}" rx="2"/>'
    b += f'<rect class="acc" x="{x0 + 1.8}" y="{y0 + 1.8}" width="{w - 3.6}" height="{h - 3.6}" rx="2" style="stroke-width:.6"/>'
    vd = blob(cx + 2, cy + 1.5, 19, 12.5, waves=((3, .04, .5), (2, .03, 1.7)))
    b += f'<path class="wf" d="{vd}"/><path class="ink" d="{vd}" style="stroke-width:.45"/>'
    b += dots([(x0 + 5, y0 + 6), (x0 + 9, y0 + h - 5), (x0 + w - 6, y0 + 5), (x0 + w - 5, y0 + h - 6), (x0 + 22, y0 + 4.5),
               (x0 + 36, y0 + h - 4.2), (x0 + 4.4, cy + 6)])
    b += f'<circle class="t2" cx="{x0 + 8.6}" cy="{y0 + 9.4}" r="5.2"/><circle class="ink" cx="{x0 + 8.6}" cy="{y0 + 9.4}" r="5.2" style="stroke-width:.5"/>'
    b += f'<circle class="t3" cx="{x0 + 9.6}" cy="{y0 + 10.2}" r="1.6"/>'
    for (dx, dy, r) in ((22, 4.6, 8), (34, 4.4, -6), (48, 4.8, 12), (w - 4.6, 18, 80), (w - 4.8, 31, 95),
                        (6, 27, 85), (6, h - 6, 30), (20, h - 4.4, -5), (46, h - 4.3, 6)):
        b += chloro(x0 + dx, y0 + dy, rot=r, rx=3.6, ry=1.8)
    b += mito(x0 + 30, y0 + h - 4.6, rx=3.0, ry=1.4, rot=0)
    b += mito(x0 + 13, y0 + h - 12, rx=3.0, ry=1.4, rot=60)
    return b


def plant_animal():
    W, H = 150, 52
    b = plant_cell(36, 26)
    b += animal_cell(numbers=False, cx=114, cy=26, s=.8)
    return svg(W, H, b, s=.84)


# ---------------------------------------------------------------- 4. амеба (задатак 32)

def amoeba_shape(cx, cy, s=1.0, lobes=None, rot=0):
    if lobes is None:
        lobes = ((-2.6, .36, .52), (-1.2, .3, .34), (.4, .34, .46), (1.75, .3, .26), (2.75, .32, .38))
    return blob(cx, cy, 20 * s, 15 * s, waves=((3, .05, .2), (7, .015, 1)), lobes=lobes, n=72, rot=rot)


def amoeba(numbers=True, s=1.0):
    cx, cy = 54, 38
    d = amoeba_shape(cx, cy)
    b = f'<path class="t1" d="{d}"/><path class="acc" d="{d}" style="stroke-width:.9"/>'
    # унутрашња граница ектоплазме, танко
    d2 = blob(cx, cy, 15.5, 11.2, waves=((3, .05, .2),), lobes=((-2.6, .34, .42), (-1.2, .28, .26), (.4, .32, .38), (1.75, .28, .18), (2.75, .3, .3)), n=72)
    b += f'<path class="ink" d="{d2}" style="stroke-width:.22;stroke-dasharray:.6 .9;opacity:.7"/>'
    b += dots([(cx - 10, cy + 3), (cx - 6, cy - 7), (cx + 2, cy + 8), (cx + 9, cy - 6), (cx - 13, cy - 3), (cx + 12, cy + 4),
               (cx - 3, cy + 1), (cx + 5, cy - 1), (cx - 8, cy + 9), (cx + 15, cy - 1), (cx - 1, cy - 9)])
    # једро
    b += f'<ellipse class="t2" cx="{cx + 2}" cy="{cy + 1}" rx="5.4" ry="4.4"/><ellipse class="ink" cx="{cx + 2}" cy="{cy + 1}" rx="5.4" ry="4.4" style="stroke-width:.5"/>'
    b += dots([(cx + 1, cy), (cx + 3, cy + 2), (cx + 4, cy - 1), (cx, cy + 2.5), (cx + 2, cy - 2)], r=.3, op=.6)
    # хранљива вакуола са честицом хране
    b += f'<circle class="wf" cx="{cx - 9}" cy="{cy - 3}" r="3.6"/><circle class="ink" cx="{cx - 9}" cy="{cy - 3}" r="3.6" style="stroke-width:.45"/>'
    b += f'<path class="t3" d="M{cx - 10.6},{cy - 3.6} q1.2,-1.4 2.6,-.2 q1.2,1.4 -.4,2.2 q-1.8,.6 -2.2,-2 z"/>'
    b += f'<circle class="wf" cx="{cx + 6}" cy="{cy + 9}" r="2.2"/><circle class="ink" cx="{cx + 6}" cy="{cy + 9}" r="2.2" style="stroke-width:.35"/>'
    # контрактилна вакуола са зрацима
    kx, ky = cx + 12, cy - 4
    for a in range(0, 360, 40):
        ra = math.radians(a)
        b += f'<path class="ink" style="stroke-width:.3" d="M{f(kx + 3.2 * math.cos(ra))},{f(ky + 3.2 * math.sin(ra))} L{f(kx + 4.6 * math.cos(ra))},{f(ky + 4.6 * math.sin(ra))}"/>'
    b += f'<circle class="wf" cx="{kx}" cy="{ky}" r="2.7"/><circle class="ink" cx="{kx}" cy="{ky}" r="2.7" style="stroke-width:.5"/>'
    if numbers:
        # врх једне лажне ножице: испупчење на углу 0.4 rad
        tip = (cx + 20 * 1.44 * math.cos(.4) * .97, cy + 15 * 1.44 * math.sin(.4) * .97)
        b += lead(tip[0], tip[1], 104, 56, 1)
        b += lead(cx + 4.6, cy + 3.4, 104, 40, 2)
        b += lead(cx - 11.6, cy - 5, 4, 20, 3)
        b += lead(kx + 1, ky - 2.4, 90, 8, 4)
        return svg(108, 66, b, s=s)
    return b


# ---------------------------------------------------------------- 5. проста деоба амебе (задатак 34)

def _phase(k, cx, cy):
    """k = 0 једно једро, 1 једро се дели, 2 сужавање, 3 две нове амебе."""
    b = ""
    if k in (0, 1):
        d = blob(cx, cy, 13, 10, waves=((3, .06, .3 + k), (5, .03, 1)), lobes=((-2.4, .3, .25), (.6, .3, .2), (2.2, .3, .18)), n=56)
        b += f'<path class="t1" d="{d}"/><path class="acc" d="{d}" style="stroke-width:.8"/>'
        b += dots([(cx - 7, cy + 3), (cx + 6, cy - 5), (cx - 4, cy - 6), (cx + 7, cy + 5), (cx - 8, cy - 2)])
        if k == 0:
            b += f'<ellipse class="t2" cx="{cx}" cy="{cy}" rx="3.8" ry="3.2"/><ellipse class="ink" cx="{cx}" cy="{cy}" rx="3.8" ry="3.2" style="stroke-width:.5"/>'
        else:
            nd = (f'M{cx - 6},{cy} C{cx - 6},{cy - 3.6} {cx - 1.6},{cy - 3.4} {cx},{cy - 1.1} '
                  f'C{cx + 1.6},{cy - 3.4} {cx + 6},{cy - 3.6} {cx + 6},{cy} '
                  f'C{cx + 6},{cy + 3.6} {cx + 1.6},{cy + 3.4} {cx},{cy + 1.1} '
                  f'C{cx - 1.6},{cy + 3.4} {cx - 6},{cy + 3.6} {cx - 6},{cy} Z')
            b += f'<path class="t2" d="{nd}"/><path class="ink" d="{nd}" style="stroke-width:.5"/>'
    elif k == 2:
        d = (f'M{cx - 15},{cy} C{cx - 15},{cy - 9} {cx - 8},{cy - 11} {cx - 4},{cy - 8} '
             f'C{cx - 1.5},{cy - 5.6} {cx + 1.5},{cy - 5.6} {cx + 4},{cy - 8} '
             f'C{cx + 8},{cy - 11} {cx + 15},{cy - 9} {cx + 15},{cy} '
             f'C{cx + 15},{cy + 9} {cx + 8},{cy + 11} {cx + 4},{cy + 8} '
             f'C{cx + 1.5},{cy + 5.6} {cx - 1.5},{cy + 5.6} {cx - 4},{cy + 8} '
             f'C{cx - 8},{cy + 11} {cx - 15},{cy + 9} {cx - 15},{cy} Z')
        b += f'<path class="t1" d="{d}"/><path class="acc" d="{d}" style="stroke-width:.8"/>'
        b += dots([(cx - 10, cy + 4), (cx + 10, cy - 4), (cx - 9, cy - 5), (cx + 9, cy + 5)])
        for sx in (-8, 8):
            b += f'<ellipse class="t2" cx="{cx + sx}" cy="{cy}" rx="3" ry="2.6"/><ellipse class="ink" cx="{cx + sx}" cy="{cy}" rx="3" ry="2.6" style="stroke-width:.5"/>'
    else:
        for sx, ph in ((-8.6, .2), (8.6, 1.4)):
            d = blob(cx + sx, cy, 7.4, 6.6, waves=((3, .07, ph), (5, .03, ph + 1)), lobes=((ph * 2, .4, .2),), n=44)
            b += f'<path class="t1" d="{d}"/><path class="acc" d="{d}" style="stroke-width:.8"/>'
            b += f'<ellipse class="t2" cx="{cx + sx}" cy="{cy}" rx="2.8" ry="2.4"/><ellipse class="ink" cx="{cx + sx}" cy="{cy}" rx="2.8" ry="2.4" style="stroke-width:.5"/>'
            b += dots([(cx + sx - 4, cy + 2.6), (cx + sx + 3.6, cy - 3)])
    return b


# распоред на цртежу: А = једро се дели, Б = две нове амебе, В = једно једро, Г = сужавање
DEOBA_RASPORED = (("А", 1), ("Б", 3), ("В", 0), ("Г", 2))


def division():
    W, H = 172, 46
    b = ""
    for i, (ch, k) in enumerate(DEOBA_RASPORED):
        cx = 21.5 + i * 43
        b += f'<rect x="{cx - 20}" y="1" width="40" height="31" rx="2.4" style="fill:none;stroke:var(--rule);stroke-width:.3"/>'
        b += _phase(k, cx, 18)
        b += letter(cx - 16, 5, ch, r=2.6)
        b += box(cx - 4.25, 35.6)
    return svg(W, H, b)


def box(x, y, label=None, s=8.5):
    """Празно поле за упис слова или броја; x је десна половина ознаке."""
    g = ""
    if label:
        g += f'<text class="mtext" x="{f(x - 1.6)}" y="{f(y + s / 2 + 1)}" text-anchor="end">{label}</text>'
    g += f'<rect x="{f(x)}" y="{f(y)}" width="{s}" height="{s}" rx="1.2" style="fill:#fff;stroke:var(--ink);stroke-width:.35"/>'
    return g


# ---------------------------------------------------------------- 6. облици бактерија (задатак 40)

def bacteria_shapes():
    """Четири панела: лоптаст, штапићаст, у облику зареза, спирално увијен."""
    W, H = 172, 48
    b = ""
    cxs = [21.5 + i * 43 for i in range(4)]
    for cx, cap in zip(cxs, ("лоптаст", "штапићаст", "у облику зареза", "спирално увијен")):
        b += f'<rect x="{cx - 20}" y="1" width="40" height="34" rx="2.4" style="fill:none;stroke:var(--rule);stroke-width:.3"/>'
        b += f'<text class="stext" x="{cx}" y="30.4" text-anchor="middle">{cap}</text>'
        b += box(cx - 4.25, 38.4)
    # лоптасте
    cx = cxs[0]
    for (x, y) in ((-5, 2), (1.2, 2.4), (-2, -3.2), (6.4, -2)):
        b += f'<circle class="t2" cx="{f(cx + x)}" cy="{f(13 + y)}" r="3.2"/><circle class="ink" cx="{f(cx + x)}" cy="{f(13 + y)}" r="3.2" style="stroke-width:.5"/>'
    # штапићасте
    cx = cxs[1]
    b += tube(f"M{cx - 11},{9} L{cx + 3},{9}", 4.4)
    b += tube(f"M{cx - 4},{17} L{cx + 11},{17}", 4.4)
    # зарез са бичем
    cx = cxs[2]
    b += tube(f"M{cx - 8},{9} Q{cx - 1},{21} {cx + 6},{11}", 4.2)
    b += f'<path class="ink" style="stroke-width:.35" d="M{cx + 7.6},{9.4} q2,-2.6 4,-1 q2,1.6 4,-1.4"/>'
    # спирала
    cx = cxs[3]
    pts = [(cx - 13 + i * 1.3, 13 + 4.2 * math.sin(i * 1.3 / 6.5 * 2 * math.pi)) for i in range(21)]
    b += tube(smooth(pts, closed=False), 3.2)
    return svg(W, H, b)


# ---------------------------------------------------------------- 7. волвокс (уз задатак 44)

def _colony(cx, cy, R, n, flag=True, fill="t1"):
    b = f'<circle class="{fill}" cx="{cx}" cy="{cy}" r="{R}"/>'
    b += f'<circle class="ink" cx="{cx}" cy="{cy}" r="{R}" style="stroke-width:.35"/>'
    pts = [(cx + (R - 1.2) * math.cos(2 * math.pi * i / n), cy + (R - 1.2) * math.sin(2 * math.pi * i / n)) for i in range(n)]
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        b += f'<path class="ink" style="stroke-width:.2" d="M{f(x1)},{f(y1)} L{f(x2)},{f(y2)}"/>'
    for i, (x, y) in enumerate(pts):
        a = 2 * math.pi * i / n
        if flag:
            for da in (-.12, .12):
                ex, ey = cx + (R + 1.6) * math.cos(a + da * .3), cy + (R + 1.6) * math.sin(a + da * .3)
                b += f'<path class="ink" style="stroke-width:.2" d="M{f(x)},{f(y)} L{f(ex)},{f(ey)}"/>'
        b += f'<circle class="accf" cx="{f(x)}" cy="{f(y)}" r="{.75 if flag else .55}"/>'
    return b


def volvox(raw=False, s=1.0):
    b = _colony(30, 30, 26, 40)
    b += _colony(21, 23, 7.2, 14, flag=False, fill="t2")
    b += _colony(37, 22, 6.2, 12, flag=False, fill="t2")
    b += _colony(30, 39, 7.6, 15, flag=False, fill="t2")
    return b if raw else svg(60, 60, b, s=s)


# ---------------------------------------------------------------- 8. сунђер у пресеку (задатак 46)

def sponge(numbers=True):
    W, H = 120, 92
    cx = 52
    top, bot = 8, 80

    def xo(t):  # спољна ивица (растојање од средине) за t од 0 (врх) до 1 (дно)
        return 22 + 7 * math.sin(math.pi * t) - 6 * t

    def xi(t):
        return xo(t) - 8.5

    ts = [i / 30 for i in range(31)]
    b = ""
    b += '<defs><pattern id="jelly" width="2.2" height="2.2" patternUnits="userSpaceOnUse">'
    b += '<circle cx=".6" cy=".6" r=".28" style="fill:var(--ink);opacity:.4"/><circle cx="1.7" cy="1.7" r=".22" style="fill:var(--ink);opacity:.3"/></pattern></defs>'
    for side in (-1, 1):
        outer = [(cx + side * xo(t), top + t * (bot - top)) for t in ts]
        inner = [(cx + side * xi(t), top + t * (bot - top)) for t in ts]
        poly = "M" + " L".join(f"{f(x)},{f(y)}" for x, y in outer + inner[::-1]) + "Z"
        b += f'<path class="t1" d="{poly}"/><path d="{poly}" style="fill:url(#jelly)"/>'
        # спољни слој: низ спљоштених ћелија
        b += '<path class="acc" style="stroke-width:1.5;opacity:.55" d="' + "M" + " L".join(f"{f(x - side * .75)},{f(y)}" for x, y in outer) + '"/>'
        b += '<path class="ink" style="stroke-width:.4" d="' + "M" + " L".join(f"{f(x)},{f(y)}" for x, y in outer) + '"/>'
        for t in ts[1:-1:2]:
            x, y = cx + side * xo(t), top + t * (bot - top)
            b += f'<path class="ink" style="stroke-width:.25" d="M{f(x)},{f(y)} L{f(x - side * 1.5)},{f(y)}"/>'
        # унутрашњи слој са бичевима
        b += '<path class="ink" style="stroke-width:.4" d="' + "M" + " L".join(f"{f(x)},{f(y)}" for x, y in inner) + '"/>'
        for t in ts[1:-1]:
            x, y = cx + side * xi(t), top + t * (bot - top)
            b += f'<circle class="t3" cx="{f(x + side * .9)}" cy="{f(y)}" r=".95"/>'
            b += f'<path class="ink" style="stroke-width:.22" d="M{f(x)},{f(y)} q{f(-side * 1.2)},-.9 {f(-side * 2.2)},0 q{f(-side * .9)},.9 {f(-side * 1.9)},0"/>'
    # поре: канали кроз зид
    for t in (.2, .42, .64):
        for side in (-1, 1):
            y = top + t * (bot - top)
            xa, xb = cx + side * (xo(t) + .4), cx + side * (xi(t) - .4)
            x0, x1 = min(xa, xb), max(xa, xb)
            b += f'<rect class="wf" x="{f(x0)}" y="{f(y - 1.6)}" width="{f(x1 - x0)}" height="3.2"/>'
            b += f'<path class="ink" style="stroke-width:.3" d="M{f(x0)},{f(y - 1.6)} H{f(x1)} M{f(x0)},{f(y + 1.6)} H{f(x1)}"/>'
            b += arrow(cx + side * (xo(t) + 5), y, cx + side * (xi(t) - 1.6), y, w=.45, head=1.2)
    # проток кроз отвор на врху
    b += arrow(cx, top + 10, cx, top - 5, w=.55, head=1.5)
    b += arrow(cx - 6, top + 14, cx - 9, top - 3, w=.45, head=1.3)
    b += arrow(cx + 6, top + 14, cx + 9, top - 3, w=.45, head=1.3)
    # подлога
    b += f'<path class="ink" style="stroke-width:.5" d="M{cx - 34},{bot} H{cx + 34}"/>'
    for i in range(14):
        x = cx - 32 + i * 4.8
        b += f'<path class="ink" style="stroke-width:.3" d="M{f(x)},{bot + .2} l-2.6,3.4"/>'
    b += f'<path class="ink" style="stroke-width:.4" d="M{f(cx - xi(1))},{bot} H{f(cx + xi(1))}"/>'
    if numbers:
        t = .42
        y = top + t * (bot - top)
        b += lead(cx - xo(t) - .4, y, 6, y - 20, 1)                                  # поре
        t2 = .78
        y2 = top + t2 * (bot - top)
        b += lead(cx - xo(t2) + .3, y2, 6, y2 + 6, 2)                               # спољашњи слој
        t3 = .32
        y3 = top + t3 * (bot - top)
        b += lead(cx + xi(t3) - 1.5, y3, 112, y3 - 14, 3)                           # унутрашњи слој
        t4 = .55
        y4 = top + t4 * (bot - top)
        b += lead(cx + (xo(t4) + xi(t4)) / 2, y4 + 4, 112, y4 + 14, 4)                # пихтијасти слој
    return svg(W, H, b)


# ---------------------------------------------------------------- 9. печурка са мицелијумом (задатак 47)

def mushroom():
    W, H = 172, 74
    gx, gy = 58, 34          # подножје дршке на тлу
    b = ""
    # тло
    b += f'<rect class="t1" x="4" y="{gy}" width="{W - 60}" height="{H - gy - 2}" rx="2"/>'
    b += f'<path class="ink" style="stroke-width:.5" d="M4,{gy} H{W - 56}"/>'
    for (x, y) in ((12, 44), (30, 62), (88, 48), (100, 66), (20, 54), (76, 64), (44, 70), (96, 40)):
        b += f'<ellipse class="t2" cx="{x}" cy="{y}" rx="1.6" ry="1"/>'
    # клобук и дршка
    b += f'<path class="t2" d="M{gx - 4},{gy} C{gx - 4.6},{gy - 10} {gx - 3.6},{gy - 15} {gx - 3},{gy - 17} L{gx + 3},{gy - 17} C{gx + 3.6},{gy - 15} {gx + 4.6},{gy - 10} {gx + 4},{gy} Z"/>'
    b += f'<path class="ink" d="M{gx - 4},{gy} C{gx - 4.6},{gy - 10} {gx - 3.6},{gy - 15} {gx - 3},{gy - 17} M{gx + 3},{gy - 17} C{gx + 3.6},{gy - 15} {gx + 4.6},{gy - 10} {gx + 4},{gy}" style="stroke-width:.5"/>'
    b += f'<path class="ink" style="stroke-width:.4" d="M{gx - 3.8},{gy - 12} q3.8,2 7.6,0"/>'
    cap = f'M{gx - 20},{gy - 17} C{gx - 19},{gy - 32} {gx + 19},{gy - 32} {gx + 20},{gy - 17} Q{gx},{gy - 20} {gx - 20},{gy - 17} Z'
    b += f'<path class="t3" d="{cap}"/><path class="ink" d="{cap}" style="stroke-width:.55"/>'
    for i in range(1, 12):
        x = gx - 19 + i * 3.2
        b += f'<path class="ink" style="stroke-width:.25" d="M{f(x)},{f(gy - 17.4 - .9 * math.sin(i / 12 * math.pi))} L{f(gx + (x - gx) * .25)},{gy - 16.4}"/>'
    for (x, y, r) in ((-10, -26, 1.6), (6, -27, 1.3), (13, -22, 1.1), (-2, -23, 1)):
        b += f'<circle class="wf" cx="{gx + x}" cy="{gy + y}" r="{r}"/>'
    # мицелијум: разгранате нити у тлу
    import random
    rnd = random.Random(7)
    paths = []

    def grow(x, y, ang, ln, depth):
        if depth == 0 or ln < 2:
            return
        pts = [(x, y)]
        for _ in range(4):
            ang += rnd.uniform(-.35, .35)
            x += ln / 4 * math.cos(ang)
            y += ln / 4 * math.sin(ang)
            y = min(max(y, gy + 1.5), H - 4)
            x = min(max(x, 6), W - 60)
            pts.append((x, y))
        paths.append(pts)
        grow(x, y, ang - rnd.uniform(.4, .8), ln * .72, depth - 1)
        grow(x, y, ang + rnd.uniform(.3, .7), ln * .7, depth - 1)

    for a in (math.pi * .9, math.pi * .7, math.pi * .5, math.pi * .3, math.pi * .12):
        grow(gx + rnd.uniform(-2.6, 2.6), gy + .6, a, 16, 4)
    for p in paths:
        b += f'<path class="ink" style="stroke-width:.3" d="{smooth(p, closed=False)}"/>'
    # увећање хифе
    mx, my, mr = 136, 46, 21
    zx, zy = 92, 52
    b += f'<path class="lead" style="stroke-dasharray:.8 .8" d="M{zx},{zy - 3} L{f(mx - mr * .82)},{f(my - mr * .57)} M{zx},{zy + 3} L{f(mx - mr * .82)},{f(my + mr * .57)}"/>'
    b += f'<circle class="ink" cx="{zx}" cy="{zy}" r="3.2" style="stroke-width:.4"/>'
    b += f'<circle class="wf" cx="{mx}" cy="{my}" r="{mr}"/><circle class="acc" cx="{mx}" cy="{my}" r="{mr}" style="stroke-width:.7"/>'
    b += f'<clipPath id="mz"><circle cx="{mx}" cy="{my}" r="{mr - .6}"/></clipPath><g clip-path="url(#mz)">'
    # ланац издужених ћелија
    for i in range(5):
        x = mx - 26 + i * 10.4
        b += f'<rect class="t2" x="{f(x)}" y="{my - 2.4}" width="10" height="4.8" rx="2.2"/>'
        b += f'<rect class="ink" x="{f(x)}" y="{my - 2.4}" width="10" height="4.8" rx="2.2" style="stroke-width:.4"/>'
    for i in range(3):
        y = my - 6 - i * 10.4
        b += f'<rect class="t2" x="{mx + 3}" y="{f(y - 8)}" width="4.8" height="10" rx="2.2"/>'
        b += f'<rect class="ink" x="{mx + 3}" y="{f(y - 8)}" width="4.8" height="10" rx="2.2" style="stroke-width:.4"/>'
    b += '</g>'
    # две празне линије за натпис
    b += f'<circle class="ldot" cx="{mx + 1}" cy="{my}" r=".55"/><path class="lead" d="M{mx + 1},{my} L{mx + 8},{my + 25}"/>'
    b += f'<path class="ink" style="stroke-width:.35" d="M{mx - 10},{my + 25.5} H{W - 1}"/>'
    b += f'<circle class="ldot" cx="26" cy="50" r=".55"/><path class="lead" d="M26,50 L19,12.5"/>'
    b += f'<path class="ink" style="stroke-width:.35" d="M4,12.5 H33"/>'
    return svg(W, H, b)
