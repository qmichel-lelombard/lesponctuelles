#!/usr/bin/env python3
"""Bulk-update the status of items previously created by import_posts.py or
import_products.py, using the import_log.json each of them writes.

Example:
  export WP_DEST_USER=admin
  export WP_DEST_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"

  python3 publish_from_log.py --dest https://lesponctuelles.be \
      --log ./export-culture/import_log.json --type post

  python3 publish_from_log.py --dest https://lesponctuelles.be \
      --log ./export-products/import_log.json --type product
"""
import argparse
import json
import os
import sys

import requests
from requests.auth import HTTPBasicAuth

ENDPOINTS = {
    "post": "wp/v2/posts",
    "product": "wc/v3/products",
}


def get_auth():
    user = os.environ.get("WP_DEST_USER")
    password = os.environ.get("WP_DEST_APP_PASSWORD")
    if not user or not password:
        raise SystemExit("Set WP_DEST_USER and WP_DEST_APP_PASSWORD environment variables.")
    return HTTPBasicAuth(user, password)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dest", required=True, help="Destination site base URL, e.g. https://lesponctuelles.be")
    parser.add_argument("--log", required=True, help="Path to an import_log.json produced by import_posts.py or import_products.py")
    parser.add_argument("--type", required=True, choices=sorted(ENDPOINTS), help="Kind of items listed in the log")
    parser.add_argument("--status", default="publish", choices=["publish", "draft", "pending", "private"])
    args = parser.parse_args()

    base_url = args.dest.rstrip("/")
    auth = get_auth()
    session = requests.Session()
    session.headers.update({"User-Agent": "lesponctuelles-migration-script/1.0"})

    with open(args.log, encoding="utf-8") as f:
        entries = json.load(f)

    endpoint = ENDPOINTS[args.type]
    print(f"Updating {len(entries)} {args.type}(s) to status='{args.status}' ...")
    failures = 0
    for entry in entries:
        item_id = entry["dest_id"]
        resp = session.post(f"{base_url}/wp-json/{endpoint}/{item_id}", json={"status": args.status}, auth=auth)
        if resp.status_code not in (200, 201):
            failures += 1
            print(f"  ERROR updating id={item_id} ({entry.get('slug')}): {resp.status_code} {resp.text[:200]}", file=sys.stderr)
            continue
        print(f"  updated: {entry.get('slug')} (id={item_id}) -> {args.status}")

    print(f"Done. {len(entries) - failures}/{len(entries)} updated to '{args.status}'.")


if __name__ == "__main__":
    main()
