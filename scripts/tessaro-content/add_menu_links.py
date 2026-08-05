#!/usr/bin/env python3
"""Ajoute Chauffage / Sanitaire / Contact au menu de navigation WordPress.

S'authentifie avec un Application Password WordPress (meme principe que
create_pages.py). Utilise l'API REST des menus (wp/v2/menus et
wp/v2/menu-items, disponible nativement depuis WordPress 5.9).

Sans --menu-id, liste les menus existants pour vous laisser choisir. Ignore
les pages deja presentes dans le menu cible (pas de doublon si vous
relancez). Les elements sont ajoutes a la fin du menu -- reordonnez-les
ensuite si besoin dans Apparence > Menus (glisser-deposer).

Exemple :
  export WP_DEST_USER=admin
  export WP_DEST_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"
  python3 add_menu_links.py --dest https://guillaumetessaro.be --menu-id 3
"""
import argparse
import os
import sys

import requests
from requests.auth import HTTPBasicAuth

from pages_config import PAGES

# Pages a ajouter au menu, dans cet ordre. Modifiez cette liste si vous
# voulez en ajouter/retirer.
MENU_SLUGS = ["chauffage", "sanitaire", "contact"]


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
        raise SystemExit(f"HTTP {resp.status_code} sur {resp.url}\nReponse du serveur : {resp.text[:1000]}")


def list_menus(base_url, auth, session):
    resp = session.get(f"{base_url}/wp-json/wp/v2/menus", params={"per_page": 100}, auth=auth)
    _raise_for_status_verbose(resp)
    return resp.json()


def find_page_id_by_slug(base_url, auth, session, slug):
    resp = session.get(f"{base_url}/wp-json/wp/v2/pages", params={"slug": slug, "status": "any"}, auth=auth)
    _raise_for_status_verbose(resp)
    data = resp.json()
    return data[0]["id"] if data else None


def get_menu_items(base_url, auth, session, menu_id):
    resp = session.get(f"{base_url}/wp-json/wp/v2/menu-items", params={"menus": menu_id, "per_page": 100}, auth=auth)
    _raise_for_status_verbose(resp)
    return resp.json()


def add_menu_item(base_url, auth, session, menu_id, page_id, title):
    payload = {
        "title": title,
        "status": "publish",
        "type": "post_type",
        "object": "page",
        "object_id": page_id,
        "menus": menu_id,
    }
    resp = session.post(f"{base_url}/wp-json/wp/v2/menu-items", json=payload, auth=auth)
    _raise_for_status_verbose(resp)
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dest", required=True, help="URL du site, ex: https://guillaumetessaro.be")
    parser.add_argument("--menu-id", type=int, default=None, help="ID du menu cible (voir la liste affichee si omis)")
    args = parser.parse_args()

    base_url = args.dest.rstrip("/")
    auth = get_auth()
    session = requests.Session()
    session.headers.update({"User-Agent": "tessaro-content-script/1.0"})

    menus = list_menus(base_url, auth, session)
    if not menus:
        raise SystemExit("Aucun menu trouve sur ce site (Apparence > Menus pour en creer un).")

    if args.menu_id is None:
        print("Menus disponibles :")
        for menu in menus:
            print(f"  id={menu['id']} -- {menu['name']} ({menu.get('count', '?')} element(s))")
        if len(menus) == 1:
            args.menu_id = menus[0]["id"]
            print(f"Un seul menu trouve, utilisation de id={args.menu_id}.")
        else:
            raise SystemExit("Plusieurs menus trouves : relancez avec --menu-id <id> pour choisir.")

    existing_items = get_menu_items(base_url, auth, session, args.menu_id)
    existing_object_ids = {item.get("object_id") for item in existing_items if item.get("object") == "page"}

    print(f"Ajout des pages {MENU_SLUGS} au menu id={args.menu_id} sur {base_url} ...")
    for slug in MENU_SLUGS:
        page = next((p for p in PAGES if p["slug"] == slug), None)
        title = page["title"] if page else slug.capitalize()
        page_id = find_page_id_by_slug(base_url, auth, session, slug)
        if not page_id:
            print(f"  ERROR: page '/{slug}/' introuvable sur le site (a-t-elle ete publiee ?)", file=sys.stderr)
            continue
        if page_id in existing_object_ids:
            print(f"  skip (deja dans le menu) : {title} -> /{slug}/")
            continue
        item = add_menu_item(base_url, auth, session, args.menu_id, page_id, title)
        print(f"  ajoute : {title} -> /{slug}/ (menu-item id={item['id']})")

    print("Termine. Verifiez l'ordre des elements dans Apparence > Menus et reordonnez si besoin.")


if __name__ == "__main__":
    main()
