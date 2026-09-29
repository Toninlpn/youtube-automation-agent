# Short vertical — « Le distributeur qui vend des souvenirs » 🎟️

Série de **10 images cinématographiques photoréalistes** en **9:16 (1080 × 1920)**, prêtes pour un
TikTok / YouTube Short : thriller surnaturel moderne, tension dès la première seconde, fin en boucle.

> **Statut : 9 images générées sur 10.** La 10ᵉ (« À TON TOUR ») reste à générer — le quota de
> génération d'images du tour a été atteint, la recette de prompt complète est fournie plus bas
> (section « Image 10 ») pour la produire à l'identique.

## 📁 Contenu du dossier

| Fichier | Rôle |
|---|---|
| `images/01…09-*.jpg` | Les images natives générées (941 × 1672, ratio 9:16 exact) |
| `exports-1080x1920/*.jpg` | **Prêtes à monter** : recadrées/extendues en 1080 × 1920, qualité 92 |
| `cover-1080x1920.jpg` | Cover verticale (image 1, le hook) |
| `contact-sheet.jpg` | Planche contact des 9 plans (repérage rapide du découpage) |
| `metadata.json` / `metadata.md` | Titre, description, tags **validés** par le validateur du dépôt |
| `description.txt` | Description YouTube prête à coller |
| `prompts.md` | Les prompts exacts + la recette de continuité personnage/décor |

## ⬇️ Voir / télécharger

