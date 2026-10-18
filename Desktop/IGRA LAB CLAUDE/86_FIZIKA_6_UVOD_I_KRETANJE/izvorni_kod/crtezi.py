# Линијски цртежи за свеску Физика 6, сви као SVG у коду.
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



def dots(pts, r=.32, cls="inkf", op=.45):
    return "".join(f'<circle class="{cls}" cx="{f(x)}" cy="{f(y)}" r="{r}" style="opacity:{op}"/>' for x, y in pts)


def arrow(x1, y1, x2, y2, cls="acc", w=.6, head=1.6):
    a = math.atan2(y2 - y1, x2 - x1)
    hx1, hy1 = x2 - head * math.cos(a - .45), y2 - head * math.sin(a - .45)
    hx2, hy2 = x2 - head * math.cos(a + .45), y2 - head * math.sin(a + .45)
    return (f'<path class="{cls}" d="M{f(x1)},{f(y1)} L{f(x2)},{f(y2)}" style="stroke-width:{w}"/>'
            f'<path class="{cls}" d="M{f(hx1)},{f(hy1)} L{f(x2)},{f(y2)} L{f(hx2)},{f(hy2)}" style="stroke-width:{w}"/>')




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


def mission_stamp(size_mm=72, top="МИСИЈА 01 · ЗАВРШЕНА", bottom="ИСТРАЖИВАЧ 12+ · ФИЗИКА 6"):
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



def box(x, y, label=None, s=8.5):
    """Празно поле за упис слова или броја; x је десна половина ознаке."""
    g = ""
    if label:
        g += f'<text class="mtext" x="{f(x - 1.6)}" y="{f(y + s / 2 + 1)}" text-anchor="end">{label}</text>'
    g += f'<rect x="{f(x)}" y="{f(y)}" width="{s}" height="{s}" rx="1.2" style="fill:#fff;stroke:var(--ink);stroke-width:.35"/>'
    return g


def qlabel(x, y, q, sub="", rest="", anchor="middle", size=3.2):
    """Ознака величине курзивом са индексом, па остатак усправно: t₁ = 0 s."""
    return (f'<text x="{f(x)}" y="{f(y)}" text-anchor="{anchor}" class="stext" style="font-size:{size}px">'
            f'<tspan style="font-style:italic">{q}</tspan>{sub}{rest}</text>')


SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


# ---------------------------------------------------------------- 1. план насеља (задатак 37)

PLAN_DESNO, PLAN_GORE, PLAN_POLJE_M = 6, 4, 50      # број поља и дужина странице поља


def _house(x, y, s=1.0, cls="t2"):
    return (f'<g transform="translate({f(x)},{f(y)}) scale({s})">'
            f'<rect class="{cls}" x="-2.6" y="-2.6" width="5.2" height="4.2"/>'
            f'<rect class="ink" x="-2.6" y="-2.6" width="5.2" height="4.2" style="stroke-width:.3"/>'
            f'<path class="wf" d="M-3.4,-2.5 L0,-5.4 L3.4,-2.5 Z"/><path class="ink" d="M-3.4,-2.5 L0,-5.4 L3.4,-2.5 Z" style="stroke-width:.3"/>'
            f'<rect class="ink" x="-.7" y="-.4" width="1.4" height="2" style="stroke-width:.25"/></g>')


def _tree(x, y, s=1.0):
    return (f'<g transform="translate({f(x)},{f(y)}) scale({s})">'
            f'<path class="ink" d="M0,1.8 L0,-.4" style="stroke-width:.4"/>'
            f'<circle class="t3" cx="0" cy="-1.8" r="2"/><circle class="ink" cx="0" cy="-1.8" r="2" style="stroke-width:.3"/></g>')


