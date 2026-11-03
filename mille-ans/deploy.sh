#!/bin/sh
# Construit dist/ (fichiers publics uniquement) et déploie le site + les fonctions sur Netlify.
# Prérequis : npm i (dépendance @netlify/blobs) et netlify-cli (npm i -g netlify-cli), NETLIFY_AUTH_TOKEN défini.
set -e
cd "$(dirname "$0")"
python3 -I build.py
rm -rf dist && mkdir dist
cp -r index.html _headers _redirects robots.txt sitemap.xml assets admin dist/
netlify deploy --prod --dir=dist --functions=netlify/functions --site=mille-ans-lelombard "$@"
