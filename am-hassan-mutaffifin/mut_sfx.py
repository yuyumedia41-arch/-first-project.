"""Film foley for the "Am Hassan" short (Surat Al-Mutaffifin 1-3).
No music, no bells/chimes, no melodic tones. Total silence is enforced in the two
verse slots (left empty for the Qari's recitation).
usage: python3 mut_sfx.py vo_ext.wav mix.wav
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve
from sfxlib import SR, t_, noise, pink, bp, lp, hp, norm, fade, svf, paper, tick, thud, impact, make_ir

DUR = 207.5; N = int(SR * DUR); R = np.random.default_rng(21)
a = lambda t: t + 2.0 if t < 66.25 else t + 32.0
b = lambda t: t + 111.4
SILENT = [(68.25, 98.25), (170.7, 207.5)]

# ---------------- sounds ----------------
def air(d=0.6, f0=500, f1=3500, peak=0.55, q=0.8):
    n = int(d * SR); k = np.arange(n) / n
    cut = f0 * (f1 / f0) ** np.sin(np.pi * np.clip(k / peak, 0, 1) * 0.5)
    e = np.where(k < peak, (k / peak) ** 2, np.exp(-(k - peak) / (1 - peak) * 4))
    return fade(norm(svf(pink(d), cut, q, 'bp') * e), 0.01, 0.05)
def swell(d=1.6, bright=1.0):
    tt = t_(d); e = np.sin(np.pi * tt / d) ** 1.6
    x = lp(pink(d), 1800 * bright, 2) * 0.8 + hp(lp(noise(d), 9000), 3500) * 0.15 * bright + lp(noise(d), 90, 2) * 3
    return fade(norm(x * e), 0.02, 0.1)
def tap(d=0.22, body=120):
    tt = t_(d); x = np.sin(2 * np.pi * np.cumsum(body + 60 * np.exp(-tt / 0.02)) / SR) * np.exp(-tt / 0.045) + lp(noise(d), 1500) * np.exp(-tt / 0.008) * 0.6
    return fade(norm(x), 0.001, 0.05)
def shimmer(d=1.2):
    tt = t_(d); x = bp(noise(d), 4000, 11000) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 7 * tt)))
    return fade(norm(x * np.sin(np.pi * tt / d) ** 1.2), 0.02, 0.1)
def glint(d=0.4):
    tt = t_(d); return fade(norm(hp(noise(d), 6000) * np.exp(-tt / 0.08) * (1 + 0.5 * np.sin(2 * np.pi * 23 * tt))), 0.002, 0.05)
def wood(d=0.14, f=220):
    tt = t_(d); return norm(bp(noise(d), 300, 1800) * np.exp(-tt / 0.012) + np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.02) * 0.5)
def clank(d=0.3):  # scale pan / metal (inharmonic, very short: foley, not a bell)
    tt = t_(d); x = sum(np.sin(2 * np.pi * f * tt + R.uniform(0, 6)) * np.exp(-tt / dc) for f, dc in [(1730, .03), (2890, .022), (4310, .015), (640, .04)])
    x += hp(noise(d), 3000) * np.exp(-tt / 0.004) * 1.2
    return fade(norm(x), 0.0005, 0.03)
def step(d=0.16):
    tt = t_(d); return fade(norm(lp(noise(d), 900) * np.exp(-tt / 0.02) + bp(noise(d), 1500, 4000) * np.exp(-tt / 0.01) * 0.3), 0.001, 0.03)
def steps(n, gap, jit=0.02):
    out = np.zeros(int((n * gap + 0.3) * SR))
    for i in range(n):
        s = int((i * gap + R.uniform(-jit, jit) + jit) * SR); g = step() * R.uniform(.7, 1); out[s:s + len(g)] += g
    return out
def flies(d=1.6):
    tt = t_(d); f = 190 + 30 * np.sin(2 * np.pi * 1.7 * tt) + 22 * np.sin(2 * np.pi * 4.3 * tt + 1) + lp(noise(d), 6) * 60
    ph = 2 * np.pi * np.cumsum(f) / SR; x = (2 * ((ph / (2 * np.pi)) % 1) - 1)
    am = 0.55 + 0.45 * np.sin(2 * np.pi * 0.9 * tt) * np.sin(2 * np.pi * 2.3 * tt)
    return fade(norm(bp(x, 300, 3500) * am), 0.15, 0.25)
def needle(d=0.9, n=14):
    out = np.zeros(int(d * SR)); t0 = 0
    for i in range(n):
        g = tick(1500 + R.uniform(-200, 200), 0.02) * (0.9 ** i); s = int(t0 * SR)
        if s + len(g) < len(out): out[s:s + len(g)] += g
        t0 += 0.03 + i * 0.006
    return norm(out)
def hiss(d=1.6):
    tt = t_(d); return fade(norm(hp(noise(d), 4500) * (0.7 + 0.3 * np.sin(2 * np.pi * 11 * tt))), 0.03, 0.2)
def tape_stop(d=0.7):
    tt = t_(d); k = tt / d; f = 900 * (1 - k) ** 2 + 40
    x = svf(pink(d), f, 2.5, 'bp') * (1 - k) ** 0.5 + np.sin(2 * np.pi * np.cumsum(f * 0.25) / SR) * 0.5 * (1 - k)
    return fade(norm(x), 0.002, 0.05)
def coin():
    x = thud(170, 0.2) * 0.6; tt = t_(0.09); k = (np.sin(2 * np.pi * 3900 * tt) + np.sin(2 * np.pi * 5750 * tt)) * np.exp(-tt / 0.012) + hp(noise(0.09), 4000) * np.exp(-tt / 0.004)
    x[:len(k)] += k * 0.5; return norm(x)
def crunch(d=0.22):
    tt = t_(d); out = bp(noise(d), 900, 5000) * np.exp(-tt / 0.03) * (np.abs(np.sin(2 * np.pi * 38 * tt)) > 0.4)
    return fade(norm(out), 0.001, 0.03)
def drip():
    d = 0.12; tt = t_(d); return fade(norm(bp(noise(d), 1800, 4200) * np.exp(-tt / 0.012) + lp(noise(d), 500) * np.exp(-tt / 0.03) * 0.5), 0.001, 0.02)
def rain(d=4.0):
    x = hp(noise(d), 2500) * 0.35; n = len(x)
    for i in R.integers(0, n - 300, int(d * 60)): x[i:i + 200] += R.uniform(.3, 1) * np.exp(-np.arange(200) / 30) * R.choice([-1, 1])
    return fade(norm(lp(x, 9000)), 0.6, 0.8)
def bird():
    out = np.zeros(int(0.5 * SR))
    for j in range(R.integers(2, 4)):
        d = 0.07; tt = t_(d); f0 = R.uniform(2800, 3600); c = np.sin(2 * np.pi * np.cumsum(f0 + 1600 * np.sin(np.pi * tt / d)) / SR) * np.sin(np.pi * tt / d) ** 2
        k = int(j * 0.1 * SR); out[k:k + len(c)] += c
    return norm(out)
def walla(d, seed=1):  # market crowd bed: slow-modulated band noise
    rr = np.random.default_rng(seed); n = int(d * SR); tt = np.arange(n) / SR; out = np.zeros(n)
    for lo, hi in [(250, 700), (500, 1400), (900, 2400)]:
        am = np.zeros(n)
        for _ in range(5): am += np.sin(2 * np.pi * rr.uniform(0.15, 1.3) * tt + rr.uniform(0, 6))
        am = np.clip(0.5 + am / 6, 0.05, 1)
        out += bp(rr.standard_normal(n), lo, hi) * am
    return norm(lp(out, 3000))

# ---------------- placement ----------------
L = np.zeros(N); Rr = np.zeros(N); WET = np.zeros((2, N))
def place(sig, t, db=0.0, pan=0.0, rev=0.15):
    g = 10 ** (db / 20); an = (pan + 1) * np.pi / 4; s = int(t * SR)
    if s >= N or s < 0: return
    sig = sig[:N - s] * g
    L[s:s + len(sig)] += sig * np.cos(an); Rr[s:s + len(sig)] += sig * np.sin(an)
    WET[0, s:s + len(sig)] += sig * np.cos(an) * rev; WET[1, s:s + len(sig)] += sig * np.sin(an) * rev
cut = lambda t, db=-17: place(air(0.4, 700, 5000, 0.5, 1.0), t - 0.2, db, 0, .1)
FZ = a(54.9)

# ---- ambience beds
bed1 = walla(FZ + 0.1, 1); bed1 *= np.clip(np.arange(len(bed1)) / (1.5 * SR), 0, 1); bed1[-int(0.12 * SR):] *= np.linspace(1, 0, int(0.12 * SR))
place(bed1, 0.0, -31, 0, .25)
for t0 in np.arange(1.0, FZ - 1, 2.3):  # sparse far-off market details
    k = R.integers(0, 3); place([wood(0.12, R.uniform(160, 300)), step(), clank(0.2)][k], t0 + R.uniform(0, 1.5), -36 + R.uniform(-3, 2), R.uniform(-.8, .8), .5)
bed2 = walla(b(47.75) - b(38.4) + 0.2, 5); place(fade(bed2, 0.8, 0.8), b(38.4), -37, 0, .3)   # dusk, quieter
bed3 = walla(170.7 - b(44.95), 9); place(fade(bed3, 0.8, 1.5), b(44.95), -33, 0, .25)       # morning
for t0 in [b(45.1), b(45.9), b(48.3), b(50.3), b(52.4), b(54.6), b(56.4), b(57.6)]: place(bird(), t0 + R.uniform(0, .3), -30, R.uniform(-.7, .7), .35)

# ---- act 1: the souk
place(swell(2.4, 0.8), 0.1, -22, 0, .3)
place(air(0.9, 300, 2500), 4.0, -20, 0.1, .15); place(tap(), a(2.3), -22, -0.5, .2)
place(tap(0.15, 200), a(7.0), -25, 0.1, .1)
for t0 in [a(8.4), a(9.0), a(9.8)]: place(air(0.3, 800, 4000, 0.4, 1.2), t0, -24, 0.2, .1)
cut(a(12.35)); place(tap(), a(13.0), -21, 0.5, .15); place(tap(), a(15.0), -21, -0.5, .15)
place(air(0.6, 500, 3500), a(14.25), -19, -0.3, .15); place(tick(3000, 0.02), a(14.4), -22, -0.3, .1)
place(flies(1.7), a(15.4), -22, 0.1, .1)
cut(a(17.0)); place(steps(4, 0.24), a(17.0), -20, -0.5, .15)
place(air(0.7, 300, 2500), a(20.2), -22, 0.2, .1)
for t0 in [a(21.7), a(21.95)]: place(clank(0.25), t0, -17, 0.4, .15)
place(glint(), a(22.5), -20, 0.4, .4); place(shimmer(0.9), a(22.55), -27, 0.4, .4)
cut(a(23.4)); place(thud(110, 0.3), a(23.5), -15, -0.2, .15); place(clank(), a(23.52), -17, -0.2, .15); place(needle(1.0), a(23.55), -22, -0.2, .1)
place(tap(), a(23.8), -22, -0.6, .15); place(thud(70, 0.5), a(24.6), -16, 0, .3); place(tap(), a(24.7), -21, -0.6, .15)
for i in range(2): place(tap(0.2, 150), a(25.0) + i * 0.25, -22, 0.5, .15); place(crunch(), a(26.7) + i * 0.12, -17, 0.5, .1)
cut(a(27.45)); place(paper(0.5) * 0.7, a(27.7), -27, 0, .1); place(paper(0.5) * 0.7, a(29.0), -27, 0, .1)
for i in range(6): place(coin(), a(28.7) + i * 0.22 + 0.45, -22, -0.3 + i * 0.12, .2)

# ---- act 2: the wholesaler
place(air(0.8, 300, 4000, 0.5), a(31.1) - 0.3, -15, 0, .2); place(thud(80, 0.4), a(31.2), -19, 0.2, .3)
place(steps(6, 0.27), a(31.3), -20, -0.6, .15); place(needle(1.2, 12), a(31.6), -24, 0.1, .1)
place(tap(), a(34.8), -22, -0.5, .2); place(air(0.7, 300, 2500), a(34.5), -22, 0.2, .1)
for t0 in [a(36.45), a(36.7)]: place(wood(0.14, 180), t0, -17, 0.1, .2)
cut(a(38.3)); place(thud(75, 0.5), a(38.4), -13, -0.3, .2); place(wood(0.16, 150), a(38.42), -15, -0.3, .2)
tt = a(39.4)
for i in range(16): place(tick(1300 + i * 40, 0.02), tt, -23, 0.5, .1); tt += 0.06 + i * 0.006
place(impact(1.2), a(40.67), -12, 0.3, .3); place(tap(), a(40.7), -20, 0.5, .15)
place(air(0.6, 500, 3500), a(42.15), -19, -0.3, .15); place(flies(1.8), a(43.6), -21, -0.2, .1)
# fury
cut(a(45.5), -14); place(impact(1.0), a(45.77), -8, 0, .3); place(impact(1.0), a(46.44), -8, 0, .3); place(hiss(1.7), a(45.6), -21, 0, .15)
cut(a(47.3), -15); place(hiss(2.2) * 0.8, a(47.35), -25, -0.4, .15); place(thud(90, 0.3), a(47.4), -16, -0.4, .2); place(thud(90, 0.3), a(48.5), -17, -0.4, .2)
place(air(0.5, 400, 2500), a(50.85), -24, 0.4, .1)
# the freeze
place(tape_stop(0.7), FZ - 0.15, -9, 0, .2); place(thud(55, 0.9), FZ + 0.02, -9, 0, .4); place(tick(2600, 0.03), FZ + 0.05, -14, 0, .2); place(tap(), FZ + 0.12, -19, 0, .2)
for t0, pn in [(a(55.6), -0.5), (a(58.7), 0.5)]: place(air(0.7, 300, 3000, 0.6), t0 - 0.1, -17, pn, .2); place(thud(85, 0.4), t0 + 0.55, -17, pn, .3)
place(tap(), a(56.4), -22, -0.5, .2); place(tap(), a(59.6), -22, 0.5, .2)
place(thud(70, 0.4), a(59.05), -16, 0, .35); place(thud(70, 0.4), a(59.33), -16, 0, .35)
place(swell(2.4, 1.0), a(62.0), -17, 0, .5); place(shimmer(1.8), a(62.4), -26, 0, .5)

# ---- tafsir (calm)
for t0 in [a(67.2), a(71.7), b(0.1), b(6.1)]: place(air(0.6, 600, 3000), t0, -24, 0, .2); place(paper(0.3), t0 + 0.1, -29, 0, .1)
place(tap(), a(75.7), -22, -0.6, .2); place(tap(), a(77.6), -22, 0.6, .2)
place(thud(75, 0.4), b(8.0), -19, 0, .3)
# hadith: light, water, rain
place(swell(2.2, 0.7), b(11.1), -23, 0, .4)
for t0 in [b(18.5), b(21.2), b(27.9)]: place(air(0.5, 700, 3000), t0, -27, 0, .2)
for i in range(3): place(drip(), b(16.3) + i * 0.33, -20, -0.1 + i * 0.1, .35)
place(rain(4.4), b(21.2), -25, 0, .3)
place(air(1.2, 300, 2200, 0.6), b(28.4), -24, 0, .3)
place(swell(2.6, 1.0), b(30.9), -18, 0, .5); place(shimmer(2.0), b(31.2), -26, 0, .55)
# fatwa
place(air(0.6, 600, 3000), b(33.3), -24, 0, .2); place(thud(65, 0.6), b(37.1), -15, 0, .4)

# ---- the ending
place(air(0.9, 300, 3000, 0.5), b(38.3), -19, 0, .2); place(steps(6, 0.44, 0.03), b(38.5), -21, 0.3, .2)
place(swell(2.0, 0.9), b(44.8), -20, 0, .4)
place(air(0.5, 500, 3000), b(46.2), -22, 0.3, .1); place(tick(2200, 0.03), b(46.72), -18, -0.1, .1)
place(clank(0.3), b(46.82), -13, -0.1, .2); place(needle(0.9), b(46.86), -20, -0.2, .1); place(tap(), b(47.0), -21, -0.6, .15)
cut(b(47.75), -19); place(wood(0.16, 140), b(48.1), -17, 0.5, .2); place(thud(80, 0.4), b(48.4), -17, 0.5, .2)
place(steps(4, 0.22), b(48.95), -21, -0.5, .15); place(needle(1.0), b(49.4), -22, 0.3, .1); place(tap(), b(50.55), -22, 0.3, .15)
place(air(0.5, 500, 3000), b(53.2), -23, 0.1, .1); place(paper(0.25), b(54.05), -20, -0.2, .1); place(thud(120, 0.25), b(54.05), -19, -0.2, .15)
for i in range(3): place(glint(0.3), b(54.1) + i * 0.15, -27, -0.2, .4)
place(swell(3.2, 1.0), b(55.4), -17, 0, .5); place(shimmer(2.4), b(55.9), -27, 0, .5)

# ---------------- mix ----------------
IRs = make_ir(1.5)
sfx = np.stack([L, Rr])
for c in range(2): sfx[c] += fftconvolve(WET[c], IRs[c])[:N] * 1.4
sfx = hp(sfx, 38)
mask = np.ones(N); tt = np.arange(N) / SR
for s0, e0 in SILENT:
    m = np.clip(np.minimum((s0 - tt) / 0.4, (tt - e0) / 0.4), 0, 1)
    mask = np.minimum(mask, np.where((tt > s0 - 0.4) & (tt < e0 + 0.4), m, 1))
sfx *= mask
sr, vo = wavfile.read(sys.argv[1]); vo = vo.astype(np.float64) / 32768.0
vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]
envv = np.sqrt(lp(vo ** 2, 12, 1).clip(0)); envv = envv / (np.percentile(envv[envv > 1e-4], 95) + 1e-9)
sfx *= lp(1 - 0.42 * np.clip(envv, 0, 1), 6, 1)
mix = np.stack([vo, vo]) * 0.72 + sfx * 0.55
mix = np.tanh(mix * 1.05) / np.tanh(1.05); mix *= min(1, 0.97 / np.max(np.abs(mix)))
wavfile.write(sys.argv[2], SR, (mix.T * 32767).astype(np.int16))
wavfile.write(sys.argv[2].replace('.wav', '_sfx_only.wav'), SR, (norm(sfx.T, 0.9) * 32767).astype(np.int16))
for s0, e0 in SILENT: print(f'silent slot {s0}-{e0}: mix peak = {np.max(np.abs(mix[:, int(s0 * SR):int(e0 * SR)])):.1e}')
s = mix.mean(0) - vo * 0.72; db = lambda x: 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
print('voice rms', round(db(vo[vo != 0] * 0.72), 1), 'sfx rms (film part)', round(db(s[:int(66 * SR)]), 1))
