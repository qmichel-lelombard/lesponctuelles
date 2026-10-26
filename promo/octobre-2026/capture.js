// Rendu image par image de promo.html puis encodage MP4 (H.264) avec la bande-son.
// usage : node capture.js [h|v] [fps] [--preview t1,t2,...]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

(async () => {
  const format = process.argv[2] || 'h';
  const fps = +(process.argv[3] || 30);
  const pi = process.argv.indexOf('--preview');
  const preview = pi > 0 ? process.argv[pi + 1].split(',').map(Number) : null;
  const W = format === 'v' ? 1080 : 1920, H = format === 'v' ? 1920 : 1080;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  page.on('console', m => console.log('[page]', m.text()));
  page.on('pageerror', e => console.error('[pageerror]', e));
  await page.goto('file://' + path.resolve(__dirname, 'promo.html') + `?capture=1&format=${format}`);
  await page.evaluate(() => window.ready);
  if (preview) {
    for (const t of preview) {
      await page.evaluate(t => render(t), t);
      await page.screenshot({ path: path.resolve(__dirname, `out/preview-${format}-${t}.jpg`), quality: 85, type: 'jpeg' });
    }
    await browser.close(); return;
  }
  const dur = await page.evaluate(() => window.DURATION);
  const n = Math.round(dur * fps);
  const out = path.resolve(__dirname, `out/lombard-octobre-2026-${format === 'v' ? '1080x1920' : '1920x1080'}.mp4`);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    '-i', path.resolve(__dirname, 'out/soundtrack.wav'),
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
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
