# Contenu "Chauffage", "Sanitaire", "Contact" et accueil -- guillaumetessaro.be

Boite a outils pour ajouter des pages dediees (Chauffage, Sanitaire,
Contact) au site one-page WordPress de Guillaume Tessaro, avec du texte
redige, une mise en page moderne (hero plein ecran, sections alternees
photo/texte, bandeau zone d'intervention, CTA avec le numero de telephone)
inspiree du logo et de la page d'accueil, et des photos placeholder faciles
a remplacer ensuite. Inclut aussi une reproduction de la page d'accueil en
HTML/CSS simple (page "Accueil (nouvelle version)", slug `nouvel-accueil`),
dans le meme style, pour remplacer a terme la version Elementor actuelle si
vous le souhaitez.

## Design

- **Typo** : titres en Oswald (condensee, gras, majuscules -- comme le logo
  "GUILLAUME TESSARO"), texte courant en Quicksand (arrondie), chargees
  depuis Google Fonts.
- **Couleurs** : noir / blanc / gris, comme la page d'accueil -- variables
  CSS modifiables en haut de `assets/tessaro-pages.css` (`--gt-black`,
  `--gt-white`, `--gt-gray-bg`, `--gt-gray-text`).
- **Structure** : hero plein ecran avec photo + titre, sections alternees
  photo/texte par theme (installation, entretien, depannage...), bandeau
  noir "Zone d'intervention", bandeau final d'appel a l'action.
- Le CSS est integre directement dans le contenu de chaque page (un seul
  bloc `<style>` embarque) : aucune etape manuelle supplementaire, tout est
  pousse par le script.
- Le vrai numero de telephone (0475 30 84 49, releve sur le pied de page du
  site) est utilise dans les boutons d'appel -- verifiez qu'il est toujours
  exact avant publication.

### Important -- Elementor / OceanWP

Le site utilise le theme OceanWP avec la page d'accueil construite sous
Elementor. Ces deux pages sont creees comme des pages WordPress classiques
(le HTML/CSS ci-dessus est mis directement dans le contenu de la page) : ca
fonctionne tres bien tant que vous les editez avec l'editeur natif
(Gutenberg) ou que vous ne touchez pas au contenu. **N'ouvrez pas ces pages
avec "Modifier avec Elementor"** sans le vouloir : Elementor prendrait alors
le controle de l'affichage et remplacerait ce contenu par une page vide a
reconstruire depuis zero. Si vous voulez a terme les reconstruire dans
Elementor pour les editer visuellement, le meme code HTML/CSS peut etre
colle tel quel dans un widget "HTML" Elementor.

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
1. Genere dans `media/` six photos placeholder par page Chauffage/Sanitaire
   (visuels simples, avec le sujet ecrit dessus -- pas de vraies photos) si
   elles n'existent pas deja. La page Contact n'a pas de photo.
2. Televerse ces images dans la mediatheque WordPress.
3. Cree les pages `/chauffage/`, `/sanitaire/` et `/contact/` en
   **brouillon** avec le texte de `content/chauffage.html`,
   `content/sanitaire.html` et `content/contact.html`.

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
  liens vers `/chauffage/`, `/sanitaire/` et `/contact/` dans Apparence >
  Menus, et/ou des liens "En savoir plus" depuis les sections correspondantes
  de la page d'accueil actuelle.
- Les boutons "Appeler" utilisent le numero `tel:+32475308449` ; le bouton
  "Nous contacter" des pages Chauffage/Sanitaire renvoie vers `/contact/`.
  Adaptez ces liens dans les fichiers `content/*.html` si besoin.

## Page Contact et formulaire

La page `/contact/` affiche les coordonnees (telephone, email, adresse,
horaires -- modifiables dans `CONTACT_INFO` en haut de `pages_config.py`)
et un emplacement pour un vrai formulaire de contact. La carte Google Maps
est fournie par le pied de page commun (voir section suivante), affiche en
bas de cette page comme des deux autres.

Ce depot ne peut pas creer le formulaire lui-meme (aucun plugin de formulaire
n'installe de point d'entree API par defaut). Marche a suivre recommandee,
avec **Contact Form 7** (gratuit, le plus repandu, compatible OceanWP) :

1. Dans wp-admin : Extensions > Ajouter > rechercher "Contact Form 7" >
   Installer > Activer.
2. Un premier formulaire est cree automatiquement (menu "Contact" dans la
   barre laterale). Ouvrez-le et adaptez les champs si besoin (Nom, Email,
   Telephone, Message).
3. Dans l'onglet **"Mail"** du formulaire, verifiez/renseignez le champ
   "To:" avec `tessaro.guillaume@hotmail.com` (l'adresse qui doit recevoir
   les messages).
4. Copiez le shortcode affiche en haut de la page (ex:
   `[contact-form-7 id="12" title="Contact form 1"]`).
5. Relancez le script en passant ce shortcode :
   ```bash
   python3 create_pages.py --dest https://guillaumetessaro.be --status draft \
     --overwrite --form-shortcode '[contact-form-7 id="12" title="Contact form 1"]'
   ```
   Vous pouvez aussi coller ce shortcode une fois pour toutes dans
   `CONTACT_FORM_SHORTCODE` (`pages_config.py`) pour ne plus avoir a le
   repasser en argument.

Tant qu'aucun shortcode n'est renseigne, la page Contact affiche un encadre
jaune expliquant que le formulaire n'est pas encore configure -- pas
d'erreur, juste un rappel visuel.

Le CSS de `assets/tessaro-pages.css` habille deja les champs generes par
Contact Form 7 (bordures arrondies, bouton noir assorti au reste du site) ;
si vous utilisez WPForms ou le formulaire natif d'Elementor Pro a la place,
l'apparence de base restera correcte mais un ajustement fin du CSS peut etre
necessaire selon les classes HTML propres a ce plugin.

**Pourquoi le shortcode peut "se perdre" apres une modification manuelle**
dans wp-admin : WordPress "texturise" le contenu (convertit les guillemets
droits `"` en guillemets courbes `" "`) lors de certains passages dans
l'editeur. Si le shortcode `[contact-form-7 id="..." ...]` se retrouve avec
des guillemets courbes, Contact Form 7 ne reconnait plus l'id et affiche
"Erreur : Formulaire de contact non trouve". Pour l'eviter, `create_pages.py`
place desormais le shortcode dans son propre bloc Gutenberg
`<!-- wp:shortcode -->...<!-- /wp:shortcode -->`, le format que WordPress
utilise justement pour proteger un shortcode de ce type de alteration. Si le
probleme revient malgre tout apres une edition manuelle dans wp-admin,
relancez `create_pages.py --overwrite` avec le meme `--form-shortcode` pour
regenerer la page proprement plutot que de corriger a la main dans
l'editeur.

## Ajouter les pages au menu de navigation

`add_menu_links.py` ajoute Chauffage, Sanitaire et Contact au menu de
navigation existant via l'API REST des menus WordPress (natif depuis
WP 5.9) -- pas besoin d'y toucher a la main dans Apparence > Menus.

