// Statistiques agrégées pour la page d'administration (protégée par mot de passe : variable ADMIN_PASSWORD).
import { createHash, timingSafeEqual } from "node:crypto";
import { connectLambda, getStore } from "@netlify/blobs";

const H = { "Content-Type": "application/json", "Cache-Control": "no-store", "X-Robots-Tag": "noindex" };
const sha = (s) => createHash("sha256").update(String(s)).digest();

export const handler = async (event) => {
  if (event.httpMethod !== "POST") return { statusCode: 405, headers: H, body: "{}" };
  let b; try { b = JSON.parse(event.body || "{}"); } catch { b = {}; }
  const expected = process.env.ADMIN_PASSWORD;
  if (!expected || !timingSafeEqual(sha(b.password || ""), sha(expected))) {
    await new Promise((r) => setTimeout(r, 800));                      // freine les essais répétés
    return { statusCode: 401, headers: H, body: JSON.stringify({ error: "Mot de passe incorrect" }) };
  }
  connectLambda(event);
  const store = getStore("elles-stats");
  const days = {}, totals = { start: 0, complete: 0, sharedview: 0 }, results = {}, clicks = {}, hours = Array(24).fill(0);
  for await (const page of store.list({ prefix: "e/", paginate: true })) {
    for (const { key } of page.blobs) {
      const [, day, type, detail, hour] = key.split("/");
      const d = (days[day] ||= { start: 0, complete: 0, click: 0, sharedview: 0 });
      d[type] = (d[type] || 0) + 1;
      if (type === "click") clicks[detail] = (clicks[detail] || 0) + 1; else totals[type] = (totals[type] || 0) + 1;
      if (type === "complete") results[detail] = (results[detail] || 0) + 1;
      if (type === "start") hours[Number(hour) || 0]++;
    }
  }
  return { statusCode: 200, headers: H, body: JSON.stringify({ totals, results, clicks, days, hours, generatedAt: new Date().toISOString() }) };
};
