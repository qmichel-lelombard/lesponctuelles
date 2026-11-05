# Calendrier de l'Avent (Avant !) 2026 – visuels Instagram

Concours sur 24 jours, du 7/11 au 30/11/2026. Le planning est dans l'onglet « Planning » de `Calendrier_Avent_AVANT_2026.xlsx`
(ligne du 1/11 = jour 1 = 7/11).

Chaque jour est décrit par un fichier `jours/jourNN.json` :
- `books` : couverture (récupérée sur lelombard.com/bd/nouveautes, format M1000x1300), position `x`/`y` et hauteur `h` du mockup ;
- `date` : texte, police, couleur (#C12D2E), angle (+5° = sens horaire) et `fill` (largeur visée, 0.9 = 90 % de la boule).
  La taille est calculée automatiquement : la plus grande possible jusqu'à 90 % de largeur, sans déborder de la boule ni toucher le houx.

Mockup 3D : calques extraits de `bd_debout_droite_bas.psd` (Shadow, Book, Cover en Overlay avec la même perspective, Shine),
dans `assets/mockup/`.

Rendu en 1080×1350 (format portrait Instagram) :

    pip install pillow numpy
    python3 compose.py jours/jour01.json sorties/jour01_07-11.png

Police de la date : `Pacifico.ttf` remplace temporairement Railey (police commerciale, pas disponible ici).
Pour passer à la vraie police, ajoute `Railey.otf` dans `assets/polices/` et modifie le champ `font`.
