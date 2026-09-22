#!/usr/bin/env python3
"""
LE REFLET — YouTube Short 9:16 (1080x1920 @30fps, 39,97 s)
Moteur d'assemblage 100 % local : mouvements de camera reels (zoompan / pan /
shake) sur les plans AI, narration francaise calee sur la duree reelle de
chaque prise, sous-titres ASS brules + .srt, sound design synthetise
(battements, drone 37 Hz, bourdonnement 100 Hz, tic-tac, booms, riser,
chuchotements, impact, gouttes). Aucune musique sous droits.

python3 render.py [subs|audio|video|all]     (video = segments + etalonnage + mux)
FORCE=1 python3 render.py video               -> re-render de tous les plans
"""
import json, os, re, shutil, subprocess, sys

ROOT   = os.path.dirname(os.path.abspath(__file__))
IMG    = os.path.join(ROOT, "img")
AUD    = os.path.join(ROOT, "audio")
TMP    = os.path.join(ROOT, "tmp")
OUT    = os.path.join(ROOT, "out")
W, H, FPS, SR = 1080, 1920, 30, 44100
SW, SH = 1620, 2880            # sur-echantillonnage -> zoom sans perte de nettete
TOTAL  = 40.0
IMPACT_T = 34.55
SLUG   = "le-reflet"

def find_ffmpeg():
    for cand in (os.environ.get("FFMPEG_PATH"), shutil.which("ffmpeg")):
        if cand and os.path.exists(cand):
            return cand
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        raise SystemExit("ffmpeg introuvable: pip3 install imageio-ffmpeg ou FFMPEG_PATH=...")

FFMPEG = find_ffmpeg()
for _d in (TMP, OUT, os.path.join(TMP, "seg")):
    os.makedirs(_d, exist_ok=True)

# ------------------------------------------------------------------ outils
def run(args, desc):
    p = subprocess.run([FFMPEG, "-hide_banner", "-y", "-loglevel", "error"] + args,
                       capture_output=True, text=True)
    if p.returncode != 0:
        print("FAILED:", desc, "\n", p.stderr[-2500:]); sys.exit(1)
    return p

def dur_of(path):
    p = subprocess.run([FFMPEG, "-hide_banner", "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", p.stderr)
    if not m:
        raise SystemExit("duree illisible: " + path)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))

def lav_out(name, graph, t=TOTAL):
    run(["-f", "lavfi", "-i", graph, "-t", str(t), "-ar", str(SR), "-ac", "2",
         "-c:a", "pcm_s16le", os.path.join(TMP, name)], name)

def vol(expr):
    return f"volume=volume={expr}:eval=frame"

def win(a, b):
    """1 si a<=t<=b (virgules echappees pour le parseur de filtres)."""
    return f"between(t\\,{a}\\,{b})"

def gate_expr(windows, inside, outside):
    s = "+".join(win(a, b) for a, b in windows)
    return f"if(gt({s}\\,0)\\,{inside}\\,{outside})"

