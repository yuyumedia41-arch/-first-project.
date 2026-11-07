"""Cartoon sound design for "Youssef's magic piggy bank" (no music).
usage: python3 kids_sfx.py vo48.wav mix.wav
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly, fftconvolve
from sfxlib import *   # SR, noise, pink, bp, lp, hp, norm, fade, svf, whoosh, pop, bell, chime, sparkle, tick, blip, impact, thud, riser, paper, sweep, rattle, sand, make_ir ...

DUR = 92.0
N = int(SR * DUR)
R = np.random.default_rng(7)

# ---------------- extra cartoon sounds ----------------
def clink(f=2700, d=0.35, g=1.0):
    tt = t_(d); parts = [(1, 1), (2.32, .6), (4.25, .35), (6.63, .2)]
    x = sum(a * np.sin(2 * np.pi * f * r * tt + R.uniform(0, 6)) * np.exp(-tt / (d * (0.35 / r ** .5))) for r, a in parts)
    x += hp(noise(d), 4000) * np.exp(-tt / 0.002) * 0.4
    return fade(norm(x), 0.0003, 0.02) * g

def coin_pair(f=2600):
    a = clink(f, 0.3); b = clink(f * 1.12, 0.35) * .7
    out = np.zeros(int(0.42 * SR)); out[:len(a)] += a; s = int(0.055 * SR); out[s:s + len(b)] += b[:len(out) - s]
    return norm(out)

def cascade(n=20, d=1.2, lo=2200, hi=3600, rising=False):
    out = np.zeros(int((d + 0.4) * SR))
    for i in range(n):
        s = (i / n) * d + R.uniform(-.02, .02); f = (lo + (hi - lo) * i / n) if rising else R.uniform(lo, hi)
        c = clink(f, 0.25) * R.uniform(.4, 1); k = int(max(0, s) * SR); out[k:k + len(c)] += c[:len(out) - k]
    return norm(out)

def boing(f0=180, d=0.5, depth=0.5):
    tt = t_(d)
    fr = f0 * (1 + 1.4 * np.exp(-tt / 0.03)) * (1 + depth * 0.3 * np.sin(2 * np.pi * 14 * tt) * np.exp(-tt / 0.25))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    x = (np.sin(ph) + 0.35 * np.sin(2 * ph)) * np.exp(-tt / (d * 0.35))
    return fade(norm(x), 0.001)

def slide(f0, f1, d=0.5, vib=6):
    tt = t_(d); k = tt / d
    fr = f0 * (f1 / f0) ** (k ** 0.9) * (1 + 0.02 * np.sin(2 * np.pi * vib * tt))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    x = np.sin(ph) + 0.15 * np.sin(2 * ph) + lp(noise(d), 3000) * 0.05
    return fade(norm(x * np.sin(np.pi * np.clip(k * 1.3, 0, 1)) ** 0.5), 0.01, 0.04)

def poof(d=0.55, bright=1.0):
    tt = t_(d)
    x = lp(pink(d), 2500 * bright, 2) * (1 - np.exp(-tt / 0.004)) * np.exp(-tt / 0.12)
    x += np.sin(2 * np.pi * np.cumsum(220 * np.exp(-tt / 0.05) + 90) / SR) * np.exp(-tt / 0.06) * 0.5
    return fade(norm(x), 0.0005, 0.05)

def zap(d=0.4):
    tt = t_(d); fr = 1800 * np.exp(-tt / 0.12) + 300
    m = np.sin(2 * np.pi * 70 * tt) * 3
    x = np.sign(np.sin(2 * np.pi * np.cumsum(fr) / SR + m)) * 0.6 + hp(noise(d), 3000) * 0.4
    return fade(norm(lp(x, 7000) * np.exp(-tt / 0.12)), 0.001)

def sizzle(d=0.8):
    tt = t_(d); x = hp(noise(d), 3500) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * tt))
    cr = np.zeros(len(tt)); idx = R.integers(0, len(tt) - 50, 160)
    for i in idx: cr[i:i + 40] += R.uniform(.3, 1) * np.exp(-np.arange(40) / 6)
    x = x * 0.6 + hp(cr, 2000)
    return fade(norm(x * np.minimum(1, tt / 0.03) * np.exp(-tt / (d * 0.6))), 0.002, 0.08)

def alarm(d=0.55):
    out = np.zeros(int((d + 0.5) * SR)); rate = 24
    for i in range(int(d * rate)):
        b = bell(2400 if i % 2 else 2550, 0.25, 1.73, 1.4) * 0.8; k = int(i / rate * SR); out[k:k + len(b)] += b[:len(out) - k]
        c = tick(1400, 0.02); out[k:k + len(c)] += c * 0.5
    return norm(out)

def gong(f=98, d=4.0):
    tt = t_(d); parts = [(1, 1), (2.01, .5), (2.76, .4), (4.07, .25), (5.4, .15)]
    x = sum(a * np.sin(2 * np.pi * f * r * tt) * np.exp(-tt / (d * 0.32 / r ** .4)) for r, a in parts)
    x *= 1 + 0.15 * np.sin(2 * np.pi * 3.2 * tt)
    x += lp(noise(d), 800) * np.exp(-tt / 0.03) * 0.5
    return fade(norm(x), 0.001, 0.4)

def chirp_bird():
    out = np.zeros(int(0.5 * SR))
    for j in range(R.integers(2, 4)):
        d = 0.07; tt = t_(d); f0 = R.uniform(2800, 3600)
        fr = f0 + 1600 * np.sin(np.pi * tt / d)
        c = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.sin(np.pi * tt / d) ** 2
        k = int(j * 0.1 * SR); out[k:k + len(c)] += c
    return norm(out)

def crickets(d=3.0):
    tt = t_(d); x = np.sin(2 * np.pi * 4700 * tt) * (np.sin(2 * np.pi * 30 * tt) > 0.2) * (0.5 + 0.5 * (np.sin(2 * np.pi * 1.4 * tt) > 0))
    x2 = np.sin(2 * np.pi * 5200 * tt) * (np.sin(2 * np.pi * 27 * tt + 1) > 0.3) * (np.sin(2 * np.pi * 0.9 * tt + 2) > 0)
    return fade(norm(lp(x + 0.7 * x2, 6000)), 0.3, 0.4)

def scribble(d=1.2):
    tt = t_(d); m = (0.5 + 0.5 * np.sin(2 * np.pi * 11 * tt)) * (0.6 + 0.4 * np.sin(2 * np.pi * 3.3 * tt))
    return fade(norm(bp(noise(d), 2500, 7000) * m), 0.02, 0.05)

def squeak(d=0.25, f=1400):
    tt = t_(d); fr = f * (1 + 0.25 * np.sin(2 * np.pi * 18 * tt))
    return fade(norm(np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.sin(np.pi * tt / d)), 0.005, 0.02)

def drop_sfx():  # counter loses coins: snatched coin + sad descending "wah"
    a = sweep(700, 260, 0.45) * 0.8
    out = np.zeros(int(0.7 * SR)); out[:len(a)] += a
    for i in range(6):
        c = tick(2200 - i * 220, 0.03, 0.7); k = int(i * 0.045 * SR); out[k:k + len(c)] += c
    return norm(out)

def tiptoe(n=6, step=0.22):
    out = np.zeros(int((n * step + 0.3) * SR)); notes = [392, 330, 392, 330, 294, 330, 392, 330]
    for i in range(n):
        tt = t_(0.12); f = notes[i % len(notes)]
        c = (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt / 0.03)
        k = int(i * step * SR); out[k:k + len(c)] += c
    return norm(out)

def correct():  # ding-ding
    return chime((1318.5, 1975.5), 0.12, 1.0)

def shwing():
    sp = sparkle(0.5, 10, 4000, 8000); sw = sweep(800, 4000, 0.5) * 0.5
    sp[:len(sw)] += sw
    return norm(sp)

def tada():
    return chime((784, 1046.5, 1318.5, 1568), 0.07, 1.8)

# ---------------- placement ----------------
L = np.zeros(N); Rc = np.zeros(N); WET = np.zeros((2, N))
def place(sig, t, db=0.0, pan=0.0, rev=0.15):
    g = 10 ** (db / 20); a = (pan + 1) * np.pi / 4; s = int(t * SR)
    if s >= N: return
    if s < 0: sig = sig[-s:]; s = 0
    sig = sig[:N - s] * g
    L[s:s + len(sig)] += sig * np.cos(a); Rc[s:s + len(sig)] += sig * np.sin(a)
    WET[0, s:s + len(sig)] += sig * np.cos(a) * rev; WET[1, s:s + len(sig)] += sig * np.sin(a) * rev
px = lambda x: (x - 960) / 960 * 0.75

# scene transitions (iris wipes): soft magic swish
for t0 in [11.05, 17.85, 22.0, 28.55, 37.3, 40.62, 46.25, 53.05, 59.98, 67.85, 73.68, 86.1]:
    place(whoosh(0.6, 500, 6000, 1.0, 0.55), t0 - 0.12, -17, 0, .25)
    place(sparkle(0.5, 7, 4000, 8000), t0 - 0.05, -25, 0, .4)

# SC1 morning
for t0, pn in [(0.25, .4), (0.95, .6), (2.3, .5), (5.2, .7)]: place(chirp_bird(), t0, -24, pn, .3)
place(paper(0.35), 1.45, -20, -0.4, .1); place(whoosh(0.5, 300, 2000), 1.5, -22, -0.4)
place(poof(0.6), 2.95, -12, 0, .2); place(sparkle(1.1, 16), 2.98, -15, 0, .45); place(bell(1568, 1.0, 2, 1), 3.05, -19, 0, .4)
place(boing(260, 0.4), 4.4, -17, 0, .1)
for i in range(28): place(clink(R.uniform(2300, 3600), 0.25), 4.94 + i * 0.05, -22 + R.uniform(-3, 2), px(965 + (i % 2 * 2 - 1) * 200), .2)
place(sweep(400, 1600, 1.4), 4.95, -26, 0.5, .2)
place(chime((1568, 2093)), 6.33, -12, 0.3, .45); place(coin_pair(2900), 6.38, -15, 0.3, .2)
place(whoosh(0.4, 1500, 7000, 1.4, 0.5), 7.95, -19, 0.3, .1); place(clink(3100), 8.5, -16, 0.3, .2)
place(tick(1800, g=1), 8.65, -17, 0.3, .1); place(tick(1300, g=1), 8.95, -17, 0.3, .1)
place(boing(220, 0.5), 9.3, -12, -0.3, .15); place(sparkle(0.7, 10), 9.35, -18, -0.3, .4)

# SC2 the secret / midnight
place(riser(1.0, 200, 3000) * 0.6 + 0, 11.0, -22, 0, .3); place(sparkle(0.9, 12, 2500, 6000), 11.15, -17, 0, .5)
place(poof(0.4), 12.45, -18, 0, .2)
for i in range(5):
    t0 = 12.7 + i * 0.18; s = 1 if i % 2 else -1
    place(clink(R.uniform(2400, 3200), 0.25), t0 + 0.45, -19, s * 0.4, .2); place(boing(320, 0.3), t0 + 0.45, -22, s * 0.4, .1)
place(sweep(420, 150, 0.45), 13.3, -15, 0, .2)
place(pop(330, 0.25), 14.45, -12, 0, .2)
tt = 14.6
while tt < 16.8:
    place(tick(2400 if int(tt * 20) % 2 else 1900, g=1), tt, -19, 0, .15); tt += max(0.05, 0.25 - (tt - 14.6) * 0.09)
place(hp(gong(110, 2.3), 80), 16.85, -10, 0, .45); place(sparkle(1.2, 22, 2500, 7500), 16.95, -15, 0, .55)

# SC3 homework later
place(paper(0.4), 20.7, -17, 0.1, .1)
place(sweep(300, 120, 0.9), 21.3, -18, 0.2, .4); place(whoosh(0.9, 2500, 300, 1.4, 0.4), 21.35, -22, 0.2, .3)

# SC4 suddenly!
place(impact(1.2), 21.94, -10, 0, .3); place(rattle(0.7), 21.95, -18, -0.3, .1)
place(poof(0.6), 23.12, -9, -0.4, .2); place(boing(150, 0.6), 23.18, -12, -0.4, .15)
for i in range(5): place(tick(900, 0.03, 1), 23.8 + i * 0.63, -27, -0.4, .05)  # hops
place(pop(500, 0.2), 26.6, -14, -0.2, .2); place(sparkle(0.5, 8, 3000, 6000), 26.62, -20, -0.2, .4)
place(whoosh(0.35, 600, 5000, 1.4, 0.5), 27.35, -15, 0, .1); place(coin_pair(2800), 27.6, -13, 0.1, .2)
place(whoosh(0.4, 4000, 600, 1.4, 0.4), 27.95, -17, -0.2, .1); place(drop_sfx(), 28.0, -14, 0.6, .2)

# SC5 scrolling
place(pop(600, 0.18), 28.6, -17, 0, .2)
tt = 29.2
while tt < 33.9: place(tick(1500, 0.03, 1), tt, -29, 0.0, .05); place(whoosh(0.15, 1500, 5000, 1.5, 0.3), tt, -34, 0, .02); tt += 0.36
place(poof(0.6), 33.15, -10, 0.4, .2); place(boing(170, 0.5), 33.2, -14, 0.4, .1)
for ts in [34.25, 35.17, 36.18]:
    place(whoosh(0.25, 900, 6000, 1.5, 0.5), ts - 0.08, -19, 0.6, .1); place(coin_pair(R.uniform(2500, 3000)), ts, -14, 0.55, .2); place(drop_sfx(), ts + 0.12, -16, 0.6, .2)
place(cascade(8, 0.45), 36.88, -13, 0.55, .2); place(drop_sfx(), 37.0, -13, 0.6, .2)

# SC6 night
place(crickets(3.3), 37.3, -30, 0, .3)
place(slide(300, 900, 1.0), 38.6, -19, 0, .3); place(pop(800, 0.12), 39.4, -21, 0.1, .2)

# SC7 TikTok alarm
place(alarm(0.55), 40.66, -9, 0.1, .3); place(alarm(0.5), 41.42, -9, 0.1, .3)
place(boing(240, 0.4), 42.18, -13, -0.4, .15); place(whoosh(0.4, 500, 3000), 42.15, -20, -0.4)
place(paper(0.25), 43.2, -15, 0.5, .1); place(thud(120, 0.3), 43.25, -15, 0.5, .2)
place(tick(2600, 0.03), 45.6, -15, -0.3, .1); place(whoosh(0.7, 400, 2500, 1.0, 0.5), 45.6, -22, -0.3, .1)

# SC8 the twist
place(tiptoe(6, 0.25), 46.4, -24, -0.3, .25)
place(thud(80, 0.4), 49.2, -16, 0.5, .3); place(sparkle(0.6, 8), 49.25, -21, 0.5, .4)
place(sweep(500, 1500, 0.7), 49.85, -22, 0.3, .4)
place(riser(0.9, 300, 8000), 50.47 - 0.9, -15, 0, .3)
place(impact(1.6), 50.47, -7, 0, .4); place(poof(0.9, 1.3), 50.47, -10, 0, .3); place(sparkle(1.5, 30, 2500, 8000), 50.5, -13, 0, .6)
place(bell(2093, 1.2, 1.41, 1.5), 52.35, -15, 0.6, .4); place(pop(700, 0.15), 52.35, -18, 0.6, .2)

# SC9 the protection rule
place(correct(), 53.1, -13, -0.6, .4)
place(pop(400, 0.22), 55.7, -14, -0.1, .2); place(sparkle(0.5, 8), 55.72, -21, -0.1, .4)
place(tiptoe(6, 0.23), 56.2, -21, 0.7, .2)
place(shwing(), 57.8, -15, -0.1, .4)
place(zap(0.45), 58.25, -12, -0.05, .2); place(boing(130, 0.6), 58.3, -14, 0.1, .1)
place(pop(460, 0.22), 58.75, -14, 0.45, .2); place(shwing(), 59.2, -16, 0.45, .4)
place(zap(0.45), 59.45, -12, 0.35, .2); place(boing(120, 0.6), 59.5, -14, 0.25, .1)

# SC10 next day
for t0, pn in [(60.0, .5), (60.6, .6)]: place(chirp_bird(), t0, -23, pn, .3)
place(paper(0.35), 60.15, -16, 0.5, .1)
place(cascade(22, 0.8, 2200, 3800, rising=True), 60.1, -15, 0.5, .25); place(tada(), 60.85, -17, 0.6, .45)
place(scribble(1.25), 62.1, -18, 0, .1)
for i in range(4): place(blip(880 * 1.122 ** (i * 2), 880 * 1.122 ** (i * 2 + 1), 0.15), 62.25 + i * 0.28, -20, -0.1 + i * 0.05, .2)
place(riser(0.6, 600, 7000), 63.5, -19, 0.2, .3); place(shwing(), 64.0, -11, 0.2, .45); place(sparkle(1.4, 24), 64.0, -15, 0.2, .55)
place(whoosh(0.4, 600, 4000), 65.1, -19, 0.6, .1)
place(sizzle(0.8), 65.95, -12, 0.4, .2); place(boing(320, 0.4), 66.0, -16, 0.4, .1)
for i in range(4): place(squeak(0.22, 1200 + i * 90), 66.65 + i * 0.25, -22, 0.35, .1)

# SC11 football
for t0, pn in [(67.9, -.5), (68.5, .6), (70.4, -.6), (72.2, .5)]: place(chirp_bird(), t0, -24, pn, .3)
for t0, x in [(68.75, 830), (69.9, 1420), (70.95, 300)]:
    place(thud(85, 0.35), t0, -12, px(x), .2); place(whoosh(0.5, 500, 3000), t0 + 0.02, -20, px(x))
for i in range(5): place(bell(1568 * 1.122 ** (i * 2), 0.6, 1.41, 1.2), 68.9 + i * 0.35, -24, -0.1 + i * 0.05, .45)
for i in range(6): place(pop(900 + i * 80, 0.1, 1.4, .2), 70.0 + i * 0.15, -25, -0.2, .2)
place(slide(900, 500, 0.4), 71.92, -14, 0.3, .2); place(slide(700, 300, 0.45), 72.91, -13, 0.3, .2)
place(poof(0.3, 1.6), 73.35, -16, 0.3, .2); place(pop(1400, 0.08), 73.38, -18, 0.3, .2)

# SC12 sunset
place(chime((1046.5, 1318.5, 1568), 0.08, 1.8), 74.95, -16, 0, .55); place(sparkle(1.2, 18), 75.0, -19, 0, .5)
place(boing(300, 0.35), 75.75, -20, 0, .1)
place(tick(1800, g=1), 76.6, -17, -0.5, .1); place(tick(1300, g=1), 76.85, -17, -0.5, .1)
place(pop(380, 0.25), 77.9, -12, 0, .2); place(bell(1568, 0.9, 2, 1), 77.95, -18, 0, .4)
place(whoosh(0.4, 1500, 7000, 1.4, 0.5), 78.72, -19, 0); place(coin_pair(3000), 79.0, -14, 0, .25); place(sparkle(0.6, 10), 79.0, -21, 0, .4)
place(pop(520, 0.18), 81.05, -15, 0.15, .2); place(pop(620, 0.18), 81.8, -15, 0.35, .2)
place(tiptoe(5, 0.22), 82.75, -23, 0.2, .2)
place(poof(0.6), 85.62, -11, 0.2, .25); place(slide(500, 1500, 0.6), 85.65, -16, 0.4, .25); place(pop(1100, 0.1), 86.1, -20, 0.6, .2)

# SC13 finale
place(sweep(400, 1200, 0.8), 86.5, -21, 0, .5); place(sparkle(0.8, 12, 2500, 6000), 86.55, -19, 0, .5)
place(pop(300, 0.3), 87.7, -12, 0, .2); place(squeak(0.35, 900), 87.9, -19, 0.1, .2)
place(whoosh(0.5, 5000, 400, 1.2, 0.2)[::-1].copy(), 88.5, -16, 0, .3)
place(thud(100, 0.45), 89.3, -9, 0, .3); place(tick(1200, 0.04), 89.3, -12, 0, .2)
place(impact(1.3), 89.32, -13, 0, .4); place(tada(), 89.35, -12, 0, .55); place(sparkle(1.8, 34, 2500, 8000), 89.36, -14, 0, .6)
place(cascade(28, 2.4, 2000, 3800), 89.4, -22, 0, .4)
for i, x in enumerate([1430, 480, 960]): place(boing(240 + i * 40, 0.4), 89.75 + i * 0.05, -19, px(x), .15)
place(chime((1568, 2093, 2637)), 90.0, -16, 0, .55)

# ---------------- mix ----------------
IRs = make_ir(1.3)
sfx = np.stack([L, Rc])
for c in range(2): sfx[c] += fftconvolve(WET[c], IRs[c])[:N] * 1.5
sfx = hp(sfx, 40)
sr, vo = wavfile.read(sys.argv[1]); vo = vo.astype(np.float64) / 32768.0
if vo.ndim > 1: vo = vo.mean(1)
vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]
envv = np.sqrt(lp(vo ** 2, 12, 1).clip(0)); envv = envv / (np.percentile(envv, 95) + 1e-9)
sfx *= lp(1 - 0.45 * np.clip(envv, 0, 1), 6, 1)
mix = np.stack([vo, vo]) * 0.70 + sfx * 0.58
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
pk = np.max(np.abs(mix)); mix *= min(1, 0.97 / pk)
wavfile.write(sys.argv[2], SR, (mix.T * 32767).astype(np.int16))
wavfile.write(sys.argv[2].replace('.wav', '_sfx_only.wav'), SR, (norm(sfx.T, 0.9) * 32767).astype(np.int16))
print('ok')