def plan():
    bs, sw = 21.0, 3.2                         # страница поља и ширина улице у mm
    cols, rows = PLAN_DESNO, PLAN_GORE
    x0, y0 = 20, 8
    W, H = x0 + cols * bs + 20, y0 + rows * bs + 15
    b = f'<rect x="{x0 - sw}" y="{y0 - sw}" width="{cols * bs + 2 * sw}" height="{rows * bs + 2 * sw}" rx="2" style="fill:#fff;stroke:var(--rule);stroke-width:.3"/>'
    for i in range(cols):
        for j in range(rows):
            bx, by = x0 + i * bs + sw / 2, y0 + j * bs + sw / 2
            w = bs - sw
            b += f'<rect class="t1" x="{f(bx)}" y="{f(by)}" width="{f(w)}" height="{f(w)}" rx="1.4"/>'
            b += f'<rect class="ink" x="{f(bx)}" y="{f(by)}" width="{f(w)}" height="{f(w)}" rx="1.4" style="stroke-width:.3"/>'
            cx, cy = bx + w / 2, by + w / 2
            pat = (i * 3 + j * 2 + i * j) % 4
            if pat == 0:
                b += _house(cx - 4, cy + 2) + _tree(cx + 4.6, cy + 2.6)
            elif pat == 1:
                b += _tree(cx - 4.6, cy + 2.6) + _tree(cx + .4, cy + 4) + _house(cx + 4.4, cy - 2.4, .9)
            elif pat == 2:
                b += _house(cx - 3.6, cy - 2.4, .9) + _house(cx + 3.6, cy + 3.6, .9)
            else:
                b += _tree(cx, cy + 1.8, 1.2) + _tree(cx - 5, cy - 3.6, .8)
    # раскрснице као тачке
    for i in range(cols + 1):
        for j in range(rows + 1):
            b += f'<circle class="inkf" cx="{f(x0 + i * bs)}" cy="{f(y0 + j * bs)}" r=".45" style="opacity:.5"/>'
    # кућа А доле лево и школа Б горе десно
    ax, ay = x0, y0 + rows * bs
    bxp, byp = x0 + cols * bs, y0
    b += _house(ax - 10, ay + 1, 1.5, "t3")
    b += letter(ax, ay, "А", r=2.6)
    sx, sy = bxp + 10, byp + 2
    b += (f'<rect class="t3" x="{f(sx - 5)}" y="{f(sy - 3)}" width="10" height="7"/>'
          f'<rect class="ink" x="{f(sx - 5)}" y="{f(sy - 3)}" width="10" height="7" style="stroke-width:.35"/>'
          f'<path class="ink" d="M{f(sx - 6)},{f(sy - 3)} L{f(sx)},{f(sy - 6.4)} L{f(sx + 6)},{f(sy - 3)}" style="stroke-width:.35"/>'
          f'<path class="ink" d="M{f(sx)},{f(sy - 6.4)} V{f(sy - 10)}" style="stroke-width:.3"/>'
          f'<path class="accf" d="M{f(sx)},{f(sy - 10)} h3 l-1,1 l1,1 h-3 Z"/>'
          + "".join(f'<rect class="wf" x="{f(sx - 4 + 2.8 * q)}" y="{f(sy - 1.4)}" width="1.8" height="1.8"/>'
                    f'<rect class="ink" x="{f(sx - 4 + 2.8 * q)}" y="{f(sy - 1.4)}" width="1.8" height="1.8" style="stroke-width:.2"/>' for q in range(3)))
    b += letter(bxp, byp, "Б", r=2.6)
    # размера: једно поље
    yy = y0 + rows * bs + 8
    b += (f'<path class="ink" d="M{f(x0 + bs)},{f(yy - 1.2)} V{f(yy + 1.2)} M{f(x0 + 2 * bs)},{f(yy - 1.2)} V{f(yy + 1.2)} '
          f'M{f(x0 + bs)},{f(yy)} H{f(x0 + 2 * bs)}" style="stroke-width:.35"/>')
    b += f'<text class="stext" x="{f(x0 + 1.5 * bs)}" y="{f(yy + 4.6)}" text-anchor="middle">50 m</text>'
    return svg(W, H, b)


# ---------------------------------------------------------------- 2. точак бицикла на старту (задатак 36)

