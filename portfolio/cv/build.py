#!/usr/bin/env python3
"""Builds letters.html (FR/NL/EN cover letters) and cv.html (FR/EN CV) in the portfolio style.
Print each to PDF with print_pdf.js (Chromium)."""
import re, pathlib

HERE = pathlib.Path(__file__).parent
CSS = (HERE / "base.css").read_text(encoding="utf-8")
FONT = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=Martian+Mono:wght@300;400;500;700&display=swap">'
PORTFOLIO = "https://quentin-michel.netlify.app/"
PFLINK = '<a href="https://quentin-michel.netlify.app/" style="white-space:nowrap"><strong>quentin-michel.netlify.app</strong></a>'
EMAIL = "quentin.michel@outlook.com"
LINKEDIN = "linkedin.com/in/quentin-michel"


def doc(title, lang, body):
    return f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>{title}</title>{FONT}<style>{CSS}</style></head><body>{body}</body></html>'


# ------------------------------------------------------------------ letters
L = {
    "fr": dict(
        lang="fr", place="Enghien, Belgique", tag="Candidature · Digital Marketing Specialist, Denza BeLux", soc="Charge",
        k_to="Destinataire", to="BYD Europe<br>Recrutement Denza BeLux", k_date="Date", date="Octobre 2026",
        k_obj="Objet", obj="Digital Marketing Specialist, Denza (BeLux)", k_pf="Portfolio",
        head="Faire vivre une marque qui fait rêver", hello="Madame, Monsieur,",
        p=[
            "Denza se développe en Belgique et au Luxembourg avec une marque encore à installer dans les esprits. Le poste de Digital Marketing Specialist consiste à construire son ton, son calendrier éditorial et sa communauté. C'est le travail que je préfère, et celui que je fais depuis plus de dix ans.",
            "Chef de projet digital au Lombard depuis avril 2021, je pilote avec l'agence les campagnes de lancement d'albums et de séries, du brief et du budget jusqu'au bilan chiffré. Je produis ou sous-traite les visuels, avec la suite Adobe et des outils d'IA, et je fais vivre les réseaux de la maison : <strong>plus de 200 000 abonnés cumulés, construits de zéro, et des vidéos qui ont dépassé plusieurs millions de vues</strong>. Je suis aussi webmaster de lelombard.com et de thorgal.com.",
            "Ce que vous demandez, je le pratique déjà. Je tiens la cohérence de ton et de marque sur des licences très connues comme Les Schtroumpfs. Je coordonne agences et équipes autour d'un même calendrier. Je publie avec Meta Business Suite et Agorapulse, et j'ai pratiqué Hootsuite. Je pilote des médias payants sur Meta, TikTok, Snapchat et Google, suivis dans des rapports chiffrés. Enfin, j'ai géré des situations sensibles, comme la polémique autour d'illustrations générées par IA ou, chez Meno, des photos produits erronées et des avis clients négatifs : répondre vite, calmement et avec les faits.",
            "L'automobile m'intéresse par le design, les marques et leur histoire. Je connais la plupart des modèles BYD et Denza vendus en Europe sans avoir encore pu les conduire. La Z9 GT réunit luxe et sportivité pour tous les jours, et la Seal me parle par son confort, son silence et sa puissance. Cette curiosité nourrit des contenus justes pour la communauté.",
            "Je travaille en français, langue maternelle, et j'utilise professionnellement le néerlandais (niveau B2, e-mailings FR/NL chez Meno) et l'anglais (B2/C1). Je suis motivé pour consolider mon néerlandais et prêt à l'illustrer en entretien. Mon portfolio, {PF}, est d'ailleurs disponible en trois langues.",
            "Je serais heureux de vous présenter ma vision des réseaux de Denza BeLux lors d'un entretien.",
            "Avec mes salutations les meilleures,",
        ]),
    "nl": dict(
        lang="nl", place="Edingen, België", tag="Sollicitatie · Digital Marketing Specialist, Denza BeLux", soc="Lading",
        k_to="Bestemmeling", to="BYD Europe<br>Werving Denza BeLux", k_date="Datum", date="Oktober 2026",
        k_obj="Betreft", obj="Digital Marketing Specialist, Denza (BeLux)", k_pf="Portfolio",
        head="Een merk laten leven dat doet dromen", hello="Geachte mevrouw, geachte heer,",
        p=[
            "Denza groeit in België en Luxemburg met een merk dat nog in de hoofden moet landen. De functie van Digital Marketing Specialist bestaat erin zijn toon, redactiekalender en community op te bouwen. Dat is het werk dat ik het liefst doe, en dat ik al meer dan tien jaar doe.",
            "Sinds april 2021 ben ik digital projectmanager bij Le Lombard. Samen met het bureau stuur ik de lanceringscampagnes van albums en reeksen aan, van briefing en budget tot becijferde evaluatie. Ik maak de visuals zelf of besteed ze uit, met Adobe en AI-tools, en ik houd de sociale kanalen van het huis levendig: <strong>meer dan 200.000 volgers samen, vanaf nul opgebouwd, en video's met meerdere miljoenen weergaven</strong>. Daarnaast ben ik webmaster van lelombard.com en thorgal.com.",
            "Wat u vraagt, doe ik al. Ik bewaak de consistentie van toon en merk bij bekende licenties zoals De Smurfen. Ik coördineer bureaus en teams rond één kalender. Ik publiceer met Meta Business Suite en Agorapulse en heb ervaring met Hootsuite. Ik stuur betaalde media aan op Meta, TikTok, Snapchat en Google, opgevolgd in rapporten met cijfers. Tot slot heb ik gevoelige situaties beheerd, zoals de ophef over met AI gegenereerde illustraties of, bij Meno, foute productfoto's en negatieve klantenreviews: snel, kalm en met de feiten reageren.",
            "Auto's boeien me door hun design, hun merken en hun geschiedenis. Ik ken de meeste BYD- en Denza-modellen die in Europa verkocht worden, zonder ze al te hebben kunnen besturen. De Z9 GT combineert luxe en sportiviteit voor elke dag, en de Seal spreekt me aan door zijn comfort, stilte en vermogen. Die nieuwsgierigheid voedt content die klopt voor de community.",
            "Frans is mijn moedertaal. Nederlands (niveau B2, onder meer FR/NL-mailings bij Meno) en Engels (B2/C1) gebruik ik professioneel. Ik wil mijn Nederlands graag verder versterken en toon het u graag tijdens een gesprek. Mijn portfolio, {PF}, bestaat trouwens in drie talen.",
            "Graag licht ik tijdens een gesprek mijn visie op de sociale kanalen van Denza BeLux toe.",
            "Met vriendelijke groeten,",
        ]),
    "en": dict(
        lang="en", place="Enghien, Belgium", tag="Application · Digital Marketing Specialist, Denza BeLux", soc="Charge",
        k_to="To", to="BYD Europe<br>Denza BeLux Recruitment", k_date="Date", date="October 2026",
        k_obj="Subject", obj="Digital Marketing Specialist, Denza (BeLux)", k_pf="Portfolio",
        head="Bringing a brand that makes people dream to life", hello="Dear Sir or Madam,",
        p=[
            "Denza is growing in Belgium and Luxembourg with a brand that still has to settle in people's minds. The Digital Marketing Specialist role is about building its tone, editorial calendar and community. It is the work I like best, and the work I have been doing for more than ten years.",
            "I have been digital project manager at Le Lombard since April 2021. With the agency, I run album and series launch campaigns, from brief and budget to a results report. I produce or subcontract the visuals, using Adobe and AI tools, and I keep the publisher's channels alive: <strong>over 200,000 followers combined, built from zero, and videos that have passed several million views</strong>. I am also webmaster of lelombard.com and thorgal.com.",
            "What you ask for, I already do. I keep tone and brand consistent on well-known licences such as The Smurfs. I coordinate agencies and teams around one calendar. I publish with Meta Business Suite and Agorapulse, and I have used Hootsuite. I run paid media on Meta, TikTok, Snapchat and Google, tracked in reports with real numbers. And I have handled sensitive situations, such as the backlash over AI-generated illustrations or, at Meno, wrong product photos and negative customer reviews: answer fast, calmly and with facts.",
            "I am drawn to cars through design, brands and history. I know most of the BYD and Denza models sold in Europe, without yet having driven one. The Z9 GT combines luxury and sportiness for every day, and the Seal speaks to me through its comfort, silence and power. That curiosity feeds content that rings true with the community.",
            "French is my mother tongue. I use Dutch (B2 level, including FR/NL e-mailings at Meno) and English (B2/C1) professionally. I am keen to strengthen my Dutch further and happy to show it in an interview. My portfolio, {PF}, incidentally exists in three languages.",
            "I would be glad to present my vision for Denza BeLux's social channels in an interview.",
            "Kind regards,",
        ]),
}


