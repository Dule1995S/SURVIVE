"""20s calm-upbeat corporate bed, 120 BPM, 10 bars of 2s, no vocals.
Scene cuts at 4/9/14/18s get a soft reverse-noise swell. Deterministic (seeded)."""
import sys
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
import wave

SR = 44100
DUR = 20.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N)
R = np.zeros(N)


def note(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def add(sig, t0, pan=0.0, gain=1.0):
    i0 = int(t0 * SR)
    if i0 >= N:
        return
    sig = sig[: N - i0] * gain
    l = np.cos((pan + 1) * np.pi / 4)
    r = np.sin((pan + 1) * np.pi / 4)
    L[i0 : i0 + len(sig)] += sig * l
    R[i0 : i0 + len(sig)] += sig * r


def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, "low", fs=SR, output="sos"), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)


def saw(f, t):
    # band-limited-ish saw via a few harmonics
    out = np.zeros_like(t)
    for k in range(1, 12):
        if f * k > 9000:
            break
        out += np.sin(2 * np.pi * f * k * t) / k
    return out


# C major: Cmaj7, G(add), Am7, Fmaj7 ; last two bars F -> C
CHORDS = [
    [48, 60, 64, 67, 71],
    [43, 55, 62, 67, 71],
    [45, 57, 60, 64, 67],
    [41, 53, 57, 60, 64],
] * 2 + [[41, 53, 57, 60, 67], [48, 60, 64, 67, 72]]
BAR = 2.0

# ---- pad ----
for b, ch in enumerate(CHORDS):
    dur = BAR + 0.6
    t = np.arange(int(dur * SR)) / SR
    env = np.minimum(t / 0.35, 1) * np.clip((dur - t) / 0.6, 0, 1)
    for m in ch[1:]:
        for det, pan in ((-0.06, -0.6), (0.06, 0.6)):
            f = note(m) * 2 ** (det / 12)
            s = lp(saw(f, t), 1400) * env
            add(s, b * BAR, pan, 0.028)

# ---- bass ----
for b, ch in enumerate(CHORDS):
    root = ch[0]
    for beat in range(4):
        t0 = b * BAR + beat * 0.5
        if b == 0 and beat < 2:
            continue
        d = 0.45
        t = np.arange(int(d * SR)) / SR
        env = np.exp(-t * 3.5) * np.minimum(t / 0.01, 1)
        f = note(root - 12 if root > 44 else root)
        s = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.15 * np.sin(2 * np.pi * 3 * f * t)) * env
        add(s, t0, 0, 0.16 if beat % 2 == 0 else 0.11)

# ---- pluck arpeggio (8ths) ----
PAT = [0, 2, 1, 2, 3, 2, 1, 2]
for b, ch in enumerate(CHORDS):
    tones = [ch[1] + 12, ch[2] + 12, ch[3] + 12, ch[1] + 24]
    for k in range(8):
        t0 = b * BAR + k * 0.25
        m = tones[PAT[k] % len(tones)] if PAT[k] < 3 else tones[3]
        d = 0.5
        t = np.arange(int(d * SR)) / SR
        env = np.exp(-t * 9) * np.minimum(t / 0.004, 1)
        f = note(m)
        s = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 14) + 0.2 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 20)) * env
        g = 0.055 if b == 0 else 0.065
        add(s, t0, 0.35 if k % 2 else -0.35, g)

# ---- drums (from bar 2 to 19.5s) ----
def kick():
    d = 0.35
    t = np.arange(int(d * SR)) / SR
    f = 45 + 85 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9) * 1.0


def clap():
    d = 0.22
    t = np.arange(int(d * SR)) / SR
    n = rng.standard_normal(len(t))
    env = np.exp(-t * 22) + 0.6 * np.exp(-((t - 0.012) ** 2) / 0.00002)
    return bp(n, 900, 3500) * env


def hat(open_=False):
    d = 0.18 if open_ else 0.05
    t = np.arange(int(d * SR)) / SR
    n = rng.standard_normal(len(t))
    return hp(n, 7000) * np.exp(-t * (18 if open_ else 70))


for b in range(1, 10):
    for beat in range(4):
        t0 = b * BAR + beat * 0.5
        if t0 >= 19.5:
            break
        if beat in (0, 2):
            add(kick(), t0, 0, 0.55)
        if beat in (1, 3) and b >= 2:
            add(clap(), t0, 0.1, 0.16)
        add(hat(), t0, 0.3, 0.05)
        add(hat(open_=True), t0 + 0.25, 0.3, 0.06)
    if b >= 2:
        for s16 in range(16):
            t0 = b * BAR + s16 * 0.125
            if t0 >= 19.5:
                break
            add(hat(), t0, -0.4, 0.018 if s16 % 2 else 0.01)

# ---- transition swells into each scene cut ----
for cut in (4.0, 9.0, 14.0, 18.0):
    d = 0.6
    t = np.arange(int(d * SR)) / SR
    n = rng.standard_normal(len(t))
    env = (t / d) ** 2.2
    s = bp(n, 1500, 8000) * env
    add(s, cut - d, -0.2, 0.09)

# final chord bell on CTA
for m in (72, 76, 79):
    d = 2.0
    t = np.arange(int(d * SR)) / SR
    s = np.sin(2 * np.pi * note(m) * t) * np.exp(-t * 2.2) * np.minimum(t / 0.005, 1)
    add(s, 18.0, 0.0, 0.05)

# ---- reverb ----
ir_len = int(1.3 * SR)
tt = np.arange(ir_len) / SR
irL = rng.standard_normal(ir_len) * np.exp(-tt * 4.2)
irR = rng.standard_normal(ir_len) * np.exp(-tt * 4.2)
irL = lp(irL, 5000)
irR = lp(irR, 5000)
irL /= np.sqrt((irL ** 2).sum())
irR /= np.sqrt((irR ** 2).sum())
wetL = fftconvolve(L, irL)[:N]
wetR = fftconvolve(R, irR)[:N]
L = L + 0.22 * wetL
R = R + 0.22 * wetR

# ---- master: low-cut, fades, soft clip ----
L = hp(L, 35)
R = hp(R, 35)
t = np.arange(N) / SR
fade = np.minimum(t / 0.05, 1) * np.clip((DUR - t) / 0.9, 0, 1)
L *= fade
R *= fade
peak = max(np.abs(L).max(), np.abs(R).max())
L = np.tanh(L / peak * 1.1) / np.tanh(1.1) * 0.89
R = np.tanh(R / peak * 1.1) / np.tanh(1.1) * 0.89

out = np.stack([L, R], axis=1)
pcm = (out * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote", sys.argv[1])
