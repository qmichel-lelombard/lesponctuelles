#!/usr/bin/env python3
"""Copy images still hot-linked from a source site into the destination media library.

Migrated posts can keep pointing at the old site's uploads (directly, or through
the Jetpack image CDN, i0.wp.com/<old-domain>/...). Those images vanish when the
old hosting ends. This script downloads each original from the source, uploads
it to the destination media library, and records the new URLs in a state file
that rewrite_image_urls.py then uses to rewrite post content.

Resumable: already-uploaded files listed in the state file are skipped.
Requests to the source are paced, with backoff on HTTP 429.

Example:
  export WP_DEST_USER=admin
  export WP_DEST_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"
  python3 repatriate_images.py --source https://lesponctuelles.com \
      --dest https://lesponctuelles.be --paths-file ./upload_paths.json \
      --state-file ./repatriate_state.json
"""
import argparse
import json
import mimetypes
import os
import re
import sys
import time
import unicodedata
from urllib.parse import quote

import requests
from requests.auth import HTTPBasicAuth

SIZE_SUFFIX = re.compile(r"-\d+x\d+(?=\.\w+$)")


def get_auth():
    user = os.environ.get("WP_DEST_USER")
    password = os.environ.get("WP_DEST_APP_PASSWORD")
    if not user or not password:
        raise SystemExit("Set WP_DEST_USER and WP_DEST_APP_PASSWORD environment variables.")
    return HTTPBasicAuth(user, password)


def ascii_filename(filename):
    normalized = unicodedata.normalize("NFKD", filename)
    return normalized.encode("ascii", "ignore").decode("ascii") or "image"


def download(session, source, path, pause):
    url = source + quote(path)
    delay = 20
    for _ in range(6):
        resp = session.get(url, timeout=120)
        if resp.status_code == 429:
            print(f"    429 from source, waiting {delay}s", flush=True)
            time.sleep(delay)
            delay = min(delay * 2, 300)
            continue
        time.sleep(pause)
        return resp
    return resp


def upload(session, dest, auth, filename, data):
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    resp = session.post(
        f"{dest}/wp-json/wp/v2/media",
        headers={
            "Content-Disposition": f'attachment; filename="{ascii_filename(filename)}"',
            "Content-Type": content_type,
        },
        data=data,
        auth=auth,
        timeout=300,
    )
    if resp.status_code not in (200, 201):
        return None, f"{resp.status_code} {resp.text[:200]}"
    text = resp.text
    return json.loads(text[text.find('{"id"'):]), None


def summarize(media):
    details = media.get("media_details") or {}
    sizes = {
        name: {"w": s.get("width"), "h": s.get("height"), "url": s.get("source_url")}
        for name, s in (details.get("sizes") or {}).items()
    }
    return {
        "id": media["id"],
        "url": media["source_url"],
        "w": details.get("width"),
        "h": details.get("height"),
        "sizes": sizes,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", required=True, help="Old site base URL")
    parser.add_argument("--dest", required=True, help="New site base URL")
    parser.add_argument("--paths-file", required=True, help="JSON list of /wp-content/uploads/... paths referenced by posts")
    parser.add_argument("--state-file", required=True, help="JSON state file (created/updated)")
    parser.add_argument("--pause", type=float, default=2.0, help="Seconds between source requests")
    parser.add_argument("--limit", type=int, help="Process at most N new files (for a test run)")
    args = parser.parse_args()

    source, dest = args.source.rstrip("/"), args.dest.rstrip("/")
    auth = get_auth()
    with open(args.paths_file, encoding="utf-8") as f:
        referenced = json.load(f)
    state = {}
    if os.path.exists(args.state_file):
        with open(args.state_file, encoding="utf-8") as f:
            state = json.load(f)

    session = requests.Session()
    session.headers.update({"User-Agent": "lesponctuelles-migration-script/1.0"})

    done = 0
    for ref in referenced:
        if "id" in state.get(ref, {}):
            continue
        if args.limit is not None and done >= args.limit:
            break
        # A "-300x200" suffix usually marks a generated size, but some originals are named that way.
        candidates = [SIZE_SUFFIX.sub("", ref)]
        if candidates[0] != ref:
            candidates.append(ref)
        entry = None
        for candidate in candidates:
            if candidate in state and "id" in state[candidate]:
                entry = dict(state[candidate])
                break
            resp = download(session, source, candidate, args.pause)
            if resp.status_code != 200:
                print(f"  source {resp.status_code}: {candidate}", flush=True)
                continue
            media, error = upload(session, dest, auth, os.path.basename(candidate), resp.content)
            if error:
                print(f"  UPLOAD FAILED {candidate}: {error}", file=sys.stderr, flush=True)
                continue
            entry = summarize(media)
            entry["original"] = candidate
            state[candidate] = entry
            done += 1
            print(f"  ok {candidate} -> id={entry['id']} ({len(resp.content) // 1024} KB)", flush=True)
            break
        state[ref] = entry if entry else {"error": "not retrievable from source"}
        with open(args.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=1)

    ok = sum(1 for r in referenced if "id" in state.get(r, {}))
    failed = [r for r in referenced if "error" in state.get(r, {})]
    print(f"Done. {ok}/{len(referenced)} referenced paths resolved, {len(failed)} failed.")
    for r in failed:
        print(f"  failed: {r}")


if __name__ == "__main__":
    main()
