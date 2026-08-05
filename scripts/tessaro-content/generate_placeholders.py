#!/usr/bin/env python3
"""Genere les photos placeholder des pages Chauffage / Sanitaire.

Ce ne sont pas de vraies photos : ce sont des visuels simples, avec le nom
du sujet ecrit dessus, qui servent a ce que les pages ne soient pas vides en
attendant les vraies photos. Elles sont faciles a reperer dans la
mediatheque WordPress et a remplacer ensuite.

Ne regenere jamais un fichier deja present dans media/ : si vous deposez une
vraie photo sous le meme nom (ex: hero-chauffage.jpg), elle sera conservee.
"""
import os

from PIL import Image, ImageDraw, ImageFont

from pages_config import PAGES

WIDTH, HEIGHT = 1200, 800

_FONT_CANDIDATES_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:\\Windows\\Fonts\\arialbd.ttf",
]
_FONT_CANDIDATES_REGULAR = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "C:\\Windows\\Fonts\\arial.ttf",
]


def _load_font(size, bold=True):
    for path in (_FONT_CANDIDATES_BOLD if bold else _FONT_CANDIDATES_REGULAR):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def make_placeholder(path, label, color):
    img = Image.new("RGB", (WIDTH, HEIGHT), color)
    draw = ImageDraw.Draw(img)

    lighter = tuple(min(255, c + 25) for c in color)
    draw.polygon([(0, HEIGHT), (WIDTH * 0.55, HEIGHT), (WIDTH, 0), (WIDTH * 0.75, 0)], fill=lighter)

    tag_font = _load_font(28)
    label_font = _load_font(46)

    tag = "PHOTO A REMPLACER"
    tag_w = draw.textlength(tag, font=tag_font)
    pad = 16
    box = (WIDTH / 2 - tag_w / 2 - pad, 60, WIDTH / 2 + tag_w / 2 + pad, 60 + 28 + pad * 2)
    draw.rounded_rectangle(box, radius=8, fill=(255, 255, 255))
    draw.text((WIDTH / 2, 60 + pad + 14), tag, font=tag_font, fill=color, anchor="mm")

    lines = _wrap_text(draw, label, label_font, WIDTH - 160)
    line_height = label_font.size + 14
    total_h = line_height * len(lines)
    y = HEIGHT / 2 - total_h / 2
    for line in lines:
        draw.text((WIDTH / 2, y + line_height / 2), line, font=label_font, fill=(255, 255, 255), anchor="mm")
        y += line_height

    img.save(path, "JPEG", quality=87)


def ensure_images(media_dir):
    os.makedirs(media_dir, exist_ok=True)
    created = []
    for page in PAGES:
        for image in page["images"]:
            path = os.path.join(media_dir, image["filename"])
            if os.path.exists(path):
                continue
            make_placeholder(path, image["alt"], image["color"])
            created.append(path)
    return created


if __name__ == "__main__":
    media_dir = os.path.join(os.path.dirname(__file__), "media")
    created = ensure_images(media_dir)
    if created:
        print(f"{len(created)} image(s) placeholder generee(s) dans {media_dir} :")
        for path in created:
            print(f"  - {os.path.basename(path)}")
    else:
        print(f"Rien a generer : toutes les images existent deja dans {media_dir}")
