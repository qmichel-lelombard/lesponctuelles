#!/usr/bin/env python3
"""Desactive les commentaires sur guillaumetessaro.be.

S'authentifie avec un Application Password WordPress (meme principe que les
autres scripts de ce dossier).

Actions effectuees :
1. Met le reglage global "default_comment_status" a "closed" (les nouveaux
   articles n'auront plus les commentaires ouverts par defaut -- equivaut a
   decocher "Autoriser les commentaires sur les nouveaux articles" dans
   wp-admin > Reglages > Discussion).
2. Ferme les commentaires (comment_status="closed") sur tous les articles et
   pages existants qui les ont actuellement ouverts.
3. Affiche le nombre de commentaires deja publies sur le site (ne les
   supprime pas -- a nettoyer vous-meme dans wp-admin > Commentaires si
   vous le souhaitez, notamment si beaucoup sont du spam).

Exemple :
  export WP_DEST_USER=admin
  export WP_DEST_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"
  python3 disable_comments.py --dest https://guillaumetessaro.be
"""
import argparse
import os

import requests
from requests.auth import HTTPBasicAuth

POST_TYPES = ["posts", "pages"]


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


def set_default_comment_status(base_url, auth, session):
    resp = session.post(f"{base_url}/wp-json/wp/v2/settings", json={"default_comment_status": "closed"}, auth=auth)
    _raise_for_status_verbose(resp)
    print("Reglage global : nouveaux articles = commentaires fermes par defaut.")


def close_existing_comments(base_url, auth, session, post_type):
    closed_count = 0
    page = 1
    while True:
        resp = session.get(
            f"{base_url}/wp-json/wp/v2/{post_type}",
            params={"per_page": 100, "page": page, "status": "any", "context": "edit"},
            auth=auth,
        )
        if resp.status_code == 400 and page > 1:
            break  # au-dela de la derniere page, l'API renvoie une erreur plutot qu'une liste vide
        _raise_for_status_verbose(resp)
        items = resp.json()
        if not items:
            break
        for item in items:
            if item.get("comment_status") == "open":
                patch = session.post(
                    f"{base_url}/wp-json/wp/v2/{post_type}/{item['id']}",
                    json={"comment_status": "closed"},
                    auth=auth,
                )
                _raise_for_status_verbose(patch)
                closed_count += 1
                print(f"  ferme : {post_type}#{item['id']} ({item.get('link', '')})")
        page += 1
    return closed_count


def count_existing_comments(base_url, auth, session):
    resp = session.get(f"{base_url}/wp-json/wp/v2/comments", params={"per_page": 1}, auth=auth)
    _raise_for_status_verbose(resp)
    return resp.headers.get("X-WP-Total", "?")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dest", required=True, help="URL du site, ex: https://guillaumetessaro.be")
    args = parser.parse_args()

    base_url = args.dest.rstrip("/")
    auth = get_auth()
    session = requests.Session()
    session.headers.update({"User-Agent": "tessaro-content-script/1.0"})

    set_default_comment_status(base_url, auth, session)

    total_closed = 0
    for post_type in POST_TYPES:
        print(f"Fermeture des commentaires ouverts sur les {post_type} existants ...")
        total_closed += close_existing_comments(base_url, auth, session, post_type)

    total_comments = count_existing_comments(base_url, auth, session)

    print(f"Termine. {total_closed} contenu(s) mis a jour (commentaires fermes).")
    print(f"Le site compte {total_comments} commentaire(s) deja publie(s) -- non supprimes.")
    print("Pour les consulter/supprimer : wp-admin > Commentaires.")


if __name__ == "__main__":
    main()