def letter_page(d):
    paras = "".join(f"<p>{x.replace('{PF}', PFLINK)}</p>" for x in d["p"][:-1])
    return f'''<div class="page">
  <div class="top"><span class="mark">QM</span><span class="soc"><span class="mono mute">{d["soc"]}</span><span class="bar"></span><span class="mono">100 %</span></span></div>
  <div class="tag mono">{d["tag"]}</div>
  <h1 class="name"><img class="bladeimg" src="name-blade.png" alt="Quentin"><span>Michel</span></h1>
  <div class="contact mono"><span>{EMAIL}</span><span>{LINKEDIN}</span><span>{d["place"]}</span></div>
  <div class="letter">
    <div class="meta">
      <p class="mono mute">{d["k_to"]}<b>{d["to"]}</b></p>
      <p class="mono mute">{d["k_date"]}<b>{d["date"]}</b></p>
      <p class="mono mute">{d["k_obj"]}<b>{d["obj"]}</b></p>
      <p class="mono mute">{d["k_pf"]}<b style="font-stretch:100%;font-size:8pt;text-transform:none;font-weight:600;overflow-wrap:anywhere"><a href="{PORTFOLIO}">quentin-michel.<br>netlify.app</a></b></p>
    </div>
    <div class="body">
      <p class="obj">{d["head"]}</p>
      <p>{d["hello"]}</p>
      {paras}
      <p>{d["p"][-1]}</p>
      <p class="sig">Quentin Michel</p>
    </div>
  </div>
</div>'''


