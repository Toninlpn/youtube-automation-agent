#!/usr/bin/env python3
"""Montage complet du Short « La caméra a filmé quelqu'un qui n'était pas là ».

Pipeline (rejouable, resume-friendly) :
  1. scenes   : chaque plan = image fixe -> crop 9:16 (retire la bande
                d'overlay incrustée par le générateur) -> zoompan (push-in /
                digital zoom / micro-shake CCTV) -> H.264 crf 12
  2. concat   : timeline brute 25 fps
  3. mix      : voix off traitées + couches synthétisées (build_audio.py)
                + murmure final détimbré -> loudnorm -14 LUFS
  4. final    : grade CCTV (eq, rgbashift aux glitches, noise, vignette,
                horodatage DVR défilant, point REC) + mux audio
  5. exports  : master 9:16, web, 720p, preview 480p, cover, thumbnail

Usage : python3 build.py [scenes|mix|final|exports|all]
"""
import calendar
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
FF = os.path.join(REPO, "..", "tools", "bin", "ffmpeg")
if not os.path.exists(FF):
    FF = "ffmpeg"
ASSETS = os.path.join(HERE, "assets")
AUDIO = os.path.join(HERE, "audio")
TMP = os.path.join(HERE, "tmp")
OUT = os.path.join(HERE, "video")
for d in (TMP, OUT):
    os.makedirs(d, exist_ok=True)

FPS = 25
W, H = 1080, 1920
# Horodatage DVR : nuit du 26 -> 27 septembre 2026, Paris (UTC+2 en été)
# 02:16:58 locales = 00:16:58 UTC
EPOCH = calendar.timegm(time.strptime("2026-09-27T00:16:58Z", "%Y-%m-%dT%H:%M:%SZ"))
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

A = lambda n: os.path.join(ASSETS, n)

# nom, source, durée, z0, z1, centre x, centre y (après crop), courbe, shake
SHOTS = [
    ("s01", A("ext07_street_empty_match.png"),   0.90, 1.03, 1.03, 0.50, 0.392, "lin", 4),
    ("s02", A("ext02_man_walking_silhouette_far.png"), 4.10, 1.02, 1.12, 0.546, 0.278, "lin", 3),
    ("s03", A("ext03_man_at_door_silhouette_closer.png"), 4.00, 1.02, 1.30, 0.518, 0.246, "pow", 2),
    ("s04", A("int04_man_keys_match.png"),       2.60, 1.02, 1.10, 0.30, 0.620, "lin", 2),
    ("s05", A("int02_livingroom_figure_doorway.png"), 0.60, 1.06, 1.06, 0.62, 0.570, "lin", 5),
    ("s06", A("int04_man_keys_match.png"),       1.80, 1.22, 1.28, 0.28, 0.640, "lin", 2),
    ("s07", A("ext08_silhouette_at_house.png"),  2.60, 1.02, 1.12, 0.40, 0.720, "lin", 3),
    ("s08", A("int05_man_turning_match.png"),    2.60, 1.02, 1.12, 0.62, 0.600, "lin", 2),
    ("s09", A("int05_man_turning_match.png"),    2.40, 1.30, 1.36, 0.64, 0.620, "lin", 1),
    ("s10", A("ext08_silhouette_at_house.png"),  2.40, 1.32, 1.42, 0.40, 0.740, "lin", 2),
    ("s11", A("ext07_street_empty_match.png"),   2.00, 1.03, 1.05, 0.50, 0.392, "lin", 4),
    ("s12", A("ext06_face_at_lens.png"),         0.16, 1.05, 1.05, 0.50, 0.392, "lin", 6),
    ("s13", A("ext07_street_empty_match.png"),   0.34, 1.03, 1.03, 0.50, 0.392, "lin", 4),
    ("s14", None,                                2.50, 1.00, 1.00, 0.50, 0.500, "lin", 0),
]

# fenêtres de glitch chromatique (t global, s)
GLITCH_WINDOWS = [(0.86, 1.04), (11.56, 12.24), (24.52, 24.78), (25.32, 25.60), (25.96, 26.52)]
EXT_ON = "lt(t,9)+between(t,14,16.6)+between(t,24,26.5)"
INT_ON = "between(t,9,14)+between(t,16.6,24)"


def run(cmd, **kw):
    print("  $", " ".join(cmd[:6]), "…")
    subprocess.run(cmd, check=True, **kw)


