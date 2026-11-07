"""Sound design for the Surat Al-Asr explainer.
No music, no bells/chimes, no melodic tones: only natural, textural sounds
(air, sand, clock ticks, paper, soft thumps, a metal shutter, a stamp, a phone buzz).
Complete silence is enforced during every on-screen verse.
usage: python3 asr_sfx.py vo_ext.wav mix.wav
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve
from sfxlib import SR, t_, noise, pink, bp, lp, hp, norm, fade, svf, paper, tick, thud, sand, make_ir

DUR = 167.0; N = int(SR * DUR); R = np.random.default_rng(11)
SILENT = [(22.1, 29.1), (49.7, 55.7), (91.1, 101.1), (156.7, 167.0)]

# ---------------- textural sounds ----------------
def air(d=0.7, f0=500, f1=3500, peak=0.55, q=0.8):
    n = int(d * SR); k = np.arange(n) / n
    cut = f0 * (f1 / f0) ** np.sin(np.pi * np.clip(k / peak, 0, 1) * 0.5)
    x = svf(pink(d), cut, q, 'bp')
    e = np.where(k < peak, (k / peak) ** 2, np.exp(-(k - peak) / (1 - peak) * 4))
    return fade(norm(x * e), 0.01, 0.05)

def swell(d=1.6, bright=1.0):  # soft breath of air with a felt low body (non-tonal)
    tt = t_(d); k = tt / d
    e = np.sin(np.pi * k) ** 1.6
    x = lp(pink(d), 1800 * bright, 2) * 0.8 + hp(lp(noise(d), 9000), 3500) * 0.15 * bright
    sub = lp(noise(d), 90, 2) * 3
    return fade(norm((x + sub) * e), 0.02, 0.1)

def tap(d=0.25, body=110):  # soft felt thump
    tt = t_(d)
    x = np.sin(2 * np.pi * np.cumsum(body + 60 * np.exp(-tt / 0.02)) / SR) * np.exp(-tt / 0.05)
    x += lp(noise(d), 1500) * np.exp(-tt / 0.008) * 0.6
    return fade(norm(x), 0.001, 0.05)

def glint(d=0.4):  # airy sparkle made of filtered noise only
    tt = t_(d); x = hp(noise(d), 6000) * np.exp(-tt / 0.08) * (1 + 0.5 * np.sin(2 * np.pi * 23 * tt))
    return fade(norm(x), 0.002, 0.05)

def shimmer(d=1.2):  # non-tonal "light" texture
    tt = t_(d); k = tt / d
    x = bp(noise(d), 4000, 11000) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 7 * tt)))
    return fade(norm(x * np.sin(np.pi * k) ** 1.2), 0.02, 0.1)

def wood(d=0.12):  # scale knock
    tt = t_(d); x = bp(noise(d), 300, 1600) * np.exp(-tt / 0.012) + np.sin(2 * np.pi * 220 * tt) * np.exp(-tt / 0.02) * 0.4
    return norm(x)

def creak(d=0.9):
    tt = t_(d); out = np.zeros(len(tt)); rate = 40 + 25 * np.sin(np.pi * tt / d)
    ph = np.cumsum(rate) / SR; idx = np.where(np.diff(np.floor(ph)) > 0)[0]
    for i in idx: g = bp(noise(0.006), 500, 2500) * np.hanning(int(0.006 * SR)); out[i:i + len(g)] += g[:len(out) - i]
    return fade(norm(out * np.sin(np.pi * tt / d)), 0.02, 0.1)

def shutter(d=1.3):
    out = np.zeros(int((d + 0.4) * SR))
    for i in range(int(d * 26)):
        s = int((i / 26) * SR + R.integers(0, 200)); g = bp(noise(0.03), 1200, 6000) * np.exp(-np.arange(int(0.03 * SR)) / (0.006 * SR)) * R.uniform(.5, 1)
        out[s:s + len(g)] += g[:len(out) - s]
    tt = np.arange(len(out)) / SR
    rumble = lp(noise(len(out) / SR), 200) * np.clip(1 - tt / d, 0, 1) * 1.5
    out += rumble
    end = thud(80, 0.4) * 1.2; s = int(d * SR); out[s:s + len(end)] += end[:len(out) - s]
    return norm(out)

def stampx():
    x = thud(95, 0.4); k = bp(noise(0.06), 600, 3000) * np.exp(-t_(0.06) / 0.01)
    x[:len(k)] += k * 0.8
    return norm(x)

def buzz(d=0.6):  # phone vibration
    tt = t_(d); on = ((tt % 0.3) < 0.2).astype(float)
    x = np.sign(np.sin(2 * np.pi * 160 * tt)) * on
    return fade(norm(lp(x, 900) * on), 0.005, 0.03)

def coin_drop():
    x = thud(160, 0.25) * 0.8; k = bp(noise(0.05), 2000, 6000) * np.exp(-t_(0.05) / 0.006)
    x[:len(k)] += k * 0.5
    return norm(x)

# ---------------- placement ----------------
L = np.zeros(N); Rr = np.zeros(N); WET = np.zeros((2, N))
def place(sig, t, db=0.0, pan=0.0, rev=0.2):
    g = 10 ** (db / 20); a = (pan + 1) * np.pi / 4; s = int(t * SR)
    if s >= N: return
    sig = sig[:N - s] * g
    L[s:s + len(sig)] += sig * np.cos(a); Rr[s:s + len(sig)] += sig * np.sin(a)
    WET[0, s:s + len(sig)] += sig * np.cos(a) * rev; WET[1, s:s + len(sig)] += sig * np.sin(a) * rev
px = lambda x: (x - 960) / 960 * 0.6

# hook: data package -> sand -> hourglass
place(swell(2.0, 0.8), 0.0, -24, 0, .3)
place(paper(0.25), 2.45, -22, 0, .15)
place(tap(), 3.6, -22, px(1360), .2); place(tap(), 6.0, -23, px(560), .2)
for i in range(4): place(air(0.25, 1500, 5000, 0.4, 1.5), 6.0 + i * 0.3, -32, 0, .05)
place(air(1.2, 300, 4000, 0.5), 7.2, -18, 0, .3); place(sand(1.2), 7.3, -24, 0, .3)
place(tap(0.3, 80), 7.95, -17, 0, .3)
place(sand(6.0) * 0.5, 8.0, -30, 0, .2)
for k in range(5): place(tick(2200 if k % 2 else 1700, 0.03), 9.5 + k, -24, -0.6, .15)
place(tap(0.35, 70), 12.35, -19, px(1290), .25)

# the surah & al-Shafi'i
place(swell(1.8), 14.2, -21, 0, .35)
for i, x in enumerate([1180, 960, 740]): place(tap(0.25, 120), 15.05 + i * 0.22, -21, px(x), .25)
place(air(0.6, 600, 3000), 18.3, -24, 0, .2); place(paper(0.3), 18.45, -27, 0, .1)

# time (al-Tabari, al-Sa'di)
place(swell(2.2, 0.6), 29.3, -22, 0, .35)
place(lp(pink(6.5), 600) * 0.4, 29.6, -36, 0, .2)  # faint wind over the city
for t0 in [32.3, 37.3]: place(air(0.6, 600, 3000), t0, -24, 0, .2); place(paper(0.3), t0 + 0.1, -28, 0, .1)
for i, x in enumerate([400, 700, 1000, 1300, 1560]): place(tap(0.2, 140), 44.3 + i * 0.4, -24, px(x), .2)
place(tap(0.3, 80), 47.1, -19, 0, .3); place(sand(2.2) * 0.6, 47.2, -28, 0, .2)

# loss, degrees, the shop
place(tap(0.3, 90), 55.9, -21, 0, .3); place(creak(0.9), 56.4, -22, 0.1, .2); place(wood(), 57.5, -20, 0.3, .2)
place(air(0.6, 600, 3000), 58.4, -24, 0, .2)
for i in range(3): place(tap(0.25, 130 - i * 25), 59.4 + i * 0.35, -21, 0.1 + i * 0.1, .25)
place(air(0.7, 300, 2500), 62.9, -21, 0, .2)
tt = 63.2
while tt < 67.3: place(tick(2000, 0.025), tt, -29, 0.25, .1); tt += 0.11
place(shutter(1.3), 67.3, -15, 0, .25)
place(paper(0.35), 68.0, -20, -0.2, .1); place(stampx(), 69.1, -15, -0.2, .25)
place(paper(0.3), 70.1, -21, 0.6, .1)

# hadith (kept very calm), the cheap trade, the way out
place(swell(2.0, 0.6), 72.2, -24, 0, .35)
place(glint(), 77.75, -27, px(1080), .4); place(glint(), 78.45, -27, px(840), .4)
place(air(1.4, 300, 2000, 0.6), 82.0, -23, 0.5, .2)
place(coin_drop(), 83.3, -21, -0.4, .2); place(coin_drop(), 83.45, -23, -0.4, .2)
place(tap(0.3, 75), 84.6, -20, -0.4, .25)
place(swell(1.6, 1.0), 86.4, -20, 0, .45); place(shimmer(1.4), 86.6, -28, 0, .5)
for i, x in enumerate([1410, 1110, 810, 510]): place(tap(0.22, 120), 89.25 + i * 0.18, -21, px(x), .25)

# the formula
for i, x in enumerate([1500, 1140, 780, 420]): place(tap(0.2, 140), 101.25 + i * 0.12, -26, px(x), .25)
for t0, x in [(101.6, 1500), (109.86, 1140), (119.76, 780), (127.1, 420)]:
    place(swell(1.3, 0.9), t0 - 0.2, -20, px(x), .4); place(shimmer(1.0), t0, -28, px(x), .45)
for t0 in [104.0, 111.6, 120.6, 129.3]: place(air(0.5, 700, 3000), t0 - 0.1, -26, 0, .2)
for t0 in [107.1, 107.3]: place(tap(0.2, 150), t0, -24, 0, .2)
for i, t0 in enumerate([113.9, 115.2, 116.7]): place(tap(0.2, 150), t0, -24, px([1280, 960, 640][i]), .2)
place(buzz(0.6), 122.9, -21, 0.2, .15); place(air(0.3, 1500, 6000, 0.4, 1.5), 125.0, -26, -0.2, .1)
place(air(1.0, 200, 1500, 0.6), 136.4, -22, px(1130), .3); place(shimmer(1.0), 136.5, -27, px(1130), .4)
place(air(1.2, 300, 2500, 0.5), 138.1, -22, 0, .3); place(air(0.6, 600, 3000), 138.0, -27, 0, .2)
for i in range(3): place(swell(1.4, 0.5), 142.6 + i * 0.9, -28, 0, .4)
place(air(1.0, 300, 2500, 0.5), 145.3, -22, 0, .3)
for t0 in [146.0, 146.25, 146.5, 147.3]: place(tap(0.2, 150), t0, -24, 0, .2)
place(tap(0.4, 70), 147.65, -17, -0.6, .35); place(shimmer(1.2), 147.7, -24, -0.6, .5)

# the final words: a big, gentle swell of light
place(air(0.7, 600, 3000), 152.5, -23, 0, .2)
place(swell(3.0, 1.0), 153.1, -14, 0, .5); place(shimmer(2.5), 153.4, -22, 0, .6)

# ---------------- mix ----------------
IRs = make_ir(1.6)
sfx = np.stack([L, Rr])
for c in range(2): sfx[c] += fftconvolve(WET[c], IRs[c])[:N] * 1.4
sfx = hp(sfx, 35)
# enforce total silence during the verses (incl. reverb tails), with gentle 0.4s fades
mask = np.ones(N); tt = np.arange(N) / SR
for a, b in SILENT:
    m = np.clip(np.minimum((a - tt) / 0.4, (tt - b) / 0.4), 0, 1)
    mask = np.minimum(mask, np.where((tt > a - 0.4) & (tt < b + 0.4), m, 1))
sfx *= mask
sr, vo = wavfile.read(sys.argv[1]); vo = vo.astype(np.float64) / 32768.0
vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]
envv = np.sqrt(lp(vo ** 2, 12, 1).clip(0)); envv = envv / (np.percentile(envv, 95) + 1e-9)
sfx *= lp(1 - 0.4 * np.clip(envv, 0, 1), 6, 1)
mix = np.stack([vo, vo]) * 0.72 + sfx * 0.5
mix = np.tanh(mix * 1.05) / np.tanh(1.05)
mix *= min(1, 0.97 / np.max(np.abs(mix)))
wavfile.write(sys.argv[2], SR, (mix.T * 32767).astype(np.int16))
wavfile.write(sys.argv[2].replace('.wav', '_sfx_only.wav'), SR, (norm(sfx.T, 0.9) * 32767).astype(np.int16))
# report: verify silence in verse windows
for a, b in SILENT:
    seg = sfx[:, int(a * SR):int(b * SR)]; print(f'verse window {a}-{b}: sfx peak = {np.max(np.abs(seg)):.2e}')
print('ok')
