# Prompts de génération — « La caméra a filmé quelqu'un qui n'était pas là »

Visuels : generate_image (9:16, style vidéosurveillance). Points communs à tous les prompts
extérieurs : rue pavillonnaire française de nuit, lampe sodium, caméra fixe en hauteur,
bruit numérique, banding, artefacts JPEG, optique grand angle bas de gamme,
« photorealistic real security footage, no text, no letters, no numbers, no watermark ».
Points communs intérieurs : salon modeste vu d'un angle de plafond, canapé beige,
table basse, lampe chaude unique, porte de couloir sombre à droite, même consigne
« no text / no overlay ».

## Générations

- `ext01_street_empty_wide.png` — rue vide vue large (alternante, non montée).
- `ext02_man_walking_silhouette_far.png` — homme veste bleu marine marchant de dos sur le
  trottoir de gauche ; **silhouette humaine immobile, minuscule, au bout de la rue sous le
  lampadaire** ; voiture argent garée à droite.
- `ext03_man_at_door_silhouette_closer.png` — même rue, angle plus haut ; l'homme à sa porte
  (clé) au premier plan gauche ; **silhouette floue debout au milieu de la chaussée**.
- `ext04_silhouette_at_gate.png` — silhouette au portail (alternante, remplacée par ext08).
- `ext05_street_empty_again.png` — rue vide (alternante, remplacée par ext07).
- `ext06_face_at_lens.png` — **visage ordinaire d'homme très près de l'objectif**, regard
  neutre décalé, reflet IR dans les yeux, distortion grand angle, noir & blanc type IR,
  « deeply unsettling but ordinary ».
- `int01_livingroom_man_keys.png` — intérieur homme penché sur la console (alternante,
  remplacée par int04).
- `int02_livingroom_figure_doorway.png` — intérieur, homme marchant vers le couloir ;
  **forme humaine pâle à peine détachée de l'ombre dans l'encadrement de la porte sombre**,
  visage dans le noir, subtil et facile à rater.
- `int03_man_turning_empty.png` — homme se retournant (alternante, remplacée par int05).

## Éditions image→image (continuité)

- `ext07_street_empty_match.png` ← ext02 : « remove every person… street completely empty…
  keep absolutely everything else identical ».
- `ext08_silhouette_at_house.png` ← ext02 : « remove the walking man ; the motionless
  silhouette now stands in the near foreground bottom-left against the house gate, about one
  third of frame height, hooded, face in shadow, not a monster ; everything else identical ».
- `int04_man_keys_match.png` ← int02 : « same room… man stands still at the console table
  with the lamp on the left, seen from above and behind, putting his keys down ; doorway
  empty ».
- `int05_man_turning_match.png` ← int02 : « same room… man stopped mid-room turning head and
  shoulders toward the dark hallway doorway, tense three-quarter profile ; doorway empty ».

## Voix (add_voice puis generate_speech)

- Narrateur (voice-01, fr, narration tendue chuchotée) :
  1. « Cette caméra a enregistré quelque chose que personne n'a vu cette nuit-là. »
  2. « À deux heures dix-sept, il est rentré chez lui. »
  3. « Mais regardez bien derrière lui. »
  4. « Le problème… »
  5. « c'est que cette personne n'est jamais entrée. »
- Entité (voice-02, fr, timbre creux) : « Antonin… » → post-traitement
  `asetrate=38400,aresample=48000,atempo=1.10,highpass=180,lowpass=1500,tremolo=f=6.5:d=0.55,aecho,volume=0.14`
  (distant, désincarné, presque trop bas).

## Notes techniques utiles

- Le générateur incruste souvent son propre overlay CCTV (CAM/REC/timestamp) : recadrage
  des 9,5 % supérieurs (`crop=700:1245:34:131`) puis recréation de l'overlay en ASS
  (`build.py:write_ass`) car ce build ffmpeg n'a pas `drawtext`.
- Centres de zoom mesurés par luminance (blob darkest/lightest) — voir table SHOTS.
