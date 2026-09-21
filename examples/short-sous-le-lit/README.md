# YouTube Short — « Sous le lit » 🕯️

Short vertical français de **44,8 secondes**, histoire originale, voix off grave traitée et musique originale.

## 📁 Le fichier à publier

| Fichier | Usage |
|---|---|
| **`short-sous-le-lit-9x16.mp4`** | ✅ **Le Short final** — à uploader (56 Mo, qualité max) |
| `short-sous-le-lit-web.mp4` | Version 1080p allégée pour le streaming (11 Mo) |
| `short-sous-le-lit-720p.mp4` | Version mobile rapide (4 Mo) |
| `samples/voix-a…d.mp3` | 4 variantes de la voix pour comparer |
| `short-sous-le-lit-fr.srt` | Sous-titres français (français parlé, à joindre sur YouTube) |
| `thumbnail-1280x720.jpg` | Miniature 16:9 (optionnelle pour un Short) |
| `cover-1080x1920.jpg` | Cover verticale 9:16 (utilisable en miniature ou en post) |
| `description.txt` | Description YouTube prête à coller |
| `metadata.json` / `metadata.md` | Titre, description, tags validés par le validateur d'AgentTube |

## ⬇️ Télécharger

Les fichiers sont versionnés sur la branche `arena/01a0c5c6-youtube-automation-agent`.