def wheel_strip():
    W, H = 172, 40
    r = 11.0
    road = H - 7
    cx, cy = 18, road - r
    b = f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="2.4" style="fill:#fff;stroke:var(--rule);stroke-width:.3"/>'
    b += f'<path class="ink" d="M4,{road} H{W - 4}" style="stroke-width:.6"/>'
    for i in range(int((W - 8) / 4)):
        x = 5 + i * 4
        b += f'<path class="ink" d="M{x},{road + .3} l-2,2.4" style="stroke-width:.25;opacity:.6"/>'
    b += f'<circle class="t2" cx="{cx}" cy="{cy}" r="{r}"/><circle class="wf" cx="{cx}" cy="{cy}" r="{r - 2.2}"/>'
    b += f'<circle class="ink" cx="{cx}" cy="{cy}" r="{r}" style="stroke-width:.5"/><circle class="ink" cx="{cx}" cy="{cy}" r="{r - 2.2}" style="stroke-width:.35"/>'
    for k in range(12):
        a = k * math.pi / 6
        b += f'<path class="ink" d="M{f(cx + 1.4 * math.cos(a))},{f(cy + 1.4 * math.sin(a))} L{f(cx + (r - 2.2) * math.cos(a))},{f(cy + (r - 2.2) * math.sin(a))}" style="stroke-width:.2"/>'
    b += f'<circle class="t3" cx="{cx}" cy="{cy}" r="1.4"/><circle class="ink" cx="{cx}" cy="{cy}" r="1.4" style="stroke-width:.3"/>'
    b += f'<circle class="accf" cx="{cx}" cy="{cy}" r=".9"/>'                               # осовина
    vx, vy = cx, road - 1.1
    b += f'<circle class="accf" cx="{vx}" cy="{vy}" r="1"/><circle class="ink" cx="{vx}" cy="{vy}" r="1" style="stroke-width:.25"/>'  # вентил
    b += f'<path class="lead" d="M{cx + .9},{cy - .6} L{cx + 15},{cy - 9}"/><text class="stext" x="{cx + 15.6}" y="{cy - 9.4}">осовина</text>'
    b += f'<path class="lead" d="M{vx + 1},{vy} L{vx + 15},{vy - 4}"/><text class="stext" x="{vx + 15.6}" y="{vy - 4.2}">вентил</text>'
    b += arrow(W - 30, 7, W - 10, 7, w=.5, head=1.4)
    b += f'<text class="mtext" x="{W - 32}" y="8" text-anchor="end">смер кретања</text>'
    return svg(W, H, b)


# ---------------------------------------------------------------- 3. и 4. дијаграм кретања и празна права (задаци 45 и 46)

KOLICA_V = 2          # m/s, колица на дијаграму
KOLICA_T = range(5)   # тренуци 0 s до 4 s


def number_line(points=()):
    W, H = 172, 30 if points else 22
    x0, step = 10, 15.0
    y = H - 11
    b = f'<path class="ink" d="M{x0 - 4},{y} H{x0 + 10 * step + 6}" style="stroke-width:.5"/>'
    b += (f'<path class="ink" d="M{x0 + 10 * step + 4},{y - 1.4} L{x0 + 10 * step + 6.4},{y} '
          f'L{x0 + 10 * step + 4},{y + 1.4}" style="stroke-width:.5"/>')
    for i in range(11):
        x = x0 + i * step
        b += f'<path class="ink" d="M{x},{y - 1.6} V{y + 1.6}" style="stroke-width:.4"/>'
        b += f'<text class="stext" x="{x}" y="{y + 6}" text-anchor="middle">{i}</text>'
        if i < 10:
            b += f'<path class="ink" d="M{x + step / 2},{y - .8} V{y + .8}" style="stroke-width:.25;opacity:.6"/>'
    b += f'<text class="stext" x="{x0 + 10 * step + 8.4}" y="{y + 6}" text-anchor="start">m</text>'
    for t, xm in points:
        x = x0 + xm * step
        b += f'<circle class="accf" cx="{f(x)}" cy="{y}" r="1.5"/>'
        b += qlabel(x, y - 4.4, "t", str(t).translate(SUB), f" = {t} s", size=3.1)
    return svg(W, H, b)


def motion_diagram():
    pts = [(t, KOLICA_V * t) for t in KOLICA_T]
    return number_line(pts)


# ---------------------------------------------------------------- 5. два сата (задатак 25)

ODMOR_T1, ODMOR_T2 = (10, 50), (11, 5)


