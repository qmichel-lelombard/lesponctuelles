# Suivi du quiz (fonctions Netlify)

- `functions/track.mjs` : `POST /api/track`, enregistre sans donnée personnelle les parties lancées/terminées (avec score) et les clics, plus les inscriptions au tirage (prénom + e-mail) dans Netlify Blobs (store `quiz`).
- `functions/stats.mjs` : `GET /api/stats`, réservé à la page `/admin/`. Le jeton d'accès est transmis dans l'en-tête `x-admin-token` ; seul son hash SHA-256 est dans le code (`TOKEN_SHA256`).
- Page d'administration : `https://duco-bouh.netlify.app/admin/#<jeton>` (non référencée, `noindex`).

Changer le jeton : générer un nouveau jeton, calculer `printf '%s' "<jeton>" | sha256sum`, remplacer `TOKEN_SHA256` dans `stats.mjs`, puis redéployer.

Déploiement manuel (hors intégration Git) : `npm install` à la racine, puis
`netlify deploy --prod --site duco-bouh --dir quiz-ducobu --functions netlify/functions --no-build`.
