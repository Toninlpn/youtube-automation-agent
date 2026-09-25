"""Musique originale du Short : partition cinematique en La mineur, 75 BPM.

Structure calée sur le montage :
  0-6 s    accroche   : sub + motif piano (A4 C5 E5 D5 C5 A4)
  6-24 s   decouverte : nappe accords + pulsation cardiaque
  24-32 s  disparition: couche de tension (9e)
  32-41 s  tempete    : intensite maximale, pulse rapide
  41-47 s  finale     : motif repris puis resolution
  47-50 s  accord final qui s'eteint
"""

import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline as T
from build_bed import fft_lp, tv_bp

SR = 48000
DUR = 51.2
N = int(SR * DUR)
T_AX = np.arange(N) / SR
BPM = 75.0
BEAT = 60.0 / BPM          # 0,8 s
BAR = 4 * BEAT             # 3,2 s

# accords : (instant de debut, fondamentale, notes de la nappe)
CHORDS = [
    (0.0,  110.00, [220.00, 261.63, 329.63]),   # Am
    (3.2,   87.31, [174.61, 220.00, 261.63]),   # F
    (6.4,  130.81, [261.63, 329.63, 392.00]),   # C
    (9.6,   98.00, [196.00, 246.94, 293.66]),   # G
    (12.8, 110.00, [220.00, 261.63, 329.63]),   # Am
    (16.0,  87.31, [174.61, 220.00, 261.63]),   # F
    (19.2, 130.81, [261.63, 329.63, 392.00]),   # C
    (22.4,  98.00, [196.00, 246.94, 293.66]),   # G
    (25.6, 110.00, [220.00, 261.63, 329.63]),   # Am
    (28.8,  87.31, [174.61, 220.00, 261.63]),   # F
    (32.0, 130.81, [261.63, 329.63, 392.00]),   # C
    (35.2,  98.00, [196.00, 246.94, 293.66]),   # G
    (38.4, 110.00, [220.00, 261.63, 329.63]),   # Am
    (41.6,  87.31, [174.61, 220.00, 261.63]),   # F
    (44.8, 110.00, [220.00, 261.63, 329.63]),   # Am
    (48.0, 110.00, [220.00, 261.63, 329.63]),   # Am (resolution)
]

# notes du motif (instant, frequence, duree, niveau)
MOTIF = [
    (0.45, 440.00, 0.9, 0.85), (1.25, 523.25, 0.9, 0.80), (2.05, 659.26, 1.2, 0.75),
    (3.25, 587.33, 0.9, 0.80), (4.05, 523.25, 0.9, 0.78), (4.85, 440.00, 1.6, 0.82),
    (12.95, 523.25, 0.8, 0.62), (13.75, 587.33, 0.8, 0.60), (14.55, 659.26, 1.1, 0.58),
    (15.75, 523.25, 1.4, 0.62),
    (41.70, 440.00, 0.9, 0.72), (42.50, 523.25, 0.9, 0.70), (43.30, 659.26, 1.6, 0.68),
    (44.90, 587.33, 1.0, 0.62), (45.70, 523.25, 1.8, 0.64),
]


def env_ad(n, attack, decay, sustain=0.0):
    a = int(attack * SR)
    e = np.zeros(n)
    if a > 0:
        e[:a] = np.linspace(0, 1, a) ** 0.5
    rest = n - a
    if rest > 0:
        e[a:] = np.exp(-np.arange(rest) / (decay * SR))
    return e


def add_tone(buf, f, t0, dur, amp, harmonics=(1.0, 0.32, 0.14, 0.06), attack=0.02,
             decay=0.9, pan=0.0, vibrato=0.0):
    n = int(dur * SR)
    if n <= 0:
        return
    tt = np.arange(n) / SR
    sig = np.zeros(n)
    for h, a in enumerate(harmonics, start=1):
        if a == 0:
            continue
        det = 1.0 + (0.0016 * (h % 2) - 0.0008)
        sig += a * np.sin(2 * np.pi * f * h * det * tt + h)
    if vibrato:
        sig *= 1 + vibrato * np.sin(2 * np.pi * 5.0 * tt)
    sig *= env_ad(n, attack, decay)
    i0 = int(t0 * SR)
    i1 = min(i0 + n, N)
    if i1 <= i0:
        return
    s = sig[:i1 - i0] * amp
    gl = np.sqrt(0.5 * (1 - pan))
    gr = np.sqrt(0.5 * (1 + pan))
    buf[i0:i1, 0] += s * gl
    buf[i0:i1, 1] += s * gr


def add_pulse(buf, t0, amp, f=54.0):
    """Pulsation cardiaque grave."""
    n = int(0.45 * SR)
    tt = np.arange(n) / SR
    sig = np.sin(2 * np.pi * (f * np.exp(-tt / 0.09) + 42) * tt) * np.exp(-tt / 0.16)
    i0 = int(t0 * SR)
    buf[i0:i0 + n, :] += np.stack([sig, sig], axis=1) * amp


