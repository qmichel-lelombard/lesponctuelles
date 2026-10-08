(() => {
  'use strict';
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Champ d'étoiles (canvas léger, pausé hors écran) ---------- */
  const cv = $('#stars'), ctx = cv.getContext('2d');
  let W, H, stars = [], raf = 0, scrollY = 0;
  const DPR = Math.min(devicePixelRatio || 1, 1.5);
  function size() {
    W = cv.width = innerWidth * DPR; H = cv.height = innerHeight * DPR;
    const n = Math.round(Math.min(220, innerWidth * innerHeight / 9000));
    stars = Array.from({ length: n }, () => ({
      x: Math.random() * W, y: Math.random() * H,
      z: Math.random() * .8 + .2, r: Math.random() * 1.2 + .3, t: Math.random() * 6.28
    }));
  }
  function draw(t) {
    ctx.clearRect(0, 0, W, H);
    for (const s of stars) {
      const y = ((s.y - scrollY * s.z * .25 * DPR) % H + H) % H;
      const a = .35 + .65 * (.5 + .5 * Math.sin(t / 900 + s.t));
      ctx.globalAlpha = a * s.z;
      ctx.fillStyle = s.z > .85 ? '#cfe0ff' : '#97b4e3';
      ctx.beginPath(); ctx.arc(s.x, y, s.r * DPR * s.z, 0, 6.283); ctx.fill();
    }
  }
  function loop(t) { draw(t); raf = requestAnimationFrame(loop); }
  size(); draw(0);
  addEventListener('resize', () => { size(); draw(0); });
  if (!reduce) {
    raf = requestAnimationFrame(loop);
    document.addEventListener('visibilitychange', () => {
      cancelAnimationFrame(raf); if (!document.hidden) raf = requestAnimationFrame(loop);
    });
  }

  /* ---------- Menu, progression, section active ---------- */
  const nav = $('#nav'), burger = $('#burger'), bar = $('#progress');
  burger.addEventListener('click', () => {
    const o = nav.classList.toggle('open'); burger.setAttribute('aria-expanded', o);
  });
  nav.addEventListener('click', e => { if (e.target.closest('a')) { nav.classList.remove('open'); burger.setAttribute('aria-expanded', false); } });
  let tick = false;
  addEventListener('scroll', () => {
    scrollY = window.scrollY;
    if (tick) return; tick = true;
    requestAnimationFrame(() => {
      const h = document.documentElement.scrollHeight - innerHeight;
      bar.style.width = (h > 0 ? scrollY / h * 100 : 0) + '%';
      if (reduce) draw(0);
      tick = false;
    });
  }, { passive: true });
  const links = $$('.top__nav a');
  const secObs = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) links.forEach(l => l.classList.toggle('on', l.dataset.s === e.target.id));
  }), { rootMargin: '-45% 0px -50% 0px' });
  $$('main > section[id]').forEach(s => secObs.observe(s));

  /* ---------- Apparition au scroll ---------- */
  const revObs = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('in'); revObs.unobserve(e.target); }
  }), { threshold: .12, rootMargin: '0px 0px -6% 0px' });
  $$('.reveal').forEach(el => revObs.observe(el));

  /* ---------- Effet « décryptage » du texte ---------- */
  const GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/<>';
  function decode(el, final, dur = 900) {
    if (reduce) { el.textContent = final; return; }
    const t0 = performance.now();
    (function step(now) {
      const p = Math.min(1, (now - t0) / dur);
      const keep = Math.floor(final.length * p);
      el.textContent = final.split('').map((c, i) =>
        i < keep || c === ' ' || c === '.' ? c : GLYPHS[Math.random() * GLYPHS.length | 0]).join('');
      if (p < 1) requestAnimationFrame(step); else el.textContent = final;
    })(t0);
  }
  const tag = $('#tag');
  setTimeout(() => decode(tag, tag.dataset.text, 1400), 350);
  const decObs = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) { decode(e.target, e.target.dataset.text); decObs.unobserve(e.target); }
  }), { threshold: .6 });
  $$('.decode').forEach(el => decObs.observe(el));
  $$('.author').forEach(a => {
    const d = $('.decode', a);
    a.addEventListener('mouseenter', () => decode(d, d.dataset.text, 500));
  });

  /* ---------- Compte à rebours ---------- */
  const cd = $('#count'), target = new Date(cd.dataset.target).getTime();
  const pad = n => String(n).padStart(2, '0');
  function count() {
    const d = target - Date.now();
    if (d <= 0) { $('.count__grid').hidden = true; $('#count-done').hidden = false; return false; }
    $('#c-d').textContent = pad(Math.floor(d / 864e5));
    $('#c-h').textContent = pad(Math.floor(d % 864e5 / 36e5));
    $('#c-m').textContent = pad(Math.floor(d % 36e5 / 6e4));
    $('#c-s').textContent = pad(Math.floor(d % 6e4 / 1e3));
    return true;
  }
  if (count()) setInterval(count, 1000);

  /* ---------- Couverture : inclinaison 3D ---------- */
  const cover = $('#cover'), tilt = $('.album__tilt');
  if (!reduce && matchMedia('(hover: hover)').matches) {
    cover.addEventListener('pointermove', e => {
      const r = cover.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
      tilt.style.transform = `rotateY(${x * 12}deg) rotateX(${-y * 12}deg)`;
      tilt.style.setProperty('--gx', (x + .5) * 100 + '%'); tilt.style.setProperty('--gy', (y + .5) * 100 + '%');
    });
    cover.addEventListener('pointerleave', () => { tilt.style.transform = ''; });
  }

  /* ---------- Orbite → carte auteur ---------- */
  $$('.orbit a, .orbit__core').forEach(a => a.addEventListener('click', () => {
    const t = $(a.getAttribute('href')); if (!t) return;
    t.classList.remove('flash'); void t.offsetWidth; t.classList.add('flash');
  }));
})();
