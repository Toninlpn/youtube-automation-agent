"""Correction du parasite sonore : regenère le bed + la voix off et remuxe la vidéo existante."""

import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline as T
import assemble as A

FF = T.FFMPEG
OUT = os.path.join(A.OUT_DIR, "short-mary-celeste-9x16.mp4")
TMP = os.path.join(T.WORK, "final_fixed.mp4")


def run(cmd, desc):
    print(">>", desc)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-4000:])
        raise SystemExit("Echec : " + desc)


def main():
    os.makedirs(T.WORK, exist_ok=True)
    print("=== 1/4 bed sonore corrige ===")
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                 "build_bed.py")], check=True)

    print("=== 2/4 voix off (rubberband) ===")
    vo = A.build_voice()

    print("=== 3/4 mixage + loudness ===")
    mix = A.mix_audio(vo, os.path.join(T.AUDIO, "bed.wav"))
    audio, meas = A.loudnorm(mix)

    print("=== 4/4 remux (video copiee telle quelle) ===")
    run([FF, "-y", "-i", OUT, "-i", audio, "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-movflags", "+faststart", "-shortest", TMP], "remux video + audio corrige")
    shutil.move(TMP, OUT)
    print("\nOK -> %s" % OUT)

    # controles
    d = subprocess.run([FF, "-i", OUT], capture_output=True, text=True).stderr
    for line in d.splitlines():
        if "Duration" in line or "Stream #0" in line:
            print("  ", line.strip())
    r = subprocess.run([FF, "-i", OUT, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    for line in r.splitlines():
        if "I:" in line or "Peak:" in line or "LRA:" in line:
            print("  ", line.strip())


if __name__ == "__main__":
    main()
