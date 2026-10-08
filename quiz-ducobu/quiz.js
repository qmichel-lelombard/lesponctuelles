// Quiz Ducobu — Duco… Bouh ! (tome 30)
// Pour ajouter des visuels détourés : déposer les fichiers dans assets/ et renseigner "img" ci-dessous.
const MASCOT = {
  think: "assets/ducobu-visage.png",
  good: "assets/ducobu-marche.png",
  bad: ["assets/ducobu-bonnet.png", "assets/ducobu-zero-rond.webp"]
};

const QUESTIONS = [
  { q: "Qui est la voisine de classe de Ducobu… celle dont il adore « s'inspirer » pendant les contrôles ?",
    img: "assets/leonie.png", a: ["Léonie Gratin", "Nénèss", "Rotule", "La directrice"], c: 0,
    ok: "Bravo ! Léonie, la première de la classe, aimerait bien qu'on arrête de lui regarder par-dessus l'épaule.",
    ko: "Raté ! C'est Léonie Gratin, la première de la classe. Ducobu a toujours un œil sur sa copie." },
  { q: "Comment s'appelle l'école où se passent toutes les aventures de Ducobu ?",
    a: ["Saint-Potache", "Sainte-Cancre", "Saint-Cartable", "Saint-Zéro-Pointé"], c: 0,
    ok: "Exact : Saint-Potache ! Une école où, ce coup-ci, il se passe de drôles de choses…",
    ko: "Non, c'est Saint-Potache. (Saint-Zéro-Pointé, c'est le nom de ses bulletins.)" },
  { q: "Qui est le squelette qui sert de « matériel pédagogique » en classe… et de complice à Ducobu ?",
    img: "assets/neness.png", a: ["Nénèss", "Casper", "Os-car", "Monsieur Tibia"], c: 0,
    ok: "Nénèss ! Il n'a plus que les os, mais il a toujours un bon conseil à glisser.",
    ko: "C'était Nénèss ! Un squelette, c'est le meilleur des complices : il ne balance jamais." },
  { q: "Et comment s'appelle le chien-squelette de Nénèss ?",
    a: ["Rotule", "Fémur", "Médiator", "Toutou-Crâne"], c: 0,
    ok: "Rotule ! Il court toujours après son os. Enfin… après un os.",
    ko: "Rotule ! (Fémur, c'est un os, pas un chien. Quoique.)" },
  { q: "Qui est l'instit' qui n'en peut plus de Ducobu et de ses combines ?",
    img: "assets/latouche.png", a: ["Monsieur Latouche", "Monsieur Gratin", "Monsieur Rotule", "Le père Fouettard"], c: 0,
    ok: "Latouche, fidèle aux « bonnes vieilles méthodes »… qui ne marchent jamais sur Ducobu.",
    ko: "C'est Monsieur Latouche, grand fan des bonnes vieilles méthodes. Ducobu, lui, préfère les nouvelles." },
  { q: "Dans le tome 30, avec quoi Ducobu essaie-t-il de tricher ?",
    a: ["Drones, IA et commandes en ligne", "Un parchemin magique", "Une machine à remonter le temps", "Un perroquet savant"], c: 0,
    ok: "Oui ! Trente albums plus tard, Ducobu est toujours dans l'air du temps. Pour tricher, du moins.",
    ko: "C'était : drones, IA et commandes en ligne ! Ducobu a compris que la triche, ça se modernise." },
  { q: "Que se passe-t-il à Saint-Potache dans Duco… Bouh ! ?",
    img: "assets/cartable-vivant.png", a: ["Des objets bougent tout seuls et les cartables prennent vie", "L'école est inondée de bonbons", "Latouche devient invisible", "Toute la classe part en vacances"], c: 0,
    ok: "Brrr ! Dans ce tome, plus rien n'est à sa place : ton cartable pourrait bien te regarder de travers.",
    ko: "Pas du tout : les objets bougent tout seuls et les cartables prennent vie. Ça donne la chair de poule." },
  { q: "Qu'est-ce qui fait peur à Ducobu et Léonie sur la couverture de Duco… Bouh ! ?",
    a: ["Une énorme citrouille aux yeux jaunes", "Un requin dans la classe", "Un père Noël en colère", "Un ballon de foot géant"], c: 0,
    ok: "Exactement : une citrouille géante, parfaite pour Halloween ! Prépare tes bonbons… et planque ton cahier de brouillon.",
    ko: "C'est une énorme citrouille aux yeux jaunes ! Regarde bien la couverture : Ducobu et Léonie n'en mènent pas large." },
  { q: "Qui a créé Ducobu dans les années 1990 ?",
    a: ["Godi (dessin) et Zidrou (scénario)", "Uderzo (dessin) et Goscinny (scénario)", "Hergé (dessin) et Jacobs (scénario)", "Peyo (dessin) et Franquin (scénario)"], c: 0,
    ok: "Godi (dessin) et Zidrou (scénario) : le duo qui fait rire Saint-Potache depuis plus de 30 ans.",
    ko: "Ce sont Godi (dessin) et Zidrou (scénario) ! Les autres, c'est une autre classe." },
  { q: "Dernière question : pour réussir un contrôle, la meilleure méthode est…",
    img: "assets/ducobu-guette.png", a: ["Réviser !", "Copier sur Léonie", "Demander à Rotule", "Corrompre Nénèss avec un os"], c: 0,
    ok: "Réviser ! Latouche est fier de toi. Ducobu, lui, fait semblant de ne pas avoir entendu.",
    ko: "Réviser, bien sûr ! Mais dans la BD, on te laisse rigoler des autres méthodes." }
];