# ------------------------------------------------------------- storyboard
# (cle, image, debut, fin, mouvement camera)
SHOTS = [
    ("a_eye",           "a_eye.png",          0.00,  2.20, dict(zoom=[1.03, 1.26], pan=[(0.50, 0.47), (0.46, 0.41)])),
    ("b_wide",          "b_wide_handup.png",  2.20,  5.10, dict(zoom=[1.22, 1.00], pan=[(0.5, 0.40), (0.5, 0.52)])),
    ("c_stare",         "c_mirror_stare.png", 5.10,  7.30, dict(zoom=[1.02, 1.15], pan=[(0.5, 0.5), (0.5, 0.44)])),
    ("d_raise",         "d_raise_slow.png",   7.30,  9.00, dict(zoom=[1.05, 1.14], pan=[(0.38, 0.52), (0.62, 0.47)])),
    ("e1_delay",        "v2_e1_frozen.png",   9.00,  9.75, dict(zoom=[1.09, 1.13], pan=[(0.5, 0.42), (0.5, 0.40)])),
    ("e2_late",         "e_late_hand.png",    9.75, 11.20, dict(zoom=[1.22, 1.02], pan=[(0.5, 0.30), (0.5, 0.44)])),
    ("f_stepback",      "f_stepback.png",    11.20, 12.60, dict(zoom=[1.15, 1.00], pan=[(0.5, 0.44), (0.5, 0.58)])),
    ("g_fear",          "g_fear.png",        12.60, 14.60, dict(zoom=[1.04, 1.16], shake=5, freq=7.5)),
    ("h_smile",         "h_smile.png",       14.60, 16.80, dict(zoom=[1.00, 1.26], pan=[(0.5, 0.5), (0.5, 0.42)])),
    ("i_turn",          "i_turn_door.png",   16.80, 18.60, dict(zoom=[1.12, 1.02], pan=[(0.12, 0.5), (0.62, 0.5)])),
    ("j_doorway",       "v2_j_doorway.png",  18.60, 20.40, dict(zoom=[1.00, 1.14], pan=[(0.5, 0.5), (0.5, 0.44)])),
    ("k_closer",        "v2_k_closer.png",   20.40, 22.20, dict(zoom=[1.02, 1.22], pan=[(0.5, 0.44), (0.5, 0.36)])),
    ("l_pressed",       "v2_l_pressed.png",  22.20, 24.20, dict(zoom=[1.04, 1.22], shake=3, freq=5.0)),
    ("m_points",        "v2_m_points.png",   24.20, 26.20, dict(zoom=[1.04, 1.18], pan=[(0.44, 0.46), (0.56, 0.40)])),
    ("n_frozen",        "v2_n_frozen.png",   26.20, 28.20, dict(zoom=[1.16, 1.02], pan=[(0.5, 0.5), (0.56, 0.44)])),
    ("o_smile_at_him",  "v2_o_smile.png",    28.20, 30.20, dict(zoom=[1.02, 1.30], pan=[(0.5, 0.46), (0.5, 0.36)])),
    ("p_no_reflection", "v2_p_void.png",     30.20, 32.00, dict(zoom=[1.18, 1.00], pan=[(0.5, 0.42), (0.5, 0.55)])),
    ("q_whisper",       "v2_q_whisper.png",  32.00, 34.55, dict(zoom=[1.04, 1.34], pan=[(0.5, 0.5), (0.5, 0.56)], shake=6, freq=9.0)),
    ("r_black",         None,                34.55, 35.10, dict(black=True)),
    ("s_empty",         "v2_s_empty.png",    35.10, 40.00, dict(zoom=[1.00, 1.22], pan=[(0.5, 0.42), (0.5, 0.5)])),
]

# ------------------------------------------------------------- narration
# t = instant de pose de la prise (s). La duree est mesuree sur le fichier.
VO = [
    dict(f="vo_s1.wav", t=0.15,  style="VO", text="Un soir, il a remarqué quelque chose d'impossible dans son miroir.", hi=["impossible"]),
    dict(f="vo_s2.wav", t=5.50,  style="VO", text="Son reflet avait toujours deux secondes de retard.", hi=["deux secondes"]),
    dict(f="vo_s3.wav", t=10.80, style="VO", text="Puis son reflet a commencé à faire des choses… qu'il ne faisait pas.", hi=["des choses"]),
    dict(f="vo_s4.wav", t=17.00, style="VO", text="Et là… il a compris qu'il n'était pas en train de regarder son reflet.", hi=["pas en train"]),
    dict(f="vo_s5.wav", t=24.30, style="VO", text="Il lui montrait quelque chose… derrière lui.", hi=["derrière lui"]),
    dict(f="vo_s6a.wav", t=32.05, style="WH", gain=1.38, whisper=True, text="Maintenant… c'est mon tour.", hi=["mon tour"]),
    dict(f="vo_s6b.wav", t=35.35, style="VO", gain=1.16, text="Et quand la lumière s'est rallumée… il n'était plus là.", hi=["plus là"]),
]

def vo_windows():
    return [(v["t"], v["t"] + dur_of(os.path.join(AUD, v["f"]))) for v in VO]

# ------------------------------------------------------------ sous-titres
HL = re.compile(r"\{\\c(&H[0-9A-Fa-f]+&)?\}")

