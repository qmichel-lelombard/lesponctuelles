#!/usr/bin/env python3
"""Build the .htaccess that takes over lesponctuelles.com redirects on plain Apache hosting.

Input: the Redirection plugin's JSON export. Output: an .htaccess for a folder
that serves nothing but redirects to the new domain (no WordPress behind it).

  python3 build_htaccess.py lesponctuelles-com-redirection-export.json ovh/.htaccess
"""
import json
import re
import sys

NEW = "https://lesponctuelles.be"
# WordPress query variables that mean something different (or nothing) on the new site.
WP_QUERY_VARS = "p|page_id|attachment_id|cat|tag|s|m|author|preview|rest_route|post_type|feed|amp"


def pattern(source):
    path = source.strip("/")
    return "".join(c if re.match(r"[A-Za-z0-9/_-]", c) or ord(c) > 127 else "\\" + c for c in path)


def main():
    export, out = sys.argv[1], sys.argv[2]
    with open(export, encoding="utf-8") as f:
        rules = [r for r in json.load(f)["redirects"] if r["enabled"]]
    explicit = sorted((r for r in rules if not r["regex"] and r["url"] != "/"), key=lambda r: r["position"])

    lines = [
        "# Redirections de lesponctuelles.com vers lesponctuelles.be",
        "# Genere par build_htaccess.py a partir de l'export du plugin Redirection.",
        "# Ce dossier ne sert qu'a rediriger : aucun site n'y est installe.",
        "",
        "<IfModule mod_rewrite.c>",
        "RewriteEngine On",
        "",
        "# Validation du certificat SSL (Let's Encrypt) : ne pas rediriger.",
        "RewriteRule ^\\.well-known/ - [L]",
        "",
        "# Accueil. Les parametres propres a l'ancien WordPress sont abandonnes,",
        "# les autres (utm, fbclid...) sont transmis.",
        f"RewriteCond %{{QUERY_STRING}} (^|&)({WP_QUERY_VARS})= [NC]",
        f"RewriteRule ^$ {NEW}/ [R=301,L,QSD]",
        f"RewriteRule ^$ {NEW}/ [R=301,L]",
        "",
        f"# Pages, articles, produits et categories ayant un equivalent ({len(explicit)} regles).",
    ]
    for r in explicit:
        target = r["action_data"]["url"]
        assert not re.search(r"[%$ ]", target), target
        lines.append(f"RewriteRule ^{pattern(r['url'])}/?$ {target} [R=301,L,NC]")
    lines += [
        "",
        "# Categories et etiquettes sans equivalent : vers le blog.",
        f"RewriteRule ^(category|tag)/ {NEW}/blog/ [R=301,L,NC,QSD]",
        "",
        "# Anciens fichiers (images...) : pas de redirection vers une page, erreur 404 normale.",
        "RewriteRule ^wp-content/ - [L]",
        "",
        "# Tout le reste : vers l'accueil.",
        f"RewriteRule ^ {NEW}/ [R=301,L,QSD]",
        "</IfModule>",
        "",
    ]
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"{len(explicit)} explicit rules written to {out}")


if __name__ == "__main__":
    main()