| Ressource | Lien direct |
|---|---|
| Planche contact des 9 plans | [contact-sheet.jpg](https://raw.githubusercontent.com/Toninlpn/youtube-automation-agent/arena/01a0eca0-youtube-automation-agent/examples/short-le-distributeur-de-souvenirs/contact-sheet.jpg) |
| Cover verticale 9:16 | [cover-1080x1920.jpg](https://raw.githubusercontent.com/Toninlpn/youtube-automation-agent/arena/01a0eca0-youtube-automation-agent/examples/short-le-distributeur-de-souvenirs/cover-1080x1920.jpg) |
| Dossier des plans natifs | [images/](https://github.com/Toninlpn/youtube-automation-agent/tree/arena/01a0eca0-youtube-automation-agent/examples/short-le-distributeur-de-souvenirs/images) |
| Dossier prêt à monter (1080 × 1920) | [exports-1080x1920/](https://github.com/Toninlpn/youtube-automation-agent/tree/arena/01a0eca0-youtube-automation-agent/examples/short-le-distributeur-de-souvenirs/exports-1080x1920) |
| Prompts + méthode de continuité | [prompts.md](https://raw.githubusercontent.com/Toninlpn/youtube-automation-agent/arena/01a0eca0-youtube-automation-agent/examples/short-le-distributeur-de-souvenirs/prompts.md) |

## 🎬 Découpage (storyboard)

| # | Plan | Image | Rôle narratif | Durée suggérée |
|---|---|---|---|---|
| 1 | **LE HOOK** — main tremblante tenant une Polaroid brûlée : lui de dos, une main pâle sur son épaule, son propre visage terrorisé derrière | `01-hook-polaroid.jpg` | Choc immédiat, < 1 s | 0:00–0:03 |
| 2 | **FLASHBACK** — quai désert, distributeur rouge seul, horloge **03:17**, néons qui clignotent | `02-flashback-quai.jpg` | Titre incrusté « 30 SECONDES PLUS TÔT » | 0:03–0:08 |
| 3 | Il découvre la machine. Écran : « INSÉREZ 1 € — RECEVEZ UN SOUVENIR » | `03-decouverte-machine.jpg` | Mise en place | 0:08–0:14 |
| 4 | Très gros plan : la pièce d'1 € dans la fente rouillée, doigts qui tremblent | `04-piece-euro.jpg` | Tension maximale | 0:14–0:19 |
| 5 | La machine s'active, la 1ʳᵉ Polaroid sort, il la saisit | `05-premiere-photo.jpg` | Bascule surnaturelle | 0:19–0:26 |
| 6 | La photo : le quai **plein de monde**, l'enfant (lui) tient la main d'une femme floue en blanc, horloge à **03:17** | `06-photo-enfant.jpg` | Révélation du souvenir | 0:26–0:31 |
| 7 | Il observe la photo, troublé — reflet discret de la femme en blanc dans la vitre sale | `07-reflet-femme.jpg` | Frisson rétrospectif | 0:31–0:36 |
| 8 | La machine s'active **seule**, 2ᵉ photo qui s'imprime | `08-machine-seule.jpg` | Montée d'angoisse | 0:36–0:40 |
| 9 | **RETOUR AU PRÉSENT** — il comprend : la main sur son épaule, maintenant | `09-prise-de-conscience.jpg` | Climax | 0:40–0:45 |
| 10 | **BOUCLE** — quai vide, 3ᵉ photo au sol, écran « À TON TOUR » | `_à générer_` | Retour au plan 1 | 0:45–0:50 |

## 🎨 Style visuel (constant sur les 10 plans)

- Thriller surnaturel photoréaliste, étalonnage **rouge sombre + cyan froid**, contraste élevé
- Objectif anamorphique, faible profondeur de champ, **grain 35 mm subtil**, lumière volumétrique
- **Espace négatif sombre réservé en haut et au centre** de chaque cadre pour les sous-titres
- Deux pivots visuels récurrents : le **distributeur rouge** (borne vintage bombée) et l'**horloge 03:17**
- Aucun gore, aucune déformation, aucun filigrane, aucun texte parasite (seuls les textes voulus :
  « INSÉREZ 1 € — RECEVEZ UN SOUVENIR » et « À TON TOUR »)

## 👤 Continuité du personnage

**Jeune homme français de 24 ans**, cheveux noirs mi-longs **légèrement bouclés**, barbe naissante,
peau olive, yeux marron foncé, silhouette fine — **manteau beige (camel) sur sweat col rond gris chiné**.
Le même visage et les mêmes vêtements dans les plans 1, 3, 5, 7 et 9.

## 🛠️ Fabrication

Les images ont été produites image par image, **en passant les plans déjà validés comme références**
(image-to-image) pour verrouiller le visage, les vêtements, la machine et le décor :

1. Plan 2 (décor quai + machine) puis plan 3 (révélation du personnage) générés en premier — ce sont les références maîtresses.
2. Chaque plan suivant référençait le plan 3 + le plan 1 (Polaroid brûlée) ou le plan 6 (photo imbriquée).
3. Export final : `convert image.jpg -resize 1080x1920^ -gravity center -extent 1080x1920 -quality 92`.

Les prompts exacts et la méthode sont dans `prompts.md`.

## ⚙️ Spécifications de montage conseillées

- **Vidéo** : 1080 × 1920 (9:16), 30 fps, H.264, ~10 Mbps, `+faststart`
- **Rythme** : coupe toutes les 2–4 s, **hook ≤ 1 s** (plan 1 en plein cadre, sans fondu d'entrée)
- **Mouvement** : Ken Burns lent (zoom 100 → 108 %) + micro-tremblement sur les plans 1, 8, 9
- **Transitions** : *flash rouge* entre 2 et 3, *cut sec* sur 8 (l'activation seule doit surprendre),
  *fondu au noir 6 images* sur 10 pour boucler proprement vers le plan 1
- **Sous-titres** : zone basse sûre (y ≈ 1150 / 1920), police type Anton, contour noir 8–9 px, apparition en fondu
- **Son** : nappe grave + pulsation cardiaque qui accélère, **silence total de 0,5 s** juste avant le plan 8,
  bourdonnement électrique sur le plan 10

## 🚀 Publication

1. Monter les 10 plans selon le tableau (exports `exports-1080x1920/`)
2. YouTube Studio → **Créer → Importer une vidéo** → lire `metadata.md`
3. Titre + `description.txt` + tags, catégorie **Divertissement**, langue **Français**
4. Sous-titres `.srt` importés, puis **« Non, ce n'est pas une vidéo pour enfants »** → Publier

> ⚠️ Le dépôt AgentTube bloque la publication automatique tant que les droits et la relecture humaine
> ne sont pas confirmés. Vérifie simplement que les visuels te conviennent avant publication.
