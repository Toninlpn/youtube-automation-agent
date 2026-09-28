# La caméra a filmé quelqu'un qui n'était pas là 😨 #shorts

Short d'horreur found-footage 9:16 · 29,0 s · 1080×1920 · 25 fps · AAC 192 k · −14,7 LUFS

## Le film

Une nuit de septembre, 2 h 16. La CAM 4 filme une rue pavillonnaire endormie.
Un homme rentre chez lui. Au bout de la rue, une silhouette immobile le regarde marcher.
À l'intérieur (CAM 2), pendant qu'il pose ses clés, une forme humaine se tient une
fraction de seconde dans l'encadrement de la porte du couloir — puis plus rien.
Dehors, la silhouette s'est rapprochée du portail, immobile. L'homme se retourne :
personne. La lumière grésille. Et quand la caméra revient sur la rue : vide.
Un visage colle alors l'objectif, quatre frames, puis le noir.
Après une demi-seconde de silence, une voix désincarnée murmure : « Antonin… »

Le twist tient en une phrase : **cette personne n'est jamais entrée.**

## Découpage (29,0 s)

| t | plan | contenu |
|---|------|---------|
| 0,0–0,9 | CAM 4 | rue vide (le même plan reviendra à la fin) |
| 0,9–5,0 | CAM 4 | l'homme marche ; silhouette au bout de la rue (hook < 1 s) |
| 5,0–9,0 | CAM 4 | zoom numérique lent sur la silhouette |
| 9,0–11,6 | CAM 2 | intérieur : l'homme pose ses clés |
| 11,6–12,2 | CAM 2 | **flash 0,6 s : une forme dans l'encadrement de la porte** |
| 12,2–14,0 | CAM 2 | retour intérieur, plan resserré |
| 14,0–16,6 | CAM 4 | la silhouette est maintenant au portail, immobile |
| 16,6–19,2 | CAM 2 | l'homme se retourne : personne ; **flicker lumineuse à 18,3 s** |
| 19,2–21,6 | CAM 2 | plan resserré, silence |
| 21,6–24,0 | CAM 4 | resserré sur le portail : toujours là |
| 24,0–26,0 | CAM 4 | rue vide, bursts glitch |
| 26,0–26,16 | CAM 4 | **4 frames : un visage colle l'objectif** |
| 26,16–26,5 | CAM 4 | retour normal |
| 26,5–29,0 | — | noir ; silence 0,5 s ; murmure « Antonin… » |

## Son

- Voix off française chuchotée (5 répliques) + murmure final détimbré (pitch −3,5 demi-tons,
  tremolo, écho) — voix auditionnées puis choisies par l'utilisateur.
- Nappes synthétisées en pur Python (`data/short-02/build_audio.py`, sans numpy) :
  vent + trafic lointain + hum 50 Hz, grondement infra-grave progressif,
  battement de cœur 58→74 BPM montant de 5 s à 26,5 s, respiration faint,
  bursts numériques sur les cuts, grésillement de néon sur le flicker.
- Mix loudnorm −14 LUFS, TP −1,9 dBTP (mesuré −14,7 LUFS intégré sur le master).
- **Aucun sous-titre** : le brief interdit captions/subtitles — tout passe par le son.

## Image

- 9 visuels générés (style vidéosurveillance : bruit numérique, banding, optique grand
  angle bas de gamme) + 4 éditions image→image pour verrouiller la continuité
  (même rue, même salon).
- Bande d'overlay incrustée par le générateur recadrée ; overlay DVR recréé en ASS
  (ce build ffmpeg n'a pas `drawtext`) : horodatage défilant `27-09-2026 02:16:58 →
  02:17:27`, labels `CAM 4` / `CAM 2` selon la source, point REC clignotant,
  tous coupés au cut-to-black.
- Mouvements : zoompan (push-in lents, zoom numérique accéléré sur la silhouette,
  micro-shake sinusoïdal façon caméra fixée).
- Grade : eq (contraste/saturation froides), flicker lumineuse scriptée à 18,3 s,
  rgbashift (aberration chromatique) sur les fenêtres de glitch, noise temporel,
  vignette.

## Fichiers

| fichier | usage |
|---|---|
| `la-camera-2h17-9x16.mp4` | master upload (16 Mo, CRF 19) |
| `la-camera-2h17-web.mp4` | web / intégration |
| `la-camera-2h17-720p.mp4` | secours |
| `la-camera-2h17-preview-480p.mp4` | preview rapide / partage |
| `cover-1080x1920.jpg` | cover verticale (frame 7,2 s, zoom silhouette) |
| `thumbnail-1280x720.jpg` | thumbnail 16:9 |
| `metadata.json` | titre / description / tags / categoryId (validé `utils/youtube-metadata-validator.js`) |
| `description.txt` | description seule, prête à coller |

## Reproduire

```bash
python3 data/short-02/build_audio.py   # couches son (pur Python)
python3 data/short-02/build.py all     # scènes → mix → final → exports
```

Sources de travail : `data/short-02/` (assets PNG, voix, scripts, mix).

## Provenance & conformité

Fiction horrifique : images, voix et sons entièrement générés pour ce film
(aucune footage réelle, aucune personne réelle). Métadonnées FR validées ;
catégorie 24 (Entertainment) ; pas de contenu choquant graphique ;
le caractère fictionnel est indiqué dans la description.
