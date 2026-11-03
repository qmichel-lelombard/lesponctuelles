// Collecte d'audience anonyme : pas de cookie, IP jamais stockée.
// Le visiteur est identifié par une empreinte du jour (IP + navigateur + date), illisible et renouvelée chaque jour.
import { createHash } from 'node:crypto';
import { getStore } from '@netlify/blobs';

const BOTS = /bot|crawl|spider|slurp|preview|headless|lighthouse|facebookexternalhit|embedly|whatsapp|pingdom|uptime/i;
// « | » sépare les champs de la clé, « / » et « % » y sont interprétés : on les neutralise
const clean = (s, n = 80) => String(s || '').replace(/[|/%\s]+/g, ' ').trim().slice(0, n);

const hash = s => createHash('sha256').update(s).digest('hex').slice(0, 12);

export default async (req, context) => {
  if (req.method !== 'POST') return new Response('', { status: 405 });
  const ua = req.headers.get('user-agent') || '';
  if (BOTS.test(ua)) return new Response('ok', { status: 202 });
  let d;
  try { d = JSON.parse(await req.text()); } catch { return new Response('', { status: 400 }); }
  const t = { v: 'v', c: 'c', s: 's' }[d?.t];
  if (!t) return new Response('', { status: 400 });

  const now = new Date(), day = now.toISOString().slice(0, 10);
  const vis = hash(day + (Netlify.env.get('STATS_SALT') || 'mille-ans') + context.ip + ua);
  const dev = /mobi|android|iphone/i.test(ua) ? 'm' : /ipad|tablet/i.test(ua) ? 't' : 'd';
  const country = context.geo?.country?.code || '';
  const id = now.getTime().toString(36) + Math.random().toString(36).slice(2, 6);
  // tout l'événement tient dans la clé : la lecture se fait par simple listage
  const key = `${day}/${id}|${t}|${vis}|${dev}|${country}|${clean(d.r, 60)}|${clean(d.l)}`;
  await getStore('stats').set(key, '');
  return new Response('ok', { status: 202 });
};

export const config = { path: '/api/t' };
