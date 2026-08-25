#!/usr/bin/env python3
"""Import products exported by export_products.py into a destination site.

Authenticates with a WordPress Application Password (Users > Profile >
Application Passwords in wp-admin, for a user with manage_woocommerce
capability) sent as HTTP Basic Auth over HTTPS. Set WP_DEST_USER /
WP_DEST_APP_PASSWORD in the environment; never pass the password on the
command line. These are the same credentials import_posts.py uses, so you
can reuse an already-created Application Password.

Categories are matched by name and created on the destination if missing.
Images are re-uploaded to the destination media library. Variable products
are recreated with their attributes and variations. Products whose SKU (or
slug, if no SKU) already exists on the destination are skipped by default.

Example:
  export WP_DEST_USER=admin
  export WP_DEST_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"
  python3 import_products.py --dest https://lesponctuelles.be \
      --input-dir ./export-products --status draft
"""
import argparse
import json
import mimetypes
import os
import sys
import unicodedata

import requests
from requests.auth import HTTPBasicAuth


def _ascii_filename(filename):
    normalized = unicodedata.normalize("NFKD", filename)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_name or "image"


def get_auth():
    user = os.environ.get("WP_DEST_USER")
    password = os.environ.get("WP_DEST_APP_PASSWORD")
    if not user or not password:
        raise SystemExit(
            "Set WP_DEST_USER and WP_DEST_APP_PASSWORD environment variables "
            "(create an Application Password in wp-admin under Users > Profile, "
            "for a user with the manage_woocommerce capability)."
        )
    return HTTPBasicAuth(user, password)


def find_existing_product(base_url, auth, session, sku, slug):
    if sku:
        resp = session.get(f"{base_url}/wp-json/wc/v3/products", params={"sku": sku}, auth=auth)
        resp.raise_for_status()
        data = resp.json()
        if data:
            return data[0]["id"]
    resp = session.get(f"{base_url}/wp-json/wc/v3/products", params={"slug": slug}, auth=auth)
    resp.raise_for_status()
    data = resp.json()
    return data[0]["id"] if data else None


def get_or_create_category(base_url, auth, session, name):
    resp = session.get(f"{base_url}/wp-json/wc/v3/products/categories", params={"search": name, "per_page": 100}, auth=auth)
    resp.raise_for_status()
    for cat in resp.json():
        if cat["name"].strip().lower() == name.strip().lower():
            return cat["id"]
    resp = session.post(f"{base_url}/wp-json/wc/v3/products/categories", json={"name": name}, auth=auth)
    resp.raise_for_status()
    return resp.json()["id"]


def get_or_create_tag(base_url, auth, session, name):
    resp = session.get(f"{base_url}/wp-json/wc/v3/products/tags", params={"search": name, "per_page": 100}, auth=auth)
    resp.raise_for_status()
    for tag in resp.json():
        if tag["name"].strip().lower() == name.strip().lower():
            return tag["id"]
    resp = session.post(f"{base_url}/wp-json/wc/v3/products/tags", json={"name": name}, auth=auth)
    resp.raise_for_status()
    return resp.json()["id"]


def upload_media(base_url, auth, session, file_path):
    filename = os.path.basename(file_path)
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    with open(file_path, "rb") as f:
        resp = session.post(
            f"{base_url}/wp-json/wp/v2/media",
            headers={
                "Content-Disposition": f'attachment; filename="{_ascii_filename(filename)}"',
                "Content-Type": content_type,
            },
            data=f.read(),
            auth=auth,
        )
    if resp.status_code not in (200, 201):
        print(f"  warning: media upload failed for {filename}: {resp.status_code} {resp.text[:200]}", file=sys.stderr)
        return None
    return resp.json()


def upload_images(base_url, auth, session, media_dir, filenames):
    uploaded = []
    for filename in filenames:
        local_path = os.path.join(media_dir, filename)
        if not os.path.exists(local_path):
            continue
        media = upload_media(base_url, auth, session, local_path)
        if media:
            uploaded.append({"id": media["id"]})
    return uploaded


def import_variation(base_url, auth, session, product_id, variation, media_dir):
    payload = {
        "sku": variation.get("sku") or None,
        "regular_price": variation.get("regular_price") or "",
        "sale_price": variation.get("sale_price") or "",
        "description": variation.get("description", ""),
        "stock_status": variation.get("stock_status", "instock"),
        "manage_stock": variation.get("manage_stock", False),
        "attributes": [
            {"name": a["name"], "option": a["option"]}
            for a in variation.get("attributes", [])
        ],
    }
    if variation.get("manage_stock") and variation.get("stock_quantity") is not None:
        payload["stock_quantity"] = variation["stock_quantity"]
    if variation.get("weight"):
        payload["weight"] = variation["weight"]
    if variation.get("image"):
        images = upload_images(base_url, auth, session, media_dir, [variation["image"]])
        if images:
            payload["image"] = images[0]

    resp = session.post(f"{base_url}/wp-json/wc/v3/products/{product_id}/variations", json=payload, auth=auth)
    if resp.status_code not in (200, 201):
        print(f"    warning: variation creation failed: {resp.status_code} {resp.text[:200]}", file=sys.stderr)


