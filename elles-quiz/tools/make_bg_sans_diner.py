"""Fond du Rosie's SANS le diner, pour les visuels réseaux sociaux uniquement (le site garde le décor d'origine).
Retouche du décor : la zone du diner est remplacée par le sol du désert, reconstruit ligne par ligne à partir
du sol voisin (mêmes teintes, même grain). Le ciel, les montagnes et le reste du sol ne sont pas modifiés.
Usage : python3 -I tools/make_bg_sans_diner.py"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

src = Image.open("img/bg-rosies-nuit.webp").convert("RGB"); W, H = src.size
a = np.asarray(src).astype(np.float32)

# zone à remplacer : l'enseigne, le bâtiment et son halo lumineux au sol
m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
d.polygon([(825, 925), (1035, 925), (1045, 1090), (1215, 1150), (1215, H), (265, H), (265, 1150), (600, 1055), (820, 1060)], fill=255)
hard = np.asarray(m) > 0

# grain du sol : détail fin (image - flou) prélevé à gauche et à droite du diner, sur les mêmes lignes
blur = np.asarray(src.filter(ImageFilter.GaussianBlur(14))).astype(np.float32)
hp = a - blur
fill = np.zeros_like(a)
for y in range(900, H):
    xs = np.nonzero(hard[y])[0]
    if xs.size == 0: continue
    x0, x1 = xs[0], xs[-1]
    L = np.median(a[y, max(0, x0 - 120):x0 - 6], axis=0); R = np.median(a[y, x1 + 6:min(W, x1 + 120)], axis=0)
    t = np.linspace(0, 1, x1 - x0 + 1)[:, None]
    fill[y, x0:x1 + 1] = L * (1 - t) + R * t
    # grain : bandes de sol voisines, en miroir alterné
    stripL = hp[y, max(0, x0 - 250):x0 - 4]; stripR = hp[y, x1 + 4:min(W, x1 + 230)]
    tex = np.concatenate([stripL[::-1], stripR[::-1], stripL, stripR] * 3)[: x1 - x0 + 1]
    fill[y, x0:x1 + 1] += tex * .9
fill[~hard] = a[~hard]                      # hors zone : le décor d'origine (évite un liseré au raccord)
fimg = Image.fromarray(np.clip(fill, 0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(.6))
soft = m.filter(ImageFilter.GaussianBlur(14))
out = Image.composite(fimg, src, soft)
out.save("social/_fond_sans_diner.png"); print("social/_fond_sans_diner.png", out.size)