```bash
python3 add_menu_links.py --dest https://guillaumetessaro.be
```

Sans `--menu-id`, le script liste les menus existants (s'il n'y en a qu'un,
il l'utilise automatiquement). S'il y en a plusieurs, relancez avec l'id
affiche :

```bash
python3 add_menu_links.py --dest https://guillaumetessaro.be --menu-id 3
```

Les pages deja presentes dans le menu sont ignorees (pas de doublon si vous
relancez). Les elements sont ajoutes a la fin : reordonnez-les ensuite dans
Apparence > Menus par glisser-deposer si besoin.

## Page d'accueil actuelle (Elementor) -- liens et bords arrondis

La page d'accueil actuelle est construite avec **Elementor**, qui stocke son
contenu dans un format different (JSON prive `_elementor_data`) des pages
classiques creees par `create_pages.py`. Ce depot ne modifie donc pas cette
page automatiquement -- ce serait trop risque de le faire a l'aveugle par
API sans jamais avoir vu la structure reelle de la page. Ces reglages se
font a la main dans l'editeur Elementor (rapide, quelques clics) :

**Liens vers les pages** : ouvrez la page d'accueil avec Elementor
("Modifier avec Elementor"), cliquez sur chaque bouton/bloc concerne
(section Chauffage du hero, section Sanitaire du hero, bouton "Contact" de
la section a propos), onglet **Contenu > Lien**, et collez l'URL
correspondante :
- `https://guillaumetessaro.be/chauffage/`
- `https://guillaumetessaro.be/sanitaire/`
- `https://guillaumetessaro.be/contact/`

**Bords arrondis** (pour matcher le style des nouvelles pages) : les
boutons utilisent `border-radius: 8px`, les images `border-radius: 10px`
(voir `assets/tessaro-pages.css`). Le plus rapide pour un reglage
coherent sur tout le site : menu hamburger Elementor (en haut a gauche) >
**Parametres du site > Style du theme** :
- Section **Boutons** : Bordure > Rayon = `8px` (tous les cotes).
- Section **Images** (si presente) : Rayon = `10px`.

Si vous preferez ajuster uniquement la page d'accueil sans toucher au style
global : cliquez sur chaque widget Bouton ou Image individuellement, onglet
**Style > Bordure > Rayon**, et entrez la meme valeur.

## Reproduction de l'accueil sans Elementor (page "Accueil (nouvelle version)")

Alternative a la section precedente : `create_pages.py` cree aussi une page
`/nouvel-accueil/` qui reproduit le contenu et la mise en page de l'accueil
actuel (hero scinde Chauffage/Sanitaire avec listes de services et liens
vers les pages dediees, grille de 4 photos + bio "Guillaume Tessaro" +
bouton Contact, meme pied de page commun) mais en HTML/CSS simple, dans le
meme style que les 3 autres pages -- pas besoin de reglages Elementor.

Elle est creee en **brouillon**, sous un slug distinct : elle ne remplace
pas la page d'accueil actuelle tant que vous ne le decidez pas. Comparez les
deux, et si vous preferez cette version :

1. Passez-la en `publish` dans wp-admin (ou relancez le script avec
   `--status publish`).
2. Dans wp-admin > Reglages > Lecture, section "Vos pages affichent" :
   choisissez "Une page statique" et selectionnez "Accueil (nouvelle
   version)" comme page d'accueil.