def _clock(cx, cy, R, h, m, label_q, label_sub, cap):
    b = f'<circle class="t1" cx="{cx}" cy="{cy}" r="{R}"/><circle class="acc" cx="{cx}" cy="{cy}" r="{R}" style="stroke-width:.8"/>'
    for k in range(60):
        a = math.radians(k * 6 - 90)
        r1 = R - (2.2 if k % 5 == 0 else 1.1)
        b += (f'<path class="ink" d="M{f(cx + r1 * math.cos(a))},{f(cy + r1 * math.sin(a))} '
              f'L{f(cx + (R - .4) * math.cos(a))},{f(cy + (R - .4) * math.sin(a))}" style="stroke-width:{.45 if k % 5 == 0 else .2}"/>')
    for k in range(1, 13):
        a = math.radians(k * 30 - 90)
        b += f'<text class="stext" x="{f(cx + (R - 5) * math.cos(a))}" y="{f(cy + (R - 5) * math.sin(a) + 1.1)}" text-anchor="middle" style="font-size:2.9px">{k}</text>'
    ah = math.radians(((h % 12) + m / 60) * 30 - 90)
    am = math.radians(m * 6 - 90)
    b += f'<path class="ink" d="M{cx},{cy} L{f(cx + R * .5 * math.cos(ah))},{f(cy + R * .5 * math.sin(ah))}" style="stroke-width:1.1"/>'
    b += f'<path class="ink" d="M{cx},{cy} L{f(cx + R * .78 * math.cos(am))},{f(cy + R * .78 * math.sin(am))}" style="stroke-width:.6"/>'
    b += f'<circle class="accf" cx="{cx}" cy="{cy}" r="1"/>'
    b += qlabel(cx, cy + R + 6, label_q, label_sub, size=3.6)
    b += f'<text class="mtext" x="{cx}" y="{cy + R + 10.4}" text-anchor="middle">{cap}</text>'
    return b


def clocks():
    W, H = 100, 50
    b = _clock(25, 19, 16, *ODMOR_T1, "t", "₁", "почетак одмора")
    b += _clock(75, 19, 16, *ODMOR_T2, "t", "₂", "крај одмора")
    return svg(W, H, b)


# ---------------------------------------------------------------- 6. лоптица са чича Глишом и под (задатак 31)

def ball_face():
    W, H = 40, 50
    cx, cy, r = 20, 16, 8.5
    b = f'<circle cx="{cx}" cy="{cy - 9}" r="{r}" style="fill:none;stroke:var(--ink);stroke-width:.3;stroke-dasharray:.8 .9;opacity:.5"/>'
    b += f'<circle class="t2" cx="{cx}" cy="{cy}" r="{r}"/><circle class="ink" cx="{cx}" cy="{cy}" r="{r}" style="stroke-width:.55"/>'
    # чича Глиша: тачка, тачка, запета, минус... нацртано као лице
    b += f'<circle class="inkf" cx="{cx - 3}" cy="{cy - 2.4}" r=".75"/><circle class="inkf" cx="{cx + 3}" cy="{cy - 2.4}" r=".75"/>'
    b += f'<path class="ink" d="M{cx},{cy - 1.4} q-1,1.6 .4,2.2" style="stroke-width:.4"/>'
    b += f'<path class="ink" d="M{cx - 3.4},{cy + 3} q3.4,2.6 6.8,0" style="stroke-width:.45"/>'
    b += f'<path class="ink" d="M{cx - 6.6},{cy - 5.4} q1,-1.6 2.6,-1.4 M{cx + 6.6},{cy - 5.4} q-1,-1.6 -2.6,-1.4" style="stroke-width:.35"/>'
    b += arrow(cx + 12, cy - 4, cx + 12, cy + 14, w=.55, head=1.5)
    fy = H - 6
    b += f'<path class="ink" d="M2,{fy} H{W - 2}" style="stroke-width:.6"/>'
    for i in range(9):
        b += f'<path class="ink" d="M{4 + i * 4},{fy + .3} l-2.4,2.8" style="stroke-width:.25"/>'
    b += f'<text class="mtext" x="{W / 2}" y="{fy - 2}" text-anchor="middle">под</text>'
    return svg(W, H, b)


# ---------------------------------------------------------------- оглед код куће и насловна

