# Métadonnées YouTube — « Le distributeur qui vend des souvenirs »

Validées par le validateur du dépôt (`utils/youtube-metadata-validator.js`) : **`valid: true`**, 0 erreur, 0 avertissement.

| Champ | Longueur | Limite |
|---|---|---|
| Titre | 74 caractères | 100 |
| Description | 682 caractères | 5000 |
| Tags | 200 caractères (14 tags) | 450 (30 max) |

## 📌 Titre

```
Ce distributeur vend des souvenirs… et il t'a déjà photographié 😨 #shorts
```

Variantes testables (A/B) :
- `N'insère JAMAIS de pièce dans ce distributeur 😨 #shorts`
- `Il achète un souvenir à 1 €… il n'aurait pas dû 😨 #shorts`

## 📝 Description

Voir `description.txt` (identique à `metadata.json > description`).

## 🏷️ Tags

```
short fr, frissons, histoire d'horreur, horreur française, mystère, créepy,
distributeur automatique, souvenirs, thriller surnaturel, histoire courte,
photo polaroid, métro abandonné, creepypasta fr, short horreur
```

## ⚙️ Réglages d'upload

| Réglage | Valeur |
|---|---|
| Catégorie | `24` — Divertissement |
| Langue de la vidéo | Français (`fr`) |
| Langue audio par défaut | Français (`fr`) |
| Public | « Non, ce n'est pas une vidéo pour enfants » |
| Visibilité suggérée | Publique, notification aux abonnés |

## 🖼️ Miniatures

- `cover-1080x1920.jpg` — cover verticale (Shorts, posts, TikTok)
- `images/01-hook-polaroid.jpg` — alternative « choc » pour un short hook-first

## ✅ Publication

1. YouTube Studio → **Créer → Importer une vidéo** → le montage 9:16 (1080 × 1920)
2. Coller le titre, puis `description.txt`, puis les tags ci-dessus
3. Ajouter les sous-titres importés (`.srt`) une fois générés
4. **Ne pas** cocher « vidéo pour enfants » → Publier

> ⚠️ Le dépôt AgentTube bloque la publication automatique tant que les droits et la relecture humaine
> ne sont pas confirmés. Vérifie que les images te conviennent avant publication.
