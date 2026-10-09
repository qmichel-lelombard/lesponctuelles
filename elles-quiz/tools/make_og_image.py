"""Génère l'image de partage réseaux sociaux (1200x630) à partir des visuels fournis (aucun dessin créé).
Usage : python3 -I tools/make_og_image.py <fredoka.ttf> <nunito.ttf>   (polices Google Fonts)"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
fred, nun = sys.argv[1], sys.argv[2]
W, H = 1200, 630
bg = Image.open("img/bg-rosies-nuit.webp").convert("RGB")
s = max(W / bg.width, H / bg.height); bg = bg.resize((int(bg.width*s), int(bg.height*s)), Image.LANCZOS)
bg = bg.crop((0, int(bg.height*.36), W, int(bg.height*.36)+H)) if bg.height > H*1.4 else bg.crop(((bg.width-W)//2, (bg.height-H)//2, (bg.width-W)//2+W, (bg.height-H)//2+H))
im = bg.convert("RGBA")
# voile violet pour la lisibilité du texte, plus dense à gauche
ov = Image.new("RGBA", (W, H)); px = ov.load()
for x in range(W):
    a = int(215 * max(0, 1 - x / 820) + 40)
    for y in range(H): px[x, y] = (28, 12, 58, min(235, a))
im.alpha_composite(ov)
# groupe des six Elles, à droite
g = Image.open("img/elles-groupe.webp").convert("RGBA"); h = 560; g = g.resize((int(g.width*h/g.height), h), Image.LANCZOS)
sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.paste((10, 0, 40, 150), (W - g.width - 6 + 8, H - g.height + 4), g.split()[3]); sh = sh.filter(ImageFilter.GaussianBlur(14)); im.alpha_composite(sh)
im.alpha_composite(g, (W - g.width - 6, H - g.height + 10))
# logo ELLES en blanc
lg = Image.open("img/logo.png").convert("RGBA"); lg.thumbnail((230, 230))
white = Image.new("RGBA", lg.size, (255, 255, 255, 255)); white.putalpha(lg.split()[3]); im.alpha_composite(white, (64, 52))
d = ImageDraw.Draw(im)
F = lambda p, n: ImageFont.truetype(p, n)
try:
    ft = F(fred, 74); ft.set_variation_by_axes([700]) if hasattr(ft, "set_variation_by_axes") else None
except Exception: ft = F(fred, 74)
y = 196
for line, col in (("Quelle", (255, 255, 255)), ("Elle", (255, 111, 166)), ("se cache en toi ?", (255, 255, 255))):
    d.text((64, y), line, font=ft, fill=col, stroke_width=0); y += 86
fs = F(nun, 30)
d.text((66, y + 18), "6 personnalités, 1 seul corps !", font=fs, fill=(255, 255, 255))
d.rounded_rectangle((64, y + 74, 64 + 520, y + 74 + 56), 28, fill=(255, 79, 147))
fb = F(fred, 27); d.text((64 + 26, y + 74 + 11), "Tome 4 · Intemporelle(s) · Le grand retour !", font=fb, fill=(255, 255, 255))
im.convert("RGB").save("img/og-image.jpg", quality=90, optimize=True); print("img/og-image.jpg")
