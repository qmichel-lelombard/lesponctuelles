// Génère les carrousels Instagram (1080x1400) du quiz Ducobu : node build.mjs
import { chromium } from "/opt/node-tools/node_modules/playwright/index.mjs";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const A = "../../../../quiz-ducobu/assets"; // vu depuis out/<dossier>/html/
const URL_SITE = "duco-bouh.netlify.app";

const css = `
:root{--yellow:#ffd400;--black:#141414;--paper:#fff8dc;--orange:#ff7a00;--purple:#4b1d6b}
*{box-sizing:border-box;margin:0}
html,body{width:1080px;height:1400px;overflow:hidden}
body{position:relative;color:var(--black);font:700 40px/1.3 "Comic Neue","Comic Sans MS",sans-serif;
  background:repeating-linear-gradient(135deg,var(--yellow) 0 40px,var(--black) 40px 80px)}
h1,h2,.k,.chip,.btn,.letter{font-family:"Bangers","Impact",sans-serif;font-weight:400;letter-spacing:.03em}
.top{position:absolute;left:50px;right:50px;top:34px;height:64px;display:flex;justify-content:space-between;align-items:center}
.chip{background:var(--black);color:var(--yellow);font-size:38px;padding:4px 22px;border-radius:14px;border:4px solid var(--orange)}
.chip.o{background:var(--orange);color:var(--black);border-color:var(--black)}
.card{position:absolute;left:50px;right:50px;top:116px;bottom:170px;background:var(--paper);border:8px solid var(--black);
  border-radius:30px;box-shadow:14px 14px 0 var(--black);padding:36px 44px;display:flex;flex-direction:column;align-items:center;text-align:center}
.frise{position:absolute;left:0;bottom:46px;width:1080px;height:auto}
.foot{position:absolute;left:0;right:0;bottom:0;height:46px;background:var(--black);color:var(--yellow);font-size:26px;
  display:flex;align-items:center;justify-content:center;gap:24px}
.k{display:inline-block;background:var(--orange);color:var(--black);font-size:46px;padding:2px 26px;border-radius:999px;transform:rotate(-2deg)}
h1{font-size:150px;line-height:.92;text-shadow:6px 6px 0 var(--yellow)}
h1 em{font-style:normal;color:var(--purple);text-shadow:6px 6px 0 var(--orange)}
h1 small{display:block;font-size:.5em;margin-top:8px}
h2{font-size:64px;line-height:1.08}
.sil{filter:brightness(0) drop-shadow(0 0 0 #000)}
.q{font-size:64px;line-height:1.08;margin:14px 0 20px;text-wrap:balance}
.ans{width:100%;display:grid;gap:16px}
.a{display:flex;align-items:center;gap:22px;text-align:left;background:#fff;border:6px solid var(--black);border-radius:20px;
  padding:10px 24px 10px 14px;box-shadow:6px 6px 0 var(--black);font-size:42px;min-height:98px;line-height:1.12}
.letter{flex:none;width:68px;height:68px;border-radius:50%;background:var(--yellow);border:5px solid var(--black);
  display:grid;place-items:center;font-size:44px}
.btn{display:inline-block;background:var(--orange);border:7px solid var(--black);border-radius:20px;padding:12px 40px;
  font-size:64px;box-shadow:8px 8px 0 var(--black)}
.pill{display:inline-block;background:var(--yellow);border:5px solid var(--black);border-radius:16px;padding:2px 20px;font-size:40px}
.swipe{position:absolute;right:46px;bottom:62px;font-family:"Bangers";font-size:44px;background:var(--black);color:var(--yellow);
  padding:2px 22px;border-radius:999px;border:4px solid var(--orange)}
.sub{font-size:42px;margin:6px 0}
`;

const page = (inner, n, total, { swipe = true } = {}) => `<!doctype html><html lang="fr"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Bangers&family=Comic+Neue:wght@400;700&display=swap" rel="stylesheet">
<style>${css}</style></head><body>
<div class="top"><span class="chip">DUCOBU · TOME 30</span><span class="chip o">${n}/${total}</span></div>
<div class="card">${inner}</div>
<img class="frise" src="${A}/halloween-frise1.png" alt="">
<div class="foot">Ducobu © Zidrou &amp; Godi — Éditions du Lombard</div>
${swipe ? '<div class="swipe">GLISSE ➜</div>' : ""}
</body></html>`;