3. Optionnel : une fois satisfait, vous pouvez supprimer l'ancienne page
   Elementor (ou la laisser en brouillon comme sauvegarde).

Les 6 photos reutilisees dans cette page (2 heros + 4 photos de la grille)
suivent les memes regles que les autres : placeholders generes
automatiquement, remplacables via wp-admin > Medias ou `fetch_stock_photos.py`
(cles `bio-chauffe-eau`, `bio-wc`, `bio-chantier`, `bio-chauffe-eau-2` en
plus de `hero-chauffage`/`hero-sanitaire` deja utilisees ailleurs -- ces deux
dernieres ne sont televersees qu'une fois par execution grace a un cache
interne, pas de doublon dans la mediatheque).

## Pied de page commun (carte + logo + coordonnees + Facebook)

Les trois pages se terminent par le meme pied de page, reproduit de celui
de la page d'accueil : une carte Google Maps plein ecran, puis une barre
avec le logo a gauche, telephone/adresse/horaires au centre, et un lien
Facebook a droite. Il est defini une seule fois dans `content/_footer.html`
et ajoute automatiquement en bas de chaque page par `create_pages.py`
(token `<!--SITE_FOOTER-->`) -- pas besoin de le dupliquer si vous ajoutez
une nouvelle page.

- **Logo** : `FOOTER_LOGO_URL` dans `pages_config.py` pointe vers
  `https://guillaumetessaro.be/wp-content/uploads/2025/08/logo-guillaume.png`.
  Si vous changez de logo, televersez le nouveau fichier dans wp-admin >
  Medias et mettez a jour cette URL (ou passez `--logo-url` en ligne de
  commande). Laissez `FOOTER_LOGO_URL = ""` pour afficher "Guillaume Tessaro"
  en texte a la place, si le fichier n'est pas disponible.
- **Facebook** : `CONTACT_INFO["facebook_url"]` (actuellement
  `https://www.facebook.com/tessaro.guillaume/`). Laissez vide pour ne pas
  afficher l'icone.
