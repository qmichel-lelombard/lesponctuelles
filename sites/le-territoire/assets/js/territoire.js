/* LE TERRITOIRE — interactions. Aucune dépendance. */
(() => {
  'use strict';

  const reduit = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fin = window.matchMedia('(pointer: fine)').matches;
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));
  const lire = (k) => { try { return localStorage.getItem(k); } catch (e) { return null; } };
  const ecrire = (k, v) => { try { localStorage.setItem(k, v); } catch (e) { /* stockage indisponible */ } };

  /* ------------------------------------------------------------------
     Défilement : une seule boucle rAF partagée
     ------------------------------------------------------------------ */
  let scrollY = window.scrollY, dernierY = scrollY, vitesse = 0, tick = false;
  const abonnes = [];
  const surDefilement = (fn) => abonnes.push(fn);
  const boucle = () => {
    scrollY = window.scrollY;
    vitesse = scrollY - dernierY;
    dernierY = scrollY;
    abonnes.forEach((fn) => fn(scrollY, vitesse));
    tick = false;
  };
  window.addEventListener('scroll', () => { if (!tick) { tick = true; requestAnimationFrame(boucle); } }, { passive: true });
  window.addEventListener('resize', () => requestAnimationFrame(boucle));

  /* ------------------------------------------------------------------
     Navigation
     ------------------------------------------------------------------ */
  const nav = $('#nav');
  const hero = $('#haut');
  surDefilement((y, v) => {
    const h = hero ? hero.offsetHeight * 0.6 : 400;
    nav.classList.toggle('is-solide', y > h);
    if (Math.abs(v) > 4) nav.classList.toggle('is-cache', v > 0 && y > h * 1.6);
  });
  const liens = $$('.nav__liens a');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entrees) => {
      entrees.forEach((e) => {
        if (!e.isIntersecting) return;
        liens.forEach((a) => a.setAttribute('aria-current', a.hash === '#' + e.target.id ? 'true' : 'false'));
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    liens.forEach((a) => { const s = $(a.hash); if (s) io.observe(s); });
  }

  /* ------------------------------------------------------------------
     Compte à rebours jusqu'à la sortie
     ------------------------------------------------------------------ */
  const compte = $('#compte');
  if (compte) {
    const sortie = new Date(compte.dataset.sortie);
    const val = $('#compte-valeur'), lab = $('#compte-label');
    const maj = () => {
      const ms = sortie - new Date();
      if (ms <= 0) { val.textContent = 'Disponible'; lab.textContent = 'en librairie'; return; }
      const j = Math.floor(ms / 864e5), h = Math.floor(ms / 36e5) % 24;
      val.textContent = j > 0 ? 'J-' + j : h + ' h';
      lab.textContent = j > 0 ? 'avant la sortie · 16.10.2026' : 'avant la sortie';
    };
    maj();
    setInterval(maj, 60000);
  }

  /* ------------------------------------------------------------------
     Diorama : parallaxe au défilement et au pointeur
     ------------------------------------------------------------------ */
  const fond = $('[data-couche="fond"]'), plan = $('[data-couche="plan"]');
  if (fond && plan && !reduit) {
    let px = 0, py = 0, cx = 0, cy = 0;
    const grand = () => window.innerWidth >= 900;
    const applique = () => {
      const y = Math.min(scrollY, window.innerHeight);
      cx += (px - cx) * 0.08; cy += (py - cy) * 0.08;
      const sF = grand() ? 1.06 : 1.12, sP = grand() ? 1.06 : 1.04;
      fond.style.transform = `translate3d(${cx * -6}px, ${y * 0.18 + cy * -4}px, 0) scale(${sF + y * 0.0002})`;
      plan.style.transform = `translate3d(${cx * 14}px, ${y * -0.06 + cy * 8}px, 0) scale(${sP})`;
    };
    surDefilement(applique);
    if (fin) {
      let anim = null;
      const suit = () => { applique(); anim = (Math.abs(px - cx) + Math.abs(py - cy) > 0.002) ? requestAnimationFrame(suit) : null; };
      hero.addEventListener('pointermove', (e) => {
        px = e.clientX / window.innerWidth - 0.5; py = e.clientY / window.innerHeight - 0.5;
        if (!anim) anim = requestAnimationFrame(suit);
      });
    }
    applique();
  }

  /* ------------------------------------------------------------------
     Neige (canvas) — le vent suit la vitesse de défilement
     ------------------------------------------------------------------ */
  const canvas = $('#neige'), boutonNeige = $('#bouton-neige');
  const neige = { active: !reduit && lire('territoire-neige') !== 'off', masquee: false };
  if (canvas && canvas.getContext) {
    const ctx = canvas.getContext('2d');
    let L = 0, H = 0, flocons = [], vent = 0, raf = null, avant = 0;
    const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    const dimensionne = () => {
      L = window.innerWidth; H = window.innerHeight;
      canvas.width = L * dpr; canvas.height = H * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const n = Math.round(Math.min(160, (L * H) / 9000) * (navigator.connection && navigator.connection.saveData ? 0.4 : 1));
      flocons = Array.from({ length: n }, () => nouveau(true));
    };
    const nouveau = (partout) => {
      const z = Math.random();
      return { x: Math.random() * L, y: partout ? Math.random() * H : -10, r: 0.6 + z * 2.2, v: 0.35 + z * 1.1, o: 0.25 + z * 0.55, p: Math.random() * 6.28, a: 0.4 + Math.random() };
    };
    const dessine = (t) => {
      const dt = Math.min(48, t - avant || 16) / 16; avant = t;
      vent += (Math.max(-25, Math.min(25, vitesse)) * 0.12 - vent) * 0.04;
      vitesse *= 0.9;
      ctx.clearRect(0, 0, L, H);
      ctx.fillStyle = '#f4f3fb';
      for (const f of flocons) {
        f.p += 0.01 * dt * f.a;
        f.y += (f.v + Math.abs(vent) * 0.15 * f.r) * dt;
        f.x += (Math.sin(f.p) * 0.4 + vent * f.r * 0.35) * dt;
        if (f.y > H + 10) Object.assign(f, nouveau(false));
        if (f.x > L + 10) f.x = -10; else if (f.x < -10) f.x = L + 10;
        ctx.globalAlpha = f.o;
        ctx.beginPath(); ctx.arc(f.x, f.y, f.r, 0, 6.283); ctx.fill();
      }
      raf = requestAnimationFrame(dessine);
    };
    const etat = () => {
      const marche = neige.active && !neige.masquee && !document.hidden;
      canvas.style.display = neige.active ? '' : 'none';
      if (marche && !raf) { avant = performance.now(); raf = requestAnimationFrame(dessine); }
      if (!marche && raf) { cancelAnimationFrame(raf); raf = null; if (!neige.active) ctx.clearRect(0, 0, L, H); }
    };
    dimensionne();
    window.addEventListener('resize', () => { clearTimeout(dimensionne.t); dimensionne.t = setTimeout(dimensionne, 200); });
    document.addEventListener('visibilitychange', etat);
    // Pas de neige devant les planches : on lit tranquillement.
    const liseuse = $('#extrait');
    if (liseuse && 'IntersectionObserver' in window) {
      new IntersectionObserver(([e]) => { neige.masquee = e.intersectionRatio > 0.35; canvas.style.opacity = neige.masquee ? '0' : ''; etat(); }, { threshold: [0, 0.35, 0.6] }).observe(liseuse);
    }
    canvas.style.transition = 'opacity .6s';
    if (boutonNeige) {
      boutonNeige.setAttribute('aria-pressed', String(neige.active));
      boutonNeige.addEventListener('click', () => {
        neige.active = !neige.active;
        boutonNeige.setAttribute('aria-pressed', String(neige.active));
        ecrire('territoire-neige', neige.active ? 'on' : 'off');
        etat();
      });
    }
    etat();
  }

  /* ------------------------------------------------------------------
     Apparitions au défilement
     ------------------------------------------------------------------ */
  const aMontrer = $$('[data-apparition], .recitatif');
  if ('IntersectionObserver' in window && !reduit) {
    const io = new IntersectionObserver((entrees) => {
      entrees.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('is-visible'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.12 });
    aMontrer.forEach((el) => io.observe(el));
  } else {
    aMontrer.forEach((el) => el.classList.add('is-visible'));
  }

  /* ------------------------------------------------------------------
     Frise : la ligne se remplit au fil de la lecture
     ------------------------------------------------------------------ */
  const frise = $('#frise');
  if (frise) {
    surDefilement(() => {
      const r = frise.getBoundingClientRect();
      const p = Math.max(0, Math.min(1, (window.innerHeight * 0.6 - r.top) / r.height));
      frise.style.setProperty('--p', p.toFixed(3));
    });
  }

  /* ------------------------------------------------------------------
     Liseuse de planches
     ------------------------------------------------------------------ */
  const scene = $('#liseuse-scene');
  if (scene) {
    const pages = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((n) => ({
      n,
      src: `assets/img/planches/planche-${n}`,
      alt: { 3: 'Préface de Joe Pruett', 4: 'Page de garde', 5: 'Page titre', 7: 'Ouverture du chapitre 1' }[n] || `Page ${n}`,
    }));
    // En double page, on respecte l'imposition de l'album : la page impaire est à droite.
    const doubles = [[0], [1, 2], [3, 4], [5, 6], [7, 8], [9]];
    const mqDouble = window.matchMedia('(min-width: 1000px) and (orientation: landscape)');
    const webp = document.createElement('canvas').toDataURL('image/webp').startsWith('data:image/webp');
    const ext = webp ? '.webp' : '.jpg';
    const vignettes = $('#liseuse-vignettes'), compteur = $('#liseuse-compteur');
    const prec = $('#liseuse-prec'), suiv = $('#liseuse-suiv');
    let i = 0;

    pages.forEach((p, k) => {
      const b = document.createElement('button');
      b.type = 'button'; b.setAttribute('role', 'tab'); b.setAttribute('aria-label', p.alt);
      b.innerHTML = `<img src="${p.src}-mini.webp" alt="" width="48" height="68" loading="lazy">`;
      b.addEventListener('click', () => aller(k));
      vignettes.appendChild(b);
    });

    const groupe = () => mqDouble.matches ? doubles.find((g) => g.includes(i)) : [i];
    const prechargement = (k) => { if (pages[k]) { const im = new Image(); im.src = pages[k].src + ext; } };

    const rendu = () => {
      const g = groupe();
      $$('img', scene).forEach((im) => im.remove());
      scene.classList.toggle('is-double', g.length > 1);
      g.forEach((k) => {
        const im = new Image();
        im.alt = pages[k].alt + ' — Le Territoire, extrait';
        im.width = 852; im.height = 1200;
        im.decoding = 'async';
        im.className = 'is-charge';
        im.onload = () => im.classList.remove('is-charge');
        im.src = pages[k].src + ext;
        scene.insertBefore(im, suiv);
      });
      const premier = g[0], dernier = g[g.length - 1];
      prec.disabled = premier === 0; suiv.disabled = dernier === pages.length - 1;
      compteur.textContent = g.map((k) => pages[k].n).join('–') + ' / 12';
      $$('button', vignettes).forEach((b, k) => b.setAttribute('aria-current', String(g.includes(k))));
      const actif = vignettes.children[premier];
      if (actif) vignettes.scrollTo({ left: actif.offsetLeft - vignettes.clientWidth / 2 + 24, behavior: reduit ? 'auto' : 'smooth' });
      prechargement(dernier + 1); prechargement(dernier + 2);
    };
    const aller = (k) => { i = Math.max(0, Math.min(pages.length - 1, k)); rendu(); };
    const pas = (d) => { const g = groupe(); aller(d > 0 ? g[g.length - 1] + 1 : g[0] - 1); };

    prec.addEventListener('click', () => pas(-1));
    suiv.addEventListener('click', () => pas(1));
    scene.parentElement.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') { e.preventDefault(); pas(1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); pas(-1); }
    });
    scene.parentElement.tabIndex = 0;
    let x0 = null;
    scene.addEventListener('pointerdown', (e) => { x0 = e.clientX; });
    scene.addEventListener('pointerup', (e) => {
      if (x0 === null) return;
      const dx = e.clientX - x0; x0 = null;
      if (Math.abs(dx) > 40) pas(dx < 0 ? 1 : -1);
    });
    mqDouble.addEventListener ? mqDouble.addEventListener('change', rendu) : mqDouble.addListener(rendu);

    // On ouvre directement sur l'histoire (planche 8), la préface reste accessible.
    i = 5;
    const lancer = () => rendu();
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { lancer(); io.disconnect(); } }, { rootMargin: '600px 0px' });
      io.observe(scene);
    } else lancer();

    const plein = $('#liseuse-plein'), boite = $('#liseuse');
    if (plein && boite.requestFullscreen) {
      plein.addEventListener('click', () => (document.fullscreenElement ? document.exitFullscreen() : boite.requestFullscreen()));
      document.addEventListener('fullscreenchange', () => { plein.textContent = document.fullscreenElement ? 'Quitter' : 'Plein écran'; });
    } else if (plein) plein.hidden = true;
  }

  /* ------------------------------------------------------------------
     Vidéo de l'atelier : chargée seulement au clic (connexions lentes)
     ------------------------------------------------------------------ */
  const facade = $('#ecran-facade');
  if (facade) {
    facade.addEventListener('click', () => {
      const f = document.createElement('iframe');
      f.src = facade.dataset.src;
      f.title = "Visite de l'atelier de Philippe Xavier";
      f.allow = 'autoplay; fullscreen; picture-in-picture';
      f.allowFullscreen = true;
      facade.replaceWith(f);
    });
  }

  /* ------------------------------------------------------------------
     Dédicaces : passées / prochaine / filtre pays
     ------------------------------------------------------------------ */
  const tournee = $('#tournee');
  if (tournee) {
    const auj = new Date(); auj.setHours(0, 0, 0, 0);
    let prochaine = false;
    $$('li', tournee).forEach((li) => {
      const d = new Date(li.dataset.date + 'T00:00:00');
      if (d < auj) li.classList.add('is-passe');
      else if (!prochaine) { li.classList.add('is-prochain'); prochaine = true; }
    });
    $$('.filtres button').forEach((b) => b.addEventListener('click', () => {
      $$('.filtres button').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      $$('li', tournee).forEach((li) => { li.hidden = b.dataset.pays !== 'tous' && li.dataset.pays !== b.dataset.pays; });
    }));
  }

  /* ------------------------------------------------------------------
     Partage
     ------------------------------------------------------------------ */
  const btnPartage = $('#partager'), btnCopie = $('#copier');
  const donnees = { title: 'Le Territoire — Philippe Xavier & Joe Pruett', text: "La fin du monde n'est pas la fin des hommes.", url: location.href.split('#')[0] };
  if (btnPartage) {
    if (navigator.share) btnPartage.addEventListener('click', () => navigator.share(donnees).catch(() => {}));
    else btnPartage.hidden = true;
  }
  if (btnCopie) btnCopie.addEventListener('click', () => {
    const ok = () => { btnCopie.textContent = 'Lien copié'; setTimeout(() => { btnCopie.textContent = 'Copier le lien'; }, 2000); };
    if (navigator.clipboard) navigator.clipboard.writeText(donnees.url).then(ok, () => {});
  });

  boucle();
})();