# ------------------------------------------------------------------ CV
C = {
    "fr": dict(
        lang="fr", place="Enghien, Belgique", top="Curriculum vitae · Digital Marketing Specialist, Denza BeLux",
        role="Chef de projet digital, Le Lombard · dans le métier depuis 2012", now="auj.",
        stats=[("200 000+", "abonnés cumulés sur les réseaux du Lombard, partis de zéro"), ("20 M", "de vues sur TikTok, sur certaines vidéos"), ("100k", "abonnés sur Instagram"), ("4", "plateformes média payant : Meta, TikTok, Snapchat, Google")],
        h_lang="Langues", langs=[("Français", "langue maternelle"), ("Néerlandais", "B2"), ("Anglais", "B2/C1")],
        h_tools="Outils",
        tools=[("Publication", "Meta Business Suite, Agorapulse, Hootsuite"), ("Médias payants", "Google Ads, Meta Ads, LinkedIn Ads, TikTok Ads, Snapchat Ads"), ("Mesure", "Google Analytics 4, Looker Studio"), ("Création et web", "Adobe Creative Cloud, outils d'IA, WordPress")],
        h_edu="Formation", edu=[("Bachelor Publicité", "Esupcom Lille, 2014"), ("Media planning", "EFP Uccle, 2014"), ("Web content", "Cepegra Charleroi, 2016"), ("CESS Latin-anglais", "CSA Enghien, 2008")],
        h_int="Centres d'intérêt", interests="Design et histoire de l'automobile, architecture, voyages, lecture, dessin, théâtre et one-man show.",
        h_exp="Expérience",
        jobs=[
            ("04.2021 → {now}", "Le Lombard", "Le Lombard", "Chef de projet digital", [
                "Lancements : campagnes pilotées avec l'agence, du brief au bilan chiffré, visuels produits ou sous-traités (Adobe, IA).",
                "Médias payants : Meta, TikTok, Snapchat et Google Ads, suivis dans des rapports chiffrés.",
                "Contenus : filtre Snapchat des Schtroumpfs, vidéos originales en prises de vues, animation 3D et IA.",
                "Web et communauté : webmaster de lelombard.com et thorgal.com, animation avec Agorapulse, gestion des situations sensibles."]),
            ("01.2020 → 03.2021", "Diegem", "AddRetail", "Project & Creative Manager · PubliFast", [
                "Sites WordPress créés pour des clients.", "Campagnes Facebook et LinkedIn Ads, animation de communautés.",
                "E-mailings HTML : conception et rédaction pour des marques belges.", "Relation client, prospection et pilotage des projets."]),
            ("03.2016 → 12.2019", "Nivelles", "Meno Group", "Web marketeer", [
                "Web : rédaction SEO et webdesign de 4 sites pour 150 magasins de bricolage.", "Réseaux : community management, Facebook Ads, formation et accompagnement.",
                "E-mailing FR/NL, e-commerce (prix, expérience utilisateur) et Google Analytics."]),
        ],
        small=[("01.2015 → 09.2015", "Bruxelles", "Media Markt", "Spécialiste e-content · gestion d'équipe, optimisation de contenu, fournisseurs"),
               ("01.2014 → 10.2014", "Namur", "Expansion", "Assistant chef de projet · communication, stratégie marketing, événements"),
               ("11.2012 → 12.2013", "Bruxelles", "Zenith Media", "Assistant achat presse · media planning, recherche médias, achat presse")],
        h_work="Réalisations", w1="Réseaux du Lombard",
        nets=[("Facebook", "12 ans d'expérience"), ("Instagram", "100k abonnés"), ("TikTok", "20 millions de vues"), ("YouTube", "motion design et Ads")],
        w2="Sites gérés en tant que webmaster", w3="Sites WordPress conçus"),
    "en": dict(
        lang="en", place="Enghien, Belgium", top="Résumé · Digital Marketing Specialist, Denza BeLux",
        role="Digital project manager, Le Lombard · in the trade since 2012", now="now",
        stats=[("200,000+", "followers combined across Le Lombard's social channels, built from zero"), ("20 M", "views on TikTok, on some videos"), ("100K", "Instagram followers"), ("4", "paid media platforms: Meta, TikTok, Snapchat, Google")],
        h_lang="Languages", langs=[("French", "mother tongue"), ("Dutch", "B2"), ("English", "B2/C1")],
        h_tools="Tools",
        tools=[("Publishing", "Meta Business Suite, Agorapulse, Hootsuite"), ("Paid media", "Google Ads, Meta Ads, LinkedIn Ads, TikTok Ads, Snapchat Ads"), ("Measurement", "Google Analytics 4, Looker Studio"), ("Creative and web", "Adobe Creative Cloud, AI tools, WordPress")],
        h_edu="Education", edu=[("Bachelor in Advertising", "Esupcom Lille, 2014"), ("Media planning", "EFP Uccle, 2014"), ("Web content", "Cepegra Charleroi, 2016"), ("CESS Latin-English", "CSA Enghien, 2008")],
        h_int="Interests", interests="Design and history of cars, architecture, travel, reading, drawing, theatre and one-man shows.",
        h_exp="Experience",
        jobs=[
            ("04.2021 → {now}", "Le Lombard", "Le Lombard", "Digital project manager", [
                "Launches: campaigns run with the agency, from brief to results report, visuals produced or subcontracted (Adobe, AI).",
                "Paid media: Meta, TikTok, Snapchat and Google Ads, tracked in reports with real numbers.",
                "Content: Smurfs Snapchat filter, original videos shot live, in 3D animation and with AI.",
                "Web and community: webmaster of lelombard.com and thorgal.com, community management with Agorapulse, handling sensitive situations."]),
            ("01.2020 → 03.2021", "Diegem", "AddRetail", "Project & Creative Manager · PubliFast", [
                "WordPress sites built for clients.", "Facebook and LinkedIn Ads campaigns, community management.",
                "HTML e-mailings: design and copywriting for Belgian brands.", "Client relations, prospecting and project management."]),
            ("03.2016 → 12.2019", "Nivelles", "Meno Group", "Web marketeer", [
                "Web: SEO copywriting and web design for 4 sites serving 150 DIY stores.", "Social: community management, Facebook Ads, training and support.",
                "FR/NL e-mailing, e-commerce (prices, user experience) and Google Analytics."]),
        ],
        small=[("01.2015 → 09.2015", "Brussels", "Media Markt", "E-content specialist · team management, content optimisation, suppliers"),
               ("01.2014 → 10.2014", "Namur", "Expansion", "Project manager assistant · communication, marketing strategy, events"),
               ("11.2012 → 12.2013", "Brussels", "Zenith Media", "Print buyer assistant · media planning, media research, print buying")],
        h_work="Selected work", w1="Le Lombard's channels",
        nets=[("Facebook", "12 years of experience"), ("Instagram", "100K followers"), ("TikTok", "20 million views"), ("YouTube", "motion design and Ads")],
        w2="Sites run as webmaster", w3="WordPress sites designed"),
}