def split_lines(text, maxc=26):
    out, cur = [], ""
    for w in text.split():
        trial = (cur + " " + w).strip()
        if len(trial) > maxc and cur:
            out.append(cur); cur = w
        else:
            cur = trial
        if cur.endswith("…"):
            out.append(cur); cur = ""
    if cur:
        out.append(cur)
    merged = []
    for ln in out:
        if merged and len(ln) < 9 and len(merged[-1]) + len(ln) <= maxc + 5:
            merged[-1] += " " + ln
        else:
            merged.append(ln)
    return merged

def build_cues():
    cues = []
    for v in VO:
        d = dur_of(os.path.join(AUD, v["f"]))
        lines = split_lines(v["text"]); wts = [len(l) for l in lines]
        t = v["t"]
        for ln, wt in zip(lines, wts):
            span = d * wt / sum(wts)
            for kw in v.get("hi", []):
                if kw.lower() in ln.lower():
                    ln = re.sub("(" + re.escape(kw) + ")",
                                lambda m: "{\c&H82BCFF&}" + m.group(1) + "{\c}",
                                ln, count=1, flags=re.I)
            cues.append(dict(text=ln, start=t + 0.05, end=t + span - 0.05,
                             style=v.get("style", "VO")))
            t += span
    cues.sort(key=lambda c: c["start"])
    for i in range(len(cues) - 1):
        cues[i]["end"] = max(cues[i]["start"] + 0.34,
                             min(cues[i]["end"], cues[i + 1]["start"] - 0.04))
    return cues

def t_ass(x):
    x = max(0.0, x); return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"

def t_srt(x):
    x = max(0.0, x); s = int(x)
    return f"{s//3600:02d}:{s%3600//60:02d}:{s%60:02d},{int(round((x%1)*1000)):03d}"

def write_subs(cues):
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: VO,DejaVu Sans,82,&H00FFFFFF,&H000000FF,&H000A0E12,&HD2000000,-1,0,0,0,100,100,-1,0,1,8,2,2,92,92,466,1
Style: WH,DejaVu Sans,76,&H00DCF4FF,&H000000FF,&H000A1218,&HD2000000,-1,1,0,0,100,100,2,0,1,7,2,2,92,92,466,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    body = "".join(
        f"Dialogue: 0,{t_ass(c['start'])},{t_ass(c['end'])},{c['style']},,0,0,0,,{{\\fad(70,90)}}{c['text']}\n"
        for c in cues)
    open(os.path.join(TMP, "subs.ass"), "w", encoding="utf-8").write(head + body)
    srt = "".join(f"{i}\n{t_srt(c['start'])} --> {t_srt(c['end'])}\n{HL.sub('', c['text'])}\n\n"
                  for i, c in enumerate(cues, 1))
    open(os.path.join(OUT, f"{SLUG}-fr.srt"), "w", encoding="utf-8").write(srt)
    return len(cues)

# --------------------------------------------------------------- segments
def seg_vf(mv, n):
    z0, z1 = mv["zoom"]; k = max(n - 1, 1)
    dz = f"{z0:.4f}+{z1-z0:.4f}*on/{k}"
    if "pan" in mv:
        (x0, y0), (x1, y1) = mv["pan"]
        fx, fy = f"{x0:.4f}+{x1-x0:.4f}*on/{k}", f"{y0:.4f}+{y1-y0:.4f}*on/{k}"
    else:
        fx = fy = "0.5"
    sx = sy = ""
    if mv.get("shake"):
        a, fq = mv["shake"], mv.get("freq", 7.0)
        sx = f"+{a}*sin(2*PI*{fq}*on/{FPS})"
        sy = f"+{a*0.6:.1f}*sin(2*PI*{fq*0.83:.2f}*on/{FPS}+1.7)"
    src = f"scale={SW}:{SH}:force_original_aspect_ratio=increase,crop={SW}:{SH}"
    return (src + f",zoompan=z='{dz}':x='(iw-iw/zoom)*({fx}){sx}':"
            f"y='(ih-ih/zoom)*({fy}){sy}':d={n}:s={W}x{H}:fps={FPS},"
            "unsharp=3:3:0.55,setsar=1,format=yuv420p")

