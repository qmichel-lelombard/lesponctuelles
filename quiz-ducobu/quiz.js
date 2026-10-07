// Quiz Ducobu — Duco… Bouh ! (tome 30)
// Pour ajouter des visuels détourés : déposer les fichiers dans assets/ et renseigner "img" ci-dessous.
const MASCOT = {
  think: "assets/ducobu-visage.png",
  good: "assets/ducobu-marche.png",
  bad: "assets/ducobu-bonnet.png"
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
    a: ["Des objets bougent tout seuls et les cartables prennent vie", "L'école est inondée de bonbons", "Latouche devient invisible", "Toute la classe part en vacances"], c: 0,
    ok: "Brrr ! Dans ce tome, l'ambiance est sinistre : ton cartable pourrait bien te regarder de travers.",
    ko: "Pas du tout : les objets bougent tout seuls et les cartables prennent vie. Ça donne la chair de poule." },
  { q: "Quel est le gros point commun entre le tome 30 et la couverture ?",
    a: ["Halloween, avec une citrouille", "La plage et un parasol", "Noël et un sapin", "Un tournoi de foot"], c: 0,
    ok: "Exactement : Halloween ! Prépare tes bonbons… et planque ton cahier de brouillon.",
    ko: "C'est Halloween ! Regarde bien la couverture : il y a une citrouille." },
  { q: "Qui a créé Ducobu dans les années 1990 ?",
    a: ["Godi (dessin) et Zidrou (scénario)", "Uderzo et Goscinny", "Hergé et Jacobs", "Peyo et Franquin"], c: 0,
    ok: "Godi et Zidrou : le duo qui fait rire Saint-Potache depuis plus de 30 ans.",
    ko: "Ce sont Godi (dessin) et Zidrou (scénario) ! Les autres, c'est une autre classe." },
  { q: "Dernière question : pour réussir un contrôle, la meilleure méthode est…",
    a: ["Réviser !", "Copier sur Léonie", "Demander à Rotule", "Corrompre Nénèss avec un os"], c: 0,
    ok: "Réviser ! Latouche est fier de toi. Ducobu, lui, fait semblant de ne pas avoir entendu.",
    ko: "Réviser, bien sûr ! Mais dans la BD, on te laisse rigoler des autres méthodes." }
];

const PROFILES = [
  { min: 9, title: "Premier de la classe ! 🏆",
    text: "Même Léonie est impressionnée. Tu connais Saint-Potache comme ta poche (et ton cartable). Va vite lire le tome 30 !" },
  { min: 6, title: "Élève très honorable 👍",
    text: "Latouche te met un bon point. Avec le tome 30, tu seras imbattable sur Ducobu." },
  { min: 3, title: "Cancre en progrès ✏️",
    text: "Pas mal ! Ducobu te félicite : tu as sûrement un peu triché… mais lui, il ne dira rien. Relis les albums pour t'améliorer." },
  { min: 0, title: "Champion du zéro pointé 🥚",
    text: "Ducobu te salue : il t'accepte dans son club ! Rejoue, ou lis le tome 30 pour réviser." }
];

const $ = id => document.getElementById(id);
let i = 0, score = 0, locked = false;

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
  if (locked) return;
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
  const m = $("mascot"), fallback = right ? MASCOT.good : MASCOT.bad;
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
  $("result-text").textContent = p.text;
  setImg($("result-img"), p.img);
  show("screen-result");
}

$("start").onclick = () => { i = 0; score = 0; show("screen-quiz"); render(); };
$("next").onclick = () => { i++; i < QUESTIONS.length ? render() : finish(); };
$("again").onclick = () => { i = 0; score = 0; show("screen-quiz"); render(); };
$("share").onclick = async () => {
  const text = `J'ai fait ${score}/10 au quiz Duco… Bouh ! Et toi, tu fais mieux que moi ?`;
  try {
    if (navigator.share) await navigator.share({ title: "Duco… Bouh ! Le Quiz", text, url: location.href });
    else { await navigator.clipboard.writeText(text + " " + location.href); $("share").textContent = "Lien copié ✔"; }
  } catch (e) {}
};
