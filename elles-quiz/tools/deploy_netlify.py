"""Construit les fonctions (suivi + stats) et déploie le site sur Netlify via l'API.
Prérequis : variable NETLIFY_AUTH_TOKEN, NETLIFY_SITE_ID ; `npm install` dans netlify/ ; mot de passe admin
dans la variable d'environnement Netlify ADMIN_PASSWORD (voir README). Usage : python3 tools/deploy_netlify.py"""
import hashlib, io, json, os, subprocess, sys, urllib.request, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN, SITE = os.environ.get("NETLIFY_AUTH_TOKEN", "x"), os.environ["NETLIFY_SITE_ID"]
API = "https://api.netlify.com/api/v1"
def call(method, path, data=None, ctype="application/json"):
    req = urllib.request.Request(API + path, data=data, method=method, headers={"Authorization": "Bearer " + TOKEN, "Content-Type": ctype})
    with urllib.request.urlopen(req) as r: b = r.read(); return json.loads(b) if b and ctype == "application/json" and r.headers.get("Content-Type","").startswith("application/json") else b

# 1) fonctions -> zip (un fichier <nom>.js par fonction)
fn = {}
for name in ("track", "stats"):
    out = f"{ROOT}/netlify/.build/{name}.js"
    subprocess.run([f"{ROOT}/netlify/node_modules/.bin/esbuild", f"{ROOT}/netlify/functions/{name}.mjs", "--bundle", "--platform=node", "--format=cjs", "--target=node20", f"--outfile={out}", "--log-level=error"], check=True)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z: z.write(out, f"{name}.js")
    fn[name] = buf.getvalue()

# 2) fichiers statiques
files = {}
for d, _, fs in os.walk(ROOT):
    rel = os.path.relpath(d, ROOT)
    if rel.split(os.sep)[0] in ("netlify", "tools", "node_modules", ".git", "video") : continue
    for f in fs:
        if f.endswith((".docx", ".md", ".py")): continue
        p = os.path.join(d, f); key = "/" + os.path.normpath(os.path.join(rel, f)).replace(os.sep, "/")
        files[key] = open(p, "rb").read()
headers = b"/gestion-elles/*\n  X-Robots-Tag: noindex, nofollow\n  Cache-Control: no-store\n/.netlify/functions/*\n  Cache-Control: no-store\n"
files["/_headers"] = headers
# l'ancienne adresse .netlify.app redirige vers le domaine officiel (le #resultat-… est conservé)
files["/_redirects"] = b"https://quelle-elles-es-tu.netlify.app/* https://elles.lelombard.com/:splat 301!\nhttp://quelle-elles-es-tu.netlify.app/* https://elles.lelombard.com/:splat 301!\n"

body = {"files": {k: hashlib.sha1(v).hexdigest() for k, v in files.items()},
        "functions": {k: hashlib.sha256(v).hexdigest() for k, v in fn.items()}}
dep = call("POST", f"/sites/{SITE}/deploys", json.dumps(body).encode())
print("deploy", dep["id"], "requis:", len(dep.get("required", [])), dep.get("required_functions"))
by_sha = {hashlib.sha1(v).hexdigest(): k for k, v in files.items()}
for sha in dep.get("required", []):
    k = by_sha[sha]; call("PUT", f"/deploys/{dep['id']}/files{k}", files[k], "application/octet-stream")
fn_by_sha = {hashlib.sha256(v).hexdigest(): k for k, v in fn.items()}
for sha in dep.get("required_functions", []) or []:
    name = fn_by_sha[sha]; call("PUT", f"/deploys/{dep['id']}/functions/{name}?runtime=js", fn[name], "application/octet-stream")
print("ok", dep.get("ssl_url"))
