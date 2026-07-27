#!/usr/bin/env python3
"""Export WooCommerce products from a source site via the WooCommerce REST API.

Unlike blog posts, the WooCommerce products endpoint always requires
authentication (there is no public/anonymous read). Authenticate with a
WordPress Application Password for a user with "manage_woocommerce"
capability (Users > Profile > Application Passwords in wp-admin), set via
the WP_SOURCE_USER / WP_SOURCE_APP_PASSWORD environment variables. Never
pass the password on the command line.

Downloads every product image and, for variable products, all variations,
and writes one JSON file per product plus the media into --output-dir.
Pair with import_products.py to publish the selection on a second site.

Examples:
  export WP_SOURCE_USER=admin
  export WP_SOURCE_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"

  # Every product
  python3 export_products.py --source https://lesponctuelles.com \
      --output-dir ./export-products

  # Only a product category
  python3 export_products.py --source https://lesponctuelles.com \
      --category bijoux --output-dir ./export-products

  # A specific list of products by SKU
  python3 export_products.py --source https://lesponctuelles.com \
      --skus ABC123,DEF456 --output-dir ./export-products
"""
import argparse
import json
import os
import sys
from urllib.parse import urlparse

import requests
from requests.auth import HTTPBasicAuth


def get_auth():
    user = os.environ.get("WP_SOURCE_USER")
    password = os.environ.get("WP_SOURCE_APP_PASSWORD")
    if not user or not password:
        raise SystemExit(
            "Set WP_SOURCE_USER and WP_SOURCE_APP_PASSWORD environment variables "
            "(create an Application Password in wp-admin under Users > Profile, "
            "for a user with the manage_woocommerce capability)."
        )
    return HTTPBasicAuth(user, password)


def resolve_category_id(base_url, auth, session, slug):
    resp = session.get(f"{base_url}/wp-json/wc/v3/products/categories", params={"slug": slug}, auth=auth)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise SystemExit(f"No product category found with slug '{slug}' on source site")
    return data[0]["id"]


def fetch_products(base_url, auth, session, category_id=None, skus=None):
    products = []
    if skus:
        for sku in skus:
            resp = session.get(f"{base_url}/wp-json/wc/v3/products", params={"sku": sku}, auth=auth)
            resp.raise_for_status()
            data = resp.json()
            if not data:
                print(f"  warning: no product found for SKU '{sku}'", file=sys.stderr)
                continue
            products.extend(data)
        return products

    page = 1
    while True:
        params = {"per_page": 100, "page": page, "status": "publish"}
        if category_id:
            params["category"] = category_id
        resp = session.get(f"{base_url}/wp-json/wc/v3/products", params=params, auth=auth)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        products.extend(batch)
        total_pages = int(resp.headers.get("X-WP-TotalPages", "1"))
        if page >= total_pages:
            break
        page += 1
    return products


def fetch_variations(base_url, auth, session, product_id):
    variations = []
    page = 1
    while True:
        resp = session.get(
            f"{base_url}/wp-json/wc/v3/products/{product_id}/variations",
            params={"per_page": 100, "page": page},
            auth=auth,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        variations.extend(batch)
        total_pages = int(resp.headers.get("X-WP-TotalPages", "1"))
        if page >= total_pages:
            break
        page += 1
    return variations


def download_image(url, dest_dir, session):
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


def export_images(images, media_dir, session):
    local_names = []
    for image in images:
        src = image.get("src")
        if not src:
            continue
        local_name = download_image(src, media_dir, session)
        if local_name:
            local_names.append(local_name)
    return local_names


def export_variation(variation, media_dir, session):
    image_name = None
    if variation.get("image") and variation["image"].get("src"):
        image_name = download_image(variation["image"]["src"], media_dir, session)
    return {
        "sku": variation.get("sku"),
        "regular_price": variation.get("regular_price"),
        "sale_price": variation.get("sale_price"),
        "description": variation.get("description", ""),
        "stock_status": variation.get("stock_status"),
        "manage_stock": variation.get("manage_stock", False),
        "stock_quantity": variation.get("stock_quantity"),
        "weight": variation.get("weight"),
        "attributes": [
            {"name": a.get("name"), "option": a.get("option")}
            for a in variation.get("attributes", [])
        ],
        "image": image_name,
    }


def export_product(product, base_url, auth, output_dir, session):
    media_dir = os.path.join(output_dir, "media")
    os.makedirs(media_dir, exist_ok=True)

    variations = []
    if product.get("type") == "variable":
        variations = [
            export_variation(v, media_dir, session)
            for v in fetch_variations(base_url, auth, session, product["id"])
        ]

    record = {
        "source_id": product["id"],
        "sku": product.get("sku"),
        "slug": product["slug"],
        "name": product["name"],
        "type": product.get("type", "simple"),
        "description": product.get("description", ""),
        "short_description": product.get("short_description", ""),
        "regular_price": product.get("regular_price"),
        "sale_price": product.get("sale_price"),
        "stock_status": product.get("stock_status"),
        "manage_stock": product.get("manage_stock", False),
        "stock_quantity": product.get("stock_quantity"),
        "weight": product.get("weight"),
        "dimensions": product.get("dimensions"),
        "categories": [c["name"] for c in product.get("categories", [])],
        "tags": [t["name"] for t in product.get("tags", [])],
        "attributes": [
            {
                "name": a.get("name"),
                "options": a.get("options", []),
                "visible": a.get("visible", True),
                "variation": a.get("variation", False),
            }
            for a in product.get("attributes", [])
        ],
        "images": export_images(product.get("images", []), media_dir, session),
        "variations": variations,
        "source_link": product.get("permalink"),
    }

    out_path = os.path.join(output_dir, f"{product['slug']}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return out_path


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", required=True, help="Source site base URL, e.g. https://lesponctuelles.com")
    parser.add_argument("--category", help="Product category slug to filter by")
    parser.add_argument("--skus", help="Comma-separated list of exact product SKUs to export")
    parser.add_argument("--output-dir", required=True, help="Directory to write exported JSON + media into")
    args = parser.parse_args()

    base_url = args.source.rstrip("/")
    os.makedirs(args.output_dir, exist_ok=True)

    auth = get_auth()
    session = requests.Session()
    session.headers.update({"User-Agent": "lesponctuelles-migration-script/1.0"})

    category_id = resolve_category_id(base_url, auth, session, args.category) if args.category else None
    skus = [s.strip() for s in args.skus.split(",")] if args.skus else None

    print(f"Fetching products from {base_url} ...")
    products = fetch_products(base_url, auth, session, category_id, skus)
    print(f"Found {len(products)} product(s) matching the selection.")

    for product in products:
        path = export_product(product, base_url, auth, args.output_dir, session)
        print(f"  exported: {path}")

    print(f"Done. {len(products)} product(s) written to {args.output_dir}")


if __name__ == "__main__":
    main()
