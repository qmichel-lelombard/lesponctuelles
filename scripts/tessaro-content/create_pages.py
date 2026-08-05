#!/usr/bin/env python3
"""Cree (ou met a jour) les pages "Chauffage" et "Sanitaire" sur un site WordPress.

S'authentifie avec un Application Password WordPress (wp-admin > Utilisateurs
> Profil > Mots de passe d'application), envoye en HTTP Basic Auth sur HTTPS.
Ne jamais passer le mot de passe en ligne de commande : utilisez la variable
d'environnement WP_DEST_APP_PASSWORD.

Genere localement de simples photos placeholder (voir
generate_placeholders.py), les televerse dans la mediatheque WordPress, puis
cree les deux pages en statut "draft" (brouillon) par defaut afin de les
relire dans wp-admin avant publication.

Exemple :
  export WP_DEST_USER=admin
  export WP_DEST_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"
  python3 create_pages.py --dest https://guillaumetessaro.be --status draft
"""
import argparse
import os
import re
import sys

import requests
from requests.auth import HTTPBasicAuth

from generate_placeholders import ensure_images
from pages_config import PAGES

IMG_TOKEN_RE = re.compile(r"<!--IMG:([a-z0-9-]+)-->")


def get_auth():
    user = os.environ.get("WP_DEST_USER")
    password = os.environ.get("WP_DEST_APP_PASSWORD")
    if not user or not password:
        raise SystemExit(
            "Set WP_DEST_USER and WP_DEST_APP_PASSWORD environment variables "
            "(create an Application Password in wp-admin under Users > Profile)."
        )
    return HTTPBasicAuth(user, password)


def find_page_id_by_slug(base_url, auth, session, slug):
    resp = session.get(f"{base_url}/wp-json/wp/v2/pages", params={"slug": slug, "status": "any"}, auth=auth)
    resp.raise_for_status()
    data = resp.json()
    return data[0]["id"] if data else None


def upload_media(base_url, auth, session, file_path, alt_text):
    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        resp = session.post(
            f"{base_url}/wp-json/wp/v2/media",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "image/jpeg",
            },
            data=f.read(),
            auth=auth,
        )
    if resp.status_code not in (200, 201):
        raise SystemExit(f"Media upload failed for {filename}: {resp.status_code} {resp.text[:300]}")
    media = resp.json()

    session.post(
        f"{base_url}/wp-json/wp/v2/media/{media['id']}",
        json={"alt_text": alt_text, "title": alt_text},
        auth=auth,
    )
    return media


def build_image_block(media, alt_text):
    escaped_alt = alt_text.replace('"', "&quot;")
    return (
        '<!-- wp:image {"id":%d,"sizeSlug":"large","linkDestination":"none"} -->\n'
        '<figure class="wp-block-image size-large"><img src="%s" alt="%s" class="wp-image-%d"/></figure>\n'
        "<!-- /wp:image -->"
    ) % (media["id"], media["source_url"], escaped_alt, media["id"])


def render_content(page, media_by_key):
    with open(page["content_file"], encoding="utf-8") as f:
        template = f.read()

    def replace(match):
        key = match.group(1)
        media = media_by_key[key]
        image_spec = next(i for i in page["images"] if i["key"] == key)
        return build_image_block(media, image_spec["alt"])

    return IMG_TOKEN_RE.sub(replace, template)


def create_or_update_page(base_url, auth, session, page, parent_id, status, overwrite, media_dir):
    existing_id = find_page_id_by_slug(base_url, auth, session, page["slug"])
    if existing_id and not overwrite:
        print(f"  skip (already exists, id={existing_id}): /{page['slug']}/ -- use --overwrite to update")
        return

    media_by_key = {}
    for image in page["images"]:
        path = os.path.join(media_dir, image["filename"])
        media_by_key[image["key"]] = upload_media(base_url, auth, session, path, image["alt"])

    content = render_content(page, media_by_key)
    featured_media_id = media_by_key[page["images"][0]["key"]]["id"]

    payload = {
        "title": page["title"],
        "slug": page["slug"],
        "content": content,
        "excerpt": page["excerpt"],
        "status": status,
        "featured_media": featured_media_id,
    }
    if parent_id:
        payload["parent"] = parent_id

    if existing_id:
        resp = session.post(f"{base_url}/wp-json/wp/v2/pages/{existing_id}", json=payload, auth=auth)
    else:
        resp = session.post(f"{base_url}/wp-json/wp/v2/pages", json=payload, auth=auth)

    if resp.status_code not in (200, 201):
        print(f"  ERROR creating/updating '{page['slug']}': {resp.status_code} {resp.text[:300]}", file=sys.stderr)
        return

    result = resp.json()
    verb = "updated" if existing_id else "created"
    print(f"  {verb}: /{page['slug']}/ -> id={result['id']} ({result.get('link')})")
    print(f"    edit in wp-admin: {base_url}/wp-admin/post.php?post={result['id']}&action=edit")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dest", required=True, help="URL du site, ex: https://guillaumetessaro.be")
    parser.add_argument("--status", default="draft", choices=["draft", "publish", "pending"], help="Statut de creation (defaut: draft, a relire avant publication)")
    parser.add_argument("--parent-slug", default=None, help="Slug d'une page existante sous laquelle rattacher ces pages (ex: 'services'), si besoin")
    parser.add_argument("--overwrite", action="store_true", help="Met a jour la page si une page du meme slug existe deja, au lieu de l'ignorer")
    args = parser.parse_args()

    base_url = args.dest.rstrip("/")
    auth = get_auth()
    session = requests.Session()
    session.headers.update({"User-Agent": "tessaro-content-script/1.0"})

    media_dir = os.path.join(os.path.dirname(__file__), "media")
    ensure_images(media_dir)

    parent_id = None
    if args.parent_slug:
        parent_id = find_page_id_by_slug(base_url, auth, session, args.parent_slug)
        if not parent_id:
            print(f"warning: parent page '{args.parent_slug}' introuvable, creation des pages au premier niveau", file=sys.stderr)

    print(f"Creation/mise a jour de {len(PAGES)} page(s) sur {base_url} en '{args.status}' ...")
    for page in PAGES:
        create_or_update_page(base_url, auth, session, page, parent_id, args.status, args.overwrite, media_dir)

    print("Termine. Relisez les pages dans wp-admin avant de passer en 'publish', et ajoutez-les a votre menu.")


if __name__ == "__main__":
    main()
