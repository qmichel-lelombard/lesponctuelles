// Statistiques agrégées pour la page /admin/ (protégée par la variable d'environnement ADMIN_KEY).
import { getStore } from '@netlify/blobs';

const json = (o, status = 200) => new Response(JSON.stringify(o), {
  status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex' },
});
const inc = (o, k, n = 1) => { o[k] = (o[k] || 0) + n; };

export default async req => {
  const key = Netlify.env.get('ADMIN_KEY');
  if (!key || req.headers.get('x-admin-key') !== key) return json({ error: 'unauthorized' }, 401);

  const url = new URL(req.url);
  const to = url.searchParams.get('to') || new Date().toISOString().slice(0, 10);
  const from = url.searchParams.get('from') || '2000-01-01';
  // un listage par mois couvert par la période
  const months = new Set();
  for (let d = new Date(from < '2026-01-01' ? '2026-01-01' : from); d.toISOString().slice(0, 10) <= to; d.setUTCDate(d.getUTCDate() + 1)) months.add(d.toISOString().slice(0, 7));
  const store = getStore('stats');
  const keys = [];
  for (const m of months) keys.push(...(await store.list({ prefix: m })).blobs.map(b => b.key));

  const days = {}, clicks = {}, refs = {}, devices = {}, countries = {}, sections = {};
  const visits = new Set();
  for (const k of keys) {
    const day = k.slice(0, 10);
    if (day < from || day > to) continue;
    const [, t, vis, dev, country, ref, label] = k.split('|');
    const v = day + vis, dd = days[day] ||= { views: 0, clicks: 0, visits: new Set() };
    if (t === 'v') {
      dd.views++;
      if (!visits.has(v)) { inc(devices, dev); inc(countries, country || '?'); }
      visits.add(v); dd.visits.add(v);
      inc(refs, ref || 'Accès direct');
    } else if (t === 'c') { dd.clicks++; inc(clicks, label); }
    else if (t === 's') { (sections[label] ||= new Set()).add(v); }
  }
  const series = Object.keys(days).sort().map(d => ({ day: d, visits: days[d].visits.size, views: days[d].views, clicks: days[d].clicks }));
  return json({
    from, to, series,
    totals: { visits: visits.size, views: series.reduce((a, s) => a + s.views, 0), clicks: series.reduce((a, s) => a + s.clicks, 0) },
    clicks, refs, devices, countries,
    sections: Object.fromEntries(Object.entries(sections).map(([s, set]) => [s, set.size])),
  });
};

export const config = { path: '/api/stats' };
