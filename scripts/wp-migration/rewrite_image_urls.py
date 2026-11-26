#!/usr/bin/env python3
"""Rewrite post content so it no longer depends on the old site.

Uses the state file written by repatriate_images.py to point every image
reference (src, srcset, data-* and link attributes, direct or through the
Jetpack image CDN) at the copy now held in the destination media library, and
rewrites remaining links to old-site pages using a JSON map of
old path -> new URL (for instance the old site's redirect rules).

Dry-run by default: prints what would change. Pass --apply to save.

Example:
  export WP_DEST_USER=admin
  export WP_DEST_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"
  python3 rewrite_image_urls.py --dest https://lesponctuelles.be \
      --old-domain lesponctuelles.com --state-file ./repatriate_state.json \
      --link-map ./link_map.json --posts-file ./posts.json --apply
"""
import argparse
import html
import json
import os
import re
import sys
from urllib.parse import parse_qs, unquote, urlsplit

import requests
from requests.auth import HTTPBasicAuth

SIZE_SUFFIX = re.compile(r"-(\d+)x(\d+)(?=\.\w+$)")
IMG_TAG = re.compile(r"<img\b[^>]*>", re.I)
ATTR = re.compile(r'([\w:-]+)=(")([^"]*)(")')
FULL_SIZE_ATTRS = {"href", "data-orig-file", "data-full-url"}


def get_auth():
    user = os.environ.get("WP_DEST_USER")
    password = os.environ.get("WP_DEST_APP_PASSWORD")
    if not user or not password:
        raise SystemExit("Set WP_DEST_USER and WP_DEST_APP_PASSWORD environment variables.")
    return HTTPBasicAuth(user, password)


