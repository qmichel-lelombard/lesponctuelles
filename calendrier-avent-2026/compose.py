"""Génère un visuel du calendrier : python3 compose.py jours/jour01.json sorties/jour01.png

Mockup : calques extraits de bd_debout_droite_bas.psd (Shadow, Book, Cover en Overlay, Shine).
"""
import json, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
M = os.path.join(HERE, 'assets', 'mockup')

# Positions des calques dans le PSD (2500x1667)
BOOK_XY, SHADOW_XY, SHINE_XY = (743, 129), (511, 1273), (1002, 128)
SHADOW_OP, SHINE_OP = 77 / 255, 184 / 255
# Quad du smart object "Cover" (TL, TR, BR, BL) et taille de son contenu
COVER_QUAD = [(742.88, 210.02), (1610.90, 128.31), (1608.34, 1533.40), (745.74, 1435.05)]
SO_W, SO_H, HINGE = 2550, 3300, 125   # bande de charnière à gauche
CROP = (505, 120, 1740, 1545)           # zone utile du mockup (livre + ombre)


def prerendered(path, body_h):
    """Charge une simulation 3D détourée, la met à la hauteur voulue ; ajoute une ombre au sol si elle n'en a pas."""
    src = Image.open(path).convert('RGBA'); src = src.crop(src.getchannel('A').getbbox())
    al = np.asarray(src.getchannel('A'))
    ys, xs = np.nonzero(al > 200)                       # le livre (opaque), hors ombre semi-transparente
    bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    own_shadow = bool(((al > 10) & (al < 200)).sum() > .01 * (al > 200).sum())
    k = float(body_h) / float(by1 - by0)
    src = src.resize((round(src.width * k), round(src.height * k)), Image.LANCZOS)
    bx0, by0, bx1, by1 = (float(v) * k for v in (bx0, by0, bx1, by1))
    bw = bx1 - bx0
    pad = round(bw * .35)
    W, H = src.width + 2 * pad, src.height + pad
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if not own_shadow:
        sh = Image.new('L', (W, H), 0)
        ImageDraw.Draw(sh).ellipse((pad + bx0 - bw * .15, pad * 0 + by1 - bw * .06,
                                    pad + bx0 + bw * .95, by1 + bw * .03), fill=255)
        sh = sh.filter(ImageFilter.GaussianBlur(bw * .05))
        shadow = Image.new('RGBA', (W, H), (40, 30, 20, 0)); shadow.putalpha(sh.point(lambda v: int(v * .32)))
        canvas.alpha_composite(shadow)
    canvas.alpha_composite(src, (pad, 0))
    body = Image.new('L', (W, H), 0); body.paste(src.getchannel('A').point(lambda v: 255 if v > 200 else 0), (pad, 0))
    return canvas, body, pad + (bx0 + bx1) / 2, (by0 + by1) / 2


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
    return canvas.crop(CROP), book.getchannel('A').crop(CROP)


# Fonds : rouge -> jaune -> bleu (couleurs relevées sur les fonds)
THEMES = {
    'rouge': {'bg': 'assets/fond_rouge.png', 'number': '#C12D2E', 'mention': '#C12D2E'},
    'jaune': {'bg': 'assets/fond_jaune.png', 'number': '#D4AF37', 'mention': '#8F6FCE'},  # numéro jaune titre, mention mauve
    'bleu':  {'bg': 'assets/fond_bleu.png',  'number': '#004AAD', 'mention': '#004AAD'},  # bleu du titre
}


