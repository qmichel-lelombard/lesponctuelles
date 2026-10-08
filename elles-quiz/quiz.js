/* ELLES – Quelle Elle se cache en toi ?  (vanilla JS, aucune dépendance) */
(() => {
  "use strict";

  const BOOK_URL = "https://www.lelombard.com/bd/elles/intemporelles";

  /* ------------------------------------------------------------------ *
   *  Les six personnalités
   * ------------------------------------------------------------------ */
  const ELLES = {
    rose: {
      name: "Rose", color: "#ff4f93", img: "img/rose.webp",
      tag: "Le cœur de la bande, l'équilibre en couleurs !",
      desc: "Tu es la personnalité de base : celle qui relie toutes les autres. Curieuse, à l'écoute et pleine de bonne humeur, tu t'adaptes à presque toutes les situations. Quand ça part dans tous les sens, c'est souvent toi qui ramènes le calme (et le sourire).",
      strengths: ["Une empathie XXL", "Tu trouves toujours le juste milieu", "Tu fais du bien aux gens autour de toi"],
      flaws: ["Tu t'oublies pour les autres", "Tu as du mal à choisir quand tout te tente"],
      mantra: "Ensemble, c'est toujours mieux.",
      ally: "bleue"
    },
    blonde: {
      name: "Blonde", color: "#ffae2b", img: "img/blonde.webp",
      tag: "Prête à en découdre, toujours en première ligne !",
      desc: "Courage, énergie et grand cœur : tu fonces d'abord et tu réfléchis après (parfois beaucoup après). Quand quelqu'un que tu aimes est en danger, tu deviens un vrai volcan. Avec toi, aucune bataille n'est perdue d'avance !",
      strengths: ["Un courage à toute épreuve", "Tu défends les tiens coûte que coûte", "Une énergie contagieuse"],
      flaws: ["Tu t'énerves plus vite que ton ombre", "Le mot « prudence » ne fait pas partie de ton vocabulaire"],
      mantra: "Qui m'aime me suive… et je passe devant !",
      ally: "verte"
    },
    brune: {
      name: "Brune", color: "#c0764a", img: "img/brune.webp",
      tag: "Prudente, sensible et incroyablement lucide.",
      desc: "Tu as toujours un temps d'avance : tu sens les dangers avant tout le monde, et tu n'oublies jamais ton plan B. Derrière ta prudence se cache une grande sensibilité et une loyauté à toute épreuve. Si tu dis « fais attention », mieux vaut t'écouter !",
      strengths: ["Un sixième sens pour les problèmes", "Une loyauté en béton", "Tu ne laisses rien au hasard"],
      flaws: ["Tu imagines toujours le pire scénario", "Tu as du mal à lâcher prise"],
      mantra: "Et si… ? Vérifions encore une fois.",
      ally: "violette"
    },
    violette: {
      name: "Violette", color: "#a86bff", img: "img/violette.webp",
      tag: "Le feu d'artifice de la bande !",
      desc: "Rire, blagues, grimaces et fous rires : tu transformes n'importe quel moment gris en soirée de fête. Les gens adorent ta bonne humeur, ton énergie et ton sens de l'autodérision. Ta mission : que personne ne s'ennuie jamais.",
      strengths: ["L'humour à toute heure", "Tu dédramatises tout", "Tu rassembles les gens"],
      flaws: ["Tu fais une blague quand il faudrait parler sérieusement", "Tu as parfois du mal à rester en place"],
      mantra: "La vie est trop courte pour ne pas rigoler !",
      ally: "brune"
    },
    verte: {
      name: "Verte", color: "#2fc474", img: "img/verte.webp",
      tag: "Discrète en surface, immense à l'intérieur.",
      desc: "Tu observes, tu écoutes et tu retiens tout. Timide ? Oui, parfois. Mais quand tu te sens en confiance, tu dévoiles une imagination, une douceur et une sincérité qui bluffent tout le monde. Ton monde intérieur est un vrai trésor.",
      strengths: ["Un regard qui voit tout", "Une créativité secrète", "Une douceur qui rassure"],
      flaws: ["Tu rougis pour un rien", "Tu gardes tes idées pour toi (alors qu'elles sont géniales)"],
      mantra: "Je dirai quelque chose… peut-être… tout à l'heure.",
      ally: "blonde"
    },
    bleue: {
      name: "Bleue", color: "#2aaee0", img: "img/bleue.webp",
      tag: "Cheffe de bande, naturellement.",
      desc: "Organisée, déterminée et sûre de toi : tu sais où tu vas et tu as déjà un plan (avec tableau et couleurs). Les autres te suivent parce que tu rassures par ton assurance. Ton défi : laisser de la place aux idées des autres.",
      strengths: ["Un sens de l'organisation redoutable", "Tu prends des décisions sans trembler", "Tu inspires confiance"],
      flaws: ["Tu veux toujours avoir raison", "Tu donnes des ordres sans t'en rendre compte"],
      mantra: "J'ai un plan. Suivez-moi.",
      ally: "rose"
    }
  };
  const KEYS = Object.keys(ELLES);

  /* ------------------------------------------------------------------ *
   *  Les 12 questions (chaque couleur est la « bonne » réponse 8 fois)
   * ------------------------------------------------------------------ */
  const QUESTIONS = [
    { world: "Le désert des possibles", bg: "desert", bx: 50,
      q: "Ton réveil sonne. Ta première pensée, c'est…",
      a: [["rose", "Allez, voyons comment la journée se présente !"],
          ["blonde", "Aujourd'hui, je vais tout déchirer. Qui veut m'en empêcher ?"],
          ["brune", "J'ai bien préparé mon sac ? Et mes devoirs ? Et… tout ?"],
          ["violette", "Cinq minutes de plus, le temps de me raconter une blague."]] },
    { world: "Le désert des possibles", bg: "desert", bx: 45,
      q: "Premier jour dans une nouvelle classe. Tu fais quoi ?",
      a: [["blonde", "Je me présente à tout le monde. Et si on me cherche, on me trouve."],
          ["brune", "Je repère les sorties, les profs et les gens bizarres. Par sécurité."],
          ["verte", "Je m'installe au fond, discrètement. Si on m'oublie, c'est parfait."],
          ["bleue", "Je repère qui dirige la classe. Spoiler : bientôt, ce sera moi."]] },
    { world: "L'arche de pierre", bg: "desert", bx: 8,
      q: "Un exposé en groupe : ton rôle, c'est…",
      a: [["rose", "Celle qui s'assure que tout le monde trouve sa place."],
          ["violette", "Celle qui met l'ambiance et glisse un meme dans les slides."],
          ["verte", "Celle qui fait la plus grosse partie du travail, sans être sur le devant de la scène."],
          ["bleue", "Celle qui crée le planning avec un code couleur."]] },
    { world: "L'arche de pierre", bg: "desert", bx: 14,
      q: "Ta meilleure amie te lance un défi complètement fou. Ta réaction ?",
      a: [["blonde", "Défi accepté, je m'échauffe !"],
          ["brune", "Euh… et si ça tourne mal ? J'ai besoin d'un plan B, C et D."],
          ["violette", "Je relève le défi en faisant tellement de bruit que tout le monde regarde."],
          ["bleue", "Je négocie les règles, je fixe les conditions. Puis j'accepte."]] },
    { world: "Rosie's Diner", bg: "desert", bx: 50,
      q: "Au Rosie's, le serveur attend ta commande…",
      a: [["rose", "Ce qui me tente, et je goûte aussi les assiettes des autres !"],
          ["blonde", "Le plus gros menu. Je ne fais jamais les choses à moitié."],
          ["brune", "Le plat que je connais déjà. Pas de mauvaise surprise."],
          ["verte", "Je chuchote ma commande en pointant le menu du doigt."]] },
    { world: "Rosie's Diner", bg: "desert", bx: 56,
      q: "Quelqu'un renverse un milkshake sur ta veste préférée !",
      a: [["rose", "Ça arrive. Je respire, on nettoie, et on en rira demain."],
          ["violette", "Je fais comme si c'était la nouvelle tendance : la veste milkshake."],
          ["verte", "Je dis « c'est pas grave », je rougis, et je file aux toilettes."],
          ["bleue", "Je veux un chiffon, des excuses et un remboursement. Dans cet ordre."]] },
    { world: "L'oasis aux secrets", bg: "desert", bx: 95,
      q: "C'est soirée pyjama ! Ton rôle dans la bande ?",
      a: [["rose", "Celle qui s'assure que chacune passe un bon moment."],
          ["blonde", "Celle qui lance la bataille d'oreillers (et la gagne)."],
          ["brune", "Celle qui vérifie que la porte est bien fermée. Deux fois."],
          ["bleue", "Celle qui choisit le film et l'ordre des snacks."]] },
    { world: "L'oasis aux secrets", bg: "desert", bx: 90,
      q: "Ta playlist du moment, c'est plutôt…",
      a: [["blonde", "Du fort, du rapide, du « on va tout casser »."],
          ["brune", "Des chansons douces et mélancoliques, casque sur les oreilles."],
          ["violette", "N'importe quoi, tant que je peux inventer la chorégraphie."],
          ["verte", "Mes pépites secrètes, que personne ne connaît (et que je garde pour moi)."]] },
    { world: "La nuit des pyramides", bg: "night",
      q: "Au milieu du désert, tu découvres une porte secrète. Tu…",
      a: [["rose", "Je regarde autour de moi : on y va ensemble, ou on n'y va pas."],
          ["violette", "Je frappe trois coups en criant « Livraison de pizzas ! »."],
          ["verte", "Je l'observe de loin… quelqu'un d'autre finira bien par l'ouvrir."],
          ["bleue", "Je prends les commandes. On entre dans l'ordre que j'ai décidé."]] },
    { world: "La nuit des pyramides", bg: "night",
      q: "Quand tu hésites, la petite voix dans ta tête te dit…",
      a: [["rose", "Écoute ton cœur, ça va aller."],
          ["blonde", "Fonce, tu n'as rien à perdre !"],
          ["brune", "Attends… vérifie encore une fois."],
          ["bleue", "Arrête de douter : tu sais ce que tu dois faire."]] },
    { world: "Sous les deux lunes", bg: "night",
      q: "Ton super-pouvoir idéal ?",
      a: [["brune", "Voir l'avenir, pour éviter les catastrophes."],
          ["violette", "Faire rire n'importe qui, même le plus grincheux."],
          ["verte", "L'invisibilité. Parfois, être tranquille, c'est le luxe."],
          ["bleue", "Convaincre n'importe qui de faire ce que je dis."]] },
    { world: "Sous les deux lunes", bg: "night",
      q: "Dernière question ! Tes amis te décriraient comme…",
      a: [["rose", "Quelqu'un de sincère, qui écoute et qui est toujours là."],
          ["blonde", "Une vraie battante, toujours prête à défendre les siens."],
          ["violette", "Le rayon de soleil de la bande (et son clown officiel)."],
          ["verte", "Quelqu'un de discret, mais intarissable quand on la connaît."]] }
  ];
  const N = QUESTIONS.length;
  const POINTS = 3;

  /* ------------------------------------------------------------------ *
   *  Utilitaires
   * ------------------------------------------------------------------ */
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const shuffle = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.random() * (i + 1) | 0; [a[i], a[j]] = [a[j], a[i]]; } return a; };
  const cssColor = k => ELLES[k].color;

  const state = { idx: 0, picks: [], scores: null, result: null, busy: false };

  /* ------------------------------------------------------------------ *
   *  Écrans & décors
   * ------------------------------------------------------------------ */
  function show(id) {
    $$(".screen").forEach(s => s.classList.toggle("active", s.id === id));
    document.body.classList.toggle("is-result", id === "result");
    window.scrollTo(0, 0);
  }

  function setBg(name, bx) {
    $$(".bg").forEach(b => {
      b.classList.toggle("on", b.dataset.bg === name);
      if (b.dataset.bg === name && bx != null) b.style.setProperty("--bx", bx + "%");
    });
    document.body.dataset.world = name === "night" ? "night" : "desert";
  }

  // parallaxe pointeur / inclinaison
  const root = document.documentElement;
  addEventListener("pointermove", e => {
    if (reduceMotion) return;
    root.style.setProperty("--px", ((e.clientX / innerWidth) - .5).toFixed(3));
    root.style.setProperty("--py", ((e.clientY / innerHeight) - .5).toFixed(3));
  }, { passive: true });
  addEventListener("deviceorientation", e => {
    if (reduceMotion || e.gamma == null) return;
    root.style.setProperty("--px", Math.max(-.5, Math.min(.5, e.gamma / 60)).toFixed(3));
    root.style.setProperty("--py", Math.max(-.5, Math.min(.5, (e.beta - 45) / 90)).toFixed(3));
  }, { passive: true });

  /* ------------------------------------------------------------------ *
   *  Quiz
   * ------------------------------------------------------------------ */
  const peekOrder = shuffle(KEYS);

  function renderQuestion() {
    const Q = QUESTIONS[state.idx];
    setBg(Q.bg, Q.bx);
    $("#qnum").textContent = state.idx + 1;
    const pr = $(".progress");
    pr.setAttribute("aria-valuenow", state.idx);
    $(".bar i").style.width = (state.idx / N * 100) + "%";
    $("#back").disabled = state.idx === 0;
    $("#world").textContent = `Monde ${state.idx + 1} · ${Q.world}`;
    $("#qtitle").textContent = Q.q;

    const box = $("#answers");
    box.innerHTML = "";
    shuffle(Q.a).forEach(([key, text], i) => {
      const b = document.createElement("button");
      b.type = "button"; b.className = "ans"; b.dataset.key = key; b.dataset.l = "ABCD"[i];
      b.style.setProperty("--i", i);
      b.textContent = text;
      b.addEventListener("click", ev => pick(b, ev));
      box.appendChild(b);
    });

    const card = $("#qcard");
    card.classList.remove("swap"); void card.offsetWidth; card.classList.add("swap");

    const peek = $("#peek");
    peek.src = ELLES[peekOrder[state.idx % 6]].img;
    peek.classList.remove("swap"); void peek.offsetWidth; peek.classList.add("swap");
  }

  function ripple(btn, ev) {
    const r = btn.getBoundingClientRect(), d = Math.max(r.width, r.height) * 2;
    const s = document.createElement("span");
    s.className = "rip";
    s.style.cssText = `width:${d}px;height:${d}px;left:${(ev.clientX || r.left + r.width / 2) - r.left - d / 2}px;top:${(ev.clientY || r.top + r.height / 2) - r.top - d / 2}px`;
    btn.appendChild(s);
    setTimeout(() => s.remove(), 650);
  }

  function pick(btn, ev) {
    if (state.busy) return;
    state.busy = true;
    ripple(btn, ev);
    btn.classList.add("picked");
    state.picks[state.idx] = btn.dataset.key;
    burst(ev.clientX || innerWidth / 2, ev.clientY || innerHeight / 2, 10, ["#fff", "#ffd1e6", "#ffe08a"]);
    setTimeout(() => {
      state.busy = false;
      if (state.idx < N - 1) { state.idx++; renderQuestion(); }
      else finish();
    }, reduceMotion ? 50 : 520);
  }

  function back() {
    if (state.busy || state.idx === 0) return;
    state.idx--; state.picks.length = state.idx; renderQuestion();
  }

  function computeScores() {
    const s = Object.fromEntries(KEYS.map(k => [k, 0]));
    state.picks.forEach(k => { s[k] += POINTS; });
    return s;
  }

  function ranking(scores) {
    // égalité : la couleur choisie le plus récemment l'emporte
    const recency = k => state.picks.lastIndexOf(k);
    return KEYS.slice().sort((a, b) => scores[b] - scores[a] || recency(b) - recency(a));
  }

  /* ------------------------------------------------------------------ *
   *  Chargement + résultat
   * ------------------------------------------------------------------ */
  const LOADING_LINES = ["Les couleurs se mélangent…", "Les cheveux changent de teinte…", "Elle écoute ses voix intérieures…", "Quelque chose se dessine…"];

  function finish() {
    $(".bar i").style.width = "100%";
    state.scores = computeScores();
    const rank = ranking(state.scores);
    state.result = rank[0]; state.second = rank[1];
    setBg("regard");
    show("loading");
    let i = 0;
    const t = setInterval(() => { $("#loadingSub").textContent = LOADING_LINES[++i % LOADING_LINES.length]; }, 900);
    setTimeout(() => { clearInterval(t); showResult(); }, reduceMotion ? 300 : 3300);
  }

  function showResult(fromHash) {
    const key = state.result, E = ELLES[key];
    root.style.setProperty("--accent", E.color);
    setBg("desert", 50);
    show("result");
    document.title = `Je suis Elle ${E.name} ! – Le test ELLES`;
    history.replaceState(null, "", "#resultat-" + key);

    const img = $("#r-img"); img.src = E.img; img.alt = `Elle ${E.name}`;
    $("#r-name").textContent = `Elle ${E.name}`;
    $("#r-tag").textContent = E.tag;
    $("#r-desc").textContent = E.desc;
    $("#r-mantra").textContent = E.mantra;
    $("#r-strengths").innerHTML = E.strengths.map(s => `<li>${s}</li>`).join("");
    $("#r-flaws").innerHTML = E.flaws.map(s => `<li>${s}</li>`).join("");
    const ally = ELLES[E.ally];
    $("#r-ally").textContent = `Elle ${ally.name}`; $("#r-ally-img").src = ally.img;

    const hasMix = !fromHash && state.scores;
    $$(".mix-title,#mix").forEach(n => n.hidden = !hasMix);
    const hidden = $("#r-hidden").closest(".duo-card");
    hidden.hidden = !hasMix;
    $(".duo").style.gridTemplateColumns = hasMix ? "" : "1fr";
    if (hasMix) {
      const H = ELLES[state.second];
      $("#r-hidden").textContent = `Elle ${H.name}`; $("#r-hidden-img").src = H.img;
      const total = POINTS * N;
      const rank = ranking(state.scores);
      $("#mix").innerHTML = rank.map(k => `
        <div class="mrow" style="--c:${cssColor(k)}"><span>${ELLES[k].name}</span>
        <div class="t"><i data-w="${Math.round(state.scores[k] / total * 100)}"></i></div>
        <output>${Math.round(state.scores[k] / total * 100)}%</output></div>`).join("");
      requestAnimationFrame(() => setTimeout(() => $$("#mix i").forEach(i => i.style.width = i.dataset.w + "%"), 250));
    }
    if (!fromHash) {
      const cols = [E.color, "#fff", "#ffd1e6", ELLES.violette.color, ELLES.blonde.color];
      for (let i = 0; i < 6; i++) setTimeout(() => burst(innerWidth * (.15 + Math.random() * .7), innerHeight * (.2 + Math.random() * .3), 26, cols), i * 220);
    }
  }

  function restart() {
    state.idx = 0; state.picks = []; state.scores = null; state.result = null;
    root.style.setProperty("--accent", "#ff4f93");
    document.title = "Quelle Elle se cache en toi ? – Le test ELLES";
    history.replaceState(null, "", location.pathname + location.search);
    setBg("desert", 50);
    show("intro");
  }

  /* ------------------------------------------------------------------ *
   *  Partage & carte à télécharger
   * ------------------------------------------------------------------ */
  function toast(msg) {
    const t = $("#toast"); t.textContent = msg; t.classList.add("on");
    clearTimeout(toast.t); toast.t = setTimeout(() => t.classList.remove("on"), 3200);
  }

  async function share() {
    const E = ELLES[state.result];
    const url = location.origin && location.origin !== "null" ? location.origin + location.pathname + "#resultat-" + state.result : location.href;
    const text = `Je suis Elle ${E.name} ! « ${E.mantra} » Et toi, quelle Elle se cache en toi ? Le tome 4, Intemporelle(s), est en librairie !`;
    try {
      if (navigator.share) { await navigator.share({ title: "Le test ELLES", text, url }); return; }
      await navigator.clipboard.writeText(`${text} ${url}`);
      toast("Lien copié ! Colle-le dans ta story ou à ta bande 💌");
    } catch (e) { if (e && e.name !== "AbortError") toast("Impossible de partager ici : copie l'adresse de la page !"); }
  }

  const loadImg = src => new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = rej; i.src = src; });

  function wrap(ctx, text, x, y, maxW, lh) {
    const words = text.split(" "); let line = "";
    words.forEach(w => {
      const test = line + w + " ";
      if (ctx.measureText(test).width > maxW && line) { ctx.fillText(line.trim(), x, y); line = w + " "; y += lh; }
      else line = test;
    });
    ctx.fillText(line.trim(), x, y); return y;
  }

  async function downloadCard() {
    const E = ELLES[state.result];
    try {
      const [bg, girl, logo] = await Promise.all([loadImg("img/bg-pyramides.webp"), loadImg(E.img), loadImg("img/logo.png")]);
      const W = 1080, H = 1920, c = document.createElement("canvas"); c.width = W; c.height = H;
      const x = c.getContext("2d");
      const s = Math.max(W / bg.width, H / bg.height);
      x.drawImage(bg, (W - bg.width * s) / 2, (H - bg.height * s) / 2, bg.width * s, bg.height * s);
      let g = x.createRadialGradient(W / 2, 900, 80, W / 2, 900, 900);
      g.addColorStop(0, E.color + "cc"); g.addColorStop(1, "#1c0f3a00");
      x.fillStyle = g; x.fillRect(0, 0, W, H);
      g = x.createLinearGradient(0, 0, 0, H);
      g.addColorStop(0, "rgba(28,15,58,.55)"); g.addColorStop(.5, "rgba(28,15,58,0)"); g.addColorStop(1, "rgba(28,15,58,.85)");
      x.fillStyle = g; x.fillRect(0, 0, W, H);
      // logo en blanc
      const lc = document.createElement("canvas"); lc.width = logo.width; lc.height = logo.height;
      const lx = lc.getContext("2d"); lx.drawImage(logo, 0, 0); lx.globalCompositeOperation = "source-in"; lx.fillStyle = "#fff"; lx.fillRect(0, 0, lc.width, lc.height);
      x.drawImage(lc, W / 2 - 150, 90, 300, 300 * logo.height / logo.width);
      // portrait
      const gh = 1000, gw = girl.width * gh / girl.height;
      x.save(); x.shadowColor = "rgba(10,0,40,.6)"; x.shadowBlur = 50; x.shadowOffsetY = 20;
      x.drawImage(girl, W / 2 - gw / 2, 420, gw, gh); x.restore();
      x.textAlign = "center";
      x.fillStyle = "#fff"; x.font = "600 44px Fredoka, Trebuchet MS, sans-serif"; x.fillText("MON MONDE INTÉRIEUR EST…", W / 2, 1520);
      x.fillStyle = E.color; x.font = "700 130px Fredoka, Trebuchet MS, sans-serif";
      x.shadowColor = "rgba(0,0,0,.35)"; x.shadowBlur = 18; x.fillText(`Elle ${E.name}`, W / 2, 1650); x.shadowBlur = 0;
      x.fillStyle = "#fff"; x.font = "500 44px Fredoka, Trebuchet MS, sans-serif"; wrap(x, `« ${E.mantra} »`, W / 2, 1735, 900, 56);
      x.font = "600 36px Fredoka, Trebuchet MS, sans-serif"; x.globalAlpha = .9;
      x.fillText("Tome 4 · Intemporelle(s) · En librairie !", W / 2, 1860); x.globalAlpha = 1;
      const a = document.createElement("a");
      a.download = `elles-${state.result}.png`; a.href = c.toDataURL("image/png");
      document.body.appendChild(a); a.click(); a.remove();
      toast("Ta carte est prête ! Partage-la en story 📸");
    } catch (e) { toast("Ouvre la page depuis le site pour télécharger ta carte."); }
  }

  /* ------------------------------------------------------------------ *
   *  Effets : étoiles, bokeh, étoile filante, confettis
   * ------------------------------------------------------------------ */
  const cv = $("#fx"), cx = cv.getContext("2d");
  let W = 0, H = 0, dpr = 1, stars = [], orbs = [], sparks = [], shoot = null, nextShoot = 2500;

  function resize() {
    dpr = Math.min(devicePixelRatio || 1, 2);
    W = innerWidth; H = innerHeight;
    cv.width = W * dpr; cv.height = H * dpr; cx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const n = Math.round(Math.min(150, W * H / 9000));
    stars = Array.from({ length: n }, () => ({ x: Math.random() * W, y: Math.random() * H * .62, r: Math.random() * 1.5 + .4, p: Math.random() * 6.28, v: .6 + Math.random() * 1.6 }));
    orbs = Array.from({ length: Math.round(Math.min(16, W / 70)) }, (_, i) => ({
      x: Math.random() * W, y: Math.random() * H, r: 18 + Math.random() * 46, c: cssColor(KEYS[i % 6]),
      vx: (Math.random() - .5) * .18, vy: -.12 - Math.random() * .25, p: Math.random() * 6.28 }));
  }

  function burst(x, y, n, colors) {
    if (reduceMotion) return;
    for (let i = 0; i < n; i++) {
      const a = Math.random() * 6.28, v = 2 + Math.random() * 5;
      sparks.push({ x, y, vx: Math.cos(a) * v, vy: Math.sin(a) * v - 2, g: .12, life: 1, d: .012 + Math.random() * .012,
        r: 2 + Math.random() * 4, c: colors[i % colors.length], sq: Math.random() < .4, rot: Math.random() * 6.28 });
    }
  }

  let last = performance.now();
  function frame(t) {
    const dt = Math.min(50, t - last); last = t;
    cx.clearRect(0, 0, W, H);
    cx.globalCompositeOperation = "lighter";
    // bokeh
    for (const o of orbs) {
      o.x += o.vx * dt / 16; o.y += o.vy * dt / 16;
      if (o.y < -o.r * 2) { o.y = H + o.r; o.x = Math.random() * W; }
      const a = .1 + .06 * Math.sin(t / 1400 + o.p);
      const g = cx.createRadialGradient(o.x, o.y, 0, o.x, o.y, o.r);
      g.addColorStop(0, o.c + "88"); g.addColorStop(1, o.c + "00");
      cx.globalAlpha = a * 2.2; cx.fillStyle = g; cx.beginPath(); cx.arc(o.x, o.y, o.r, 0, 6.28); cx.fill();
    }
    // étoiles
    cx.fillStyle = "#fff";
    for (const s of stars) {
      cx.globalAlpha = .25 + .75 * Math.abs(Math.sin(t / 1000 * s.v + s.p));
      cx.beginPath(); cx.arc(s.x, s.y, s.r, 0, 6.28); cx.fill();
    }
    // étoile filante
    nextShoot -= dt;
    if (!shoot && nextShoot < 0) { shoot = { x: Math.random() * W * .8 + W * .15, y: Math.random() * H * .25, l: 0 }; nextShoot = 4500 + Math.random() * 5000; }
    if (shoot) {
      shoot.l += dt / 650; const k = shoot.l, ax = shoot.x - k * 260, ay = shoot.y + k * 110;
      const g = cx.createLinearGradient(ax, ay, ax + 120, ay - 52);
      g.addColorStop(0, "#fff0"); g.addColorStop(1, "#fff");
      cx.globalAlpha = 1 - k * .8; cx.strokeStyle = g; cx.lineWidth = 2.2; cx.beginPath(); cx.moveTo(ax, ay); cx.lineTo(ax + 120, ay - 52); cx.stroke();
      if (k >= 1) shoot = null;
    }
    // confettis
    cx.globalCompositeOperation = "source-over";
    for (let i = sparks.length - 1; i >= 0; i--) {
      const p = sparks[i];
      p.x += p.vx; p.y += p.vy; p.vy += p.g; p.vx *= .985; p.life -= p.d; p.rot += .15;
      if (p.life <= 0) { sparks.splice(i, 1); continue; }
      cx.globalAlpha = Math.min(1, p.life * 1.6); cx.fillStyle = p.c;
      if (p.sq) { cx.save(); cx.translate(p.x, p.y); cx.rotate(p.rot); cx.fillRect(-p.r, -p.r / 2, p.r * 2, p.r); cx.restore(); }
      else { cx.beginPath(); cx.arc(p.x, p.y, p.r, 0, 6.28); cx.fill(); }
    }
    cx.globalAlpha = 1;
    requestAnimationFrame(frame);
  }

  /* ------------------------------------------------------------------ *
   *  Initialisation
   * ------------------------------------------------------------------ */
  addEventListener("resize", resize);
  resize();
  if (!reduceMotion) requestAnimationFrame(frame);

  $("#start").addEventListener("click", e => { burst(e.clientX, e.clientY, 18, KEYS.map(cssColor)); state.idx = 0; state.picks = []; show("quiz"); renderQuestion(); });
  $("#back").addEventListener("click", back);
  $("#again").addEventListener("click", restart);
  $("#share").addEventListener("click", share);
  $("#card").addEventListener("click", downloadCard);
  addEventListener("keydown", e => {
    if (!$("#quiz").classList.contains("active") || e.metaKey || e.ctrlKey) return;
    const n = "1234".indexOf(e.key);
    if (n >= 0) $$(".ans")[n]?.click();
    else if (e.key === "ArrowLeft") back();
  });

  // lien partagé : #resultat-violette
  const m = location.hash.match(/^#resultat-(\w+)$/);
  if (m && ELLES[m[1]]) { state.result = m[1]; showResult(true); }
})();
