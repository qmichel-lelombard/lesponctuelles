// Rendu image par image de promo.html puis encodage MP4 (H.264) avec la bande-son.
// usage : node capture.js <mois, ex. 2026-11> [h|v|p] [fps] [--slot 6] [--preview t1,t2,...] [--still]
//   --still : seulement l'image de fin en PNG (out/fin-<mois>-<LxH>.png)
// (générer d'abord la bande-son : python3 soundtrack.py <mois> [temps par album])
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

(async () => {
  const month = process.argv[2] || '2026-10';
  const format = process.argv[3] || 'h';
  const fps = +(process.argv[4] || 30);
  const si = process.argv.indexOf('--slot');
  const slot = si > 0 ? +process.argv[si + 1] : 4;
  const sfx = slot === 4 ? '' : `-long`;
  const pi = process.argv.indexOf('--preview');
  const preview = pi > 0 ? process.argv[pi + 1].split(',').map(Number) : null;
  const W = format === 'h' ? 1920 : 1080, H = { h: 1080, v: 1920, p: 1440 }[format];
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  page.on('console', m => console.log('[page]', m.text()));
  page.on('pageerror', e => console.error('[pageerror]', e));
  await page.goto('file://' + path.resolve(__dirname, 'promo.html') + `?capture=1&month=${month}&format=${format}&slot=${slot}`);
  await page.evaluate(() => window.ready);
  if (process.argv.includes('--still')) {
    const t = await page.evaluate(() => window.DURATION - 1 / 30);
    await page.evaluate(t => render(t), t);
    const name = await page.evaluate(() => `${MONTH}-${M.year}`);
    await page.screenshot({ path: path.resolve(__dirname, `out/fin-${name}-${W}x${H}.png`), type: 'png' });
    await browser.close(); return;
  }
  if (preview) {
    for (const t of preview) {
      await page.evaluate(t => render(t), t);
      await page.screenshot({ path: path.resolve(__dirname, `out/preview-${month}${sfx}-${format}-${t}.jpg`), quality: 85, type: 'jpeg' });
    }
    await browser.close(); return;
  }
  const dur = await page.evaluate(() => window.DURATION);
  const n = Math.round(dur * fps);
  const name = await page.evaluate(() => `${MONTH}-${M.year}`);
  const out = path.resolve(__dirname, `out/lombard-${name}${sfx}-${W}x${H}.mp4`);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    '-i', path.resolve(__dirname, `out/soundtrack-${month}${sfx}.wav`),
    '-c:v', 'libx264', '-preset', 'slow', '-b:v', '14M', '-maxrate', '18M', '-bufsize', '28M', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
    '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = 0; f < n; f++) {
    await page.evaluate(t => render(t), f / fps);
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 60 === 0) process.stdout.write(`frame ${f}/${n}\n`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('OK', out);
})();