# Repli automatique : si un plan v2 n'a pas pu etre genere (budget d'images),
# on reuse un plan AI existant avec un cadrage different. `derive_frames.py`
# fabrique de son cote les plans composes (verre embue, miroir vide).
ALT = {
    "e1_delay":        ("c_mirror_stare.png", dict(zoom=[1.02, 1.06], pan=[(0.5, 0.42), (0.5, 0.40)])),
    "j_doorway":       ("i_turn_door.png",    dict(zoom=[1.02, 1.24], pan=[(0.55, 0.5), (0.95, 0.46)])),
    "k_closer":        ("f_stepback.png",     dict(zoom=[1.00, 1.34], pan=[(0.45, 0.42), (0.42, 0.32)])),
    "m_points":        ("e_late_hand.png",    dict(zoom=[1.05, 1.20], pan=[(0.30, 0.26), (0.44, 0.20)])),
    "n_frozen":        ("g_fear.png",         dict(zoom=[1.24, 1.02], pan=[(0.5, 0.40), (0.5, 0.55)])),
    "o_smile_at_him":  ("h_smile.png",        dict(zoom=[1.05, 1.42], pan=[(0.5, 0.42), (0.5, 0.30)])),
    # Plan final : le visage reste seul dans le verre, pull-back -> boucle sur l'oeil.
    "s_empty":         ("c_mirror_stare.png", dict(zoom=[1.36, 1.00], pan=[(0.5, 0.34), (0.5, 0.46)])),
}

def shot_source(key, img, mv):
    """(fichier, mouvement) : plan demande si present, sinon repli sur un plan AI existant."""
    if img and os.path.exists(os.path.join(IMG, img)):
        return os.path.join(IMG, img), mv
    alt = ALT.get(key)
    if alt and os.path.exists(os.path.join(IMG, alt[0])):
        return os.path.join(IMG, alt[0]), alt[1]
    return None, mv

def render_segments():
    for key, img, st, en, mv in SHOTS:
        if img and not os.path.exists(os.path.join(IMG, img)):
            src, _ = shot_source(key, img, mv)
            print("  repli:", key, "->", (os.path.basename(src) if src else "AUCUN"))
    miss = sorted({s[1] for s in SHOTS if s[1] and not shot_source(s[0], s[1], s[4])[0]})
    if miss:
        raise SystemExit("IMAGES MANQUANTES -> " + ", ".join(miss) +
                         "\n   (relance derive_frames.py, ou genere les plans v2_*)")
    for key, img, st, en, mv in SHOTS:
        n = int(round((en - st) * FPS))
        dst = os.path.join(TMP, "seg", f"{key}.mp4")
        if os.environ.get("FORCE") == "1" and os.path.exists(dst):
            os.remove(dst)
        if os.path.exists(dst):
            continue
        if mv.get("black"):
            run(["-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}", "-frames:v", str(n),
                 "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", dst], key)
            continue
        src, mv2 = shot_source(key, img, mv)
        run(["-i", src, "-vf", seg_vf(mv2, n), "-frames:v", str(n),
             "-c:v", "libx264", "-preset", "fast", "-crf", "13", "-pix_fmt", "yuv420p", dst], key)
        print("  seg", key, f"{n}f", flush=True)
    with open(os.path.join(TMP, "seglist.txt"), "w") as f:
        for key, *_ in SHOTS:
            f.write(f"file '{os.path.join(TMP,'seg',key+'.mp4')}'\n")

