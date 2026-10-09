(() => {
  'use strict';
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const smooth = (a, b, v) => { const t = clamp((v - a) / (b - a)); return t * t * (3 - 2 * t); };
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* ignoré */ } }
  };

  /* ---------- Ciel : étoiles en dérive, warp au scroll, galaxie, étoiles filantes ---------- */
  const cv = $('#stars'), ctx = cv.getContext('2d');
  const DPR = Math.min(devicePixelRatio || 1, 1.5);
  let W, H, stars = [], arm = [], shoots = [], raf = 0, scrollY = 0, vel = 0, lastY = 0, nextShoot = 3000;
  function size() {
    W = cv.width = innerWidth * DPR; H = cv.height = innerHeight * DPR;
    const n = Math.round(Math.min(280, innerWidth * innerHeight / 7000));
    stars = Array.from({ length: n }, () => ({
      x: Math.random() * W, y: Math.random() * H,
      z: Math.random() * .85 + .15, r: Math.random() * 1.2 + .3, t: Math.random() * 6.28
    }));
    arm = Array.from({ length: 520 }, (_, i) => {
      const a = i % 2 ? Math.PI : 0, t = Math.pow(Math.random(), .7);
      return { th: t * 5.2 + a + (Math.random() - .5) * .35, r: t, o: (Math.random() - .5) * .08, s: Math.random() * 1.1 + .3, b: Math.random() * .7 + .3 };
    });
  }
  function galaxy(t) {
    const fade = clamp(1 - scrollY / (innerHeight * 1.1));
    if (fade <= 0) return;
    const R = Math.min(W, H) * .42, cx = W * .8, cy = H * .26, rot = t / 70000;
    ctx.save(); ctx.translate(cx, cy); ctx.scale(1, .55); ctx.rotate(-.4);
    const g = ctx.createRadialGradient(0, 0, 0, 0, 0, R * .5);
    g.addColorStop(0, 'rgba(255,225,180,' + .55 * fade + ')'); g.addColorStop(.35, 'rgba(160,190,255,' + .14 * fade + ')'); g.addColorStop(1, 'rgba(100,140,255,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, R * .5, 0, 6.283); ctx.fill();
    for (const p of arm) {
      const th = p.th + rot * (1.6 - p.r), r = (p.r + p.o) * R;
      ctx.globalAlpha = .55 * p.b * fade * (1 - p.r * .4);
      ctx.fillStyle = p.r < .25 ? '#ffe3b8' : '#a9c4ff';
      ctx.fillRect(Math.cos(th) * r, Math.sin(th) * r, p.s * DPR, p.s * DPR);
    }
    ctx.restore(); ctx.globalAlpha = 1;
  }
  function draw(t, dt) {
    ctx.clearRect(0, 0, W, H);
    galaxy(t);
    const warp = clamp(Math.abs(vel) / 60);
    for (const s of stars) {
      s.x += .05 * s.z * DPR * dt / 16; s.y += .02 * s.z * DPR * dt / 16 - vel * s.z * .05 * DPR;
      if (s.x > W) s.x = 0; if (s.y > H) s.y = 0; if (s.y < 0) s.y = H;
      const tw = .35 + .65 * (.5 + .5 * Math.sin(t / 900 + s.t));
      ctx.globalAlpha = tw * s.z;
      ctx.fillStyle = s.z > .85 ? '#cfe0ff' : '#97b4e3';
      if (warp > .08) {
        ctx.strokeStyle = ctx.fillStyle; ctx.lineWidth = s.r * DPR * s.z;
        ctx.beginPath(); ctx.moveTo(s.x, s.y); ctx.lineTo(s.x, s.y + (vel > 0 ? 1 : -1) * warp * 38 * s.z * DPR); ctx.stroke();
      } else { ctx.beginPath(); ctx.arc(s.x, s.y, s.r * DPR * s.z, 0, 6.283); ctx.fill(); }
    }
    nextShoot -= dt;
    if (nextShoot < 0) {
      nextShoot = 5000 + Math.random() * 7000;
      shoots.push({ x: Math.random() * W * .8, y: Math.random() * H * .4, vx: (6 + Math.random() * 4) * DPR, vy: (2.5 + Math.random() * 2) * DPR, life: 1 });
    }
    shoots = shoots.filter(s => s.life > 0);
    for (const s of shoots) {
      s.x += s.vx; s.y += s.vy; s.life -= .018;
      const g = ctx.createLinearGradient(s.x, s.y, s.x - s.vx * 14, s.y - s.vy * 14);
      g.addColorStop(0, 'rgba(255,255,255,' + s.life + ')'); g.addColorStop(1, 'rgba(151,180,227,0)');
      ctx.globalAlpha = 1; ctx.strokeStyle = g; ctx.lineWidth = 1.6 * DPR;
      ctx.beginPath(); ctx.moveTo(s.x, s.y); ctx.lineTo(s.x - s.vx * 14, s.y - s.vy * 14); ctx.stroke();
    }
    ctx.globalAlpha = 1;
  }
  let tPrev = 0;
  function loop(t) {
    const dt = Math.min(50, t - tPrev || 16); tPrev = t;
    vel *= .9; draw(t, dt); raf = requestAnimationFrame(loop);
  }
  size(); draw(0, 16);
  addEventListener('resize', () => { size(); draw(0, 16); });
  if (!reduce) {
    raf = requestAnimationFrame(loop);
    document.addEventListener('visibilitychange', () => {
      cancelAnimationFrame(raf); if (!document.hidden) { tPrev = performance.now(); raf = requestAnimationFrame(loop); }
    });
  }

  /* ---------- En-tête : visible seulement après 10 s d'inactivité ---------- */
  const top = $('#top'), nav = $('#nav'), burger = $('#burger'), bar = $('#progress');
  let idle = 0;
  const showTop = () => top.classList.add('show');
  const hideTop = () => { if (!nav.classList.contains('open') && !top.matches(':hover')) top.classList.remove('show'); };
  const arm10 = () => { clearTimeout(idle); idle = setTimeout(showTop, 10000); };
  ['scroll', 'wheel', 'touchmove', 'keydown'].forEach(ev => addEventListener(ev, () => { hideTop(); arm10(); }, { passive: true }));
  ['pointermove', 'pointerdown', 'touchstart'].forEach(ev => addEventListener(ev, arm10, { passive: true }));
  arm10();
  burger.addEventListener('click', () => {
    const o = nav.classList.toggle('open'); burger.setAttribute('aria-expanded', o);
  });
  nav.addEventListener('click', e => { if (e.target.closest('a')) { nav.classList.remove('open'); burger.setAttribute('aria-expanded', false); top.classList.remove('show'); } });

  /* ---------- Section active, scènes immersives ---------- */
  const links = $$('.top__nav a');
  const secObs = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) links.forEach(l => l.classList.toggle('on', l.dataset.s === e.target.id));
  }), { rootMargin: '-45% 0px -50% 0px' });
  $$('main > section[id]').forEach(s => secObs.observe(s));

  const scenes = $$('.scene').map(el => {
    const pan = $('.scene__pan', el), cvs = $('.scene__fx', el);
    return { el, pan, cvs, c: cvs.getContext('2d'), ratio: parseFloat(pan.dataset.ratio), fx0: parseFloat(el.dataset.fx0 || .5),
      kind: el.dataset.fx, texts: $$('.scene__text p', el), vis: false, parts: [] };
  });
  function layoutScene(s) {
    const vw = innerWidth, vh = innerHeight;
    const Wd = Math.max(vw, vh * 1.28 * s.ratio), Hd = Wd / s.ratio;
    s.Wd = Wd; s.Hd = Hd; s.pan.style.width = Wd + 'px'; s.pan.style.height = Hd + 'px';
    s.cvs.width = vw; s.cvs.height = vh;
    s.parts = Array.from({ length: s.kind === 'embers' ? 70 : 55 }, () => ({
      x: Math.random() * vw, y: Math.random() * vh, r: Math.random() * 1.8 + .5, v: Math.random() * .5 + .15,
      sw: Math.random() * 6.28, a: Math.random() * .6 + .3
    }));
  }
  function updateScenes() {
    const vh = innerHeight, vw = innerWidth;
    for (const s of scenes) {
      const r = s.el.getBoundingClientRect();
      s.vis = r.bottom > 0 && r.top < vh;
      if (!s.vis) continue;
      const p = clamp(-r.top / (r.height - vh));
      const ease = p * p * (3 - 2 * p) * .6 + p * .4;
      s.pan.style.transform = `translate3d(${-(s.Wd - vw) * s.fx0}px,${-(s.Hd - vh) * ease}px,0)`;
      s.texts.forEach(t => {
        const a = +t.dataset.a, b = +t.dataset.b;
        const o = smooth(a, a + .12, p) * (1 - smooth(b, b + .12, p));
        t.style.opacity = o; t.style.transform = `translateY(${(1 - o) * 20}px)`;
      });
    }
  }
  function fxScenes(t) {
    for (const s of scenes) {
      if (!s.vis) continue;
      const c = s.c, w = s.cvs.width, h = s.cvs.height;
      c.clearRect(0, 0, w, h);
      for (const q of s.parts) {
        if (s.kind === 'embers') { q.y -= q.v; q.x += Math.sin(t / 1500 + q.sw) * .3; if (q.y < -5) { q.y = h + 5; q.x = Math.random() * w; } }
        else { q.y += q.v * .4; q.x += Math.sin(t / 2200 + q.sw) * .5 + .15; if (q.y > h + 5) { q.y = -5; q.x = Math.random() * w; } if (q.x > w + 5) q.x = -5; }
        const tw = .5 + .5 * Math.sin(t / 700 + q.sw);
        c.globalAlpha = q.a * (.4 + .6 * tw) * .8;
        c.fillStyle = s.kind === 'embers' ? '#ffcf8a' : '#ffffff';
        c.shadowColor = s.kind === 'embers' ? '#ff9a3c' : '#bfe0ff'; c.shadowBlur = 8;
        c.beginPath(); c.arc(q.x, q.y, q.r, 0, 6.283); c.fill();
      }
      c.shadowBlur = 0; c.globalAlpha = 1;
    }
  }
  /* ---------- Duo : deux décors en écran partagé ---------- */
  const duo = $('#duo');
  const duoParts = ['#duo-a', '#duo-b'].map(s => {
    const el = $(s), cvs = $('canvas', el), img = $('img', el);
    return { el, cvs, img, c: cvs.getContext('2d'), kind: cvs.dataset.kind, parts: [], vis: false };
  });
  const [dA, dB] = duoParts, line = $('#duo-line'), t1 = $('#duo-t1'), t2 = $('#duo-t2');
  const stacked = () => innerWidth <= 760;
  function layoutDuo() {
    for (const d of duoParts) {
      const w = d.el.offsetWidth, h = d.el.offsetHeight;
      d.cvs.width = w; d.cvs.height = h;
      d.parts = Array.from({ length: d.kind === 'embers' ? 45 : 35 }, () => ({ x: Math.random() * w, y: Math.random() * h, r: Math.random() * 1.8 + .5, v: Math.random() * .5 + .15, sw: Math.random() * 6.28, a: Math.random() * .6 + .3 }));
    }
  }
  function updateDuo() {
    const r = duo.getBoundingClientRect(), vh = innerHeight;
    dA.vis = dB.vis = r.bottom > 0 && r.top < vh;
    if (!dA.vis) return;
    const p = clamp(-r.top / (r.height - vh)), st = stacked();
    const ea = smooth(0, .2, p), eb = smooth(.46, .68, p);
    dA.el.style.transform = `translate3d(${-(1 - ea) * 101}%,0,0)`;
    dB.el.style.transform = `translate3d(${(1 - eb) * 101}%,0,0)`;
    const W = dA.el.offsetWidth, H = dA.el.offsetHeight;
    // balayage lent des images pendant tout le défilement
    dA.img.style.transform = `translate3d(${-p * .28 * W}px,${-p * .1 * H}px,0)`;
    dB.img.style.transform = `translate3d(${-p * .06 * W}px,${-(0.15 + p * .85) * .28 * H}px,0)`;
    const l = smooth(.04, .2, p) * (1 - smooth(.9, 1, p) * .6);
    line.style.opacity = l; line.style.transform = st ? `scaleX(${ea})` : `scaleY(${ea})`;
    const o1 = smooth(.14, .27, p) * (1 - smooth(.4, .5, p)), o2 = smooth(.64, .76, p) * (1 - smooth(.96, 1, p));
    t1.style.opacity = o1; t1.style.transform = `translateY(${(1 - o1) * 22}px)`;
    t2.style.opacity = o2; t2.style.transform = `translateY(${(1 - o2) * 22}px)`;
  }
  function fxDuo(t) {
    for (const d of duoParts) {
      if (!d.vis) continue;
      const c = d.c, w = d.cvs.width, h = d.cvs.height; c.clearRect(0, 0, w, h);
      for (const q of d.parts) {
        if (d.kind === 'embers') { q.y -= q.v; q.x += Math.sin(t / 1500 + q.sw) * .3; if (q.y < -5) { q.y = h + 5; q.x = Math.random() * w; } }
        else { q.y += q.v * .4; q.x += Math.sin(t / 2200 + q.sw) * .5 + .15; if (q.y > h + 5) { q.y = -5; q.x = Math.random() * w; } if (q.x > w + 5) q.x = -5; }
        c.globalAlpha = q.a * (.4 + .6 * (.5 + .5 * Math.sin(t / 700 + q.sw))) * .8;
        c.fillStyle = d.kind === 'embers' ? '#ffcf8a' : '#ffffff'; c.shadowColor = d.kind === 'embers' ? '#ff9a3c' : '#bfe0ff'; c.shadowBlur = 8;
        c.beginPath(); c.arc(q.x, q.y, q.r, 0, 6.283); c.fill();
      }
      c.shadowBlur = 0; c.globalAlpha = 1;
    }
  }
  layoutDuo();
  addEventListener('resize', () => { layoutDuo(); updateDuo(); });
  if (!reduce) (function dloop(t) { fxDuo(t); requestAnimationFrame(dloop); })(0);
  scenes.forEach(layoutScene);
  addEventListener('resize', () => { scenes.forEach(layoutScene); updateScenes(); });

  let tick = false;
  addEventListener('scroll', () => {
    vel = clamp(window.scrollY - lastY, -90, 90) * .6 + vel * .4; lastY = scrollY = window.scrollY;
    if (tick) return; tick = true;
    requestAnimationFrame(() => {
      const h = document.documentElement.scrollHeight - innerHeight;
      bar.style.width = (h > 0 ? scrollY / h * 100 : 0) + '%';
      updateScenes(); updateDuo();
      if (reduce) draw(0, 16);
      tick = false;
    });
  }, { passive: true });
  updateScenes(); updateDuo();
  if (!reduce) (function sloop(t) { fxScenes(t); requestAnimationFrame(sloop); })(0);

  /* ---------- Apparition au scroll ---------- */
  const revObs = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('in'); revObs.unobserve(e.target); }
  }), { threshold: .12, rootMargin: '0px 0px -6% 0px' });
  $$('.reveal').forEach(el => revObs.observe(el));

  /* ---------- Décryptage du texte ---------- */
  const GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/<>';
  function decode(el, final, dur = 900) {
    if (reduce) { el.textContent = final; return; }
    const t0 = performance.now();
    (function step(now) {
      const p = Math.min(1, (now - t0) / dur), keep = Math.floor(final.length * p);
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

  /* ---------- Logo : inclinaison à la souris ---------- */
  const logo = $('#logo');
  if (!reduce && matchMedia('(hover: hover)').matches) {
    addEventListener('pointermove', e => {
      if (scrollY > innerHeight) return;
      const x = e.clientX / innerWidth - .5, y = e.clientY / innerHeight - .5;
      logo.style.transform = `perspective(900px) rotateY(${x * 7}deg) rotateX(${-y * 5}deg) translate3d(${x * -10}px,${y * -6}px,0)`;
    }, { passive: true });
  }

  /* ---------- Couverture : 3D + bascule ---------- */
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
  const cimg = $('#cover-img'), ccap = $('#cover-cap');
  $$('.switch button').forEach(b => b.addEventListener('click', () => {
    if (b.classList.contains('on')) return;
    $$('.switch button').forEach(x => { x.classList.toggle('on', x === b); x.setAttribute('aria-pressed', x === b); });
    cimg.classList.add('fade');
    setTimeout(() => {
      cimg.src = b.dataset.src; cimg.alt = b.dataset.alt; ccap.textContent = b.dataset.cap;
      cimg.onload = () => cimg.classList.remove('fade'); setTimeout(() => cimg.classList.remove('fade'), 600);
    }, 250);
  }));

  /* ---------- Orbite → carte auteur ---------- */
  $$('.orbit a, .orbit__core').forEach(a => a.addEventListener('click', () => {
    const t = $(a.getAttribute('href')); if (!t) return;
    t.classList.remove('flash'); void t.offsetWidth; t.classList.add('flash');
  }));

  /* ---------- Carnet + agrandissement ---------- */
  const cn = JSON.parse($('#cn-data').textContent), cnImg = $('#cn-img'), cnCap = $('#cn-cap');
  const tabs = $$('.cn__tab'), lb = $('#lb');
  let cur = 0;
  function show(i) {
    cur = (i + cn.length) % cn.length;
    tabs.forEach((t, k) => { t.classList.toggle('on', k === cur); t.setAttribute('aria-selected', k === cur); });
    cnImg.classList.add('fade');
    setTimeout(() => {
      cnImg.src = cn[cur].src; cnImg.alt = cn[cur].a;
      cnCap.innerHTML = ''; const b = document.createElement('b'); b.textContent = cn[cur].t;
      cnCap.append(b, cn[cur].c);
      cnImg.onload = () => cnImg.classList.remove('fade'); setTimeout(() => cnImg.classList.remove('fade'), 500);
    }, 200);
  }
  tabs.forEach((t, k) => {
    t.addEventListener('click', () => show(k));
    t.addEventListener('keydown', e => {
      if (e.key === 'ArrowDown' || e.key === 'ArrowRight') { e.preventDefault(); show(cur + 1); tabs[cur].focus(); }
      if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') { e.preventDefault(); show(cur - 1); tabs[cur].focus(); }
    });
  });
  $('#cn-open').addEventListener('click', () => {
    $('#lb-img').src = cn[cur].src; $('#lb-img').alt = cn[cur].a;
    if (lb.showModal) lb.showModal(); else lb.setAttribute('open', '');
  });
  $('#lb-x').addEventListener('click', () => lb.close());
  lb.addEventListener('click', e => { if (e.target === lb || e.target.id === 'lb-img') lb.close(); });

  /* ---------- Extrait WeStory en fenêtre ---------- */
  const ex = $('#ex'), frame = $('#ex-frame');
  $$('[data-open=excerpt]').forEach(b => b.addEventListener('click', () => {
    if (!frame.getAttribute('src')) frame.src = frame.dataset.src;
    if (ex.showModal) ex.showModal(); else ex.setAttribute('open', '');
  }));
  $('#ex-x').addEventListener('click', () => ex.close());
  ex.addEventListener('click', e => { if (e.target === ex) ex.close(); });

  /* ---------- Ambiance sonore (synthèse Web Audio, aucun fichier) ---------- */
  const snd = $('#snd');
  let ac = null, master = null, started = false, enabled = store.get('milleans-sound') !== 'off';
  let nextLoop = 0.3, sched = 0;
  function buses(ctx, out) {
    const len = ctx.sampleRate * 4.5, ir = ctx.createBuffer(2, len, ctx.sampleRate);
    for (let c = 0; c < 2; c++) { const d = ir.getChannelData(c); for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 2.4); }
    const rev = ctx.createConvolver(); rev.buffer = ir;
    const wet = ctx.createGain(); wet.gain.value = 1; wet.connect(rev);
    const revOut = ctx.createGain(); revOut.gain.value = .9; rev.connect(revOut); revOut.connect(out);
    const dry = ctx.createGain(); dry.gain.value = 1; dry.connect(out);
    wet.connect(out); wet.gain.value = .7;
    const echo = ctx.createGain(); echo.connect(dry); echo.connect(rev);
    const dl = ctx.createDelay(2); dl.delayTime.value = .62; const fb = ctx.createGain(); fb.gain.value = .38;
    echo.connect(dl); dl.connect(fb); fb.connect(dl); dl.connect(rev); dl.connect(out);
    return { dry, wet, echo };
  }
  function build() {
    const AC = window.AudioContext || window.webkitAudioContext; if (!AC || !window.MilleMusic) return false;
    ac = new AC(); master = ac.createGain(); master.gain.value = 0;
    const comp = ac.createDynamicsCompressor(); comp.threshold.value = -18; comp.ratio.value = 3;
    master.connect(comp); comp.connect(ac.destination);
    const b = buses(ac, master);
    nextLoop = ac.currentTime + .4;
    const tick = () => {
      if (ac.currentTime > nextLoop - 12) { window.MilleMusic.schedule(ac, b, nextLoop); nextLoop += window.MilleMusic.LOOP; }
    };
    tick(); sched = setInterval(tick, 2000);
    return true;
  }
  function fadeTo(v, s) { master.gain.cancelScheduledValues(ac.currentTime); master.gain.setValueAtTime(master.gain.value, ac.currentTime); master.gain.linearRampToValueAtTime(v, ac.currentTime + s); }
  async function soundOn() {
    if (!started) { if (!build()) { snd.hidden = true; return; } started = true; }
    try { await ac.resume(); } catch (e) { /* ignoré */ }
    fadeTo(.8, 4); enabled = true; snd.classList.add('on'); snd.classList.remove('wait'); snd.setAttribute('aria-pressed', 'true'); store.set('milleans-sound', 'on');
  }
  function soundOff() {
    enabled = false; snd.classList.remove('on', 'wait'); snd.setAttribute('aria-pressed', 'false'); store.set('milleans-sound', 'off');
    if (ac) { fadeTo(0, .6); setTimeout(() => { if (!enabled) ac.suspend(); }, 700); }
  }
  snd.addEventListener('click', e => { e.stopPropagation(); snd.classList.contains('on') ? soundOff() : soundOn(); });
  if (enabled) {
    snd.classList.add('wait'); snd.title = 'Cliquez ou touchez la page pour lancer l’ambiance sonore';
    const first = e => {
      removeEventListener('pointerdown', first); removeEventListener('keydown', first);
      if (e.target.closest && e.target.closest('#snd')) return;
      if (enabled && !started) soundOn();
    };
    addEventListener('pointerdown', first); addEventListener('keydown', first);
  }
  document.addEventListener('visibilitychange', () => {
    if (!ac || !enabled || !started) return;
    if (document.hidden) { fadeTo(0, .3); setTimeout(() => ac.suspend(), 350); } else { ac.resume(); fadeTo(.8, 1.5); }
  });
})();