class Rewriter:
    def __init__(self, old_domain, dest, state, link_map, fallback):
        self.old = re.escape(old_domain)
        self.dest = dest
        self.state = state
        self.link_map = link_map
        self.fallback = fallback
        self.any_old = re.compile(rf"https?://(?:i\d\.wp\.com/)?(?:www\.)?{self.old}[^\s\"'<>]*", re.I)
        self.upload = re.compile(
            rf"https?://(?:i\d\.wp\.com/)?(?:www\.)?{self.old}(/wp-content/uploads/[^\s\"'<>?]+)(\?[^\s\"'<>]*)?", re.I
        )
        self.unresolved = []
        self.id_map = {}

    def entry_for(self, path):
        path = unquote(path)
        entry = self.state.get(path) or self.state.get(SIZE_SUFFIX.sub("", path))
        return entry if entry and "id" in entry else None

    @staticmethod
    def same_ratio_sizes(entry):
        sizes = [(entry["w"], entry["url"])]
        if entry.get("w") and entry.get("h"):
            ratio = entry["w"] / entry["h"]
            for size in entry["sizes"].values():
                if size.get("w") and size.get("h") and size["w"] < entry["w"]:
                    if abs(size["w"] / size["h"] - ratio) / ratio < 0.03:
                        sizes.append((size["w"], size["url"]))
        return sorted(set(sizes))

    def requested_width(self, path, query):
        params = parse_qs(html.unescape(query or "").lstrip("?"))
        zoom = float(params.get("zoom", ["1"])[0] or 1)
        for key in ("resize", "fit"):
            if key in params:
                return int(float(params[key][0].split(",")[0]) * zoom)
        if "w" in params:
            return int(float(params["w"][0]) * zoom)
        match = SIZE_SUFFIX.search(path)
        entry = self.entry_for(path)
        if match and entry and entry.get("original") != unquote(path):
            return int(match.group(1))
        return None

    def pick(self, entry, width):
        sizes = self.same_ratio_sizes(entry)
        if width:
            for w, url in sizes:
                if w and w >= width:
                    return url
        return entry["url"]

    def replace_upload(self, match, full=False):
        entry = self.entry_for(match.group(1))
        if not entry:
            self.unresolved.append(match.group(0))
            return match.group(0)
        if full:
            return entry["url"]
        return self.pick(entry, self.requested_width(match.group(1), match.group(2)))

    def map_link(self, url):
        parts = urlsplit(html.unescape(url))
        if "attachment_id=" in parts.query:
            return None
        path = parts.path.rstrip("/") or "/"
        dated = re.match(r"^/\d{4}/\d{2}/\d{2}(/.+)$", path)
        for candidate in filter(None, [path, dated.group(1) if dated else None]):
            if candidate in self.link_map:
                return self.link_map[candidate]
        return None

    def rewrite_img(self, tag):
        found = self.upload.search(tag)
        entry = self.entry_for(found.group(1)) if found else None

        def attr(match):
            name, value = match.group(1).lower(), match.group(3)
            if not self.any_old.search(value):
                return match.group(0)
            if name == "srcset" and entry:
                value = ", ".join(f"{url} {w}w" for w, url in self.same_ratio_sizes(entry))
            elif name in ("data-permalink", "data-link") and entry and not self.upload.search(value):
                value = entry["url"]
            else:
                value = self.upload.sub(lambda m: self.replace_upload(m, full=name in FULL_SIZE_ATTRS), value)
            return f'{match.group(1)}="{value}"'

        tag = ATTR.sub(attr, tag)
        if entry:
            old_id = re.search(r"\bwp-image-(\d+)\b", tag)
            if old_id:
                self.id_map[old_id.group(1)] = entry["id"]
            tag = re.sub(r"\bwp-image-\d+\b", f"wp-image-{entry['id']}", tag)
            tag = re.sub(r'\b(data-attachment-id|data-id)="\d+"', rf'\1="{entry["id"]}"', tag)
        return tag

    def rewrite(self, content):
        # Links wrapping an image: point at the full-size copy of that image.
        def anchor(match):
            href = match.group(2)
            if not self.any_old.search(href):
                return match.group(0)
            own = self.upload.search(href)
            inner = self.upload.search(match.group(3))
            entry = (self.entry_for(own.group(1)) if own else None) or (self.entry_for(inner.group(1)) if inner else None)
            if entry and (own or not self.map_link(href)):
                return match.group(1) + entry["url"] + match.group(3)
            return match.group(0)

        content = re.sub(r'(<a\b[^>]*?\bhref=")([^"]*)("[^>]*>\s*<img\b[^>]*>)', anchor, content, flags=re.I)
        content = IMG_TAG.sub(lambda m: self.rewrite_img(m.group(0)), content)
        content = self.upload.sub(lambda m: self.replace_upload(m, full=True), content)
        for old_id, new_id in self.id_map.items():
            content = re.sub(rf'(<!-- wp:image \{{[^>]*?"id":){old_id}\b', rf"\g<1>{new_id}", content)

        def link(match):
            url = match.group(0)
            target = self.map_link(url)
            if target:
                return target
            self.unresolved.append(url)
            return self.fallback or url

        return self.any_old.sub(link, content)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dest", required=True)
    parser.add_argument("--old-domain", required=True)
    parser.add_argument("--state-file", required=True)
    parser.add_argument("--link-map", required=True, help="JSON object: old path (no trailing slash) -> new URL")
    parser.add_argument("--posts-file", required=True, help='JSON list of {"id": .., "type": "posts|pages|product"}')
    parser.add_argument("--fallback-url", help="Target for old-site links with no mapping (default: leave unchanged)")
    parser.add_argument("--only", help="Comma-separated post IDs to restrict to")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    dest = args.dest.rstrip("/")
    auth = get_auth()
    with open(args.state_file, encoding="utf-8") as f:
        state = json.load(f)
    with open(args.link_map, encoding="utf-8") as f:
        link_map = json.load(f)
    with open(args.posts_file, encoding="utf-8") as f:
        posts = json.load(f)
    only = {int(x) for x in args.only.split(",")} if args.only else None

    session = requests.Session()
    session.headers.update({"User-Agent": "lesponctuelles-migration-script/1.0"})
    old = re.compile(re.escape(args.old_domain), re.I)

    for post in posts:
        if only and post["id"] not in only:
            continue
        url = f"{dest}/wp-json/wp/v2/{post['type']}/{post['id']}"
        resp = session.get(url, params={"context": "edit"}, auth=auth)
        text = resp.text
        data = json.loads(text[text.find('{"id"'):])
        raw = data["content"]["raw"]
        rewriter = Rewriter(args.old_domain, dest, state, link_map, args.fallback_url)
        new = rewriter.rewrite(raw)
        before, after = len(old.findall(raw)), len(old.findall(new))
        print(f"{post['type']} {post['id']} {data['slug']}: old-domain refs {before} -> {after}"
              + (f" | unresolved: {sorted(set(rewriter.unresolved))}" if rewriter.unresolved else ""))
        if args.apply and new != raw:
            saved = session.post(url, json={"content": new}, auth=auth)
            if saved.status_code not in (200, 201):
                print(f"  ERROR saving: {saved.status_code} {saved.text[:200]}", file=sys.stderr)


if __name__ == "__main__":
    main()
