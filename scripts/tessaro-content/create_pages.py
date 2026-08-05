#!/usr/bin/env python3
"""Cree (ou met a jour) les pages "Chauffage", "Sanitaire" et "Contact" sur un site WordPress.

S'authentifie avec un Application Password WordPress (wp-admin > Utilisateurs
> Profil > Mots de passe d'application), envoye en HTTP Basic Auth sur HTTPS.
Ne jamais passer le mot de passe en ligne de commande : utilisez la variable
d'environnement WP_DEST_APP_PASSWORD.

Genere localement de simples photos placeholder (voir
generate_placeholders.py), les televerse dans la mediatheque WordPress, puis
cree les pages en statut "draft" (brouillon) par defaut afin de les relire
dans wp-admin avant publication. La page Contact affiche les coordonnees
(pages_config.py > CONTACT_INFO) et un emplacement pour le shortcode d'un
formulaire de contact (voir --form-shortcode).

Exemple :
  export WP_DEST_USER=admin
  export WP_DEST_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"
  python3 create_pages.py --dest https://guillaumetessaro.be --status draft
"""
import argparse
import os
import re
import sys
import urllib.parse

import requests
from requests.auth import HTTPBasicAuth

from generate_placeholders import ensure_images
from pages_config import (
    CONTACT_FORM_SHORTCODE,
    CONTACT_INFO,
    FOOTER_LOGO_URL,
    FOOTER_MAP_QUERY,
    FOOTER_PARTIAL,
    PAGES,
)

IMG_URL_TOKEN_RE = re.compile(r"<!--IMGURL:([a-z0-9-]+)-->")
CSS_PATH = os.path.join(os.path.dirname(__file__), "assets", "tessaro-pages.css")

FORM_MISSING_HTML = (
    '<div class="gt-form-missing">Formulaire de contact non configure pour le '
    "moment. Installez Contact Form 7 (ou un autre plugin de formulaire), "
    "creez le formulaire dans wp-admin, puis relancez ce script avec "
    "<code>--form-shortcode '[contact-form-7 id=\"...\" title=\"...\"]'</code> "
    "-- voir README.md.</div>"
)

FACEBOOK_ICON_SVG = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
    '<path d="M22 12.06C22 6.505 17.523 2 12 2S2 6.505 2 12.06c0 5.02 3.657 9.184 8.438 9.94v-7.03H7.898v-2.91h2.54V9.845'
    "c0-2.507 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.462h-1.26c-1.243 0-1.63.771-1.63 1.562v1.878h2.773"
    'l-.443 2.91h-2.33V22c4.78-.756 8.437-4.92 8.437-9.94Z"/></svg>'
)


def render_footer(logo_url):
    with open(FOOTER_PARTIAL, encoding="utf-8") as f:
        footer_html = f.read()

    if logo_url:
        logo_html = f'<img src="{logo_url}" alt="Guillaume Tessaro" class="gt-footer-logo-img">'
    else:
        logo_html = '<div class="gt-footer-logo">Guillaume<br>Tessaro</div>'

    if CONTACT_INFO["facebook_url"]:
        facebook_html = (
            f'<a class="gt-footer-fb" href="{CONTACT_INFO["facebook_url"]}" '
            'target="_blank" rel="noopener" aria-label="Facebook">'
            f"{FACEBOOK_ICON_SVG}</a>"
        )
    else:
        facebook_html = ""

    tokens = {
        "<!--FOOTER_LOGO_HTML-->": logo_html,
        "<!--FOOTER_FACEBOOK_HTML-->": facebook_html,
        "<!--FOOTER_MAP_QUERY-->": urllib.parse.quote(FOOTER_MAP_QUERY),
        "<!--CONTACT_PHONE_TEL-->": CONTACT_INFO["phone_tel"],
        "<!--CONTACT_PHONE_DISPLAY-->": CONTACT_INFO["phone_display"],
        "<!--CONTACT_ADDRESS_SHORT-->": CONTACT_INFO["address_short"],
        "<!--CONTACT_HOURS_SHORT-->": CONTACT_INFO["hours_short"],
    }
    for token, value in tokens.items():
        footer_html = footer_html.replace(token, value)
    return footer_html


def get_auth():
    user = os.environ.get("WP_DEST_USER")
    password = os.environ.get("WP_DEST_APP_PASSWORD")
    if not user or not password:
        raise SystemExit(
            "Set WP_DEST_USER and WP_DEST_APP_PASSWORD environment variables "
            "(create an Application Password in wp-admin under Users > Profile)."
        )
    return HTTPBasicAuth(user, password)


