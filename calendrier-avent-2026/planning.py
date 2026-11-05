"""Génère jours/jourNN.json pour les 24 jours puis les visuels : python3 planning.py [n° de jours…]

Planning = onglet « Planning » de Calendrier_Avent_AVANT_2026.xlsx (ligne du 1/11 = jour 1 = 7/11),
avec la ligne 9 (Gallmeister) = Betty + Le Gang de la clef à molette.
"""
import json, os, glob, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))

# jour : ISBN des albums, de gauche (devant) à droite (derrière).
# {'serie': [...]} = même série : albums en éventail l'un derrière l'autre, le plus récent devant,
#                   angles -5°, -2°, +1°, +4°…
PLANNING = [
    ['9782808217989', '9782808217972'],   # 1  BD de l'Avent polar + jeunesse 2026
    {'serie': ['9782808218535', '9782808214865', '9782808212939']},                  # 2  Thorgal 44, 43, 42
    {'serie': ['9782808218504', '9782808206181', '9782808200004', '9782803678242']}, # 3  Elles 4, 3, 2, 1
    {'serie': ['9782808217958', '9782808214957', '9782808213097']},                  # 4  Schtroumpfs 44, 43, 42
    ['9782808216326'],                    # 5  Après Arthur 1 – Le trône et l'épée
    ['9782808217804'],                    # 6  Chroniques de fer et d'écailles 1 – Le vol des gobelins
    ['9782808215367'],                    # 7  Edgar et les guimauves 1
    ['9782808218726'],                    # 8  La bibliothèque du père Noël 1 – Julbocken
    ['9782808212809', '9782808219358'],   # 9  Gallmeister : Betty + Le Gang de la clef à molette
    ['9782808217460'],                    # 10 Le soleil va se lever
    ['9782808217828'],                    # 11 Mille Ans
    ['9782808211604'],                    # 12 Le Lien
    ['9782808219211'],                    # 13 Le Territoire
    ['9782808201292'],                    # 14 Resurrection Hill
    ['9782808218115'],                    # 15 Un Noël à Paris 2
    ['9782808217071', '9782808215008'],   # 16 Jian 2 + La voie du glaive 3
    ['9782808212588'],                    # 17 Mitsuo 2
    ['9782808217453', '9782808218092'],   # 18 M.A.D. 3 + Sherlock Holmes contre Arsène Lupin 2
    ['9782808218078', '9782808216821'],   # 19 Pro gamer 2 + Dinodyssée 3
    ['9782808216760'],                    # 20 Alpha 21 – Caméléon
    ['9782808216937'],                    # 21 Les Enfants de la Résistance 10 – La guerre n'est pas finie
    ['9782808215121', '9782808214421'],   # 22 Aylin 2 + Elsbeth 2
    ['9782808218740'],                    # 23 Ducobu 30 – Duco... Bouh !
    ['9782808211260'],                    # 24 Lonesome Dove partie 1
]
THEMES = ['rouge', 'jaune', 'bleu']
FONT = '../assets/polices/DancingScript.ttf'


def cover(isbn):
    f = glob.glob(os.path.join(HERE, 'assets', 'couvertures', isbn + '-*.jpg'))
    assert f, 'couverture manquante : ' + isbn
    return '../assets/couvertures/' + os.path.basename(f[0])


SERIE_OVERLAP = 0.6    # chaque album de la série décalé de 40 % de largeur
ONLY = [int(a) for a in sys.argv[1:]]
for n, entry in enumerate(PLANNING, 1):
    if ONLY and n not in ONLY: continue
    serie = isinstance(entry, dict)
    isbns = entry['serie'] if serie else entry
    books = [{'img': cover(i)} for i in isbns]
    overlap = 0.1
    if serie:
        for k, b in enumerate(books):
            b['angle'] = -5 + 3 * k
        overlap = SERIE_OVERLAP
    elif len(books) == 2:                   # réglages validés au jour 1
        books[0]['angle'] = -3
        books[1].update(angle=3, scale=1.02)
    cx = 525 if len(books) >= 4 else 540   # 4 albums : léger décalage pour dégager le houx
    cfg = {
        'theme': THEMES[(n - 1) % 3],
        'layout': {'y': 600, 'h': 520, 'overlap': overlap, 'cx': cx},
        'books': books,
        'date': {'text': str(n), 'font': FONT, 'angle': 5, 'cx': 959, 'cy': 1201, 'diam': 147, 'fill': 0.9},
        'mention': {'text': '* voir conditions de participation', 'font': FONT, 'size': 24, 'x': 1050, 'y': 1318},
    }
    jp = os.path.join(HERE, 'jours', f'jour{n:02d}.json')
    json.dump(cfg, open(jp, 'w'), ensure_ascii=False, indent=2)
    subprocess.run([sys.executable, os.path.join(HERE, 'compose.py'), jp,
                    os.path.join(HERE, 'sorties', f'jour{n:02d}.png')], check=True)