- **Carte** : centree sur `FOOTER_MAP_QUERY` (`Chaussée d'Ath, 7850 Enghien`,
  memes reperes que la carte de la page d'accueil), modifiable dans
  `pages_config.py`.

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

## Utiliser des photos libres de droit en attendant les vraies photos

`fetch_stock_photos.py` telecharge des photos depuis des URLs que vous
choisissez (Unsplash, Pexels, Pixabay -- gratuites, usage commercial
autorise, sans attribution obligatoire), les recadre automatiquement en
1200x800 et les depose dans `media/` sous le bon nom de fichier.

1. Ouvrez `fetch_stock_photos.py` et completez le dictionnaire
   `STOCK_PHOTO_URLS` avec l'URL directe du fichier image (pas l'URL de la
   page) pour chaque cle qui vous interesse. Suggestions de recherche :

   | Cle | Fichier | Recherche suggeree |
   |---|---|---|
   | hero-chauffage | hero-chauffage.jpg | "heating technician", "chauffagiste" |
   | chaudiere-condensation | chaudiere-condensation.jpg | "gas boiler installation", "chaudiere murale" |
   | pompe-a-chaleur | pompe-a-chaleur.jpg | "heat pump outdoor unit" |
   | entretien-chaudiere | entretien-chaudiere.jpg | "boiler maintenance technician" |
   | radiateurs | radiateurs.jpg | "radiator installation plumber" |
   | depannage-chauffage | depannage-chauffage.jpg | "emergency heating repair" |
   | hero-sanitaire | hero-sanitaire.jpg | "plumber bathroom", "plombier sanitaire" |
   | installation-sanitaire | installation-sanitaire.jpg | "bathroom plumbing installation" |
   | renovation-sdb | renovation-sdb.jpg | "bathroom renovation" |
   | chauffe-eau | chauffe-eau.jpg | "water heater installation" |
   | depannage-plomberie | depannage-plomberie.jpg | "plumber fixing leak" |
   | robinetterie | robinetterie.jpg | "faucet installation bathroom" |

2. Lancez :
   ```bash
   python3 fetch_stock_photos.py
   python3 create_pages.py --dest https://guillaumetessaro.be --status draft --overwrite
   ```

Ce sont des photos temporaires (pas les vrais chantiers de Guillaume) : a
remplacer par de vraies photos des que possible, avec l'une des deux
methodes ci-dessus.

## Adapter le texte

Le contenu de chaque page est dans `content/chauffage.html` et
`content/sanitaire.html` : un unique bloc Gutenberg "Custom HTML"
(`<!-- wp:html -->`) contenant la structure de la page (hero, sections,
zone d'intervention, CTA). Les jetons `<!--IMGURL:cle-->` marquent
l'emplacement des photos (dans un `src=` ou un `background-image:url(...)`)
et sont remplaces automatiquement par le script avec l'URL reelle de
l'image televersee -- ne les supprimez pas, deplacez-les si besoin. Le style
visuel commun (couleurs, typo, mise en page) est dans
`assets/tessaro-pages.css` et s'applique aux deux pages.

## A verifier avant publication

- **Zone d'intervention** : la liste des villes (Enghien, Silly, Lens, Ath,
  Soignies, Braine-le-Comte, Ecaussinnes, Rebecq, Tubize, Hal, Nivelles,
  Mons...) est une estimation d'un rayon de 50 km autour d'Enghien -- ajustez
  selon les zones que vous couvrez reellement.
- **Entretien legal des chaudieres** : le texte mentionne l'obligation de
  controle periodique en Belgique sans donner de frequence precise (les regles
  different selon combustible et region/organisme agree) -- completez avec
  votre situation exacte si vous le souhaitez.
- **Numero de telephone / email** : `0475 30 84 49` et
  `tessaro.guillaume@hotmail.com` -- verifiez qu'ils sont toujours exacts
  avant publication.
- **Adresse** : seule la ville "7850 Enghien, Belgique" est affichee (pas de
  numero de rue), pour rester coherent avec le pied de page actuel du site.
  Completez `CONTACT_INFO["address"]` dans `pages_config.py` si vous voulez
  une adresse plus precise sur la carte.
- **Formulaire de contact** : installez et configurez Contact Form 7 (voir
  section ci-dessus) avant de publier la page Contact, sinon elle affichera
  un encadre "formulaire non configure" a la place.
- **Photos** : si vous utilisez `fetch_stock_photos.py`, pensez a les
  remplacer par de vraies photos de chantier avant de publier durablement.
