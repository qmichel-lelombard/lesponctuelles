#!/usr/bin/env python3
"""Create a "real wedding" blog post as a DRAFT, cloned from an existing article.

Reads a JSON spec, resizes + uploads the photos to the media library, then
creates a draft post whose Elementor layout (_elementor_data) is a copy of an
existing article (--base-id) with the hero, intro text, gallery, photo credit
and testimonial replaced.

Spec (JSON):
  {
    "title": "Marine & Jonathan",
    "slug": "marine-jonathan",
    "date": "2025-10-11",                 # wedding date
    "categories": [8, 7],                  # 8 = Coordination, 7 = Décoration
    "photo_dir": "/path/to/originals",
    "hero": "Couple-68.jpg",               # landscape; also the featured image
    "gallery": ["Dinner-1.jpg", ...],      # in display order
    "intro_html": "<p>...</p>",            # intro + vendors list
    "credits_html": "<p>© Crédits photos : ...</p>",
    "testimonial": {"text": "...", "image": "Couple-17.jpg"}   # optional
  }

Auth: set WP_DEST_USER / WP_DEST_APP_PASSWORD, or leave both unset when an
outbound proxy injects the credentials for the site.

Example:
  python3 create_wedding_post.py --dest https://unjourencouleurs.be \
      --base-id 5219 --spec marine-jonathan.json
"""
import argparse
import io
import json
import os
import sys

import requests
from PIL import Image, ImageOps
from requests.auth import HTTPBasicAuth

PORTRAIT = (850, 1276)    # sizes used by the existing articles
LANDSCAPE = (1400, 933)


def get_auth():
    user, password = os.environ.get("WP_DEST_USER"), os.environ.get("WP_DEST_APP_PASSWORD")
    return HTTPBasicAuth(user, password) if user and password else None


def resized_jpeg(path, exact=False):
    """Return (bytes, orientation) of the photo scaled to the site's standard size.

    With exact=True the photo is centre-cropped to exactly that size: the blog
    grid misaligns when cover images differ by even a pixel or two in ratio.
    """
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    orientation = "paysage" if im.width > im.height else "portrait"
    size = LANDSCAPE if orientation == "paysage" else PORTRAIT
    if exact:
        im = ImageOps.fit(im, size, Image.LANCZOS)
    else:
        im.thumbnail(size, Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=82, optimize=True, progressive=True)
    return buf.getvalue(), orientation


def upload(session, api, auth, data, filename, alt):
    resp = session.post(
        f"{api}/media", auth=auth, data=data,
        headers={"Content-Type": "image/jpeg", "Content-Disposition": f'attachment; filename="{filename}"'},
    )
    resp.raise_for_status()
    media = resp.json()
    session.post(f"{api}/media/{media['id']}", auth=auth, json={"alt_text": alt}).raise_for_status()
    return {"id": media["id"], "url": media["source_url"]}


def find_widgets(elements, widget_type):
    for el in elements:
        if el.get("widgetType") == widget_type:
            yield el
        yield from find_widgets(el.get("elements", []), widget_type)


