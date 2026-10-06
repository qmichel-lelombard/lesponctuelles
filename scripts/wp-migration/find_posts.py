#!/usr/bin/env python3
"""Search posts by title/keyword on a public WordPress site via the REST API.

Helper for picking the right --slugs to pass to export_posts.py when you only
know approximate titles (e.g. from a handwritten list) and not exact slugs.
Uses the built-in WordPress `search` REST parameter (matches title/content),
so no credentials are needed for a public source site.

Examples:
  # One query
  python3 find_posts.py --source https://lesponctuelles.com \
      --query "Sous la plume"

  # Many queries at once, one per line in a file
  python3 find_posts.py --source https://lesponctuelles.com \
      --queries-file ./queries.txt
"""
import argparse
import sys

import requests


def search_posts(base_url, session, query, per_page=10):
    resp = session.get(
        f"{base_url}/wp-json/wp/v2/posts",
        params={"search": query, "per_page": per_page, "status": "publish"},
    )
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", required=True, help="Source site base URL, e.g. https://lesponctuelles.com")
    parser.add_argument("--query", action="append", default=[], help="A search phrase; repeatable")
    parser.add_argument("--queries-file", help="Text file with one search phrase per line")
    parser.add_argument("--per-page", type=int, default=10, help="Max results shown per query (default: 10)")
    args = parser.parse_args()

    queries = list(args.query)
    if args.queries_file:
        with open(args.queries_file, encoding="utf-8") as f:
            queries.extend(line.strip() for line in f if line.strip())
    if not queries:
        raise SystemExit("Provide at least one --query or a --queries-file")

    base_url = args.source.rstrip("/")
    session = requests.Session()
    session.headers.update({"User-Agent": "lesponctuelles-migration-script/1.0"})

    all_slugs = []
    for query in queries:
        print(f"\n=== {query!r} ===")
        try:
            results = search_posts(base_url, session, query, args.per_page)
        except requests.HTTPError as exc:
            print(f"  error: {exc}", file=sys.stderr)
            continue
        if not results:
            print("  (aucun résultat)")
            continue
        for post in results:
            slug = post["slug"]
            title = post["title"]["rendered"]
            link = post.get("link", "")
            print(f"  slug={slug!r}  title={title!r}  {link}")
            all_slugs.append(slug)

    print("\n--- Slugs trouvés (à vérifier/dédupliquer avant export) ---")
    print(",".join(dict.fromkeys(all_slugs)))


if __name__ == "__main__":
    main()
