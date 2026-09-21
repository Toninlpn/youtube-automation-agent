# Made with Lumen

This directory is reserved for verified output evidence. Do not add mock videos, simulated runs, or estimated results.

For each example, provide:

```markdown
## Video title

- Niche or prompt:
- Text provider and model:
- Image provider and model:
- TTS provider and model:
- Started at:
- Finished at:
- Elapsed generation time:
- Estimated API cost and calculation source:
- Human editing time:
- Lumen version or commit:
- Final video URL:
- Verification: non-simulated MP4 container signature confirmed
```

The preferred launch gallery contains three materially different niches and preserves truthful failures, retries, and manual edits in the notes.

## Sous le lit — YouTube Short vertical FR (45 s)

- Niche or prompt: histoire courte française, frisson + twist émotionnel (« ne jamais regarder sous le lit »)
- Text provider and model: écriture et storyboard par l'agent Arena (aucun appel API externe)
- Image provider and model: 6 images cinématiques photo-réalistes générées par le modèle d'image d'Arena
- TTS provider and model: voix d'Arena (voix masculine grave), chaine de traitement ffmpeg pitch -7 % + EQ + reverb
- Musique : synthétisée localement avec ffmpeg (nappe grave, pulsation, ambiance) — aucune ressource sous licence externe
- Started at: 2026-09-21 21:01 UTC
- Finished at: 2026-09-21 21:37 UTC
- Elapsed generation time: ~36 min (dont 2 rendus vidéo complets)
- Estimated API cost and calculation source: aucun coût mesuré côté providers (pas de clé API du dépôt utilisée)
- Human editing time: sélection de la voix (2 auditions) puis validation du rendu
- Lumen version or commit: pipeline local `data/scripts/short-01/build.py` sur la branche `arena/01a0c5c6-youtube-automation-agent`
- Final video URL: assets de la release `short-sous-le-lit` de ce dépôt
- Verification: MP4 décodé intégralement sans erreur (`ffmpeg -v error -f null -`), 1080x1920, 30 fps, 44,8 s, H.264 + AAC 48 kHz, loudness -14,4 LUFS / true peak -1,5 dBFS, métadonnées validées par `utils/youtube-metadata-validator.js`

Les trois rendus sont versionnés dans `examples/short-sous-le-lit/` : master 1080p (~10 Mbps, pour l'upload YouTube),
web 1080p allégé (streaming) et mobile 720p. Le retraitement complet se rejoue avec
`data/scripts/short-01/build.py` (variables `VO_PREFIX`, `VO_FX`, `SHORT_TMP`).
