"""Timeline du Short « Le mystère du Mary Celeste » (9:16, ~50 s)."""

import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGES = os.path.join(HERE, "images")
AUDIO = os.path.join(HERE, "audio")
WORK = os.path.join(HERE, "work")

FFMPEG = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"

FPS = 30
W, H = 1080, 1920

# Vitesse de la voix off : pitch -4,8 % (voix plus grave) + acceleration nette x1,03
PITCH_RATE = 1.05
ATEMPO = PITCH_RATE / 1.03

VOICEOVER = [
    ("vo1", "Imaginez d\u00e9couvrir un bateau en pleine mer\u2026 mais sans aucun membre d'\u00e9quipage."),
    ("vo2", "En 1872, un navire est retrouv\u00e9 d\u00e9rivant dans l'Atlantique. Mais quelque chose ne va pas."),
    ("vo3", "Le bateau est encore en \u00e9tat de naviguer. La cargaison est toujours l\u00e0. De la nourriture et de l'eau sont toujours pr\u00e9sentes."),
    ("vo4", "Mais les dix personnes qui se trouvaient \u00e0 bord ont disparu. Et leur canot de sauvetage manque \u00e9galement."),
    ("vo5", "Personne ne sait exactement pourquoi ils ont quitt\u00e9 le navire. Temp\u00eate ? Erreur de jugement ? Peur d'une catastrophe ?"),
    ("vo6", "Plus de 150 ans plus tard, le myst\u00e8re reste l'un des plus c\u00e9l\u00e8bres de l'histoire maritime."),
]

VO_STARTS = [0.50, 7.60, 15.90, 24.60, 32.00, 41.00]

CAPTIONS = [
    ("vo1", "Imaginez d\u00e9couvrir un bateau en pleine mer\u2026", ["bateau"]),
    ("vo1", "Mais sans aucun membre d'\u00e9quipage.", ["sans aucun membre d'\u00e9quipage"]),
    ("vo2", "En 1872, un navire est retrouv\u00e9 d\u00e9rivant dans l'Atlantique.", ["1872"]),
    ("vo2", "Mais quelque chose ne va pas.", ["ne va pas"]),
    ("vo3", "Le bateau est encore en \u00e9tat de naviguer.", ["encore en \u00e9tat de naviguer"]),
    ("vo3", "La cargaison est toujours l\u00e0.", ["toujours l\u00e0"]),
    ("vo3", "Nourriture et eau sont toujours pr\u00e9sentes.", ["toujours pr\u00e9sentes"]),
    ("vo4", "Mais les dix personnes \u00e0 bord ont disparu.", ["disparu"]),
    ("vo4", "Leur canot de sauvetage manque \u00e9galement.", ["manque"]),
    ("vo5", "Personne ne sait exactement pourquoi ils ont quitt\u00e9 le navire.", ["Personne ne sait", "quitt\u00e9 le navire"]),
    ("vo5", "Temp\u00eate ? Erreur de jugement ? Peur d'une catastrophe ?", ["Peur d'une catastrophe"]),
    ("vo6", "Plus de 150 ans plus tard,", ["150 ans"]),
    ("vo6", "le myst\u00e8re reste l'un des plus c\u00e9l\u00e8bres de l'histoire maritime.", ["myst\u00e8re"]),
]

HOOK_TEXT = {
    "start": 0.00, "end": 3.10, "y": 520,
    "lines": [
        ("UN BATEAU A \u00c9T\u00c9 RETROUV\u00c9\u2026", 84, "white"),
        ("SANS PERSONNE \u00c0 BORD.", 98, "gold"),
    ],
}
FINAL_TEXT = {
    "start": 47.32, "end": 50.60, "y": 780,
    "lines": [
        ("TOI, TU AURAIS", 92, "white"),
        ("QUITT\u00c9 LE NAVIRE ?", 100, "gold"),
    ],
}

