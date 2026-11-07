"""Synthesized sound-design layer for the explainer (no music).

Every effect is generated procedurally and placed on the same timeline as
index.html, then mixed under the voiceover with ducking, stereo panning
(following on-screen position) and a light reverb.

usage: python3 sfx.py vo.wav out_mix.wav
"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve, resample_poly

SR = 48000
DUR = 63.0
N = int(SR * DUR)
rng = np.random.default_rng(1234)

# ------------------------------------------------------------------ timeline
SEG = [
 (0.21,1.61,'إنت صاحب مشروع صغير؟'),(2.09,2.93,'طب قولّي بصراحة...'),(3.73,5.85,'يومك بيخلص قبل ما شغلك يخلص؟'),
 (6.74,7.82,'عارفين الإحساس ده.'),(8.44,10.25,'ردود على العملا، فواتير،'),(10.52,11.73,'بوستات للسوشيال ميديا...'),
 (12.15,12.77,'وفي الآخر،'),(13.10,14.65,'مفيش وقت للحاجة الأهم:'),(15.18,16.52,'إنك تكبّر مشروعك.'),
 (17.24,19.14,'طب إيه رأيك لو قلتلك إن فيه مساعد...'),(19.47,21.19,'بيشتغل ٢٤ ساعة،'),(21.52,22.23,'مبيتعبش،'),
 (22.55,23.58,'ومش هياخد مرتب؟'),(24.13,25.21,'ده الذكاء الاصطناعي!'),(26.04,27.13,'تعالى نشوف بيعمل إيه،'),
 (27.31,28.48,'في تلات خطوات بسيطة.'),(29.14,29.56,'أولاً:'),(29.87,32.32,'بيرد على أسئلة العملا المتكررة على الواتساب...'),
 (32.52,33.06,'في ثواني.'),(33.79,34.20,'تانياً:'),(34.47,36.01,'بيكتبلك بوستات وإعلانات.'),(36.33,37.55,'إنت بس تقوله عايز إيه.'),
 (38.14,38.54,'تالتاً:'),(38.83,40.59,'بيرتّبلك الحسابات والفواتير،'),(40.82,42.77,'ويطلّعلك تقرير في آخر كل شهر.'),
 (43.38,45.42,'يعني بدل ما تقضي ٣ ساعات في الحاجات دي...'),(45.79,47.14,'تخلّصها في ربع ساعة.'),(47.78,48.62,'والأهم من كده؟'),
 (49.00,50.08,'الوقت اللي وفّرته ده...'),(50.32,50.84,'بتاعك.'),(51.31,52.54,'تفكّر، تخطّط،'),(52.85,54.24,'أو حتى تقعد مع عيلتك شوية.'),
 (54.87,55.67,'فمتستناش.'),(56.03,57.73,'ابدأ النهارده بأداة واحدة بس...'),(58.00,59.20,'وشوف الفرق بنفسك.'),
 (59.76,60.81,'مشروعك يستاهل...'),(61.10,62.03,'وإنت كمان تستاهل.'),
]
def wt(i, j):
    s, e, txt = SEG[i]
    ws = txt.split(' ')
    w = [len(x.translate({ord(c): None for c in '.،؟!:'})) + 1.5 for x in ws]
    tot = sum(w); j = min(j, len(ws) - 1)
    return s + (e - s) * 0.94 * sum(w[:j]) / tot - 0.06

# ------------------------------------------------------------------ dsp helpers
def t_(d): return np.arange(int(d * SR)) / SR
def noise(d): return rng.standard_normal(int(d * SR))
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def norm(x, peak=1.0):
    m = np.max(np.abs(x)) + 1e-9
    return x / m * peak
def env_ad(n, a, d, curve=4.0):
    """attack seconds a, then exponential decay over the rest (d = decay time const)."""
    t = np.arange(n) / SR
    e = np.where(t < a, (t / max(a, 1e-4)) ** 1.5, np.exp(-(t - a) / d))
    return e
def fade(x, fi=0.002, fo=0.01):
    n = len(x); a = int(fi * SR); b = int(fo * SR)
    if a: x[:a] *= np.linspace(0, 1, a)
    if b: x[-b:] *= np.linspace(1, 0, b)
    return x

def svf(x, cutoff, q=0.7, mode='bp'):
    """time-varying state-variable filter (cutoff array in Hz)."""
    cutoff = np.broadcast_to(cutoff, x.shape)
    g = np.tan(np.pi * np.clip(cutoff, 20, SR * 0.45) / SR)
    k = 1.0 / q
    ic1 = ic2 = 0.0
    out = np.empty_like(x)
    for i in range(len(x)):
        gi = g[i]
        a1 = 1.0 / (1.0 + gi * (gi + k)); a2 = gi * a1; a3 = gi * a2
        v3 = x[i] - ic2
        v1 = a1 * ic1 + a2 * v3
        v2 = ic2 + a2 * ic1 + a3 * v3
        ic1 = 2 * v1 - ic1; ic2 = 2 * v2 - ic2
        out[i] = v1 if mode == 'bp' else (v2 if mode == 'lp' else x[i] - k * v1 - v2)
    return out

def pink(d):
    n = int(d * SR); w = rng.standard_normal(n)
    f = np.fft.rfft(w); fr = np.fft.rfftfreq(n, 1 / SR); fr[0] = 1
    return norm(np.fft.irfft(f / np.sqrt(fr), n))

# ------------------------------------------------------------------ sound designs
def whoosh(d=0.55, f0=400, f1=4000, q=1.2, peak_at=0.6, bright=1.0):
    n = int(d * SR); t = np.arange(n) / n
    cut = f0 * (f1 / f0) ** np.sin(np.pi * np.clip(t / peak_at, 0, 1) * 0.5) if peak_at < 1 else f0 * (f1 / f0) ** t
    x = svf(pink(d) * 0.7 + noise(d) * 0.3 * bright, cut, q, 'bp')
    e = np.where(t < peak_at, (t / peak_at) ** 2.2, np.exp(-(t - peak_at) / (1 - peak_at) * 4))
    return fade(norm(x * e))

def swipe():  # big transition whoosh with a sub layer
    a = whoosh(0.75, 250, 6000, 0.9, 0.55)
    tt = t_(0.75); sub = np.sin(2 * np.pi * (60 + 40 * tt) * tt) * np.exp(-((tt - 0.42) / 0.16) ** 2) * 0.2
    return norm(a + sub[:len(a)])

def pop(f=520, d=0.16, drop=1.8, click=0.25):
    tt = t_(d); fr = f * (1 + (drop - 1) * np.exp(-tt / 0.012))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    x = np.sin(ph) * np.exp(-tt / (d * 0.28)) + 0.25 * np.sin(2 * ph) * np.exp(-tt / (d * 0.12))
    c = hp(noise(0.006), 2500) * np.exp(-np.arange(int(0.006 * SR)) / (0.0015 * SR)) * click
    x[:len(c)] += c
    return fade(norm(x), 0.0005)

def bell(f=1320, d=1.2, ratio=3.51, idx=2.5, bright=0.6):
    tt = t_(d); e = np.exp(-tt / (d * 0.3))
    m = np.sin(2 * np.pi * f * ratio * tt) * idx * np.exp(-tt / (d * 0.12))
    x = np.sin(2 * np.pi * f * tt + m) * e + bright * 0.3 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt / (d * 0.08))
    return fade(norm(x), 0.001, 0.05)

def chime(notes=(1046.5, 1568), gap=0.07, d=1.4):
    out = np.zeros(int((gap * len(notes) + d) * SR))
    for i, f in enumerate(notes):
        b = bell(f, d, 2.0, 1.2) * (0.9 ** i); s = int(i * gap * SR); out[s:s + len(b)] += b
    return norm(out)

def sparkle(d=1.0, n=14, lo=2500, hi=7000, density_tail=True):
    out = np.zeros(int((d + 0.5) * SR))
    for i in range(n):
        s = rng.uniform(0, d) * (rng.uniform(0, 1) if density_tail else 1)
        f = rng.uniform(lo, hi); b = bell(f, 0.35, 1.41, 0.8) * rng.uniform(0.3, 1)
        k = int(s * SR); out[k:k + len(b)] += b[:len(out) - k]
    return norm(out)

def tick(f=3200, d=0.03, g=1.0):
    tt = t_(d); x = np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.004) + hp(noise(d), 3000) * np.exp(-tt / 0.0015) * 0.6
    return norm(x) * g

def blip(f1=880, f2=1320, d=0.22):
    tt = t_(d); half = int(len(tt) * 0.4)
    fr = np.where(np.arange(len(tt)) < half, f1, f2)
    x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * env_ad(len(tt), 0.004, 0.05)
    x += 0.2 * np.sin(2 * 2 * np.pi * np.cumsum(fr) / SR) * env_ad(len(tt), 0.004, 0.03)
    return fade(norm(x), 0.002, 0.02)

def impact(d=2.2):
    tt = t_(d)
    sub = np.sin(2 * np.pi * np.cumsum(45 + 110 * np.exp(-tt / 0.06)) / SR) * np.exp(-tt / 0.55)
    body = lp(noise(d), 900, 4) * np.exp(-tt / 0.12) * 0.9
    crack = hp(noise(d), 2500) * np.exp(-tt / 0.025) * 0.5
    tail = bp(noise(d), 300, 3000) * np.exp(-tt / 0.6) * 0.12
    return fade(norm(np.tanh(1.6 * (sub * 1.2 + body + crack + tail))), 0.0005, 0.2)

def thud(f=70, d=0.45, g=1.0):
    tt = t_(d)
    x = np.sin(2 * np.pi * np.cumsum(f + 90 * np.exp(-tt / 0.03)) / SR) * np.exp(-tt / 0.11)
    x += lp(noise(d), 1200) * np.exp(-tt / 0.02) * 0.5
    return fade(norm(x), 0.0005) * g

def riser(d=1.2, f0=300, f1=6000):
    n = int(d * SR); tt = np.arange(n) / SR; k = tt / d
    cut = f0 * (f1 / f0) ** (k ** 1.6)
    x = svf(noise(d), cut, 2.5, 'bp')
    tone = np.sin(2 * np.pi * np.cumsum(150 * (8 ** k)) / SR) * 0.25
    trem = 0.75 + 0.25 * np.sin(2 * np.pi * (4 + 18 * k) * tt)
    return fade(norm((x + tone) * trem * k ** 2.2), 0.01, 0.004)

def reverse_swell(d=0.9):
    return norm(sparkle(d * 0.8, 18)[::-1][-int(d * SR):] * 1.0 + riser(d, 800, 9000) * 0.6)

def paper(d=0.18):
    tt = t_(d); x = bp(noise(d), 1200, 7000) * env_ad(len(tt), 0.01, 0.04) * (0.6 + 0.4 * np.sin(2 * np.pi * 70 * tt))
    return fade(norm(x))

def keyclick():
    d = 0.045; tt = t_(d)
    x = bp(noise(d), 1800, 6000) * np.exp(-tt / 0.006) + np.sin(2 * np.pi * rng.uniform(900, 1400) * tt) * np.exp(-tt / 0.01) * 0.4
    return norm(x)

def stamp():
    return norm(thud(90, 0.5) + np.pad(bp(noise(0.08), 400, 2500) * np.exp(-t_(0.08) / 0.015) * 0.7, (0, int(0.42 * SR))))

def sweep(f0, f1, d, wave='sine'):
    tt = t_(d); k = tt / d; fr = f0 * (f1 / f0) ** k
    ph = 2 * np.pi * np.cumsum(fr) / SR
    x = np.sin(ph) + 0.3 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
    return fade(norm(x * np.sin(np.pi * k) ** 0.8), 0.005, 0.02)

def charge(d=0.6):
    tt = t_(d); k = tt / d
    ph = 2 * np.pi * np.cumsum(200 * (6 ** k)) / SR
    saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
    return fade(norm(lp(saw, 3000) * (0.3 + 0.7 * k) * (0.8 + 0.2 * np.sin(2 * np.pi * 30 * tt))))

def sand(d=1.0):
    x = np.zeros(int(d * SR)); idx = rng.integers(0, len(x) - 200, int(d * 900))
    for i in idx: x[i:i + 60] += rng.uniform(.2, 1) * np.exp(-np.arange(60) / 8) * rng.choice([-1, 1])
    k = np.arange(len(x)) / len(x)
    return norm(hp(x, 2500) * (1 - k) ** 0.7)

def rattle(d=0.7):
    out = np.zeros(int(d * SR))
    for i in range(int(d * 22)):
        s = int(i / 22 * SR) + rng.integers(0, 300); c = paper(0.05) * rng.uniform(.4, 1)
        out[s:s + len(c)] += c[:len(out) - s]
    return norm(out)

# ------------------------------------------------------------------ reverb
def make_ir(d=1.1):
    n = int(d * SR); tt = np.arange(n) / SR
    irs = []
    for _ in range(2):
        ir = lp(noise(d), 6000) * np.exp(-tt / 0.28)
        ir[:int(0.012 * SR)] = 0
        irs.append(ir / np.sqrt(np.sum(ir ** 2)))
    return irs
IR = make_ir()

# ------------------------------------------------------------------ cue list
L = np.zeros(N); R = np.zeros(N); WET = np.zeros((2, N))
def place(sig, t, gain_db=0.0, pan=0.0, rev=0.15, pitch=1.0):
    """pan: -1 left .. +1 right (equal power)."""
    if pitch != 1.0:
        up, down = int(round(1000 / pitch)), 1000
        sig = resample_poly(sig, up, down)
    g = 10 ** (gain_db / 20)
    a = (pan + 1) * np.pi / 4
    s = int(t * SR)
    if s >= N: return
    if s < 0: sig = sig[-s:]; s = 0
    sig = sig[:N - s] * g
    L[s:s + len(sig)] += sig * np.cos(a); R[s:s + len(sig)] += sig * np.sin(a)
    WET[0, s:s + len(sig)] += sig * np.cos(a) * rev; WET[1, s:s + len(sig)] += sig * np.sin(a) * rev
def px(x): return (x - 960) / 960 * 0.8  # screen x -> pan

# Scene A: shop, clock, dusk
place(pop(380, 0.22), 0.18, -6, 0, .2)
for i in range(8): place(pop(700 + i * 90, 0.09, 1.5, .4), 0.40 + i * 0.05, -16, px(710 + i * 62), .2)
place(chime((1318.5, 1975.5)), 0.78, -16, 0, .35)
place(whoosh(0.6, 300, 2500), 1.85, -15, -0.3, .1)
place(pop(300, 0.25), 3.48, -8, px(1330), .2)
tt = 3.7
while tt < 6.3:  # accelerating clock ticks
    place(tick(2600 if int(tt * 10) % 2 else 2100, g=1), tt, -18, px(1330), .1)
    tt += max(0.06, 0.32 - (tt - 3.7) * 0.11)
place(sparkle(0.9, 10, 3000, 6000), 5.2, -22, -0.2, .4)

# transitions
for t0 in [6.45, 16.95, 28.85, 43.1, 47.5, 54.6]:
    place(swipe(), t0 - 0.42, -9, 0, .2)

# Scene B: overwhelm
place(thud(60, 0.6), wt(3, 0), -12, 0, .3)
for t0, x in [(wt(4, 0), 1420), (wt(4, 3), 960), (wt(5, 0), 500)]:
    place(paper(0.2), t0 - 0.03, -13, px(x), .1); place(pop(260, 0.2, 2.2), t0 + 0.05, -9, px(x), .15)
pills = np.random.default_rng(42)
for i in range(16):
    x = 280 + pills.random() * 1360; pills.random()
    place(blip(*[(880, 1320), (988, 1480), (784, 1175), (1047, 1568)][i % 4]), 9.0 + i * 0.19, -19 + min(i, 8) * 0.4, px(x), .15)
place(rattle(1.2), 10.7, -24, 0, .1)
place(sweep(900, 120, 0.9), 12.1, -16, 0, .2)
place(whoosh(0.8, 2500, 200, 1.0, 0.3), 12.12, -12, 0, .15)
place(thud(55, 0.7), 12.75, -14, 0, .3)
place(pop(330, 0.22), 13.05, -9, 0, .2)
place(sand(1.1), 13.1, -20, 0, .2)
place(pop(400, 0.18), 15.1, -11, 0, .2)
for i, f in enumerate([523.3, 659.3, 784, 1046.5]): place(bell(f, 0.6, 2, 1.0), 15.25 + i * 0.12, -18, px(740 + i * 150), .25)
place(riser(0.85, 500, 7000), 15.45, -19, 0.2, .2)
place(chime((1568, 2093)), 16.2, -15, 0.3, .4)

# Scene C: assistant
place(reverse_swell(1.1), 17.25, -15, 0, .3)
place(pop(240, 0.3, 2.4), 18.3, -7, 0, .25)
place(norm(sweep(600, 1500, 0.12)), 18.55, -17, 0, .3); place(norm(sweep(1500, 900, 0.1)), 18.68, -17, 0, .3)  # robot "boop"
place(sweep(300, 900, 1.6), 19.5, -24, 0, .3)
place(pop(500, 0.18), 19.5, -11, px(1450), .2); place(bell(1760, .8, 2, 1), 19.55, -21, px(1450), .3)
place(charge(0.6), 21.55, -19, px(1450), .15); place(pop(560, 0.18), 21.5, -11, px(1450), .2); place(blip(1175, 1760), 22.12, -18, px(1450), .2)
place(pop(460, 0.18), 22.55, -11, px(370), .2); place(blip(1568, 1047), 22.65, -19, px(370), .2)

# Scene D: reveal
place(riser(1.25, 200, 9000), 24.05 - 1.25, -9, 0, .2)
place(impact(), 24.05, -3, 0, .35)
place(sparkle(1.4, 26, 2500, 8000), 24.1, -15, 0, .5)
place(sweep(2000, 4000, 1.2), 24.15, -27, 0, .5)

# Scene E: three steps
place(whoosh(0.5, 400, 3000), 25.8, -17, 0, .1)
for i, (x, f) in enumerate([(1460, 659.3), (960, 784), (460, 1046.5)]):
    t0 = wt(15, i) + 0.05 + (0.05 if i == 2 else 0)
    place(pop(300 + i * 80, 0.2), t0, -9, px(x), .2); place(bell(f, 0.9, 2, 1.0), t0 + 0.02, -17, px(x), .3)

# Scene F: chat
place(whoosh(0.6, 300, 3500), 28.85, -14, -0.4, .1)
for t0, kind in [(29.95, 'in'), (30.85, 'out'), (31.35, 'in'), (32.0, 'out')]:
    if kind == 'in': place(blip(1047, 1397, 0.16), t0, -15, -0.25, .15)
    else: place(whoosh(0.18, 1500, 6000, 1.5, 0.3), t0 - 0.06, -19, -0.35, .1); place(pop(820, 0.1, 1.4, .3), t0, -15, -0.35, .15)
for a, b in [(30.3, 30.85), (31.55, 32.0)]:
    tt = a
    while tt < b: place(tick(1800, g=.6), tt, -27, -0.35, .1); tt += 0.09
place(pop(520, 0.18), wt(18, 0), -10, -0.1, .2); place(chime((2093, 2637), 0.05, 0.9), wt(18, 0) + 0.04, -14, -0.1, .35)
for k in range(5): place(tick(4000, g=.7), wt(18, 0) + 0.1 + k * 0.06, -25, -0.1, .1)

# Scene G: content writing
place(whoosh(0.6, 300, 3500), 33.5, -14, -0.4, .1)
place(pop(300, 0.22), wt(20, 1), -10, -0.4, .2); place(pop(420, 0.2), wt(20, 2), -11, -0.4, .2)
cap_len = len('عرض الأسبوع! خصم ٢٠٪ على كل المنتجات')
for i in range(cap_len):
    if rng.random() < 0.85: place(keyclick(), 34.5 + 1.4 * i / cap_len + rng.uniform(-0.01, 0.01), -24 + rng.uniform(-3, 2), -0.4, .05)
for i in range(8): place(pop(900 + i * 60, 0.08, 1.3, .2), 35.4 + i * 0.25, -23, -0.45, .2)
place(pop(600, 0.16), wt(21, 0) - 0.1, -12, -0.3, .2)
pl = len('اكتبلي بوست لعرض الأسبوع')
for i in range(pl): place(keyclick(), 36.4 + 0.9 * i / pl, -25 + rng.uniform(-2, 2), -0.3, .05)
place(whoosh(0.25, 1200, 7000, 1.5, 0.4), 37.32, -18, -0.3, .15)

# Scene H: books & reports
place(whoosh(0.6, 300, 3500), 37.85, -14, -0.4, .1)
for i in range(3): place(paper(0.18), 38.0 + i * 0.12, -14, px(450 + i * 110), .1)
for i in range(3): place(whoosh(0.35, 800, 5000, 1.4, 0.5), 38.95 + i * 0.12, -19, -0.4, .1)
place(sparkle(0.7, 12, 3000, 7000), 39.0, -21, -0.4, .3)
place(pop(350, 0.2), 39.55, -11, -0.45, .2)
for i, f in enumerate([523.3, 587.3, 659.3, 784, 1046.5]): place(bell(f, 0.5, 2, 0.9), 39.75 + i * 0.1, -20, -0.45, .2)
place(whoosh(0.7, 200, 2500, 0.9, 0.6), 40.7, -12, -0.35, .15)
place(sweep(500, 1600, 0.9), 41.3, -27, -0.35, .2)
place(stamp(), 42.15, -8, -0.4, .25)
place(chime((1568, 2349)), 42.2, -17, -0.4, .4)

# Scene I: 3h -> 15m
place(sweep(220, 660, 1.3), 43.4, -20, 0, .3)
place(pop(260, 0.26), 43.5, -10, 0, .2)
for i in range(3): place(pop(700 + i * 120, 0.1, 1.4, .3), 43.6 + i * 0.15, -20, px(960 + 350 * np.cos(i * 2.094)), .2)
place(sweep(1800, 260, 0.9), 45.85, -15, 0, .3)
place(whoosh(0.9, 6000, 300, 1.2, 0.2), 45.85, -16, 0, .2)
place(pop(380, 0.24), 46.0, -9, 0, .2)
place(chime((1046.5, 1318.5, 1568), 0.06, 1.6), 46.05, -14, 0, .45)

# Scene J: your time, your family
place(thud(65, 0.6, 1), wt(27, 0), -14, 0, .35)
place(pop(300, 0.22), 48.95, -9, 0, .2)
place(rattle(0.7), 49.6, -20, 0, .1)
place(pop(520, 0.2, 2.0), 50.3, -9, 0.2, .2)
place(whoosh(0.5, 600, 5000, 1.2, 0.4), 50.3, -17, 0.4, .1)
place(sparkle(1.3, 22, 2500, 7500), 50.32, -14, 0, .55)
place(bell(1318.5, 1.0, 2, 1), 50.55, -18, 0.1, .4)
place(pop(460, 0.18), wt(30, 0), -10, px(1520), .2); place(bell(2093, 0.9, 1.41, 1.5), wt(30, 0) + 0.05, -16, px(1520), .4)
place(pop(400, 0.18), wt(30, 1), -10, px(1190), .2)
for i in range(3): place(tick(2400, g=.8), wt(30, 1) + 0.3 + i * 0.2, -19, px(1190), .2)
place(pop(240, 0.3, 2.0), wt(31, 0), -9, px(620), .25)
for i in range(4): place(pop(500 + i * 70, 0.12, 1.5, .2), wt(31, 0) + 0.15 + i * 0.12, -20, px(620), .2)
place(chime((784, 1046.5, 1318.5), 0.08, 2.0), wt(31, 3) + 0.2, -15, px(620), .55)

# Scene K: call to action
place(riser(0.5, 400, 6000), wt(32, 0) - 0.5, -17, 0, .2)
place(impact(1.6), wt(32, 0), -6, 0, .3)
place(pop(330, 0.24), 56.05, -9, 0, .2)
place(whoosh(0.7, 500, 2500, 1.0, 0.7), 56.3, -24, 0.3, .05)
place(norm(tick(2200, 0.03) + np.pad(tick(1400, 0.03), (int(0.025 * SR), 0))[:int(0.03 * SR)]), 57.05, -8, 0, .15)
place(thud(110, 0.3), 57.05, -14, 0, .2)
place(chime((1568, 2093), 0.05, 1.2), 57.1, -15, 0, .4)
place(whoosh(0.6, 300, 3500), 57.85, -14, 0, .1)
place(pop(500, 0.18), 58.3, -12, 0, .2)
place(riser(0.9, 500, 5000), 58.4, -20, -0.3, .2)
place(bell(1568, 0.9, 2, 1), 59.3, -18, -0.3, .4)

# Scene L: end card
place(whoosh(0.6, 250, 3000), 59.45, -15, 0, .2)
place(pop(300, 0.26), 59.62, -8, 0, .25)
for i in range(8): place(pop(700 + i * 90, 0.09, 1.5, .4), 59.75 + i * 0.05, -18, px(710 + i * 62), .2)
for i, (x, _) in enumerate([(700, 0), (1220, 0), (650, 0), (1270, 0)]): place(bell(2637 + i * 200, 0.7, 1.41, 1.2), 60.0 + i * 0.2, -22, px(x), .45)
place(riser(0.7, 600, 8000), wt(36, 0) - 0.65, -18, 0, .2)
place(impact(1.4), wt(36, 0) + 0.05, -12, 0, .3)
place(sparkle(1.8, 30, 2500, 8000), wt(36, 0) + 0.05, -14, 0, .55)
place(chime((523.3, 784, 1046.5, 1568), 0.09, 2.6), wt(36, 0) + 0.1, -14, 0, .6)

# ------------------------------------------------------------------ mix
sfx = np.stack([L, R])
for c in range(2):
    sfx[c] += fftconvolve(WET[c], IR[c])[:N] * 1.4
sfx = hp(sfx, 35)

sr, vo = wavfile.read(sys.argv[1])
vo = vo.astype(np.float64) / 32768.0
if vo.ndim > 1: vo = vo.mean(1)
if sr != SR: vo = resample_poly(vo, SR, sr)
vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]

# duck SFX under the voice (smoothed envelope, ~5 dB)
envv = np.sqrt(lp(vo ** 2, 12, 1).clip(0))
envv = envv / (np.percentile(envv, 95) + 1e-9)
duck = 1 - 0.45 * np.clip(envv, 0, 1)
duck = lp(duck, 6, 1)
sfx *= duck

mix = np.stack([vo, vo]) * 0.70 + sfx * 0.47
# gentle bus glue + safety limiter
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
peak = np.max(np.abs(mix))
if peak > 0.97: mix *= 0.97 / peak
wavfile.write(sys.argv[2], SR, (mix.T * 32767).astype(np.int16))
wavfile.write(sys.argv[2].replace('.wav', '_sfx_only.wav'), SR, (norm(sfx.T, 0.9) * 32767).astype(np.int16))
print('ok', sys.argv[2])
