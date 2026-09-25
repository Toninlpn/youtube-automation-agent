"""Design sonore du Short : nappe de suspense, impacts basse, tonnerre, houle, grincements."""

import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline as T

SR = 48000
DUR = 51.2
N = int(SR * DUR)
T_AX = np.arange(N) / SR


def brown(n, seed):
    rng = np.random.default_rng(seed)
    w = rng.standard_normal(n)
    out = np.cumsum(w) / np.sqrt(np.arange(1, n + 1))
    return out / (np.abs(out).max() + 1e-9)


def white(n, seed):
    return np.random.default_rng(seed).standard_normal(n)


def fft_lp(x, fc):
    a = float(np.exp(-2 * np.pi * fc / SR))
    n = len(x)
    X = np.fft.rfft(x, 2 * n)
    w = 2 * np.pi * np.fft.rfftfreq(2 * n)
    H = (1 - a) / (1 - a * np.exp(-1j * w))
    return np.fft.irfft(X * H, 2 * n)[:n]


def tv_bp(x, lo, hi):
    def tv_lp(sig, fc):
        fc = np.asarray(fc, dtype=float)
        if fc.ndim == 0:
            fc = np.full(len(sig), float(fc))
        a = np.exp(-2 * np.pi * fc / SR)
        y = np.empty_like(sig)
        acc = float(sig[0])
        for i in range(len(sig)):
            acc = a[i] * acc + (1 - a[i]) * sig[i]
            y[i] = acc
        return y

    lp = tv_lp(x, hi)
    return lp - tv_lp(lp, lo)


def smooth_env(times, values, tau=0.25):
    env = np.interp(T_AX, times, values, left=values[0], right=values[-1])
    a = np.exp(-1.0 / (SR * tau))
    out = np.empty_like(env)
    acc = env[0]
    for i, v in enumerate(env):
        acc = a * acc + (1 - a) * v
        out[i] = acc
    return out


def add_bass_impact(buf, t0, gain=1.0):
    n = int(2.6 * SR)
    tt = np.arange(n) / SR
    f = 140 * np.exp(-tt / 0.16) + 36
    phase = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(phase) * np.exp(-tt / 0.42)
    click = fft_lp(white(n, 7), 1200) * np.exp(-tt / 0.020) * 0.9
    sig = (body * 0.9 + click * 0.35) * gain
    i0 = int(t0 * SR)
    buf[i0:i0 + n, :] += np.stack([sig, sig * 0.98], axis=1)


def add_thunder(buf, t0, gain=1.0):
    n = int(2.4 * SR)
    tt = np.arange(n) / SR
    k = np.ones(40) / 40
    low = np.convolve(white(n, 21), k, mode="same") * 6.0
    env = np.exp(-tt / 0.9) * (1 - np.exp(-tt / 0.02))
    sig = low * env * 0.8 * gain
    sig += np.sin(2 * np.pi * 46 * tt) * np.exp(-tt / 0.7) * 0.35 * gain
    i0 = int(t0 * SR)
    buf[i0:i0 + n, :] += np.stack([sig * 0.9, sig], axis=1)


def add_creak(buf, t0, gain=1.0):
    n = int(0.5 * SR)
    tt = np.arange(n) / SR
    f = 380 + 520 * (tt / 0.5) ** 1.6
    phase = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(phase) * (0.6 + 0.4 * np.sin(2 * np.pi * 11 * tt))
    noise = white(n, 33) * 0.25
    env = np.exp(-tt / 0.16) * (1 - np.exp(-tt / 0.01))
    sig = (tone + noise) * env * gain
    i0 = int(t0 * SR)
    buf[i0:i0 + n, :] += np.stack([sig, sig * 0.92], axis=1)