const L = ["A", "B", "C", "D"];
const question = (num, tot, n, total, q, answers, img, sil = true, imgH = 250) => page(`
  <span class="k">Question ${num}/${tot}</span>
  ${img ? `<img src="${A}/${img}" class="${sil ? "sil" : ""}" style="height:${imgH}px;width:auto;margin-top:14px;max-width:700px;object-fit:contain" alt="">` : ""}
  <h2 class="q">${q}</h2>
  <div class="ans">${answers.map((t, i) => `<div class="a"><span class="letter">${L[i]}</span><span>${t}</span></div>`).join("")}</div>
`, n, total);

// ---------- Carrousel 1 : 10 slides ----------
const T1 = 10;
const set1 = [
  page(`
    <span class="k" style="margin-top:6px">🎃 Spécial Halloween</span>
    <img src="${A}/logo-ducobu.png" style="width:420px;margin:22px 0 6px" alt="Ducobu">
    <h1>Duco… <em>Bouh&nbsp;!</em><small>Le Quiz</small></h1>
    <img src="${A}/couverture-tome-30-v2.jpg" style="height:430px;margin-top:26px;border:6px solid var(--black);border-radius:8px;transform:rotate(-3deg);box-shadow:10px 10px 0 var(--orange)" alt="">
    <p class="sub" style="margin-top:30px">Saint-Potache est hantée.<br>Garderas-tu ton sang-froid&nbsp;?</p>
  `, 1, T1),
  question(1, 7, 2, T1, "Qui est la voisine de classe dont Ducobu adore «&nbsp;s'inspirer&nbsp;» en contrôle&nbsp;?",
    ["Nénèss", "Léonie Gratin", "Rotule", "La directrice"], "leonie.png"),
  question(2, 7, 3, T1, "Comment s'appelle l'école de Ducobu&nbsp;?",
    ["Sainte-Cancre", "Saint-Cartable", "Saint-Potache", "Saint-Zéro-Pointé"], "ducobu-visage.png", false, 300),
  question(3, 7, 4, T1, "Qui est le squelette de la classe, complice de Ducobu&nbsp;?",
    ["Nénèss", "Casper", "Os-car", "Monsieur Tibia"], "neness.png"),
  question(4, 7, 5, T1, "Et comment s'appelle le chien-squelette&nbsp;?",
    ["Fémur", "Médiator", "Toutou-Crâne", "Rotule"], "ducobu-guette.png", false, 290),
  question(5, 7, 6, T1, "Qui est l'instit' à bout de nerfs face aux combines de Ducobu&nbsp;?",
    ["Monsieur Gratin", "Monsieur Latouche", "Monsieur Rotule", "Le père Fouettard"], "latouche.png"),
  question(6, 7, 7, T1, "Dans le tome&nbsp;30, avec quoi Ducobu essaie-t-il de tricher&nbsp;?",
    ["Un parchemin magique", "Une machine à remonter le temps", "Drones, IA et commandes en ligne", "Un perroquet savant"], "ducobu-bonnet.png", false, 290),
  question(7, 7, 8, T1, "Qui a créé Ducobu dans les années&nbsp;1990&nbsp;?",
    ["Godi (dessin) et Zidrou (scénario)", "Uderzo (dessin) et Goscinny (scénario)", "Hergé (dessin) et Jacobs (scénario)", "Peyo (dessin) et Franquin (scénario)"], "ducobu-micro.webp", false, 290),
  page(`
    <span class="k">Les réponses</span>
    <div style="width:100%;display:grid;gap:12px;margin-top:22px;text-align:left;font-size:41px">
      ${[["1", "Léonie Gratin", "B"], ["2", "Saint-Potache", "C"], ["3", "Nénèss", "A"], ["4", "Rotule", "D"], ["5", "Monsieur Latouche", "B"], ["6", "Drones, IA et commandes en ligne", "C"], ["7", "Godi (dessin) et Zidrou (scénario)", "A"]]
        .map(([q, r, l]) => `<div class="a" style="min-height:0;padding:8px 20px 8px 12px;font-size:40px"><span class="letter" style="background:var(--orange);width:56px;height:56px;font-size:38px">${q}</span><span><b style="font-family:Bangers;font-weight:400;color:var(--purple)">${l}.</b> ${r}</span></div>`).join("")}
    </div>
    <div style="margin-top:26px;display:grid;gap:6px;font-size:40px;line-height:1.2">
      <div><b style="font-family:Bangers;font-weight:400;color:var(--purple)">7/7</b> Premier de la classe 🏆</div>
      <div><b style="font-family:Bangers;font-weight:400;color:var(--purple)">4 à 6</b> Élève très honorable 👍</div>
      <div><b style="font-family:Bangers;font-weight:400;color:var(--purple)">0 à 3</b> Champion du zéro pointé 🥚</div>
    </div>
  `, 9, T1),
  page(`
    <span class="k">🎁 Tirage au sort</span>
    <h2 style="margin:14px 0 4px;font-size:120px">Concours</h2>
    <p class="sub" style="font-size:40px">Joue sur le site et tente de gagner<br><span style="color:var(--purple)">le tome&nbsp;30 + le jeu de cartes Ducobu</span></p>
    <img src="${A}/lot-tome30-jeu-v2.png" style="height:430px;margin:10px 0" alt="">
    <span class="btn" style="font-size:54px">🔗 Lien dans la bio</span>
    <p class="sub" style="font-size:36px;margin-top:14px">${URL_SITE}</p>
  `, 10, T1, { swipe: false }),
];

