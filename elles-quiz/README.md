# ELLES – « Quelle Elle se cache en toi ? »

Test de personnalité en ligne (12 questions, ~5 min, mobile + PC) qui rattache le joueur à l'une des six
personnalités de la série : **Rose, Blonde, Châtain, Violette, Verte, Bleue**.

Site 100 % statique, sans dépendance ni build : `index.html`, `style.css`, `quiz.js`, dossier `img/`.

## Tester en local
```
cd elles-quiz && python3 -m http.server 8000   # puis http://localhost:8000
```
(la carte « Télécharger ma carte » nécessite d'être servi en http(s), pas en `file://`).

## Mise en ligne
Déposer le dossier tel quel sur n'importe quel hébergement statique (Netlify, serveur Le Lombard, WordPress en iframe…).
Le résultat est partageable via un lien du type `…/index.html#resultat-violette`.

## Où modifier quoi
| Quoi | Où |
|---|---|
| Questions / réponses | `QUESTIONS` dans `quiz.js` (chaque réponse = `[couleur, texte]`, 4 réponses par question) |
| Textes des résultats, mantra, alliée | `ELLES` dans `quiz.js` |
| Couleurs | variables `:root` de `style.css` |
| Lien d'achat | bouton `#buy` dans `index.html` |

## Scoring
Chaque réponse rapporte 3 points à une couleur. Chaque couleur est proposée en « bonne réponse » exactement 8 fois sur 12
(ordre des réponses mélangé à chaque affichage). Égalité : la couleur choisie le plus récemment l'emporte.
Le résultat affiche la couleur dominante, la couleur cachée (2ᵉ) et le mélange en pourcentages.

## Visuels
Aucun dessin n'a été créé ni modifié : uniquement des recadrages et détourages des fichiers fournis
(`tools/prepare_assets.py`). Les détourages des six Elles sont **provisoires** (issus d'un visuel de groupe
de faible définition) : à remplacer par les PNG détourés HD en gardant les noms `img/rose.webp`, `blonde.webp`,
`brune.webp`, `violette.webp`, `verte.webp`, `bleue.webp` (+ `elles-groupe.webp` pour l'accueil).

## Suivi des participations (page admin)
- Page cachée : `/gestion-elles/` (non liée depuis le site, `noindex`), protégée par mot de passe.
- Le mot de passe est la variable d'environnement Netlify `ADMIN_PASSWORD` (Site configuration → Environment variables) : il n'est jamais dans le code. Pour le changer, modifier la variable puis redéployer.
- Mesure **anonyme** (aucun cookie, aucune IP, aucune donnée personnelle) : démarrages, résultats obtenus, clics sur « Découvrir le tome 4 », encart couverture, « Partager », « Télécharger ma carte », « Refaire le test », « Découvrir la série », ouvertures de liens partagés.
- Fonctions : `netlify/functions/track.mjs` (enregistre) et `stats.mjs` (agrège, protégée). Stockage : Netlify Blobs.
- Déploiement (fonctions incluses) : `cd netlify && npm install` puis `NETLIFY_SITE_ID=… python3 tools/deploy_netlify.py`.
