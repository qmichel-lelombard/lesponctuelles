#!/usr/bin/env python3
"""Import posts exported by export_posts.py into a destination WordPress site.

Authenticates with a WordPress Application Password (Users > Profile >
Application Passwords in wp-admin) sent as HTTP Basic Auth over HTTPS.
Never pass the password on the command line: set it via the
WP_DEST_APP_PASSWORD environment variable.

Categories/tags are matched by name and created on the destination if
missing. Featured + inline images are re-uploaded to the destination media
library and the content is rewritten to point at the new URLs. Posts whose
slug already exists on the destination are skipped by default.

Example:
  export WP_DEST_USER=admin
  export WP_DEST_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"
  python3 import_posts.py --dest https://lesponctuelles.be \
      --input-dir ./export --status draft
"""
import argparse
import json
import mimetypes
import os
import sys

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


def post_exists(base_url, auth, session, slug):
    resp = session.get(f"{base_url}/wp-json/wp/v2/posts", params={"slug": slug, "status": "any"}, auth=auth)
    resp.raise_for_status()
    data = resp.json()
    return data[0]["id"] if data else None


def get_or_create_term(base_url, auth, session, taxonomy, name):
    resp = session.get(f"{base_url}/wp-json/wp/v2/{taxonomy}", params={"search": name, "per_page": 100}, auth=auth)
    resp.raise_for_status()
    for term in resp.json():
        if term["name"].strip().lower() == name.strip().lower():
            return term["id"]
    resp = session.post(f"{base_url}/wp-json/wp/v2/{taxonomy}", json={"name": name}, auth=auth)
    resp.raise_for_status()
    return resp.json()["id"]


def upload_media(base_url, auth, session, file_path):
    filename = os.path.basename(file_path)
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    with open(file_path, "rb") as f:
        resp = session.post(
            f"{base_url}/wp-json/wp/v2/media",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": content_type,
            },
            data=f.read(),
            auth=auth,
        )
    if resp.status_code not in (200, 201):
        print(f"  warning: media upload failed for {filename}: {resp.status_code} {resp.text[:200]}", file=sys.stderr)
        return None
    return resp.json()


def import_post(record, base_url, auth, session, media_dir, status, skip_existing, log):
    slug = record["slug"]
    if skip_existing:
        existing_id = post_exists(base_url, auth, session, slug)
        if existing_id:
            print(f"  skip (already exists, id={existing_id}): {slug}")
            return

    content = record["content"]

    featured_media_id = None
    if record.get("featured_image"):
        media = upload_media(base_url, auth, session, os.path.join(media_dir, record["featured_image"]))
        if media:
            featured_media_id = media["id"]

    for local_name in {os.path.basename(v) for v in _referenced_media(content)}:
        local_path = os.path.join(media_dir, local_name)
        if not os.path.exists(local_path):
            continue
        media = upload_media(base_url, auth, session, local_path)
        if media:
            content = content.replace(f"media/{local_name}", media["source_url"])

    category_ids = [get_or_create_term(base_url, auth, session, "categories", name) for name in record.get("categories", [])]
    tag_ids = [get_or_create_term(base_url, auth, session, "tags", name) for name in record.get("tags", [])]

    payload = {
        "title": record["title"],
        "slug": slug,
        "content": content,
        "excerpt": record.get("excerpt", ""),
        "status": status,
        "categories": category_ids,
        "tags": tag_ids,
        "date": record.get("date"),
    }
    if featured_media_id:
        payload["featured_media"] = featured_media_id

    resp = session.post(f"{base_url}/wp-json/wp/v2/posts", json=payload, auth=auth)
    if resp.status_code not in (200, 201):
        print(f"  ERROR creating '{slug}': {resp.status_code} {resp.text[:300]}", file=sys.stderr)
        return

    new_post = resp.json()
    print(f"  created: {slug} -> id={new_post['id']} ({new_post.get('link')})")
    log.append({
        "slug": slug,
        "source_link": record.get("source_link"),
        "dest_id": new_post["id"],
        "dest_link": new_post.get("link"),
    })


def _referenced_media(content):
    import re
    return re.findall(r'media/([^"\')\s]+)', content)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dest", required=True, help="Destination site base URL, e.g. https://lesponctuelles.be")
    parser.add_argument("--input-dir", required=True, help="Directory produced by export_posts.py")
    parser.add_argument("--status", default="draft", choices=["draft", "publish", "pending"], help="Status to create posts with (default: draft, review before publishing)")
    parser.add_argument("--overwrite", action="store_true", help="Import even if a post with the same slug already exists")
    args = parser.parse_args()

    base_url = args.dest.rstrip("/")
    media_dir = os.path.join(args.input_dir, "media")
    auth = get_auth()
    session = requests.Session()
    session.headers.update({"User-Agent": "lesponctuelles-migration-script/1.0"})

    files = sorted(f for f in os.listdir(args.input_dir) if f.endswith(".json"))
    if not files:
        raise SystemExit(f"No exported *.json files found in {args.input_dir}")

    print(f"Importing {len(files)} post(s) into {base_url} as '{args.status}' ...")
    log = []
    for filename in files:
        with open(os.path.join(args.input_dir, filename), encoding="utf-8") as f:
            record = json.load(f)
        import_post(record, base_url, auth, session, media_dir, args.status, not args.overwrite, log)

    log_path = os.path.join(args.input_dir, "import_log.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"Done. Mapping of source -> destination links written to {log_path}")
    print("Review the imported posts in wp-admin before switching status to 'publish'.")


if __name__ == "__main__":
    main()
