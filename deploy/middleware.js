// Pre-launch access gate (Vercel Routing Middleware, Edge runtime).
// Runs on Vercel's servers BEFORE any page, image or file is served.
// The code itself is NOT in this file: it is the ACCESS_CODE environment
// variable (type "sensitive") on the Vercel project.
// To go live: remove this file from the deployment (and the X-Robots-Tag header).

const COOKIE = "yiasemi_access";
const MAX_AGE = 60 * 60 * 24 * 30; // 30 days

async function sha256(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
function safeEqual(a, b) {
  if (a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}
function cookieValue(req) {
  const m = (req.headers.get("cookie") || "").match(new RegExp("(?:^|;\\s*)" + COOKIE + "=([a-f0-9]{64})"));
  return m ? m[1] : "";
}
function safeNext(v) {
  return typeof v === "string" && v.startsWith("/") && !v.startsWith("//") && !v.startsWith("/__access") ? v : "/";
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function gatePage(next, error, status) {
  const esc = (s) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const html = `<!doctype html><html lang="el"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow">
<title>Γιασεμί · Yiasemi</title>
<style>
:root{--bg:#f6f0e6;--paper:#fcf9f3;--ink:#2a2620;--muted:#645d52;--line:#cbbfa9;--clay:#9a4d2b;--olive:#55633e}
*{box-sizing:border-box;margin:0}body{min-height:100vh;display:grid;place-items:center;padding:24px;background:var(--bg);color:var(--ink);font:400 16px/1.6 Georgia,"Times New Roman",serif}
main{width:min(420px,100%);background:var(--paper);border:1px solid var(--line);border-radius:18px;padding:36px 28px;text-align:center}
svg{width:40px;height:40px;color:var(--olive);margin:0 auto 14px;display:block}h1{font-weight:400;font-size:1.9rem;line-height:1.15}
p{color:var(--muted);font:400 .95rem/1.6 system-ui,-apple-system,"Segoe UI",sans-serif;margin-top:10px}
label{display:block;text-align:left;font:500 .85rem system-ui,sans-serif;margin:22px 0 6px}
input{width:100%;height:50px;padding:0 16px;border:1px solid var(--line);border-radius:999px;background:#fff;color:var(--ink);font:500 1.15rem system-ui,sans-serif;letter-spacing:.25em;text-align:center}
input:focus{outline:2px solid var(--clay);outline-offset:2px}
button{width:100%;height:50px;margin-top:12px;border:0;border-radius:999px;background:var(--ink);color:var(--bg);font:500 1rem system-ui,sans-serif;cursor:pointer}
button:hover{background:var(--olive)}.err{color:#a3341b;font-weight:500}
</style></head><body><main>
<svg viewBox="0 0 40 40" aria-hidden="true"><g fill="currentColor"><ellipse cx="20" cy="10.5" rx="5.2" ry="8.5"/><ellipse cx="20" cy="10.5" rx="5.2" ry="8.5" transform="rotate(72 20 20)"/><ellipse cx="20" cy="10.5" rx="5.2" ry="8.5" transform="rotate(144 20 20)"/><ellipse cx="20" cy="10.5" rx="5.2" ry="8.5" transform="rotate(216 20 20)"/><ellipse cx="20" cy="10.5" rx="5.2" ry="8.5" transform="rotate(288 20 20)"/></g><circle cx="20" cy="20" r="3.4" fill="#fcf9f3"/></svg>
<h1>Γιασεμί</h1>
<p>Ο ιστότοπος δεν είναι ακόμη δημόσιος.<br><span lang="en">This website is not public yet.</span></p>
<form method="post" action="/__access">
<input type="hidden" name="next" value="${esc(next)}">
<label for="code">Κωδικός πρόσβασης · <span lang="en">Access code</span></label>
<input id="code" name="code" type="password" inputmode="numeric" autocomplete="current-password" required autofocus${error ? ' aria-describedby="err" aria-invalid="true"' : ""}>
${error ? '<p id="err" class="err" role="alert">Λάθος κωδικός. <span lang="en">Incorrect code.</span></p>' : ""}
<button type="submit">Είσοδος · <span lang="en">Enter</span></button>
</form></main></body></html>`;
  return new Response(html, {
    status,
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "no-store",
      "x-robots-tag": "noindex, nofollow",
      "x-frame-options": "DENY",
      "referrer-policy": "no-referrer",
      "content-security-policy": "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
    },
  });
}

export default async function middleware(request) {
  const code = process.env.ACCESS_CODE;
  if (!code) return new Response("Site temporarily unavailable.", { status: 503, headers: { "cache-control": "no-store" } });
  const token = await sha256("yiasemi-gate-v1:" + code);
  const url = new URL(request.url);

  if (url.pathname === "/__logout") {
    return new Response(null, { status: 303, headers: { location: "/", "set-cookie": `${COOKIE}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax`, "cache-control": "no-store" } });
  }

  if (url.pathname === "/__access") {
    if (request.method !== "POST") return gatePage("/", false, 401);
    const form = await request.formData().catch(() => null);
    const given = String(form?.get("code") || "").trim().slice(0, 64);
    const next = safeNext(String(form?.get("next") || "/"));
    if (safeEqual(await sha256("yiasemi-gate-v1:" + given), token)) {
      return new Response(null, { status: 303, headers: { location: next, "set-cookie": `${COOKIE}=${token}; Path=/; Max-Age=${MAX_AGE}; HttpOnly; Secure; SameSite=Lax`, "cache-control": "no-store" } });
    }
    await sleep(1200);                                   // slow down guessing
    return gatePage(next, true, 401);
  }

  if (safeEqual(cookieValue(request), token)) {
    return new Response(null, { headers: { "x-middleware-next": "1" } });   // continue to the site
  }
  return gatePage(url.pathname + url.search, false, 401);
}
