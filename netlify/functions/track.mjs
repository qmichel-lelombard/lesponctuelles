// Suivi anonyme du quiz : POST /api/track
// Chaque évènement = une clé dans Netlify Blobs (pas de compteur partagé, donc pas de conflit d'écriture).
//   start/<jour>/<id>            partie lancée
//   finish/<score>/<jour>/<id>   partie terminée
//   click/<lien>/<jour>/<id>     clic sur un lien
//   sub/<hash e-mail>            inscription au tirage (prénom, e-mail, date)
import { getStore } from "@netlify/blobs";
import { createHash, randomUUID } from "node:crypto";

const LINKS = new Set(["brand", "decouvrir", "jeux", "film", "partage"]);
const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { "content-type": "application/json", "cache-control": "no-store" } });

export default async (req) => {
  if (req.method !== "POST") return json({ error: "method" }, 405);
  let b;
  try { b = await req.json(); } catch { return json({ error: "json" }, 400); }
  if (!b || typeof b !== "object") return json({ error: "body" }, 400);

  const store = getStore({ name: "quiz", consistency: "strong" });
  const day = new Date().toLocaleDateString("sv-SE", { timeZone: "Europe/Brussels" });
  const id = `${Date.now()}-${randomUUID().slice(0, 8)}`;

  switch (b.type) {
    case "start":
      await store.set(`start/${day}/${id}`, "1");
      break;
    case "finish": {
      const score = Number(b.score);
      if (!Number.isInteger(score) || score < 0 || score > 10) return json({ error: "score" }, 400);
      await store.set(`finish/${score}/${day}/${id}`, "1");
      break;
    }
    case "click":
      if (!LINKS.has(b.link)) return json({ error: "link" }, 400);
      await store.set(`click/${b.link}/${day}/${id}`, "1");
      break;
    case "subscribe": {
      const email = String(b.email || "").trim().toLowerCase();
      const prenom = String(b.prenom || "").trim().slice(0, 60);
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]{2,}$/.test(email) || email.length > 120 || !prenom) return json({ error: "fields" }, 400);
      const key = `sub/${createHash("sha256").update(email).digest("hex").slice(0, 32)}`;
      if (!(await store.get(key))) await store.setJSON(key, { prenom, email, at: new Date().toISOString() });
      break;
    }
    default:
      return json({ error: "type" }, 400);
  }
  return json({ ok: true });
};

export const config = { path: "/api/track" };
