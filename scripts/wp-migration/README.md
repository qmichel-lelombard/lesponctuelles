# Migration lesponctuelles.com -> lesponctuelles.be + WooCommerce

Boîte à outils pour copier une sélection d'articles depuis
`lesponctuelles.com` vers un nouveau site WordPress `lesponctuelles.be`, puis
installer une boutique WooCommerce sur ce nouveau site.

Ces scripts ne s'exécutent pas depuis cet environnement (pas d'accès réseau
vers les deux sites depuis ici) : ils sont prévus pour être lancés depuis
votre poste ou un serveur ayant accès aux deux domaines.

## Prérequis

- `lesponctuelles.be` doit déjà être une installation WordPress fonctionnelle
  (hébergement + DNS + WordPress installés). Ces scripts ne font pas cette
  partie.
- Python 3.9+ avec les dépendances : `pip install -r requirements.txt`
- Sur `lesponctuelles.be` : un compte WordPress avec les droits nécessaires
  (Auteur/Éditeur/Admin) et un **Application Password** créé dans
  wp-admin > Utilisateurs > Profil > "Mots de passe d'application". Ne jamais
  utiliser le mot de passe du compte lui-même.
- `lesponctuelles.com` doit exposer son API REST publique (c'est le cas par
  défaut sur WordPress, sauf si un plugin de sécurité la bloque) — aucune
  authentification n'est nécessaire côté source puisqu'on ne lit que du
  contenu déjà public.
- Pour l'étape WooCommerce : accès SSH au serveur de `lesponctuelles.be` avec
  [WP-CLI](https://wp-cli.org/) installé. Si le SSH n'est pas disponible
  (hébergement mutualisé sans cette option), installez et configurez
  WooCommerce manuellement depuis wp-admin (Extensions > Ajouter >
  WooCommerce > Activer, puis suivre l'assistant de configuration) — le
  script `setup_woocommerce.sh` reste utile comme aide-mémoire des réglages
  à vérifier.
- Pour l'export/import des **produits** (étape 4) : l'API WooCommerce exige
  une authentification même en lecture, donc un Application Password est
  aussi nécessaire côté `lesponctuelles.com`, pour un compte ayant la
  capacité `manage_woocommerce`.

## 1. Exporter une sélection d'articles depuis lesponctuelles.com

```bash
python3 export_posts.py --source https://lesponctuelles.com \
    --category nom-de-la-categorie \
    --output-dir ./export
```

Filtres disponibles (combinables) :
- `--category <slug>` : uniquement les articles d'une catégorie
- `--tag <slug>` : uniquement les articles d'un tag
- `--slugs a,b,c` : liste explicite d'articles par slug (prioritaire sur les
  filtres ci-dessus)
- `--after YYYY-MM-DD` / `--before YYYY-MM-DD` : plage de dates de
  publication

Résultat : un fichier `.json` par article dans `./export/`, plus les images
(image mise en avant + images du corps de texte) dans `./export/media/`.

**Limite connue** : l'API REST publique ne renvoie que le HTML rendu du
contenu (pas le code source des blocs Gutenberg). Les articles importés
seront donc modifiables comme du contenu WordPress classique, mais certains
blocs réutilisables ou shortcodes spécifiques au thème d'origine pourront
apparaître comme du HTML brut à retravailler après import.

## 2. Importer la sélection sur lesponctuelles.be

```bash
export WP_DEST_USER="votre-identifiant"
export WP_DEST_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"

python3 import_posts.py --dest https://lesponctuelles.be \
    --input-dir ./export --status draft
```

- Les articles sont créés en **brouillon** par défaut (`--status draft`) :
  relisez-les dans wp-admin avant de les publier. Utilisez
  `--status publish` uniquement si vous êtes sûr du résultat.
- Les catégories/tags sont recherchés par nom sur le site de destination et
  créés automatiquement s'ils n'existent pas.
- Les images sont re-téléversées dans la médiathèque du site de destination
  (elles ne pointent pas vers lesponctuelles.com).
- Un article dont le slug existe déjà sur `lesponctuelles.be` est ignoré,
  sauf si vous passez `--overwrite`.
- Un fichier `import_log.json` est généré avec la correspondance
  ancien lien -> nouveau lien, utile pour mettre en place des redirections
  ou un lien canonique plus tard.

## 3. Installer WooCommerce sur lesponctuelles.be

Sur le serveur de `lesponctuelles.be` (via SSH), dans le dossier WordPress :

```bash
./setup_woocommerce.sh
```

Le script installe et active WooCommerce, et règle les bases (pays: BE,
devise: EUR, séparateurs de prix). Il affiche ensuite la liste des étapes à
finaliser manuellement dans wp-admin (paiement, livraison, TVA, pages
légales obligatoires, thème, produits) — voir la sortie du script pour le
détail.

## 4. Copier des produits WooCommerce de lesponctuelles.com vers lesponctuelles.be

À faire une fois WooCommerce actif sur `lesponctuelles.be` (étape 3).

```bash
export WP_SOURCE_USER="votre-identifiant-sur-.com"
export WP_SOURCE_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"

python3 export_products.py --source https://lesponctuelles.com \
    --output-dir ./export-products
```

Filtres disponibles : `--category <slug>` (catégorie de produit),
`--skus a,b,c` (liste précise de références). Sans filtre, tous les produits
publiés sont exportés. Le résultat inclut les images, les catégories/tags,
et pour les produits variables (déclinaisons) leurs attributs et variations.

Puis import (réutilise les mêmes `WP_DEST_USER` / `WP_DEST_APP_PASSWORD` que
pour les articles, à condition que ce compte ait la capacité
`manage_woocommerce`) :

```bash
python3 import_products.py --dest https://lesponctuelles.be \
    --input-dir ./export-products --status draft
```

- Comme pour les articles, les produits sont créés en **brouillon** par
  défaut : vérifiez prix, stock, images et déclinaisons dans wp-admin avant
  de passer en `publish`.
- Un produit dont le SKU (ou, à défaut, le slug) existe déjà sur la
  destination est ignoré, sauf `--overwrite`.
- Un `import_log.json` est généré dans `./export-products/` avec la
  correspondance ancien lien -> nouveau lien.

**Limite connue** : les avis produits (reviews) et l'historique des ventes
ne sont pas repris — seuls la fiche produit, les prix, le stock, les
catégories/tags, les images et les déclinaisons le sont.

## 5. Publier en masse les articles/produits importés

Une fois la relecture faite, plutôt que de publier un par un dans wp-admin,
`publish_from_log.py` republie en masse tout ce qui est listé dans un
`import_log.json` (généré par `import_posts.py` ou `import_products.py`) :

```bash
python3 publish_from_log.py --dest https://lesponctuelles.be \
    --log ./export/import_log.json --type post

python3 publish_from_log.py --dest https://lesponctuelles.be \
    --log ./export-products/import_log.json --type product
```

`--status` accepte aussi `draft`/`pending`/`private` si vous voulez repasser
en arrière.

## Points d'attention SEO / légaux

- Publier le même contenu sur deux domaines crée du contenu dupliqué. Pensez
  à ajouter une balise `rel="canonical"` vers `lesponctuelles.be` sur les
  nouveaux articles, ou à ajuster votre stratégie de contenu (contenu
  résumé + lien vers l'original, redirections, etc.) selon l'usage prévu du
  nouveau site.
- Un site marchand belge doit afficher des CGV, une politique de
  confidentialité (RGPD), une politique de cookies, et respecter le délai de
  rétractation de 14 jours — voir la liste affichée en fin de
  `setup_woocommerce.sh`.