def remove_widgets(elements, widget_type):
    elements[:] = [el for el in elements if el.get("widgetType") != widget_type]
    for el in elements:
        remove_widgets(el.get("elements", []), widget_type)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dest", required=True, help="Site base URL, e.g. https://unjourencouleurs.be")
    parser.add_argument("--base-id", required=True, type=int, help="ID of the existing article to clone the layout from")
    parser.add_argument("--spec", required=True, help="Path to the JSON spec")
    parser.add_argument("--uploaded", help="JSON file caching uploaded media (reused on re-runs to avoid duplicates)")
    args = parser.parse_args()

    spec = json.load(open(args.spec, encoding="utf-8"))
    api = args.dest.rstrip("/") + "/wp-json/wp/v2"
    auth, session = get_auth(), requests.Session()

    if session.get(f"{api}/posts", auth=auth, params={"slug": spec["slug"], "status": "any"}).json():
        sys.exit(f"A post with slug '{spec['slug']}' already exists; aborting.")

    base = session.get(f"{api}/posts/{args.base_id}", auth=auth, params={"context": "edit"})
    base.raise_for_status()
    base = base.json()
    tree = json.loads(base["meta"]["_elementor_data"])

    # --- photos -----------------------------------------------------------
    cache_path = args.uploaded or os.path.splitext(args.spec)[0] + ".uploaded.json"
    cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}
    counters = {"portrait": 0, "paysage": 0}
    wanted = [spec["hero"]] + spec["gallery"]
    if spec.get("testimonial", {}).get("image"):
        wanted.append(spec["testimonial"]["image"])
    for name in dict.fromkeys(wanted):
        is_hero = name == spec["hero"]
        data, orientation = resized_jpeg(os.path.join(spec["photo_dir"], name), exact=is_hero)
        if is_hero and orientation != "paysage":
            sys.exit(f"Hero image '{name}' must be landscape (it is cropped to {LANDSCAPE[0]}x{LANDSCAPE[1]}).")
        counters[orientation] += 1
        if name in cache:
            continue
        filename = f"{spec['slug']}-{orientation}-{counters[orientation]}.jpg"
        alt = f"Mariage {spec['title']} - Un Jour en Couleurs wedding planner"
        cache[name] = upload(session, api, auth, data, filename, alt)
        json.dump(cache, open(cache_path, "w"), indent=1)
        print(f"uploaded {name} -> {cache[name]['url']}")

    # --- layout -----------------------------------------------------------
    hero = cache[spec["hero"]]
    tree[0]["settings"]["background_image"] = {"url": hero["url"], "id": hero["id"], "alt": "", "source": "library", "size": ""}
    day, month, year = spec["date"][8:10], spec["date"][5:7], spec["date"][:4]
    next(find_widgets(tree, "oew-animated-heading"))["settings"]["animated_heading"] = f"{spec['title']} - {day}/{month}/{year}"

    editors = list(find_widgets(tree, "text-editor"))
    editors[0]["settings"]["editor"] = spec["intro_html"]
    editors[1]["settings"]["editor"] = spec["credits_html"]
    next(find_widgets(tree, "oew-image-gallery"))["settings"]["gallery_images"] = [cache[n] for n in spec["gallery"]]

    testimonial = spec.get("testimonial")
    if testimonial:
        months = "janvier février mars avril mai juin juillet août septembre octobre novembre décembre".split()
        slide = next(find_widgets(tree, "oew-testimonial-carousel"))["settings"]["testimonial_slider"][0]
        slide["testimonial_content"] = f'" {testimonial["text"]} "'
        slide["testimonial_name"] = spec["title"]
        slide["testimonial_company"] = f"{int(day)} {months[int(month) - 1]} {year}"
        img = cache[testimonial["image"]]
        slide["testimonial_image"] = {"url": img["url"], "id": img["id"], "alt": "", "source": "library", "size": ""}
    else:
        remove_widgets(tree, "oew-testimonial-carousel")

    meta = {k: v for k, v in base["meta"].items() if k.startswith("_elementor") or k == "ocean_disable_margins"}
    meta["_elementor_data"] = json.dumps(tree)
    resp = session.post(f"{api}/posts", auth=auth, json={
        "title": spec["title"], "slug": spec["slug"], "status": "draft",
        "date": f"{spec['date']}T14:00:00", "categories": spec["categories"],
        "featured_media": hero["id"], "content": spec["intro_html"],
        "comment_status": base["comment_status"], "ping_status": base["ping_status"], "meta": meta,
    })
    resp.raise_for_status()
    post = resp.json()
    print(f"Draft created: id={post['id']}  preview: {args.dest.rstrip('/')}/?p={post['id']}&preview=true")
    print(f"Edit: {args.dest.rstrip('/')}/wp-admin/post.php?post={post['id']}&action=elementor")


if __name__ == "__main__":
    main()
