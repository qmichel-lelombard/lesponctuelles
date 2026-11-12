# Calendrier de l'Avent (Avant !) 2026 – visuels Instagram

Concours sur 24 jours, du 7/11 au 30/11/2026. Le planning est dans l'onglet « Planning » de `Calendrier_Avent_AVANT_2026.xlsx`
(ligne du 1/11 = jour 1 = 7/11).

Chaque jour est décrit par un fichier `jours/jourNN.json` :
- `books` : couvertures (récupérées sur lelombard.com/bd/nouveautes, format M1000x1300), de gauche à droite, tous à la même taille ; chaque album passe derrière celui de gauche ;
- `layout` : `y` (haut du mockup), `h` (hauteur), `overlap` (chevauchement, 0.1 = 10 % de la largeur d'un album), `cx` (centre horizontal du groupe).
  `shadow` : ombre portée d'un album sur celui de derrière, uniquement sur la partie recouverte (`dx`, `dy`, `blur`, `opacity`, défaut 6/3/9/0.45).
  Par album : `angle` (en degrés, + = sens horaire), `scale` (1.02 = 102 %), et `x`/`y` pour forcer la position ;
- `date` : numéro du jour (1 à 24), police, couleur (#C12D2E), angle (+5° = sens horaire) et `fill`.
  La taille est calculée automatiquement : 90 % (`fill`) de la taille maximale qui tient dans la partie dorée de la boule, sous le houx.

`mention` : petite phrase sous la boule, alignée à droite (`text`, `font`, `size`, `color`, `x`, `y` = coin bas droit).

Mockup 3D : calques extraits de `bd_debout_droite_bas.psd` (Shadow, Book, Cover en Overlay avec la même perspective, Shine),
dans `assets/mockup/`.

Fonds en alternance rouge → jaune → bleu (jour 1 rouge, 2 jaune, 3 bleu…), champ `theme` :
- rouge : numéro et mention en rouge #C12D2E ;
- jaune : numéro en jaune du titre #D4AF37 (boule bleue), mention en mauve #8F6FCE ;
- bleu : numéro et mention en bleu du titre #004AAD (boule argentée).

Les 24 jours (fichiers JSON + visuels) sont générés par `planning.py` à partir du planning qui y est recopié :

    python3 planning.py          # les 24 jours
    python3 planning.py 2 3 4    # seulement certains jours

Même série (`{'serie': [...]}` dans `planning.py`) : albums en éventail l'un derrière l'autre, le plus récent devant à gauche,
angles -5°, -2°, +1°, +4°… (+3° par album), chaque album décalé de 40 % de largeur.

Deux albums (séries différentes) : -3° / +3°, celui de droite à 102 % et derrière, chevauchement 10 %, ombre portée. Un album : droit, centré, à 110 %.

Simulation 3D fournie (PNG détouré dans `assets/simu3d/<ISBN>-….png`) : utilisée automatiquement à la place du mockup (jour 9 : Betty, Le Gang de la clef à molette ; jour 10 : Le soleil va se lever).
Si la simulation a déjà sa propre ombre au sol, elle est gardée telle quelle.

Compositions sur mesure : dictionnaire `COMPOSITIONS` de `planning.py` (angle, échelle, profondeur `z` et écarts par album).
Jour 16 : Jian 2 devant (-5°), Jian 1 derrière à sa droite (-2°) | La voie du glaive 3, 2, 1 à droite (+3°, +6°, +9°).

Versions alternatives : liste `VARIANTES` de `planning.py` (ex. `jour14b` : Resurrection Hill, Little Tulip, New York Cannibals – collection Signé Boucq/Charyn ; `jour15b` : Un Noël à Paris 2 devant, 1 derrière)..

Rendu d'un seul jour en 1080×1350 (format portrait Instagram) :

    pip install pillow numpy
    python3 compose.py jours/jour01.json sorties/jour01.png

Police du numéro : `DancingScript.ttf` (Google Fonts, OFL) remplace temporairement Railey (police commerciale, pas disponible ici).
Pour passer à la vraie police, ajoute `Railey.otf` dans `assets/polices/` et modifie le champ `font`.

Format story 1080×1920 (dans `sorties/story/`), à relancer après `planning.py` :

    python3 story.py
