"""Ajoute la musique au Short : mix voix + musique + ambiances, puis remux."""

import os
import re
import json
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline as T
import assemble as A

FF = T.FFMPEG
OUT = os.path.join(A.OUT_DIR, "short-mary-celeste-9x16.mp4")
TMP = os.path.join(T.WORK, "final_music.mp4")


def run(cmd, desc):
    print(">>", desc)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-4000:])
        raise SystemExit("Echec : " + desc)


def main():
    os.makedirs(T.WORK, exist_ok=True)
    print("=== 1/5 musique ===")
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                 "build_music.py")], check=True)
    print("=== 2/5 ambiances (vents, houle, tonnerre, impacts) ===")
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                 "build_bed.py")], check=True)
    print("=== 3/5 voix off ===")
    vo = A.build_voice()

    print("=== 4/5 mixage 3 sources + loudness ===")
    mix = os.path.join(T.WORK, "mix3.wav")
    run([FF, "-y", "-i", vo, "-i", os.path.join(T.AUDIO, "music.wav"),
         "-i", os.path.join(T.AUDIO, "bed.wav"), "-filter_complex",
         "[0:a]volume=1.00[vo];[1:a]volume=0.28[mu];[2:a]volume=0.45[bd];"
         "[vo][mu][bd]amix=inputs=3:normalize=0:duration=longest,"
         "alimiter=limit=0.95:level=false,atrim=0:%.2f,asetpts=N/SR/TB[m]"
         % (T.VIDEO_END + 0.6),
         "-map", "[m]", "-c:a", "pcm_s16le", mix], "mixage voix + musique + ambiances")
    audio, meas = A.loudnorm(mix)

    print("=== 5/5 remux (video inchangee) ===")
    run([FF, "-y", "-i", OUT, "-i", audio, "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-movflags", "+faststart", "-shortest", TMP], "remux video + musique")
    shutil.move(TMP, OUT)
    print("\nOK -> %s" % OUT)

    d = subprocess.run([FF, "-i", OUT], capture_output=True, text=True).stderr
    for line in d.splitlines():
        if "Duration" in line:
            print("  ", line.strip())
    r = subprocess.run([FF, "-i", OUT, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    for line in r.splitlines():
        if line.strip().startswith(("I:", "LRA:", "Peak:")):
            print("  ", line.strip())


if __name__ == "__main__":
    main()
