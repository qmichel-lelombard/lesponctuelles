#!/usr/bin/env python3
"""Génère index.html à partir de template.html + authors.json.

Usage : python3 build.py
Pour modifier un auteur (bio, photo, œuvres), éditer authors.json puis relancer.
"""
import hashlib
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
authors = json.loads((ROOT / "authors.json").read_text(encoding="utf-8"))
tpl = (ROOT / "template.html").read_text(encoding="utf-8")


def initials(a):
    return (a["first"][:1] + a["name"][:1]).upper() if a["first"] else a["name"][:2].upper()


def fullname(a):
    return f'{a["first"]} {a["name"]}'.strip()


def card(a, i, total):
    cls = "author" + (" author--lead" if a["id"] == "duval" else "")
    if a["photo"]:
        media = (f'<img src="{a["photo"]}" alt="Portrait de {escape(fullname(a))}" '
                 f'loading="lazy" decoding="async">')
    else:
        media = (f'<div class="author__mono" role="img" aria-label="Portrait à venir">'
                 f'<span>{initials(a)}</span><small>Signal en attente</small></div>')
    badge = f'<span class="chip chip--hot">{escape(a["badge"])}</span>' if a.get("badge") else ""
    born = f'<p class="author__born">{escape(a["born"])}</p>' if a["born"] else ""
    if a["bio"]:
        bio = f'<p class="author__bio">{escape(a["bio"])}</p>'
    else:
        bio = '<p class="author__bio author__bio--wait">Fiche détaillée en cours de décryptage.</p>'
    chapter = f'<p class="author__chapter">{escape(a["chapter"])}</p>' if a.get("chapter") else ""
    works = ""
    if a["works"]:
        works = ('<div class="author__works"><h4>Repères</h4><ul>'
                 + "".join(f"<li>{escape(w)}</li>" for w in a["works"]) + "</ul></div>")
    credit = f'<span class="author__credit">{escape(a["credit"])}</span>' if a.get("credit") else ""
    first = f'<span class="author__first">{escape(a["first"])}</span>' if a["first"] else ""
    return f'''
    <article class="{cls} reveal" id="auteur-{a["id"]}" data-author="{a["id"]}">
      <div class="author__media">{media}<i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
        {credit}</div>
      <div class="author__body">
        <div class="chips"><span class="chip">{escape(a["role"])}</span>{badge}</div>
        <h3 class="author__name">{first}<span class="decode" data-text="{escape(a["name"].upper())}">{escape(a["name"].upper())}</span></h3>
        {born}{chapter}{bio}{works}
        <a class="link-out" href="{a["link"]}" target="_blank" rel="noopener">Fiche sur lelombard.com <span aria-hidden="true">↗</span></a>
      </div>
    </article>'''


def orbit_nodes():
    draw = [a for a in authors if a["id"] != "duval"]
    n = len(draw)
    out = []
    for k, a in enumerate(draw):
        ang = 360 / n * k
        out.append(
            f'<li style="--a:{ang:.2f}deg"><a href="#auteur-{a["id"]}" class="orbit__node">'
            f'<span class="orbit__dot"></span><span class="orbit__label">{escape(a["name"].upper())}</span></a></li>')
    return "\n".join(out)


cards = "\n".join(card(a, i + 1, len(authors)) for i, a in enumerate(authors))
html = tpl.replace("{{AUTHORS}}", cards).replace("{{ORBIT}}", orbit_nodes())


def versioned(m):
    f = ROOT / m.group(1)
    return f'{m.group(1)}?v={hashlib.md5(f.read_bytes()).hexdigest()[:8]}'


# anti-cache : CSS/JS/polices référencés avec une empreinte du contenu
html = re.sub(r'(assets/(?:css/style\.css|js/main\.js|js/music\.js|fonts/fonts\.css))(?=")', versioned, html)


def typo(text):
    """Espace insécable avant ; : ! ? » et après « (typographie française)."""
    text = re.sub(r"[ \u202f]+(?=[;:!?»])", "\u00a0", text)
    return re.sub(r"(?<=«)[ \u202f]+", "\u00a0", text)


def typo_html(doc):
    # ne touche ni aux balises/attributs, ni aux blocs <style> ; traite le texte et le JSON du carnet
    parts = re.split(r"(<[^>]+>)", doc)
    out, skip = [], False
    for p in parts:
        if p.startswith("<"):
            low = p.lower()
            if low.startswith("<style"):
                skip = True
            elif low.startswith("</style"):
                skip = False
            out.append(p)
        else:
            out.append(p if skip else typo(p))
    return "".join(out)


html = typo_html(html)
(ROOT / "index.html").write_text(html, encoding="utf-8")
print(f"index.html généré ({len(html)//1024} Ko, {len(authors)} auteurs)")
