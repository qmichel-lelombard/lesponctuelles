# Contenu "Chauffage" et "Sanitaire" -- guillaumetessaro.be

Boite a outils pour ajouter deux pages dediees (Chauffage, Sanitaire) au site
one-page WordPress de Guillaume Tessaro, avec du texte redige et des photos
placeholder faciles a remplacer ensuite.

Ces scripts ne s'executent pas depuis cet environnement (pas d'acces reseau
vers guillaumetessaro.be depuis ici) : lancez-les depuis votre poste ou un
serveur ayant acces au site.

## Prerequis

- Python 3.9+ avec les dependances : `pip install -r requirements.txt`
- Sur `guillaumetessaro.be` : un compte WordPress avec les droits Auteur /
  Editeur / Admin, et un **Application Password** cree dans wp-admin >
  Utilisateurs > Profil > "Mots de passe d'application". N'utilisez jamais le
  mot de passe du compte lui-meme.

## Utilisation

```bash
export WP_DEST_USER="votre-identifiant"
export WP_DEST_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"

python3 create_pages.py --dest https://guillaumetessaro.be --status draft
```

Le script :
1. Genere dans `media/` six photos placeholder par page (visuels simples,
   avec le sujet ecrit dessus -- pas de vraies photos) si elles n'existent
   pas deja.
2. Televerse ces images dans la mediatheque WordPress.
3. Cree les pages `/chauffage/` et `/sanitaire/` en **brouillon** avec le
   texte de `content/chauffage.html` et `content/sanitaire.html`.

Une page dont le slug existe deja est **ignoree** par defaut. Ajoutez
`--overwrite` pour la mettre a jour (utile si vous relancez le script apres
avoir modifie le texte ou les images) :

```bash
python3 create_pages.py --dest https://guillaumetessaro.be --status draft --overwrite
```

Si le site a deja une page "Services" et que vous voulez y rattacher ces deux
pages comme sous-pages, precisez son slug :

```bash
python3 create_pages.py --dest https://guillaumetessaro.be --parent-slug services
```

## Apres la generation

- Les pages sont creees en **brouillon** : relisez-les dans wp-admin avant de
  passer en `publish`.
- Le script ne touche pas au menu de navigation : ajoutez manuellement des
  liens vers `/chauffage/` et `/sanitaire/` dans Apparence > Menus, et/ou des
  liens "En savoir plus" depuis les sections Chauffage / Sanitaire de la page
  d'accueil actuelle.
- Le bouton de contact en bas de chaque page pointe vers `/#contact` (l'ancre
  de la section contact de la page d'accueil one-page). Adaptez ce lien si
  votre section contact utilise une autre ancre, ou si vous creez une page de
  contact dediee.

## Remplacer les photos placeholder par les vraies photos

Deux options :

1. **Le plus simple** : dans wp-admin > Medias, ouvrez chaque image
   placeholder (nommees `hero-chauffage.jpg`, `chaudiere-condensation.jpg`,
   etc.) et utilisez "Remplacer l'image" / re-televersez la vraie photo
   par-dessus.
2. **Depuis ce script** : deposez vos vraies photos dans `media/` sous
   exactement le meme nom de fichier que le placeholder correspondant (voir
   `pages_config.py` pour la liste des noms attendus), puis relancez
   `create_pages.py --overwrite`. Le script ne regenere jamais un fichier deja
   present dans `media/`, donc vos vraies photos ne seront pas ecrasees.

## Adapter le texte

Le texte de chaque page est dans `content/chauffage.html` et
`content/sanitaire.html`, au format blocs Gutenberg (les commentaires
`<!-- wp:... -->` sont conserves pour rester editables normalement dans
l'editeur WordPress). Les lignes `<!--IMG:cle-->` marquent l'emplacement des
photos et sont remplacees automatiquement par le script -- ne les supprimez
pas, deplacez-les si besoin.

## A verifier avant publication

- **Zone d'intervention** : la liste des villes (Enghien, Silly, Lens, Ath,
  Soignies, Braine-le-Comte, Ecaussinnes, Rebecq, Tubize, Hal, Nivelles,
  Mons...) est une estimation d'un rayon de 50 km autour d'Enghien -- ajustez
  selon les zones que vous couvrez reellement.
- **Entretien legal des chaudieres** : le texte mentionne l'obligation de
  controle periodique en Belgique sans donner de frequence precise (les regles
  different selon combustible et region/organisme agree) -- completez avec
  votre situation exacte si vous le souhaitez.
- **Lien de contact** (`/#contact`) et **coordonnees** (telephone, email) :
  aucune coordonnee n'est inventee dans ce contenu ; verifiez que le bouton de
  contact pointe bien vers la bonne section/page.
