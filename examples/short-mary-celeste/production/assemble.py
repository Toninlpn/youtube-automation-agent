"""Assemble le Short final : plans Ken Burns, transitions, etalonnage, sous-titres, mix audio."""

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline as T

FF = T.FFMPEG
HERE = os.path.dirname(os.path.abspath(__file__))
CLIPS = os.path.join(T.WORK, "clips")
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT_DIR = os.path.join(REPO, "examples", "short-mary-celeste")


def run(cmd, desc=""):
    print(">>", desc)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-5000:])
        raise SystemExit("Echec : " + desc)
    return r


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def build_clips():
    os.makedirs(CLIPS, exist_ok=True)
    expected = [os.path.join(CLIPS, "clip_%02d.mp4" % i) for i in range(len(T.SHOTS))]
    if all(os.path.exists(p) for p in expected):
        print(">> plans deja rendus, reutilisation")
        return expected
    for i, (name, start, end, z0, z1, px, py, trans) in enumerate(T.SHOTS):
        t_prev = T.SHOTS[i - 1][7] if i > 0 else 0.0
        t_next = T.SHOTS[i + 1][7] if i < len(T.SHOTS) - 1 else 0.0
        length = (end - start) + (t_prev + t_next) / 2.0
        frames = max(2, int(round(length * T.FPS)))
        img = T.image_path(name)
        out = os.path.join(CLIPS, "clip_%02d.mp4" % i)
        zexpr = "%.4f+(%.4f)*on/%d" % (z0, z1 - z0, frames - 1)
        xexpr = "iw/2-(iw/zoom/2)+(%.4f)*(iw/zoom)*on/%d" % (px, frames - 1)
        yexpr = "ih/2-(ih/zoom/2)+(%.4f)*(ih/zoom)*on/%d" % (py, frames - 1)
        vf = ("scale=2160:3840:flags=lanczos,setsar=1,"
              "zoompan=z='%s':x='%s':y='%s':d=%d:s=1080x1920:fps=%d,"
              "trim=duration=%.4f,setpts=PTS-STARTPTS,fps=%d,setsar=1,format=yuv420p"
              % (zexpr, xexpr, yexpr, frames, T.FPS, length, T.FPS))
        run([FF, "-y", "-loop", "1", "-framerate", str(T.FPS), "-t", "%.4f" % length,
             "-i", img, "-vf", vf, "-c:v", "libx264", "-preset", "veryfast",
             "-crf", "14", "-pix_fmt", "yuv420p", "-r", str(T.FPS), "-an", out],
            "plan %02d %s (%.2fs, zoom %.2f->%.2f)" % (i, name, length, z0, z1))
    return expected


GRADE = ("eq=contrast=1.06:brightness=-0.010:saturation=0.78,"
         "colorbalance=bs=0.06:bm=0.02:rs=-0.02,"
         "vignette=angle=PI/4.5,"
         "hqdn3d=1.2:1.2:5:5,"
         "noise=alls=3:allf=u,"
         "unsharp=5:5:0.35:5:5:0.0,"
         "fade=t=in:st=0:d=%.2f,"
         "fade=t=out:st=%.2f:d=%.2f,"
         "format=yuv420p" % (T.FADE_IN, T.FADE_OUT_START, T.VIDEO_END - T.FADE_OUT_START))


def clip_length(i):
    """Duree encodee du plan i (inclut les demi-transitions)."""
    b, e = T.SHOTS[i][1], T.SHOTS[i][2]
    prev_trans = T.SHOTS[i - 1][7] if i > 0 else 0.0
    next_trans = T.SHOTS[i + 1][7] if i < len(T.SHOTS) - 1 else 0.0
    return (e - b) + (prev_trans + next_trans) / 2.0


