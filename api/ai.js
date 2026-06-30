// onboard-kit — optional AI personalization (Vercel serverless function).
// Model toggle: "flash" (default), "pro", "minimax". One NVIDIA_API_KEY powers
// all three (optional per-model overrides). Deterministic pack is the default;
// this only adds a welcome paragraph + Day-1 tip. Key stays server-side only.

const ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions";
const MODELS = {
  flash:   { id: "deepseek-ai/deepseek-v4-flash", keys: ["NVIDIA_API_KEY_FLASH", "NVIDIA_API_KEY"], extra: { chat_template_kwargs: { thinking: false } } },
  pro:     { id: "deepseek-ai/deepseek-v4-pro",   keys: ["NVIDIA_API_KEY_PRO", "NVIDIA_API_KEY"],   extra: { chat_template_kwargs: { thinking: false } } },
  minimax: { id: "minimaxai/minimax-m3",          keys: ["NVIDIA_API_KEY_MINIMAX", "NVIDIA_API_KEY"], extra: {} },
};
const cfgFor = (m) => MODELS[m] || MODELS.flash;
const keyFor = (c) => { for (const e of c.keys) { if (process.env[e]) return process.env[e]; } return null; };
async function readBody(req) {
  let b = req.body;
  if (typeof b === "string") { try { b = JSON.parse(b); } catch { b = {}; } }
  if (!b) { b = await new Promise((res) => { let raw = ""; req.on("data", c => raw += c); req.on("end", () => { try { res(JSON.parse(raw || "{}")); } catch { res({}); } }); }); }
  return b || {};
}
const jsonFrom = (t) => { const m = t.match(/\{[\s\S]*\}/); if (!m) return null; try { return JSON.parse(m[0]); } catch { return null; } };

const SYSTEM = `You write warm, specific onboarding copy for a new hire. Given a name, role and department, respond ONLY with compact JSON:
{"welcome":"<2 sentences welcoming them, specific to the role and department, plain and human, no cliches, no em dashes>","tip":"<one practical Day-1 tip specific to that department>"}
No markdown, no extra text.`;

module.exports = async (req, res) => {
  if (req.method !== "POST") { res.status(405).json({ error: "POST only" }); return; }
  const body = await readBody(req);
  const cfg = cfgFor(body.model);
  const key = keyFor(cfg);
  if (!key) { res.status(503).json({ error: "AI backend not configured" }); return; }
  const name = (body.name || "the new starter").toString().slice(0, 80);
  const role = (body.role || "").toString().slice(0, 80);
  const department = (body.department || "").toString().slice(0, 80);
  const user = `Name: ${name}\nRole: ${role}\nDepartment: ${department}`;

  const payload = { model: cfg.id, messages: [{ role: "system", content: SYSTEM }, { role: "user", content: user }], max_tokens: 320, temperature: 0.6, top_p: 0.95, stream: false, ...cfg.extra };
  const ctrl = new AbortController(); const to = setTimeout(() => ctrl.abort(), 55000);
  try {
    const r = await fetch(ENDPOINT, { method: "POST", headers: { Authorization: "Bearer " + key, "Content-Type": "application/json" }, body: JSON.stringify(payload), signal: ctrl.signal });
    clearTimeout(to);
    if (!r.ok) { res.status(502).json({ error: "upstream " + r.status }); return; }
    const d = await r.json();
    const j = jsonFrom((d.choices?.[0]?.message?.content || "").trim()) || {};
    res.status(200).json({ welcome: j.welcome || "", tip: j.tip || "", model: cfg.id });
  } catch (e) { clearTimeout(to); res.status(502).json({ error: "request failed" }); }
};
