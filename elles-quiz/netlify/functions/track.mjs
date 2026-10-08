// Enregistre un évènement anonyme (aucun cookie, aucune IP, aucune donnée personnelle).
import { connectLambda, getStore } from "@netlify/blobs";

const RESULTS = ["rose", "blonde", "brune", "violette", "verte", "bleue"];
const CLICKS = ["buy", "book", "share", "card", "again", "series"];
const ALLOWED = { start: [""], complete: RESULTS, sharedview: RESULTS, click: CLICKS };
const H = { "Cache-Control": "no-store" };

export const handler = async (event) => {
  if (event.httpMethod !== "POST") return { statusCode: 405, headers: H, body: "" };
  let b; try { b = JSON.parse(event.body || "{}"); } catch { return { statusCode: 400, headers: H, body: "" }; }
  const type = String(b.type || ""), detail = String(b.detail || "");
  if (!ALLOWED[type] || !ALLOWED[type].includes(type === "start" ? "" : detail)) return { statusCode: 400, headers: H, body: "" };
  connectLambda(event);
  const store = getStore("elles-stats");
  const day = new Date().toLocaleDateString("sv-SE", { timeZone: "Europe/Paris" });
  const hour = new Date().toLocaleTimeString("fr-FR", { timeZone: "Europe/Paris", hour: "2-digit" }).slice(0, 2);
  const key = `e/${day}/${type}/${detail || "-"}/${hour}/${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  await store.set(key, "1");
  return { statusCode: 204, headers: H, body: "" };
};