def add_tick(buf, t0, amp):
    """Clic d'arpège (tempo rapide de la tempete)."""
    n = int(0.12 * SR)
    tt = np.arange(n) / SR
    sig = (np.sin(2 * np.pi * 1400 * tt) + np.sin(2 * np.pi * 2100 * tt) * 0.5)
    sig *= np.exp(-tt / 0.035)
    sig = tv_bp(sig, 900, 4000)
    i0 = int(t0 * SR)
    buf[i0:i0 + n, 0] += sig * amp * 0.7
    buf[i0:i0 + n, 1] += sig * amp * 0.9


def main():
    buf = np.zeros((N, 2))

    # ---- 1. nappe d'accords (pad) ----
    for i, (t0, root, notes) in enumerate(CHORDS):
        t1 = CHORDS[i + 1][0] if i + 1 < len(CHORDS) else DUR
        dur = t1 - t0
        # intensite par section
        if t0 < 6.4:
            lvl = 0.30
        elif t0 < 24.0:
            lvl = 0.46
        elif t0 < 32.0:
            lvl = 0.60
        elif t0 < 41.6:
            lvl = 0.72
        else:
            lvl = 0.40
        # fondamentale (sub)
        add_tone(buf, root / 2.0, t0, dur + 0.4, lvl * 0.55,
                 harmonics=(1.0, 0.10, 0.03), attack=0.35, decay=3.0, pan=0.0)
        # nappe : 3 notes reparties dans l'image stereo
        for j, f in enumerate(notes):
            pan = [-0.72, 0.0, 0.72][j % 3]
            add_tone(buf, f, t0, dur + 0.4, lvl * 0.44,
                     harmonics=(1.0, 0.30, 0.16, 0.08, 0.04),
                     attack=0.55, decay=2.6, pan=pan, vibrato=0.05)

    # ---- 2. couche de tension (9e) : 24 s -> 41 s ----
    n = int(17.0 * SR)
    tt = np.arange(n) / SR
    tension = (np.sin(2 * np.pi * 493.88 * tt) * 0.5
               + np.sin(2 * np.pi * 497.2 * tt) * 0.3)
    tension *= 1 + 0.10 * np.sin(2 * np.pi * 4.5 * tt)
    tension = fft_lp(tension, 2200)
    rampe = np.clip((T_AX - 24.0) / 3.0, 0, 1) * np.clip((41.6 - T_AX) / 3.0, 0, 1)
    i0 = int(24.0 * SR)
    buf[i0:i0 + n, 0] += tension * rampe[i0:i0 + n] * 0.30
    buf[i0:i0 + n, 1] += np.roll(tension, 90)[:n] * rampe[i0:i0 + n] * 0.30

    # ---- 3. pulsation ----
    t = 6.4
    while t < 47.5:
        if t < 24.0:
            amp = 0.34
        elif t < 32.0:
            amp = 0.55
        elif t < 41.6:
            amp = 0.85
        else:
            amp = 0.38
        add_pulse(buf, t, amp)
        add_pulse(buf, t + 2 * BEAT, amp * 0.75)
        t += BAR

    # ---- 4. arpege rapide pendant la tempete (32-41 s) ----
    storm_notes = [261.63, 329.63, 392.00, 523.25, 392.00, 329.63]
    k = 0
    t = 32.0
    while t < 41.0:
        f = storm_notes[k % len(storm_notes)]
        add_tick(buf, t, 0.16)
        if k % 2 == 0:
            add_tone(buf, f, t, 0.5, 0.10, harmonics=(1.0, 0.2), attack=0.005,
                     decay=0.22, pan=0.3 if k % 4 == 0 else -0.3)
        k += 1
        t += BEAT / 2.0

    # ---- 5. motif melodique ----
    for t0, f, dur, lvl in MOTIF:
        add_tone(buf, f, t0, dur, lvl, harmonics=(1.0, 0.28, 0.10, 0.04),
                 attack=0.006, decay=0.75, pan=0.12, vibrato=0.012)

    # ---- 6. accord final (47,3 s, synchronise avec l'impact basse) ----
    for j, f in enumerate([110.0, 220.0, 261.63, 329.63]):
        add_tone(buf, f, 47.30, 3.0, [0.5, 0.30, 0.26, 0.22][j],
                 harmonics=(1.0, 0.25, 0.10), attack=0.03, decay=1.6,
                 pan=[0.0, -0.5, 0.0, 0.5][j])

    # ---- 7. branlement global + fondu ----
    f0, f1 = T.SOUND["fade_out"]
    ramp = np.clip((f1 - T_AX) / (f1 - f0), 0, 1) ** 1.4
    buf *= ramp[:, None]
    buf *= 0.62 / (np.abs(buf).max() + 1e-9)

    out = os.path.join(T.AUDIO, "music.wav")
    pcm = (np.clip(buf, -1, 1) * 32767).astype("<i2")
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("music -> %s (%.1f s, pic %.2f)" % (out, DUR, np.abs(buf).max()))


if __name__ == "__main__":
    main()
