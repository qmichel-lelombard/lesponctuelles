# Calendrier de l'Avent (Avant !) 2026 – visuels Instagram

Concours sur 24 jours, du 7/11 au 30/11/2026. Le planning est dans l'onglet « Planning » de `Calendrier_Avent_AVANT_2026.xlsx`.

Chaque jour est décrit par un fichier `jours/jourNN.json` :
- les couvertures (récupérées sur lelombard.com/bd/nouveautes, format M1000x1300) ;
- la position et l'angle des albums ;
- la date à écrire dans la boule (rouge #C12D2E, 36px, +5°).

Rendu en 1080×1350 (format portrait Instagram) :

    node render.js jours/jour01.json sorties/jour01_07-11.png

Police de la date : `Pacifico.ttf` remplace temporairement Railey (police commerciale, pas disponible ici).
Pour passer à la vraie police, ajoute `Railey.otf` dans `assets/polices/` et modifie le champ `font`.