def scene_filter(src, dur, z0, z1, fx, fy, curve, shake):
    nf = max(1, int(round(dur * FPS)))
    p = f"(on/{nf})" if curve == "lin" else f"pow(on/{nf},1.6)"
    z = f"{z0}+({z1}-{z0})*{p}" if z1 != z0 else f"{z0}"
    sx = f"+{shake}*sin(2*PI*on/95)" if shake else ""
    sy = f"+{shake}*sin(2*PI*on/71+1.3)" if shake else ""
    x = f"max(0,min(iw-iw/zoom,iw*{fx}-(iw/zoom)/2{sx}))"
    y = f"max(0,min(ih-ih/zoom,ih*{fy}-(ih/zoom)/2{sy}))"
    return (
        "crop=700:1245:34:131,scale=2160:3840:flags=lanczos,"
        f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s={W}x{H}:fps={FPS},format=yuv420p"
    )


def build_scenes():
    for name, src, dur, z0, z1, fx, fy, curve, shake in SHOTS:
        out = os.path.join(TMP, f"{name}.mp4")
        if os.path.exists(out):
            continue
        if src is None:
            run([FF, "-hide_banner", "-loglevel", "error", "-y",
                 "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}:d={dur}",
                 "-c:v", "libx264", "-crf", "12", "-preset", "veryfast",
                 "-pix_fmt", "yuv420p", "-r", str(FPS), out])
        else:
            vf = scene_filter(src, dur, z0, z1, fx, fy, curve, shake)
            run([FF, "-hide_banner", "-loglevel", "error", "-y",
                 "-loop", "1", "-framerate", str(FPS), "-t", f"{dur}", "-i", src,
                 "-vf", vf, "-c:v", "libx264", "-crf", "12", "-preset", "veryfast",
                 "-pix_fmt", "yuv420p", "-r", str(FPS), out])
    lst = os.path.join(TMP, "concat.txt")
    with open(lst, "w") as f:
        for name, *_ in SHOTS:
            f.write(f"file '{os.path.join(TMP, name + '.mp4')}'\n")
    run([FF, "-hide_banner", "-loglevel", "error", "-y",
         "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
         os.path.join(TMP, "timeline.mp4")])


VO_CHAIN = ("highpass=f=90,lowpass=f=11500,"
            "acompressor=threshold=-20dB:ratio=2.5:attack=6:release=220:makeup=4,"
            "equalizer=f=3200:t=q:w=1.2:g=2.5,aecho=0.7:0.5:23:0.10,volume={v}")
WHISPER_CHAIN = ("asetrate=38400,aresample=48000,atempo=1.10,highpass=f=180,lowpass=f=1500,"
                 "tremolo=f=6.5:d=0.55,aecho=0.8:0.7:70|120:0.35|0.22,volume=0.14")


def build_mix():
    out = os.path.join(OUT, "mix.wav")
    if os.path.exists(out):
        return
    L = lambda n: os.path.join(AUDIO, "layers", n)
    inputs = []
    for n in ("amb", "rumble", "heart", "breath", "glitch", "buzz"):
        inputs += ["-i", L(f"{n}.wav")]
    for n in ("vo1", "vo2", "vo3", "vo4", "vo5"):
        inputs += ["-i", os.path.join(AUDIO, f"{n}.wav")]
    inputs += ["-i", os.path.join(AUDIO, "entity_whisper.wav")]
    parts, idx = [], 0
    for n in ("amb", "rumble", "heart", "breath", "glitch", "buzz"):
        parts.append(f"[{idx}:a]anull[a{n}]")
        idx += 1
    vo_delays = {"vo1": 300, "vo2": 5300, "vo3": 10400, "vo4": 19300, "vo5": 21500}
    vo_vols = {"vo1": 1.0, "vo2": 1.0, "vo3": 0.95, "vo4": 0.90, "vo5": 0.95}
    labels = ["aamb", "arumble", "aheart", "abreath", "aglitch", "abuzz"]
    for n, d in vo_delays.items():
        parts.append(f"[{idx}:a]{VO_CHAIN.format(v=vo_vols[n])},"
                     f"adelay={d}|{d}[{n}]")
        labels.append(n)
        idx += 1
    parts.append(f"[{idx}:a]{WHISPER_CHAIN},adelay=27100|27100[wh]")
    labels.append("wh")
    mix = "[" + "][".join(labels) + f"]amix=inputs={len(labels)}:normalize=0:duration=longest,"
    mix += "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[mx]"
    parts.append(mix)
    run([FF, "-hide_banner", "-loglevel", "error", "-y", *inputs,
         "-filter_complex", ";".join(parts), "-map", "[mx]",
         "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", out])


