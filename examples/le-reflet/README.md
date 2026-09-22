# LE REFLET — Short YouTube 9:16 (40 s)

Court-métrage d'horreur psychologique vertical, produit de bout en bout dans ce dépôt :
images fixes générées par IA, vrais mouvements de caméra (zoompan/pan/shake), narration
française, sous-titres brûlés, sound design 100 % synthétisé. **Aucune clé de provider
vidéo payante n'a été utilisée** (Seedance/Kling/MiniMax absents du `.env`) — c'est un
animatic cinématographique, pas un clip en mouvement continu.

## Lire / télécharger

| Fichier | Contenu |
|---|---|
| `out/le-reflet-9x16.mp4` | 1080×1920 · 30 fps · 39,97 s · H.264 High + AAC 192 k · ~19,6 Mo · −14 LUFS |
| `out/le-reflet-fr.srt` | 19 sous-titres calés sur la durée réelle de chaque prise de voix |
| `cover-1080x1920.jpg` | vignette 9:16 |
| `metadata.json` / `metadata.md` / `description.txt` | package de publication |
| `img/`, `audio/` | plans et prises de voix (entrées du montage) |
| `render.py`, `derive_frames.py` | le montage, rejouable |

## Découpage (20 plans, changement d'image toutes les 1,8 à 4,9 s)

| Temps | Plan | Décor | Audio |
|---|---|---|---|
| 0,00–2,20 | a_eye | gros plan extrême sur l'œil, push-in | « Un soir, il a remarqué… » |
| 2,20–5,10 | b_wide | reveal du miroir : main levée, reflet immobile | « …quelque chose d'impossible dans son miroir. » |
| 5,10–7,30 | c_stare | le reflet fixe, visage seul dans le verre | « Son reflet avait toujours… » |
| 7,30–9,00 | d_raise | l'homme lève la main lentement, le reflet non | « …deux secondes de retard. » |
| 9,00–9,75 | e1_delay | plan figé = le retard lui-même | (silence, tic-tac) |
| 9,75–11,20 | e2_late | le reflet lève la main, l'homme bras ballants | — |
| 11,20–12,60 | f_stepback | il recule, le reflet reste collé au miroir | « Puis son reflet a commencé… » |
| 12,60–14,60 | g_fear | dos plaqué au carrelage, terreur | « …à faire des choses… » |
| 14,60–16,80 | h_smile | le reflet sourit, lui non, push-in | « …qu'il ne faisait pas. » |
| 16,80–18,60 | i_turn | rotation vers la porte | « Et là… il a compris » |
| 18,60–20,40 | j_doorway | couloir vide, rien | « qu'il n'était pas en train » |
| 20,40–22,20 | k_closer | le reflet bien plus près du verre | « de regarder son reflet. » + boom 20,40 |
| 22,20–24,20 | l_pressed | front et paume plaqués contre la vitre, haleine | chuchotements en fond |
| 24,20–26,20 | m_points | un index désigne l'espace derrière lui | « Il lui montrait quelque chose… » |
| 26,20–28,20 | n_frozen | figé, tête à demi tournée, rien derrière | « derrière lui. » |
| 28,20–30,20 | o_smile_at_him | le reflet lui sourit en face | **1,00 s de silence numérique total (29,3–30,3)** |
| 30,20–32,00 | p_no_reflection | le miroir ne renvoie plus l'homme | boom 30,20 |
| 32,00–34,55 | q_whisper | lèvres contre la vitre | « Maintenant… c'est mon tour. » (voix −2 demi-tons) |
| 34,55–35,10 | r_black | coupure franche + impact | silence |
| 35,10–40,00 | s_empty | salle vide, t-shirt au sol, visage encore dans le miroir | « Et quand la lumière s'est rallumée… il n'était plus là. » |

Le dernier plan recadre sur le miroir exactement comme le premier : **lecture en boucle sans coupure**.

## Rejouer le montage

```bash
pip3 install imageio-ffmpeg          # ou FFMPEG_PATH=/chemin/vers/ffmpeg
python3 derive_frames.py             # fabrique les plans composés manquants
FORCE=1 python3 render.py video      # segments + étalonnage + mix + mux
python3 render.py cues               # inspecte le cahier de sous-titres
```

Tout est déclaratif en haut de `render.py` :

- `SHOTS` : `(clé, image, début, fin, mouvement)` — `zoom`, `pan`, `shake`, `freq`, `black`.
- `VO` : `(fichier wav, instant de pose, style, texte, mots surlignés)` — la **durée est mesurée
  sur le fichier**, donc les sous-titres et le découpage se recalculent si tu réenregistres une prise.
- `ALT` : plan de repli automatique si un `img/v2_*.png` n'a pas pu être généré (budget d'images
  de 10 par tour). Dès que tu génères le vrai `v2_*.png`, `render.py` l'utilise sans rien changer.
- `GRADE` : étalonnage (contraste, courbes, balance teal/ambre, vignette, grain) + clignotements.

## Sound design (ffmpeg seul, aucun échantillon externe)

`anoisesrc` couleur brun filtré à 430 Hz (nappe de pièce) · bourdonnement 100 Hz modulé
(ampoule) · drone 37 Hz qui monte en pow(t,1.4) · lub-dub synthétisé par double impulsion
exponentielle (0,86 s puis 0,52 s de période) · tic-tac 2 300 Hz · deux booms graves à
balayage descendant (20,40 s et 30,20 s) · riser de 8,35 s · chuchotements bruit filtré +
`tremolo` · impact final (34,55 s) · robinet qui goutte sur le dernier plan. Décor ducké de
−10 dB sous la voix, bus voix passeur 85 Hz + EQ 2,7 kHz + réverbération courte.

## Limites connues et prochaine amélioration

1. Six plans (`e1_delay`, `j_doorway`, `k_closer`, `m_points`, `n_frozen`, `o_smile_at_him`)
   réutilisent un plan existant avec un cadrage différent : le plafond de 10 images par tour
   a été atteint. Les générer en `v2_*` suffit à les remplacer.
2. Quatre plans sont composés par `derive_frames.py` (ImageMagick) : buée sur le verre, reflet
   effacé, homme effacé. lisibles sur mobile mais moins nobles qu'un plan dédié.
3. Les visages ne bougent pas : pour un mouvement continu, il faut une clé `VIDEO_PROVIDER`
   (Seedance/Kling/MiniMax/Wan) dans le `.env`, puis repasser la même liste de plans en
   génération vidéo clip par clip.

## Porte de sortie AgentTube

`render.py` écrit un manifest de plans 1:1 avec la convention `scene manifest` du dépôt
(clé, image, horodatage, mouvement, provider). Pour intégrer ce Short au pipeline complet
(gates de qualité, droits, révision, planification), voir `docs/` et le Review Studio du
dashboard ; la publication reste bloquée tant que les gates ne passent pas.
