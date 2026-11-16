"""Visuels réseaux sociaux (Instagram 4:5, 1080x1350) : un carrousel de 8 images et une image unique.
Aucun dessin créé : uniquement les visuels fournis. Usage : python3 -I tools/make_social.py <fredoka.ttf> <nunito.ttf>"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
fred, nun = sys.argv[1], sys.argv[2]
W, H = 1080, 1350
F = lambda p, n: ImageFont.truetype(p, n)
NB = " "
ELLES = [  # clé image, nom, couleur, accroche courte
    ("rose-pied", "Rose", (255, 79, 147), "Le cœur de la bande"),
    ("blonde", "Blonde", (255, 174, 43), "La compétitrice"),
    ("brune", "Châtain", (192, 118, 74), "La sensible au cœur d'artiste"),
    ("violette", "Violette", (168, 107, 255), "Le boute-en-train"),
    ("verte", "Verte", (32, 184, 148), "La discrète pleine de sagesse"),
    ("bleue", "Bleue", (42, 174, 224), "La stratège"),
]

def cover(path, focus=(.5, .5)):
    im = Image.open(path).convert("RGB"); s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = round((im.width - W) * focus[0]); y = round((im.height - H) * focus[1])
    return im.crop((x, y, x + W, y + H)).convert("RGBA")

def veil(im, top=120, bottom=235, start=.45):
    """voile sombre en haut (logo) et en bas (texte)"""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); px = ov.load()
    for y in range(H):
        a = 0
        if y < 300: a = int(top * (1 - y / 300))
        if y > H * start: a = max(a, int(bottom * min(1, (y - H * start) / (H * (1 - start) * .75))))
        for x in range(W): px[x, y] = (24, 10, 52, a)
    im.alpha_composite(ov); return im

def halo(im, col, box):
    h = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(h).ellipse(box, fill=col + (165,))
    im.alpha_composite(h.filter(ImageFilter.GaussianBlur(90))); return im

def paste(im, g, x, y):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.paste((10, 0, 40, 150), (x + 8, y + 10), g.split()[3])
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    im.alpha_composite(g, (x, y)); return im

def fit(g, maxw, maxh):
    s = min(maxw / g.width, maxh / g.height); return g.resize((round(g.width * s), round(g.height * s)), Image.LANCZOS)

def logo(im, w=300, y=64):
    lg = Image.open("img/logo.png").convert("RGBA"); lg = lg.resize((w, round(lg.height * w / lg.width)), Image.LANCZOS)
    wh = Image.new("RGBA", lg.size, (255, 255, 255, 255)); wh.putalpha(lg.split()[3]); im.alpha_composite(wh, ((W - w) // 2, y)); return im

def center(d, y, text, font, fill, stroke=0):
    w = d.textlength(text, font=font); d.text(((W - w) / 2, y), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=(24, 10, 52)); return w

def pill(d, y, text, font, fill=(255, 79, 147), pad=(44, 20)):
    w = d.textlength(text, font=font); bb = font.getbbox(text); h = bb[3] - bb[1]
    x0 = (W - w) / 2 - pad[0]; d.rounded_rectangle((x0, y, x0 + w + 2 * pad[0], y + h + 2 * pad[1]), (h + 2 * pad[1]) / 2, fill=fill)
    d.text(((W - w) / 2, y + pad[1] - bb[1]), text, font=font, fill=(255, 255, 255))

def dots(d, i, n=8):
    for k in range(n):
        x = W / 2 + (k - (n - 1) / 2) * 30; r = 7 if k == i else 5
        d.ellipse((x - r, H - 44 - r, x + r, H - 44 + r), fill=(255, 255, 255, 255 if k == i else 110))

def title(d, y, size=104, lead=1.08):
    f = F(fred, size)
    center(d, y, "Quelle Elle", f, (255, 255, 255))
    # « Elle » en rose
    w = d.textlength("Quelle Elle", font=f); x = (W - w) / 2 + d.textlength("Quelle ", font=f)
    d.text((x, y), "Elle", font=f, fill=(255, 111, 166))
    center(d, y + size * lead, f"se cache en toi{NB}?", f, (255, 255, 255))

def group_slide(name, cta, with_dots=None, sub=None, gy=235, lead=1.08):
    im = veil(cover("img/bg-rosies-nuit.webp", (.5, .25)), bottom=245, start=.5)
    g = fit(Image.open("img/elles-groupe.webp").convert("RGBA"), 900, 760)
    halo(im, (255, 79, 147), (140, 240, 940, 900)); logo(im); paste(im, g, (W - g.width) // 2, gy)   # le groupe passe devant le logo
    d = ImageDraw.Draw(im, "RGBA")
    title(d, (925 if sub else 955) + round(96 * (1.08 - lead)), 96, lead)
    if sub: center(d, 1152, sub, F(fred, 36), (255, 255, 255))
    pill(d, 1206 if not sub else 1212, cta, F(fred, 40))
    if with_dots is not None: dots(d, with_dots)
    im.convert("RGB").save(f"social/{name}", quality=92); print(name)

# ---------- Carrousel
group_slide("carrousel_1_couverture.jpg", f"Découvre les 6 Elles")
for i, (key, name, col, tag) in enumerate(ELLES, 1):
    im = cover("img/bg-pyramides.webp", (.5, .2)); halo(im, col, (120, 260, 960, 1060)); veil(im, bottom=250, start=.56)
    g = Image.open(f"img/{key}.webp").convert("RGBA")
    g = fit(g, 820, 800)
    paste(im, g, (W - g.width) // 2, 1020 - g.height)
    logo(im, 210, 56); d = ImageDraw.Draw(im, "RGBA")
    center(d, 1040, f"Elle {name}", F(fred, 118), col)
    center(d, 1180, tag, F(nun, 42), (255, 255, 255))
    slug = {"Châtain": "chatain"}.get(name, name.lower())
    im.convert("RGB").save(f"social/carrousel_{i+1}_{slug}.jpg", quality=92); print(i + 1, name)
# dernière image : appel à l'action + tome 4
im = veil(cover("img/bg-rosies-nuit.webp", (.5, .25)), top=150, bottom=250, start=.42)
cv = Image.open("img/couverture-t4.webp").convert("RGBA"); cv = fit(cv, 520, 640).rotate(-4, expand=True, resample=Image.BICUBIC)
halo(im, (255, 79, 147), (200, 220, 880, 900)); paste(im, cv, (W - cv.width) // 2, 240)
logo(im, 210, 56); d = ImageDraw.Draw(im, "RGBA")
center(d, 930, "Et toi, quelle Elle es-tu" + NB + "?", F(fred, 70), (255, 255, 255))
pill(d, 1040, "Fais le test", F(fred, 46))
center(d, 1150, "elles.lelombard.com", F(fred, 46), (255, 255, 255))
center(d, 1222, f"Tome 4 · Intemporelle(s) · en librairie", F(nun, 32), (255, 220, 235))
im.convert("RGB").save("social/carrousel_8_fais-le-test.jpg", quality=92); print(8)

# ---------- Image unique
group_slide("photo_unique.jpg", "elles.lelombard.com", sub="Fais le test", gy=192, lead=.9)