// ---------- Carrousel 2 : 4 slides, sans questions ----------
const T2 = 4;
const set2 = [
  page(`
    <span class="k" style="margin-top:6px">🎃 Spécial Halloween</span>
    <h1 style="margin-top:20px;font-size:132px">Saint-Potache<br>est <em>hantée…</em></h1>
    <img src="${A}/couverture-tome-30-v2.jpg" style="height:560px;margin-top:30px;border:6px solid var(--black);border-radius:8px;transform:rotate(-3deg);box-shadow:10px 10px 0 var(--orange)" alt="">
    <p class="sub" style="margin-top:34px">Ducobu, tome&nbsp;30 : <b style="color:var(--purple)">Duco… Bouh&nbsp;!</b></p>
  `, 1, T2),
  page(`
    <span class="k">Les cartables bougent tout seuls</span>
    <img src="${A}/cartable-vivant.png" style="width:760px;margin:24px 0 10px" alt="">
    <h2 style="font-size:78px;margin:10px 0">Tu connais vraiment<br>Saint-Potache&nbsp;?</h2>
    <div style="display:flex;align-items:flex-end;justify-content:center;gap:26px;margin:14px 0 6px">
      <img src="${A}/leonie.png" style="height:230px" alt=""><img src="${A}/neness.png" style="height:260px" alt=""><img src="${A}/latouche.png" style="height:240px" alt="">
    </div>
    <p class="sub" style="font-size:38px"><span class="pill">⏱️ 5 minutes</span> <span class="pill">❓ 10 questions</span></p>
  `, 2, T2),
  page(`
    <span class="k">🎁 À gagner</span>
    <h2 style="font-size:84px;margin:18px 0 0">Le tome&nbsp;30<br>+ le jeu de cartes</h2>
    <img src="${A}/lot-tome30-jeu-v2.png" style="height:600px;margin:12px 0" alt="">
    <p class="sub" style="font-size:40px">Tirage au sort pour les joueurs<br>inscrits à la newsletter du Lombard</p>
    <p class="sub" style="font-size:34px;opacity:.75">En librairie le 9 octobre</p>
  `, 3, T2),
  page(`
    <span class="k">Prêt(e) à jouer&nbsp;?</span>
    <img src="${A}/ducobu-marche.png" style="height:480px;margin:14px 0 0" alt="">
    <h1 style="font-size:112px;margin-top:12px">Duco… <em>Bouh&nbsp;!</em><small>Le Quiz</small></h1>
    <span class="btn" style="margin-top:26px">🔗 Lien dans la bio</span>
    <p class="sub" style="font-size:36px;margin-top:16px">${URL_SITE}</p>
    <p class="sub" style="font-size:30px;opacity:.75;margin-top:2px">Conseil de Latouche : ne copie pas. Conseil de Ducobu : si.</p>
  `, 4, T2, { swipe: false }),
];

const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium", args: ["--no-sandbox"] });
const ctx = await browser.newContext({ viewport: { width: 1080, height: 1400 }, deviceScaleFactor: 1 });
for (const [dir, slides] of [["carrousel-10-slides", set1], ["carrousel-4-slides", set2]]) {
  const htmlDir = path.join(here, "out", dir, "html");
  fs.rmSync(path.join(here, "out", dir), { recursive: true, force: true });
  fs.mkdirSync(htmlDir, { recursive: true });
  for (const [i, html] of slides.entries()) {
    const nn = String(i + 1).padStart(2, "0");
    const f = path.join(htmlDir, `slide-${nn}.html`);
    fs.writeFileSync(f, html);
    const p = await ctx.newPage();
    await p.goto("file://" + f, { waitUntil: "networkidle" });
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: path.join(here, "out", dir, `slide-${nn}.png`) });
    await p.close();
  }
}
await browser.close();
