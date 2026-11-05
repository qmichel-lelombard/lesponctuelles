"""Génère un visuel du calendrier : python3 compose.py jours/jour01.json sorties/jour01.png

Mockup : calques extraits de bd_debout_droite_bas.psd (Shadow, Book, Cover en Overlay, Shine).
"""
import json, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
M = os.path.join(HERE, 'assets', 'mockup')

# Positions des calques dans le PSD (2500x1667)
BOOK_XY, SHADOW_XY, SHINE_XY = (743, 129), (511, 1273), (1002, 128)
SHADOW_OP, SHINE_OP = 77 / 255, 184 / 255
# Quad du smart object "Cover" (TL, TR, BR, BL) et taille de son contenu
COVER_QUAD = [(742.88, 210.02), (1610.90, 128.31), (1608.34, 1533.40), (745.74, 1435.05)]
SO_W, SO_H, HINGE = 2550, 3300, 125   # bande de charnière à gauche
CROP = (505, 120, 1740, 1545)           # zone utile du mockup (livre + ombre)


def perspective_coeffs(dst, src):
    """Coefficients pour Image.transform(PERSPECTIVE) : point dst -> point src."""
    A, b = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    return np.linalg.solve(np.array(A, float), np.array(b, float)).tolist()


def so_content(cover):
    """Contenu du smart object : couverture + charnière prolongée à gauche."""
    so = Image.new('RGB', (SO_W, SO_H))
    cover = cover.convert('RGB')
    e = max(1, round(cover.width * .004))          # supprime le liseré de bord éventuel
    cover = cover.crop((e, e, cover.width - e, cover.height - e))
    c = cover.resize((SO_W - HINGE, SO_H), Image.LANCZOS)
    so.paste(c, (HINGE, 0))
    k = round(c.width * .01)                        # charnière = prolongement du bord gauche
    so.paste(c.crop((k, 0, k + 1, SO_H)).resize((HINGE, SO_H)), (0, 0))
    return so


def render_book(cover_path):
    """Rend le mockup complet (RGBA, taille CROP) pour une couverture."""
    W, H = 2500, 1667
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    shadow = Image.open(os.path.join(M, 'shadow.png')).convert('RGBA')
    a = shadow.getchannel('A').point(lambda p: int(p * SHADOW_OP)); shadow.putalpha(a)
    canvas.alpha_composite(shadow, SHADOW_XY)

    book = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    book.paste(Image.open(os.path.join(M, 'book.png')).convert('RGBA'), BOOK_XY)
    # couverture déformée en perspective sur le quad
    src = [(0, 0), (SO_W, 0), (SO_W, SO_H), (0, SO_H)]
    warped = so_content(Image.open(cover_path)).transform(
        (W, H), Image.PERSPECTIVE, perspective_coeffs(COVER_QUAD, src), Image.BICUBIC)
    qmask = Image.new('L', (W, H), 0)
    ImageDraw.Draw(qmask).polygon(COVER_QUAD, fill=255)
    # mode Overlay (calque Cover) sur le livre
    base = np.asarray(book, float) / 255
    bl = np.asarray(warped, float) / 255
    rgb = base[..., :3]
    ov = np.where(rgb < .5, 2 * rgb * bl, 1 - 2 * (1 - rgb) * (1 - bl))
    m = (np.asarray(qmask, float) / 255)[..., None]
    rgb = rgb * (1 - m) + ov * m
    out = np.dstack([rgb, base[..., 3]])
    book = Image.fromarray((out * 255).round().astype('uint8'), 'RGBA')
    # Shine (normal) limité au livre
    shine = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    shine.paste(Image.open(os.path.join(M, 'shine.png')).convert('RGBA'), SHINE_XY)
    sa = np.asarray(shine.getchannel('A'), float) * SHINE_OP * np.asarray(book.getchannel('A'), float) / 255
    shine.putalpha(Image.fromarray(sa.astype('uint8')))
    book.alpha_composite(shine)
    canvas.alpha_composite(book)
    return canvas.crop(CROP)


def main(cfg_path, out_path):
    cfg = json.load(open(cfg_path)); base = os.path.dirname(os.path.abspath(cfg_path))
    p = lambda f: os.path.join(base, f)
    bg = Image.open(p(cfg['bg'])).convert('RGBA')
    for b in cfg['books']:
        im = render_book(p(b['img']))
        s = b['h'] / (1545 - 120)   # h = hauteur de la zone mockup en px
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        bg.alpha_composite(im, (b['x'], b['y']))
    # date dans la boule
    d = cfg['date']; cx, cy, diam = d['cx'], d['cy'], d['diam']
    target = d.get('fill', .9) * diam
    font_path = p(d['font'])
    def layer(size):
        f = ImageFont.truetype(font_path, size)
        l, t, r, bt = f.getbbox(d['text'])
        t_im = Image.new('RGBA', (r - l + 40, bt - t + 40), (0, 0, 0, 0))
        ImageDraw.Draw(t_im).text((20 - l, 20 - t), d['text'], font=f, fill=d.get('color', '#C12D2E'))
        rot = t_im.rotate(-d.get('angle', 5), resample=Image.BICUBIC, expand=True)  # + = sens horaire
        return rot.crop(rot.getbbox())
    # zone dorée libre de la boule (hors houx/baies), légèrement rétrécie
    from PIL import ImageFilter
    reg = bg.crop((cx - diam, cy - diam, cx + diam, cy + diam)).convert('RGB')
    g = np.asarray(reg).astype(int)
    gold = (g[..., 0] > 150) & (g[..., 1] > 110) & (g[..., 2] < 140) & (g[..., 0] - g[..., 2] > 60)
    yy, xx = np.mgrid[:gold.shape[0], :gold.shape[1]]
    gold &= (xx - diam) ** 2 + (yy - diam) ** 2 <= (diam / 2) ** 2
    gm = Image.fromarray((gold * 255).astype('uint8')).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(11))
    gold = np.asarray(gm) > 0
    best = None
    for size in range(20, 200):
        t_im = layer(size)
        if t_im.width > target: break
        ink = np.asarray(t_im.getchannel('A')) > 40
        ok = None
        for dy in range(0, round(diam / 4)):       # descend le texte si besoin (sous le houx)
            x0 = round(diam - t_im.width / 2); y0 = round(diam - t_im.height / 2 + dy)
            sub = gold[y0:y0 + t_im.height, x0:x0 + t_im.width]
            if sub.shape == ink.shape and not (ink & ~sub).any(): ok = dy; break
        if ok is None: continue
        best = (size, t_im, ok)
    size, t_im, dy = best
    bg.alpha_composite(t_im, (round(cx - t_im.width / 2), round(cy - t_im.height / 2 + dy)))
    bg.convert('RGB').save(out_path)
    print(out_path, f'police {size}px, texte {t_im.size}, largeur = {t_im.width / diam:.0%} de la boule')


if __name__ == '__main__':
    main(*sys.argv[1:3])
