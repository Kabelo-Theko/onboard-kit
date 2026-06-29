// onboard-kit — optional AI personalization (Vercel serverless function).
//
// The deterministic pack is the default. This adds, on request, a short
// role/department-specific welcome paragraph and a Day-1 tip. The browser POSTs
// { name, role, department }. Key lives ONLY in NVIDIA_API_KEY (Vercel env).

const ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions";
const MODEL = "deepseek-ai/deepseek-v4-flash";

const SYSTEM = `You write warm, specific onboarding copy for a new hire. Given a name, role and department, respond ONLY with compact JSON:
{"welcome":"<2 sentences welcoming them, specific to the role and department, plain and human, no cliches, no em dashes>","tip":"<one practical Day-1 tip specific to that department>"}
No markdown, no extra text.`;

module.exports = async (req, res) => {
  if (req.method !== "POST") { res.status(405).json({ error: "POST only" }); return; }
  const key = process.env.NVIDIA_API_KEY;
  if (!key) { res.status(503).json({ error: "AI backend not configured" }); return; }

  let body = req.body;
  if (typeof body === "string") { try { body = JSON.parse(body); } catch { body = {}; } }
  if (!body) { body = await new Promise((resolve) => { let raw = ""; req.on("data", c => raw += c); req.on("end", () => { try { resolve(JSON.parse(raw || "{}")); } catch { resolve({}); } }); }); }

  const name = (body.name || "the new starter").toString().slice(0, 80);
  const role = (body.role || "").toString().slice(0, 80);
  const department = (body.department || "").toString().slice(0, 80);
  const user = `Name: ${name}\nRole: ${role}\nDepartment: ${department}`;

  const payload = {
    model: MODEL,
    messages: [{ role: "system", content: SYSTEM }, { role: "user", content: user }],
    max_tokens: 320, temperature: 0.6, top_p: 0.95, stream: false,
    chat_template_kwargs: { thinking: false },
  };
  try {
    const r = await fetch(ENDPOINT, { method: "POST", headers: { Authorization: "Bearer " + key, "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    if (!r.ok) { res.status(502).json({ error: "upstream " + r.status }); return; }
    const data = await r.json();
    const text = data.choices?.[0]?.message?.content?.trim() || "";
    let out = { welcome: "", tip: "" };
    const m = text.match(/\{[\s\S]*\}/);
    if (m) { try { const j = JSON.parse(m[0]); out = { welcome: j.welcome || "", tip: j.tip || "" }; } catch {} }
    res.status(200).json(out);
  } catch (e) { res.status(502).json({ error: "request failed" }); }
};