# ------------------------------------------------------------------ audio
def render_stems():
    vw = vo_windows()
    duck = vol(gate_expr(vw, 0.32, 1))             # -10 dB de decor sous la voix
    hush = vol(gate_expr([(29.30, 30.30)], 0, 1))  # 1 s de silence total (scene 5)

    def heart(f, per, dec, amp, w0, w1, g):
        return (f"aevalsrc=sin(2*PI*{f}*t)*exp(-{dec}*mod(t\\,{per}))"
                f"+{amp}*sin(2*PI*{f-9}*t)*exp(-{float(dec)+6:g}*mod(t+{per}-0.19\\,{per})):d={TOTAL},"
                f"lowpass=f=190,volume={g},{vol(win(w0, w1))}")

    lav_out("room.wav",   "anoisesrc=color=brown:amplitude=0.05:seed=7,lowpass=f=430,volume=0.95")
    lav_out("buzz.wav",   f"aevalsrc=0.055*sin(2*PI*100*t)*(0.7+0.3*sin(2*PI*0.7*t))*"
                          f"(1-0.9*{win(34.4,40)}):d={TOTAL},highpass=f=60,lowpass=f=950")
    lav_out("drone.wav",  f"aevalsrc=0.55*sin(2*PI*37*t)*(0.55+0.45*sin(2*PI*0.06*t))*"
                          f"pow(t/{TOTAL}\\,1.4):d={TOTAL},lowpass=f=130")
    lav_out("tick.wav",   f"aevalsrc=0.55*sin(2*PI*2300*t)*exp(-85*mod(t\\,0.5)):d={TOTAL},"
                          f"highpass=f=1400,{vol(win(5.1,11.2))}")
    lav_out("hb_slow.wav", heart(57, "0.86", "13.5", 0.62, 5.4, 16.9, 1.25))
    lav_out("hb_fast.wav", heart(62, "0.52", "19.0", 0.58, 17.0, 34.5, 1.75))
    lav_out("boomA.wav",  f"aevalsrc=sin(2*PI*(155*t-55*t*t))*exp(-2.7*t)+0.3*(random(0)-0.5)*"
                          f"exp(-11*t):d=22:sample_rate={SR},lowpass=f=230,volume=1.35,adelay=20400:all=1")
    lav_out("boomB.wav",  f"aevalsrc=sin(2*PI*(140*t-48*t*t))*exp(-2.5*t)+0.25*(random(0)-0.5)*"
                          f"exp(-10*t):d=22:sample_rate={SR},lowpass=f=210,volume=1.2,adelay=30200:all=1")
    lav_out("impact.wav", f"aevalsrc=sin(2*PI*(210*t-95*t*t))*exp(-2.1*t)+0.6*(random(0)-0.5)*"
                          f"exp(-6.5*t):d=22:sample_rate={SR},lowpass=f=340,volume=1.75,"
                          f"adelay={int(IMPACT_T*1000)}:all=1")
    RISEX = "if(" + win(26.2, IMPACT_T) + "\\,pow((t-26.2)/8.35\\,2.4)*0.5\\,0)"
    lav_out("riser.wav",  "anoisesrc=color=pink:amplitude=0.6:seed=21,highpass=f=420," + vol(RISEX))
    lav_out("whisper.wav", "anoisesrc=color=pink:amplitude=0.55:seed=13,bandpass=f=1150:w=600,"
                           f"tremolo=f=5.5:d=0.85,{vol(win(21.0,31.4))}")
    lav_out("drip.wav",   f"aevalsrc=0.5*sin(2*PI*1450*t)*exp(-32*mod(t\\,1.25)):d={TOTAL},"
                          f"highpass=f=650,{vol(win(35.1,39.9))}")

    stems = ["room", "buzz", "drone", "tick", "hb_slow", "hb_fast",
             "boomA", "boomB", "impact", "riser", "whisper", "drip"]
    inputs = []
    for i, s in enumerate(stems):
        inputs += ["-i", os.path.join(TMP, s + ".wav")]
    graph = ("".join(f"[{i}:a]" for i in range(len(stems))) +
             f"amix=inputs={len(stems)}:normalize=0:duration=longest,"
             f"aformat=sample_rates={SR}:channel_layouts=stereo,atrim=0:{TOTAL},"
             f"afade=t=in:d=0.6,afade=t=out:st=39.3:d=0.7,{duck},{hush}[amb]")
    run(inputs + ["-filter_complex", graph, "-map", "[amb]", "-ar", str(SR), "-ac", "2",
                  "-c:a", "pcm_s16le", os.path.join(TMP, "ambience.wav")], "ambience mix")

    for i, v in enumerate(VO):
        if v.get("whisper"):
            head = f"[0:a]asetrate={SR}*0.86,aresample={SR},atempo=1.14,highpass=f=90,"
            echo = "aecho=0.85:0.42:56|112:0.42|0.26,"
        else:
            head = "[0:a]highpass=f=85,"
            echo = "aecho=0.7:0.2:33|69:0.2|0.1,"
        graph = (head + f"equalizer=f=2700:t=q:w=1.4:g=2.4,volume={v.get('gain',1.0):.2f}," + echo +
                 f"adelay={int(round(v['t']*1000))}:all=1,"
                 f"aformat=sample_rates={SR}:channel_layouts=stereo,apad,atrim=0:{TOTAL}[out]")
        run(["-i", os.path.join(AUD, v["f"]), "-filter_complex", graph, "-map", "[out]",
             "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le",
             os.path.join(TMP, f"vo_{i}.wav")], f"vo {i}")

    inputs = []
    for i in range(len(VO)):
        inputs += ["-i", os.path.join(TMP, f"vo_{i}.wav")]
    graph = ("".join(f"[{i}:a]" for i in range(len(VO))) +
             f"amix=inputs={len(VO)}:normalize=0,atrim=0:{TOTAL},"
             "loudnorm=I=-15:TP=-1.6:LRA=9[vo]")
    run(inputs + ["-filter_complex", graph, "-map", "[vo]", "-ar", str(SR), "-ac", "2",
                  "-c:a", "pcm_s16le", os.path.join(TMP, "vo_mix.wav")], "narration mix")
    print("audio ok")

