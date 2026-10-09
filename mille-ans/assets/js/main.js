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
  /* ---------- Duo : transition prismatique (WebGL) entre deux décors ---------- */
  const duo = $('#duo'), glc = $('#duo-gl'), t1 = $('#duo-t1'), t2 = $('#duo-t2');
  const fbA = $('#fb-a'), fbB = $('#fb-b');
  let gl = null, prog = null, U = {}, texA = null, texB = null, ready = 0, dP = 0, dVis = false;
  const VS = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
  const FS = `precision highp float;
uniform sampler2D A,B;uniform vec2 R;uniform vec2 IA;uniform float P,T,FA,FB,ZA,ZB;
float h(float n){return fract(sin(n*91.345)*47453.5453);}
vec2 cov(vec2 uv,vec2 im,float fy,float z){float ra=R.x/R.y,ia=im.x/im.y;vec2 s=ra>ia?vec2(1.,ia/ra):vec2(ra/ia,1.);s*=z;vec2 o=(1.-s)*vec2(.5,fy);return uv*s+o;}
vec3 pal(float t){return .5+.5*cos(6.2831*(t+vec3(0.,.33,.67)));}
vec3 smp(vec2 uv,float k){ /* k : 0 = A, 1 = B */
  vec3 a=texture2D(A,cov(uv,vec2(1500.,1469.),FA,ZA)).rgb;
  vec3 b=texture2D(B,cov(uv,vec2(1450.,1933.),FB,ZB)).rgb;
  return mix(a,b,k);}
void main(){
  vec2 uv=gl_FragCoord.xy/R;
  float W=.2, front=P*(1.+2.*W)-W;                     /* le front va de gauche à droite */
  float row=floor(uv.y*34.);
  float jag=(h(row+floor(T*6.))-.5)*.10*sin(3.14159*clamp(P,0.,1.));
  float d=uv.x-front+jag;                               /* <0 : derrière le front */
  float band=1.-smoothstep(0.,W,abs(d));                /* profil de la bande de verre */
  band=band*band*(3.-2.*band);
  float amp=band*sin(3.14159*clamp(P,0.,1.));
  /* réfraction : décalage horizontal + vertical onduleux */
  vec2 off=vec2(sin(uv.y*26.+T*3.)*.035+ (uv.x-front)*.25,cos(uv.y*18.-T*2.)*.012)*amp;
  /* traînées : étirement horizontal par bandes de lignes */
  float sm=step(.72,h(row*1.7+floor(T*4.)))*amp*(.8+.2*sin(T));
  vec2 uvs=vec2(mix(uv.x,front-jag,sm*.85),uv.y);
  /* séparation chromatique */
  float ca=.022*amp;
  float kr=step(0.,-(uvs.x+off.x+ca-front+jag)), kg=step(0.,-(uvs.x+off.x-front+jag)), kb=step(0.,-(uvs.x+off.x-ca-front+jag));
  float r=smp(uvs+off+vec2(ca,0.),kr).r;
  float g=smp(uvs+off,kg).g;
  float b=smp(uvs+off-vec2(ca,0.),kb).b;
  vec3 col=vec3(r,g,b);
  /* éclat irisé du prisme */
  vec3 rain=pal(d*5.+uv.y*.6+T*.15);
  col=mix(col,col+rain*.65,band*.75*amp*1.6);
  col+=vec3(.55,.8,1.)*pow(band,5.)*amp*.9;             /* arête lumineuse */
  /* bloc glitch final */
  float gb=step(.9,h(row*3.1+floor(T*9.)))*smoothstep(0.,.35,band)*amp;
  col=mix(col,smp(vec2(fract(uv.x*1.15+h(row)),uv.y),1.),gb*.7);
  gl_FragColor=vec4(col,1.);
}`;
  function glInit() {
    try { gl = glc.getContext('webgl', { antialias: false, alpha: false, powerPreference: 'low-power' }); } catch (e) { gl = null; }
    if (!gl) return false;
    const sh = (ty, src) => { const s = gl.createShader(ty); gl.shaderSource(s, src); gl.compileShader(s); return gl.getShaderParameter(s, gl.COMPILE_STATUS) ? s : null; };
    const vs = sh(gl.VERTEX_SHADER, VS), fs = sh(gl.FRAGMENT_SHADER, FS);
    if (!vs || !fs) { gl = null; return false; }
    prog = gl.createProgram(); gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) { gl = null; return false; }
    gl.useProgram(prog);
    const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(prog, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    ['A', 'B', 'R', 'IA', 'P', 'T', 'FA', 'FB', 'ZA', 'ZB'].forEach(n => U[n] = gl.getUniformLocation(prog, n));
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
    const load = (img, unit, key) => {
      const go = () => {
        const tex = gl.createTexture(); gl.activeTexture(gl.TEXTURE0 + unit); gl.bindTexture(gl.TEXTURE_2D, tex);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, img);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        gl.uniform1i(U[key], unit); ready++; if (ready === 2) { duo.classList.add('gl'); drawDuo(performance.now()); }
      };
      img.complete && img.naturalWidth ? go() : img.addEventListener('load', go, { once: true });
    };
    load(fbA, 0, 'A'); load(fbB, 1, 'B');
    return true;
  }
  function sizeDuo() {
    if (!gl) return;
    const d = Math.min(devicePixelRatio || 1, 1.5);
    const w = Math.round(glc.clientWidth * d), h = Math.round(glc.clientHeight * d);
    if (glc.width !== w || glc.height !== h) { glc.width = w; glc.height = h; gl.viewport(0, 0, w, h); }
  }
  function drawDuo(t) {
    if (!gl || ready < 2) return;
    sizeDuo();
    const p = dP, pa = clamp(p / .5), pb = clamp((p - .5) / .5);
    gl.uniform2f(U.R, glc.width, glc.height);
    gl.uniform1f(U.P, smooth(.36, .64, p) * 1.0);
    gl.uniform1f(U.T, t / 1000);
    const portrait = innerWidth < innerHeight;
    gl.uniform1f(U.FA, portrait ? .55 - pa * .25 : .75 - pa * .5);       /* balayage vertical de l'orange */
    gl.uniform1f(U.FB, portrait ? .85 - pb * .6 : .95 - pb * .75);       /* de la tour vers l'astronaute */
    gl.uniform1f(U.ZA, 1 - .08 * pa); gl.uniform1f(U.ZB, .92 + .08 * pb);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  }
  function updateDuo() {
    const r = duo.getBoundingClientRect(), vh = innerHeight;
    dVis = r.bottom > 0 && r.top < vh;
    if (!dVis) return;
    dP = clamp(-r.top / (r.height - vh));
    const o1 = smooth(.04, .16, dP) * (1 - smooth(.3, .4, dP)), o2 = smooth(.62, .74, dP) * (1 - smooth(.96, 1, dP));
    t1.style.opacity = o1; t1.style.transform = `translateY(${(1 - o1) * 22}px)`;
    t2.style.opacity = o2; t2.style.transform = `translateY(${(1 - o2) * 22}px)`;
    if (!gl) { const e = smooth(.36, .64, dP); fbB.style.opacity = e; fbA.style.opacity = 1 - e * .6; }
    else drawDuo(performance.now());
  }
  glInit();
  addEventListener('resize', () => { sizeDuo(); updateDuo(); });
  if (!reduce) (function dloop(t) { if (dVis && gl && dP > .3 && dP < .7) drawDuo(t); requestAnimationFrame(dloop); })(0);
  const earth = $('#earth'), earthIn = $('.earth__in', earth);
  function updateEarth() {
    const r = earth.getBoundingClientRect(), vh = innerHeight;
    if (r.bottom < 0 || r.top > vh) return;
    const k = clamp((vh - r.top) / (vh + r.height));
    earthIn.style.transform = `translate3d(0,${((.5 - k) * 70).toFixed(1)}px,0) scale(${(1.04 + k * .06).toFixed(3)})`;
  }
  scenes.forEach(layoutScene);
  addEventListener('resize', () => { scenes.forEach(layoutScene); updateScenes(); });

  let tick = false;
  addEventListener('scroll', () => {
    vel = clamp(window.scrollY - lastY, -90, 90) * .6 + vel * .4; lastY = scrollY = window.scrollY;
    if (tick) return; tick = true;
    requestAnimationFrame(() => {
      const h = document.documentElement.scrollHeight - innerHeight;
      bar.style.width = (h > 0 ? scrollY / h * 100 : 0) + '%';
      updateScenes(); updateDuo(); updateEarth();
      if (reduce) draw(0, 16);
      tick = false;
    });
  }, { passive: true });
  updateScenes(); updateDuo(); updateEarth();
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
