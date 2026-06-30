// onboard-kit — AI serverless harness (Vercel function). Tasks:
//   "personalize" (default): {welcome, tip, day1plan[]} for the new starter
//   "manifest": rationale for why a department gets its software/hardware/access
// Model toggle: flash (default) / pro / minimax. One NVIDIA_API_KEY powers all.
// Deterministic pack remains the default; this only adds optional copy.

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
async function callModel(cfg, key, messages, max_tokens, temperature) {
  const payload = { model: cfg.id, messages, max_tokens, temperature, top_p: 0.95, stream: false, ...cfg.extra };
  const ctrl = new AbortController(); const to = setTimeout(() => ctrl.abort(), 55000);
  try {
    const r = await fetch(ENDPOINT, { method: "POST", headers: { Authorization: "Bearer " + key, "Content-Type": "application/json" }, body: JSON.stringify(payload), signal: ctrl.signal });
    clearTimeout(to);
    if (!r.ok) return { error: "upstream " + r.status };
    const d = await r.json();
    return { text: (d.choices?.[0]?.message?.content || "").trim() };
  } catch (e) { clearTimeout(to); return { error: "request failed" }; }
}

const SYS_PERSONALIZE = `You write warm, specific onboarding copy for a new hire. Given name, role and department, respond ONLY with compact JSON:
{"welcome":"<2 sentences welcoming them, specific to role and department, plain, no cliches, no em dashes>","tip":"<one practical Day-1 tip for that department>","day1plan":["<3 to 5 short first-day actions specific to the role>"]}
No markdown, no extra text.`;
const SYS_MANIFEST = `You are an IT manager explaining a new starter's provisioning to a non-technical reader. Given a department and its software, hardware and access groups, respond ONLY with compact JSON:
{"rationale":"<3 to 5 short plain-English sentences: why this person needs these specific tools, devices and access for this department. No jargon, no em dashes.>"}
No markdown, no extra text.`;

module.exports = async (req, res) => {
  if (req.method !== "POST") { res.status(405).json({ error: "POST only" }); return; }
  const body = await readBody(req);
  const cfg = cfgFor(body.model);
  const key = keyFor(cfg);
  if (!key) { res.status(503).json({ error: "AI backend not configured" }); return; }

  if (body.task === "manifest") {
    const dept = (body.department || "").toString().slice(0, 80);
    const software = (Array.isArray(body.software) ? body.software : []).join(", ").slice(0, 400);
    const hardware = (Array.isArray(body.hardware) ? body.hardware : []).join(", ").slice(0, 400);
    const groups = (Array.isArray(body.groups) ? body.groups : []).join(", ").slice(0, 200);
    const user = `Department: ${dept}\nSoftware: ${software}\nHardware: ${hardware}\nAccess groups: ${groups}`;
    const out = await callModel(cfg, key, [{ role: "system", content: SYS_MANIFEST }, { role: "user", content: user }], 360, 0.4);
    if (out.error) { res.status(502).json({ error: out.error }); return; }
    const j = jsonFrom(out.text) || { rationale: out.text };
    res.status(200).json({ rationale: j.rationale || out.text, model: cfg.id });
    return;
  }
  // default: personalize
  const name = (body.name || "the new starter").toString().slice(0, 80);
  const role = (body.role || "").toString().slice(0, 80);
  const department = (body.department || "").toString().slice(0, 80);
  const out = await callModel(cfg, key, [{ role: "system", content: SYS_PERSONALIZE }, { role: "user", content: `Name: ${name}\nRole: ${role}\nDepartment: ${department}` }], 380, 0.6);
  if (out.error) { res.status(502).json({ error: out.error }); return; }
  const j = jsonFrom(out.text) || {};
  res.status(200).json({ welcome: j.welcome || "", tip: j.tip || "", day1plan: Array.isArray(j.day1plan) ? j.day1plan : [], model: cfg.id });
};