# ------------------------------------------------------------------ final
def dip(t0, t1, opacity=1.0):
    """Clignotement borne a une fenetre (un fade=t=in noircirait tout l'avant)."""
    return (f"drawbox=x=0:y=0:w=iw:h=ih:c=black@{opacity}:t=fill:"
            f"enable='between(t,{t0},{t1})'")

GRADE = ",".join([
    "eq=contrast=1.06:brightness=-0.008:gamma=1.05:saturation=0.82",
    "colorbalance=rs=-0.05:gs=0.01:bs=0.07:rh=0.05:bm=-0.05",
    "curves=all='0/0 0.22/0.165 0.62/0.665 1/0.96'",
    "vignette=PI/4.6",
    "noise=alls=7:allf=u",
    f"ass={os.path.join(TMP, 'subs.ass')}",
    "fade=t=in:st=0:d=0.18",
    dip(2.13, 2.20, 1.0),      # coupe seche sur le plan large
    dip(3.06, 3.11, 0.62),     # amenee d'ampoule
    dip(4.02, 4.06, 0.5),
    dip(20.33, 20.41, 1.0),    # boom grave + retournement vers le miroir
]) + ","

def render_video():
    run(["-f", "concat", "-safe", "0", "-i", os.path.join(TMP, "seglist.txt"),
         "-vf", GRADE, "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "22",
         "-maxrate", "9M", "-bufsize", "12M", "-g", "120",
         "-profile:v", "high", "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
         "-color_trc", "bt709", "-colorspace", "bt709", os.path.join(TMP, "video.mp4")], "video")
    final = os.path.join(OUT, f"{SLUG}-9x16.mp4")
    run(["-i", os.path.join(TMP, "video.mp4"), "-i", os.path.join(TMP, "ambience.wav"),
         "-i", os.path.join(TMP, "vo_mix.wav"), "-filter_complex",
         "[1:a][2:a]amix=inputs=2:normalize=0:duration=longest,atrim=0:" + str(TOTAL) +
         ",alimiter=limit=0.92,loudnorm=I=-14:TP=-1.5:LRA=10[a]",
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-ar", "44100", "-ac", "2", "-movflags", "+faststart", "-shortest", final], "mux")
    print("OK ->", final, round(dur_of(final), 2), "s",
          round(os.path.getsize(final) / 1e6, 1), "Mo")
    return final

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    cues = build_cues()
    if mode in ("subs", "all"):
        print("cues:", write_subs(cues))
    if mode in ("audio", "all"):
        render_stems()
    if mode in ("video", "all"):
        write_subs(cues); render_segments(); render_stems(); render_video()
    if mode == "cues":
        print(json.dumps([{"in": round(c["start"], 2), "out": round(c["end"], 2), "x": c["text"]}
                          for c in cues], ensure_ascii=False, indent=1))
