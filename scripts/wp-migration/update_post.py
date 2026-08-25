#!/usr/bin/env python3
"""Update an existing post/page's content and/or featured image via the REST API.

Lighter-weight than the block/Elementor editors (a couple of plain REST
calls), useful as a workaround when the visual editors are broken.

Authenticates with a WordPress Application Password (same as import_posts.py).

Example:
  export WP_DEST_USER=admin
  export WP_DEST_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"
  python3 update_post.py --dest https://lesponctuelles.be \
      --slug betty --content-file ./betty-content.html \
      --featured-image-url https://lesponctuelles.be/wp-content/uploads/2026/08/betty-lesponctuelles.jpg
"""
import argparse
import os
import sys
from urllib.parse import urlparse

import requests
from requests.auth import HTTPBasicAuth


def get_auth():
    user = os.environ.get("WP_DEST_USER")
    password = os.environ.get("WP_DEST_APP_PASSWORD")
    if not user or not password:
        raise SystemExit(
            "Set WP_DEST_USER and WP_DEST_APP_PASSWORD environment variables "
            "(create an Application Password in wp-admin under Users > Profile)."
        )
    return HTTPBasicAuth(user, password)


def find_post_id(base_url, auth, session, post_type, slug):
    resp = session.get(f"{base_url}/wp-json/wp/v2/{post_type}", params={"slug": slug, "status": "any"}, auth=auth)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise SystemExit(f"No {post_type[:-1]} found with slug '{slug}' on {base_url}")
    return data[0]["id"]


def find_media_id_by_url(base_url, auth, session, image_url):
    filename = os.path.basename(urlparse(image_url).path)
    search_term = os.path.splitext(filename)[0]
    resp = session.get(f"{base_url}/wp-json/wp/v2/media", params={"search": search_term, "per_page": 50}, auth=auth)
    resp.raise_for_status()
    for item in resp.json():
        if item.get("source_url") == image_url:
            return item["id"]
    raise SystemExit(f"No media item found matching URL '{image_url}' (searched for '{search_term}')")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dest", required=True, help="Destination site base URL, e.g. https://lesponctuelles.be")
    parser.add_argument("--post-type", default="posts", help="'posts' (default) or 'pages'")
    parser.add_argument("--slug", required=True, help="Slug of the post/page to update")
    parser.add_argument("--content-file", help="Path to an HTML file with the new content")
    parser.add_argument("--title", help="New title (optional, leaves unchanged if omitted)")
    parser.add_argument("--featured-image-url", help="URL of an already-uploaded media item to set as featured image")
    args = parser.parse_args()

    if not args.content_file and not args.title and not args.featured_image_url:
        raise SystemExit("Nothing to do: pass at least one of --content-file, --title, --featured-image-url")

    base_url = args.dest.rstrip("/")
    auth = get_auth()
    session = requests.Session()
    session.headers.update({"User-Agent": "lesponctuelles-migration-script/1.0"})

    post_id = find_post_id(base_url, auth, session, args.post_type, args.slug)
    print(f"Found {args.post_type[:-1]} '{args.slug}' -> id={post_id}")

    payload = {}
    if args.content_file:
        with open(args.content_file, encoding="utf-8") as f:
            payload["content"] = f.read()
    if args.title:
        payload["title"] = args.title
    if args.featured_image_url:
        payload["featured_media"] = find_media_id_by_url(base_url, auth, session, args.featured_image_url)

    resp = session.post(f"{base_url}/wp-json/wp/v2/{args.post_type}/{post_id}", json=payload, auth=auth)
    if resp.status_code not in (200, 201):
        print(f"ERROR updating post {post_id}: {resp.status_code} {resp.text[:300]}", file=sys.stderr)
        sys.exit(1)

    updated = resp.json()
    print(f"Updated: {updated.get('link')}")


if __name__ == "__main__":
    main()