| Fichier | Poids | Lien de téléchargement direct |
|---|---|---|
| **Master 1080p** (à uploader sur YouTube) | 54 Mo | [telecharger](https://raw.githubusercontent.com/Toninlpn/youtube-automation-agent/arena/01a0c5c6-youtube-automation-agent/examples/short-sous-le-lit/short-sous-le-lit-9x16.mp4) |
| Web 1080p (streaming) | 11 Mo | [telecharger](https://raw.githubusercontent.com/Toninlpn/youtube-automation-agent/arena/01a0c5c6-youtube-automation-agent/examples/short-sous-le-lit/short-sous-le-lit-web.mp4) |
| Mobile 720p | 3,9 Mo | [telecharger](https://raw.githubusercontent.com/Toninlpn/youtube-automation-agent/arena/01a0c5c6-youtube-automation-agent/examples/short-sous-le-lit/short-sous-le-lit-720p.mp4) |
| Sous-titres FR | 1 Ko | [telecharger](https://raw.githubusercontent.com/Toninlpn/youtube-automation-agent/arena/01a0c5c6-youtube-automation-agent/examples/short-sous-le-lit/short-sous-le-lit-fr.srt) |

Dossier complet : [examples/short-sous-le-lit](https://github.com/Toninlpn/youtube-automation-agent/tree/arena/01a0c5c6-youtube-automation-agent/examples/short-sous-le-lit)

## 📖 L'histoire (thème « frisson + twist émotionnel »)

> « Je n'ai jamais eu qu'une seule règle dans la vie : ne jamais regarder sous le lit de ma chambre d'enfance. Ma mère me l'a répété jusqu'à sa mort. Alors quand j'ai dû vider la maison, seul, une lampe torche à la main, ma main tremblait. J'ai éclairé sous le lit. Rien du tout. Juste une boîte en bois : des lettres, une montre, et une photo de mon père. Première ligne : *Pardon, je n'ai jamais su revenir.* Ma mère ne cachait pas un monstre. Elle protégeait son amour. Et vous, qu'est-ce qui dort sous votre lit ? »

Structure de rétention : **hook (0–8 s) → montée de tension (8–28 s) → révélation (28–36 s) → question finale ouverte + outro musical (36–45 s)**.

## 🎬 Découpage

| Temps | Image | Texte à l'écran | Narration |
|---|---|---|---|
| 0:00–0:08 | Couloir, chambre entrouverte | NE JAMAIS REGARDER SOUS LE LIT | La règle |
| 0:08–0:13 | Mains mère/enfant | MA MÈRE ME L'A RÉPÉTÉ JUSQU'À SA MORT | L'interdit |
| 0:13–0:18 | Maison sous la pluie | J'AI DÛ REVENIR DANS CETTE MAISON | Le retour |
| 0:18–0:28 | Sous le lit, boîte | J'AI ÉCLAIRÉ SOUS LE LIT | Le moment de vérité |
| 0:28–0:36 | Boîte ouverte | JUSTE UNE BOÎTE EN BOIS | La découverte |
| 0:35–0:36 | Homme dans la lumière | ELLE PROTÉGEAIT SON AMOUR | La révélation |
| 0:36–0:45 | Chambre à l'aube (fondu) | QU'EST-CE QUI DORT SOUS VOTRE LIT ? | Le CTA + outro musical |

## 🛠️ Caractéristiques techniques

- **Vidéo** : 1080 × 1920 (9:16), 30 fps, H.264, ~10 Mbps, `+faststart`
- **Audio** : AAC 192 kbps, 48 kHz, stéréo
- **Loudness** : **-14,4 LUFS intégré**, true peak **-1,5 dBFS** (norme YouTube)
- **Chaîne voix** : pitch -7 %, EQ (+5 dB à 105 Hz, -2,5 dB à 3,4 kHz), compression, reverb courte, limitateur
- **Équilibre** : voix ~14 dB au-dessus de la nappe, ducking de la musique sous la voix (ratio 6, release 520 ms)
- **Montage** : fondus de 0,3 s entre chaque plan, Ken Burns (zoom lent), grain de film, vignettage, étalonnage contraste/saturation
- **Musique** : nappe grave + pulsation cardiaque, **ducking automatique** sous la voix (sidechain compressor) puis normalisation
- **Voix off** : voix masculine grave, pitch abaissé de 7 %, EQ +5 dB à 105 Hz, creux à 3,4 kHz, compression et reverb courte de pièce
- **Captions** : police Anton, contour noir 9 px, zone basse sure (y = 1150 sur 1920), apparition/disparition en fondu

## ⚙️ Reproductibilité

Le pipeline complet est scripté et rejouable :

```bash
# Depuis la racine du dépôt — montage complet
python3 data/scripts/short-01/build.py

# Rendu avec la voix grave et sa chaîne de traitement sombre
cd data/scripts/short-01
SHORT_TMP=$PWD/tmp-dark VO_PREFIX=d VO_FX=dark RESUME=1 \
  python3 build.py captions scenes vo music mix final srt

node data/scripts/short-01/metadata.js   # validation + export des métadonnées YouTube
```

Variables d'environnement : `VO_PREFIX` (`v` = voix d'origine, `d` = voix grave),
`VO_FX` (`natural` / `dark`), `SHORT_TMP`, `RESUME=1` (conserve les scènes déjà rendues).

Le script `build.py` lit les images dans `data/assets/short-01/`, la voix dans `data/audio/short-01/`
et écrit le Short dans `data/videos/short-01/`. Il utilise le validateur du dépôt
(`utils/youtube-metadata-validator.js`) pour contrôler titre, description et tags.

## 🚀 Publier sur YouTube

1. YouTube Studio → **Créer → Importer une vidéo** → `short-sous-le-lit-9x16.mp4`
2. Titre : `Ne regarde JAMAIS sous ce lit 😨 #shorts` (le `#shorts` suffit à déclencher le format vertical)
3. Coller `description.txt`, ajouter les tags depuis `metadata.md`, catégorie **Divertissement**, langue **Français**
4. Options avancées → **Ajouter des sous-titres → Importer un fichier** → `short-sous-le-lit-fr.srt`
5. Public : « Non, ce n'est pas une vidéo pour enfants » → Publier

> ⚠️ Le dépôt AgentTube bloque la publication automatique tant que les droits et la relecture humaine
> ne sont pas confirmés. Ici, les visuels et la musique sont générés pour cette vidéo : vérifie simplement
> que la musique convenue te convient avant publication.
