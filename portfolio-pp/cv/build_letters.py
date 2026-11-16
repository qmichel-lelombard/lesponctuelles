#!/usr/bin/env python3
"""Builds letters.html: Quentin's cover letter for Poils & Plumes, one A4 page per language (FR, NL, EN)."""
import pathlib
HERE = pathlib.Path(__file__).parent
EMAIL, LINKEDIN = "quentin.michel@outlook.com", "linkedin.com/in/quentin-michel"
ADDRESS, PHONE = "Chaussée d'Ath 208a, 7850 Enghien", "+32 494 58 18 99"
PAW = '<svg class="paw" viewBox="0 0 24 24"><ellipse cx="4.6" cy="10.4" rx="2.2" ry="3"/><ellipse cx="9.2" cy="5.4" rx="2.2" ry="3"/><ellipse cx="14.8" cy="5.4" rx="2.2" ry="3"/><ellipse cx="19.4" cy="10.4" rx="2.2" ry="3"/><path d="M12 11c-3.5 0-6.5 3.2-6.5 6.3 0 2.2 1.8 3.2 3.6 3.2 1.2 0 1.9-.5 2.9-.5s1.7.5 2.9.5c1.8 0 3.6-1 3.6-3.2C18.5 14.2 15.5 11 12 11z"/></svg>'
CSS = """
@page { size: A4; margin: 0; }
:root { --bg:#FAF5FC; --surface:#F1E6F6; --card:#FFFFFF; --ink:#2B1038; --mute:#6D5A7A; --line:rgba(102,36,131,.2); --brand:#662483; --accent:#951272; --fs: 9.6pt; }
* { box-sizing: border-box; }
html, body { margin: 0; background: var(--bg); color: var(--ink); }
body { font: 400 var(--fs)/1.5 "Nunito", "Trebuchet MS", Arial, sans-serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 210mm; height: 297mm; padding: 12mm 16mm 11mm; position: relative; overflow: hidden; page-break-after: always; display: flex; flex-direction: column; }
.page:last-child { page-break-after: auto; }
.label { font-weight: 800; font-size: 6.8pt; letter-spacing: .09em; text-transform: uppercase; }
.mute { color: var(--mute); }
.paw { width: 1em; height: 1em; fill: currentColor; flex: none; }
.blob { position: absolute; top: -22mm; right: -26mm; width: 110mm; height: 100mm; background: var(--surface); border-radius: 58% 42% 47% 53% / 46% 55% 45% 54%; }
.page > :not(.blob) { position: relative; }
.head { display: flex; justify-content: space-between; align-items: flex-start; gap: 8mm; }
.name { margin: 0; font: 800 44pt/.8 "Baloo 2", sans-serif; letter-spacing: -.02em; }
.name span { display: block; }
.name .first { color: var(--brand); }
.photo { width: 30mm; height: 30mm; object-fit: cover; border: 1.2mm solid var(--card); border-radius: 44% 56% 52% 48% / 55% 44% 56% 45%; box-shadow: 0 2mm 6mm rgba(43,16,56,.16); flex: none; }
.coords { margin: 3.5mm 0 0; font-weight: 700; font-size: 9pt; line-height: 1.45; }
.to { width: 78mm; flex: none; }
.date { margin: 3mm 0 0; text-align: right; font-weight: 700; font-size: 9pt; }
.close { display: flex; flex-direction: column; align-items: flex-end; margin-top: 1mm; }
.close .photo { margin-top: 3mm; }
.close p { margin: 0 !important; text-align: right; }
.meta { display: grid; gap: 2.4mm; padding: 4mm 5mm; background: var(--card); border: .25mm solid var(--line); border-radius: 5mm; }
.meta p { margin: 0; }
.meta b { display: block; font-weight: 800; font-size: 8.6pt; letter-spacing: 0; text-transform: none; color: var(--ink); margin-top: .4mm; }
.body { margin-top: 7mm; flex: 1; min-height: 0; }
.body p { margin: 0 0 2.5mm; text-align: left; }
.body .hello { font: 700 14pt/1.1 "Baloo 2", sans-serif; color: var(--brand); margin-bottom: 2.5mm; }
.sig { margin-top: 2mm !important; text-align: right !important; font: 800 15pt/1 "Baloo 2", sans-serif; color: var(--brand); }
.foot { display: flex; justify-content: space-between; align-items: center; gap: 6mm; border-top: .25mm solid var(--line); padding-top: 2.6mm; margin-top: 2mm; }
"""
L = {
"fr": dict(tag="Candidature · Marketing &amp; Business Support Manager", k_to="À l'attention de", to="Felix Delva, Business Lead · Poils &amp; Plumes", k_date="Date", date="Enghien, le 16 novembre 2026", k_obj="Objet", obj="Marketing &amp; Business Support Manager",
  hello="Cher Monsieur Delva,", place="Enghien, Belgique", bye="Sincères salutations,", p=[
  "Je vous propose ma candidature au poste de Marketing &amp; Business Support Manager : votre offre semble en effet avoir été rédigée à mon attention. Un couteau suisse du web marketing et de la communication digitale, c'est ce que je suis ! C'était d'ailleurs déjà l'expression utilisée dans la description de ma fonction actuelle lors de mon embauche.",
  "Je suis actuellement Digital Marketing Manager au sein des Éditions du Lombard (bande dessinée). Il s'agit d'une fonction passionnante et variée dans un milieu culturel qui l'est tout autant. Cependant, je suis aujourd'hui à la recherche d'un nouveau défi, particulièrement pour pouvoir exploiter la puissance nouvelle des outils IA.",
  "L'intelligence artificielle, surtout générative, est en effet un sujet très sensible dans l'édition, principalement par rapport aux droits d'auteur et au vol de propriété intellectuelle. Cela dit, dans le cadre de ma fonction, j'ai pu pleinement tester les possibilités de ces nouveaux outils (Claude Code mais aussi Copilot, ChatGPT, etc.).",
  "De fait, voilà déjà quelques mois que la plupart des tâches qui m'incombent sont désormais réalisées par IA : encodage des actualités, événements et citations sur le site, création de vidéos ou de carrousels photos pour les réseaux sociaux, montage d'interviews ou de trailers vidéo, mise en page de PowerPoint et PDF, conception de sites web complets, etc. Je connais et maîtrise aussi la génération d'images, de vidéos et de 3D assistée par IA (ou non assistée d'ailleurs : suite Adobe maîtrisée à 100 %).",
  "De 2016 à 2021, j'ai également occupé une fonction très similaire au poste proposé ici, puisque j'étais Web Marketeer au sein du groupe Meno, une coopérative de magasins indépendants (quincaillerie) dont le siège se trouve à Nivelles mais les adhérents répartis sur toute la Belgique, et dans les deux langues nationales. Dans ce contexte, j'ai pu évoluer durant cinq ans dans un environnement totalement bilingue et appréhender les nombreux défis auxquels sont confrontés les magasins indépendants.",
  "Mes précédentes expériences en gestion de projets et en agence de communication m'ont également appris à consolider un budget et tenir un planning, à faire preuve de pragmatisme et d'un grand esprit d'initiative, mais aussi à travailler en équipe. Les réseaux sociaux et les campagnes digitales n'ont aucun secret pour moi : je maîtrise Meta Ads, TikTok, Snapchat, YouTube, Google Ads, GA4… et tous les outils inhérents.",
  "Naturellement, si votre offre m'intéresse, c'est avant tout car je suis un grand ami des animaux, qu'ils soient à poils ou à plumes. Même si j'avoue avoir une légère préférence pour les premiers : j'ai en effet toujours vécu avec des chiens et des chats. Je suis marié et j'ai une petite fille de 6 ans. Notre foyer compte pour l'instant un Berger Blanc Suisse de quatre ans prénommé Virgile et un chat qui vient de fêter ses dix ans, prénommé – entre autres surnoms – Cléo. Nul doute qu'ils seraient tous deux très heureux de cette opportunité chez Poils &amp; Plumes !",
  "Je vous remercie pour votre attention et je serais bien sûr ravi de vous rencontrer lors d'un entretien ultérieur."]),
"nl": dict(addr="Aatsesteenweg 208a, 7850 Edingen", tag="Sollicitatie · Marketing &amp; Business Support Manager", k_to="Ter attentie van", to="Felix Delva, Business Lead · Poils &amp; Plumes", k_date="Datum", date="Edingen, 16 november 2026", k_obj="Betreft", obj="Marketing &amp; Business Support Manager",
  hello="Beste meneer Delva,", place="Edingen, België", bye="Met vriendelijke groeten,", p=[
  "Graag stel ik me kandidaat voor de functie van Marketing &amp; Business Support Manager: uw vacature lijkt wel voor mij geschreven. Een Zwitsers zakmes van webmarketing en digitale communicatie, dat ben ik! Die uitdrukking stond trouwens al in de omschrijving van mijn huidige functie toen ik werd aangeworven.",
  "Momenteel ben ik Digital Marketing Manager bij Éditions du Lombard (stripverhalen). Het is een boeiende en afwisselende functie in een culturele sector die dat evenzeer is. Toch ben ik vandaag op zoek naar een nieuwe uitdaging, vooral om de nieuwe kracht van AI-tools ten volle te kunnen benutten.",
  "Artificiële intelligentie, vooral generatieve, ligt in de uitgeverswereld immers erg gevoelig, voornamelijk vanwege het auteursrecht en de diefstal van intellectuele eigendom. In mijn functie heb ik de mogelijkheden van deze nieuwe tools wel uitgebreid kunnen testen (Claude Code, maar ook Copilot, ChatGPT enz.).",
  "Sinds enkele maanden voer ik de meeste van mijn taken dan ook uit met AI: invoeren van nieuws, evenementen en citaten op de website, video's of fotocarrousels maken voor sociale media, interviews of videotrailers monteren, PowerPoints en pdf's opmaken, volledige websites bouwen enz. Ik ken en beheers ook het genereren van beelden, video's en 3D met AI (of zonder, trouwens: de Adobe-suite beheers ik voor 100 %).",
  "Van 2016 tot 2021 had ik bovendien een functie die sterk lijkt op deze vacature: ik was Web Marketeer bij de Meno-groep, een coöperatie van zelfstandige winkels (ijzerwaren) met hoofdzetel in Nijvel, maar met leden verspreid over heel België en in de twee landstalen. Daar heb ik vijf jaar in een volledig tweetalige omgeving gewerkt en de vele uitdagingen van zelfstandige winkels leren kennen.",
  "Mijn eerdere ervaringen in projectbeheer en in een communicatiebureau hebben me ook geleerd een budget te bewaken en een planning te halen, pragmatisch te zijn en veel initiatief te tonen, maar ook in team te werken. Sociale media en digitale campagnes hebben voor mij geen geheimen: ik beheers Meta Ads, TikTok, Snapchat, YouTube, Google Ads, GA4… en alle bijbehorende tools.",
  "Uw vacature spreekt me natuurlijk vooral aan omdat ik een grote dierenvriend ben, met haren of met pluimen. Al geef ik toe dat ik een lichte voorkeur heb voor de eerste: ik heb altijd met honden en katten samengeleefd. Ik ben getrouwd en heb een dochtertje van 6 jaar. Ons gezin telt momenteel een Zwitserse Witte Herder van vier jaar die Virgile heet, en een kat die net tien is geworden en – naast andere bijnamen – Cléo heet. Ze zouden allebei ongetwijfeld erg blij zijn met deze kans bij Poils &amp; Plumes!",
  "Ik dank u voor uw aandacht en ontmoet u uiteraard graag tijdens een gesprek."]),
"en": dict(tag="Application · Marketing &amp; Business Support Manager", k_to="For the attention of", to="Felix Delva, Business Lead · Poils &amp; Plumes", k_date="Date", date="Enghien, 16 November 2026", k_obj="Subject", obj="Marketing &amp; Business Support Manager",
  hello="Dear Mr Delva,", place="Enghien, Belgium", bye="Kind regards,", p=[
  "I would like to apply for the position of Marketing &amp; Business Support Manager: your posting really does seem to have been written for me. A Swiss army knife of web marketing and digital communication, that is what I am! It was, in fact, already the expression used in the description of my current role when I was hired.",
  "I am currently Digital Marketing Manager at Éditions du Lombard (comics). It is an exciting and varied role in a cultural sector that is just as much so. However, I am now looking for a new challenge, particularly to be able to harness the new power of AI tools.",
  "Artificial intelligence, especially generative AI, is indeed a very sensitive subject in publishing, mainly because of copyright and the theft of intellectual property. That said, in my role I have been able to fully test what these new tools can do (Claude Code, but also Copilot, ChatGPT, etc.).",
  "In fact, for several months now, most of the tasks I am responsible for have been done with AI: entering news, events and quotes on the website, creating videos or photo carousels for social media, editing interviews or video trailers, laying out PowerPoints and PDFs, building complete websites, etc. I also know and master AI-assisted generation of images, videos and 3D (or unassisted, for that matter: 100% command of the Adobe suite).",
  "From 2016 to 2021, I also held a role very similar to the one offered here, as Web Marketeer at the Meno group, a cooperative of independent stores (hardware) headquartered in Nivelles, with members spread all over Belgium and in both national languages. There, I worked for five years in a fully bilingual environment and came to understand the many challenges independent stores face.",
  "My earlier experience in project management and in a communication agency also taught me to manage a budget and keep to a schedule, to be pragmatic and show a great deal of initiative, and to work in a team. Social media and digital campaigns hold no secrets for me: I master Meta Ads, TikTok, Snapchat, YouTube, Google Ads, GA4… and all the related tools.",
  "Naturally, if your posting appeals to me, it is above all because I am a great friend of animals, whether furry or feathered. Although I admit to a slight preference for the first: I have always lived with dogs and cats. I am married and have a 6-year-old daughter. Our household currently includes a four-year-old White Swiss Shepherd named Virgile and a cat who has just turned ten, named – among other nicknames – Cléo. No doubt both of them would be very happy about this opportunity at Poils &amp; Plumes!",
  "Thank you for your attention. I would of course be delighted to meet you for an interview."]),
}
def page(lang, d):
    paras = "".join(f"<p>{x}</p>" for x in d["p"])
    return f'''<div class="page" lang="{lang}">
  <div class="blob"></div>
  <div class="head">
    <div class="me"><h1 class="name"><span class="first">Quentin</span><span>Michel</span></h1>
      <p class="coords">{d.get("addr", ADDRESS)}<br>{PHONE}<br>{EMAIL}</p></div>
    <div class="to"><div class="meta"><p class="label mute">{d["k_to"]}<b>Felix Delva, Business Lead<br>Poils &amp; Plumes srl<br>Avenue Edison 8, 1300 Wavre</b></p><p class="label mute">{d["k_obj"]}<b>{d["obj"]}</b></p></div>
      <p class="date">{d["date"]}</p></div>
  </div>
  <div class="body"><p class="hello">{d["hello"]}</p>{paras}<div class="close"><p>{d["bye"]}</p><p class="sig">Quentin Michel</p><img class="photo" src="../img/duo.jpg" alt=""></div></div>
</div>'''
html = f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Quentin Michel · Lettre de motivation Poils &amp; Plumes</title><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&family=Nunito:wght@400;600;700;800&display=swap"><style>{CSS}</style></head><body>{"".join(page(k, L[k]) for k in ("fr","nl","en"))}</body></html>'
(HERE / "letters.html").write_text(html, encoding="utf-8")
print("built")
