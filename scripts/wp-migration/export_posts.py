#!/usr/bin/env python3
"""Export a selection of posts from a public WordPress site via the REST API.

Reads only public, published content through /wp-json/wp/v2/posts, so no
credentials are needed for the source site. Downloads the featured image and
any inline <img> tags found in the post content, and writes one JSON file per
post plus the media into --output-dir. Pair with import_posts.py to publish
the selection on a second WordPress site.

Examples:
  # Everything in the "recettes" category, published
  python3 export_posts.py --source https://lesponctuelles.com \
      --category recettes --output-dir ./export

  # A specific list of posts by slug
  python3 export_posts.py --source https://lesponctuelles.com \
      --slugs mon-article,un-autre-article --output-dir ./export

  # Everything published after a given date
  python3 export_posts.py --source https://lesponctuelles.com \
      --after 2024-01-01 --output-dir ./export
"""
import argparse
import json
import os
import re
import sys
from urllib.parse import urlparse

import requests

IMG_SRC_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)


def resolve_term_id(base_url, taxonomy, slug, session):
    resp = session.get(f"{base_url}/wp-json/wp/v2/{taxonomy}", params={"slug": slug})
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise SystemExit(f"No {taxonomy[:-1]} found with slug '{slug}' on source site")
    return data[0]["id"]


def fetch_posts(base_url, session, category_id=None, tag_id=None, slugs=None, after=None, before=None):
    posts = []
    if slugs:
        for slug in slugs:
            resp = session.get(f"{base_url}/wp-json/wp/v2/posts", params={"slug": slug, "_embed": 1})
            resp.raise_for_status()
            data = resp.json()
            if not data:
                print(f"  warning: no post found for slug '{slug}'", file=sys.stderr)
                continue
            posts.append(data[0])
        return posts

    page = 1
    while True:
        params = {"per_page": 100, "page": page, "_embed": 1, "status": "publish"}
        if category_id:
            params["categories"] = category_id
        if tag_id:
            params["tags"] = tag_id
        if after:
            params["after"] = f"{after}T00:00:00"
        if before:
            params["before"] = f"{before}T23:59:59"
        resp = session.get(f"{base_url}/wp-json/wp/v2/posts", params=params)
        if resp.status_code == 400:
            break
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        posts.extend(batch)
        total_pages = int(resp.headers.get("X-WP-TotalPages", "1"))
        if page >= total_pages:
            break
        page += 1
    return posts


def embedded_terms(post, taxonomy):
    for group in post.get("_embedded", {}).get("wp:term", []):
        for term in group:
            if term.get("taxonomy") == taxonomy:
                yield term["name"]


def download_media(url, dest_dir, session):
    filename = os.path.basename(urlparse(url).path)
    if not filename:
        return None
    local_path = os.path.join(dest_dir, filename)
    if not os.path.exists(local_path):
        resp = session.get(url, stream=True)
        if resp.status_code != 200:
            print(f"  warning: could not download {url} ({resp.status_code})", file=sys.stderr)
            return None
        with open(local_path, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
    return filename


def export_post(post, base_url, output_dir, session):
    media_dir = os.path.join(output_dir, "media")
    os.makedirs(media_dir, exist_ok=True)

    content = post["content"]["rendered"]

    featured_image = None
    embedded_media = post.get("_embedded", {}).get("wp:featuredmedia")
    if embedded_media and embedded_media[0].get("source_url"):
        featured_image = download_media(embedded_media[0]["source_url"], media_dir, session)

    image_map = {}
    for src in set(IMG_SRC_RE.findall(content)):
        if urlparse(src).netloc != urlparse(base_url).netloc:
            continue
        local_name = download_media(src, media_dir, session)
        if local_name:
            image_map[src] = local_name
            content = content.replace(src, f"media/{local_name}")

    record = {
        "source_id": post["id"],
        "slug": post["slug"],
        "title": post["title"]["rendered"],
        "excerpt": post["excerpt"]["rendered"],
        "content": content,
        "date": post["date"],
        "categories": list(embedded_terms(post, "category")),
        "tags": list(embedded_terms(post, "post_tag")),
        "featured_image": featured_image,
        "source_link": post.get("link"),
    }

    out_path = os.path.join(output_dir, f"{post['slug']}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return out_path


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", required=True, help="Source site base URL, e.g. https://lesponctuelles.com")
    parser.add_argument("--category", help="Category slug to filter by")
    parser.add_argument("--tag", help="Tag slug to filter by")
    parser.add_argument("--slugs", help="Comma-separated list of exact post slugs to export")
    parser.add_argument("--after", help="Only posts published after this date (YYYY-MM-DD)")
    parser.add_argument("--before", help="Only posts published before this date (YYYY-MM-DD)")
    parser.add_argument("--output-dir", required=True, help="Directory to write exported JSON + media into")
    args = parser.parse_args()

    base_url = args.source.rstrip("/")
    os.makedirs(args.output_dir, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": "lesponctuelles-migration-script/1.0"})

    category_id = resolve_term_id(base_url, "categories", args.category, session) if args.category else None
    tag_id = resolve_term_id(base_url, "tags", args.tag, session) if args.tag else None
    slugs = [s.strip() for s in args.slugs.split(",")] if args.slugs else None

    print(f"Fetching posts from {base_url} ...")
    posts = fetch_posts(base_url, session, category_id, tag_id, slugs, args.after, args.before)
    print(f"Found {len(posts)} post(s) matching the selection.")

    for post in posts:
        path = export_post(post, base_url, args.output_dir, session)
        print(f"  exported: {path}")

    print(f"Done. {len(posts)} post(s) written to {args.output_dir}")


if __name__ == "__main__":
    main()
