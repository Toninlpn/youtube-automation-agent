#!/usr/bin/env python3
"""Synthèse pure Python (sans numpy) des nappes sonores du Short
« La caméra a filmé quelqu'un qui n'était pas là ».

Chaque couche est écrite en WAV mono 48 kHz sur toute la durée du film
(29,0 s) avec ses propres enveloppes temporelles :

  amb.wav       vent + trafic lointain + hum électrique 50 Hz (0 → 26,5 s)
  rumble.wav    grondement infra-grave qui monte (1,5 → 26,5 s)
  heart.wav     battement de cœur lub-dub, BPM et niveau progressifs (5 → 26,5 s)
  breath.wav    respiration très faint (9 → 14,2 s et 19,2 → 21,6 s)
  glitch.wav    bursts numériques aux cuts (0,90 / 11,60 / 24,60 / 25,40 / 26,00 s)
  buzz.wav      grésillement de néon pendant le flicker (18,30 → 18,55 s)

Le mix final (voix + couches + loudness) est fait par build.py via ffmpeg.
"""
import math
import random
import wave

SR = 48000
DUR = 29.0
N = int(SR * DUR)
random.seed(20260927)


def clamp(v, a, b):
    return a if v < a else (b if v > b else v)


def ramp(t, t0, t1):
    """0 avant t0, 1 après t1, linéaire entre les deux."""
    if t1 <= t0:
        return 1.0 if t >= t0 else 0.0
    return clamp((t - t0) / (t1 - t0), 0.0, 1.0)


def write_wav(path, buf):
    peak = max(1e-9, max(abs(s) for s in buf))
    scale = min(1.0, 0.98 / peak)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = bytearray()
        for s in buf:
            v = int(clamp(s * scale, -1.0, 1.0) * 32767)
            frames += v.to_bytes(2, "little", signed=True)
        w.writeframes(bytes(frames))
    print(f"  wrote {path}  peak={peak:.3f}")


def white():
    return random.uniform(-1.0, 1.0)


# ---------------------------------------------------------------- ambience
def build_amb():
    buf = [0.0] * N
    w_lp = 0.0     # vent : bruit passe-bas léger
    b_lp = 0.0     # trafic : bruit brun passe-bas lourd
    for i in range(N):
        t = i / SR
        w_lp += 0.045 * (white() - w_lp)
        b_lp += 0.010 * (white() - b_lp)
        wind_mod = 0.55 + 0.45 * math.sin(2 * math.pi * 0.07 * t + 2.0 * math.sin(2 * math.pi * 0.023 * t))
        traffic_mod = 0.7 + 0.3 * math.sin(2 * math.pi * 0.011 * t + 1.7)
        wind = w_lp * 0.55 * wind_mod
        traffic = b_lp * 2.2 * traffic_mod
        hum = 0.010 * math.sin(2 * math.pi * 50 * t) + 0.005 * math.sin(2 * math.pi * 100 * t + 0.6)
        env = 1.0 - ramp(t, 26.30, 26.50)          # coupure nette au cut to black
        buf[i] = (wind + traffic + hum) * 0.16 * env
    return buf


# ---------------------------------------------------------------- rumble
def build_rumble():
    buf = [0.0] * N
    lp = 0.0
    for i in range(N):
        t = i / SR
        lp += 0.03 * (white() - lp)
        amp = 0.10 * ramp(t, 1.5, 6.0) + 0.12 * ramp(t, 20.0, 25.5)
        if t >= 26.5:
            amp = 0.0
        sig = math.sin(2 * math.pi * 34 * t) + 0.5 * math.sin(2 * math.pi * 41 * t + 1.1) + 0.35 * lp
        buf[i] = sig * amp * 0.5
    return buf


# ---------------------------------------------------------------- heartbeat
def build_heart():
    buf = [0.0] * N
    t = 5.0
    while t < 26.4:
        bpm = 58 + 16 * clamp((t - 5) / 16, 0, 1)
        level = 0.05 + 0.42 * clamp((t - 5) / 15, 0, 1) ** 1.6
        for off, freq, gain, dec in ((0.0, 52.0, 1.0, 0.085), (0.30, 44.0, 0.55, 0.075)):
            t0 = t + off
            i0 = int(t0 * SR)
            length = int(0.38 * SR)
            for k in range(length):
                j = i0 + k
                if j >= N or j < 0:
                    continue
                tau = k / SR
                buf[j] += gain * level * math.sin(2 * math.pi * freq * tau) * math.exp(-tau / dec)
        t += 60.0 / bpm
    return buf


# ---------------------------------------------------------------- breathing
def build_breath():
    buf = [0.0] * N
    lp = 0.0
    windows = ((9.0, 14.2), (19.2, 21.6))
    for i in range(N):
        t = i / SR
        lp += 0.22 * (white() - lp)
        env = 0.0
        for w0, w1 in windows:
            if w0 <= t < w1:
                phase = (t - w0) % 3.8            # inspire 1,6 s / expire 2,2 s
                env = math.sin(math.pi * phase / 3.8) ** 2
        buf[i] = lp * 0.055 * env
    return buf


# ---------------------------------------------------------------- glitches
def build_glitch():
    buf = [0.0] * N
    for g0 in (0.90, 11.60, 24.60, 25.40, 26.00):
        dur = 0.11
        i0 = int(g0 * SR)
        hold = 0.0
        for k in range(int(dur * SR)):
            j = i0 + k
            if j >= N:
                break
            tau = k / SR
            if k % 6 == 0:
                hold = white() * 0.55
            env = math.exp(-tau / 0.045)
            click = 0.5 * white() if tau < 0.004 else 0.0
            buf[j] += (hold * 0.7 + click) * env
        # contre-temps plus grave
        i1 = int((g0 + 0.06) * SR)
        hold = 0.0
        for k in range(int(0.05 * SR)):
            j = i1 + k
            if j >= N:
                break
            if k % 10 == 0:
                hold = white() * 0.35
            buf[j] += hold * math.exp(-(k / SR) / 0.03)
    return buf


# ---------------------------------------------------------------- neon buzz
def build_buzz():
    buf = [0.0] * N
    i0, i1 = int(18.30 * SR), int(18.55 * SR)
    for j in range(i0, min(i1, N)):
        t = j / SR
        tau = t - 18.30
        edge = ramp(tau, 0.0, 0.006) * (1 - ramp(tau, 0.22, 0.25))
        sq = 0.6 if math.sin(2 * math.pi * 100 * t) >= 0 else -0.6
        am = 0.6 + 0.4 * math.sin(2 * math.pi * 9 * t)
        buf[j] = sq * am * edge * 0.10
    return buf


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio", "layers")
    os.makedirs(out, exist_ok=True)
    for name, fn in (("amb", build_amb), ("rumble", build_rumble), ("heart", build_heart),
                     ("breath", build_breath), ("glitch", build_glitch), ("buzz", build_buzz)):
        print(f"synth {name}…")
        write_wav(os.path.join(out, f"{name}.wav"), fn())
    print("done.")
