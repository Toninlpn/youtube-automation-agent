#!/usr/bin/env python3
"""
Plans composes pour LE REFLET — utilise ImageMagick sur les plans AI deja la.
Chaque derive n'est cree que si le vrai plan AI (v2_*) est absent : des qu'un
budget d'images permet de generer v2_l_pressed.png etc., render.py bascule
dessus tout seul et ce script ne fait plus rien.

  v2_l_pressed   visage plaque contre le verre + haleine condensee
  v2_q_whisper   levres contre la vitre, teinte froide dans le verre
  v2_p_void      le miroir ne renvoie plus l'homme (reflet efface)
  v2_s_empty     piece vide apres la coupure de courant (homme efface)
"""
import os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG  = os.path.join(ROOT, "img")

def sh(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if p.returncode != 0:
        print("FAIL:", cmd, "\n", p.stderr[-400:]); sys.exit(1)

def have(tool):
    return shutil.which(tool)

def need(dst):
    """True si le plan derive doit etre fabrique."""
    if os.path.exists(os.path.join(IMG, dst)):
        print("  deja genere par l'IA:", dst)
        return False
    return True

def fog(size, ellipse, blur, mult):
    """Couche de buee pleine trame (le flou ne doit pas etre rogne par le canevas)."""
    sh(f'convert -size {size} xc:none -fill white -draw "ellipse {ellipse} 0,360" '
       f'-blur 0x{blur} -evaluate multiply {mult} /tmp/fog.png')
    return "/tmp/fog.png"

def main():
    if not have("convert"):
        raise SystemExit("ImageMagick (convert) introuvable: apt-get install imagemagick")

    if need("v2_l_pressed.png"):
        f = fog("768x1376", "372,600 190,86", 70, "0.20")
        sh(f'convert {IMG}/c_mirror_stare.png {f} -gravity north -composite '
           f'-alpha remove -alpha off {IMG}/v2_l_pressed.png')
        print("  + v2_l_pressed.png")

    if need("v2_q_whisper.png"):
        f = fog("768x1376", "372,700 205,96", 78, "0.26")
        sh(f'convert {IMG}/c_mirror_stare.png -modulate 95 '
           f'-fill "rgba(150,196,224,0.07)" -draw "rectangle 0,0 100%,100%" '
           f'{f} -gravity north -composite -alpha remove -alpha off {IMG}/v2_q_whisper.png')
        print("  + v2_q_whisper.png")

    if need("v2_p_void.png"):
        # Le miroir ne renvoie plus l'homme : masque radial adouci (pas de rectangle dur),
        # pose sur la zone du miroir de f_stepback (x 24-47 %, y 14-43 %).
        sh('convert -size 177x399 xc:none -fill white -draw "ellipse 88,199 88,199 0,360" '
           '-blur 0x46 -evaluate multiply 0.72 /tmp/mask.png')
        sh("convert -size 177x399 xc:'#04080b' /tmp/mask.png -alpha off "
           "-compose CopyOpacity -composite /tmp/patch.png")
        sh(f"convert {IMG}/f_stepback.png /tmp/patch.png -geometry +184+193 -composite "
           f"-modulate 97 {IMG}/v2_p_void.png")
        print("  + v2_p_void.png (masque feathered)")

if __name__ == "__main__":
    main()
