"""Génère, pour chaque Elle, une vignette de partage (1200x630) et une page /r/<couleur>/ portant les balises Open Graph.
Les robots des réseaux sociaux n'exécutent pas le JavaScript : chaque résultat a donc sa propre adresse.
Usage : python3 -I tools/make_og_results.py <fredoka.ttf> <nunito.ttf>"""
import os, sys, html
from PIL import Image, ImageDraw, ImageFont, ImageFilter
fred, nun = sys.argv[1], sys.argv[2]
SITE = "https://elles.lelombard.com"
E = {  # clé: (slug, nom, couleur, accroche, mantra, image)
 "rose":     ("rose", "Rose", (255, 79, 147), "Le cœur de la bande, l'équilibre en couleurs !", "Ensemble, c'est toujours mieux.", "rose-pied"),
 "blonde":   ("blonde", "Blonde", (255, 174, 43), "La compétitrice : toujours prête à gagner !", "Qui m'aime me suive… et je passe devant !", "blonde"),
 "brune":    ("chatain", "Châtain", (192, 118, 74), "La plus sensible, avec un cœur d'artiste.", "Je ressens tout… et c'est ma force.", "brune"),
 "violette": ("violette", "Violette", (168, 107, 255), "Le boute-en-train de la bande !", "La vie est trop courte pour ne pas rigoler !", "violette"),
 "verte":    ("verte", "Verte", (32, 184, 148), "Discrète, réfléchie et pleine de sagesse.", "Je dirai quelque chose… quand ce sera le bon moment.", "verte"),
 "bleue":    ("bleue", "Bleue", (42, 174, 224), "La stratège : toujours un plan d'avance.", "J'ai un plan. Suivez-moi.", "bleue"),
}
W, H = 1200, 630
F = lambda p, n: ImageFont.truetype(p, n)
def wrap(d, text, font, maxw):
    out, line = [], ""
    for w in text.split():
        t = (line + " " + w).strip()
        if d.textlength(t, font=font) > maxw and line: out.append(line); line = w
        else: line = t
    return out + [line]

bg0 = Image.open("img/bg-rosies-nuit.webp").convert("RGB")
s = max(W / bg0.width, H / bg0.height); bg0 = bg0.resize((int(bg0.width*s), int(bg0.height*s)), Image.LANCZOS)
bg0 = bg0.crop((0, int(bg0.height*.30), W, int(bg0.height*.30) + H))
logo = Image.open("img/logo.png").convert("RGBA"); logo.thumbnail((190, 190))
logo_w = Image.new("RGBA", logo.size, (255, 255, 255, 255)); logo_w.putalpha(logo.split()[3])

for key, (slug, name, col, tag, mantra, imgname) in E.items():
    im = bg0.convert("RGBA")
    ov = Image.new("RGBA", (W, H)); px = ov.load()                       # voile sombre + halo de la couleur
    for x in range(W):
        a = int(225 * max(0, 1 - x / 800) + 45)
        for y in range(H): px[x, y] = (28, 12, 58, min(238, a))
    im.alpha_composite(ov)
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(halo).ellipse((650, 40, 1200, 650), fill=col + (170,))
    im.alpha_composite(halo.filter(ImageFilter.GaussianBlur(70)))
    g = Image.open(f"img/{imgname}.webp").convert("RGBA")
    h = 585 if imgname == "rose-pied" else 600
    g = g.resize((int(g.width*h/g.height), h), Image.LANCZOS)
    if g.width > 520: g = g.resize((520, int(g.height*520/g.width)), Image.LANCZOS)
    gx, gy = W - g.width - 60, H - g.height
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.paste((10, 0, 40, 160), (gx + 6, gy + 4), g.split()[3]); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    im.alpha_composite(g, (gx, gy))
    im.alpha_composite(logo_w, (60, 40))
    d = ImageDraw.Draw(im)
    d.text((60, 205), "Mon monde intérieur est…", font=F(nun, 30), fill=(255, 255, 255))
    big = F(fred, 100); d.text((60, 245), f"Elle {name}" if len(name) < 8 else f"Elle {name}", font=big, fill=col)
    d.text((60, 365), tag, font=F(fred, 32), fill=(255, 255, 255))
    y = 420
    for line in wrap(d, f"« {mantra} »", F(nun, 28), 560): d.text((60, y), line, font=F(nun, 28), fill=(255, 225, 240)); y += 38
    d.rounded_rectangle((60, 545, 60 + 560, 545 + 54), 27, fill=(255, 79, 147))
    d.text((60 + 24, 545 + 10), "Et toi, quelle Elle se cache en toi ?", font=F(fred, 27), fill=(255, 255, 255))
    os.makedirs("img/og", exist_ok=True); im.convert("RGB").save(f"img/og/{slug}.jpg", quality=88, optimize=True)

    title = f"Je suis Elle {name} ! – Quelle Elle se cache en toi ?"
    desc = f"{tag} « {mantra} » Et toi, quelle Elle se cache en toi ? Tome 4, Intemporelle(s), en librairie !"
    url = f"{SITE}/r/{slug}/"; image = f"{SITE}/img/og/{slug}.jpg"
    A = lambda s: html.escape(s, quote=True)
    os.makedirs(f"r/{slug}", exist_ok=True)
    open(f"r/{slug}/index.html", "w", encoding="utf-8").write(f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{A(title)}</title>
<meta name="description" content="{A(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="ELLES – Le Lombard"><meta property="og:locale" content="fr_FR"><meta property="og:type" content="website">
<meta property="og:url" content="{url}"><meta property="og:title" content="{A(title)}"><meta property="og:description" content="{A(desc)}">
<meta property="og:image" content="{image}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Je suis Elle {A(name)} ! {A(tag)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{A(title)}"><meta name="twitter:description" content="{A(desc)}"><meta name="twitter:image" content="{image}">
<link rel="icon" type="image/png" href="/img/favicon.png">
<noscript><meta http-equiv="refresh" content="0; url=/#resultat-{key}"></noscript>
<script>location.replace("/#resultat-{key}");</script>
</head><body style="background:#1c0f3a;color:#fff;font-family:sans-serif;text-align:center;padding:3rem"><p>Chargement de ton résultat… <a style="color:#ff8fbd" href="/#resultat-{key}">Continuer</a></p></body></html>
''')
    print(slug)
