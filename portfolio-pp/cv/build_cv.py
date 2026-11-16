#!/usr/bin/env python3
"""Builds cv.html: Quentin's CV for Poils & Plumes, one A4 page per language (FR, NL, EN)."""
import pathlib
HERE = pathlib.Path(__file__).parent
EMAIL, PHONE = "quentin.michel@outlook.com", "+32 494 58 18 99"
PAW = '<svg class="paw" viewBox="0 0 24 24"><ellipse cx="4.6" cy="10.4" rx="2.2" ry="3"/><ellipse cx="9.2" cy="5.4" rx="2.2" ry="3"/><ellipse cx="14.8" cy="5.4" rx="2.2" ry="3"/><ellipse cx="19.4" cy="10.4" rx="2.2" ry="3"/><path d="M12 11c-3.5 0-6.5 3.2-6.5 6.3 0 2.2 1.8 3.2 3.6 3.2 1.2 0 1.9-.5 2.9-.5s1.7.5 2.9.5c1.8 0 3.6-1 3.6-3.2C18.5 14.2 15.5 11 12 11z"/></svg>'
CSS = """
@page { size: A4; margin: 0; }
:root { --bg:#FAF5FC; --surface:#F1E6F6; --card:#FFFFFF; --ink:#2B1038; --mute:#6D5A7A; --line:rgba(102,36,131,.2); --brand:#662483; --accent:#951272; }
* { box-sizing: border-box; }
html, body { margin: 0; background: var(--bg); color: var(--ink); }
body { font: 400 8.6pt/1.42 "Nunito", "Trebuchet MS", Arial, sans-serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 210mm; height: 297mm; padding: 10mm 14mm 8mm; position: relative; overflow: hidden; page-break-after: always; display: flex; flex-direction: column; font-size: var(--fs, 8.6pt); }
.page:last-child { page-break-after: auto; }
.label { font-weight: 800; font-size: .8em; letter-spacing: .09em; text-transform: uppercase; }
.mute { color: var(--mute); }
.paw { width: 1em; height: 1em; fill: currentColor; flex: none; }
.blob { position: absolute; top: -24mm; right: -26mm; width: 104mm; height: 96mm; background: var(--surface); border-radius: 58% 42% 47% 53% / 46% 55% 45% 54%; }
.page > :not(.blob) { position: relative; }
.head { display: flex; justify-content: space-between; align-items: flex-start; gap: 8mm; }
.name { margin: 0; font: 800 38pt/.8 "Baloo 2", sans-serif; letter-spacing: -.02em; }
.name span { display: block; }
.name .first { color: var(--brand); }
.role { margin: 3mm 0 0; font: 700 12.5pt/1.1 "Baloo 2", sans-serif; color: var(--accent); }
.coords { margin: 1.6mm 0 0; font-weight: 700; line-height: 1.45; }
.site { color: var(--accent); font-weight: 800; text-decoration: none; }
.photo { width: 36mm; height: 36mm; object-fit: cover; border: 1.3mm solid var(--card); border-radius: 44% 56% 52% 48% / 55% 44% 56% 45%; box-shadow: 0 2mm 6mm rgba(43,16,56,.16); flex: none; margin-top: -2mm; }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 2.5mm; margin-top: 3.5mm; }
.stats div { background: var(--card); border: .25mm solid var(--line); border-radius: 4.5mm; padding: 2.2mm 3.2mm; }
.stats b { display: block; font: 800 14pt/1 "Baloo 2", sans-serif; color: var(--brand); }
.stats span { display: block; font-weight: 700; font-size: .88em; line-height: 1.25; margin-top: .6mm; }
.cols { display: grid; grid-template-columns: 52mm 1fr; gap: 5mm; margin-top: 3.5mm; flex: 1; min-height: 0; }
h2 { margin: 0 0 1mm; font: 800 11.5pt/1 "Baloo 2", sans-serif; color: var(--brand); display: flex; align-items: center; gap: 1.8mm; }
h2 .paw { color: var(--accent); font-size: .85em; }
.side { display: flex; flex-direction: column; gap: 2mm; }
.box { background: var(--card); border: .25mm solid var(--line); border-radius: 4mm; padding: 2.3mm 3.2mm; }
.box.hl { background: var(--brand); color: #fff; border-color: transparent; }
.box.hl h2 { color: #fff; } .box.hl h2 .paw { color: #fff; }
.box ul { margin: 0; padding: 0; list-style: none; }
.box li { padding: 0; font-weight: 600; line-height: 1.38; }
.box li small { font-weight: 600; color: var(--mute); font-size: .92em; }
.chips { display: flex; flex-wrap: wrap; gap: .9mm; }
.chips span { font-weight: 700; font-size: .9em; background: color-mix(in srgb, #fff 20%, transparent); border-radius: 99mm; padding: .5mm 1.9mm; }
.box:not(.hl) .chips span { background: var(--surface); }
.edu b { display: block; font-weight: 800; }
.main { display: flex; flex-direction: column; min-height: 0; }
.sum { margin: 0 0 3mm; font-weight: 600; font-size: 1.06em; line-height: 1.4; }
.job { display: grid; grid-template-columns: 23mm 1fr; gap: 3mm; padding: 1.8mm 0; border-top: .25mm solid var(--line); }
.job:first-of-type { border-top: 0; padding-top: .5mm; }
.job .when { padding-top: .5mm; line-height: 1.4; }
.job .when b { display: block; }
.job h3 { margin: 0; font: 800 12pt/1 "Baloo 2", sans-serif; }
.job h3 em { font: 700 .76em/1 "Nunito", sans-serif; font-style: normal; color: var(--accent); }
.job .desc { margin: .5mm 0 1mm; color: var(--mute); font-weight: 600; font-style: italic; }
.job ul { margin: 0; padding: 0; list-style: none; }
.job li { padding-left: 3.4mm; position: relative; margin-bottom: .2mm; }
.job li::before { content: ""; position: absolute; left: 0; top: .5em; width: 1.6mm; height: 1.6mm; border-radius: 50%; background: var(--accent); }
.job li b { font-weight: 800; }
"""
SITES = "lelombard.com · thorgal.com"
C = {
"fr": dict(addr="Chaussée d'Ath 208a, 7850 Enghien", role="Marketing digital, réseaux sociaux &amp; IA",
  stats=[("200 000+","abonnés cumulés sur les réseaux du Lombard"),("20 M","de vues sur TikTok"),("150","magasins indépendants accompagnés"),("12 ans","d'expérience en marketing digital")],
  h_sum="Résumé", summary="Créatif et pragmatique, j'élabore des stratégies marketing sur le web et les réseaux sociaux, et je transpose les idées en actions de communication concrètes. Aujourd'hui, la plupart de mes tâches sont réalisées avec l'aide d'outils IA.",
  h_exp="Parcours professionnel", now="auj.",
  jobs=[
   ("03.2021 → {now}","Bruxelles","Le Lombard","Digital Marketing Manager","Éditeur belge de bandes dessinées depuis 1946 : Ducobu, Léonard, Thorgal, Les Schtroumpfs…",[
     "<b>Réseaux sociaux</b> : Facebook, Instagram, YouTube, TikTok. Plus de 200 000 abonnés cumulés et des vidéos à plusieurs millions de vues.",
     "<b>Publicité digitale</b> : Meta Ads, Google Ads, TikTok Ads, Snapchat Ads et partenariats.",
     "<b>IA</b> : contenus, vidéos, sites web et reportings réalisés avec Claude Code, ChatGPT, Copilot et Gemini.",
     "<b>Marketing digital</b> : gestion du budget, stratégie de communication, accompagnement des auteurs et éditeurs.",
     "<b>CRM</b> : e-mail marketing, analyse des données, gestion RGPD.",
     "<b>Web</b> : webmaster de lelombard.com et thorgal.com."]),
   ("01.2020 → 03.2021","Diegem","AddRetail","Creative &amp; Project Manager","Agence de communication et de publicité belge active dans le retail.",[
     "<b>Contenus digitaux</b> : design et création de sites WordPress pour PME.",
     "<b>Réseaux sociaux</b> : community management Facebook, LinkedIn Ads.",
     "<b>E-mail marketing</b> : design HTML pour Trafic et Ici Paris XL.",
     "<b>Relation clients</b> : prospection et gestion des projets."]),
   ("03.2016 → 12.2019","Nivelles","Meno Group","Web Marketeer","Coopérative de magasins de bricolage indépendants, dans toute la Belgique.",[
     "<b>Contenus digitaux</b> : rédaction SEO et webdesign de 4 sites pour 150 magasins.",
     "<b>Réseaux sociaux</b> : support et formation Facebook pour les magasins (40 profils), Meta Ads.",
     "<b>CRM</b> : e-mail marketing FR/NL, mise en place du RGPD.",
     "<b>Marques propres</b> : accompagnement de leur développement (peinture, outillage), chartes graphiques."]),
   ("01.2015 → 09.2015","Bruxelles","Media Markt","E-content Specialist","Chaîne de magasins d'électroménager qui développait son site e-commerce.",[
     "Supervision d'une équipe de 4 encodeurs, optimisation des fiches produits, contact avec les fournisseurs."]),
   ("01.2014 → 10.2014","Namur","Expansion","Project Manager Assistant","Agence de communication globale, secteur public et clients régionaux.",[
     "Appels d'offres publics, création d'identité et stratégie 360°, organisation d'événements."]),
  ],
  h_ai="IA au quotidien", ai=["Claude Code","ChatGPT","Copilot","Gemini","Grok","Higgsfield","Artlist","Firefly","Veed"],
  h_skills="Compétences", skills=["Réseaux sociaux","Publicité digitale","Marketing automation et CRM","Montage vidéo et motion design","Suite Adobe","Rédaction et SEO"],
  h_tools="Outils", tools=["Meta Business Suite","TikTok Business Manager","Agorapulse","Brevo","HubSpot","Google Analytics 4","WordPress","HTML / CSS"],
  h_lang="Langues", langs=[("Français","langue maternelle"),("Néerlandais","B2"),("Anglais","B2/C1"),("Espagnol","A2/B1")],
  h_edu="Formation", edu=[("Bachelor Chef de publicité","Esupcom Lille, 2014"),("Rédaction SEO","Cepegra Charleroi, 2016"),("Media planning","EFP Uccle, 2014"),("CESS Latin-anglais","CSA Enghien, 2008")],
  h_home="À la maison", home="Virgile, Berger Blanc Suisse, et Cléo, chat de dix ans."),
"nl": dict(addr="Aatsesteenweg 208a, 7850 Edingen", role="Digitale marketing, sociale media &amp; AI",
  stats=[("200.000+","volgers samen op de kanalen van Le Lombard"),("20 M","weergaven op TikTok"),("150","zelfstandige winkels begeleid"),("12 jaar","ervaring in digitale marketing")],
  h_sum="Profiel", summary="Creatief en pragmatisch: ik werk marketingstrategieën uit voor het web en sociale media en zet ideeën om in concrete communicatieacties. Vandaag voer ik de meeste van mijn taken uit met behulp van AI-tools.",
  h_exp="Loopbaan", now="nu",
  jobs=[
   ("03.2021 → {now}","Brussel","Le Lombard","Digital Marketing Manager","Belgische stripuitgeverij sinds 1946: Ducobu, Leonardo, Thorgal, De Smurfen…",[
     "<b>Sociale media</b>: Facebook, Instagram, YouTube, TikTok. Meer dan 200.000 volgers samen en video's met meerdere miljoenen weergaven.",
     "<b>Online advertising</b>: Meta Ads, Google Ads, TikTok Ads, Snapchat Ads en partnerships.",
     "<b>AI</b>: content, video's, websites en rapporten gemaakt met Claude Code, ChatGPT, Copilot en Gemini.",
     "<b>Digitale marketing</b>: budgetbeheer, communicatiestrategie, begeleiding van auteurs en uitgevers.",
     "<b>CRM</b>: e-mailmarketing, data-analyse, AVG-beheer.",
     "<b>Web</b>: webmaster van lelombard.com en thorgal.com."]),
   ("01.2020 → 03.2021","Diegem","AddRetail","Creative &amp; Project Manager","Belgisch communicatie- en reclamebureau, actief in retail.",[
     "<b>Digitale content</b>: design en bouw van WordPress-sites voor kmo's.",
     "<b>Sociale media</b>: community management op Facebook, LinkedIn Ads.",
     "<b>E-mailmarketing</b>: HTML-design voor Trafic en Ici Paris XL.",
     "<b>Klantrelatie</b>: prospectie en projectbeheer."]),
   ("03.2016 → 12.2019","Nijvel","Meno Group","Web Marketeer","Coöperatie van zelfstandige doe-het-zelfwinkels in heel België.",[
     "<b>Digitale content</b>: SEO-copywriting en webdesign van 4 sites voor 150 winkels.",
     "<b>Sociale media</b>: ondersteuning en Facebook-opleiding voor de winkels (40 profielen), Meta Ads.",
     "<b>CRM</b>: e-mailmarketing FR/NL, invoering van de AVG.",
     "<b>Eigen merken</b>: begeleiding van hun ontwikkeling (verf, gereedschap), huisstijlgidsen."]),
   ("01.2015 → 09.2015","Brussel","Media Markt","E-content Specialist","Elektroketen die haar webshop uitbouwde.",[
     "Leiding over een team van 4 encodeurs, optimalisatie van productfiches, contact met leveranciers."]),
   ("01.2014 → 10.2014","Namen","Expansion","Project Manager Assistant","Communicatiebureau voor de publieke sector en regionale klanten.",[
     "Overheidsopdrachten, identiteitsontwerp en 360°-strategie, organisatie van evenementen."]),
  ],
  h_ai="AI, elke dag", ai=["Claude Code","ChatGPT","Copilot","Gemini","Grok","Higgsfield","Artlist","Firefly","Veed"],
  h_skills="Vaardigheden", skills=["Sociale media","Online advertising","Marketing automation en CRM","Videomontage en motion design","Adobe-suite","Copywriting en SEO"],
  h_tools="Tools", tools=["Meta Business Suite","TikTok Business Manager","Agorapulse","Brevo","HubSpot","Google Analytics 4","WordPress","HTML / CSS"],
  h_lang="Talen", langs=[("Frans","moedertaal"),("Nederlands","B2"),("Engels","B2/C1"),("Spaans","A2/B1")],
  h_edu="Opleiding", edu=[("Bachelor Reclame","Esupcom Rijsel, 2014"),("SEO-copywriting","Cepegra Charleroi, 2016"),("Mediaplanning","EFP Ukkel, 2014"),("CESS Latijn-Engels","CSA Edingen, 2008")],
  h_home="Thuis", home="Virgile, Zwitserse Witte Herder, en Cléo, een kat van tien jaar."),
"en": dict(addr="Chaussée d'Ath 208a, 7850 Enghien", role="Digital marketing, social media &amp; AI",
  stats=[("200,000+","followers combined on Le Lombard's channels"),("20 M","views on TikTok"),("150","independent stores supported"),("12 years","of experience in digital marketing")],
  h_sum="Summary", summary="Creative and pragmatic, I build marketing strategies for the web and social media and turn ideas into concrete communication actions. Today, most of my tasks are done with the help of AI tools.",
  h_exp="Experience", now="now",
  jobs=[
   ("03.2021 → {now}","Brussels","Le Lombard","Digital Marketing Manager","Belgian comics publisher since 1946: Ducobu, Léonard, Thorgal, The Smurfs…",[
     "<b>Social media</b>: Facebook, Instagram, YouTube, TikTok. Over 200,000 followers combined and videos with several million views.",
     "<b>Online advertising</b>: Meta Ads, Google Ads, TikTok Ads, Snapchat Ads and partnerships.",
     "<b>AI</b>: content, videos, websites and reports produced with Claude Code, ChatGPT, Copilot and Gemini.",
     "<b>Digital marketing</b>: budget management, communication strategy, support for authors and editors.",
     "<b>CRM</b>: e-mail marketing, data analysis, GDPR management.",
     "<b>Web</b>: webmaster of lelombard.com and thorgal.com."]),
   ("01.2020 → 03.2021","Diegem","AddRetail","Creative &amp; Project Manager","Belgian communication and advertising agency active in retail.",[
     "<b>Web content</b>: design and build of WordPress sites for SMEs.",
     "<b>Social media</b>: Facebook community management, LinkedIn Ads.",
     "<b>E-mail marketing</b>: HTML design for Trafic and Ici Paris XL.",
     "<b>Client relations</b>: prospecting and project management."]),
   ("03.2016 → 12.2019","Nivelles","Meno Group","Web Marketeer","Cooperative of independent DIY stores across Belgium.",[
     "<b>Web content</b>: SEO copywriting and web design for 4 sites serving 150 stores.",
     "<b>Social media</b>: Facebook support and training for the stores (40 profiles), Meta Ads.",
     "<b>CRM</b>: FR/NL e-mail marketing, GDPR roll-out.",
     "<b>Private labels</b>: supported their development (paint, tools), brand guidelines."]),
   ("01.2015 → 09.2015","Brussels","Media Markt","E-content Specialist","Consumer electronics chain building up its webshop.",[
     "Supervised a team of 4 data-entry operators, optimised product pages, liaised with suppliers."]),
   ("01.2014 → 10.2014","Namur","Expansion","Project Manager Assistant","Communication agency for the public sector and regional clients.",[
     "Public tenders, identity design and 360° strategy, event organisation."]),
  ],
  h_ai="AI, every day", ai=["Claude Code","ChatGPT","Copilot","Gemini","Grok","Higgsfield","Artlist","Firefly","Veed"],
  h_skills="Skills", skills=["Social media","Online advertising","Marketing automation and CRM","Video editing and motion design","Adobe suite","Copywriting and SEO"],
  h_tools="Tools", tools=["Meta Business Suite","TikTok Business Manager","Agorapulse","Brevo","HubSpot","Google Analytics 4","WordPress","HTML / CSS"],
  h_lang="Languages", langs=[("French","mother tongue"),("Dutch","B2"),("English","B2/C1"),("Spanish","A2/B1")],
  h_edu="Education", edu=[("Bachelor in Advertising","Esupcom Lille, 2014"),("SEO copywriting","Cepegra Charleroi, 2016"),("Media planning","EFP Uccle, 2014"),("CESS Latin-English","CSA Enghien, 2008")],
  h_home="At home", home="Virgile, a White Swiss Shepherd, and Cléo, a ten-year-old cat."),
}
def h2(t): return f"<h2>{PAW}{t}</h2>"
def page(lang, d):
    stats = "".join(f"<div><b>{a}</b><span>{b}</span></div>" for a, b in d["stats"])
    jobs = ""
    for when, place, name, role, desc, bullets in d["jobs"]:
        li = "".join(f"<li>{x}</li>" for x in bullets)
        jobs += f'<article class="job"><div class="when label"><b>{when.format(now=d["now"])}</b><span class="mute">{place}</span></div><div><h3>{name} <em>· {role}</em></h3><p class="desc">{desc}</p><ul>{li}</ul></div></article>'
    chips = lambda xs: "".join(f"<span>{x}</span>" for x in xs)
    return f'''<div class="page" lang="{lang}">
  <div class="blob"></div>
  <div class="head"><div><h1 class="name"><span class="first">Quentin</span><span>Michel</span></h1><p class="role">{d["role"]}</p>
    <p class="coords">{d["addr"]} · {PHONE} · {EMAIL}<br><a class="site" href="https://quentin-michel.netlify.app/">quentin-michel.netlify.app</a></p></div><img class="photo" src="../img/duo.jpg" alt=""></div>
  <div class="stats">{stats}</div>
  <div class="cols">
    <div class="side">
      <div class="box hl">{h2(d["h_ai"])}<div class="chips">{chips(d["ai"])}</div></div>
      <div class="box">{h2(d["h_skills"])}<ul>{"".join(f"<li>{x}</li>" for x in d["skills"])}</ul></div>
      <div class="box">{h2(d["h_tools"])}<div class="chips">{chips(d["tools"])}</div></div>
      <div class="box">{h2(d["h_lang"])}<ul>{"".join(f"<li>{a} <small>{b}</small></li>" for a,b in d["langs"])}</ul></div>
      <div class="box edu">{h2(d["h_edu"])}<ul>{"".join(f"<li><b>{a}</b><small>{b}</small></li>" for a,b in d["edu"])}</ul></div>
    </div>
    <div class="main">{h2(d["h_sum"])}<p class="sum">{d["summary"]}</p>{h2(d["h_exp"])}{jobs}</div>
  </div>
</div>'''
html = f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Quentin Michel · CV Poils &amp; Plumes</title><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&family=Nunito:wght@400;600;700;800&display=swap"><style>{CSS}</style></head><body>{"".join(page(k, C[k]) for k in ("fr","nl","en"))}</body></html>'
(HERE / "cv.html").write_text(html, encoding="utf-8")
print("built")