const PROFILES = [
  { min: 10, title: "10/10 : sans-faute, bravo ! 🏆", img: "assets/leonie-dix-sur-dix.png",
    text: "Sans-faute ! Même Léonie n'aurait pas fait mieux, et tu n'as pas triché (on a vérifié). Direction le tome 30 !" },
  { min: 8, title: "Premier de la classe ! 🏆", img: "assets/leonie-livres.png",
    text: "Même Léonie est impressionnée. Tu connais Saint-Potache comme ta poche (et ton cartable). Va vite lire le tome 30 !" },
  { min: 6, title: "Élève très honorable 👍", img: "assets/leonie-ducobu-tableau.png",
    text: "Latouche te met un bon point. Avec le tome 30, tu seras imbattable sur Ducobu." },
  { min: 3, title: "Cancre en progrès ✏️", img: "assets/ducobu-zero-copies2.png",
    text: "Pas mal ! Ducobu te félicite : tu as sûrement un peu triché… mais lui, il ne dira rien. Relis les albums pour t'améliorer." },
  { min: 0, title: "Champion du zéro pointé 🥚", img: "assets/ducobu-zero-copies.png",
    text: "Ducobu te salue : il t'accepte dans son club ! Rejoue, ou lis le tome 30 pour réviser." }
];

// Tirage au sort : formulaire Brevo (champs PRENOM et EMAIL). Si "endpoint" est vide, le formulaire
// fonctionne en mode test : rien n'est envoyé ni enregistré.
const NEWSLETTER = {
  endpoint: "https://8e4b1da6.sibforms.com/serve/MUIFAOMBy3DAP--3s4Ag8X8qx6kSGQLNkrJ4_MKVGeY0wJIyP1k8hK-lwk_ECTseSw_uWYk82wZncZGTAywxBjk_lco_t9Xw6lho7AkyzE9IyuiNY2CBoY2lGodugv8RhWPFwlpdVda2Cvegs5ZUAdrocZN8l-m0RaaEvnducdyRaculbN3aDywXpzuRTko7oK18k5HU3gZMZl0=",
  reglementUrl: ""   // lien vers le règlement officiel du tirage au sort
};

const $ = id => document.getElementById(id);
let i = 0, score = 0, locked = false, readyAt = 0;