def main():
    S = T.SOUND
    buf = np.zeros((N, 2))

    drone = np.zeros(N)
    for f0, g, det in ((55.0, 0.30, 0.0), (82.41, 0.20, 0.3),
                       (110.0, 0.16, -0.25), (164.81, 0.07, 0.2)):
        drone += g * np.sin(2 * np.pi * f0 * T_AX + det)
        drone += g * 0.5 * np.sin(2 * np.pi * (f0 * 1.005) * T_AX)
    drone *= 1 + 0.12 * np.sin(2 * np.pi * 0.35 * T_AX)
    build = smooth_env([0, 6, 24, 32, 41, 47.3, 49.8, 51.2],
                       [0.55, 0.62, 0.72, 0.80, 1.0, 1.15, 0.7, 0.0], tau=1.2)
    buf[:, 0] += drone * build
    buf[:, 1] += np.concatenate([np.zeros(int(0.008 * SR)), drone])[:N] * build

    wind = fft_lp(brown(N, 5), 420)
    wind_env = smooth_env([0, 8, 20, 32, 41, 47, 51.2],
                          [0.35, 0.42, 0.5, 0.95, 0.8, 0.45, 0.3], tau=2.0)
    buf[:, 0] += wind * wind_env * 0.75
    buf[:, 1] += np.roll(wind, 137) * wind_env * 0.75

    swell = tv_bp(white(N, 11), 200, 850)
    swell_env = (0.55 + 0.45 * np.sin(2 * np.pi * 0.07 * T_AX)
                 + 0.25 * np.sin(2 * np.pi * 0.11 * T_AX + 1.3)
                 + 0.15 * np.sin(2 * np.pi * 0.19 * T_AX + 2.1))
    swell_env = np.clip(swell_env, 0.05, None)
    storm = smooth_env([S["storm_boost"][0] - 2, S["storm_boost"][0],
                        S["storm_boost"][1], S["storm_boost"][1] + 2],
                       [1.0, 2.6, 2.6, 1.0], tau=1.5)
    buf[:, 0] += swell * swell_env * storm * 0.42
    buf[:, 1] += np.roll(swell, 311) * swell_env * storm * 0.42

    r0, r1 = S["riser"]
    n = int((r1 - r0) * SR)
    tt = np.arange(n) / SR
    noise = tv_bp(white(n, 41), 300 + 3200 * (tt / (r1 - r0)), 4200)
    riser = noise * (tt / (r1 - r0)) ** 2 * 0.5
    sweep = np.sin(2 * np.pi * np.cumsum(90 + 210 * tt / (r1 - r0)) / SR) * (tt / (r1 - r0)) ** 2 * 0.25
    sig = riser + sweep
    i0 = int(r0 * SR)
    buf[i0:i0 + n, 0] += sig
    buf[i0:i0 + n, 1] += sig

    for t in S["bass_impacts"]:
        add_bass_impact(buf, t, 1.0 if t < 10 else 1.15)
    for t in S["thunder"]:
        add_thunder(buf, t, 0.9)
    for t in S["creaks"]:
        add_creak(buf, t, 0.5)

    t0 = S["final_tone"]
    n = int(3.0 * SR)
    tt = np.arange(n) / SR
    tone = (np.sin(2 * np.pi * 220.0 * tt) * 0.5
            + np.sin(2 * np.pi * 261.63 * tt) * 0.32
            + np.sin(2 * np.pi * 329.63 * tt) * 0.22) * np.exp(-tt / 1.1)
    i0 = int(t0 * SR)
    buf[i0:i0 + n, 0] += tone * 0.5
    buf[i0:i0 + n, 1] += tone * 0.5

    f0, f1 = S["fade_out"]
    ramp = np.clip((f1 - T_AX) / (f1 - f0), 0, 1) ** 1.5
    buf *= ramp[:, None]

    # fondu d'entree (evite tout demarrage brutal) + suppression du continu / sub-harmonique
    fin = np.clip(T_AX / 0.30, 0, 1) ** 1.5
    buf *= fin[:, None]
    buf = fft_lp(buf[:, 0], 16000)[:, None] * 0 + buf
    # highpass simple par retrait de la moyenne glissante tres basse
    k = np.ones(int(0.05 * SR)) / int(0.05 * SR)
    slow = np.stack([np.convolve(buf[:, c], k, mode="same") for c in range(2)], axis=1)
    buf = buf - 0.85 * slow

    buf *= 0.72 / (np.abs(buf).max() + 1e-9)

    out = os.path.join(T.AUDIO, "bed.wav")
    pcm = (np.clip(buf, -1, 1) * 32767).astype("<i2")
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("bed -> %s (%.1f s, peak %.2f)" % (out, DUR, np.abs(buf).max()))


if __name__ == "__main__":
    main()
