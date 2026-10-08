"""Nettoie le liseré clair/gris autour des personnages détourés (sans toucher au dessin).
Usage : python3 -I defringe.py <dossier_img>   (à lancer UNE fois sur les fichiers fournis)"""
import sys
from collections import deque
import numpy as np
from PIL import Image, ImageFilter

def holes(a, thr=232, minsize=120):
    """Supprime les poches blanches enfermées entre deux membres / deux personnages."""
    rgb = a[..., :3].astype(int)
    white = (rgb.min(axis=2) >= thr) & (a[..., 3] > 0)
    h, w = white.shape; seen = np.zeros((h, w), bool)
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
            for y, x in comp: a[y, x, 3] = 0

def defringe(path, remove_holes=False):
    im = Image.open(path).convert("RGBA"); a = np.asarray(im).copy()
    if remove_holes: holes(a)
    al = Image.fromarray(a[..., 3])
    near = np.asarray(al.filter(ImageFilter.MinFilter(5))) < 30      # à moins de 2 px du vide franc
    rgb = a[..., :3].astype(int); mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    pale = (mn >= 200) & (mx - mn <= 45)                              # blanc cassé
    grey = (mx - mn <= 18) & (mx >= 130)                              # gris neutre
    a[..., 3][near & (pale | grey) & (a[..., 3] > 0)] = 0
    al = Image.fromarray(a[..., 3]).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.7))
    a[..., 3] = np.asarray(al)
    a[..., 3][a[..., 3] < 12] = 0
    Image.fromarray(a).save(path, lossless=True, method=6)

if __name__ == "__main__":
    d = sys.argv[1].rstrip("/") + "/"
    for n, hl in [("verte", 0), ("violette", 0), ("brune", 0), ("bleue", 0), ("blonde", 0), ("rose-pied", 1), ("elles-groupe", 1), ("rose", 1)]:
        defringe(d + n + ".webp", hl); print(n)