def build_segments(clips):
    """Decoupe en segments courts (tete, transition, corps) pour rester legere en RAM."""
    n = len(clips)
    segs = []
    for i in range(n):
        b, e = T.SHOTS[i][1], T.SHOTS[i][2]
        prev_trans = T.SHOTS[i - 1][7] if i > 0 else 0.0
        next_trans = T.SHOTS[i + 1][7] if i < n - 1 else 0.0
        len_i = clip_length(i)

        if i == 0:
            dur = T.SHOTS[1][1] - T.SHOTS[0][7] / 2.0
            out = os.path.join(T.WORK, "seg_%02d_head.mp4" % i)
            run([FF, "-y", "-i", clips[i], "-vf",
                 "trim=duration=%.4f,setpts=PTS-STARTPTS,settb=AVTB,fps=%d,setsar=1,format=yuv420p"
                 % (dur, T.FPS),
                 "-c:v", "libx264", "-preset", "superfast", "-crf", "13",
                 "-pix_fmt", "yuv420p", "-r", str(T.FPS), "-an", out],
                "segment tete (plan 0, %.2fs)" % dur)
            segs.append(out)

        if i > 0:
            # segment de transition : fondue du plan precedent vers le plan courant
            out = os.path.join(T.WORK, "seg_%02d_trans.mp4" % i)
            len_prev = clip_length(i - 1)
            fc = ("[0:v]trim=start=%.4f:duration=%.4f,setpts=PTS-STARTPTS,settb=AVTB,fps=%d[bg];"
                  "[1:v]trim=duration=%.4f,setpts=PTS-STARTPTS,settb=AVTB,fps=%d,format=rgba,"
                  "fade=t=in:st=0:d=%.4f:alpha=1[ov];"
                  "[bg][ov]overlay=0:0,setsar=1,format=yuv420p[v]"
                  % (len_prev - prev_trans, prev_trans, T.FPS,
                     prev_trans, T.FPS, prev_trans))
            run([FF, "-y", "-i", clips[i - 1], "-i", clips[i], "-filter_complex", fc,
                 "-map", "[v]", "-c:v", "libx264", "-preset", "superfast", "-crf", "13",
                 "-pix_fmt", "yuv420p", "-r", str(T.FPS), "-an", out],
                "segment transition %d (%.2fs)" % (i, prev_trans))
            segs.append(out)

            body_start = prev_trans
            body_end = len_i if i == n - 1 else len_i - next_trans / 2.0
            if body_end - body_start > 0.02:
                out = os.path.join(T.WORK, "seg_%02d_body.mp4" % i)
                run([FF, "-y", "-i", clips[i], "-vf",
                     "trim=start=%.4f:end=%.4f,setpts=PTS-STARTPTS,settb=AVTB,fps=%d,setsar=1,format=yuv420p"
                     % (body_start, body_end, T.FPS),
                     "-c:v", "libx264", "-preset", "superfast", "-crf", "13",
                     "-pix_fmt", "yuv420p", "-r", str(T.FPS), "-an", out],
                    "segment corps (plan %d, %.2fs)" % (i, body_end - body_start))
                segs.append(out)
    return segs


def build_base(clips):
    segs = build_segments(clips)
    lines = []
    for i, s in enumerate(segs):
        lines.append("[%d:v]settb=AVTB,fps=%d,setpts=PTS-STARTPTS[s%d]" % (i, T.FPS, i))
    lines.append("".join("[s%d]" % i for i in range(len(segs)))
                 + "concat=n=%d:v=1:a=0[cat]" % len(segs))
    lines.append("[cat]%s,trim=duration=%.2f,setpts=PTS-STARTPTS[vout]" % (GRADE, T.VIDEO_END))
    script = os.path.join(T.WORK, "graph_base.txt")
    with open(script, "w") as fh:
        fh.write(";\n".join(lines))
    out = os.path.join(T.WORK, "base.mp4")
    cmd = [FF, "-y"]
    for s in segs:
        cmd += ["-i", s]
    cmd += ["-filter_complex_script", script, "-map", "[vout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "15",
            "-pix_fmt", "yuv420p", "-r", str(T.FPS), "-an", out]
    run(cmd, "assemblage %d segments + etalonnage cine" % len(segs))
    return out