def drop_icon():
    W, H = 44, 34
    b = '<g transform="translate(9,8) rotate(-12)"><rect class="wf" x="-7" y="-5" width="14" height="10"/>'
    b += '<rect class="ink" x="-7" y="-5" width="14" height="10" style="stroke-width:.35"/>'
    b += ''.join(f'<path class="ink" d="M-5,{-2.6 + 2.2 * i} H5" style="stroke-width:.15;opacity:.6"/>' for i in range(4)) + '</g>'
    b += '<g transform="translate(25,10) rotate(70)"><rect class="t3" x="-8" y="-1.1" width="13" height="2.2"/>'
    b += '<rect class="ink" x="-8" y="-1.1" width="13" height="2.2" style="stroke-width:.3"/>'
    b += '<path class="wf" d="M5,-1.1 L8.4,0 L5,1.1 Z"/><path class="ink" d="M5,-1.1 L8.4,0 L5,1.1 Z" style="stroke-width:.3"/></g>'
    b += blob(37, 10, 4.2, 3.8, waves=((5, .1, .3), (3, .06, 1)), n=30).join(['<path class="t1" d="', '"/>'])
    b += blob(37, 10, 4.2, 3.8, waves=((5, .1, .3), (3, .06, 1)), n=30).join(['<path class="ink" style="stroke-width:.35" d="', '"/>'])
    for x in (9, 25, 37):
        b += arrow(x, 19, x, 27, w=.45, head=1.2)
    b += f'<path class="ink" d="M2,{H - 3} H{W - 2}" style="stroke-width:.5"/>'
    return svg(W, H, b)


def cover_art():
    W, H = 170, 110
    b = '<g style="--acc:var(--c-kre)">'
    cl = blob(42, 22, 26, 11, waves=((5, .08, .2), (3, .05, 1.2), (8, .03, .4)), n=60)
    b += f'<path class="t1" d="{cl}"/><path class="ink" d="{cl}" style="stroke-width:.6"/>'
    bolt = "M44,30 L36,50 L44,50 L37,72 L56,44 L47,44 L54,30 Z"
    b += f'<path class="accf" d="{bolt}"/><path class="ink" d="{bolt}" style="stroke-width:.5"/></g>'
    b += '<g style="--acc:var(--c-fiz)">'
    for k, r in enumerate((10, 17, 24, 31)):
        b += (f'<path class="acc" d="M{f(70 + r * math.cos(-.6))},{f(56 + r * math.sin(-.6))} '
              f'A{r},{r} 0 0,1 {f(70 + r * math.cos(.6))},{f(56 + r * math.sin(.6))}" style="stroke-width:{.9 - k * .15}"/>')
    b += '</g>'
    b += f'<g style="--acc:var(--c-vel)">{_clock(136, 30, 20, 10, 50, "", "", "")}</g>'
    b += '<g style="--acc:var(--c-brz)" transform="translate(5,80)">'
    x0, step, y = 10, 14.0, 18
    b += f'<path class="ink" d="M{x0 - 4},{y} H{x0 + 10 * step + 4}" style="stroke-width:.5"/>'
    for i in range(11):
        b += f'<path class="ink" d="M{x0 + i * step},{y - 1.4} V{y + 1.4}" style="stroke-width:.35"/>'
    for t in range(6):
        b += f'<circle class="accf" cx="{x0 + 2 * t * step}" cy="{y}" r="1.5" style="opacity:{.35 + t * .13}"/>'
    cx = x0 + 10 * step - 4
    b += (f'<rect class="t3" x="{cx - 9}" y="{y - 11}" width="16" height="7" rx="1.2"/>'
          f'<rect class="ink" x="{cx - 9}" y="{y - 11}" width="16" height="7" rx="1.2" style="stroke-width:.4"/>'
          f'<circle class="wf" cx="{cx - 5}" cy="{y - 3}" r="2"/><circle class="ink" cx="{cx - 5}" cy="{y - 3}" r="2" style="stroke-width:.4"/>'
          f'<circle class="wf" cx="{cx + 3}" cy="{y - 3}" r="2"/><circle class="ink" cx="{cx + 3}" cy="{y - 3}" r="2" style="stroke-width:.4"/>')
    b += arrow(cx - 30, y - 8, cx - 14, y - 8, w=.6, head=1.6)
    b += '</g>'
    return svg(W, H, b)