def ass_ts(sec_frac):
    h = int(sec_frac // 3600)
    m = int((sec_frac % 3600) // 60)
    s = sec_frac % 60
    return f"{h}:{m:02d}:{int(s):02d}.{int(round((s - int(s)) * 100)):02d}"


def write_ass():
    """Overlay DVR (horodatage défilant, label CAM, point REC clignotant).
    Ce build ffmpeg n'a pas drawtext : on passe par libass (filtre subtitles)."""
    path = os.path.join(TMP, "overlay.ass")
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "WrapStyle: 2",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: TS,DejaVu Sans Mono,34,&HCCFFFFFF,&H00000000,&H70000000,&H70000000,0,0,0,0,100,100,0,0,1,2,1,7,40,40,40,1",
        "Style: CAM,DejaVu Sans Mono,28,&HA5FFFFFF,&H00000000,&H70000000,&H70000000,0,0,0,0,100,100,0,0,1,2,1,7,40,40,40,1",
        "Style: REC,DejaVu Sans Mono,30,&H000000E0,&H00000000,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,0,0,7,40,40,40,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    base = EPOCH  # 00:16:58 UTC = 02:16:58 Paris
    for idx in range(27):          # 0 → 26 s (rien au-delà : cut to black)
        clock = time.gmtime(base + idx)
        txt = time.strftime("%d-%m-%Y %H:%M:%S", clock)
        lines.append(f"Dialogue: 0,{ass_ts(idx)},{ass_ts(idx + 1)},"
                     f"TS,,0,0,0,,{{\\pos(40,1846)}}{txt}")
    for t0, t1, cam in ((0, 9, "CAM 4"), (9, 14, "CAM 2"), (14, 16.6, "CAM 4"),
                        (16.6, 21.6, "CAM 2"), (21.6, 26.5, "CAM 4")):
        lines.append(f"Dialogue: 0,{ass_ts(t0)},{ass_ts(t1)},CAM,,0,0,0,,"
                     f"{{\\pos(40,40)}}{cam}")
    k = 0
    t = 0.0
    while t < 26.5:
        if (t % 2) < 1.2:
            lines.append(f"Dialogue: 0,{ass_ts(t)},{ass_ts(min(t + 0.5, 26.5))},"
                         f"REC,,0,0,0,,{{\\pos(1016,38)}}●")
        t += 0.5
        k += 1
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


GRADE = (
    "eq=eval=frame:contrast=1.06:saturation=0.80:"
    "brightness='if(between(t,18.30,18.40),-0.55,if(between(t,18.40,18.47),0.22,"
    "if(between(t,18.47,18.56),-0.38,0)))',"
    "rgbashift=rh=8:bh=-8:rv=3:bv=-3:enable='"
    + "+".join(f"between(t,{a},{b})" for a, b in GLITCH_WINDOWS) + "',"
    "noise=alls=6:allf=t+u,vignette=a=PI/4.7"
)


def build_final():
    out = os.path.join(OUT, "la-camera-2h17-9x16.mp4")
    if os.path.exists(out):
        return
    ass = write_ass()
    run([FF, "-hide_banner", "-loglevel", "error", "-y",
         "-i", os.path.join(TMP, "timeline.mp4"), "-i", os.path.join(OUT, "mix.wav"),
         "-filter_complex", f"[0:v]{GRADE},subtitles=filename={ass}[v];"
         "[1:a]loudnorm=I=-14:TP=-1.5:LRA=11[a]",
         "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-preset", "slow", "-crf", "19",
         "-profile:v", "high", "-level", "4.0", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-movflags", "+faststart", "-t", "29.0", out])


def build_exports():
    master = os.path.join(OUT, "la-camera-2h17-9x16.mp4")
    jobs = [
        ("la-camera-2h17-web.mp4", ["-vf", f"scale={W}:{H}", "-c:v", "libx264", "-crf", "26", "-preset", "medium", "-b:a", "128k"]),
        ("la-camera-2h17-720p.mp4", ["-vf", "scale=720:1280", "-c:v", "libx264", "-crf", "27", "-preset", "medium", "-b:a", "128k"]),
        ("la-camera-2h17-preview-480p.mp4", ["-vf", "scale=480:854", "-c:v", "libx264", "-crf", "28", "-preset", "medium", "-b:a", "96k"]),
    ]
    for name, extra in jobs:
        dst = os.path.join(OUT, name)
        if not os.path.exists(dst):
            run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", master,
                 *extra, "-c:a", "aac", "-movflags", "+faststart", dst])
    cover = os.path.join(OUT, "cover-1080x1920.jpg")
    if not os.path.exists(cover):
        run([FF, "-hide_banner", "-loglevel", "error", "-y", "-ss", "7.2", "-i", master,
             "-frames:v", "1", "-q:v", "3", cover])
    thumb = os.path.join(OUT, "thumbnail-1280x720.jpg")
    if not os.path.exists(thumb):
        run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", cover,
             "-vf", "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720",
             "-q:v", "3", thumb])


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage in ("scenes", "all"):
        print("== scenes ==")
        build_scenes()
    if stage in ("mix", "all"):
        print("== mix ==")
        build_mix()
    if stage in ("final", "all"):
        print("== final ==")
        build_final()
    if stage in ("exports", "all"):
        print("== exports ==")
        build_exports()
    print("OK")