def _raise_for_status_verbose(resp):
    if resp.status_code >= 400:
        raise SystemExit(
            f"HTTP {resp.status_code} sur {resp.url}\n"
            f"Reponse du serveur : {resp.text[:1000]}"
        )


def find_page_id_by_slug(base_url, auth, session, slug):
    resp = session.get(f"{base_url}/wp-json/wp/v2/pages", params={"slug": slug, "status": "any"}, auth=auth)
    _raise_for_status_verbose(resp)
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


def render_content(page, media_by_key, css, extra_tokens=None):
    with open(page["content_file"], encoding="utf-8") as f:
        template = f.read()

    def replace(match):
        return media_by_key[match.group(1)]["source_url"]

    html = IMG_URL_TOKEN_RE.sub(replace, template)
    for token, value in (extra_tokens or {}).items():
        html = html.replace(token, value)
    style_block = f"<style>\n{css}\n</style>\n"
    return html.replace("<!-- wp:html -->", "<!-- wp:html -->\n" + style_block, 1)


def create_or_update_page(base_url, auth, session, page, parent_id, status, overwrite, media_dir, css, extra_tokens):
    existing_id = find_page_id_by_slug(base_url, auth, session, page["slug"])
    if existing_id and not overwrite:
        print(f"  skip (already exists, id={existing_id}): /{page['slug']}/ -- use --overwrite to update")
        return

    media_by_key = {}
    for image in page["images"]:
        path = os.path.join(media_dir, image["filename"])
        media_by_key[image["key"]] = upload_media(base_url, auth, session, path, image["alt"])

    content = render_content(page, media_by_key, css, extra_tokens)

    payload = {
        "title": page["title"],
        "slug": page["slug"],
        "content": content,
        "excerpt": page["excerpt"],
        "status": status,
    }
    if page["images"]:
        payload["featured_media"] = media_by_key[page["images"][0]["key"]]["id"]
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
    parser.add_argument("--form-shortcode", default=None, help="Shortcode du formulaire de contact (ex: Contact Form 7) a inserer sur la page Contact ; surcharge CONTACT_FORM_SHORTCODE de pages_config.py")
    parser.add_argument("--logo-url", default=None, help="URL du fichier logo a utiliser dans le pied de page ; surcharge FOOTER_LOGO_URL de pages_config.py")
    args = parser.parse_args()

    base_url = args.dest.rstrip("/")
    auth = get_auth()
    session = requests.Session()
    session.headers.update({"User-Agent": "tessaro-content-script/1.0"})

    media_dir = os.path.join(os.path.dirname(__file__), "media")
    ensure_images(media_dir)

    with open(CSS_PATH, encoding="utf-8") as f:
        css = f.read()

    form_shortcode = args.form_shortcode or CONTACT_FORM_SHORTCODE or FORM_MISSING_HTML
    logo_url = args.logo_url or FOOTER_LOGO_URL
    extra_tokens = {
        "<!--FORMSHORTCODE-->": form_shortcode,
        "<!--CONTACT_PHONE_TEL-->": CONTACT_INFO["phone_tel"],
        "<!--CONTACT_PHONE_DISPLAY-->": CONTACT_INFO["phone_display"],
        "<!--CONTACT_EMAIL-->": CONTACT_INFO["email"],
        "<!--CONTACT_ADDRESS-->": CONTACT_INFO["address"],
        "<!--CONTACT_HOURS-->": CONTACT_INFO["hours"],
        "<!--SITE_FOOTER-->": render_footer(logo_url),
    }

    parent_id = None
    if args.parent_slug:
        parent_id = find_page_id_by_slug(base_url, auth, session, args.parent_slug)
        if not parent_id:
            print(f"warning: parent page '{args.parent_slug}' introuvable, creation des pages au premier niveau", file=sys.stderr)

    print(f"Creation/mise a jour de {len(PAGES)} page(s) sur {base_url} en '{args.status}' ...")
    for page in PAGES:
        create_or_update_page(base_url, auth, session, page, parent_id, args.status, args.overwrite, media_dir, css, extra_tokens)

    print("Termine. Relisez les pages dans wp-admin avant de passer en 'publish', et ajoutez-les a votre menu.")


if __name__ == "__main__":
    main()