function show(id){
  document.querySelectorAll(".screen").forEach(s => s.classList.remove("active"));
  $(id).classList.add("active");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function setImg(el, src){
  if (src){ el.style.display = ""; el.src = src; } else { el.removeAttribute("src"); el.style.display = "none"; }
}

function shuffle(a){
  for (let k = a.length - 1; k > 0; k--){ const j = Math.floor(Math.random() * (k + 1)); [a[k], a[j]] = [a[j], a[k]]; }
  return a;
}

function render(){
  const Q = QUESTIONS[i];
  locked = false;
  readyAt = Date.now() + 600; // évite qu'un double-tap sur « Suivant » valide une réponse sans le vouloir
  $("num").textContent = i + 1;
  $("total").textContent = QUESTIONS.length;
  $("score").textContent = score;
  $("bar").style.width = (i / QUESTIONS.length * 100) + "%";
  $("question").textContent = Q.q;
  setImg($("mascot"), MASCOT.think);
  $("mascot").classList.remove("hop");
  $("feedback").hidden = true;
  const box = $("answers");
  box.innerHTML = "";
  const order = shuffle(Q.a.map((t, idx) => ({ t, idx })));
  order.forEach(o => {
    const b = document.createElement("button");
    b.className = "answer";
    b.textContent = o.t;
    b.onclick = () => pick(b, o.idx);
    b.dataset.idx = o.idx;
    box.appendChild(b);
  });
}

function pick(btn, idx){
  if (locked || Date.now() < readyAt) return;
  locked = true;
  const Q = QUESTIONS[i];
  const right = idx === Q.c;
  if (right) score++;
  $("score").textContent = score;
  btn.classList.add(right ? "good" : "bad");
  document.querySelectorAll(".answer").forEach(b => {
    b.disabled = true;
    if (+b.dataset.idx === Q.c) b.classList.add("good");
  });
  $("feedback-text").textContent = (right ? "✅ " : "❌ ") + (right ? Q.ok : Q.ko);
  $("next").textContent = i === QUESTIONS.length - 1 ? "Mon bulletin ➜" : "Suivant ➜";
  // le personnage de la question est dévoilé après la réponse
  const m = $("mascot"), fallback = right ? MASCOT.good : MASCOT.bad[Math.floor(Math.random() * MASCOT.bad.length)];
  m.onerror = () => { m.onerror = null; m.src = fallback; };
  setImg(m, Q.img || fallback);
  $("mascot").classList.toggle("hop", right);
  $("feedback").hidden = false;
  $("next").focus();
}

function finish(){
  const p = PROFILES.find(p => score >= p.min);
  $("bar").style.width = "100%";
  $("result-title").textContent = p.title;
  $("result-score").textContent = score;
  $("result-count").textContent = score > 1 ? "bonnes réponses" : "bonne réponse";
  $("result-text").textContent = p.text;
  setImg($("result-img"), p.img);
  show("screen-result");
}

$("start").onclick = () => { i = 0; score = 0; show("screen-quiz"); render(); };
$("next").onclick = () => { if ($("feedback").hidden) return; i++; i < QUESTIONS.length ? render() : finish(); };
$("again").onclick = () => { i = 0; score = 0; show("screen-quiz"); render(); };
$("share").onclick = async () => {
  const text = `J'ai fait ${score}/10 au quiz Duco… Bouh ! Et toi, tu fais mieux que moi ?`;
  try {
    if (navigator.share) await navigator.share({ title: "Duco… Bouh ! Le Quiz", text, url: location.href });
    else { await navigator.clipboard.writeText(text + " " + location.href); $("share").textContent = "Lien copié ✔"; }
  } catch (e) {}
};

// ---- Inscription newsletter / tirage au sort ----
(function () {
  const form = $("draw-form");
  if (!form) return;
  const link = $("reglement-link");
  if (NEWSLETTER.reglementUrl) link.href = NEWSLETTER.reglementUrl;
  else link.addEventListener("click", e => e.preventDefault());

  const err = msg => { $("draw-error").textContent = msg; $("draw-error").hidden = !msg; };

  form.addEventListener("submit", async e => {
    e.preventDefault();
    err("");
    const prenom = form.prenom.value.trim();
    const email = form.email.value.trim();
    if (form.site.value) return;                       // champ piège pour les robots
    if (!prenom) return err("Écris ton prénom pour participer.");
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]{2,}$/.test(email)) return err("Vérifie ton adresse e-mail.");
    if (!form.consent.checked) return err("Coche la case pour accepter la newsletter et le règlement.");

    const data = new FormData();
    data.append("PRENOM", prenom);
    data.append("EMAIL", email);
    data.append("email_address_check", "");            // champ anti-robot attendu par Brevo
    data.append("locale", "fr");
    const btn = $("draw-submit");
    btn.disabled = true;
    try {
      if (NEWSLETTER.endpoint) {
        const res = await fetch(NEWSLETTER.endpoint, { method: "POST", body: data, headers: { Accept: "application/json" } });
        let body = null;
        try { body = await res.json(); } catch (x) {}
        if (!res.ok || (body && body.success === false)) throw new Error("brevo");
      } else {
        $("draw-done-text").textContent = "Mode test : ton inscription n'a pas été enregistrée.";
      }
      form.hidden = true;
      $("draw-done").hidden = false;
    } catch (x) {
      err("Oups, l'inscription n'a pas fonctionné. Vérifie ton e-mail ou réessaie dans un instant.");
      btn.disabled = false;
    }
  });

  // Rejouer : on réaffiche le formulaire
  $("again").addEventListener("click", () => { form.hidden = false; $("draw-done").hidden = true; $("draw-submit").disabled = false; });
})();

// Aperçu : ouvrir la page avec #tirage affiche directement l'écran de résultat et le formulaire (score fictif de 8/10).
if (location.hash === "#tirage") {
  score = 8;
  finish();
  setTimeout(() => $("draw").scrollIntoView({ behavior: "auto", block: "start" }), 150);
}
