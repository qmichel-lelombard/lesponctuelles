"""Prépare les visuels du quiz à partir des fichiers sources fournis (recadrages et détourages uniquement,
aucune retouche du dessin). Usage : python3 -I prepare_assets.py <dossier_sources> <dossier_sortie>"""
import sys
from collections import deque
from PIL import Image, ImageFilter
import numpy as np

src, out = sys.argv[1].rstrip("/") + "/", sys.argv[2].rstrip("/") + "/"

def save(im, name, q=82):
    im.save(out + name, quality=q, method=6) if name.endswith("webp") else im.save(out + name)

def cut_white(im, thr=222):
    """Détourage : on retire le blanc relié aux bords (flood fill), puis on adoucit le liseré."""
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    h, w, _ = a.shape
    near = a.min(axis=2) >= thr
    seen = np.zeros((h, w), bool)
    dq = deque()
    for x in range(w):
        for y in (0, h - 1):
            if near[y, x] and not seen[y, x]: seen[y, x] = True; dq.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if near[y, x] and not seen[y, x]: seen[y, x] = True; dq.append((y, x))
    while dq:
        y, x = dq.popleft()
        for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny, nx = y+dy, x+dx
            if 0 <= ny < h and 0 <= nx < w and near[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True; dq.append((ny, nx))
    alpha = Image.fromarray(((~seen) * 255).astype("uint8"))
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.1))
    rgba = im.convert("RGBA"); rgba.putalpha(alpha)
    return rgba

def drop_sage(im, box, extra=None):
    """Retire, dans une zone, les pixels vert-de-gris du pantalon d'une autre fille qui dépasse derrière."""
    a = np.asarray(im).copy()
    x0, y0, x1, y1 = box
    z = a[y0:y1, x0:x1].astype(int)
    r, g, b = z[..., 0], z[..., 1], z[..., 2]
    m = (g > r + 14) & (a[y0:y1, x0:x1, 3] > 0)
    a[y0:y1, x0:x1, 3][m] = 0
    return Image.fromarray(a)

# --- Logo
Image.open(src + "1.webp").convert("RGBA").resize((1000, 545), Image.LANCZOS).save(out + "logo.png", optimize=True)

# --- Les six Elles (3.jpg est en CMYK) : coordonnées dans l'image d'origine
g = Image.open(src + "3.jpg").convert("RGB")
full = cut_white(g)
full = full.crop(full.getbbox())
full.thumbnail((1400, 1400)); save(full, "elles-groupe.webp", 86)

OX, OY = 150, 300   # origine du repère de la grille de repérage

def largest(im):
    """Ne garde que la plus grande forme détourée (élimine les morceaux des voisines)."""
    a = np.asarray(im).copy()
    mask = a[..., 3] > 20
    h, w = mask.shape
    lab = np.zeros((h, w), np.int32); best, best_n, k = 0, 0, 0
    for sy in range(h):
        for sx in range(w):
            if mask[sy, sx] and not lab[sy, sx]:
                k += 1; lab[sy, sx] = k; dq = deque([(sy, sx)]); n = 0
                while dq:
                    y, x = dq.popleft(); n += 1
                    for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        ny, nx = y+dy, x+dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = k; dq.append((ny, nx))
                if n > best_n: best, best_n = k, n
    a[..., 3][lab != best] = 0
    return Image.fromarray(a)

def erase(im, rect):
    a = np.asarray(im).copy(); x0, y0, x1, y1 = rect
    a[y0:y1, x0:x1, 3] = 0
    return Image.fromarray(a)

def erase_color(im, rect, test):
    a = np.asarray(im).copy(); x0, y0, x1, y1 = rect
    z = a[y0:y1, x0:x1].astype(int)
    m = test(z[..., 0], z[..., 1], z[..., 2])
    a[y0:y1, x0:x1, 3][m] = 0
    return Image.fromarray(a)

def bust(name, x0, y0, x1, y1, fix=None):
    c = cut_white(g.crop((OX+x0, OY+y0, OX+x1, OY+y1)))
    if fix: c = fix(c)
    c = largest(c)
    c = c.crop(c.getbbox())
    a = np.asarray(c).copy(); a[..., 3][a[..., 3] < 14] = 0
    c = Image.fromarray(a)
    c.thumbnail((900, 1100)); c.save(out + name + ".webp", lossless=True, method=6)

sage = lambda r, gg, b: gg > r + 14
bust("verte",   215, 45, 400, 505)
bust("rose",    400, 35, 670, 500)
bust("bleue",   668, 50, 890, 545)
bust("blonde",  195, 528, 458, 1000, lambda c: erase_color(
        erase_color(c, (0, 0, c.width, 330), sage), (0, 0, c.width, 45), lambda r, gg, b: r < 110))
brune_fix = lambda c: erase_color(c, (0, int(c.height*0.55), 75, c.height), lambda r, gg, b: np.minimum(np.minimum(r, gg), b) > 165)
bust("brune",   450, 578, 716, 1210, lambda c: brune_fix(erase_color(
        erase_color(c, (0, 0, c.width, 300), sage), (0, 0, c.width, 300),
        lambda r, gg, b: (b > gg + 40) | (b > r + 40))))
def fix_violet(c):
    c = erase_color(c, (0, 0, c.width, 60), lambda r, gg, b: (gg > r + 8) & (b > r + 8))
    c = erase_color(c, (0, 0, c.width, 70), lambda r, gg, b: (r > gg + 25) & (gg >= b - 5))
    return erase_color(c, (int(c.width*0.57), 0, c.width, int(c.height*0.43)), lambda r, gg, b: b < gg + 25)
bust("violette", 685, 540, 960, 1000, fix_violet)

# --- Décors
n = Image.open(src + "4.jpg").convert("RGB")
save(n.crop((150, 135, 1395, 1830)), "bg-pyramides.webp", 80)
d = Image.open(src + "5.jpg").convert("RGB")
save(d.crop((0, 592, 1542, 1378)), "bg-desert.webp", 82)
save(d.crop((133, 122, 543, 545)), "bg-regard.webp", 80)
print("ok")