def import_product(record, base_url, auth, session, media_dir, status, skip_existing, log):
    slug = record["slug"]
    sku = record.get("sku")

    if skip_existing:
        existing_id = find_existing_product(base_url, auth, session, sku, slug)
        if existing_id:
            print(f"  skip (already exists, id={existing_id}): {slug}")
            return

    category_ids = [{"id": get_or_create_category(base_url, auth, session, name)} for name in record.get("categories", [])]
    tag_ids = [{"id": get_or_create_tag(base_url, auth, session, name)} for name in record.get("tags", [])]
    images = upload_images(base_url, auth, session, media_dir, record.get("images", []))

    payload = {
        "name": record["name"],
        "slug": slug,
        "type": record.get("type", "simple"),
        "status": status,
        "description": record.get("description", ""),
        "short_description": record.get("short_description", ""),
        "categories": category_ids,
        "tags": tag_ids,
        "images": images,
        "stock_status": record.get("stock_status", "instock"),
        "manage_stock": record.get("manage_stock", False),
    }
    if sku:
        payload["sku"] = sku
    if record.get("weight"):
        payload["weight"] = record["weight"]
    if record.get("dimensions"):
        payload["dimensions"] = record["dimensions"]
    if record.get("manage_stock") and record.get("stock_quantity") is not None:
        payload["stock_quantity"] = record["stock_quantity"]

    if record.get("type") == "variable":
        payload["attributes"] = [
            {
                "name": a["name"],
                "options": a["options"],
                "visible": a.get("visible", True),
                "variation": True,
            }
            for a in record.get("attributes", [])
        ]
    else:
        payload["regular_price"] = record.get("regular_price") or ""
        payload["sale_price"] = record.get("sale_price") or ""
        payload["attributes"] = [
            {
                "name": a["name"],
                "options": a["options"],
                "visible": a.get("visible", True),
                "variation": False,
            }
            for a in record.get("attributes", [])
        ]

    resp = session.post(f"{base_url}/wp-json/wc/v3/products", json=payload, auth=auth)
    if resp.status_code not in (200, 201):
        print(f"  ERROR creating '{slug}': {resp.status_code} {resp.text[:300]}", file=sys.stderr)
        return

    new_product = resp.json()
    print(f"  created: {slug} -> id={new_product['id']} ({new_product.get('permalink')})")

    for variation in record.get("variations", []):
        import_variation(base_url, auth, session, new_product["id"], variation, media_dir)

    log.append({
        "slug": slug,
        "sku": sku,
        "source_link": record.get("source_link"),
        "dest_id": new_product["id"],
        "dest_link": new_product.get("permalink"),
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dest", required=True, help="Destination site base URL, e.g. https://lesponctuelles.be")
    parser.add_argument("--input-dir", required=True, help="Directory produced by export_products.py")
    parser.add_argument("--status", default="draft", choices=["draft", "publish", "pending", "private"], help="Status to create products with (default: draft, review before publishing)")
    parser.add_argument("--overwrite", action="store_true", help="Import even if a product with the same SKU/slug already exists")
    args = parser.parse_args()

    base_url = args.dest.rstrip("/")
    media_dir = os.path.join(args.input_dir, "media")
    auth = get_auth()
    session = requests.Session()
    session.headers.update({"User-Agent": "lesponctuelles-migration-script/1.0"})

    files = sorted(f for f in os.listdir(args.input_dir) if f.endswith(".json"))
    if not files:
        raise SystemExit(f"No exported *.json files found in {args.input_dir}")

    print(f"Importing {len(files)} product(s) into {base_url} as '{args.status}' ...")
    log = []
    for filename in files:
        with open(os.path.join(args.input_dir, filename), encoding="utf-8") as f:
            record = json.load(f)
        import_product(record, base_url, auth, session, media_dir, args.status, not args.overwrite, log)

    log_path = os.path.join(args.input_dir, "import_log.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"Done. Mapping of source -> destination links written to {log_path}")
    print("Review the imported products in wp-admin before switching status to 'publish'.")


if __name__ == "__main__":
    main()