def main(cfg_path, out_path):
    cfg = json.load(open(cfg_path)); base = os.path.dirname(os.path.abspath(cfg_path))
    p = lambda f: os.path.join(base, f)
    th = THEMES[cfg.get('theme', 'rouge')]
    bg = Image.open(os.path.join(HERE, th['bg'])).convert('RGBA')
    lay = cfg.get('layout', {})
    h = lay.get('h', 520); s = h / (CROP[3] - CROP[1])
    book_w = (1635 - 743) * s; off = (743 - CROP[0]) * s     # largeur du livre / décalage dans le mockup
    n = len(cfg['books'])
    # écart entre albums consécutifs (en largeur d'album) : 'steps' explicite, sinon 1 - overlap partout
    steps = lay.get('steps') or [1 - lay.get('overlap', .1)] * (n - 1)
    offs = [0.0]
    for st in steps: offs.append(offs[-1] + st * book_w)
    left = lay.get('cx', 540) - (offs[-1] + book_w) / 2
    # même taille pour tous ; on dessine de droite à gauche : l'album de droite est à l'arrière-plan
    bodies = None
    # ordre de dessin : 'z' croissant (le plus grand devant) ; par défaut l'album de gauche est devant
    order = sorted(range(n), key=lambda i: cfg['books'][i].get('z', -i))
    for i in order:
        b = cfg['books'][i]
        x = b.get('x', round(left + offs[i] - off)); y = b.get('y', lay.get('y', 600)) + b.get('dy', 0)
        # centre du livre (hors ombre) : point fixe pour l'échelle et la rotation
        bx = x + (743 + 1635) / 2 * s - CROP[0] * s; by = y + (129 + 1533) / 2 * s - CROP[1] * s
        if 'png' in b:
            # simulation 3D fournie (PNG détouré) : même hauteur que le livre du mockup + ombre au sol
            im, body, ccx, ccy = prerendered(p(b['png']), (1533 - 129) * s * b.get('scale', 1))
        else:
            im, body = render_book(p(b['img']))
            k = s * b.get('scale', 1)
            im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
            body = body.resize(im.size, Image.LANCZOS)
            ccx = ((743 + 1635) / 2 - CROP[0]) * k; ccy = ((129 + 1533) / 2 - CROP[1]) * k
        ang = b.get('angle', 0)                        # + = sens horaire (comme le numéro)
        if ang:
            W0, H0 = im.size
            im = im.rotate(-ang, resample=Image.BICUBIC, expand=True, center=(ccx, ccy))
            body = body.rotate(-ang, resample=Image.BICUBIC, expand=True, center=(ccx, ccy))
            # avec expand, PIL tourne autour du centre de l'image : on recalcule la position du point fixe
            import math
            a = math.radians(-ang); dx, dy = ccx - W0 / 2, ccy - H0 / 2
            ccx = im.width / 2 + dx * math.cos(a) + dy * math.sin(a)
            ccy = im.height / 2 - dx * math.sin(a) + dy * math.cos(a)
        pos = (round(bx - ccx), round(by - ccy))
        mask = Image.new('L', bg.size, 0); mask.paste(body, pos)
        if bodies is not None:
            # ombre portée de cet album sur les albums déjà posés derrière (seulement sur la partie recouverte)
            sh = lay.get('shadow', {})
            ox, oy = sh.get('dx', 6), sh.get('dy', 3)
            m = Image.new('L', bg.size, 0); m.paste(mask, (ox, oy))
            m = m.filter(ImageFilter.GaussianBlur(sh.get('blur', 9)))
            a = np.asarray(m, float) / 255 * sh.get('opacity', .45) * np.asarray(bodies, float) / 255
            rgb = np.asarray(bg, float); rgb[..., :3] *= (1 - a)[..., None]
            bg = Image.fromarray(rgb.round().astype('uint8'), 'RGBA')
        bg.alpha_composite(im, pos)
        bodies = mask if bodies is None else ImageChops.lighter(bodies, mask)
    # date dans la boule
    d = cfg['date']; cx, cy, diam = d['cx'], d['cy'], d['diam']
    font_path = p(d['font'])
    def layer(size):
        f = ImageFont.truetype(font_path, size)
        l, t, r, bt = f.getbbox(d['text'])
        t_im = Image.new('RGBA', (r - l + 40, bt - t + 40), (0, 0, 0, 0))
        ImageDraw.Draw(t_im).text((20 - l, 20 - t), d['text'], font=f, fill=d.get('color', th['number']))
        rot = t_im.rotate(-d.get('angle', 5), resample=Image.BICUBIC, expand=True)  # + = sens horaire
        return rot.crop(rot.getbbox())
    # zone dorée libre de la boule (hors houx/baies), légèrement rétrécie
    # houx et baies identiques sur les 3 fonds : on les détecte sur le fond rouge (boule dorée, sans ambiguïté)
    ref = Image.open(os.path.join(HERE, THEMES['rouge']['bg'])).convert('RGB')
    reg = ref.crop((cx - diam, cy - diam, cx + diam, cy + diam))
    g = np.asarray(reg).astype(int)
    # boule = disque, moins le houx (vert foncé) et les baies (rouge), quelle que soit la couleur de la boule
    r_, g_, b_ = g[..., 0], g[..., 1], g[..., 2]
    holly = (g_ > r_ + 15) & (r_ < 120) & (g_ < 170) & (b_ < g_)
    berry = (r_ > 150) & (g_ < 110) & (b_ < 110)
    excl = Image.fromarray(((holly | berry) * 255).astype('uint8')).filter(ImageFilter.MaxFilter(13))
    yy, xx = np.mgrid[:g.shape[0], :g.shape[1]]
    gold = ((xx - diam) ** 2 + (yy - diam) ** 2 <= (diam / 2 - 5) ** 2) & ~(np.asarray(excl) > 0)
    gm = Image.fromarray((gold * 255).astype('uint8')).filter(ImageFilter.MinFilter(3))
    gold = np.asarray(gm) > 0
    # centre = barycentre de la zone dorée libre ; taille max qui tient, puis x fill (90 %)
    ys, xs = np.nonzero(gold); gx, gy = xs.mean(), ys.mean()
    def fits(t_im):
        ink = np.asarray(t_im.getchannel('A')) > 40
        x0 = round(gx - t_im.width / 2); y0 = round(gy - t_im.height / 2)
        if x0 < 0 or y0 < 0: return False
        sub = gold[y0:y0 + t_im.height, x0:x0 + t_im.width]
        return sub.shape == ink.shape and not (ink & ~sub).any()
    size_max = 20
    while fits(layer(size_max + 1)): size_max += 1
    size = round(size_max * d.get('fill', .9))
    t_im = layer(size)
    bg.alpha_composite(t_im, (round(cx - diam + gx - t_im.width / 2), round(cy - diam + gy - t_im.height / 2)))
    # mention légale sous la boule (alignée à droite)
    mt = cfg.get('mention')
    if mt:
        f = ImageFont.truetype(p(mt['font']), mt.get('size', 22))
        ImageDraw.Draw(bg).text((mt['x'], mt['y']), mt['text'], font=f, fill=mt.get('color', th['mention']), anchor='rs')
    bg.convert('RGB').save(out_path)
    print(out_path, f'police {size}px (max {size_max}px), texte {t_im.size}')


if __name__ == '__main__':
    main(*sys.argv[1:3])