# (image, debut, fin, zoom debut, zoom fin, pan x, pan y, duree de transition)
SHOTS = [
    ("scene1-ocean",       0.00,  2.80, 1.00, 1.35,  0.00,  0.00, 0.22),
    ("scene8-waves-hull",  2.80,  4.80, 1.12, 1.30,  0.00,  0.00, 0.35),
    ("scene2-lifeboats",   4.80,  7.60, 1.04, 1.20,  0.08,  0.00, 0.35),
    ("scene3-deck",        7.60,  9.90, 1.20, 1.18, -0.12,  0.00, 0.35),
    ("scene3b-belongings", 9.90, 12.10, 1.05, 1.22,  0.00,  0.04, 0.35),
    ("scene4-cargo",      12.10, 14.40, 1.02, 1.18,  0.06,  0.00, 0.22),
    ("scene4b-barrels",   14.40, 15.90, 1.16, 1.32,  0.00,  0.00, 0.35),
    ("scene4-cargo",      15.90, 18.20, 1.26, 1.10, -0.10,  0.00, 0.35),
    ("scene4b-barrels",   18.20, 20.60, 1.10, 1.28,  0.10,  0.00, 0.35),
    ("scene3-deck",       20.60, 22.90, 1.30, 1.18,  0.06, -0.05, 0.35),
    ("scene5-cabin",      22.90, 25.30, 1.05, 1.20,  0.00,  0.00, 0.35),
    ("scene5b-chart",     25.30, 27.50, 1.10, 1.26, -0.08,  0.00, 0.35),
    ("scene6-davits",     27.50, 29.90, 1.15, 1.05,  0.12,  0.00, 0.22),
    ("scene5-cabin",      29.90, 32.20, 1.26, 1.08,  0.00,  0.00, 0.35),
    ("scene8-waves-hull", 32.20, 34.60, 1.05, 1.22,  0.06,  0.00, 0.35),
    ("scene8-waves-hull", 34.60, 36.80, 1.20, 1.08, -0.08,  0.00, 0.35),
    ("scene1-ocean",      36.80, 39.00, 1.30, 1.12,  0.00,  0.00, 0.35),
    ("scene8-waves-hull", 39.00, 41.00, 1.24, 1.08, -0.10,  0.00, 0.60),
    ("scene9-sunset",     41.00, 50.60, 1.32, 1.00,  0.00,  0.00, 0.00),
]

VIDEO_END = 50.60
FADE_IN = 0.35
FADE_OUT_START = 49.85

SOUND = {
    "bass_impacts": [0.45, 47.30],
    "thunder": [32.20, 34.70, 36.95],
    "creaks": [8.10, 19.60, 27.70, 29.95],
    "riser": (39.60, 47.20),
    "storm_boost": (32.00, 41.20),
    "final_tone": 47.35,
    "fade_out": (49.80, 50.90),
}


def image_path(name):
    """Chemin de l'image source (.jpg apres optimisation, .png en secours)."""
    for ext in (".jpg", ".png"):
        p = os.path.join(IMAGES, name + ext)
        if os.path.exists(p):
            return p
    return os.path.join(IMAGES, name + ".png")


def probe_duration(path):
    out = subprocess.run([FFMPEG, "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", out)
    h, mn, s = m.groups()
    return int(h) * 3600 + int(mn) * 60 + float(s)


def vo_windows():
    wins = {}
    for (name, _), start in zip(VOICEOVER, VO_STARTS):
        raw = probe_duration(os.path.join(AUDIO, name + ".mp3"))
        dur = raw * 1.03
        wins[name] = (round(start, 3), round(start + dur, 3))
    return wins


def caption_windows(wins):
    per_vo = {}
    for key, text, _ in CAPTIONS:
        per_vo.setdefault(key, []).append(text)
    out = []
    for key, _ in VOICEOVER:
        start, end = wins[key]
        texts = per_vo.get(key, [])
        if not texts:
            continue
        total_chars = sum(len(t) for t in texts)
        t = start
        for i, text in enumerate(texts):
            d = (end - start) * len(text) / total_chars
            if i == len(texts) - 1:
                d = end - t
            out.append((round(t, 3), round(t + d, 3), text))
            t += d
    return out