def cv_page(d):
    stats = "".join(f"<div><b>{a}</b><span>{b}</span></div>" for a, b in d["stats"])
    langs = "".join(f"<li>{a} <small>{b}</small></li>" for a, b in d["langs"])
    tools = "".join(f"<li><b>{a}</b><br>{b}</li>" for a, b in d["tools"])
    edu = "".join(f"<li><b>{a}</b><br><small>{b}</small></li>" for a, b in d["edu"])
    jobs = ""
    for when, place, name, role, bullets in d["jobs"]:
        li = "".join(f"<li>{x}</li>" for x in bullets)
        jobs += f'<article class="job"><div class="when mono"><b>{when.format(now=d["now"])}</b><br><span class="mute">{place}</span></div><div><h3>{name}</h3><p class="role">{role}</p><ul>{li}</ul></div></article>'
    for when, place, name, role in d["small"]:
        jobs += f'<article class="job small"><div class="when mono"><b>{when}</b><br><span class="mute">{place}</span></div><div><h3>{name}</h3><p class="role" style="margin-bottom:0">{role}</p></div></article>'
    nets = "".join(f'<span><b class="blue">{a}</b> · {b}</span>' for a, b in d["nets"])
    cur = "".join(f'<span class="cur">{x}</span>' for x in ["lelombard.com", "thorgal.com"])
    old = "".join(f"<span>{x}</span>" for x in ["meno.be", "menopro.be", "handyhome.be", "mediamarkt.be"])
    wp = "".join(f"<span>{x}</span>" for x in ["unjourencouleurs.be", "lesponctuelles.be", "guillaumetessaro.be", "marcherman.be"])
    return f'''<div class="page">
  <div class="top"><span class="mark">QM</span><span class="mono mute">{d["top"]} · <a href="{PORTFOLIO}">quentin-michel.netlify.app</a></span></div>
  <div class="cvhead"><div><h1 class="cvname">Quentin Michel</h1><p class="cvrole">{d["role"]}</p>
    <p class="mono mute" style="margin:1.4mm 0 0">{EMAIL} · {LINKEDIN} · {d["place"]}</p></div>
    <img class="portrait" src="../img/portrait.jpg" alt=""></div>
  <div class="stats">{stats}</div>
  <div class="cols">
    <div class="side">
      <section><h2 class="k">{d["h_lang"]}</h2><ul>{langs}</ul></section>
      <section><h2 class="k">{d["h_tools"]}</h2><ul>{tools}</ul></section>
      <section><h2 class="k">{d["h_edu"]}</h2><ul>{edu}</ul></section>
      <section><h2 class="k">{d["h_int"]}</h2><p>{d["interests"]}</p></section>
    </div>
    <div class="main">
      <section><h2 class="k">{d["h_exp"]}</h2>{jobs}</section>
      <section><h2 class="k">{d["h_work"]}</h2>
        <p class="mono mute" style="margin:0 0 1.6mm">{d["w1"]}</p><div class="chips">{nets}</div>
        <p class="mono mute" style="margin:1.8mm 0 1.2mm">{d["w2"]}</p><div class="chips">{cur}{old}</div>
        <p class="mono mute" style="margin:1.8mm 0 1.2mm">{d["w3"]}</p><div class="chips">{wp}</div>
      </section>
    </div>
  </div>
</div>'''


(HERE / "letters.html").write_text(doc("Quentin Michel · Lettre de motivation / Motivatiebrief / Cover letter", "fr", "".join(letter_page(L[k]) for k in ("fr", "nl", "en"))), encoding="utf-8")
(HERE / "cv.html").write_text(doc("Quentin Michel · CV / Résumé", "fr", "".join(cv_page(C[k]) for k in ("fr", "en"))), encoding="utf-8")
print("built")