def build_video(base):
    """Incruste les textes par tranches de 6 s (memoire maitrisee)."""
    entries = json.load(open(os.path.join(T.WORK, "texts.json"), encoding="utf-8"))
    CHUNK = 6.0
    outs = []
    c0 = 0.0
    ci = 0
    while c0 < T.VIDEO_END - 0.01:
        c1 = min(c0 + CHUNK, T.VIDEO_END)
        active = [e for e in entries if e["end"] > c0 + 0.01 and e["start"] < c1 - 0.01]
        out = os.path.join(T.WORK, "txt_%02d.mp4" % ci)
        if not active:
            run([FF, "-y", "-ss", "%.3f" % c0, "-i", base, "-t", "%.3f" % (c1 - c0),
                 "-c:v", "libx264", "-preset", "superfast", "-crf", "14",
                 "-pix_fmt", "yuv420p", "-r", str(T.FPS), "-an", out],
                "tranche %d (%.1f-%.1fs, sans texte)" % (ci, c0, c1))
        else:
            lines, inputs = [], []
            for j, e in enumerate(active):
                inputs += ["-loop", "1", "-t", "%.3f" % (c1 - c0), "-i", e["file"]]
                if e["start"] > c0 + 0.01:
                    lines.append("[%d:v]format=rgba,settb=AVTB,"
                                 "fade=t=in:st=%.3f:d=0.15:alpha=1[t%d]"
                                 % (j + 1, e["start"] - c0, j))
                else:
                    lines.append("[%d:v]format=rgba,settb=AVTB[t%d]" % (j + 1, j))
            cur = "0:v"
            for j, e in enumerate(active):
                s = max(e["start"], c0) - c0
                en = min(e["end"], c1) - c0
                nxt = "o%d" % j
                lines.append("[%s][t%d]overlay=0:0:enable='between(t,%.3f,%.3f)'[%s]"
                             % (cur, j, s, en, nxt))
                cur = nxt
            run([FF, "-y", "-ss", "%.3f" % c0, "-t", "%.3f" % (c1 - c0), "-i", base] + inputs
                + ["-filter_complex", ";\n".join(lines), "-map", "[%s]" % cur,
                   "-c:v", "libx264", "-preset", "superfast", "-crf", "14",
                   "-pix_fmt", "yuv420p", "-r", str(T.FPS), "-an", out],
                "tranche %d (%.1f-%.1fs, %d textes)" % (ci, c0, c1, len(active)))
        outs.append(out)
        c0 = c1
        ci += 1

    lines = []
    for i in range(len(outs)):
        lines.append("[%d:v]settb=AVTB,fps=%d,setpts=PTS-STARTPTS[t%d]" % (i, T.FPS, i))
    lines.append("".join("[t%d]" % i for i in range(len(outs)))
                 + "concat=n=%d:v=1:a=0,trim=duration=%.2f,setpts=PTS-STARTPTS[v]"
                 % (len(outs), T.VIDEO_END))
    out = os.path.join(T.WORK, "video_final.mp4")
    cmd = [FF, "-y"]
    for o in outs:
        cmd += ["-i", o]
    cmd += ["-filter_complex", ";\n".join(lines), "-map", "[v]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "17",
            "-maxrate", "11M", "-bufsize", "22M",
            "-pix_fmt", "yuv420p", "-r", str(T.FPS), "-an", out]
    run(cmd, "assemblage des %d tranches de sous-titres" % len(outs))
    return out


def build_voice():
    wins = T.vo_windows()
    lines, inputs = [], []
    for i, (name, _) in enumerate(T.VOICEOVER):
        inputs += ["-i", os.path.join(T.AUDIO, name + ".mp3")]
        ms = int(round(wins[name][0] * 1000))
        lines.append(
            "[%d:a]aresample=48000,"
            "rubberband=pitch=%.4f:tempo=%.4f,"
            "highpass=f=90,equalizer=f=110:t=q:w=1.2:g=2.5,equalizer=f=3400:t=q:w=2:g=-2,"
            "acompressor=threshold=-18dB:ratio=2.5:attack=10:release=200:makeup=1.5,"
            "pan=stereo|c0=c0|c1=c0,adelay=%d|%d[v%d]"
            % (i, 1.0 / T.PITCH_RATE, T.NET_TEMPO, ms, ms, i))
    lines.append("[v0][v1][v2][v3][v4][v5]amix=inputs=6:normalize=0:duration=longest,"
                 "atrim=0:%.2f,asetpts=N/SR/TB,"
                 "aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[vout]"
                 % (T.VIDEO_END + 0.6))
    script = os.path.join(T.WORK, "graph_vo.txt")
    with open(script, "w") as fh:
        fh.write(";\n".join(lines))
    out = os.path.join(T.WORK, "vo_mix.wav")
    run([FF, "-y"] + inputs + ["-filter_complex_script", script, "-map", "[vout]",
                               "-c:a", "pcm_s16le", out], "voix off traitee (pitch -5 %, EQ, comp, reverb)")
    return out


