"""Détourage affiné : retire les liserés blancs/gris restants autour des personnages (sans retoucher le dessin).
Usage : python3 -I refine_cutouts.py <dossier_sources_images> <dossier_img>"""
import sys
from collections import deque
import numpy as np
from PIL import Image, ImageFilter

src, out = sys.argv[1].rstrip("/") + "/", sys.argv[2].rstrip("/") + "/"

def flood_white(rgb, thr):
    h, w, _ = rgb.shape; near = rgb.min(axis=2) >= thr; seen = np.zeros((h, w), bool); dq = deque()
    for x in range(w):
        for y in (0, h-1):
            if near[y, x] and not seen[y, x]: seen[y, x] = True; dq.append((y, x))
    for y in range(h):
        for x in (0, w-1):
            if near[y, x] and not seen[y, x]: seen[y, x] = True; dq.append((y, x))
    while dq:
        y, x = dq.popleft()
        for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny, nx = y+dy, x+dx
            if 0 <= ny < h and 0 <= nx < w and near[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True; dq.append((ny, nx))
    return seen

def pockets(rgb, alpha, thr=225, minsize=60):
    """poches blanches enfermées entre deux membres / personnages"""
    white = (rgb.min(axis=2) >= thr) & (alpha > 0); h, w = white.shape; seen = np.zeros((h, w), bool)
    for sy, sx in zip(*np.nonzero(white)):
        if seen[sy, sx]: continue
        comp = [(sy, sx)]; seen[sy, sx] = True; i = 0
        while i < len(comp):
            y, x = comp[i]; i += 1
            for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                ny, nx = y+dy, x+dx
                if 0 <= ny < h and 0 <= nx < w and white[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True; comp.append((ny, nx))
        if len(comp) >= minsize:
            for y, x in comp: alpha[y, x] = 0

def finish(rgb, alpha, band=4, erode=1):
    """dégradé de matte sur la bande de bord : tout ce qui est blanc/gris pâle neutre disparaît"""
    al = Image.fromarray(alpha.astype("uint8"))
    near = np.asarray(al.filter(ImageFilter.MinFilter(2*band+1))) < 40
    mx, mn = rgb.max(axis=2), rgb.min(axis=2); sat = mx - mn
    pale = (mn >= 175) & (sat <= 55)
    grey = (sat <= 22) & (mx >= 120) & (mx <= 215)
    kill = near & (pale | grey) & (alpha > 0)
    alpha = alpha.copy(); alpha[kill] = 0
    al = Image.fromarray(alpha.astype("uint8"))
    for _ in range(erode): al = al.filter(ImageFilter.MinFilter(3))
    al = al.filter(ImageFilter.GaussianBlur(.8))
    a = np.asarray(al).copy(); a[a < 14] = 0
    return a

def save(rgb, alpha, name, maxsize=None):
    im = Image.fromarray(np.dstack([rgb.astype("uint8"), alpha])); bb = im.getbbox(); im = im.crop(bb)
    if maxsize: im.thumbnail(maxsize, Image.LANCZOS)
    im.save(out + name, lossless=True, method=6); print(name, im.size)

# --- sources déjà détourées (PNG/WebP avec transparence)
for s, n in [("10.png", "violette.webp"), ("11.png", "brune.webp")]:
    im = Image.open(src + s).convert("RGBA"); a = np.asarray(im)
    rgb, al = a[..., :3].astype(int), a[..., 3].astype(int)
    al = finish(rgb, al, band=4, erode=1)
    if n == "violette.webp":                       # le bord droit de la source est coupé net : on l'estompe
        w = al.shape[1]; ramp = np.clip((w - 1 - np.arange(w)) / 16.0, 0, 1)
        al = (al * ramp[None, :]).astype("uint8")
    save(rgb, al, n, (900, 1100))

# --- Rose en pied (JPG sur fond blanc)
rgb = np.asarray(Image.open(src + "8.jpg").convert("RGB")).astype(int)
al = np.where(flood_white(rgb, 232), 0, 255); pockets(rgb, al); al = finish(rgb, al, band=3, erode=1)
save(rgb, al, "rose-pied.webp", (700, 1500))

# --- Les six Elles (3.jpg, CMYK -> RGB), pleine définition
g = Image.open(src + "3.jpg").convert("RGB"); rgb = np.asarray(g).astype(int)
al = np.where(flood_white(rgb, 232), 0, 255); pockets(rgb, al, minsize=80); al = finish(rgb, al, band=3, erode=1)
save(rgb, al, "elles-groupe.webp", (1400, 1400))
