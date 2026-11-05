# Calendrier de l'Avent (Avant !) 2026 – visuels Instagram

Concours sur 24 jours, du 7/11 au 30/11/2026. Le planning est dans l'onglet « Planning » de `Calendrier_Avent_AVANT_2026.xlsx`
(ligne du 1/11 = jour 1 = 7/11).

Chaque jour est décrit par un fichier `jours/jourNN.json` :
- `books` : couvertures (récupérées sur lelombard.com/bd/nouveautes, format M1000x1300), de gauche à droite, tous à la même taille ; chaque album passe derrière celui de gauche ;
- `layout` : `y` (haut du mockup), `h` (hauteur), `overlap` (chevauchement, 0.1 = 10 % de la largeur d'un album), `cx` (centre horizontal du groupe).
  Par album : `angle` (en degrés, + = sens horaire), `scale` (1.02 = 102 %), et `x`/`y` pour forcer la position ;
- `date` : numéro du jour (1 à 24), police, couleur (#C12D2E), angle (+5° = sens horaire) et `fill`.
  La taille est calculée automatiquement : 90 % (`fill`) de la taille maximale qui tient dans la partie dorée de la boule, sous le houx.

Mockup 3D : calques extraits de `bd_debout_droite_bas.psd` (Shadow, Book, Cover en Overlay avec la même perspective, Shine),
dans `assets/mockup/`.

Rendu en 1080×1350 (format portrait Instagram) :

    pip install pillow numpy
    python3 compose.py jours/jour01.json sorties/jour01.png

Police du numéro : `DancingScript.ttf` (Google Fonts, OFL) remplace temporairement Railey (police commerciale, pas disponible ici).
Pour passer à la vraie police, ajoute `Railey.otf` dans `assets/polices/` et modifie le champ `font`.
