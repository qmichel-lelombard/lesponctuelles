#!/usr/bin/env python3
"""Inspect or edit text inside an Elementor page's _elementor_data via the REST API.

Elementor stores a page's real layout/content as a JSON tree in the postmeta
_elementor_data, separate from the normal WordPress `content` field. Editing
`content` (e.g. via update_post.py) has no visible effect on an
Elementor-built page. This script reads/writes that JSON tree directly --
useful while the Elementor/Gutenberg editors themselves are broken.

Modes:
  --dump                        Print every text-bearing widget found, with
                                 its --path (dot-separated child indices) and
                                 a preview of its text, e.g.:
                                   0.0.0 [heading] title: "Some Heading..."
                                   0.0.1 [text-editor] editor: "Some para..."

  --set-path PATH --text-file F Replace the text at PATH with the content of
                                 file F, and save back to the site. For a
                                 text-editor widget, F should contain HTML
                                 (e.g. one or more <p>...</p>).

Example:
  export WP_DEST_USER=admin
  export WP_DEST_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"
  python3 elementor_text.py --dest https://lesponctuelles.be --page-id 171 --dump
  python3 elementor_text.py --dest https://lesponctuelles.be --page-id 171 \
      --set-path 0.0.0 --text-file ./new-title.txt
"""
import argparse
import json
import os
import sys

import requests
from requests.auth import HTTPBasicAuth

# Known widgetType -> settings key that holds its main text.
TEXT_FIELDS = {
    "heading": "title",
    "text-editor": "editor",
    "button": "text",
    "icon-box": "title_text",
    "call-to-action": "description",
}


def get_auth():
    user = os.environ.get("WP_DEST_USER")
    password = os.environ.get("WP_DEST_APP_PASSWORD")
    if not user or not password:
        raise SystemExit(
            "Set WP_DEST_USER and WP_DEST_APP_PASSWORD environment variables "
            "(create an Application Password in wp-admin under Users > Profile)."
        )
    return HTTPBasicAuth(user, password)


def walk(elements, path_prefix=""):
    for i, el in enumerate(elements):
        path = f"{path_prefix}{i}"
        widget_type = el.get("widgetType")
        field = TEXT_FIELDS.get(widget_type)
        if field and field in el.get("settings", {}):
            text = el["settings"][field]
            preview = (text[:80] + "...") if len(text) > 80 else text
            print(f"{path} [{widget_type}] {field}: {preview!r}")
        if el.get("elements"):
            walk(el["elements"], path + ".")


def get_node(tree, path):
    indices = [int(x) for x in path.split(".")]
    node_list = tree
    node = None
    for idx in indices:
        node = node_list[idx]
        node_list = node.get("elements", [])
    return node


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dest", required=True, help="Destination site base URL, e.g. https://lesponctuelles.be")
    parser.add_argument("--page-id", required=True, type=int, help="Page (or post) ID")
    parser.add_argument("--post-type", default="pages", help="'pages' (default) or 'posts'")
    parser.add_argument("--dump", action="store_true", help="List all text-bearing widgets with their path")
    parser.add_argument("--set-path", help="Dot-separated path (from --dump) of the widget to update")
    parser.add_argument("--text-file", help="File with the new text/HTML content for --set-path")
    args = parser.parse_args()

    base_url = args.dest.rstrip("/")
    auth = get_auth()
    session = requests.Session()
    session.headers.update({"User-Agent": "lesponctuelles-migration-script/1.0"})

    url_base = f"{base_url}/wp-json/wp/v2/{args.post_type}"

    def fetch():
        resp = session.get(f"{url_base}/{args.page_id}", params={"context": "edit"}, auth=auth)
        resp.raise_for_status()
        data = resp.json()
        raw = data.get("meta", {}).get("_elementor_data")
        if not raw:
            raise SystemExit(f"No _elementor_data meta found on {args.post_type[:-1]} {args.page_id}")
        return json.loads(raw)

    tree = fetch()

    if args.dump:
        walk(tree)
        return

    if args.set_path and args.text_file:
        node = get_node(tree, args.set_path)
        widget_type = node.get("widgetType")
        field = TEXT_FIELDS.get(widget_type)
        if not field:
            raise SystemExit(f"Don't know which settings field holds text for widgetType '{widget_type}'")
        with open(args.text_file, encoding="utf-8") as f:
            new_text = f.read()
        old_text = node["settings"].get(field, "")
        node["settings"][field] = new_text
        print(f"Path {args.set_path} [{widget_type}].{field}:")
        print(f"  before: {old_text[:120]!r}")
        print(f"  after:  {new_text[:120]!r}")
        resp = session.post(
            f"{url_base}/{args.page_id}",
            json={"meta": {"_elementor_data": json.dumps(tree)}},
            auth=auth,
        )
        if resp.status_code not in (200, 201):
            print(f"ERROR saving: {resp.status_code} {resp.text[:300]}", file=sys.stderr)
            sys.exit(1)
        print(f"Saved: {resp.json().get('link')}")
        return

    parser.error("Pass --dump, or --set-path together with --text-file")


if __name__ == "__main__":
    main()