def mix_audio(vo, bed):
    out = os.path.join(T.WORK, "mix.wav")
    run([FF, "-y", "-i", vo, "-i", bed, "-filter_complex",
         "[0:a]volume=1.0[vo];[1:a]volume=0.85[bd];"
         "[vo][bd]amix=inputs=2:normalize=0:duration=longest,"
         "alimiter=limit=0.95:level=false,atrim=0:%.2f,asetpts=N/SR/TB[m]"
         % (T.VIDEO_END + 0.6),
         "-map", "[m]", "-c:a", "pcm_s16le", out], "mixage voix + design sonore")
    return out


def loudnorm(mix):
    r = subprocess.run([FF, "-i", mix, "-af",
                        "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\}", r.stderr, re.S)
    meas = json.loads(m.group(0))
    print("   loudness mesuree : %s LUFS integres" % meas["input_i"])
    out = os.path.join(T.WORK, "audio_final.wav")
    run([FF, "-y", "-i", mix, "-af",
         "loudnorm=I=-14:TP=-1.5:LRA=11:linear=true:"
         "measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s,"
         "aresample=48000" % (meas["input_i"], meas["input_tp"], meas["input_lra"],
                              meas["input_thresh"], meas["target_offset"]),
         "-c:a", "pcm_s16le", out], "normalisation -14 LUFS / -1,5 dBTP")
    return out, meas


def final_mux(video, audio):
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "short-mary-celeste-9x16.mp4")
    run([FF, "-y", "-i", video, "-i", audio, "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-movflags", "+faststart", "-shortest", out], "rendu final 1080x1920")
    return out


def write_srt():
    entries = json.load(open(os.path.join(T.WORK, "texts.json"), encoding="utf-8"))
    caps = [e for e in entries if e["kind"] == "cap"]
    lines = []
    for i, e in enumerate(caps, 1):
        lines += [str(i), "%s --> %s" % (srt_time(e["start"]), srt_time(e["end"])),
                  e["text"], ""]
    path = os.path.join(OUT_DIR, "short-mary-celeste-fr.srt")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return path


def cleanup():
    """Supprime les intermediaires lourds (le harnais elague les gros artefacts)."""
    import shutil
    freed = 0
    for d in ("clips",):
        p = os.path.join(T.WORK, d)
        if os.path.isdir(p):
            freed += sum(os.path.getsize(os.path.join(r, f))
                         for r, _, fs in os.walk(p) for f in fs)
            shutil.rmtree(p, ignore_errors=True)
    for f in os.listdir(T.WORK):
        if f.startswith(("seg_", "txt_")) or f in ("base.mp4", "video_final.mp4",
                                                   "vo_mix.wav", "mix.wav", "audio_final.wav"):
            fp = os.path.join(T.WORK, f)
            if os.path.isfile(fp):
                freed += os.path.getsize(fp)
                os.remove(fp)
    print(">> intermediaires supprimes (%.0f Mo liberes)" % (freed / 1e6))


def main():
    os.makedirs(T.WORK, exist_ok=True)
    print("=== 1/6 plans Ken Burns ===")
    clips = build_clips()
    print("=== 2/6 transitions + etalonnage ===")
    base = build_base(clips)
    print("=== 3/6 sous-titres ===")
    video = build_video(base)
    print("=== 4/6 voix off ===")
    vo = build_voice()
    print("=== 5/6 mixage + loudness ===")
    mix = mix_audio(vo, os.path.join(T.AUDIO, "bed.wav"))
    audio, meas = loudnorm(mix)
    print("=== 6/6 rendu final ===")
    final = final_mux(video, audio)
    srt = write_srt()
    cleanup()
    print("\nOK -> %s\nSRT -> %s" % (final, srt))


if __name__ == "__main__":
    main()
