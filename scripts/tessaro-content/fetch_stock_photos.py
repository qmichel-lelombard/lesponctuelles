#!/usr/bin/env python3
"""Telecharge des photos libres de droit et les installe dans media/ pour
remplacer temporairement les images placeholder.

Marche a suivre :
1. Choisissez des photos libres de droit, par exemple sur Unsplash
   (unsplash.com) ou Pexels (pexels.com) -- gratuites, utilisation
   commerciale autorisee, sans attribution obligatoire. Voir les suggestions
   de recherche par photo dans README.md.
2. Sur la page de la photo choisie, recuperez l'URL directe du fichier image
   (bouton telecharger, ou clic droit sur l'image > "Copier l'adresse de
   l'image").
3. Collez cette URL dans STOCK_PHOTO_URLS ci-dessous, pour la cle
   correspondante.
4. Lancez : python3 fetch_stock_photos.py
5. Relancez : python3 create_pages.py --dest https://guillaumetessaro.be \
     --status draft --overwrite

Les images sont recadrees au centre en 1200x800 (meme format que les
placeholders) pour s'inserer proprement dans la mise en page. Ce sont des
photos temporaires : remplacez-les par les vraies photos de chantier des que
possible (voir README.md, section "Remplacer les photos").
"""
import io
import os

import requests
from PIL import Image

from pages_config import PAGES

TARGET_SIZE = (1200, 800)  # doit rester coherent avec generate_placeholders.py

_RESAMPLE = getattr(getattr(Image, "Resampling", None), "LANCZOS", None) or Image.LANCZOS

# Collez ici l'URL directe du FICHIER IMAGE (pas l'URL de la page web) pour
# chaque cle qui vous interesse. Laissez les autres vides : elles garderont
# leur placeholder genere. Cles disponibles (voir pages_config.py) :
#   hero-chauffage, chaudiere-condensation, pompe-a-chaleur,
#   entretien-chaudiere, radiateurs, depannage-chauffage,
#   hero-sanitaire, installation-sanitaire, renovation-sdb, chauffe-eau,
#   depannage-plomberie, robinetterie
STOCK_PHOTO_URLS = {
   # "hero-chauffage": "https://images.pexels.com/photos/29226620/pexels-photo-29226620.jpeg",
   # "chaudiere-condensation": https://www.pexels.com/fr-fr/photo/reparer-entretien-maintenance-machinerie-7859953/
   # "pompe-a-chaleur": https://images.pexels.com/photos/20046692/pexels-photo-20046692.jpeg
   # "entretien-chaudiere": https://images.pexels.com/photos/34054464/pexels-photo-34054464.jpeg
   # "pose-radiateur-chauffage": https://images.pexels.com/photos/5691521/pexels-photo-5691521.jpeg
   # "depannage-chauffage": https://images.pexels.com/photos/33531820/pexels-photo-33531820.jpeg
   # "hero-sanitaire": https://images.pexels.com/photos/7587731/pexels-photo-7587731.jpeg
   # "installation-sanitaire": https://images.pexels.com/photos/5691486/pexels-photo-5691486.jpeg
   # "renovation-salle-de-bain": https://images.pexels.com/photos/8146338/pexels-photo-8146338.jpeg
   # "installation-chauffe-eau": https://images.pexels.com/photos/29206492/pexels-photo-29206492.jpeg
   # "depannage-fuite": https://images.pexels.com/photos/16509869/pexels-photo-16509869.jpeg
   # "pose-robinetterie": https://images.pexels.com/photos/6419128/pexels-photo-6419128.jpeg
}


def _center_crop_to_ratio(img, target_w, target_h):
    target_ratio = target_w / target_h
    w, h = img.size
    ratio = w / h
    if ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    return img.resize((target_w, target_h), _RESAMPLE)


def _filename_for_key(key):
    for page in PAGES:
        for image in page["images"]:
            if image["key"] == key:
                return image["filename"]
    raise SystemExit(f"Cle inconnue dans STOCK_PHOTO_URLS : '{key}' (voir pages_config.py pour la liste valide)")


def fetch(key, url, media_dir):
    filename = _filename_for_key(key)
    resp = requests.get(url, timeout=30, headers={"User-Agent": "tessaro-content-script/1.0"})
    resp.raise_for_status()
    img = Image.open(io.BytesIO(resp.content)).convert("RGB")
    img = _center_crop_to_ratio(img, *TARGET_SIZE)
    path = os.path.join(media_dir, filename)
    img.save(path, "JPEG", quality=88)
    print(f"  {filename} <- {url}")


def main():
    urls = {k: v for k, v in STOCK_PHOTO_URLS.items() if v}
    if not urls:
        raise SystemExit(
            "Aucune URL renseignee dans STOCK_PHOTO_URLS. Ouvrez ce fichier, "
            "collez des URLs d'images libres de droit pour les cles qui vous "
            "interessent, puis relancez ce script."
        )
    media_dir = os.path.join(os.path.dirname(__file__), "media")
    os.makedirs(media_dir, exist_ok=True)
    print(f"Telechargement de {len(urls)} photo(s) dans {media_dir} ...")
    for key, url in urls.items():
        fetch(key, url, media_dir)
    print("Termine. Relancez create_pages.py --overwrite pour pousser ces photos sur le site.")


if __name__ == "__main__":
    main()
