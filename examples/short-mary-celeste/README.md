# Short vertical — « Le mystère du Mary Celeste » 🚢

Short **9:16 de 50,6 secondes** pour TikTok / YouTube Shorts : reconstitution cinématographique de
l'affaire du *Mary Celeste* (1872), racontée comme un **mystère historique non résolu**.

## 📁 Le fichier à publier

| Fichier | Usage |
|---|---|
| **`short-mary-celeste-9x16.mp4`** | ✅ **le Short final** — 1080×1920, 30 fps, 50,6 s, ~10 Mbps, 64 Mo |
| `short-mary-celeste-fr.srt` | sous-titres français synchronisés |
| `cover-1080x1920.jpg` | cover verticale |
| `thumbnail-1280x720.jpg` | miniature 16:9 |
| `description.txt` | description YouTube prête à coller |
| `metadata.json` / `metadata.md` | titre, tags, paramètres techniques |

## 🎬 Découpage (19 plans, nouveau visuel toutes les 1 à 3 s)

| Temps | Plan | Texte à l'écran | Narration |
|---|---|---|---|
| 0:00–0:03 | Vue aérienne, zoom rapide vers le navire | **UN BATEAU A ÉTÉ RETROUVÉ… SANS PERSONNE À BORD.** | « Imaginez découvrir un bateau en pleine mer… » |
| 0:03–0:07 | Vagues sur la coque (cut punch) | — | « …mais sans aucun membre d'équipage. » |
| 0:05–0:10 | Les marins abordent en canot | — | « En 1872, un navire est retrouvé dérivant… » |
| 0:10–0:14 | Pont vide, affaires abandonnées | — | « Mais quelque chose ne va pas. » |
| 0:14–0:22 | Cale, barils d'eau, provisions | — | « Le bateau est encore en état de naviguer… » |
| 0:23–0:28 | Cabine du capitaine, carte de navigation | — | « Mais les dix personnes à bord ont disparu. » |
| 0:28–0:32 | Emplacement du canot vide | — | « Leur canot de sauvetage manque également. » |
| 0:32–0:41 | Tempête, vagues, retours cabine/océan | — | « Tempête ? Erreur de jugement ? Peur d'une catastrophe ? » |
| 0:41–0:50 | Le navire seul au coucher du soleil, la caméra s'éloigne | **TOI, TU AURAIS QUITTÉ LE NAVIRE ?** | « Plus de 150 ans plus tard… » |

## 🛠️ Caractéristiques techniques

- **Vidéo** : 1080 × 1920 (9:16), 30 fps, H.264 High, ~10 Mbps, `+faststart`
- **Audio** : AAC 192 kbps, 48 kHz stéréo — **-14,1 LUFS** intégré, true peak **-1,0 dBFS**
- **Voix off** : masculine française, pitch -5 %, EQ, compression, reverb courte, rythme accéléré ×1,03
- **Design sonore** : impact basse à l'accroche et à la révélation, tonnerre, houle, vent, grincements du bois, montée de tension (riser)
- **Étalonnage** : contraste +6 %, saturation -22 %, balance vers le bleu, vignettage, grain léger
- **Sous-titres** : gras 62 px, mots clés en doré, fondus d'apparition

## 🔧 Reproduction

Tout est reproductible depuis `production/` :

```bash
cd examples/short-mary-celeste/production
python3 render_texts.py   # calques de texte (PIL)
python3 build_bed.py      # design sonore (numpy -> bed.wav)
python3 assemble.py       # plans Ken Burns, dissolves, étalonnage, mix, rendu final
```

Dépendances : `imageio-ffmpeg`, `pillow`, `numpy`. Les images sources sont dans `production/images/`,
les voix off dans `production/audio/`, la timeline (plans, sous-titres, events sonores) dans `production/timeline.py`.

## ⚠️ Note

Le dossier `production/work/` contient les fichiers de travail ; les gros intermédiaires sont
supprimés automatiquement en fin de montage.
