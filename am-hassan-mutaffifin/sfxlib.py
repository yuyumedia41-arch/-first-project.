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

