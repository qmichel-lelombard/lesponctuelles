// Données de la page d'administration : GET /api/stats (en-tête x-admin-token) ; ?format=csv pour l'export des inscrits.
// Accès = jeton (dans l'adresse) ET mot de passe. Seuls leurs empreintes sont dans le code : SHA-256 du jeton, scrypt (salé) du mot de passe.
import { getStore } from "@netlify/blobs";
import { createHash, scryptSync, timingSafeEqual } from "node:crypto";

const TOKEN_SHA256 = "8529c84f015e5a85479542f042aa4990a0043acb16c8f9ba51eb5390b2b321d1";

const PASSWORD_SCRYPT = "1d48500a36de08180309fd62b5728b26:23110784127c2bdfa0c883d163824eb585617a9a20c0dc0362fea3446a868a9d"; // sel:empreinte

const authorized = (req) => {
  const token = createHash("sha256").update(req.headers.get("x-admin-token") || "").digest();
  const [salt, hash] = PASSWORD_SCRYPT.split(":");
  const pw = scryptSync(req.headers.get("x-admin-password") || "", salt, 32);
  // les deux comparaisons sont toujours faites (pas de sortie anticipée)
  const okToken = timingSafeEqual(token, Buffer.from(TOKEN_SHA256, "hex"));
  const okPw = timingSafeEqual(pw, Buffer.from(hash, "hex"));
  return okToken && okPw;
};

async function keys(store, prefix) {
  const out = [];
  for await (const page of store.list({ prefix, paginate: true })) for (const b of page.blobs) out.push(b.key);
  return out;
}

const csvCell = (v) => '"' + String(v).replace(/"/g, '""') + '"';

export default async (req) => {
  if (!authorized(req)) {
    await new Promise((r) => setTimeout(r, 800)); // freine les essais répétés
    return new Response(JSON.stringify({ error: "unauthorized" }), { status: 401, headers: { "content-type": "application/json" } });
  }
  const store = getStore({ name: "quiz", consistency: "strong" });
  const url = new URL(req.url);

  // Inscrits
  const subKeys = (await keys(store, "sub/")).slice(0, 10000);
  const subs = [];
  for (let i = 0; i < subKeys.length; i += 25) {
    const batch = await Promise.all(subKeys.slice(i, i + 25).map((k) => store.get(k, { type: "json" })));
    subs.push(...batch.filter(Boolean));
  }
  subs.sort((a, b) => (a.at < b.at ? 1 : -1));

  if (url.searchParams.get("format") === "csv") {
    const rows = ["prenom,email,date", ...subs.map((s) => [s.prenom, s.email, s.at].map(csvCell).join(","))];
    return new Response("﻿" + rows.join("\r\n"), {
      headers: { "content-type": "text/csv; charset=utf-8", "content-disposition": 'attachment; filename="inscrits-quiz-ducobu.csv"', "cache-control": "no-store" },
    });
  }

  // Parties et clics (on ne lit que les clés, pas les valeurs)
  const [starts, finishes, clicks] = await Promise.all([keys(store, "start/"), keys(store, "finish/"), keys(store, "click/")]);
  const byDay = {};
  const day = (d) => (byDay[d] ||= { starts: 0, finishes: 0, subs: 0 });
  starts.forEach((k) => day(k.split("/")[1]).starts++);
  const scores = Array(11).fill(0);
  finishes.forEach((k) => { const [, s, d] = k.split("/"); scores[+s]++; day(d).finishes++; });
  const clickTotals = {};
  clicks.forEach((k) => { const l = k.split("/")[1]; clickTotals[l] = (clickTotals[l] || 0) + 1; });
  subs.forEach((s) => day(new Date(s.at).toLocaleDateString("sv-SE", { timeZone: "Europe/Brussels" })).subs++);

  return new Response(JSON.stringify({
    starts: starts.length, finishes: finishes.length, scores, clicks: clickTotals,
    days: Object.entries(byDay).sort().reverse().slice(0, 30).map(([d, v]) => ({ day: d, ...v })),
    subscribers: subs, generatedAt: new Date().toISOString(),
  }), { headers: { "content-type": "application/json", "cache-control": "no-store" } });
};

export const config = { path: "/api/stats" };
